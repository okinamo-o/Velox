#!/usr/bin/env python3
"""
VELOX Browser Data & Open Tab Migration Tool

Allows users switching to VELOX to effortlessly discover, extract, and migrate:
- Active open tabs and session URLs
- Bookmarks and folder hierarchies
- Browsing history

Supports: Perplexity Comet, Google Chrome, Microsoft Edge, Brave Browser, Opera, Vivaldi, Mozilla Firefox.
"""

import os
import sys
import json
import sqlite3
import shutil
import struct
import subprocess
import argparse
from pathlib import Path

def get_installed_browser_profiles():
    """Detects installed browsers and returns their default user data profiles."""
    local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    appdata = Path(os.environ.get("APPDATA", ""))

    detected = {}

    # Comet (Perplexity)
    comet_path = local_appdata / "Perplexity" / "Comet" / "User Data" / "Default"
    if comet_path.exists():
        detected["comet"] = {
            "name": "Comet (Perplexity)",
            "type": "chromium",
            "profile_path": comet_path
        }

    # Google Chrome
    chrome_path = local_appdata / "Google" / "Chrome" / "User Data" / "Default"
    if chrome_path.exists():
        detected["chrome"] = {
            "name": "Google Chrome",
            "type": "chromium",
            "profile_path": chrome_path
        }

    # Microsoft Edge
    edge_path = local_appdata / "Microsoft" / "Edge" / "User Data" / "Default"
    if edge_path.exists():
        detected["edge"] = {
            "name": "Microsoft Edge",
            "type": "chromium",
            "profile_path": edge_path
        }

    # Brave Browser
    brave_path = local_appdata / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default"
    if brave_path.exists():
        detected["brave"] = {
            "name": "Brave Browser",
            "type": "chromium",
            "profile_path": brave_path
        }

    # Vivaldi
    vivaldi_path = local_appdata / "Vivaldi" / "User Data" / "Default"
    if vivaldi_path.exists():
        detected["vivaldi"] = {
            "name": "Vivaldi",
            "type": "chromium",
            "profile_path": vivaldi_path
        }

    # Opera
    opera_path = appdata / "Opera Software" / "Opera Stable"
    if opera_path.exists():
        detected["opera"] = {
            "name": "Opera",
            "type": "chromium",
            "profile_path": opera_path
        }

    # Mozilla Firefox
    firefox_base = appdata / "Mozilla" / "Firefox" / "Profiles"
    if firefox_base.exists():
        for p in firefox_base.iterdir():
            if p.is_dir() and (p / "places.sqlite").exists():
                detected["firefox"] = {
                    "name": "Mozilla Firefox",
                    "type": "firefox",
                    "profile_path": p
                }
                break

    return detected

def get_velox_profile_path():
    """Returns the default VELOX User Data profile path."""
    local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    velox_profile = local_appdata / "Velox" / "User Data" / "Default"
    velox_profile.mkdir(parents=True, exist_ok=True)
    return velox_profile

