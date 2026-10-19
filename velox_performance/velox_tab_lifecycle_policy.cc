// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_performance/velox_tab_lifecycle_policy.h"

#include <algorithm>

namespace velox {

VeloxTabLifecyclePolicy::VeloxTabLifecyclePolicy(VeloxTabStrip* tab_strip)
    : tab_strip_(tab_strip) {}

VeloxTabLifecyclePolicy::~VeloxTabLifecyclePolicy() = default;

void VeloxTabLifecyclePolicy::EvaluateTabs(uint64_t current_time_ms, MemoryPressureLevel pressure) {
  if (!tab_strip_) return;

  const auto& tabs = tab_strip_->GetAllTabs();
  int32_t active_tab_id = tab_strip_->GetActiveTabId();

  // Accelerate aging factors under memory pressure
  double age_multiplier = 1.0;
  if (pressure == MemoryPressureLevel::kModerate) {
    age_multiplier = 2.0;
  } else if (pressure == MemoryPressureLevel::kCritical) {
    age_multiplier = 5.0;
  }

  for (const auto& tab : tabs) {
    if (tab.id == active_tab_id) {
      if (tab.lifecycle_state != TabLifecycleState::kActive) {
        tab_strip_->TransitionTabLifecycle(tab.id, TabLifecycleState::kActive);
      }
      continue;
    }

    // Protected tabs remain in background, never low resource / discardable
    if (tab_strip_->IsProtectedFromDiscard(tab)) {
      if (tab.lifecycle_state != TabLifecycleState::kBackground) {
        tab_strip_->TransitionTabLifecycle(tab.id, TabLifecycleState::kBackground);
      }
      continue;
    }

    uint64_t idle_duration_ms = current_time_ms > tab.last_active_timestamp_ms
                                    ? (current_time_ms - tab.last_active_timestamp_ms)
                                    : 0;
    uint64_t effective_duration_ms = static_cast<uint64_t>(idle_duration_ms * age_multiplier);

    if (tab.lifecycle_state == TabLifecycleState::kDiscarded) {
      continue;
    }

    if (effective_duration_ms >= discardable_threshold_ms_ || pressure == MemoryPressureLevel::kCritical) {
      tab_strip_->TransitionTabLifecycle(tab.id, TabLifecycleState::kDiscardable);
    } else if (effective_duration_ms >= low_resource_threshold_ms_ || pressure == MemoryPressureLevel::kModerate) {
      tab_strip_->TransitionTabLifecycle(tab.id, TabLifecycleState::kLowResource);
    } else if (effective_duration_ms >= background_threshold_ms_) {
      tab_strip_->TransitionTabLifecycle(tab.id, TabLifecycleState::kBackground);
    }
  }

  // Under critical pressure, discard the best discardable candidate immediately
  if (pressure == MemoryPressureLevel::kCritical) {
    int32_t victim = FindBestDiscardCandidate();
    if (victim != -1) {
      DiscardTab(victim);
    }
  }
}

int32_t VeloxTabLifecyclePolicy::FindBestDiscardCandidate() const {
  if (!tab_strip_) return -1;

  const auto& tabs = tab_strip_->GetAllTabs();
  int32_t best_id = -1;
  uint64_t oldest_active_time = UINT64_MAX;

  for (const auto& tab : tabs) {
    if (tab.lifecycle_state == TabLifecycleState::kDiscarded) continue;
    if (tab_strip_->IsProtectedFromDiscard(tab)) continue;

    if (tab.lifecycle_state == TabLifecycleState::kDiscardable ||
        tab.lifecycle_state == TabLifecycleState::kLowResource) {
      if (tab.last_active_timestamp_ms < oldest_active_time) {
        oldest_active_time = tab.last_active_timestamp_ms;
        best_id = tab.id;
      }
    }
  }

  return best_id;
}

bool VeloxTabLifecyclePolicy::DiscardTab(int32_t tab_id) {
  if (!tab_strip_) return false;

  auto* tab = tab_strip_->GetTab(tab_id);
  if (!tab || tab_strip_->IsProtectedFromDiscard(*tab)) {
    return false;
  }

  bool success = tab_strip_->TransitionTabLifecycle(tab_id, TabLifecycleState::kDiscarded);
  if (success) {
    // Memory footprint of a discarded tab is strictly tab metadata (~100 KB vs ~50 MB)
    tab->estimated_memory_bytes = 100 * 1024;
  }
  return success;
}

}  // namespace velox
