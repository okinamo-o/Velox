#!/usr/bin/env python3
"""
Rebuild VELOX with Branding Fixes and Monitor RAM / Disk Usage
"""

import os
import sys
import shutil
import subprocess
import time
import threading
import ctypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
    ]

def get_ram_mb():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    total_mb = stat.ullTotalPhys / (1024 * 1024)
    avail_mb = stat.ullAvailPhys / (1024 * 1024)
    used_mb = total_mb - avail_mb
    return total_mb, used_mb, avail_mb, stat.dwMemoryLoad

def get_disk_gb(drive="D:"):
    total, used, free = shutil.disk_usage(drive + "\\")
    return total / (1024**3), used / (1024**3), free / (1024**3)

class ResourceMonitor(threading.Thread):
    def __init__(self, interval=1.0):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = True
        self.max_ram_used_mb = 0
        self.min_ram_avail_mb = 999999
        self.samples = []
        self.start_disk_d_free = get_disk_gb("D:")[2]

    def run(self):
        while self.running:
            total_mb, used_mb, avail_mb, load = get_ram_mb()
            if used_mb > self.max_ram_used_mb:
                self.max_ram_used_mb = used_mb
            if avail_mb < self.min_ram_avail_mb:
                self.min_ram_avail_mb = avail_mb
            self.samples.append((time.time(), used_mb, avail_mb, load))
            time.sleep(self.interval)

    def stop(self):
        self.running = False

def run_build():
    print("=" * 70)
    print("VELOX BRANDING REBUILD & RESOURCE USAGE MONITOR")
    print("=" * 70)

    t_mb, u_mb, a_mb, load = get_ram_mb()
    d_tot, d_used, d_free = get_disk_gb("D:")
    c_tot, c_used, c_free = get_disk_gb("C:")

    print(f"Initial State:")
    print(f"  RAM:  {u_mb/1024:.2f} GB used / {t_mb/1024:.2f} GB total ({a_mb/1024:.2f} GB available, {load}% load)")
    print(f"  Disk C: {c_free:.2f} GB free / {c_tot:.2f} GB total")
    print(f"  Disk D: {d_free:.2f} GB free / {d_tot:.2f} GB total")

    env = os.environ.copy()
    env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    env["DEPOT_TOOLS_UPDATE"] = "0"
    env["GYP_MSVS_VERSION"] = "2022"
    env["vs2022_install"] = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
    env["WINDOWSSDKDIR"] = r"C:\Program Files (x86)\Windows Kits\10"
    env["PATH"] = r"D:\depot_tools;" + env.get("PATH", "")

    ninja_exe = r"D:\Velox\src\third_party\ninja\ninja.exe"
    build_dir = r"D:\Velox\src\out\Default"

    monitor = ResourceMonitor(interval=0.5)
    monitor.start()

    # Step 1: Build chrome
    print("\n--- Step 1: Compiling 'chrome' target with new branding and icons ---")
    t0 = time.time()
    p1 = subprocess.run(
        [ninja_exe, "-C", build_dir, "chrome", "-j", "14"],
        env=env,
        cwd=r"D:\Velox\src"
    )
    t1 = time.time()
    print(f"'chrome' target finished with exit code {p1.returncode} in {t1 - t0:.1f}s")
    if p1.returncode != 0:
        monitor.stop()
        return 1

    # Copy chrome.exe to velox.exe
    shutil.copy2(os.path.join(build_dir, "chrome.exe"), os.path.join(build_dir, "velox.exe"))
    print("Updated velox.exe with newly linked binary.")

    # Step 2: Build mini_installer
    print("\n--- Step 2: Compiling 'mini_installer' target with new VELOX icon ---")
    t2 = time.time()
    p2 = subprocess.run(
        [ninja_exe, "-C", build_dir, "mini_installer", "-j", "14"],
        env=env,
        cwd=r"D:\Velox\src"
    )
    t3 = time.time()
    print(f"'mini_installer' target finished with exit code {p2.returncode} in {t3 - t2:.1f}s")

    if p2.returncode == 0:
        shutil.copy2(os.path.join(build_dir, "mini_installer.exe"), os.path.join(build_dir, "velox_installer.exe"))
        print("Updated velox_installer.exe with newly packaged installer.")

    monitor.stop()
    monitor.join(timeout=2.0)

    # Post-build resource report
    end_d_free = get_disk_gb("D:")[2]
    disk_delta = monitor.start_disk_d_free - end_d_free
    post_t, post_u, post_a, post_load = get_ram_mb()

    print("\n" + "=" * 70)
    print("BUILD & RESOURCE CONSUMPTION TELEMETRY REPORT")
    print("=" * 70)
    print(f"Total Compilation Time:     {t3 - t0:.1f} seconds")
    print(f"Peak RAM Usage:             {monitor.max_ram_used_mb / 1024:.2f} GB ({(monitor.max_ram_used_mb / post_t)*100:.1f}% of {post_t/1024:.2f} GB physical)")
    print(f"Lowest Free RAM during run: {monitor.min_ram_avail_mb / 1024:.2f} GB")
    print(f"Ending RAM Usage:           {post_u / 1024:.2f} GB ({post_load}% load)")
    print(f"Disk D delta:               {'+' if disk_delta >= 0 else ''}{disk_delta*1024:.1f} MB disk space change")
    print(f"Disk D remaining:           {end_d_free:.2f} GB free")

    # Verify binaries
    print("\nGenerated Binary Verification:")
    for name in ["velox.exe", "chrome.exe", "velox_installer.exe", "mini_installer.exe"]:
        bp = os.path.join(build_dir, name)
        if os.path.exists(bp):
            sz = os.path.getsize(bp) / (1024 * 1024)
            print(f"  [OK] {name:<22} {sz:.2f} MB")
        else:
            print(f"  [FAIL] {name:<22} MISSING")

    return 0

if __name__ == "__main__":
    sys.exit(run_build())
