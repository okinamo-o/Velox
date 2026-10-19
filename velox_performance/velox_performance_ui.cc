// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_performance/velox_performance_ui.h"

#include <sstream>
#include <iomanip>

namespace velox {

static const char* LifecycleStateToString(TabLifecycleState state) {
  switch (state) {
    case TabLifecycleState::kActive: return "ACTIVE";
    case TabLifecycleState::kBackground: return "BACKGROUND";
    case TabLifecycleState::kLowResource: return "LOW_RESOURCE";
    case TabLifecycleState::kDiscardable: return "DISCARDABLE";
    case TabLifecycleState::kDiscarded: return "DISCARDED";
    default: return "UNKNOWN";
  }
}

VeloxPerformanceUI::VeloxPerformanceUI(
    VeloxTabStrip* tab_strip,
    VeloxMemoryPressureMonitor* memory_monitor)
    : tab_strip_(tab_strip),
      memory_monitor_(memory_monitor) {}

VeloxPerformanceUI::~VeloxPerformanceUI() = default;

std::string VeloxPerformanceUI::GeneratePerformanceReportJson() {
  std::ostringstream ss;
  SystemMemoryStats sys_mem = memory_monitor_
                                  ? memory_monitor_->SampleSystemMemory()
                                  : SystemMemoryStats{};

  ss << "{\n";
  ss << "  \"system_memory\": {\n";
  ss << "    \"total_bytes\": " << sys_mem.total_physical_bytes << ",\n";
  ss << "    \"used_bytes\": " << sys_mem.used_physical_bytes << ",\n";
  ss << "    \"free_bytes\": " << sys_mem.free_physical_bytes << ",\n";
  ss << "    \"load_percent\": " << std::fixed << std::setprecision(1) << sys_mem.memory_load_percent << "\n";
  ss << "  },\n";

  ss << "  \"tabs\": [\n";
  if (tab_strip_) {
    const auto& tabs = tab_strip_->GetAllTabs();
    for (size_t i = 0; i < tabs.size(); ++i) {
      const auto& t = tabs[i];
      ss << "    {\n";
      ss << "      \"id\": " << t.id << ",\n";
      ss << "      \"url\": \"" << t.url << "\",\n";
      ss << "      \"state\": \"" << LifecycleStateToString(t.lifecycle_state) << "\",\n";
      ss << "      \"memory_bytes\": " << t.estimated_memory_bytes << ",\n";
      ss << "      \"protected\": " << (tab_strip_->IsProtectedFromDiscard(t) ? "true" : "false") << "\n";
      ss << "    }" << (i + 1 < tabs.size() ? "," : "") << "\n";
    }
  }
  ss << "  ]\n";
  ss << "}";

  return ss.str();
}

std::string VeloxPerformanceUI::GenerateDashboardHtml() {
  SystemMemoryStats sys_mem = memory_monitor_
                                  ? memory_monitor_->SampleSystemMemory()
                                  : SystemMemoryStats{};

  std::ostringstream ss;
  ss << "<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>velox://performance</title>\n";
  ss << "<style>\n";
  ss << "  body { font-family: -apple-system, 'Segoe UI', sans-serif; background: #0f1117; color: #e1e4ea; margin: 0; padding: 24px; }\n";
  ss << "  .card { background: #1a1d26; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #282c37; }\n";
  ss << "  h1, h2 { color: #58a6ff; margin-top: 0; }\n";
  ss << "  table { width: 100%; border-collapse: collapse; margin-top: 12px; }\n";
  ss << "  th, td { text-align: left; padding: 10px; border-bottom: 1px solid #282c37; font-size: 14px; }\n";
  ss << "  th { color: #8b949e; }\n";
  ss << "  .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }\n";
  ss << "  .badge-active { background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb; }\n";
  ss << "  .badge-discarded { background: #6e768122; color: #8b949e; border: 1px solid #6e7681; }\n";
  ss << "  .badge-low { background: #d2992222; color: #d29922; border: 1px solid #d29922; }\n";
  ss << "</style></head><body>\n";
  ss << "<h1>VELOX Resource Performance Center (velox://performance)</h1>\n";

  // System stats card
  ss << "<div class='card'><h2>Host System Memory</h2>\n";
  ss << "<p>Physical Load: <strong>" << std::fixed << std::setprecision(1) << sys_mem.memory_load_percent << "%</strong> | ";
  ss << "Free Physical: <strong>" << (sys_mem.free_physical_bytes / (1024 * 1024)) << " MB</strong> / ";
  ss << "Total: <strong>" << (sys_mem.total_physical_bytes / (1024 * 1024)) << " MB</strong></p></div>\n";

  // Tab stats card
  ss << "<div class='card'><h2>Tabstrip Lifecycle & Memory Accountability</h2>\n";
  ss << "<table><thead><tr><th>ID</th><th>URL</th><th>Lifecycle State</th><th>Est. Memory</th><th>Protected</th></tr></thead><tbody>\n";

  if (tab_strip_) {
    for (const auto& t : tab_strip_->GetAllTabs()) {
      ss << "<tr><td>" << t.id << "</td>";
      ss << "<td>" << t.url << "</td>";
      std::string badge_cls = (t.lifecycle_state == TabLifecycleState::kActive)
                                  ? "badge-active"
                                  : (t.lifecycle_state == TabLifecycleState::kDiscarded
                                         ? "badge-discarded"
                                         : "badge-low");
      ss << "<td><span class='badge " << badge_cls << "'>" << LifecycleStateToString(t.lifecycle_state) << "</span></td>";
      ss << "<td>" << (t.estimated_memory_bytes / 1024) << " KB</td>";
      ss << "<td>" << (tab_strip_->IsProtectedFromDiscard(t) ? "Yes" : "No") << "</td></tr>\n";
    }
  }

  ss << "</tbody></table></div></body></html>";
  return ss.str();
}

}  // namespace velox
