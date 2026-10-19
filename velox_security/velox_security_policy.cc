// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_security/velox_security_policy.h"

#include <algorithm>
#include <cctype>

namespace velox {

VeloxSecurityPolicy::VeloxSecurityPolicy() = default;
VeloxSecurityPolicy::~VeloxSecurityPolicy() = default;

VeloxSecurityPolicy::SecurityAuditResult VeloxSecurityPolicy::AuditCommandLine(
    const std::vector<std::string>& command_line_args) {
  SecurityAuditResult result;

  // Forbidden flags per Directive Section 7 & 22
  const std::vector<std::string> forbidden_switches = {
      "--no-sandbox",
      "--single-process",
      "--disable-web-security",
      "--disable-site-isolation-trials",
      "--ignore-certificate-errors",
      "--allow-running-insecure-content",
      "--disable-gpu-sandbox",
      "--disable-blink-features=SameSiteByDefaultCookies"
  };

  for (const auto& arg : command_line_args) {
    for (const auto& forbidden : forbidden_switches) {
      if (arg == forbidden || arg.rfind(forbidden + "=", 0) == 0) {
        result.passed = false;
        result.violations.push_back("Forbidden flag detected per Directive Section 7/22: " + arg);
      }
    }
  }

  return result;
}

bool VeloxSecurityPolicy::IsSafeRendererNavigation(const std::string& target_url) {
  std::string lower_url = target_url;
  std::transform(lower_url.begin(), lower_url.end(), lower_url.begin(),
                 [](unsigned char c) { return std::tolower(c); });

  // Reject javascript: URLs in high-level omnibox submissions (case-insensitive)
  if (lower_url.rfind("javascript:", 0) == 0) {
    return false;
  }

  // Reject data: text/html top-level document navigations with script
  if (lower_url.rfind("data:text/html", 0) == 0) {
    return false;
  }

  return true;
}

bool VeloxSecurityPolicy::CanOriginAccessScheme(
    const std::string& source_origin,
    const std::string& target_scheme) {
  std::string lower_origin = source_origin;
  std::transform(lower_origin.begin(), lower_origin.end(), lower_origin.begin(),
                 [](unsigned char c) { return std::tolower(c); });

  std::string lower_target = target_scheme;
  std::transform(lower_target.begin(), lower_target.end(), lower_target.begin(),
                 [](unsigned char c) { return std::tolower(c); });

  // Only internal browser schemes can access velox:// or chrome://
  if (lower_target == "velox" || lower_target == "chrome") {
    if (lower_origin.rfind("velox://", 0) == 0 || lower_origin.rfind("chrome://", 0) == 0) {
      return true;
    }
    return false; // Web origins cannot navigate or embed internal schemes
  }

  return true;
}

}  // namespace velox
