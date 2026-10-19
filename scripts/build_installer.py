#!/usr/bin/env python3
"""
VELOX Mini Installer Build Orchestrator
Sets up build environment and triggers ninja target 'mini_installer'
"""

import os
import sys
import subprocess
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

def main():
    print("=" * 70)
    print("VELOX Phase 10: Building mini_installer")
    print("=" * 70)

    env = os.environ.copy()
    env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    env["DEPOT_TOOLS_UPDATE"] = "0"
    env["GYP_MSVS_VERSION"] = "2022"
    env["vs2022_install"] = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
    env["WINDOWSSDKDIR"] = r"C:\Program Files (x86)\Windows Kits\10"
    env["PATH"] = r"D:\depot_tools;" + env.get("PATH", "")

    ninja_exe = r"D:\Velox\src\third_party\ninja\ninja.exe"
    build_dir = r"D:\Velox\src\out\Default"

    # Compile mini_installer target
    cmd = [ninja_exe, "-C", build_dir, "mini_installer", "-j", "14"]
    print(f"Executing: {' '.join(cmd)}")
    start_time = time.time()

    proc = subprocess.Popen(
        cmd,
        env=env,
        cwd=r"D:\Velox\src",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in proc.stdout:
        print(line, end="", flush=True)

    proc.wait()
    duration = time.time() - start_time
    print(f"\nFinished in {duration:.1f} seconds. Exit code: {proc.returncode}")

    if proc.returncode == 0:
        installer_path = os.path.join(build_dir, "mini_installer.exe")
        if os.path.exists(installer_path):
            size_mb = os.path.getsize(installer_path) / (1024 * 1024)
            print(f"SUCCESS: {installer_path} generated ({size_mb:.2f} MB)")
            # Also create a copy named velox_installer.exe for direct distribution
            velox_installer = os.path.join(build_dir, "velox_installer.exe")
            import shutil
            shutil.copy2(installer_path, velox_installer)
            print(f"Created: {velox_installer}")
            return 0
        else:
            print("ERROR: mini_installer.exe not found in output directory")
            return 1
    else:
        print("ERROR: ninja build failed")
        return proc.returncode

if __name__ == "__main__":
    sys.exit(main())
