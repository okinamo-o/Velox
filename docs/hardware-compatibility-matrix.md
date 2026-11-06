# VELOX Universal Hardware Compatibility Matrix (`Phase B` & `Phase C`)

**Document Status:** Complete  
**Target Build:** Velox Chromium `134.0.6998.186` (`Windows x64`)  
**Scope:** Runtime hardware capability detection (`Phase B`), hardware vs. software decoder selection across Intel, AMD, and NVIDIA GPUs (`Phase C`), processor SIMD scaling, RAM tiers, and display configurations.

---

## 1. Runtime Capability Detection Architecture (`Phase B`)

Velox detects hardware capabilities dynamically at runtime using Chromium's multi-process hardware introspection APIs without relying on hardcoded GPU/CPU model strings or transmitting hardware fingerprints externally.

### 1.1 Graphics & Video Decoder Detection (`CONFIRMED`)

| Capability Dimension | Runtime Detection Mechanism in Velox | Source Implementation | Privacy & Scope |
|---|---|---|---|
| **GPU Vendor & Device ID** | DXGI adapter enumeration (`IDXGIAdapter::GetDesc1`) populating `gpu::GPUInfo::GPUDevice` (`vendor_id`, `device_id`, `sub_sys_id`, `revision`, `luid`). | `src/gpu/config/gpu_info_collector_win.cc`, `src/content/browser/gpu/gpu_data_manager_impl_private.cc` | Internal to GPU/Browser process & local `velox://media` WebUI. |
| **Graphics APIs & ANGLE Backend** | Queries D3D11 feature level, D3D12 feature level, Vulkan driver version, DirectML feature level, and SharedImage D3D support (`gpu_info.shared_image_d3d`). | `src/gpu/config/gpu_info.h`, `src/ui/gl/init/gl_factory_win.cc` | Internal runtime selection. |
| **Hardware Video Decode Profiles & Max Resolution** | Enumerates DXVA2 / D3D11 decoder GUIDs via `ID3D11VideoDevice::GetVideoDecoderProfile()` and tests resolution tiers (`1080p`, `1440p`, `4K`, `8K`) via `GetVideoDecoderConfigCount()`. | `src/media/gpu/windows/supported_profile_helpers.cc:150–455` | Exposed to `DecoderSelector`, `MediaCapabilities`, and `velox://media`. |
| **DirectComposition & Hardware Overlays (MPO)** | Queries `IDCompositionDevice2` and DXGI output overlay support for `NV12` (8-bit 4:2:0 SDR), `P010` (10-bit 4:2:0 HDR), `YUY2`, `BGRA8`, and `RGB10A2`. | `src/ui/gl/direct_composition_support.cc`, `gpu_info.overlay_info` | Internal to Viz Display Compositor & `velox://media`. |
| **Driver Compatibility & Workarounds** | Evaluates `gpu_driver_bug_list.json` and `software_rendering_list.json` against active `vendor_id`, `device_id`, and `driver_version` to populate `GpuFeatureInfo` and `GpuDriverBugWorkarounds`. | `src/gpu/config/gpu_control_list.cc`, `src/media/gpu/windows/d3d11_video_decoder.cc` | Automatically disables broken driver paths (e.g., `disable_d3d11_video_decoder`, `disable_vp9_hmft`) per driver version. |

### 1.2 Processor & System Resource Detection (`CONFIRMED`)

| Capability Dimension | Runtime Detection Mechanism in Velox | Source Implementation | Adaptive Behavior |
|---|---|---|---|
| **CPU Architecture & SIMD Instruction Sets** | `base::CPU` executes `CPUID` to detect `SSE2`, `SSSE3`, `SSE4.1`, `SSE4.2`, `AVX`, `FMA3`, `AVX2`, `AVX-VNNI`, `AVX-512F/BW/VNNI`. | `src/base/cpu.cc`, `third_party/dav1d`, `third_party/libvpx`, `third_party/ffmpeg` | `dav1d`, `libvpx`, and `ffmpeg` dynamically dispatch `AVX2` / `SSE4.1` assembly kernels at runtime for software decoding. |
| **Logical Processor Count & Web Worker Concurrency** | `base::SysInfo::NumberOfProcessors()` determines thread pool sizing for `OffloadingDav1dVideoDecoder`, `OffloadingVpxVideoDecoder`, and `FFmpegVideoDecoder`. | `src/media/filters/offloading_video_decoder.cc`, `src/third_party/blink/renderer/core/frame/navigator_concurrent_hardware.cc` | `navigator.hardwareConcurrency` adapts across `{2, 4, 8, 12, 16}` tiers so 2/4-core CPUs are never oversubscribed and 12+ core CPUs scale 4K60 worker pools. |
| **Physical RAM & Memory Pressure** | `base::SysInfo::AmountOfPhysicalMemory()`, `AmountOfAvailablePhysicalMemory()`, and `base::MemoryPressureMonitor` (`MODERATE` vs `CRITICAL`). | `src/base/system/sys_info_win.cc`, `src/content/renderer/render_thread_impl.cc` | Protects active/audible video renderers from cache purges during `MODERATE` memory pressure while reclaiming memory from hidden background tabs. |

