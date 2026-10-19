// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SECURITY_VELOX_PRIVACY_CONTROLLER_H_
#define VELOX_SECURITY_VELOX_PRIVACY_CONTROLLER_H_

#include <string>

namespace velox {

struct PrivacyPreferences {
  // Security-critical: Must remain enabled by default
  bool safe_browsing_enabled{true};
  bool crlset_updates_enabled{true};
  bool component_updater_enabled{true};

  // Privacy: Disabled by default
  bool metrics_reporting_enabled{false};      // UMA disabled
  bool remote_search_suggestions{false};     // No keystroke leak to search engine
  bool crash_reporting_enabled{false};        // Crashpad opt-in
  bool webrtc_protect_local_ips{true};       // Prevent LAN IP leakage via STUN
};

class VeloxPrivacyController {
 public:
  VeloxPrivacyController();
  ~VeloxPrivacyController();

  const PrivacyPreferences& GetPreferences() const { return prefs_; }

  // Modifiers
  void SetSafeBrowsingEnabled(bool enabled);
  void SetMetricsReportingEnabled(bool enabled);
  void SetRemoteSearchSuggestions(bool enabled);
  void SetCrashReportingEnabled(bool enabled);
  void SetWebRtcProtectLocalIps(bool enabled);

  // Audits current configuration against Directive Section 8 rules
  bool ValidatePrivacyAndSecurityBalance(std::string* out_warning) const;

 private:
  PrivacyPreferences prefs_;
};

}  // namespace velox

#endif  // VELOX_SECURITY_VELOX_PRIVACY_CONTROLLER_H_
