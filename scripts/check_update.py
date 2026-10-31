#!/usr/bin/env python3
"""
VELOX Remote Auto-Updater Tool

Checks for browser updates via remote version manifest or GitHub Releases,
verifies cryptographic SHA-256 signatures, and executes silent in-place upgrades.
"""

import os
import sys
import json
import hashlib
import argparse
import urllib.request
import subprocess
from pathlib import Path

DEFAULT_MANIFEST_URL = "https://raw.githubusercontent.com/velox-browser/velox/main/releases/version.json"
LOCAL_FALLBACK_MANIFEST = Path(__file__).resolve().parent.parent / "releases" / "version.json"

def get_installed_version():
    """Detects current installed VELOX version from LocalAppData directory."""
    appdata = os.environ.get("LOCALAPPDATA", "")
    app_dir = Path(appdata) / "Velox" / "Application"
    
    if app_dir.exists():
        # Version subdirectories follow the pattern 134.0.6998.178
        version_dirs = [d.name for d in app_dir.iterdir() if d.is_dir() and d.name.replace(".", "").isdigit()]
        if version_dirs:
            # Sort by parsed version tuple
            version_dirs.sort(key=lambda v: tuple(map(int, v.split("."))), reverse=True)
            return version_dirs[0]

    # Fallback to source tree VERSION file if running from repo
    version_file = Path(__file__).resolve().parent.parent / "src" / "chrome" / "VERSION"
    if version_file.exists():
        data = {}
        for line in version_file.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k] = v
        return f"{data.get('MAJOR', '134')}.{data.get('MINOR', '0')}.{data.get('BUILD', '6998')}.{data.get('PATCH', '178')}"
    
    return "134.0.6998.178"

def compare_versions(v1_str, v2_str):
    """
    Compares two dot-separated version strings.
    Returns:
        -1 if v1 < v2 (v2 is newer)
         0 if v1 == v2
         1 if v1 > v2 (v1 is newer)
    """
    v1_parts = [int(p) for p in v1_str.strip().split(".") if p.isdigit()]
    v2_parts = [int(p) for p in v2_str.strip().split(".") if p.isdigit()]
    
    # Pad to equal length
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts += [0] * (max_len - len(v1_parts))
    v2_parts += [0] * (max_len - len(v2_parts))
    
    if v1_parts < v2_parts:
        return -1
    elif v1_parts > v2_parts:
        return 1
    return 0

