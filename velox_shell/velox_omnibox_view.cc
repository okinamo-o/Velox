// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_shell/velox_omnibox_view.h"

#include <algorithm>
#include <sstream>

namespace velox {

static std::string WStringToString(const std::wstring& wstr) {
  std::string str(wstr.begin(), wstr.end());
  return str;
}

VeloxOmniboxView::VeloxOmniboxView() = default;
VeloxOmniboxView::~VeloxOmniboxView() = default;

void VeloxOmniboxView::OnUserTextChange(const std::wstring& text) {
  current_text_ = text;
  current_suggestions_.clear();

  if (text.empty()) return;

  std::string input = WStringToString(text);

  // 1. Check for internal schemes
  if (input.rfind("velox://", 0) == 0 || input.rfind("chrome://", 0) == 0) {
    OmniboxSuggestion s;
    s.destination_url = input;
    s.display_title = text;
    s.is_internal_scheme = true;
    current_suggestions_.push_back(s);
    return;
  }

  // 2. Direct URL resolution
  if (input.find('.') != std::string::npos && input.find(' ') == std::string::npos) {
    OmniboxSuggestion s;
    s.destination_url = (input.rfind("http://", 0) == 0 || input.rfind("https://", 0) == 0)
                            ? input
                            : "https://" + input;
    s.display_title = text;
    s.is_search_query = false;
    current_suggestions_.push_back(s);
  }

  // 3. Fallback search suggestion (default engine without background ping)
  OmniboxSuggestion search_s;
  search_s.destination_url = "https://duckduckgo.com/?q=" + input;
  search_s.display_title = L"Search for \"" + text + L"\"";
  search_s.is_search_query = true;
  current_suggestions_.push_back(search_s);
}

std::string VeloxOmniboxView::SanitizeAndResolveNavigation(const std::wstring& input) {
  std::string str = WStringToString(input);
  if (str.empty()) return "velox://newtab";

  if (str.rfind("velox://", 0) == 0 ||
      str.rfind("http://", 0) == 0 ||
      str.rfind("https://", 0) == 0 ||
      str.rfind("file:///", 0) == 0) {
    return str;
  }

  if (str.find('.') != std::string::npos && str.find(' ') == std::string::npos) {
    return "https://" + str;
  }

  return "https://duckduckgo.com/?q=" + str;
}

bool VeloxOmniboxView::IsInternalScheme(const std::string& url) {
  return url.rfind("velox://", 0) == 0 || url.rfind("chrome://", 0) == 0;
}

bool VeloxOmniboxView::IsSecureOrigin(const std::string& url) {
  return url.rfind("https://", 0) == 0 ||
         url.rfind("velox://", 0) == 0 ||
         url.rfind("http://localhost", 0) == 0 ||
         url.rfind("http://127.0.0.1", 0) == 0;
}

}  // namespace velox
