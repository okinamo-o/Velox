# VELOX — DRM & Protected Media Architecture (Widevine CDM)

> **Component**: Widevine Content Decryption Module (CDM) Pipeline  
> **Key System**: `com.widevine.alpha`  
> **Standard**: W3C Encrypted Media Extensions (EME)  
> **Target Sites**: Netflix, Spotify, Disney+, Amazon Prime Video, Hulu  

---

## 1. Architectural Overview

Commercial streaming services require hardware- or software-backed digital rights management (DRM) via the W3C Encrypted Media Extensions (EME) specification. In Chromium-based browsers, this is implemented through the **Google Widevine Content Decryption Module (CDM)**.

### Legal and Open-Source Distribution Model
Open-source Chromium derivatives (including VELOX, Brave, Ungoogled-Chromium, and Vivaldi) cannot legally redistribute Google's proprietary signed `widevinecdm.dll` binary directly inside public Git repositories or open-source releases without a formal distribution license from Google LLC.

VELOX resolves this challenge using a compliant two-tier architecture:
1. **Native Media Pipeline Integration**: Compiled with `enable_widevine = true` and `enable_widevine_cdm_component = true`. The browser engine natively recognizes `com.widevine.alpha`, hooks CDM IPC channels, and parses CDM manifests.
2. **Dynamic Provisioning & Discovery**:
   - Primary: Looks in `chrome::DIR_BUNDLED_WIDEVINE_CDM` (`<ApplicationDir>\<Version>\WidevineCdm\`).
   - Secondary: Looks in `chrome::DIR_COMPONENT_UPDATED_WIDEVINE_CDM` (`%LOCALAPPDATA%\Velox\User Data\WidevineCdm\`).
   - Provisioner Tool: `scripts/install_widevine.py` discovers official signed CDM binaries from the host system or component servers and stages them into VELOX with zero user effort.

---

## 2. Directory Layout

The Widevine CDM directory must strictly match the following tree:

```
%LOCALAPPDATA%\Velox\Application\134.0.6998.178\WidevineCdm\
├── manifest.json
└── _platform_specific\
    └── win_x64\
        ├── widevinecdm.dll
        └── widevinecdm.dll.sig
```

### Manifest Schema (`manifest.json`)
```json
{
  "manifest_version": 2,
  "name": "WidevineCdm",
  "version": "4.10.3112.0",
  "x-cdm-codecs": "vp8,vp9.0,avc1",
  "x-cdm-host-versions": "1",
  "x-cdm-interface-versions": "10",
  "x-cdm-module-versions": "4"
}
```

---

## 3. GN Build Flags

In `src/out/Default/args.gn`:
```gn
enable_widevine = true
```

This compiles:
- `//third_party/widevine/cdm:buildflags` with `BUILDFLAG_INTERNAL_ENABLE_WIDEVINE() (1)` and `BUILDFLAG_INTERNAL_ENABLE_WIDEVINE_CDM_COMPONENT() (1)`.
- `//components/cdm/renderer/widevine_key_system_info.cc`: registers `com.widevine.alpha` in Blink's `KeySystemSupport` map.
- `//chrome/browser/component_updater/widevine_cdm_component_installer.cc`: registers component update and file detection hooks.

---

## 4. Operation & Provisioning Commands

### Check DRM & Widevine Status
```bash
python scripts/install_widevine.py --status
```

### Auto-Discover and Provision from Host
```bash
python scripts/install_widevine.py --provision
```

### Provision from Custom Source Folder
```bash
python scripts/install_widevine.py --source "C:\Path\To\WidevineCdm"
```

### Verification
Visit any DRM test site (e.g. `https://shaka-player-demo.appspot.com/` or `https://bitmovin.com/demos/drm`) or open Spotify / Netflix to confirm playback.
