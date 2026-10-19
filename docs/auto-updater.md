# VELOX — Remote Auto-Updater Specification & Architecture

> **Component**: `scripts/check_update.py`, `releases/version.json`, `VersionUpdaterWin`  
> **Target Platform**: Windows 10 / 11 (x64)  
> **Security Model**: Cryptographic SHA-256 Digest Verification, Decoupled from Google Omaha  

---

## 1. Architectural Overview

Standard Chromium relies on Google Update (Omaha) via proprietary COM interfaces (`IGoogleUpdate3Web`, `AppWeb`), which continuously attempt to query Google's update endpoints and fail with cryptic error codes on independent browser builds.

VELOX replaces this legacy dependency with an autonomous, privacy-preserving, and transparent update mechanism consisting of:
1. **A Decentralized Remote Version Manifest (`releases/version.json`)**: Hosted on the VELOX release server or GitHub Releases API, containing version numbers, release dates, changelog links, and binary checksums.
2. **Cryptographic SHA-256 Validation**: Every downloaded update binary is strictly verified against its expected cryptographic digest prior to staging or execution.
3. **Clean WebUI Integration**: The `chrome://settings/help` page cleanly reports version status and update readiness without Google Update COM failures.
4. **Autonomous Updater Utility (`scripts/check_update.py`)**: A multi-mode CLI and background tool supporting version checks, downloads, and unattended silent upgrades.
5. **Scheduled Background Automation**: An optional Windows Task Scheduler job (`VeloxUpdateCheck`) for daily non-intrusive update checks.

---

## 2. Remote Manifest Specification

The update server serves a static, lightweight JSON manifest at `https://updates.veloxbrowser.com/version.json` (or via GitHub Releases):

```json
{
  "name": "VELOX Browser",
  "version": "134.0.6998.178",
  "channel": "stable",
  "release_date": "2026-09-28",
  "min_os_version": "10.0.17763",
  "release_notes_url": "https://github.com/velox-browser/velox/releases/tag/v134.0.6998.178",
  "platforms": {
    "win_x64": {
      "installer_filename": "velox_installer.exe",
      "installer_url": "https://github.com/velox-browser/velox/releases/download/v134.0.6998.178/velox_installer.exe",
      "sha256": "9bb52c29da743ccfff170815ccbfe70e45480ea6db9265575041192eb8b2e3b4",
      "size_bytes": 141059584
    }
  }
}
```

### Schema Attributes
- `name`: Browser brand identifier.
- `version`: Dot-separated 4-part semantic version (`MAJOR.MINOR.BUILD.PATCH`).
- `channel`: Release channel (`stable`, `beta`, `nightly`).
- `min_os_version`: Minimum supported Windows build version.
- `platforms.win_x64.installer_url`: Direct HTTPS link to the installer artifact.
- `platforms.win_x64.sha256`: Lowercase 64-character SHA-256 digest of the release installer.
- `platforms.win_x64.size_bytes`: File size for download progress calculation and staging validation.

---

## 3. Update Lifecycle Flow

```
+------------------------------------------------------------------------+
| 1. Query Manifest (HTTPS / Local Release)                             |
|    Fetches version.json, parses remote 4-part version number.          |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| 2. Semantic Version Comparison                                         |
|    Local:  %LOCALAPPDATA%\Velox\Application\<version>\                 |
|    Remote: manifest["version"]                                         |
|    If Local >= Remote -> UP_TO_DATE (Terminate)                        |
|    If Local < Remote  -> UPDATE_AVAILABLE (Proceed)                    |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| 3. Download & Stage Installer                                          |
|    Streams velox_installer.exe to temporary staging directory.         |
|    Computes real-time streaming SHA-256 digest.                        |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| 4. Cryptographic Integrity Audit                                       |
|    Assert: Actual SHA-256 == manifest["sha256"]                        |
|    Mismatch? Abort, delete staged payload, log security error.         |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| 5. Silent In-Place Execution                                           |
|    Executes: velox_installer.exe --silent --do-not-launch-chrome       |
|    Chromium setup.exe extracts new version files alongside existing,    |
|    updating master symlinks and registry entries cleanly.              |
+------------------------------------------------------------------------+
```

---

## 4. Usage & Automation Commands

### Interactive / Check Only
```bash
python scripts/check_update.py --check-only
```

### Machine-Readable JSON Output (for CI/CD or Agent monitoring)
```bash
python scripts/check_update.py --json
```

### Download Update Only
```bash
python scripts/check_update.py --download --output-dir "D:\Velox\downloads"
```

### Download, Verify and Install Silently
```bash
python scripts/check_update.py --install
```

### Background Task Management
```cmd
:: Install scheduled daily update check
scripts\register_updater_task.bat

:: Uninstall scheduled update check
scripts\register_updater_task.bat --uninstall
```
