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
    version = sys.argv[1] if len(sys.argv) > 1 else "134.0.6998.186"
    tag = f"v{version}"
    name = f"Velox Browser v{version} (Universal Media Engine, Morphing Spaces & Diagnostics)"
    body = (
        f"## Velox Browser v{version}\n\n"
        f"### 🌟 What's New in v{version}\n"
        "- **🎬 Universal Video Playback & Adaptive Decoders**: Full D3D11/DXVA hardware acceleration for 1080p, 1440p, 4K60, and HDR video streams. Enabled resolution-based decoder priority (>=360p HW / <360p SW) to optimize GPU context switches.\n"
        "- **🛡️ Playback-Safe Memory Protection**: Protected active video renderers from mid-playback Skia/Blink cache purges during moderate system memory pressure on 8GB-16GB PCs, eliminating stutter and ABR quality drops.\n"
        "- **⚡ Adaptive Hardware Concurrency**: Dynamic processor tiering ({2, 4, 8, 12, 16}) prevents low-end CPUs from being oversubscribed by media/WASM workers while scaling up to 16 threads on high-end CPUs.\n"
        "- **📊 Native Media Diagnostics (`velox://media`)**: Interactive privileged WebUI reporting GPU/driver telemetry, DXVA profiles, DirectComposition overlays, live MediaCapabilities probes, frame drop statistics, and local diagnostics export.\n"
        "- **🌌 Morphing Spaces Switcher & Tab Previews**: Assembles spaces into a single morphing toolbar button with cubic slide animation, interactive tab hover preview cards, '+' dynamic space creation, and end-of-space tab placement.\n"
        "- **🏝️ Pinned & Top Sites Weekly History**: Shows the week's most-used sites powered by `HistoryService` and domain deduplication, with clean Deep Obsidian styling.\n"
        "- **🔮 Cyber-Glass Tab Context Menu**: Redesigned native menu with glowing cyan-to-violet borders, floating pills, keycap shortcut badges, and crisp action icons.\n"
        "- **🛡️ Built-in Velox Shield**: Native intelligent tracker and ad blocking with zero extra resource overhead.\n"
        "- **🔔 Cryptographically Signed Auto-Updates**: In-browser auto-update detector backed by pinned RSA-2048 PKCS#1 SHA-256 release manifest signatures.\n\n"
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
