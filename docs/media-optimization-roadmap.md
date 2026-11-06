# VELOX Long-Term Media Optimization Roadmap

**Document Status:** Complete  
**Target Build:** Velox Chromium `134.0.6998.186` (`Windows x64`)  
**Scope:** Prioritized engineering roadmap for continued media pipeline, hardware acceleration, HDR/color management, and diagnostic enhancements across future Velox releases.

---

## 1. Completed in Current Release (`134.0.6998.186`) — `CONFIRMED`

| Milestone | Engineering Deliverable | Source Files Modified | Status |
|---|---|---|---|
| **M1.1** | **Playback-Safe Adaptive Memory Pressure Handling**: Prevent `MEMORY_PRESSURE_LEVEL_MODERATE` from purging Skia/Blink caches in visible or audible media-playing renderers while keeping aggressive reclamation for hidden background tabs. | `src/content/renderer/render_thread_impl.cc` | `CONFIRMED` |
| **M1.2** | **Adaptive Hardware Concurrency Tiering**: Replace fixed `8` core count with runtime processor bucketing (`{2, 4, 8, 12, 16}`) so 2/4-core CPUs are never oversubscribed by MSE/WASM worker pools and 12+ core CPUs scale 4K60 worker threads. | `src/third_party/blink/renderer/core/frame/navigator_concurrent_hardware.cc` | `CONFIRMED` |
| **M1.3** | **Resolution-Based Decoder Priority (`>= 360p` HW / `< 360p` SW)**: Enable `kResolutionBasedDecoderPriority` on Windows desktop so `D3D11VideoDecoder` is prioritized for all $\ge 360\text{p}$ streams while tiny $<360\text{p}$ thumbnail/preview videos use lightweight software decoding. | `src/media/base/media_switches.cc` | `CONFIRMED` |
| **M1.4** | **Audible / Explicit Auto-Picture-in-Picture Eligibility**: Require `has_audio_focus_ || WasRecentlyAudible() || is_enter_auto_picture_in_picture_available_` in `MeetsVideoPlaybackConditions()` so silent decorative `<video>` background loops do not hijack Auto-PiP on tab switch. | `src/chrome/browser/picture_in_picture/auto_picture_in_picture_tab_helper.cc` | `CONFIRMED` |
| **M1.5** | **Product-Level Media & Hardware Diagnostics (`velox://media`)**: Ship native internal diagnostic WebUI reporting real runtime GPU/driver info, DXVA hardware decode profiles, DirectComposition/MPO overlay support, live `MediaCapabilities` & MSE probes, EME status, interactive 60fps playback inspector, and local JSON export. | `src/chrome/browser/ui/webui/velox/velox_performance_ui.h`, `velox_performance_ui.cc`, `chrome_web_ui_configs.cc` | `CONFIRMED` |

---

## 2. Near-Term Engineering Roadmap (Next 1–2 Releases)

### 2.1 Direct3D 12 Video Decoder (`D3D12VideoDecoder`) Gradual Rollout — `POTENTIAL RISK` / `NOT TESTED`
- **Context**: Chromium 134 includes `D3D12VideoDecoder` (`src/media/gpu/windows/d3d12_video_decoder.cc`) behind `media::kD3D12VideoDecoder` (`FEATURE_DISABLED_BY_DEFAULT`).
- **Recommendation**: Keep `D3D11VideoDecoder` as the universal default for Windows 10/11 compatibility across older Intel/AMD/NVIDIA drivers, and evaluate enabling `kD3D12VideoDecoder` selectively on WDDM 3.1+ drivers once upstream driver stability parity is confirmed.

### 2.2 Video Super Resolution (VSR) & RTX / Intel / AMD Upscaling Integration — `NOT TESTED`
- **Context**: `ID3D11VideoProcessor` supports driver-level Video Super Resolution (`kNvidiaVpSuperResolution`, Intel VSR) when DirectComposition video overlays are active.
- **Recommendation**: Expose an optional user-facing toggle in `velox://settings` and `velox://media` to allow users on plugged-in AC power with supported RTX 30/40/50, Intel Arc, or AMD RDNA GPUs to opt in or out of driver-level Video Super Resolution without forcing it on battery-powered laptops.

### 2.3 Per-Instance `MediaLog` Mojo Bridge into `velox://media` — `HIGH-CONFIDENCE INFERENCE`
- **Context**: Currently, `velox://media` combines browser-process `GpuDataManager` / `Display` / `CPU` hardware introspection with client-side `MediaCapabilities`, `MediaSource`, EME, and `getVideoPlaybackQuality()` probes, while low-level per-tab `MediaLog` events are also accessible in `chrome://media-internals`.
- **Recommendation**: Add a read-only `MediaInternals` observer hook to `VeloxMediaUI` so `velox://media` can optionally list active `<video>` players across open browser tabs alongside its built-in hardware and playback inspector.

---

## 3. Long-Term Architectural Guardrails

1. **Never Re-Introduce Fixed GPU Memory Caps**: Do not add `--force-gpu-mem-available-mb` to launcher flags or patches; always let `GpuChannelManager` and `SharedContextState` scale texture caches to actual device memory.
2. **Preserve Zero-Copy D3D11 SharedImage Paths**: Any future privacy or rendering hooks must avoid forcing CPU readback on `VideoFrame` textures (`PIXEL_FORMAT_NV12` / `PIXEL_FORMAT_P010LE`).
3. **Maintain Multi-Hardware CI Verification**: Expand automated headless and GPU-runner test coverage across Intel iGPU, AMD APU/dGPU, and NVIDIA dGPU runners using the exported `velox-media-diagnostics.json` schema from `velox://media`.
