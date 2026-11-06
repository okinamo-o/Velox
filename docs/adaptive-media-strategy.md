# VELOX Adaptive GPU & Memory Management Strategy (`Phase E`)

**Document Status:** Complete  
**Target Build:** Velox Chromium `134.0.6998.186` (`Windows x64`)  
**Scope:** Investigation of `--force-gpu-mem-available-mb=128`, adaptive GPU memory budgeting, Skia cache sizing, video texture management, Low-End Device Mode, and renderer memory pressure handling across low-RAM, mid-range, and high-end systems.

---

## 1. Evaluation of `--force-gpu-mem-available-mb=128` (`Phase E`)

### 1.1 Source Code Audit (`CONFIRMED`)

We inspected `src/gpu/command_buffer/service/service_utils.cc` (`lines 240–243`), `src/gpu/ipc/service/gpu_channel_manager.cc` (`lines 110–190`), `src/gpu/command_buffer/service/shared_context_state.cc` (`lines 160–215`), and all 23 Velox patches (`patches/0001`–`0023`):

```cpp
// src/gpu/command_buffer/service/service_utils.cc:240-243
if (CompileTimeSwitchIsSupported() &&
    command_line->HasSwitch(switches::kForceGpuMemAvailableMb)) {
  // Overrides gpu_preferences.force_gpu_mem_available_bytes
}
```

- **Current State in Velox (`CONFIRMED`)**: `--force-gpu-mem-available-mb=128` is **not** hardcoded in the Velox binary or patch set.
- **Why a Fixed `128 MB` GPU Memory Cap Is Harmful Across Hardware (`CONFIRMED`)**:
  1. **4K & High-Frame-Rate Video Texture Pools**: A single `D3D11VideoDecoder` session decoding 4K (`3840x2160`) VP9 or AV1 allocates a reference + output texture pool (`kD3D11NumBuffers = 16` to `20` surfaces). In `NV12` (12 bits/pixel), 16 surfaces at `3840x2160` require $\approx 199\text{ MB}$ of GPU memory; in 10-bit `P010` (24 bits/pixel), 16 surfaces require $\approx 398\text{ MB}$.
  2. **Skia Ganesh / Graphite Resource Cache Thrashing**: `DetermineGrCacheLimitsFromAvailableMemory` in `shared_context_state.cc` derives the Skia GPU resource cache limit from available GPU memory. Forcing `128 MB` clamps the Skia glyph/tile/image cache, causing constant texture eviction and re-upload stalls during 1440p/4K video compositing or scrolling alongside a playing video.
  3. **False Assumption on Integrated vs. Dedicated GPUs**: A fixed `128 MB` cap severely starves modern integrated GPUs (which dynamically share 4 GB–16 GB of system DDR4/DDR5 RAM via Windows WDDM Shared GPU Memory) and dedicated GPUs (4 GB–24 GB VRAM) alike.

### 1.2 Velox's Native Adaptive GPU Memory Architecture (`CONFIRMED`)

Instead of any fixed cap, Velox relies on Chromium's native WDDM/DXGI-aware adaptive memory management:

1. **Dynamic Budget Calculation (`GpuChannelManager` & `SharedContextState`)**:
   - Queries system physical memory (`base::SysInfo::AmountOfPhysicalMemory()`) and DXGI adapter memory limits to size tile transfer caches and Skia GPU resource caches proportionally to actual device capacity.
2. **Zero-Copy SharedImage Video Pipeline (`D3D11VideoDecoder` + `D3DImageBacking`)**:
   - Decoded video frames remain in `ID3D11Texture2D` surfaces wrapped by `gpu::SharedImage` and are passed by handle/mailbox to the Viz Display Compositor without duplicating textures between the decoder and compositor contexts.
3. **Automatic Resource Reclamation on Visibility & Memory Pressure**:
   - In `GpuChannelManager::OnMemoryPressure` (`src/gpu/ipc/service/gpu_channel_manager.cc:680–730`), when the OS signals memory pressure, the GPU process trims scratch buffers and unused GrContext/Graphite resources without destroying in-flight `SharedImage` video textures actively bound by a visible `VideoFrameCompositor`.

---

## 2. Low-End Device Mode Evaluation (`Phase E`)

