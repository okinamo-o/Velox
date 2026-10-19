# VELOX — Chromium Upstream Strategy & Tracking

> **Document Version**: 1.0.0  
> **Status**: APPROVED  
> **Pinned Upstream Revision**: `134.0.6998.178` (Chromium 134 Stable Branch)  
> **Commit Hash**: `81fef1e264547cc88c9450117b091ea5798a5adf`  

---

## 1. Upstream Pinning Rationale

VELOX is an engine-level browser fork based directly on upstream Chromium. In accordance with **Section 1 and Section 6** of the Master Engineering Directive:

1. **Stability & Security**: Stable milestone 134 provides full Manifest V3 support, modern WebGPU/WebGL2, CSS nesting, standard WebRTC, and verified memory management primitives (e.g. `PerformanceManager`, `PageLifecycleObserver`, and `MemoryPressureListener`).
2. **Pristine Source Checkout**: Upstream source code resides strictly in an unmodified checkout (`chromium/src`) pinned to tag `134.0.6998.178`.
3. **No Direct Tree Contamination**: Upstream files are NEVER edited directly in place. All changes must be applied cleanly via patch series (`/patches/`) or housed within modular VELOX subdirectories (`/velox_shell/`, `/velox_performance/`, `/velox_security/`, `/velox_extensions/`).

---

## 2. Upstream Tracking Architecture

```
d:\Velox\
├── src/                          <- Pristine Chromium checkout (tracked via .gclient)
│   ├── build/
│   ├── chrome/
│   ├── content/
│   ├── v8/
│   └── third_party/
├── patches/                      <- Ordered series of .patch files
│   ├── 0001-brand-identity.patch
│   ├── 0002-privacy-telemetry-disable.patch
│   ├── 0003-performance-lifecycle-hooks.patch
│   └── 0004-velox-views-entrypoint.patch
├── velox_shell/                  <- Native UI Views & Window Management
├── velox_performance/            <- Memory pressure, lifecycle, velox://performance
├── velox_security/               <- Origin isolation, profile security, download rules
├── velox_extensions/             <- MV3 extension harness and management
├── docs/                         <- Engineering specifications and audit reports
└── scripts/                      <- Checkout, patch application, and build automation
```

---

## 3. Upstream Rebase & Synchronization Policy

1. **Rebase Cadence**: Rebase occurs at every major Chromium stable release (every 4 weeks) or when an emergency security fix (0-day) is released upstream.
2. **Rebase Protocol**:
   - Check out target tag in `src/`.
   - Run `python scripts/apply_patches.py --dry-run` to test patch compatibility.
   - For any conflicting patch:
     - Review upstream diff to determine if the hook point moved or behavior changed.
     - Regenerate patch cleanly against the new baseline.
     - Document changes in `docs/patches.md`.
   - Execute full compilation and test suite (Section 21, Phases 1–8) before tagging VELOX release.
3. **Rollback Safety**: The patch series allows instantaneous rollback to the unmodified baseline at any point:
   ```powershell
   git -C src checkout -f
   git -C src clean -fd
   ```
