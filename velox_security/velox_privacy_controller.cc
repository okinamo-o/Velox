// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_security/velox_privacy_controller.h"

namespace velox {

VeloxPrivacyController::VeloxPrivacyController() = default;
VeloxPrivacyController::~VeloxPrivacyController() = default;

void VeloxPrivacyController::SetSafeBrowsingEnabled(bool enabled) {
  prefs_.safe_browsing_enabled = enabled;
}

void VeloxPrivacyController::SetMetricsReportingEnabled(bool enabled) {
  prefs_.metrics_reporting_enabled = enabled;
}

void VeloxPrivacyController::SetRemoteSearchSuggestions(bool enabled) {
  prefs_.remote_search_suggestions = enabled;
}

void VeloxPrivacyController::SetCrashReportingEnabled(bool enabled) {
  prefs_.crash_reporting_enabled = enabled;
}

void VeloxPrivacyController::SetWebRtcProtectLocalIps(bool enabled) {
  prefs_.webrtc_protect_local_ips = enabled;
}

bool VeloxPrivacyController::ValidatePrivacyAndSecurityBalance(std::string* out_warning) const {
  // Master Engineering Directive Section 8:
  // "Never silently strip a security-critical service in the name of privacy —
  // document the tradeoff and let the setting be explicit and visible."
  if (!prefs_.safe_browsing_enabled) {
    if (out_warning) {
      *out_warning = "Safe Browsing is disabled. Real-time phishing and malware protections are inactive.";
    }
    return false;
  }

  if (!prefs_.crlset_updates_enabled) {
    if (out_warning) {
      *out_warning = "CRLSet updates are disabled. Revoked certificate verification may fail.";
    }
    return false;
  }

  return true;
}

}  // namespace velox