### 1.3 Display & Color Capability Detection (`CONFIRMED`)

| Capability Dimension | Runtime Detection Mechanism in Velox | Source Implementation | Adaptive Behavior |
|---|---|---|---|
| **Display Resolution, DPI Scaling & Refresh Rate** | `display::Screen::GetScreen()->GetAllDisplays()` queries Windows DXGI/Monitor APIs for physical pixel dimensions (`GetSizeInPixel()`), DIP scale factor (`device_scale_factor()`), and refresh rate (`display_frequency()`). | `src/ui/display/win/screen_win.cc`, `src/ui/display/display.h` | Sizes swap chains at native physical pixels and schedules `VideoFrameCompositor` cadence against actual monitor VSync (`60Hz`, `120Hz`, `144Hz`, `240Hz`). |
| **HDR & Color Space Capabilities** | Queries `IDXGIOutput6::GetDesc1()` for `DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020` (HDR10), SDR white level in nits (`GetSDRMaxLuminanceNits()`), and HDR max luminance relative headroom (`GetHDRMaxLuminanceRelative()`). | `src/ui/gfx/display_color_spaces.h`, `src/ui/display/win/color_profile_reader.cc` | Enables 10-bit `P010` / `RGBA_F16` HDR tone-mapping and presentation only when the target monitor actively supports HDR; otherwise tone-maps cleanly to SDR sRGB/Rec.709. |

---

## 2. Universal Hardware Compatibility Matrix across GPU Generations

> **Honesty & Verification Note:** Code paths for all GPU classes below are **`CONFIRMED`** in Velox's `supported_profile_helpers.cc`, `d3d11_video_decoder.cc`, and `gpu_driver_bug_list.json`. Physical execution on the development workstation is verified on **Intel Core i7-14700F + Windows 11 x64**; other GPU hardware classes are classified as **`HIGH-CONFIDENCE INFERENCE`** (backed by Chromium DXVA/D3D11 driver contracts) and **`NOT TESTED`** (on physical discrete hardware not attached to this single machine).

| Hardware Class | Representative GPUs | H.264 (AVC) | VP8 | VP9 (P0 / P2 HDR) | AV1 (Main 8/10-bit) | HEVC (Main / Main10) | Primary Decode Path & Fallback Strategy | Evidence Status |
|---|---|---|---|---|---|---|---|---|
| **Intel Integrated (Gen 7–8 / Older)** | HD 4000, HD 4400, HD 4600, HD 5500 | **HW** (up to 1080p/4K) | **SW** (`libvpx`) | **SW** (`libvpx`; hybrid DXVA blocklisted on older drivers) | **SW** (`dav1d` SSE4.1/AVX2) | **Unsupported** (or SW-unavailable; falls back to H.264/VP9 via MSE) | `D3D11VideoDecoder` for H.264; automatic `OffloadingVpxVideoDecoder` / `OffloadingDav1dVideoDecoder` for VP9/AV1. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **Intel Integrated (Gen 9–10)** | UHD 620, UHD 630, Iris Plus | **HW** (up to 4K60) | **HW / SW** | **HW** (P0 & P2 10-bit up to 4K60) | **SW** (`dav1d` AVX2) | **HW** (8/10-bit up to 4K60) | `D3D11VideoDecoder` for H.264, VP9, HEVC + `NV12`/`P010` DirectComposition overlays; `dav1d` SW for AV1. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **Intel Integrated & Arc (Gen 11–14 / Xe / Arc)** | Iris Xe, UHD 730/770, Arc A380/A770, Battlemage | **HW** (up to 4K60) | **HW / SW** | **HW** (up to 8K) | **HW** (Main 8/10-bit up to 8K) | **HW** (Main/Main10/Rext up to 8K) | Full `D3D11VideoDecoder` hardware acceleration across H.264, VP9, AV1, and HEVC with MPO overlays. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **AMD Integrated (Vega / RDNA2 / RDNA3 APU)** | Radeon Vega 8, Radeon 680M, 780M, 890M | **HW** (up to 4K60) | **SW** (`libvpx`) | **HW** (up to 4K60) | **HW** on RDNA2+ (600M/700M/800M); **SW** (`dav1d`) on Vega | **HW** (up to 4K60) | `D3D11VideoDecoder` with zero-copy `NV12` textures; respects `amd_switchable` on hybrid laptops. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **AMD Dedicated GPUs (Polaris / Vega / RDNA 1–3)** | RX 580, RX 5700 XT, RX 6600/6800, RX 7800 XT / 7900 XTX | **HW** (up to 4K60) | **SW** (`libvpx`) | **HW** (4K/8K on Vega/RDNA; SW fallback on RX 400/500 if driver lacks VP9 VLD) | **HW** (RX 6000/7000 RDNA2/3 up to 8K); **SW** (`dav1d`) on RX 500/5000 | **HW** (up to 4K/8K) | `D3D11VideoDecoder` for supported DXVA GUIDs; seamless per-codec fallback to `dav1d`/`libvpx` when GUID absent. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **NVIDIA Dedicated GPUs (Maxwell / Pascal / Turing)** | GTX 960/970, GTX 1060/1080, GTX 1650, RTX 2060/2080 | **HW** (NVDEC via D3D11 up to 4K) | **HW / SW** | **HW** (up to 4K/8K on GTX 950/960 & 10/16/20-series) | **SW** (`dav1d` AVX2) | **HW** (up to 4K/8K) | `D3D11VideoDecoder` maps to NVIDIA NVDEC through D3D11 Video API; `dav1d` handles AV1 in software (or YouTube serves VP9 HW via `powerEfficient` reporting). | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **NVIDIA Dedicated GPUs (Ampere / Ada / Blackwell)** | RTX 3060/3080, RTX 4060/4070/4090, RTX 50-series | **HW** (up to 4K) | **HW / SW** | **HW** (up to 8K) | **HW** (Main 8/10-bit up to 8K) | **HW** (Main/Main10/4:4:4 up to 8K) | Full `D3D11VideoDecoder` hardware decode for H.264, VP9, AV1, and HEVC + DirectComposition `NV12`/`P010` overlays. | `CONFIRMED` (Code) / `HIGH-CONFIDENCE INFERENCE` |
| **Software / Basic Render / Broken GPU Driver** | Microsoft Basic Render Driver (`0x1414`), WARP, or blocklisted GPU | **SW** (`FFmpegVideoDecoder`) | **SW** (`OffloadingVpx`) | **SW** (`OffloadingVpx`) | **SW** (`OffloadingDav1d`) | **Unsupported** (Websites negotiate H.264/VP9/AV1 via MSE) | Graceful degradation to multi-threaded SIMD software decoders + SwiftShader/Skia software compositor. | `CONFIRMED` |

