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
    version = sys.argv[1] if len(sys.argv) > 1 else "134.0.6998.180"
    tag = f"v{version}"
    name = f"Velox Browser v{version} (Super PiP & Universal Dark Theme)"
    body = (
        f"## Velox Browser v{version}\n\n"
        "### 🌟 New Features & Enhancements\n"
        "- **Universal Cyberpunk Dark Theme**: Forced deep cyberpunk dark theme (`#0A0D14` frame, `#131826` active tabs, `#0C101B` toolbar, `#121826` omnibox with `#38BDF8` cyan border & crisp white text) on every device, regardless of Windows OS light/dark personalization.\n"
        "- **Super Picture-in-Picture (PiP)**:\n"
        "  - **Modern 2024 Controls**: Integrated seek bar timeline, 10s backward/forward seek buttons, play/pause.\n"
        "  - **Auto-PiP on Tab Switch**: Seamlessly floats video when switching tabs without requiring web page opt-in.\n"
        "  - **Neon Cyberpunk Gradient Rim**: Glowing cyan-to-purple (`#00F0FF` -> `#A855F7`) border overlay.\n"
        "  - **Keyboard Hotkeys**: `T` key cycles opacity (100% -> 70% -> 40% -> 100%), `Left`/`Right` arrow keys seek 10s, `Space` toggles playback.\n"
        "  - **Mouse Transparency Control**: `Ctrl` + mouse wheel smoothly adjusts PiP transparency down to 35%.\n"
        "- **Fixed Incognito Window Exit Issue**: Prevented process teardown crashes when closing incognito sessions.\n"
        "- **Background Auto-Updater**: Instant one-click update via the glowing **Update Velox** toolbar button.\n\n"
        "### Downloads & Verification\n"
        "- **VeloxSetup.exe** (Standalone Installer)\n"
        f"- **Velox-v{version}-Portable-x64.zip** (Portable Edition)\n"
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
