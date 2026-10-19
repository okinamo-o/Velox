// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_SHELL_VELOX_PROFILE_MANAGER_H_
#define VELOX_SHELL_VELOX_PROFILE_MANAGER_H_

#include <filesystem>
#include <string>
#include <vector>

namespace velox {

struct VeloxProfile {
  std::string name;
  std::filesystem::path profile_path;
  bool is_incognito{false};
  bool is_default{false};
};

class VeloxProfileManager {
 public:
  VeloxProfileManager();
  explicit VeloxProfileManager(const std::filesystem::path& custom_root_path);
  ~VeloxProfileManager();

  // Root User Data Directory
  // Defaults to %LOCALAPPDATA%\Velox\User Data (isolated from Chrome/Edge)
  std::filesystem::path GetUserDataDirectory() const { return user_data_root_; }

  // Profile operations
  bool CreateProfile(const std::string& name, bool is_incognito = false);
  const VeloxProfile* GetProfile(const std::string& name) const;
  std::vector<VeloxProfile> GetAllProfiles() const;
  
  // App Identity Verification (Section 9)
  static std::string GetApplicationId() { return "VeloxBrowser.App"; }
  static std::wstring GetWindowsRegistryKey() { return L"Software\\Velox"; }

 private:
  std::filesystem::path user_data_root_;
  std::vector<VeloxProfile> profiles_;
};

}  // namespace velox

#endif  // VELOX_SHELL_VELOX_PROFILE_MANAGER_H_
