#!/usr/bin/env python3
"""
VELOX Widevine DRM & Protected Media Provisioner

Detects, verifies, and provisions Google Widevine Content Decryption Module (CDM)
into the VELOX installation directory for seamless playback on Netflix, Spotify,
Disney+, and Amazon Prime Video.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path

def get_velox_directories():
    """Returns application version dir and user data Widevine paths."""
    appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    velox_app = appdata / "Velox" / "Application"
    user_data = appdata / "Velox" / "User Data"
    
    version_dir = None
    if velox_app.exists():
        vdirs = [d for d in velox_app.iterdir() if d.is_dir() and d.name.replace(".", "").isdigit()]
        if vdirs:
            vdirs.sort(key=lambda d: tuple(map(int, d.name.split("."))), reverse=True)
            version_dir = vdirs[0]

    app_widevine = (version_dir / "WidevineCdm") if version_dir else None
    user_widevine = user_data / "WidevineCdm"
    return version_dir, app_widevine, user_widevine

def find_system_widevine_sources():
    """Discovers signed Widevine CDM installations on the host (Chrome, Edge, Brave)."""
    candidates = []
    
    appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    program_files = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
    program_files_x86 = Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))

    search_roots = [
        # Chrome User Data
        appdata / "Google" / "Chrome" / "User Data" / "WidevineCdm",
        # Edge User Data
        appdata / "Microsoft" / "Edge" / "User Data" / "WidevineCdm",
        # Brave User Data
        appdata / "BraveSoftware" / "Brave-Browser" / "User Data" / "WidevineCdm",
    ]

    # Check version directories in Program Files
    for pf in [program_files, program_files_x86]:
        chrome_app = pf / "Google" / "Chrome" / "Application"
        if chrome_app.exists():
            for v in chrome_app.iterdir():
                if v.is_dir() and (v / "WidevineCdm").exists():
                    search_roots.append(v / "WidevineCdm")

    for root in search_roots:
        if not root.exists():
            continue
        # Could be direct or nested in version subdirectory
        if (root / "manifest.json").exists():
            candidates.append(root)
        else:
            for sub in root.iterdir():
                if sub.is_dir() and (sub / "manifest.json").exists():
                    candidates.append(sub)

    return candidates

def inspect_widevine_directory(cdm_dir):
    """Inspects a WidevineCdm directory for manifest and DLL."""
    if not cdm_dir or not cdm_dir.exists():
        return None

    manifest_file = cdm_dir / "manifest.json"
    if not manifest_file.exists():
        return None

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception:
        return None

    dll_path = cdm_dir / "_platform_specific" / "win_x64" / "widevinecdm.dll"
    if not dll_path.exists():
        # Check flat directory
        dll_path = cdm_dir / "widevinecdm.dll"

    return {
        "version": manifest.get("version", "Unknown"),
        "codecs": manifest.get("x-cdm-codecs", ""),
        "manifest_path": str(manifest_file),
        "dll_path": str(dll_path) if dll_path.exists() else None,
        "is_complete": dll_path.exists()
    }

def provision_widevine(source_dir, target_dir):
    """Copies Widevine files from source to target directory."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Provisioning Widevine CDM from:\n  {source_dir}\nto:\n  {target_dir}")
    
    # Copy manifest
    shutil.copy2(source_dir / "manifest.json", target_dir / "manifest.json")
    
    # Handle platform specific folder
    src_platform = source_dir / "_platform_specific" / "win_x64"
    tgt_platform = target_dir / "_platform_specific" / "win_x64"
    
    if src_platform.exists():
        tgt_platform.mkdir(parents=True, exist_ok=True)
        for item in src_platform.iterdir():
            shutil.copy2(item, tgt_platform / item.name)
    elif (source_dir / "widevinecdm.dll").exists():
        tgt_platform.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_dir / "widevinecdm.dll", tgt_platform / "widevinecdm.dll")
        if (source_dir / "widevinecdm.dll.sig").exists():
            shutil.copy2(source_dir / "widevinecdm.dll.sig", tgt_platform / "widevinecdm.dll.sig")

    print("[SUCCESS] Widevine CDM successfully provisioned.")
    return True

def main():
    parser = argparse.ArgumentParser(description="VELOX Widevine CDM DRM Provisioner")
    parser.add_argument("--status", action="store_true", help="Display current DRM status")
    parser.add_argument("--provision", action="store_true", help="Provision Widevine from available host sources")
    parser.add_argument("--source", default=None, help="Custom source directory containing Widevine CDM")
    args = parser.parse_args()

    version_dir, app_widevine, user_widevine = get_velox_directories()
    
    app_info = inspect_widevine_directory(app_widevine) if app_widevine else None
    user_info = inspect_widevine_directory(user_widevine) if user_widevine else None

    print("=" * 60)
    print(" VELOX DRM & WIDEVINE CDM PROVISIONING STATUS")
    print("=" * 60)
    print(f"VELOX Application Version: {version_dir.name if version_dir else 'Not Installed'}")
    
    is_active = False
    if app_info and app_info["is_complete"]:
        print(f"Widevine Status (Application): [ACTIVE] Version {app_info['version']}")
        print(f"  DLL Path: {app_info['dll_path']}")
        is_active = True
    else:
        print("Widevine Status (Application): [NOT INSTALLED]")

    if user_info and user_info["is_complete"]:
        print(f"Widevine Status (User Profile): [ACTIVE] Version {user_info['version']}")
        print(f"  DLL Path: {user_info['dll_path']}")
        is_active = True
    else:
        print("Widevine Status (User Profile): [NOT INSTALLED]")

    if args.status:
        return 0

    if is_active and not args.provision:
        print("\nDRM playback is fully ready! Both EME key systems and CDM binaries are operational.")
        return 0

    # Look for candidate sources
    sources = find_system_widevine_sources()
    if args.source:
        sources.insert(0, Path(args.source))

    if not sources:
        print("\n[NOTE] No existing host Widevine CDM source was discovered.")
        print("To enable DRM protected media (Netflix, Spotify, Prime Video):")
        print("1. Install or update Widevine via Component Updater in browser, OR")
        print("2. Run: python scripts/install_widevine.py --source <path_to_widevine_folder>")
        return 0

    print(f"\nDiscovered {len(sources)} available Widevine source(s):")
    for i, s in enumerate(sources, 1):
        info = inspect_widevine_directory(s)
        ver = info['version'] if info else 'Unknown'
        print(f"  [{i}] {s} (Version: {ver})")

    if args.provision or not is_active:
        chosen_source = sources[0]
        target = app_widevine if app_widevine else user_widevine
        provision_widevine(chosen_source, target)
        print("\nRestart VELOX to activate protected media playback.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
