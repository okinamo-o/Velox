<div align="center">

# ⚡ VELOX BROWSER

### The Ultra-Fast, Shielded Web Browser

[![Release](https://img.shields.io/github/v/release/okinamo-o/Velox?color=00f0ff&label=Release&style=for-the-badge)](https://github.com/okinamo-o/Velox/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-a855f7?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/okinamo-o/Velox/releases)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-10b981?style=for-the-badge)](LICENSE)
[![Chromium](https://img.shields.io/badge/Engine-Chromium%20134%20Ultra-blue?style=for-the-badge&logo=googlechrome)](https://chromium.googlesource.com/chromium/src)

<br/>

**Velox** is a next-generation desktop browser re-architected for raw speed, clean aesthetics, and zero distractions. Built upon custom-tuned Chromium 134, Velox strips away telemetry and background clutter while introducing deep system-level optimizations and modern workflows.

[**Download for Windows**](https://github.com/okinamo-o/Velox/releases/latest/download/VeloxSetup.exe) • [**Download for Linux**](#-linux-installation) • [**Portable ZIP**](https://github.com/okinamo-o/Velox/releases/latest/download/Velox-v134.0.6998.183-Portable-x64.zip) • [**View Showcase Site**](dist/website/index.html)

</div>

---

## ✨ Key Highlights

### 🛡️ Native Velox Shield
Content blocking baked directly into the network loader pipeline. Ads, third-party tracking beacons, cryptominers, and fingerprinting scripts are dropped before they ever reach the DOM—eliminating JavaScript bloat and speeding up page loads by up to 3×.

### 🏝️ Opera One Tab Islands
Tabs group automatically into color-coded context islands. Collapse entire research clusters with one click, slide smoothly between active sessions, and enjoy custom glowing visual identifiers.

### 🌌 Customizable Spaces (Workspaces)
Effortlessly organize tabs into isolated workflows (e.g. *Work*, *Personal*, *Gaming*, *Dev*, *Study*).
- Switch instantly with hotkeys (<kbd>Ctrl</kbd> + <kbd>1</kbd> / <kbd>2</kbd> / <kbd>3</kbd> or <kbd>Alt</kbd> + <kbd>1</kbd> / <kbd>2</kbd> / <kbd>3</kbd>) or the toolbar pill.
- **Double-click or Right-click** any Space to rename it with custom names and quick preset chips.
- Inactive spaces freeze background tabs automatically to save 0 KB wasted RAM.

### 📝 New Tab Scratchpad & Focus Dashboard
`chrome://newtab` now features a glassmorphic command center with a persistent quick scratchpad, focus session timer, and real-time shield & RAM statistics.

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

### 🪟 Windows Installation

#### Option 1: Standalone Installer (Recommended)
Download and run the latest standalone setup:
👉 **[Download VeloxSetup.exe](https://github.com/okinamo-o/Velox/releases/latest/download/VeloxSetup.exe)**

#### Option 2: Portable Edition (Zero Install)
Download the portable ZIP archive, extract it anywhere (including a USB drive), and run `velox.exe`:
👉 **[Download Portable ZIP](https://github.com/okinamo-o/Velox/releases/latest/download/Velox-v134.0.6998.183-Portable-x64.zip)**

#### Option 3: Windows Package Manager (`winget`)
Install in one command via PowerShell or Command Prompt:
```powershell
winget install Velox.VeloxBrowser
```

---

### 🐧 Linux Installation

#### Option 1: 1-Click Quick Runner (Wine / Proton)
Run this single command in your terminal to download Velox, configure the environment, and integrate application menu shortcuts:
```bash
curl -sSL https://raw.githubusercontent.com/okinamo-o/Velox/main/scripts/velox-linux.sh | bash -s -- --wine
```

#### Option 2: Build Native Linux Binary from Source
You can compile native Velox directly on Linux using our patch set:
```bash
# View interactive build instructions:
curl -sSL https://raw.githubusercontent.com/okinamo-o/Velox/main/scripts/velox-linux.sh | bash -s -- --build
```
Or follow the [Building From Source](#-building-from-source) instructions below.

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

### Building on Windows (10 / 11 64-bit)
1. **Prerequisites**: Visual Studio 2022 (with *Desktop development with C++*, MFC, ATL, and Windows 10/11 SDK) and Google `depot_tools`.
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
autoninja -C out/Default chrome mini_installer
```

### Building on Linux (Ubuntu / Debian / Arch / Fedora)
1. **Prerequisites**: Google `depot_tools`, `git`, `python3`, `curl`, and standard C++ build essentials.
```bash
# 1. Fetch Chromium source code
mkdir -p ~/velox-src && cd ~/velox-src
fetch --nohooks chromium
cd src && git checkout -b velox-134 refs/tags/134.0.6998.182
gclient sync -D

# 2. Clone Velox and apply patches
git clone https://github.com/okinamo-o/Velox.git ~/Velox
for p in ~/Velox/patches/*.patch; do patch -p1 -N < "$p" || true; done

# 3. Generate Linux build configuration
gn gen out/Release --args="target_os=\"linux\" target_cpu=\"x64\" is_debug=false is_component_build=false is_official_build=true symbol_level=0 enable_widevine=true proprietary_codecs=true ffmpeg_branding=\"Chrome\""

# 4. Compile native Linux binary
autoninja -C out/Release chrome
```

---

## 📄 License & Acknowledgements

- **Velox** is open-source under the [BSD 3-Clause License](LICENSE).
- Chromium is a trademark of Google LLC. Velox is an independent open-source fork.
