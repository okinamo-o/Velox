// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_PERFORMANCE_VELOX_PERFORMANCE_UI_H_
#define VELOX_PERFORMANCE_VELOX_PERFORMANCE_UI_H_

#include <string>
#include <vector>
#include <memory>
#include "velox_shell/velox_tab_strip.h"
#include "velox_performance/velox_memory_pressure_monitor.h"

namespace velox {

struct ProcessResourceMetric {
  int32_t process_id{0};
  std::string process_type; // Browser, GPU, Renderer, Utility, Network
  uint64_t working_set_bytes{0};
  double cpu_percent{0.0};
  std::string details;
};

struct TabPerformanceMetric {
  int32_t tab_id{0};
  std::string url;
  std::string lifecycle_state_str;
  uint64_t memory_estimate_bytes{0};
  bool is_protected{false};
};

class VeloxPerformanceUI {
 public:
  VeloxPerformanceUI(VeloxTabStrip* tab_strip,
                     VeloxMemoryPressureMonitor* memory_monitor);
  ~VeloxPerformanceUI();

  // Generates JSON snapshot for the privileged velox://performance WebUI
  std::string GeneratePerformanceReportJson();

  // Generates rendered HTML dashboard for standalone WebUI display
  std::string GenerateDashboardHtml();

 private:
  VeloxTabStrip* tab_strip_;
  VeloxMemoryPressureMonitor* memory_monitor_;
};

}  // namespace velox

#endif  // VELOX_PERFORMANCE_VELOX_PERFORMANCE_UI_H_