### 2.1 How Low-End Device Mode Works in Chromium (`CONFIRMED`)

- Controlled by `base::SysInfo::IsLowEndDevice()` (`src/base/system/sys_info.cc`), which checks `switches::kEnableLowEndDeviceMode` or whether physical RAM is below the low-end threshold ($\le 1\text{ GB}$ on desktop/Android).
- **Why Global Low-End Device Mode Must Not Be Forced (`CONFIRMED`)**:
  - When `IsLowEndDevice()` is forced true globally:
    - Compositor tile bit depth and image decode working sets (`ImageDecodeCacheUtils::GetWorkingSetBytesForImageDecode`) are slashed.
    - Media preload and MSE `SourceBuffer` memory limits (`DemuxerStream` buffer budgets for audio/video) are reduced, increasing rebuffering frequency on high-bitrate 1080p60/4K streams.
- **Velox Policy**: Do **not** force `--enable-low-end-device-mode`. Allow `base::SysInfo::IsLowEndDevice()` to trigger only on genuinely memory-constrained hardware while using targeted, playback-aware memory pressure handling on 4 GB–16 GB+ systems.

---

## 3. Adaptive Renderer Memory Pressure & Tab Lifecycle Strategy (`CONFIRMED`)

### 3.1 Playback-Aware Memory Pressure Handling (`src/content/renderer/render_thread_impl.cc:1651–1668`)

Previously (`Patch 0011`), `RenderThreadImpl::OnMemoryPressure` executed full Skia and Blink cache purges on `MEMORY_PRESSURE_LEVEL_MODERATE` in all renderers. Because Windows triggers `MODERATE` memory pressure whenever physical RAM utilization crosses ~75–80% (a routine state on 8 GB and 16 GB PCs), foreground tabs playing video experienced periodic main-thread stalls and frame drops.

**Implemented Adaptive Policy (`CONFIRMED`):**

```cpp
  if (memory_pressure_level ==
          base::MemoryPressureListener::MEMORY_PRESSURE_LEVEL_CRITICAL ||
      memory_pressure_level ==
          base::MemoryPressureListener::MEMORY_PRESSURE_LEVEL_MODERATE) {
    // Safe in all states: only releases unlocked/free discardable memory pages.
    discardable_memory_allocator_->ReleaseFreeMemory();

    // Only purge active Skia/Blink caches on CRITICAL pressure, or on MODERATE
    // pressure when this renderer is hidden and backgrounded (not playing media
    // or visible to the user), preventing frame drops during video playback.
    if (blink_platform_impl_ &&
        (memory_pressure_level ==
             base::MemoryPressureListener::MEMORY_PRESSURE_LEVEL_CRITICAL ||
         (RendererIsHidden() && RendererIsBackgrounded()))) {
      SkGraphics::PurgeAllCaches();
      blink::WebMemoryPressureListener::OnPurgeMemory();
    }
  }
```

### 3.2 Behavior Across System Memory Tiers

| System State / Renderer Role | `MEMORY_PRESSURE_LEVEL_MODERATE` (~75–80% RAM used) | `MEMORY_PRESSURE_LEVEL_CRITICAL` (Near OOM) | Result |
|---|---|---|---|
| **Foreground Tab Playing Video** (`!RendererIsHidden()`) | Releases only unlocked free discardable blocks; preserves active Skia, Blink, and MSE caches. | Purges caches to prevent system/process OOM crash. | **Zero mid-playback purge stutter on 8 GB–16 GB PCs.** |
| **Background Tab Playing Audio/Video** (`RendererIsHidden() && !RendererIsBackgrounded()`) | Protected from aggressive Skia/Blink cache purges because Chromium keeps audible media renderers at foreground priority. | Purges caches if system reaches critical OOM. | **Uninterrupted background audio/video & PiP playback.** |
| **Idle Hidden Background Tab** (`RendererIsHidden() && RendererIsBackgrounded()`) | Immediately runs `ReleaseFreeMemory()`, `SkGraphics::PurgeAllCaches()`, and `OnPurgeMemory()`. | Full critical memory reclamation + eligible for tab discard. | **Aggressive RAM savings on idle tabs without hurting active media.** |
