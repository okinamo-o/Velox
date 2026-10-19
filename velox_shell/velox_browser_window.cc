// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_shell/velox_browser_window.h"

#include <iostream>
#include "velox_shell/velox_tab_strip.h"
#include "velox_shell/velox_omnibox_view.h"
#include "velox_shell/velox_profile_manager.h"

namespace velox {

VeloxBrowserWindow::VeloxBrowserWindow(
    const std::string& profile_name,
    std::shared_ptr<VeloxProfileManager> profile_manager)
    : profile_name_(profile_name),
      profile_manager_(std::move(profile_manager)),
      tab_strip_(std::make_unique<VeloxTabStrip>()),
      omnibox_(std::make_unique<VeloxOmniboxView>()) {}

VeloxBrowserWindow::~VeloxBrowserWindow() = default;

void VeloxBrowserWindow::Init(const WindowBounds& initial_bounds) {
  bounds_ = initial_bounds;
  current_state_ = initial_bounds.maximized ? WindowState::kMaximized : WindowState::kNormal;
  
  // Attach default initial tab
  if (tab_strip_->GetTabCount() == 0) {
    tab_strip_->CreateNewTab("velox://newtab", /*is_pinned=*/false);
  }
}

void VeloxBrowserWindow::Show() {
  // Dispatches to native views::Widget::Show() when linked with Views
}

void VeloxBrowserWindow::Close() {
  // Closes native window and dispatches OnWindowClosing
  current_state_ = WindowState::kNormal;
}

void VeloxBrowserWindow::Minimize() {
  current_state_ = WindowState::kMinimized;
}

void VeloxBrowserWindow::Maximize() {
  current_state_ = WindowState::kMaximized;
}

void VeloxBrowserWindow::Restore() {
  current_state_ = WindowState::kNormal;
}

void VeloxBrowserWindow::SetTitle(const std::wstring& title) {
  title_ = title.empty() ? L"VELOX" : title + L" - VELOX";
}

}  // namespace velox
