// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_shell/velox_tab_strip.h"

#include <chrono>
#include <algorithm>

namespace velox {

static uint64_t GetCurrentTimeMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::system_clock::now().time_since_epoch()).count();
}

VeloxTabStrip::VeloxTabStrip() = default;
VeloxTabStrip::~VeloxTabStrip() = default;

int32_t VeloxTabStrip::CreateNewTab(const std::string& url, bool is_pinned) {
  VeloxTabItem tab;
  tab.id = next_tab_id_++;
  tab.url = url.empty() ? "velox://newtab" : url;
  tab.title = L"New Tab";
  tab.is_pinned = is_pinned;
  tab.lifecycle_state = TabLifecycleState::kActive;
  tab.last_active_timestamp_ms = GetCurrentTimeMs();
  tab.estimated_memory_bytes = 45 * 1024 * 1024; // Baseline estimated renderer heap

  tabs_.push_back(tab);
  active_tab_id_ = tab.id;
  return tab.id;
}

bool VeloxTabStrip::CloseTab(int32_t tab_id) {
  auto it = std::find_if(tabs_.begin(), tabs_.end(),
                         [tab_id](const VeloxTabItem& t) { return t.id == tab_id; });
  if (it == tabs_.end()) {
    return false;
  }

  tabs_.erase(it);
  if (active_tab_id_ == tab_id) {
    active_tab_id_ = tabs_.empty() ? -1 : tabs_.back().id;
  }
  return true;
}

bool VeloxTabStrip::SelectTab(int32_t tab_id) {
  auto* tab = GetTab(tab_id);
  if (!tab) return false;

  // If the tab was discarded, this triggers reload / reactivation
  if (tab->lifecycle_state == TabLifecycleState::kDiscarded) {
    tab->lifecycle_state = TabLifecycleState::kActive;
  }

  active_tab_id_ = tab_id;
  tab->last_active_timestamp_ms = GetCurrentTimeMs();
  return true;
}

VeloxTabItem* VeloxTabStrip::GetTab(int32_t tab_id) {
  for (auto& tab : tabs_) {
    if (tab.id == tab_id) return &tab;
  }
  return nullptr;
}

bool VeloxTabStrip::IsProtectedFromDiscard(const VeloxTabItem& tab) const {
  // Master Engineering Directive Section 13:
  // "Never discard or throttle a tab that's playing audio/video, in an active
  // WebRTC call, mid-download, running critical PWA activity, explicitly pinned,
  // or serving an active extension operation."
  if (tab.id == active_tab_id_) return true;
  if (tab.is_pinned) return true;
  if (tab.is_playing_audio) return true;
  if (tab.is_active_webrtc) return true;
  if (tab.has_active_download) return true;

  return false;
}

bool VeloxTabStrip::TransitionTabLifecycle(int32_t tab_id, TabLifecycleState target_state) {
  auto* tab = GetTab(tab_id);
  if (!tab) return false;

  // Enforce discard protection rules
  if (target_state == TabLifecycleState::kDiscarded && IsProtectedFromDiscard(*tab)) {
    return false;
  }

  tab->lifecycle_state = target_state;
  return true;
}

}  // namespace velox
