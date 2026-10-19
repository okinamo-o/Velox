// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_PERFORMANCE_VELOX_TAB_LIFECYCLE_POLICY_H_
#define VELOX_PERFORMANCE_VELOX_TAB_LIFECYCLE_POLICY_H_

#include <cstdint>
#include <vector>
#include <memory>
#include "velox_shell/velox_tab_strip.h"
#include "velox_performance/velox_memory_pressure_monitor.h"

namespace velox {

class VeloxTabLifecyclePolicy {
 public:
  explicit VeloxTabLifecyclePolicy(VeloxTabStrip* tab_strip);
  ~VeloxTabLifecyclePolicy();

  // Evaluates tabs and transitions lifecycle states according to age & memory pressure
  void EvaluateTabs(uint64_t current_time_ms, MemoryPressureLevel pressure);

  // Identifies the single best tab candidate to discard under severe pressure
  // Returns tab_id or -1 if no discardable tab exists
  int32_t FindBestDiscardCandidate() const;

  // Discards the specified tab, freeing renderer memory
  bool DiscardTab(int32_t tab_id);

  // Configuration timeouts (ms)
  uint64_t GetBackgroundThresholdMs() const { return background_threshold_ms_; }
  uint64_t GetLowResourceThresholdMs() const { return low_resource_threshold_ms_; }
  uint64_t GetDiscardableThresholdMs() const { return discardable_threshold_ms_; }

 private:
  VeloxTabStrip* tab_strip_;
  uint64_t background_threshold_ms_{5 * 60 * 1000};      // 5 minutes
  uint64_t low_resource_threshold_ms_{15 * 60 * 1000};   // 15 minutes
  uint64_t discardable_threshold_ms_{60 * 60 * 1000};     // 1 hour
};

}  // namespace velox

#endif  // VELOX_PERFORMANCE_VELOX_TAB_LIFECYCLE_POLICY_H_
