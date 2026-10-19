# VELOX — Windows Authenticode Code-Signing & Production Release Guide

> **Target Platform**: Windows 10 & Windows 11 (x64)  
> **Signing Engine**: Microsoft `signtool.exe` (Windows 10/11 SDK)  
> **Hash Algorithm**: SHA-256 with RFC 3161 Timestamping  
> **Artifacts**: `velox_installer.exe`, `velox.exe`, `chrome.dll`, `setup.exe`  

---

## 1. Overview & SmartScreen Reputation

When Windows users download an executable from the web, Microsoft Defender SmartScreen evaluates its digital signature. If an executable is unsigned or signed with an unrecognized untrusted certificate, Windows displays a full-screen warning:

> *"Windows protected your PC: Microsoft Defender SmartScreen prevented an unrecognized app from starting."*

To achieve a seamless global consumer release, all distributed VELOX executables and DLLs must be digitally signed with a valid Windows Authenticode certificate issued by a Microsoft-recognized Certificate Authority (CA).

### Certificate Types
1. **Extended Validation (EV) Code Signing (Recommended)**:
   - Instant SmartScreen reputation (zero or minimal warnings).
   - Requires private key storage in a FIPS 140-2 Level 2 hardware security module (USB token or Cloud HSM).
   - Compatible with DigiCert ONE / KeyLocker, Sectigo, or Azure Trusted Signing.
2. **Standard / OV Code Signing**:
   - Accumulates SmartScreen reputation gradually over download volume.
   - Distributed as a password-protected `.pfx` file or cloud token.

---

## 2. Release Signing Pipeline (`scripts/sign_binaries.py`)

VELOX includes an automated signing tool that wraps Microsoft SDK `signtool.exe`, ensuring correct signing flags, RFC 3161 timestamping, and dependency ordering.

### Signing Dependency Order
Binaries must be signed in strict bottom-up order so internal hashes remain valid:
1. `chrome.dll` (Core browser engine)
2. `setup.exe` (Chromium unpacker & registrar)
3. `chrome.exe` & `velox.exe` (Browser process launchers)
4. `velox_installer.exe` (Outer self-extracting distribution installer)

### Signing Commands

#### With a PFX Certificate File
```bash
python scripts/sign_binaries.py \
  --cert-file "C:\path\to\velox_release.pfx" \
  --cert-password "YourSecretPassword" \
  --timestamp-url "http://timestamp.digicert.com"
```

#### With an EV Token / Windows Certificate Store
```bash
python scripts/sign_binaries.py \
  --thumbprint "A1B2C3D4E5F67890123456789ABCDEF012345678" \
  --timestamp-url "http://timestamp.digicert.com"
```

#### Signature Audit & Verification Only
```bash
python scripts/sign_binaries.py --verify-only
```

---

## 3. Production Release Packaging (`scripts/package_release.py`)

The packaging script prepares the distribution directory in `releases/`:
- Copies the final signed `velox_installer.exe`.
- Updates `releases/version.json` with the installer's exact byte count and SHA-256 digest.
- Generates `SHA256SUMS.txt` and `SHA512SUMS.txt` cryptographic manifests.
- Optionally creates a portable archive `velox-v<version>-win-x64-portable.zip`.

```bash
# Package standard installer release
python scripts/package_release.py

# Package both installer and standalone portable ZIP
python scripts/package_release.py --portable
```

---

## 4. GitHub Actions CI/CD Pipeline

To automate builds, testing, signing, and distribution on GitHub, add `.github/workflows/release.yml`:

```yaml
name: VELOX Production Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-sign:
    runs-on: windows-2022
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run Test Suite
        run: python tests/run_tests.py

      - name: Package Release Manifests
        run: python scripts/package_release.py

      - name: Sign Binaries (Authenticode)
        if: env.CERT_BASE64 != ''
        env:
          CERT_BASE64: ${{ secrets.CODE_SIGNING_PFX_BASE64 }}
          CERT_PASS: ${{ secrets.CODE_SIGNING_PASSWORD }}
        run: |
          [System.IO.File]::WriteAllBytes("cert.pfx", [System.Convert]::FromBase64String($env:CERT_BASE64))
          python scripts/sign_binaries.py --cert-file cert.pfx --cert-password $env:CERT_PASS
          Remove-Item cert.pfx -Force

      - name: Publish GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            releases/velox_installer.exe
            releases/version.json
            releases/SHA256SUMS.txt
            releases/SHA512SUMS.txt
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 5. Security & Verification Checkpoint

Before publishing any global release build:
1. Ensure all unit and architectural tests pass: `python tests/run_tests.py`.
2. Verify reverse-apply cleanliness of all patches: Patch 0001 through Patch 0013.
3. Validate installer integrity with `python scripts/check_update.py --check-only`.
4. Inspect `releases/SHA256SUMS.txt` to confirm hash parity across distribution mirrors.
