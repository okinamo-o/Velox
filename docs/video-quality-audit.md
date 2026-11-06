# VELOX Video Quality, Adaptive Streaming & Visual Accuracy Audit (`Phase D` & `Phase F`)

**Document Status:** Complete  
**Target Build:** Velox Chromium `134.0.6998.186` (`Windows x64`)  
**Scope:** Investigation of adaptive streaming quality negotiation on YouTube, Twitch, and MSE platforms (`Phase D`), and visual rendering quality, scaling, color spaces, HDR/SDR handling, and DirectComposition hardware overlays (`Phase F`).

---

## 1. Adaptive Streaming & Resolution Selection Analysis (`Phase D`)

Streaming platforms (YouTube, Twitch, Vimeo, Netflix/DASH, HLS.js, Shaka Player) determine which codecs (`AV1`, `VP9`, `H.264`, `HEVC`), resolutions (`1080p`, `1440p`, `4K`), and frame rates (`30fps` vs `60fps`) to serve based on five browser signals:

1. **`MediaSource.isTypeSupported(mimeCodec)`** — Determines which container and codec profiles can be appended to an MSE `SourceBuffer`.
2. **`navigator.mediaCapabilities.decodingInfo(configuration)`** — Reports `{ supported, smooth, powerEfficient }` for specific `(codec, width, height, framerate, bitrate)` tuples.
3. **`HTMLVideoElement.getVideoPlaybackQuality()`** — Reports `totalVideoFrames` and `droppedVideoFrames`; if dropped frames exceed a threshold (typically >5–10% in a sliding window), adaptive players downgrade resolution or step down from `60fps` to `30fps`.
4. **`navigator.hardwareConcurrency` & `window.devicePixelRatio`** — Used by player worker pools (e.g., Twitch low-latency WASM workers, MSE transmuxers) and viewport-aware ABR algorithms.
5. **MSE `SourceBuffer` Memory Limits** — Controls how much video data can be buffered ahead in `SourceBufferStream`.

### 1.1 MediaCapabilities & Smoothness Prediction Audit (`CONFIRMED`)

Inspection of `src/third_party/blink/renderer/modules/media_capabilities/media_capabilities.cc` (`lines 1–650`) and `src/media/mojo/services/video_decode_perf_history.cc` (`lines 1–240`) confirms:

- **`supported`**: Evaluated against compiled codec parsers (`IsSupportedVideoType`) and platform hardware profiles (`GpuMojoMediaClientWin`).
- **`powerEfficient`**: Returns `true` when the requested `(codec, profile, resolution)` matches an active hardware decoder profile in `gpu_info.video_decode_accelerator_supported_profiles` (e.g., `D3D11VideoDecoder` DXVA support for H.264, VP9, AV1, or HEVC).
  - *Why this matters on older GPUs*: On an NVIDIA GTX 1060/2060 or Intel UHD 630 (which has hardware VP9 decode up to 4K60, but no hardware AV1 decode), `decodingInfo()` reports `powerEfficient: true` for 4K60 VP9 and `powerEfficient: false` for 4K60 AV1. YouTube uses this signal to serve hardware-accelerated **4K60 VP9** instead of forcing software-decoded 4K60 AV1 or dropping resolution!
- **`smooth`**: Queried via `VideoDecodePerfHistory::GetPerfInfo` (`video_decode_perf_history.cc:140–215`), which defaults optimistically to `is_smooth = true` when no prior high-drop-rate history exists for that codec/resolution bucket (`kMaxSmoothDroppedFramesPercent`).

### 1.2 Root Causes of Streaming Quality Drops Found & Fixed in Velox (`CONFIRMED`)

| Issue | Mechanism Causing Lower Quality / Frame Drops | Fix Implemented in Velox | Evidence Status |
|---|---|---|---|
| **Moderate Memory Pressure Cache Purges During Playback (`V-01`)** | In `RenderThreadImpl::OnMemoryPressure` (`render_thread_impl.cc:1651`), `SkGraphics::PurgeAllCaches()` and `WebMemoryPressureListener::OnPurgeMemory()` were triggered on `MEMORY_PRESSURE_LEVEL_MODERATE` even in foreground tabs actively playing video. When those synchronous purges caused a burst of dropped frames (`droppedVideoFrames`), YouTube/Twitch ABR logic interpreted the frame drops as decoder overload and downgraded from `1080p60`/`4K60` or recorded non-smooth history in `VideoDecodePerfHistory`. | Restricted `SkGraphics::PurgeAllCaches()` and `OnPurgeMemory()` on `MODERATE` pressure to hidden & backgrounded renderers (`RendererIsHidden() && RendererIsBackgrounded()`). Active video renderers no longer suffer mid-playback cache purge stalls. | `CONFIRMED` |
| **Hardcoded `navigator.hardwareConcurrency = 8` (`V-02`)** | In `navigator_concurrent_hardware.cc:15`, returning `8` on 2-core / 4-thread CPUs caused Twitch/HLS/WASM media players to spawn 8 worker threads, starving the media and compositor threads and triggering ABR quality downgrades. On 12–28 thread CPUs, capping at `8` limited high-bitrate 4K60 worker concurrency. | Updated `NavigatorConcurrentHardware::hardwareConcurrency()` to bucket actual runtime CPU count into `{2, 4, 8, 12, 16}`, preventing thread oversubscription on low-end CPUs and enabling 12/16-thread scaling on high-end CPUs. | `CONFIRMED` |
| **Unfiltered Hardware Decoder Allocation on Sub-360p Videos (`V-03`)** | With `kResolutionBasedDecoderPriority` disabled on desktop, hovering over video thumbnails or loading pages with multiple tiny `<360p` preview videos allocated D3D11 hardware decoder instances alongside the main video player. | Enabled `kResolutionBasedDecoderPriority` in `media_switches.cc:1000`, keeping `D3D11VideoDecoder` prioritized for all $\ge 360\text{p}$ streams while routing $<360\text{p}$ previews to lightweight software decoders. | `CONFIRMED` |

