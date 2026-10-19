// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SHELL_VELOX_OMNIBOX_VIEW_H_
#define VELOX_SHELL_VELOX_OMNIBOX_VIEW_H_

#include <string>
#include <vector>

namespace velox {

struct OmniboxSuggestion {
  std::string destination_url;
  std::wstring display_title;
  bool is_search_query{false};
  bool is_internal_scheme{false};
};

class VeloxOmniboxView {
 public:
  VeloxOmniboxView();
  ~VeloxOmniboxView();

  // User input handling
  void OnUserTextChange(const std::wstring& text);
  std::string SanitizeAndResolveNavigation(const std::wstring& input);

  // Suggestions (Local-first, privacy-preserving)
  const std::vector<OmniboxSuggestion>& GetCurrentSuggestions() const {
    return current_suggestions_;
  }

  // Scheme verification
  static bool IsInternalScheme(const std::string& url);
  static bool IsSecureOrigin(const std::string& url);

 private:
  std::wstring current_text_;
  std::vector<OmniboxSuggestion> current_suggestions_;
  bool remote_search_suggestions_enabled_{false}; // Section 8: Disabled by default
};

}  // namespace velox

#endif  // VELOX_SHELL_VELOX_OMNIBOX_VIEW_H_
