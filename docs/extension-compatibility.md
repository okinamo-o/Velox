# VELOX — Manifest V3 Extension Compatibility Matrix

> **Requirement**: Directive Section 11  
> **Target Manifest**: Manifest V3 (MV3) exclusively  
> **Idle-Timeout Rule**: Upstream Chromium MV3 service-worker idle-timeout timing is inherited exactly (no premature worker termination).  

---

## 1. Extension Verification Matrix

Status Key:
- `VERIFIED` — Tested with test artifact (log/screenshot/automated test)
- `PARTIALLY VERIFIED` — Tested under partial flows
- `NOT VERIFIED` — Spec'd but awaiting full browser runtime execution
- `BLOCKED` — Requires unavailable external account/store access

| Extension | Category | Manifest | Core APIs Exercised | Install | Load | Permissions | Runtime / Messaging | Background Worker | Content Scripts | Storage | Network Blocking | UI (Popup/Options) | Result | Verification State |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **uBlock Origin Lite** | Ad Blocker / Content Filter | V3 | `declarativeNetRequest`, `storage.local`, `tabs`, `webNavigation` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Functional rule evaluation and element hiding | **NOT VERIFIED** (Pending Phase 5) |
| **Bitwarden** | Password Manager | V3 | `storage.sync`, `runtime.sendMessage`, `autofillPrivate`, `contextMenus`, `tabs` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | N/A | Pass | Secure vault unlock, credential matching, and autofill | **NOT VERIFIED** (Pending Phase 5) |
| **React Developer Tools** | Developer Tools | V3 | `devtools.panels`, `devtools.inspectedWindow`, `tabs`, `scripting` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | N/A | Pass | DevTools panel registration and React tree inspection | **NOT VERIFIED** (Pending Phase 5) |
| **Dark Reader** | Content Modification | V3 | `scripting`, `storage.sync`, `declarativeContent`, `tabs` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | N/A | Pass | Dynamic CSS generation and style injection | **NOT VERIFIED** (Pending Phase 5) |
| **Tampermonkey MV3** | Script Manager | V3 | `userScripts`, `scripting`, `storage.local`, `webRequest` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | N/A | Pass | User script execution in isolated worlds | **NOT VERIFIED** (Pending Phase 5) |
| **SingleFile** | Archival / Productivity | V3 | `tabs`, `scripting`, `downloads`, `storage` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | N/A | Pass | Page serialization, image embedding, file download | **NOT VERIFIED** (Pending Phase 5) |

---

## 2. API Support Verification Status

| API Namespace | Upstream Support in M134 | VELOX Implementation Strategy | Verification State |
|---|---|---|---|
| `chrome.declarativeNetRequest` | Native Chromium Engine | Unmodified; full rule quota and dynamic rules preserved | NOT VERIFIED |
| `chrome.storage.local / sync` | Native LevelDB backend | Unmodified storage quota and quota serialization | NOT VERIFIED |
| `chrome.runtime` | Native Mojo Extension System | Unmodified port and message dispatcher | NOT VERIFIED |
| `chrome.scripting` | Native Blink execution engine | Content script injection with isolated world integrity | NOT VERIFIED |
| `chrome.tabs` | Native TabManager integration | Controlled tab queries with lifecycle awareness | NOT VERIFIED |
| `chrome.sidePanel` | Native Views SidePanel | Native side panel container integration | NOT VERIFIED |
| `chrome.userScripts` | Native V8 isolate | Enabled with standard permission verification | NOT VERIFIED |

---

## 3. Testing Methodology
1. **Unpacked Extension Harness**: Load fixtures from `tests/extensions/fixtures/` using `--load-extension` CLI flags.
2. **Automated WPT Extension Test Runner**: Execute automated injection, storage write/read, and messaging tests.
3. **Manual Spot Check Verification**: Verify UI popups, options pages, and persistent background worker wakeup under load.
