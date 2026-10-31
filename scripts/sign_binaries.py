#!/usr/bin/env python3
"""
VELOX Windows Authenticode Code-Signing & Verification Tool

Automates digital signing of VELOX binaries and installers using Microsoft signtool.exe.
Supports Standard/EV PFX files, Windows Certificate Store, and RFC 3161 timestamping.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

DEFAULT_TIMESTAMP_URL = "http://timestamp.digicert.com"

def find_signtool():
    """Locates signtool.exe in Windows Kits SDK directory."""
    sdk_bin = Path(r"C:\Program Files (x86)\Windows Kits\10\bin")
    if not sdk_bin.exists():
        sdk_bin = Path(r"C:\Program Files\Windows Kits\10\bin")

    if sdk_bin.exists():
        candidates = list(sdk_bin.glob("**/x64/signtool.exe"))
        if candidates:
            # Sort by version number descending
            candidates.sort(reverse=True)
            return candidates[0]

    # Check PATH
    try:
        res = subprocess.run(["where", "signtool"], capture_output=True, text=True)
        if res.returncode == 0:
            lines = res.stdout.strip().splitlines()
            if lines:
                return Path(lines[0])
    except Exception:
        pass

    return None

def verify_signature(binary_path, signtool_path=None, allow_self_signed=False, expected_publisher=None):
    """Verifies Authenticode signature using signtool.exe or PowerShell Get-AuthenticodeSignature."""
    binary_path = Path(binary_path).resolve()
    if not binary_path.exists():
        return False, f"File not found: {binary_path}"

    signtool = signtool_path or find_signtool()
    if signtool and signtool.exists():
        # First check full public verification (/pa)
        res_pa = subprocess.run(
            [str(signtool), "verify", "/pa", "/v", str(binary_path)],
            capture_output=True,
            text=True
        )
        if res_pa.returncode == 0:
            if expected_publisher and expected_publisher not in res_pa.stdout:
                return False, f"Signed, but publisher does not match '{expected_publisher}'"
            return True, "Valid Authenticode signature (Trusted Root CA)"

        # Check if signed but untrusted root (e.g. self-signed test cert) only when explicitly permitted
        if allow_self_signed:
            res_v = subprocess.run(
                [str(signtool), "verify", "/v", str(binary_path)],
                capture_output=True,
                text=True
            )
            if "Signing Certificate Chain" in res_v.stdout:
                signer = "Unknown"
                for line in res_v.stdout.splitlines():
                    if "Issued to:" in line:
                        signer = line.strip().replace("Issued to: ", "")
                        break
                if expected_publisher and expected_publisher not in signer:
                    return False, f"Signed by [{signer}], does not match expected [{expected_publisher}]"
                return True, f"Signed by [{signer}] (Self-Signed / Private Root)"

        return False, "Unsigned or untrusted binary"
    else:
        # Fallback to PowerShell
        ps_cmd = (
            f"$sig = Get-AuthenticodeSignature -FilePath '{binary_path}'; "
            f"$status = $sig.Status.ToString(); "
            f"$subject = if ($sig.SignerCertificate) {{ $sig.SignerCertificate.Subject }} else {{ '' }}; "
            f"Write-Output ($status + '|||' + $subject)"
        )
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        out = res.stdout.strip()
        parts = out.split("|||", 1)
        status = parts[0] if parts else ""
        subject = parts[1] if len(parts) > 1 else ""

        if status != "Valid":
            return False, f"Invalid Authenticode status: {status}"

        if expected_publisher and expected_publisher.lower() not in subject.lower():
            return False, f"Signed, but publisher '{subject}' does not match expected '{expected_publisher}'"

        return True, f"Valid Authenticode signature ({subject})"

def sign_binary(binary_path, signtool, cert_file=None, cert_password=None,
                thumbprint=None, subject_name=None, timestamp_url=DEFAULT_TIMESTAMP_URL):
    """Signs a binary using Microsoft signtool.exe."""
    binary_path = Path(binary_path).resolve()
    if not binary_path.exists():
        print(f"[ERROR] Target file not found: {binary_path}")
        return False

    cmd = [
        str(signtool),
        "sign",
        "/fd", "SHA256",
        "/tr", timestamp_url,
        "/td", "SHA256",
    ]

    if cert_file:
        cmd.extend(["/f", str(Path(cert_file).resolve())])
        if cert_password:
            cmd.extend(["/p", cert_password])
    elif thumbprint:
        cmd.extend(["/sha1", thumbprint])
    elif subject_name:
        cmd.extend(["/n", subject_name])
    else:
        print("[ERROR] No certificate specified. Provide --cert-file, --thumbprint, or --subject-name.")
        return False

    cmd.append(str(binary_path))

    print(f"Signing: {binary_path.name} ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[SUCCESS] Signed {binary_path.name}")
        return True
    else:
        print(f"[FAILED] Failed to sign {binary_path.name}:\n{res.stdout}\n{res.stderr}")
        return False

def create_test_certificate(pfx_path, password="velox-test-password"):
    """Generates a self-signed code signing certificate for local testing."""
    pfx_path = Path(pfx_path).resolve()
    pfx_path.parent.mkdir(parents=True, exist_ok=True)
    
    ps_script = f"""
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=VELOX Test Code Signing, O=The VELOX Authors" -CertStoreLocation "Cert:\\CurrentUser\\My" -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(1)
    $pwd = ConvertTo-SecureString -String "{password}" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "{pfx_path}" -Password $pwd | Out-Null
    Write-Output "Certificate created: $($cert.Thumbprint)"
    """
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if res.returncode == 0 and pfx_path.exists():
        print(f"[OK] Self-signed test certificate created at: {pfx_path}")
        print(f"     Password: {password}")
        return True
    else:
        print(f"[ERROR] Failed to create test certificate: {res.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="VELOX Windows Authenticode Signing Tool")
    parser.add_argument("--cert-file", default=None, help="Path to .pfx certificate file")
    parser.add_argument("--cert-password", default=None, help="Password for .pfx file")
    parser.add_argument("--thumbprint", default=None, help="Certificate SHA-1 thumbprint in Certificate Store")
    parser.add_argument("--subject-name", default=None, help="Certificate Subject Name in Certificate Store")
    parser.add_argument("--timestamp-url", default=DEFAULT_TIMESTAMP_URL, help="RFC 3161 Timestamp URL")
    parser.add_argument("--target", default=None, help="Specific file to sign or verify")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing signatures")
    parser.add_argument("--allow-self-signed", action="store_true", help="Allow self-signed test certificates during verification")
    parser.add_argument("--expected-publisher", default=None, help="Expected publisher substring to match during verification")
    parser.add_argument("--require-all-targets", action="store_true", help="Fail verification if any default release binary is missing")
    parser.add_argument("--create-test-cert", default=None, help="Generate a self-signed PFX test certificate at given path")
    args = parser.parse_args()

    signtool = find_signtool()
    print("=" * 60)
    print(" VELOX WINDOWS AUTHENTICODE SIGNING TOOL")
    print("=" * 60)
    print(f"signtool.exe: {signtool or 'NOT FOUND (Install Windows 10/11 SDK)'}")

    if args.create_test_cert:
        success = create_test_certificate(args.create_test_cert, args.cert_password or "velox-test-password")
        return 0 if success else 1

    repo_root = Path(__file__).resolve().parent.parent
    default_targets = [
        repo_root / "src" / "out" / "Default" / "chrome.dll",
        repo_root / "src" / "out" / "Default" / "chrome.exe",
        repo_root / "src" / "out" / "Default" / "velox.exe",
        repo_root / "src" / "out" / "Default" / "setup.exe",
        repo_root / "src" / "out" / "Default" / "velox_installer.exe",
        repo_root / "src" / "out" / "Default" / "mini_installer.exe",
    ]

    if args.require_all_targets and not args.target:
        missing = [p for p in default_targets if not p.exists()]
        if missing:
            print("[ERROR] Required release binaries are missing:")
            for path in missing:
                print(f"  {path}")
            return 1

    targets = [Path(args.target)] if args.target else [p for p in default_targets if p.exists()]

    if args.verify_only:
        print(f"\nVerifying signatures for {len(targets)} binaries:")
        all_valid = True
        for t in targets:
            valid, msg = verify_signature(
                t, signtool,
                allow_self_signed=args.allow_self_signed,
                expected_publisher=args.expected_publisher
            )
            if not valid:
                status_str = "[UNTRUSTED / INVALID]"
            elif "Self-Signed / Private Root" in msg:
                status_str = "[SELF-SIGNED / DEV ONLY]"
            else:
                status_str = "[SIGNED & TRUSTED]"
            print(f"  {status_str} {t.name}")
            if not valid:
                all_valid = False
        return 0 if all_valid else 1

    if not signtool:
        print("[ERROR] signtool.exe is required for signing. Please install the Windows SDK.")
        return 1

    if not (args.cert_file or args.thumbprint or args.subject_name):
        print("[ERROR] No certificate credentials provided.")
        print("Usage:")
        print("  python scripts/sign_binaries.py --cert-file <path.pfx> --cert-password <pwd>")
        print("  python scripts/sign_binaries.py --thumbprint <SHA1_THUMBPRINT>")
        print("  python scripts/sign_binaries.py --verify-only")
        return 1

    print(f"\nSigning {len(targets)} binaries in dependency order:")
    failed = 0
    for t in targets:
        if not sign_binary(t, signtool, args.cert_file, args.cert_password,
                           args.thumbprint, args.subject_name, args.timestamp_url):
            failed += 1

    print(f"\nSigning completed: {len(targets) - failed} succeeded, {failed} failed.")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
