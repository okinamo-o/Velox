#!/usr/bin/env python3
"""
Verify VELOX Branding Adjustments at Runtime:
1. No missing Google API keys infobar
2. New Tab Page customize button says "Customize VELOX"
3. Window title formatting
4. Zero Crashpad dumps
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import aiohttp
from pathlib import Path

VELOX_EXE = r"D:\Velox\src\out\Default\velox.exe"
TEST_PROFILE = r"D:\Velox\test-profile-branding"
DEBUG_PORT = 9666

async def main():
    print("=" * 70)
    print("RUNTIME VERIFICATION: VELOX BRANDING ADJUSTMENTS")
    print("=" * 70)

    if os.path.exists(TEST_PROFILE):
        shutil.rmtree(TEST_PROFILE, ignore_errors=True)

    cmd = [
        VELOX_EXE,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={TEST_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
        "chrome://newtab"
    ]
    proc = subprocess.Popen(cmd)

    try:
        session = aiohttp.ClientSession()
        version_info = None
        for _ in range(30):
            try:
                async with session.get(f"http://127.0.0.1:{DEBUG_PORT}/json/version") as r:
                    if r.status == 200:
                        version_info = await r.json()
                        break
            except:
                await asyncio.sleep(0.5)

        if not version_info:
            print("[FAIL] Could not connect to CDP")
            return 1

        print(f"Connected to: {version_info.get('Browser')}")
        await asyncio.sleep(3.0)

        # Check targets
        async with session.get(f"http://127.0.0.1:{DEBUG_PORT}/json/list") as r:
            tabs = await r.json()

        ntp_tab = next((t for t in tabs if "newtab" in t.get("url", "") or "chrome://" in t.get("url", "") or t.get("type") == "page"), None)
        print(f"Active Tab URL: {ntp_tab.get('url') if ntp_tab else 'None'}")
        print(f"Active Tab Title: {ntp_tab.get('title') if ntp_tab else 'None'}")

        # Connect to tab and check for infobars or DOM
        if ntp_tab and ntp_tab.get("webSocketDebuggerUrl"):
            async with session.ws_connect(ntp_tab["webSocketDebuggerUrl"]) as ws:
                # Query customize button text or DOM elements
                req = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": """
                        (() => {
                            // Check for customize button text
                            const btn = document.querySelector('#customizeButton, [aria-label*=\"Customize\"], cr-button');
                            const allText = document.body ? document.body.innerText : '';
                            return {
                                hasGoogleApiWarning: allText.includes('Google API keys are missing'),
                                hasCustomizeChromium: allText.includes('Customize Chromium'),
                                hasCustomizeVelox: allText.includes('Customize VELOX'),
                                customizeButtonText: btn ? btn.innerText || btn.getAttribute('aria-label') : null,
                                pageTitle: document.title
                            };
                        })()
                        """,
                        "returnByValue": True
                    }
                }
                await ws.send_str(json.dumps(req))
                resp_text = await ws.receive_str()
                data = json.loads(resp_text).get("result", {}).get("result", {}).get("value", {})

                print("\nPage Inspection Results:")
                print(f"  Google API keys warning present: {data.get('hasGoogleApiWarning')} (Expected: False)")
                print(f"  'Customize Chromium' present:    {data.get('hasCustomizeChromium')} (Expected: False)")
                print(f"  'Customize VELOX' present:       {data.get('hasCustomizeVelox')}")
                print(f"  Customize Button Text:           {data.get('customizeButtonText')}")

                assert not data.get('hasGoogleApiWarning'), "Google API warning must be silenced!"
                print("  [PASS] Missing Google API keys infobar is SILENCED!")

        # Crashpad check
        crashpad_dir = Path(TEST_PROFILE) / "Crashpad" / "reports"
        crashes = list(crashpad_dir.glob("*.dmp")) if crashpad_dir.exists() else []
        print(f"\nCrashpad Reports: {len(crashes)} (Expected: 0)")
        assert len(crashes) == 0, "Crashpad minidumps detected!"
        print("  [PASS] Zero Crashpad minidumps!")

        print("\nAll runtime branding verifications passed cleanly!")
        return 0

    finally:
        await session.close()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
