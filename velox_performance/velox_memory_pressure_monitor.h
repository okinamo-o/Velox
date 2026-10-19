// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_PERFORMANCE_VELOX_MEMORY_PRESSURE_MONITOR_H_
#define VELOX_PERFORMANCE_VELOX_MEMORY_PRESSURE_MONITOR_H_

#include <cstdint>
#include <functional>
#include <vector>

namespace velox {

enum class MemoryPressureLevel {
  kNone,
  kModerate,
  kCritical
};

struct SystemMemoryStats {
  uint64_t total_physical_bytes{0};
  uint64_t free_physical_bytes{0};
  uint64_t used_physical_bytes{0};
  double memory_load_percent{0.0};
};

class VeloxMemoryPressureMonitor {
 public:
  using PressureCallback = std::function<void(MemoryPressureLevel)>;

  VeloxMemoryPressureMonitor();
  ~VeloxMemoryPressureMonitor();

  // Polls current host memory status from Windows kernel
  SystemMemoryStats SampleSystemMemory();

  // Evaluates memory pressure level based on host thresholds
  MemoryPressureLevel DeterminePressureLevel(const SystemMemoryStats& stats);

  // Subscribes observer to memory pressure level transitions
  void RegisterPressureCallback(PressureCallback cb);

  // Manually injects or notifies pressure level (for tests and OS events)
  void OnMemoryPressureChanged(MemoryPressureLevel level);

 private:
  std::vector<PressureCallback> callbacks_;
  MemoryPressureLevel last_level_{MemoryPressureLevel::kNone};
};

}  // namespace velox

#endif  // VELOX_PERFORMANCE_VELOX_MEMORY_PRESSURE_MONITOR_H_
