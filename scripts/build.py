#!/usr/bin/env python3
"""
VELOX Build Orchestration Script

Verifies the build environment, validates GN configuration parameters,
and coordinates building the native Chromium binary with memory-safe flags.
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def get_root():
    return Path(__file__).resolve().parent.parent

def check_environment():
    print("=" * 60)
    print("VELOX — Build Environment Preflight Audit")
    print("=" * 60)

    issues = []

    # 1. Check Python
    py_ver = sys.version.split()[0]
    print(f"[+] Python Version: {py_ver}")

    # 2. Check Git
    git_path = shutil.which("git")
    if git_path:
        ret = subprocess.run(["git", "--version"], capture_output=True, text=True)
        print(f"[+] Git: {ret.stdout.strip()} ({git_path})")
    else:
        issues.append("git not found in PATH")

    # 3. Check depot_tools
    gclient_path = shutil.which("gclient") or shutil.which("gclient.bat")
    depot_default = Path("D:/depot_tools")
    if not gclient_path and depot_default.exists():
        os.environ["PATH"] = str(depot_default) + os.pathsep + os.environ.get("PATH", "")
        gclient_path = shutil.which("gclient") or shutil.which("gclient.bat")

    if gclient_path:
        print(f"[+] depot_tools: Found at {gclient_path}")
    else:
        issues.append("depot_tools not installed or not in PATH")

    # 4. Check Disk Space
    root = get_root()
    total, used, free = shutil.disk_usage(root)
    free_gb = free // (2**30)
    print(f"[+] Working Drive Free Space: {free_gb} GB")
    if free_gb < 100:
        issues.append(f"Insufficient disk space: {free_gb} GB available (minimum 100 GB required)")

    # 5. Check Visual Studio / MSVC Toolchain
    vswhere = Path("C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe")
    vs_found = False
    if vswhere.exists():
        ret = subprocess.run([str(vswhere), "-latest", "-products", "*", "-property", "installationPath"], capture_output=True, text=True)
        vs_path = ret.stdout.strip()
        if vs_path and Path(vs_path).exists():
            print(f"[+] Visual Studio Installation: {vs_path}")
            vs_found = True

    if not vs_found:
        print("[!] Visual Studio C++ toolchain (v143) is not detected.")
        issues.append("Visual Studio 2022 C++ Workload (MSVC v143) is missing.")

    # 6. Check Windows Kits / SDK
    sdk_root = Path("C:/Program Files (x86)/Windows Kits/10")
    if sdk_root.exists():
        inc_dir = sdk_root / "Include"
        sdk_versions = [d.name for d in inc_dir.iterdir() if d.is_dir()] if inc_dir.exists() else []
        print(f"[+] Windows SDK Root: {sdk_root} (Versions: {', '.join(sdk_versions)})")
    else:
        print("[!] Windows SDK (10.0.22621+) is not detected.")
        issues.append("Windows 10/11 SDK is missing.")

    print("-" * 60)
    if issues:
        print(f"Status: BLOCKED — {len(issues)} prerequisite(s) missing:")
        for issue in issues:
            print(f"  [-] {issue}")
        return False
    else:
        print("Status: READY — All toolchain requirements satisfied.")
        return True

def generate_gn_args(out_dir="out/Default"):
    root = get_root()
    target_out = root / out_dir
    target_out.mkdir(parents=True, exist_ok=True)
    args_file = target_out / "args.gn"

    gn_content = """# VELOX Optimized Build Configuration for Windows x64
target_os = "win"
target_cpu = "x64"
is_debug = false
is_official_build = false
is_component_build = false

# Memory and linker tuning for 16 GB RAM workstations
symbol_level = 0
blink_symbol_level = 0
v8_symbol_level = 0

# Streamline build targets
enable_nacl = false
treat_warnings_as_errors = false

# Keep standard security boundaries active
dcheck_always_on = false
"""

    args_file.write_text(gn_content, encoding="utf-8")
    print(f"[+] Generated GN arguments at: {args_file}")
    return 0

def main():
    parser = argparse.ArgumentParser(description="VELOX Build Script")
    parser.add_argument("--check-env", action="store_true", help="Audit host environment and prerequisites")
    parser.add_argument("--gen-args", action="store_true", help="Generate args.gn for output directory")
    parser.add_argument("--out-dir", default="out/Default", help="Output directory relative to repo root")
    args = parser.parse_args()

    if args.check_env:
        ready = check_environment()
        sys.exit(0 if ready else 1)

    if args.gen_args:
        sys.exit(generate_gn_args(args.out_dir))

    check_environment()

if __name__ == "__main__":
    main()