### 1.3 User-Agent, Client Hints & Identity Integrity (`CONFIRMED`)

- Velox does **not** spoof third-party browser brand tokens or use superficial User-Agent hacks to trick streaming sites.
- Standard `Sec-CH-UA` Chromium brand version headers and standard MSE/EME/MediaCapabilities APIs are preserved so streaming platforms negotiate codecs based on real runtime decoder capabilities.

---

## 2. Visual Quality, Scaling, Color Accuracy & Presentation Audit (`Phase F`)

### 2.1 Video Frame Pixel Formats & Chroma Subsampling (`CONFIRMED`)

- **8-bit SDR Video (`H.264`, `VP8`, `VP9 Profile 0`, `AV1 Main 8-bit`, `HEVC Main`)**:
  - Hardware decoded into `NV12` (`PIXEL_FORMAT_NV12`, 4:2:0 semi-planar) D3D11 textures (`D3D11VideoDecoder`).
  - Software decoded into `I420` (`PIXEL_FORMAT_I420`) or `NV12` video frames and uploaded to GPU `SharedImage` textures.
- **10-bit HDR / High Bit-Depth Video (`VP9 Profile 2`, `AV1 Main 10-bit`, `HEVC Main10`)**:
  - Hardware decoded into `P010` (`PIXEL_FORMAT_P010LE`, 10-bit 4:2:0) D3D11 textures without truncating to 8-bit prior to tone-mapping or overlay presentation.
- **High Chroma Subsampling (`4:2:2` / `4:4:4`)**:
  - Handled via `OffloadingVpxVideoDecoder`, `OffloadingDav1dVideoDecoder`, `FFmpegVideoDecoder`, or HEVC Rext via Skia `YUVVideoDrawQuad` / `TextureDrawQuad` shaders, preserving full chroma fidelity.

### 2.2 Color Space Conversion & HDR / SDR Tone Mapping (`CONFIRMED`)

Inspection of `RenderThreadImpl::SetRenderingColorSpace` (`src/content/renderer/render_thread_impl.cc:1827`), `gfx::DisplayColorSpaces` (`src/ui/gfx/display_color_spaces.h`), and Viz compositor color management confirms:

1. **Color Metadata Propagation**:
   - Container (`colr` box in MP4/WebM) and bitstream VUI color metadata (`BT.709`, `BT.601`, `SMPTE 170M`, `BT.2020`, transfer functions `sRGB`, `BT.709`, `PQ / SMPTE ST 2084`, `HLG`, and matrix coefficients, plus `Full` vs `Limited` `[16–235]` range) are attached to every `media::VideoFrame::ColorSpace()`.
2. **SDR Displays (`SupportsHDR() == false`)**:
   - SDR `BT.709` / `BT.601` Limited-range `NV12` frames are converted using exact studio-range `[16–235]` $\rightarrow$ full-range `[0–255]` matrices in either the DirectComposition Video Processor (`ID3D11VideoProcessor`) or Viz's Skia color-space shader—preventing washed-out blacks or crushed shadows.
   - When an HDR (`BT.2020 PQ` / `HLG`) video is played on an SDR monitor, Viz applies tone-mapping to the display's target SDR color space (`GetSDRMaxLuminanceNits()`) rather than clipping highlights or rendering desaturated grey colors.
3. **HDR Displays (`SupportsHDR() == true`)**:
   - When Windows HD Color is enabled on an HDR monitor, `DisplayColorSpaces::SupportsHDR()` returns `true` and reports `GetHDRMaxLuminanceRelative() > 1.0`.
   - `P010` 10-bit video frames are presented via hardware `P010` / `RGB10A2` MPO overlays or composited in `RGBA_F16` scRGB linear space without degrading SDR page elements.

### 2.3 Video Scaling, Device Pixel Ratio (DPR) & Fullscreen Presentation (`CONFIRMED`)

- **High-DPI & Fractional Scaling (`1.0x`, `1.25x`, `1.5x`, `2.0x`)**:
  - `VideoFrameSubmitter` submits `VideoFrame` resources at their native decoded pixel dimensions (`coded_size` / `visible_rect`, e.g., `1920x1080`, `2560x1440`, `3840x2160`) directly to the Viz Display Compositor (`SurfaceLayerBridge`), independent of CSS DIP scaling.
  - On a 4K monitor with `150%` (`1.5x`) Windows scaling, a 4K (`3840x2160`) video is **not** downscaled to `2560x1440` CSS pixels and re-upscaled; Viz maps the `3840x2160` `VideoFrame` texture 1:1 to physical display pixels.
- **DirectComposition Hardware Overlays (MPO) & Fullscreen**:
  - On Windows (`gpu_info.overlay_info.direct_composition == true`), `SwapChainPresenter` (`src/ui/gl/swap_chain_presenter.cc`) promotes eligible `<video>` quads (especially in fullscreen and single-video layouts) into dedicated DirectComposition swap chains (`NV12` or `P010`), utilizing the GPU's hardware display scaler and bypassing intermediate compositor texture copies.
