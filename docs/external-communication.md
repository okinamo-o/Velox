# VELOX — External Communication & Privacy Classification

> **Requirement**: Directive Section 8  
> **Rule**: Never silently strip a security-critical service in the name of privacy. Document all network surfaces and let settings be explicit, transparent, and user-configurable.

---

## 1. Network Communication Classification Matrix

| Subsystem / Service | Classification | Data Transmitted | Trigger / Frequency | Can it be disabled? | Impact / Loss if Disabled | Default in VELOX |
|---|---|---|---|---|---|---|
| **Safe Browsing (v4/v5)** | **Security-critical** | Hashed URL prefixes, binary download metadata on suspect downloads | On page navigation to unknown/flagged URLs; on dangerous file download | Yes (user toggle in `velox://settings/privacy`) | Real-time phishing protection, malware blocking, and malicious download warnings | **Enabled** (Preserved) |
| **CRLSet / Certificate Revocation Updates** | **Security-critical** | Version query to Google Component Updater for revoked TLS cert lists | Periodic background check (daily / on browser start) | No (Hardcoded security rule) | Browser may trust revoked, compromised, or rogue TLS certificates | **Enabled** (Preserved) |
| **Component Updater (CRX)** | **Security-critical** | Client OS, current component version IDs | Periodic check for out-of-band updates (Widevine, Trust Tokens, ad-blocking rules) | Configurable | Delay in zero-day fixes for isolated browser components | **Enabled** (Preserved) |
| **DoH (DNS-over-HTTPS)** | **Security-critical** | Encrypted DNS queries for hostnames | On domain resolution | Yes | Falls back to system plaintext DNS; exposes visited hostnames to local ISP | **Configurable** (System Default) |
| **Crash Reporting (Crashpad)** | **Optional** | Minidump files (registers, stack memory, loaded module list) | Upon browser process crash | Yes (Disabled via switch/policy) | Developer diagnostics and automated bug regression analysis | **Disabled by default** (Opt-in) |
| **UMA Metrics & Telemetry** | **Disabled by default** | Usage metrics, feature usage counters, hardware profile | Hourly telemetry flush | Yes | Upstream Google telemetry / diagnostics | **Disabled by default** |
| **Google Account / Sync** | **Optional** | Saved passwords, bookmarks, open tabs, history | Continuous when logged into a Google profile | Yes | Cloud profile synchronization | **Disabled / Decoupled** |
| **Promotional & Suggestion Services** | **Disabled by default** | Keystrokes in address bar (Omnibox search suggestions), promo pings | On typing in address bar; on New Tab page load | Yes | Live search query suggestions in omnibox dropdown | **Disabled by default** (Local suggestions only) |
| **Captive Portal Detection** | **Functionality-critical** | HTTP probe (`generate_204`) | On network change / Wi-Fi association | Yes | Automatic login splash screen for public Wi-Fi networks | **Enabled** (Configurable) |
| **WebRTC IP Leak Protection** | **Functionality-critical** | Local/private LAN IP addresses via STUN/TURN | During WebRTC peer connection establishment | Configurable | Exposes internal private LAN IPs to peer sites; disabling can break P2P calls on complex NATs | **Restricted to Default Route** |

---

## 2. Policy Enforcement & Auditing

1. **No Silent Security Stripping**: Safe Browsing and CRLSet updates are critical origin protections. They are kept active by default.
2. **Explicit User Controls**: VELOX introduces clear privacy toggles under `velox://settings/privacy`:
   - *Network Security Protection Level* (Standard Safe Browsing / Disabled)
   - *Search Suggestion Network Queries* (Disabled / Local Cache Only / Enabled)
   - *Crashpad Telemetry Sharing* (Disabled by default)
3. **Mojo & Network Service Boundary**: All external HTTP requests initiated by the browser core pass through the hardened Network Service process with strict CORS, CSP, and origin validation intact.
