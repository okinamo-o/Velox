// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SHELL_VELOX_TAB_STRIP_H_
#define VELOX_SHELL_VELOX_TAB_STRIP_H_

#include <cstdint>
#include <string>
#include <vector>
#include <memory>

namespace velox {

// Lifecycle states matching Section 13 of the Directive
enum class TabLifecycleState {
  kActive,
  kBackground,
  kLowResource,
  kDiscardable,
  kDiscarded
};

// Represents an individual browser tab managed in native Views
struct VeloxTabItem {
  int32_t id{0};
  std::string url;
  std::wstring title;
  bool is_pinned{false};
  bool is_playing_audio{false};
  bool is_active_webrtc{false};
  bool has_active_download{false};
  TabLifecycleState lifecycle_state{TabLifecycleState::kActive};
  uint64_t last_active_timestamp_ms{0};
  uint64_t estimated_memory_bytes{0};
};

class VeloxTabStrip {
 public:
  VeloxTabStrip();
  ~VeloxTabStrip();

  // Tab Strip operations
  int32_t CreateNewTab(const std::string& url, bool is_pinned = false);
  bool CloseTab(int32_t tab_id);
  bool SelectTab(int32_t tab_id);
  
  // Tab state queries
  size_t GetTabCount() const { return tabs_.size(); }
  int32_t GetActiveTabId() const { return active_tab_id_; }
  VeloxTabItem* GetTab(int32_t tab_id);
  const std::vector<VeloxTabItem>& GetAllTabs() const { return tabs_; }

  // Discard Protection & Verification Check (Section 13)
  // Returns true if tab cannot be discarded under any circumstance
  bool IsProtectedFromDiscard(const VeloxTabItem& tab) const;

  // Lifecycle transitions
  bool TransitionTabLifecycle(int32_t tab_id, TabLifecycleState target_state);

 private:
  int32_t next_tab_id_{1};
  int32_t active_tab_id_{-1};
  std::vector<VeloxTabItem> tabs_;
};

}  // namespace velox

#endif  // VELOX_SHELL_VELOX_TAB_STRIP_H_
