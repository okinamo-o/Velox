<div align="center">

# ⚡ VELOX BROWSER

### The Ultra-Fast, Shielded Web Browser

[![Release](https://img.shields.io/github/v/release/okinamo-o/Velox?color=00f0ff&label=Release&style=for-the-badge)](https://github.com/okinamo-o/Velox/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-a855f7?style=for-the-badge&logo=windows)](https://github.com/okinamo-o/Velox/releases)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-10b981?style=for-the-badge)](LICENSE)
[![Chromium](https://img.shields.io/badge/Engine-Chromium%20134%20Ultra-blue?style=for-the-badge&logo=googlechrome)](https://chromium.googlesource.com/chromium/src)

<br/>

**Velox** is a next-generation desktop browser re-architected for raw speed, clean aesthetics, and zero distractions. Built upon custom-tuned Chromium 134, Velox strips away telemetry and background clutter while introducing deep system-level optimizations and modern workflows.

[**Download Velox (Installer)**](https://github.com/okinamo-o/Velox/releases/latest/download/VeloxSetup.exe) • [**Download Portable ZIP**](https://github.com/okinamo-o/Velox/releases/latest/download/Velox-v134.0.6998.178-Portable-x64.zip) • [**View Showcase Site**](dist/website/index.html)

</div>

---

## ✨ Key Highlights

### 🛡️ Native Velox Shield
Content blocking baked directly into the network loader pipeline. Ads, third-party tracking beacons, cryptominers, and fingerprinting scripts are dropped before they ever reach the DOM—eliminating JavaScript bloat and speeding up page loads by up to 3×.

### 🏝️ Opera One Tab Islands
Tabs group automatically into color-coded context islands. Collapse entire research clusters with one click, slide smoothly between active sessions, and enjoy custom glowing visual identifiers.

### ⚡ Ultra Hardware Acceleration
- Custom-tuned GPU rasterization and WebGL shader pipelines.
- Sub-350ms cold launch latency.
- Aggressive memory saver algorithms that suspend dormant tabs without losing state.

### 🔒 Zero Background Clutter & No Lingering Apps
When you close Velox, it actually exits. Hidden background mode is completely disabled, meaning no lingering system tray icons, no background resource drain, and zero silent updates eating your CPU.

### 🎨 Cyber / Glassmorphic UI
- Neon accent border glows and translucent materials.
- Modern non-client window frame integration.
- Custom vector icons and smooth window control buttons.

### 🔔 Intelligent Dynamic Updates
Velox stays out of your way. Update buttons only appear in your toolbar when an actual update is ready to apply. Click once, relaunch, and resume your exact tabs automatically.

---

## 🚀 Quick Install

### Option 1: Standalone Installer (Recommended)
Download and run the latest standalone setup:
👉 **[Download VeloxSetup.exe](https://github.com/okinamo-o/Velox/releases/latest/download/VeloxSetup.exe)**

### Option 2: Windows Package Manager (`winget`)
Install in one command via PowerShell or Command Prompt:
```powershell
winget install Velox.VeloxBrowser
```

### Option 3: Portable Edition (Zero Install)
Download the portable ZIP archive, extract it anywhere (including a USB drive), and run `velox.exe`:
👉 **[Download Portable ZIP](https://github.com/okinamo-o/Velox/releases/latest/download/Velox-v134.0.6998.178-Portable-x64.zip)**

---

## 📁 Repository Structure

```
Velox/
├── branding/          # Official Velox logos, SVG assets, and icons
├── dist/              # Release tools, website landing page, and manifests
│   ├── website/       # Production dark-mode product showcase site
│   ├── winget/        # Official Microsoft winget package manifest
│   ├── package_release.ps1 # 1-click release compilation & staging script
│   └── version.json   # Auto-update version manifest
├── docs/              # Architecture, security, and building documentation
├── patches/           # Complete patch series applied over Chromium
│   ├── 0001-...       # Velox branding & install modes
│   ├── ...            # Shield blocking, memory tuning, Tab Islands
│   └── 0016-...       # Latest Tab Islands & dynamic update infrastructure
├── scripts/           # Python & PowerShell build and utility scripts
├── LICENSE            # BSD 3-Clause License
└── README.md          # Project documentation
```

---

## 🛠️ Building From Source

### Prerequisites
1. **Windows 10 / 11 (64-bit)**
2. **Visual Studio 2022** (with *Desktop development with C++*, MFC, ATL, and Windows 10/11 SDK)
3. **Google depot_tools** configured in your `PATH`
4. At least 100 GB of free SSD storage

### Step-by-Step Build
```powershell
# 1. Clone this repository
git clone https://github.com/okinamo-o/Velox.git D:\Velox
cd D:\Velox

# 2. Fetch Chromium source via depot_tools
fetch --no-history chromium

# 3. Apply Velox Patches
python scripts/apply_patches.py

# 4. Generate build configuration
gn gen out/Default --args="target_os=\"win\" target_cpu=\"x64\" is_debug=false is_component_build=false symbol_level=0 enable_widevine=true proprietary_codecs=true ffmpeg_branding=\"Chrome\""

# 5. Compile Velox
autoninja -C out/Default chrome

# 6. Package Standalone Installer
autoninja -C out/Default mini_installer
```

---

## 📄 License & Acknowledgements

- **Velox** is open-source under the [BSD 3-Clause License](LICENSE).
- Chromium is a trademark of Google LLC. Velox is an independent open-source fork.
