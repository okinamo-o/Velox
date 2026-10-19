// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef VELOX_EXTENSIONS_VELOX_EXTENSION_MANAGER_H_
#define VELOX_EXTENSIONS_VELOX_EXTENSION_MANAGER_H_

#include <string>
#include <vector>
#include <memory>
#include <filesystem>

namespace velox {

enum class ManifestVersion {
  kUnknown,
  kManifestV2,
  kManifestV3
};

struct VeloxExtensionInfo {
  std::string id;
  std::string name;
  std::string version;
  ManifestVersion manifest_version{ManifestVersion::kManifestV3};
  std::vector<std::string> permissions;
  std::vector<std::string> host_permissions;
  bool is_enabled{true};
  bool has_background_worker{false};
  bool has_side_panel{false};
  std::filesystem::path install_path;
};

class VeloxExtensionManager {
 public:
  VeloxExtensionManager();
  ~VeloxExtensionManager();

  // Loads an unpacked MV3 extension from local directory
  bool LoadUnpackedExtension(const std::filesystem::path& extension_path, std::string* out_extension_id);

  // Unloads or disables an extension
  bool DisableExtension(const std::string& extension_id);
  bool EnableExtension(const std::string& extension_id);
  bool RemoveExtension(const std::string& extension_id);

  // Queries
  const VeloxExtensionInfo* GetExtension(const std::string& extension_id) const;
  std::vector<VeloxExtensionInfo> GetInstalledExtensions() const;

  // Manifest V3 validation (Directive Section 11: MV2 is rejected)
  static bool ValidateManifestV3(const std::string& manifest_json, std::string* out_error);

 private:
  std::vector<VeloxExtensionInfo> extensions_;
};

}  // namespace velox

#endif  // VELOX_EXTENSIONS_VELOX_EXTENSION_MANAGER_H_
