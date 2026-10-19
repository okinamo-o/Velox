# VELOX Browser: Data & Open Tab Migration Guide

VELOX provides seamless onboarding for users migrating from Google Chrome, Microsoft Edge, Brave Browser, or Mozilla Firefox.

## 1. Native Importer Dialog (`chrome://settings/importData`)
When users open the "Import bookmarks and settings" dialog, VELOX automatically detects:
- The **Current Default Browser** on Windows (e.g. `Google Chrome (Default)` or `Microsoft Edge (Default)`) preselected at the top.
- The complete list of installed modern browsers:
  - **Google Chrome**
  - **Microsoft Edge**
  - **Brave Browser**
  - **Comet**
  - **Mozilla Firefox**
  - **Vivaldi** / **Opera**
- Legacy Internet Explorer is automatically hidden in favor of modern installed browsers.
- Native parser extracts Chromium JSON `Bookmarks` and SQLite `History` directly.

## 2. Onboarding UI: 1-Click Migration
When users launch VELOX for the first time (or open `velox://welcome`), the Onboarding Tour features a prominent **Easy Migration** banner:

- **Button:** `📦 Transfer Data & Tabs →`
- **Destination:** `chrome://settings/importData`
- **Supported Data:**
  - Active open tabs and session state
  - Bookmarks & folder hierarchies
  - Browsing history
  - Saved passwords & credentials
  - Autofill form data & search engines

## 2. Automated Migration Tool (`scripts/import_browser_data.py`)
For advanced users, system administrators, or automated deployments, VELOX provides a standalone migration utility:

### Scanning Installed Browsers
```bash
python scripts/import_browser_data.py --scan
```
Output:
```text
Detected 2 installed browser(s):
  * [CHROME] Google Chrome
    Profile: C:\Users\<User>\AppData\Local\Google\Chrome\User Data\Default
    Available: 15 Bookmarks, ~25 Open Tabs / Sessions
  * [EDGE] Microsoft Edge
    Profile: C:\Users\<User>\AppData\Local\Microsoft\Edge\User Data\Default
    Available: 8 Bookmarks, ~19 Open Tabs / Sessions
```

### Performing 1-Click Migration
To transfer bookmarks and queue active open tabs directly into VELOX:
```bash
python scripts/import_browser_data.py --from-browser chrome --import-all
```

Transferred open tabs are written to `transferred_tabs.json` in VELOX's user profile for immediate session restoration.
