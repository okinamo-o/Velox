// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SECURITY_VELOX_SECURITY_POLICY_H_
#define VELOX_SECURITY_VELOX_SECURITY_POLICY_H_

#include <string>
#include <vector>

namespace velox {

// Verifies that VELOX never runs with compromised security settings
// as strictly mandated by Master Engineering Directive Section 7 & 22.
class VeloxSecurityPolicy {
 public:
  struct SecurityAuditResult {
    bool passed{true};
    std::vector<std::string> violations;
  };

  VeloxSecurityPolicy();
  ~VeloxSecurityPolicy();

  // Audits command-line flags and rejects forbidden flags:
  // e.g. --no-sandbox, --single-process, --disable-web-security,
  // --disable-site-isolation-trials, --ignore-certificate-errors
  static SecurityAuditResult AuditCommandLine(const std::vector<std::string>& command_line_args);

  // Verifies that a target navigation URL is safe to load in a standard renderer
  static bool IsSafeRendererNavigation(const std::string& target_url);

  // Verifies that privileged schemes (velox://, chrome://) are only
  // initiated by authorized browser components, never by web origins
  static bool CanOriginAccessScheme(const std::string& source_origin, const std::string& target_scheme);
};

}  // namespace velox

#endif  // VELOX_SECURITY_VELOX_SECURITY_POLICY_H_
