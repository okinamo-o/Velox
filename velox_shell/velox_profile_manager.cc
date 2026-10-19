// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_shell/velox_profile_manager.h"

#include <cstdlib>
#include <iostream>

namespace velox {

static std::filesystem::path DetermineDefaultUserDataDir() {
  const char* local_app_data = std::getenv("LOCALAPPDATA");
  if (local_app_data) {
    return std::filesystem::path(local_app_data) / "Velox" / "User Data";
  }
  return std::filesystem::current_path() / "velox_data";
}

VeloxProfileManager::VeloxProfileManager()
    : user_data_root_(DetermineDefaultUserDataDir()) {
  // Initialize Default Profile
  CreateProfile("Default", /*is_incognito=*/false);
}

VeloxProfileManager::VeloxProfileManager(const std::filesystem::path& custom_root_path)
    : user_data_root_(custom_root_path) {
  CreateProfile("Default", /*is_incognito=*/false);
}

VeloxProfileManager::~VeloxProfileManager() = default;

bool VeloxProfileManager::CreateProfile(const std::string& name, bool is_incognito) {
  for (const auto& p : profiles_) {
    if (p.name == name) return false;
  }

  VeloxProfile profile;
  profile.name = name;
  profile.is_incognito = is_incognito;
  profile.is_default = (name == "Default");
  profile.profile_path = user_data_root_ / name;

  if (!is_incognito) {
    std::error_code ec;
    std::filesystem::create_directories(profile.profile_path, ec);
  }

  profiles_.push_back(profile);
  return true;
}

const VeloxProfile* VeloxProfileManager::GetProfile(const std::string& name) const {
  for (const auto& p : profiles_) {
    if (p.name == name) return &p;
  }
  return nullptr;
}

std::vector<VeloxProfile> VeloxProfileManager::GetAllProfiles() const {
  return profiles_;
}

}  // namespace velox
