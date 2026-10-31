#!/usr/bin/env python3
"""
VELOX Production Release Packaging & Checksum Generator

Collects built release artifacts, generates SHA-256 and SHA-512 checksum manifests,
packages portable distribution archives, and synchronizes the release version manifest.
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DEFAULT = REPO_ROOT / "src" / "out" / "Default"
RELEASES_DIR = REPO_ROOT / "releases"

def compute_hash(file_path, algorithm="sha256"):
    hasher = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def package_portable_zip(target_zip_path, version="134.0.6998.184"):
    """Creates a standalone portable ZIP package of VELOX."""
    target_zip_path = Path(target_zip_path)
    target_zip_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Creating portable ZIP package at: {target_zip_path.name}...")
    
    files_to_pack = [
        (OUT_DEFAULT / "chrome.exe", "velox/chrome.exe"),
        (OUT_DEFAULT / "velox.exe", "velox/velox.exe"),
        (OUT_DEFAULT / "chrome.dll", f"velox/{version}/chrome.dll"),
        (OUT_DEFAULT / "resources.pak", f"velox/{version}/resources.pak"),
        (OUT_DEFAULT / "chrome_100_percent.pak", f"velox/{version}/chrome_100_percent.pak"),
        (OUT_DEFAULT / "chrome_200_percent.pak", f"velox/{version}/chrome_200_percent.pak"),
        (OUT_DEFAULT / "icudtl.dat", f"velox/{version}/icudtl.dat"),
        (OUT_DEFAULT / "v8_context_snapshot.bin", f"velox/{version}/v8_context_snapshot.bin"),
        (REPO_ROOT / "LICENSE", "velox/LICENSE"),
    ]

    # Locale files
    locales_dir = OUT_DEFAULT / "locales"
    if locales_dir.exists():
        for pak in locales_dir.glob("*.pak"):
            files_to_pack.append((pak, f"velox/{version}/locales/{pak.name}"))

    with zipfile.ZipFile(target_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for src, arcname in files_to_pack:
            if src.exists():
                zf.write(src, arcname)

    sz_mb = target_zip_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Portable package created ({sz_mb:.2f} MB)")
    return True

def generate_checksum_manifests(release_dir):
    """Generates SHA256SUMS.txt and SHA512SUMS.txt for all files in releases/."""
    release_dir = Path(release_dir)
    files = [f for f in release_dir.iterdir() if f.is_file() and not f.name.endswith("SUMS.txt")]

    sha256_lines = []
    sha512_lines = []

    for f in sorted(files, key=lambda x: x.name):
        h256 = compute_hash(f, "sha256")
        h512 = compute_hash(f, "sha512")
        sha256_lines.append(f"{h256}  {f.name}")
        sha512_lines.append(f"{h512}  {f.name}")

    (release_dir / "SHA256SUMS.txt").write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")
    (release_dir / "SHA512SUMS.txt").write_text("\n".join(sha512_lines) + "\n", encoding="utf-8")
    print(f"[SUCCESS] Generated SHA256SUMS.txt and SHA512SUMS.txt for {len(files)} artifacts.")

def main():
    parser = argparse.ArgumentParser(description="VELOX Release Packaging Tool")
    parser.add_argument("--version", default="134.0.6998.184", help="Release version string")
    parser.add_argument("--portable", action="store_true", help="Generate portable ZIP package")
    parser.add_argument("--out-dir", default=str(RELEASES_DIR), help="Output releases directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(" VELOX PRODUCTION RELEASE PACKAGING")
    print("=" * 60)
    print(f"Version:        {args.version}")
    print(f"Releases Dir:   {out_dir}")

    # Stage velox_installer.exe
    src_installer = OUT_DEFAULT / "velox_installer.exe"
    if src_installer.exists():
        dst_installer = out_dir / "velox_installer.exe"
        print(f"Staging installer: {dst_installer.name}...")
        shutil.copy2(src_installer, dst_installer)
        installer_h = compute_hash(dst_installer, "sha256")
        installer_sz = dst_installer.stat().st_size
    else:
        print("[WARNING] out/Default/velox_installer.exe not found.")
        installer_h = None
        installer_sz = 0

    if args.portable:
        portable_zip = out_dir / f"velox-v{args.version}-win-x64-portable.zip"
        package_portable_zip(portable_zip, args.version)

    # Update version.json
    manifest_file = out_dir / "version.json"
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["version"] = args.version
        if installer_h:
            manifest["platforms"]["win_x64"]["sha256"] = installer_h
            manifest["platforms"]["win_x64"]["size_bytes"] = installer_sz
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print("[SUCCESS] Updated releases/version.json with latest checksums.")

    generate_checksum_manifests(out_dir)

    print("\nRelease packaging completed successfully!")
    print(f"Artifacts ready in: {out_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
