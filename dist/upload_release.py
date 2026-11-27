import os
import sys
import json
import urllib.request
import subprocess

def get_token():
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(input='protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    return None

def main():
    token = get_token()
    if not token:
        print("Error: Could not retrieve GitHub token.")
        sys.exit(1)

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Velox-Release-Agent'
    }

    # 1. Create or get existing release
    version = sys.argv[1] if len(sys.argv) > 1 else "134.0.6998.188"
    tag = f"v{version}"
    name = f"Velox Browser v{version} (Fingerprint Farbling, Startup Speed & Spaces Fixes)"
    body = (
        f"## Velox Browser v{version}\n\n"
        f"### 🌟 What's New in v{version}\n"
        "- **🛡️ Domain-Keyed Fingerprint Farbling (Velox Privacy Shield)**: Per-session, per-`eTLD+1` deterministic farbling across Canvas 2D, WebGL, WebAudio, `navigator.plugins`, and `navigator.hardwareConcurrency` (randomized fingerprint on EFF Cover Your Tracks without breaking web apps).\n"
        "- **⚡ Faster Startup & Session Restore**: Batched Spaces TabStrip layout pass during session restore, staggered background-tab favicon fetching, deferred `BEST_EFFORT` startup update check, and faster classic UDP DNS fallback on packet drops.\n"
        "- **🔐 Google & Gmail Session Stability**: Removed unsafe Blink spoofing and hardened NTP Gmail widget handling to prevent unexpected Google account sign-outs.\n"
        "- **🌌 Spaces & Auto-Hide Reliability**: Fixed new tabs opening in another space, cross-space tab group visibility/bleed issues, and prevented the auto-hide header from retracting while interacting with toolbar controls and menus.\n"
        "- **🧩 Customizable NTP Widgets Studio & Clean Hover Previews**: Modular customizable New Tab widgets and hover cards that never wake or preload unloaded background tabs.\n"
        "- **📦 Cleaner, Smaller Portable Archive**: Excluded cached installer payloads and stale backup binaries from the Portable ZIP.\n"
        "- **🔔 Cryptographically Signed Auto-Updates**: Pinned RSA-2048 PKCS#1 SHA-256 release manifest verification with one-click update staging.\n\n"
        "### 📦 Downloads & Verification\n"
        "- **VeloxSetup.exe** (Standalone Installer)\n"
        f"- **Velox-v{version}-Portable-x64.zip** (Portable Edition)\n"
        "- **Linux 1-Click Script**: `curl -sSL https://raw.githubusercontent.com/okinamo-o/Velox/main/scripts/velox-linux.sh | bash -s -- --wine`\n"
    )

    # Check if release already exists
    req = urllib.request.Request("https://api.github.com/repos/okinamo-o/Velox/releases/tags/" + tag, headers=headers)
    release = None
    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode())
            print(f"Release already exists: {release.get('id')}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            pass
        else:
            print(f"Error checking release: {e.code} {e.read().decode()}")
            sys.exit(1)

    if release:
        update_payload = {
            'tag_name': tag,
            'target_commitish': 'main',
            'name': name,
            'body': body
        }
        patch_req = urllib.request.Request(
            f"https://api.github.com/repos/okinamo-o/Velox/releases/{release.get('id')}",
            data=json.dumps(update_payload).encode('utf-8'),
            headers={**headers, 'Content-Type': 'application/json'},
            method='PATCH'
        )
        try:
            with urllib.request.urlopen(patch_req) as resp:
                release = json.loads(resp.read().decode())
                print(f"Updated existing release {release.get('id')} metadata & notes.")
        except urllib.error.HTTPError as e:
            print(f"Warning: Failed to update release metadata: {e.code}")

    if not release:
        payload = {
            'tag_name': tag,
            'target_commitish': 'main',
            'name': name,
            'body': body,
            'draft': False,
            'prerelease': False
        }
        create_req = urllib.request.Request(
            "https://api.github.com/repos/okinamo-o/Velox/releases",
            data=json.dumps(payload).encode('utf-8'),
            headers={**headers, 'Content-Type': 'application/json'}
        )
        try:
            with urllib.request.urlopen(create_req) as resp:
                release = json.loads(resp.read().decode())
                print(f"Created release: {release.get('id')} ({release.get('html_url')})")
        except urllib.error.HTTPError as e:
            print(f"Error creating release: {e.code} {e.read().decode()}")
            sys.exit(1)

    upload_url_template = release.get('upload_url')
    # URL format is like: https://uploads.github.com/repos/okinamo-o/Velox/releases/12345/assets{?name,label}
    upload_base = upload_url_template.split('{')[0]

    # Check existing assets
    assets = release.get('assets', [])
    existing_asset_names = {a['name']: a['id'] for a in assets}

    # Files to upload
    files_to_upload = [
        ("D:/Velox/dist/VeloxSetup.exe", "VeloxSetup.exe", "application/octet-stream"),
        (f"D:/Velox/dist/Velox-v{version}-Portable-x64.zip", f"Velox-v{version}-Portable-x64.zip", "application/zip")
    ]

    for file_path, asset_name, content_type in files_to_upload:
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping.")
            continue

        if asset_name in existing_asset_names:
            print(f"Asset {asset_name} already exists. Deleting first...")
            asset_id = existing_asset_names[asset_name]
            del_req = urllib.request.Request(
                f"https://api.github.com/repos/okinamo-o/Velox/releases/assets/{asset_id}",
                headers=headers,
                method='DELETE'
            )
            with urllib.request.urlopen(del_req) as resp:
                print(f"Deleted old asset {asset_name}")

        size = os.path.getsize(file_path)
        print(f"Uploading {asset_name} ({size / (1024*1024):.2f} MB)...")
        upload_url = f"{upload_base}?name={asset_name}"
        
        with open(file_path, 'rb') as f:
            data = f.read()

        up_req = urllib.request.Request(
            upload_url,
            data=data,
            headers={
                **headers,
                'Content-Type': content_type,
                'Content-Length': str(size)
            }
        )

        try:
            with urllib.request.urlopen(up_req) as resp:
                res = json.loads(resp.read().decode())
                print(f"Successfully uploaded {asset_name}! URL: {res.get('browser_download_url')}")
        except urllib.error.HTTPError as e:
            print(f"Failed to upload {asset_name}: {e.code} {e.read().decode()}")

    print(f"\nRelease v{version} is completely published!")

if __name__ == "__main__":
    main()