def fetch_manifest(manifest_source):
    """Fetches and parses the version manifest from URL or local file path."""
    if os.path.exists(manifest_source):
        with open(manifest_source, "r", encoding="utf-8") as f:
            return json.load(f)
    
    req = urllib.request.Request(
        manifest_source,
        headers={"User-Agent": "VELOX-AutoUpdater/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def verify_file_sha256(filepath, expected_sha256):
    """Verifies that the SHA-256 hash of a file matches expected hash."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest().lower()
    return actual_hash == expected_sha256.lower(), actual_hash

def download_installer(url, target_path, expected_sha256):
    """Downloads installer package with progress display and mandatory cryptographic SHA-256 check."""
    if not expected_sha256 or len(str(expected_sha256).strip()) != 64:
        print("SECURITY ERROR: Remote manifest is missing a valid 64-character SHA-256 hash. Aborting.")
        return False

    print(f"Downloading installer from: {url}")
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, downloaded * 100.0 / total_size)
            mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\rProgress: {percent:5.1f}% ({mb:.1f} MB / {total_mb:.1f} MB)")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, target_path, reporthook=report_hook)
    print("\nDownload finished.")

    print("Verifying cryptographic SHA-256 integrity...")
    valid, actual_hash = verify_file_sha256(target_path, expected_sha256)
    if not valid:
        print(f"SECURITY ERROR: SHA-256 mismatch!\nExpected: {expected_sha256}\nGot:      {actual_hash}")
        target_path.unlink(missing_ok=True)
        return False
    print(f"Integrity verified! SHA-256 matches: {actual_hash}")

    return True

def install_update(installer_path, silent=True, allow_unsigned=False, expected_publisher="VELOX"):
    """Executes the downloaded VELOX installer after verifying Authenticode signature."""
    installer_path = Path(installer_path).resolve()
    if not installer_path.exists():
        print(f"ERROR: Installer binary not found at {installer_path}")
        return False

    if not allow_unsigned:
        print(f"Verifying Windows Authenticode signature on installer binary (expected publisher: '{expected_publisher}')...")
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import sign_binaries
            is_signed, sig_msg = sign_binaries.verify_signature(
                installer_path,
                expected_publisher=expected_publisher
            )
            if not is_signed:
                print(f"SECURITY ERROR: Installer failed Authenticode verification: {sig_msg}")
                print("Aborting installation to protect system integrity.")
                return False
            print(f"[AUTHENTICODE VERIFIED] {sig_msg}")
        except Exception as e:
            print(f"WARNING: Authenticode verification subsystem returned error ({e}).")
            if not allow_unsigned:
                print("SECURITY ERROR: Cannot verify installer signature. Aborting.")
                return False

    args = [str(installer_path)]
    if silent:
        args.extend(["--silent", "--do-not-launch-chrome"])

    print(f"Launching installer: {' '.join(args)}")
    try:
        proc = subprocess.run(args, check=True)
        print("Installation process completed successfully.")
        return proc.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Installer failed with exit code: {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="VELOX Browser Remote Auto-Updater")
    parser.add_argument("--manifest-url", default=None, help="Custom manifest URL or file path")
    parser.add_argument("--check-only", action="store_true", help="Only check for updates without downloading")
    parser.add_argument("--download", action="store_true", help="Download the latest installer if available")
    parser.add_argument("--install", action="store_true", help="Download and install the latest update silently")
    parser.add_argument("--allow-unsigned", action="store_true", help="Allow running unsigned installer (for test/dev only)")
    parser.add_argument("--expected-publisher", default="VELOX", help="Expected Authenticode publisher substring")
    parser.add_argument("--output-dir", default=None, help="Directory to save downloaded installer")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    installed_version = get_installed_version()
    manifest_src = args.manifest_url or (str(LOCAL_FALLBACK_MANIFEST) if LOCAL_FALLBACK_MANIFEST.exists() else DEFAULT_MANIFEST_URL)

    result = {
        "installed_version": installed_version,
        "latest_version": None,
        "update_available": False,
        "status": "CHECKING",
        "error": None
    }

    try:
        manifest = fetch_manifest(manifest_src)
        latest_version = manifest.get("version", "")
        result["latest_version"] = latest_version
        result["release_notes"] = manifest.get("release_notes_url", "")
        
        cmp = compare_versions(installed_version, latest_version)
        if cmp < 0:
            platform_info = manifest.get("platforms", {}).get("win_x64", {})
            sha256_hash = platform_info.get("sha256", "")
            if not sha256_hash or len(sha256_hash.strip()) != 64:
                result["update_available"] = False
                result["status"] = "ERROR"
                result["error"] = "Manifest security failure: missing mandatory 64-character SHA-256 hash"
            else:
                result["update_available"] = True
                result["status"] = "UPDATE_AVAILABLE"
                result["installer_url"] = platform_info.get("installer_url", "")
                result["sha256"] = sha256_hash
        else:
            result["update_available"] = False
            result["status"] = "UP_TO_DATE"

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("=" * 60)
    print(" VELOX BROWSER REMOTE UPDATE CHECKER")
    print("=" * 60)
    print(f"Installed Version: {result['installed_version']}")
    print(f"Latest Version:    {result['latest_version'] or 'Unknown'}")
    print(f"Status:            {result['status']}")

    if result.get("error"):
        print(f"Check failed: {result['error']}")
        return 1

    if not result["update_available"]:
        print("VELOX is up to date!")
        return 0

    print("\n* A new version of VELOX is available!")
    print(f"Release Notes: {result.get('release_notes')}")
    print(f"Download URL:  {result.get('installer_url')}")

    if args.download or args.install:
        out_dir = Path(args.output_dir or (Path.home() / "Downloads"))
        out_file = out_dir / "velox_installer.exe"
        success = download_installer(result["installer_url"], out_file, result.get("sha256"))
        if not success:
            return 1

        if args.install:
            print("\nApplying update...")
            return 0 if install_update(
                out_file,
                silent=True,
                allow_unsigned=args.allow_unsigned,
                expected_publisher=args.expected_publisher
            ) else 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
