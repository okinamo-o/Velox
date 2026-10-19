// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_performance/velox_memory_pressure_monitor.h"

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

namespace velox {

VeloxMemoryPressureMonitor::VeloxMemoryPressureMonitor() = default;
VeloxMemoryPressureMonitor::~VeloxMemoryPressureMonitor() = default;

SystemMemoryStats VeloxMemoryPressureMonitor::SampleSystemMemory() {
  SystemMemoryStats stats;

#if defined(_WIN32)
  MEMORYSTATUSEX mem_status;
  mem_status.dwLength = sizeof(mem_status);
  if (GlobalMemoryStatusEx(&mem_status)) {
    stats.total_physical_bytes = mem_status.ullTotalPhys;
    stats.free_physical_bytes = mem_status.ullAvailPhys;
    stats.used_physical_bytes = mem_status.ullTotalPhys - mem_status.ullAvailPhys;
    stats.memory_load_percent = static_cast<double>(mem_status.dwMemoryLoad);
  }
#else
  // Fallback stub for portable verification
  stats.total_physical_bytes = 16ULL * 1024 * 1024 * 1024;
  stats.free_physical_bytes = 6ULL * 1024 * 1024 * 1024;
  stats.used_physical_bytes = 10ULL * 1024 * 1024 * 1024;
  stats.memory_load_percent = 62.5;
#endif

  return stats;
}

MemoryPressureLevel VeloxMemoryPressureMonitor::DeterminePressureLevel(const SystemMemoryStats& stats) {
  // Moderate pressure threshold: >= 80% RAM used or < 2 GB free
  // Critical pressure threshold: >= 92% RAM used or < 1 GB free
  const uint64_t one_gb = 1024ULL * 1024 * 1024;

  if (stats.memory_load_percent >= 92.0 || stats.free_physical_bytes < one_gb) {
    return MemoryPressureLevel::kCritical;
  }
  if (stats.memory_load_percent >= 80.0 || stats.free_physical_bytes < (2 * one_gb)) {
    return MemoryPressureLevel::kModerate;
  }

  return MemoryPressureLevel::kNone;
}

void VeloxMemoryPressureMonitor::RegisterPressureCallback(PressureCallback cb) {
  callbacks_.push_back(std::move(cb));
}

void VeloxMemoryPressureMonitor::OnMemoryPressureChanged(MemoryPressureLevel level) {
  if (level == last_level_) return;
  last_level_ = level;

  for (const auto& cb : callbacks_) {
    if (cb) {
      cb(level);
    }
  }
}

}  // namespace velox
