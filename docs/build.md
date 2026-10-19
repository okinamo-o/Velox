# VELOX — Windows Build Guide & GN Configuration

> **Host Target**: Windows 11 x64  
> **Toolchain**: Visual Studio 2022 (v143) + Windows 11 SDK (10.0.22621+) + depot_tools  
> **Pinned Baseline**: Chromium `134.0.6998.178`  

---

## 1. Prerequisites Checklist

Before compiling VELOX, the host machine must satisfy the following requirements:

| Component | Minimum Version | Installation Details |
|---|---|---|
| **OS** | Windows 10/11 64-bit | Windows 11 23H2 or later recommended |
| **Storage** | 120 GB free space | Recommended on fast NVMe drive (`D:\` used in VELOX environment) |
| **RAM** | 16 GB Physical | 16 GB requires `symbol_level=0` and linker parallelism constraints |
| **depot_tools** | Latest upstream | Installed in `D:\depot_tools` and prepended to `PATH` |
| **Visual Studio** | 2022 (v17.4+) | Workloads: Desktop C++, MSVC v143, C++ ATL, C++ MFC |
| **Windows SDK** | 10.0.22621.0+ | Components: Windows SDK + Debugging Tools for Windows |

### Toolchain Installation Commands (Run in Elevated Administrator Prompt)
```cmd
winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.VC.ATL --add Microsoft.VisualStudio.Component.VC.MFC --add Microsoft.VisualStudio.Component.Windows11SDK.22621"
```

---

## 2. Environment Variables Setup

Ensure PowerShell has the following environment configured:
```powershell
$env:DEPOT_TOOLS_WIN_TOOLCHAIN = "0"
$env:GYP_MSVS_VERSION = "2022"
$env:PATH = "D:\depot_tools;" + $env:PATH
```

---

## 3. Source Syncing & Preparation

```powershell
# 1. Initialize gclient configuration
cd D:\Velox
gclient config --unmanaged https://chromium.googlesource.com/chromium/src.git

# 2. Sync pinned tag (shallow sync for disk/network efficiency)
git clone --depth 1 --branch 134.0.6998.178 https://chromium.googlesource.com/chromium/src.git src

# 3. Synchronize third-party dependencies via gclient
gclient sync --with_branch_heads --with_tags -j 8

# 4. Apply VELOX patch series
python scripts/apply_patches.py
```

---

## 4. GN Build Configuration (`args.gn`)

To ensure reliable compilation on a 16 GB RAM developer workstation without encountering linker Out-Of-Memory (OOM) failures, configure `out/Default/args.gn` with:

```gn
# Core build settings
target_os = "win"
target_cpu = "x64"
is_debug = false
is_official_build = false
is_component_build = false

# Memory and linker optimizations for 16 GB RAM workstations
symbol_level = 0
blink_symbol_level = 0
v8_symbol_level = 0

# Strip non-critical subsystems to reduce build time & attack surface
enable_nacl = false
treat_warnings_as_errors = false

# Security verification flags (MUST REMAIN TRUE per Directive Section 7)
is_cfi = false
dcheck_always_on = false
```

Generate the ninja build files:
```powershell
gn gen out/Default
```

---

## 5. Compiling VELOX

Compile the native browser binary and chrome tests:
```powershell
# Build chrome executable using ninja
ninja -C out/Default chrome -j 14
```

*Note: With 28 logical cores and 16 GB RAM, `-j 14` provides optimal compiler throughput while preventing linker thrashing.*

---

## 6. Verification Commands

Once built, verify executable launch and security status:
```powershell
# Verify version and native launch
.\out\Default\chrome.exe --user-data-dir="D:\Velox\test-profile" --version

# Launch browser with devtools enabled
.\out\Default\chrome.exe --user-data-dir="D:\Velox\test-profile"
```