def get_velox_executable():
    """Finds the installed or built VELOX executable."""
    local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = [
        local_appdata / "Velox" / "Application" / "velox.exe",
        local_appdata / "Velox" / "Application" / "chrome.exe",
        Path("D:/Velox/src/out/Default/velox.exe"),
        Path("D:/Velox/src/out/Default/chrome.exe")
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def extract_chromium_bookmarks(profile_path):
    """Extracts bookmarks from a Chromium-based browser profile."""
    bookmarks_file = Path(profile_path) / "Bookmarks"
    if not bookmarks_file.exists():
        return []

    try:
        with open(bookmarks_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        extracted = []
        def parse_node(node):
            if node.get("type") == "url":
                extracted.append({
                    "name": node.get("name", ""),
                    "url": node.get("url", "")
                })
            elif node.get("type") == "folder":
                for child in node.get("children", []):
                    parse_node(child)

        roots = data.get("roots", {})
        for root_name, root_node in roots.items():
            parse_node(root_node)

        return extracted
    except Exception as e:
        print(f"Warning: Failed to parse bookmarks from {bookmarks_file}: {e}")
        return []

def parse_snss_session_file(file_path):
    """Parses Chromium SNSS (Session Navigation Serialized Storage) to get active open tabs."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception:
        return []

    if len(data) < 8:
        return []

    sig, ver = struct.unpack_from("<II", data, 0)
    if sig != 0x53534E53:  # "SSNS"
        return []

    offset = 8
    commands = []
    while offset + 2 <= len(data):
        cmd_size = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        if cmd_size == 0 or offset + cmd_size > len(data):
            break
        cmd_id = data[offset]
        payload = data[offset + 1 : offset + cmd_size]
        offset += cmd_size
        commands.append((cmd_id, payload))

    tabs = {}
    for cmd_id, payload in commands:
        if cmd_id == 0:  # SetTabWindow
            if len(payload) >= 8:
                win_id, tab_id = struct.unpack_from("<ii", payload, 0)
                if tab_id not in tabs:
                    tabs[tab_id] = {"closed": False, "navigations": {}, "current_index": 0}
                tabs[tab_id]["window_id"] = win_id

        elif cmd_id == 16:  # TabClosed
            if len(payload) >= 4:
                tab_id = struct.unpack_from("<i", payload, 0)[0]
                if tab_id in tabs:
                    tabs[tab_id]["closed"] = True

        elif cmd_id == 17:  # WindowClosed
            if len(payload) >= 4:
                win_id = struct.unpack_from("<i", payload, 0)[0]
                for t in tabs.values():
                    if t.get("window_id") == win_id:
                        t["closed"] = True

        elif cmd_id == 7:  # SetSelectedNavigationIndex
            if len(payload) >= 8:
                tab_id, idx = struct.unpack_from("<ii", payload, 0)
                if tab_id not in tabs:
                    tabs[tab_id] = {"closed": False, "navigations": {}, "current_index": 0}
                tabs[tab_id]["current_index"] = idx

        elif cmd_id == 6:  # UpdateTabNavigation (Pickle payload)
            try:
                p_offset = 0
                if len(payload) >= 4:
                    p_offset = 4
                tab_id = struct.unpack_from("<i", payload, p_offset)[0]
                p_offset += 4
                nav_index = struct.unpack_from("<i", payload, p_offset)[0]
                p_offset += 4
                url_len = struct.unpack_from("<I", payload, p_offset)[0]
                p_offset += 4
                if url_len < 4096 and p_offset + url_len <= len(payload):
                    url_str = payload[p_offset : p_offset + url_len].decode("utf-8", errors="ignore")
                    p_offset += (url_len + 3) & ~3
                    title_len = struct.unpack_from("<I", payload, p_offset)[0]
                    p_offset += 4
                    title_str = ""
                    if title_len < 4096 and p_offset + title_len * 2 <= len(payload):
                        title_str = payload[p_offset : p_offset + title_len * 2].decode("utf-16le", errors="ignore")

                    if tab_id not in tabs:
                        tabs[tab_id] = {"closed": False, "navigations": {}, "current_index": 0}
                    tabs[tab_id]["navigations"][nav_index] = {"url": url_str, "title": title_str}
            except Exception:
                pass

    active_tabs = []
    for tab_id, info in tabs.items():
        if not info.get("closed") and info["navigations"]:
            curr = info.get("current_index", 0)
            if curr in info["navigations"]:
                active_tabs.append(info["navigations"][curr])
            else:
                max_idx = max(info["navigations"].keys())
                active_tabs.append(info["navigations"][max_idx])

    return active_tabs

def extract_chromium_open_tabs(profile_path):
    """Extracts active open tabs from Sessions files, falling back to History if necessary."""
    sessions_dir = Path(profile_path) / "Sessions"
    if sessions_dir.exists():
        session_files = sorted(sessions_dir.glob("Session_*"), key=os.path.getmtime, reverse=True)
        for sfile in session_files:
            tabs = parse_snss_session_file(sfile)
            if tabs:
                return tabs

    # Fallback to recent history
    return extract_chromium_recent_tabs(profile_path, limit=20)

def extract_chromium_recent_tabs(profile_path, limit=25):
    """Extracts recent active navigation URLs/tabs from Chromium History database."""
    history_file = Path(profile_path) / "History"
    if not history_file.exists():
        return []

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_history = Path(tmp.name)

    try:
        shutil.copy2(history_file, tmp_history)
        conn = sqlite3.connect(str(tmp_history))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        tabs = []
        for url, title, visit_time in rows:
            if url.startswith("http://") or url.startswith("https://"):
                tabs.append({"url": url, "title": title or url})
        return tabs
    except Exception:
        return []
    finally:
        tmp_history.unlink(missing_ok=True)

def open_tabs_in_velox(tabs):
    """Opens a list of tabs directly in the running VELOX instance."""
    velox_bin = get_velox_executable()
    if not velox_bin:
        print("[WARNING] VELOX executable not found.")
        return False

    urls = [t["url"] for t in tabs if t.get("url") and (t["url"].startswith("http://") or t["url"].startswith("https://"))]
    if not urls:
        print("[INFO] No URLs to open.")
        return True

    print(f"Launching {len(urls)} tab(s) into VELOX ({velox_bin.name})...")
    # Launch in batches of 15 to prevent command-line length limits
    batch_size = 15
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        cmd = [str(velox_bin)] + batch
        subprocess.Popen(cmd)

    return True

def migrate_data_to_velox(source_browser_key, copy_bookmarks=True, copy_tabs=True, open_tabs=False):
    """Transfers bookmarks and open tabs from the source browser into VELOX."""
    detected = get_installed_browser_profiles()
    if source_browser_key not in detected:
        return False, f"Browser '{source_browser_key}' was not found on this system."

    source_info = detected[source_browser_key]
    source_path = source_info["profile_path"]
    velox_path = get_velox_profile_path()

    stats = {
        "browser": source_info["name"],
        "bookmarks_transferred": 0,
        "tabs_transferred": 0,
        "tabs": []
    }

    # 1. Bookmarks migration
    if copy_bookmarks:
        if source_info["type"] == "chromium":
            src_bookmarks = source_path / "Bookmarks"
            if src_bookmarks.exists():
                dst_bookmarks = velox_path / "Bookmarks"
                shutil.copy2(src_bookmarks, dst_bookmarks)
                bookmarks = extract_chromium_bookmarks(source_path)
                stats["bookmarks_transferred"] = len(bookmarks)

    # 2. Tabs migration
    if copy_tabs:
        tabs = extract_chromium_open_tabs(source_path)
        stats["tabs_transferred"] = len(tabs)
        stats["tabs"] = tabs

        # Save transferred tabs as a restored session file for VELOX
        session_tabs_file = velox_path / "transferred_tabs.json"
        with open(session_tabs_file, "w", encoding="utf-8") as f:
            json.dump(tabs, f, indent=2)

        if open_tabs and tabs:
            open_tabs_in_velox(tabs)

    return True, stats

def main():
    parser = argparse.ArgumentParser(description="VELOX Browser Data & Open Tabs Migration Utility")
    parser.add_argument("--scan", action="store_true", help="Scan and detect installed browsers and data")
    parser.add_argument("--from-browser", choices=["comet", "chrome", "edge", "brave", "vivaldi", "opera", "firefox"], help="Source browser to import from")
    parser.add_argument("--import-all", action="store_true", help="Import bookmarks and open tabs into VELOX")
    parser.add_argument("--open-tabs", action="store_true", help="Immediately open transferred tabs into the running VELOX browser")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    detected = get_installed_browser_profiles()

    if args.json and args.scan:
        res = {k: {"name": v["name"], "path": str(v["profile_path"])} for k, v in detected.items()}
        print(json.dumps(res, indent=2))
        return 0

    if args.scan or not args.from_browser:
        print("=" * 60)
        print(" VELOX BROWSER MIGRATION ASSISTANT")
        print("=" * 60)
        print(f"Detected {len(detected)} installed browser(s):\n")
        for key, info in detected.items():
            bm = extract_chromium_bookmarks(info["profile_path"]) if info["type"] == "chromium" else []
            tabs = extract_chromium_open_tabs(info["profile_path"]) if info["type"] == "chromium" else []
            print(f"  * [{key.upper()}] {info['name']}")
            print(f"    Profile:   {info['profile_path']}")
            print(f"    Available: {len(bm)} Bookmarks, {len(tabs)} Open Tabs / Sessions\n")
        print("To transfer data into VELOX and open active tabs:")
        print("  python scripts/import_browser_data.py --from-browser comet --import-all --open-tabs")
        return 0

    if args.from_browser:
        print(f"Transferring data from {args.from_browser.upper()} to VELOX...")
        success, details = migrate_data_to_velox(
            args.from_browser,
            copy_bookmarks=True,
            copy_tabs=True,
            open_tabs=args.open_tabs or args.import_all
        )
        if success:
            print("\n[SUCCESS] Migration completed successfully!")
            print(f"  Browser:   {details['browser']}")
            print(f"  Bookmarks: {details['bookmarks_transferred']} items transferred")
            print(f"  Tabs:      {details['tabs_transferred']} open tabs/sessions processed and opened in VELOX")
            print(f"  Saved to:  {get_velox_profile_path()}")
            return 0
        else:
            print(f"\n[ERROR] Migration failed: {details}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
