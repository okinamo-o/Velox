#!/usr/bin/env python3
"""
VELOX Patch Applicator and Verification Script

Applies all patches in /patches/ in numerical sequence to the pristine 
chromium/src checkout. Supports dry-run verification and automatic rollback.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_repo_root():
    return Path(__file__).resolve().parent.parent

def run_command(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout, result.stderr

def apply_patches(dry_run=False, reverse=False):
    root = get_repo_root()
    src_dir = root / "src"
    patches_dir = root / "patches"

    if not patches_dir.exists():
        print(f"[!] Patches directory not found: {patches_dir}")
        return 1

    patches = sorted([p for p in patches_dir.glob("*.patch")])
    if not patches:
        print("[i] No patches found in patches directory.")
        return 0

    if not src_dir.exists():
        print(f"[!] Upstream source directory not found at: {src_dir}")
        print("    Run 'gclient sync' to check out pristine upstream Chromium first.")
        return 1

    action_name = "Checking" if dry_run else ("Reverting" if reverse else "Applying")
    print(f"[*] {action_name} {len(patches)} patch(es)...")

    for patch in patches:
        cmd = ["git", "apply"]
        if dry_run:
            cmd.append("--check")
        if reverse:
            cmd.append("-R")
        cmd.extend(["--whitespace=nowarn", str(patch)])

        print(f"    -> {patch.name} ... ", end="", flush=True)
        ret, stdout, stderr = run_command(cmd, cwd=src_dir)
        if ret == 0:
            print("OK")
        else:
            print("FAILED")
            print(f"[!] Error applying {patch.name}:")
            print(stderr)
            return ret

    print(f"[+] All patches {action_name.lower()} successfully.")
    return 0

def main():
    parser = argparse.ArgumentParser(description="VELOX Patch Management Tool")
    parser.add_argument("--dry-run", action="store_true", help="Check if patches apply cleanly without modifying files")
    parser.add_argument("--reverse", action="store_true", help="Reverse/unapply all patches")
    args = parser.parse_args()

    sys.exit(apply_patches(dry_run=args.dry_run, reverse=args.reverse))

if __name__ == "__main__":
    main()