---

## 3. Intelligent Decoder Selection Strategy (`Phase C`)

### 3.1 Priority Ordering & Resolution Cutoff (`CONFIRMED`)

Velox uses Chromium's `DecoderSelector<DemuxerStream::VIDEO>` (`src/media/filters/decoder_selector.cc`) with `kResolutionBasedDecoderPriority` enabled (`src/media/base/media_switches.cc:1000`):

1. **Streams with height $\ge 360\text{p}$ (`360p`, `480p`, `720p`, `1080p`, `1440p`, `4K`, `8K`)**:
   - **Priority 1 (`kNormal`)**: `MojoVideoDecoder` $\rightarrow$ `D3D11VideoDecoder` (Hardware decoding on the GPU when the codec profile and resolution are within `gpu_info.video_decode_accelerator_supported_profiles`).
   - **Priority 2 (`kDeprioritized` Fallback)**: `OffloadingVpxVideoDecoder` (VP8/VP9), `OffloadingDav1dVideoDecoder` (AV1), `FFmpegVideoDecoder` (H.264).
2. **Streams with height $< 360\text{p}$ (e.g., `144p` / `240p` hover previews, tiny UI animations)**:
   - **Priority 1 (`kNormal`)**: Software decoders (`OffloadingVpx`, `OffloadingDav1d`, `FFmpegVideoDecoder`) to avoid allocating heavy D3D11 hardware decoder instances and texture arrays for tiny decorative videos while a main 1080p/4K video is playing.
   - **Priority 2 (`kDeprioritized` Fallback)**: `D3D11VideoDecoder` (used automatically if no software decoder exists for the codec, such as `<360p` HEVC).

### 3.2 Graceful Fallback & Failure Handling (`CONFIRMED`)

- **Initialization Failure**: If `D3D11VideoDecoder::Initialize` fails (e.g., unsupported profile/level, `E_OUTOFMEMORY`, DXGI device reset, or driver error), `DecoderSelector::OnDecoderInitializeDone` logs the reason to `MediaLog` and immediately advances to the next candidate decoder in the list (software fallback) without aborting playback (`src/media/filters/decoder_selector.cc:240–295`).
- **Mid-Stream Decode Error**: If `D3D11VideoDecoder::Decode` encounters an unrecoverable hardware error during playback (`DecoderStatus::Codes::kPlatformDecodeFailure`), `DecoderStream::OnDecodeDone` triggers `FallBackToNextDecoder()`, re-initializing the software decoder on the next keyframe to preserve playback continuity without crashing the tab or GPU process.
- **No Infinite Retry Loops**: Once a hardware decoder fails initialization for a stream configuration, `DecoderSelector` removes it from the candidate set for that configuration pass so it is not repeatedly retried.
