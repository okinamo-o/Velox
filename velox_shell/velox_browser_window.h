// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SHELL_VELOX_BROWSER_WINDOW_H_
#define VELOX_SHELL_VELOX_BROWSER_WINDOW_H_

#include <memory>
#include <string>
#include <vector>

namespace velox {

class VeloxTabStrip;
class VeloxOmniboxView;
class VeloxProfileManager;

// Represents the state of a browser window in the native Views hierarchy.
struct WindowBounds {
  int x{100};
  int y{100};
  int width{1280};
  int height{800};
  bool maximized{false};
};

// Interface for native Views browser window frame.
// Integrates with Chromium's views::Widget and BrowserView hierarchy
// without embedding third-party web chrome or CEF.
class VeloxBrowserWindow {
 public:
  enum class WindowState {
    kNormal,
    kMinimized,
    kMaximized,
    kFullscreen
  };

  VeloxBrowserWindow(const std::string& profile_name,
                     std::shared_ptr<VeloxProfileManager> profile_manager);
  virtual ~VeloxBrowserWindow();

  // Window lifecycle
  void Init(const WindowBounds& initial_bounds);
  void Show();
  void Close();
  void Minimize();
  void Maximize();
  void Restore();

  // Navigation and Layout accessors
  VeloxTabStrip* GetTabStrip() const { return tab_strip_.get(); }
  VeloxOmniboxView* GetOmnibox() const { return omnibox_.get(); }
  WindowState GetState() const { return current_state_; }
  const WindowBounds& GetBounds() const { return bounds_; }
  const std::string& GetProfileName() const { return profile_name_; }

  // Title and Status
  void SetTitle(const std::wstring& title);
  const std::wstring& GetTitle() const { return title_; }

 private:
  std::string profile_name_;
  std::shared_ptr<VeloxProfileManager> profile_manager_;
  std::unique_ptr<VeloxTabStrip> tab_strip_;
  std::unique_ptr<VeloxOmniboxView> omnibox_;
  WindowBounds bounds_;
  WindowState current_state_{WindowState::kNormal};
  std::wstring title_{L"VELOX"};
};

}  // namespace velox

#endif  // VELOX_SHELL_VELOX_BROWSER_WINDOW_H_
