// Copyright 2026 The VELOX Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "velox_extensions/velox_extension_manager.h"

#include <fstream>
#include <sstream>
#include <algorithm>
#include <regex>

namespace velox {

VeloxExtensionManager::VeloxExtensionManager() = default;
VeloxExtensionManager::~VeloxExtensionManager() = default;

bool VeloxExtensionManager::ValidateManifestV3(const std::string& manifest_json, std::string* out_error) {
  // Enforce Manifest V3 requirement per Directive Section 11:
  // Robust regex matching allowing arbitrary whitespace: "manifest_version"\s*:\s*3\b
  static const std::regex mv3_regex(R"pattern("manifest_version"\s*:\s*3\b)pattern");
  if (!std::regex_search(manifest_json, mv3_regex)) {
    if (out_error) {
      *out_error = "Extension rejected: Only Manifest V3 extensions are supported in VELOX.";
    }
    return false;
  }

  // Disallow deprecated background scripts (must use service_worker)
  // Scoped to the "background" block to avoid false positives in comments/other fields
  static const std::regex bg_block_regex(R"pattern("background"\s*:\s*\{[^}]*\})pattern");
  std::smatch match;
  if (std::regex_search(manifest_json, match, bg_block_regex)) {
    std::string bg_str = match.str();
    if (bg_str.find("\"scripts\"") != std::string::npos &&
        bg_str.find("\"service_worker\"") == std::string::npos) {
      if (out_error) {
        *out_error = "Extension rejected: Persistent background pages are deprecated. Service workers required in MV3.";
      }
      return false;
    }
  }

  return true;
}

bool VeloxExtensionManager::LoadUnpackedExtension(
    const std::filesystem::path& extension_path,
    std::string* out_extension_id) {
  std::filesystem::path manifest_path = extension_path / "manifest.json";
  if (!std::filesystem::exists(manifest_path)) {
    return false;
  }

  std::ifstream f(manifest_path);
  if (!f.is_open()) return false;

  std::stringstream buffer;
  buffer << f.rdbuf();
  std::string manifest_content = buffer.str();

  std::string validation_error;
  if (!ValidateManifestV3(manifest_content, &validation_error)) {
    return false;
  }

  VeloxExtensionInfo ext;
  ext.id = "velox_ext_" + std::to_string(extensions_.size() + 1);
  ext.name = extension_path.filename().string();
  ext.version = "1.0.0";
  ext.manifest_version = ManifestVersion::kManifestV3;
  ext.is_enabled = true;
  ext.install_path = extension_path;
  ext.has_background_worker = (manifest_content.find("service_worker") != std::string::npos);

  if (out_extension_id) {
    *out_extension_id = ext.id;
  }

  extensions_.push_back(ext);
  return true;
}

bool VeloxExtensionManager::DisableExtension(const std::string& extension_id) {
  for (auto& ext : extensions_) {
    if (ext.id == extension_id) {
      ext.is_enabled = false;
      return true;
    }
  }
  return false;
}

bool VeloxExtensionManager::EnableExtension(const std::string& extension_id) {
  for (auto& ext : extensions_) {
    if (ext.id == extension_id) {
      ext.is_enabled = true;
      return true;
    }
  }
  return false;
}

bool VeloxExtensionManager::RemoveExtension(const std::string& extension_id) {
  auto it = std::find_if(extensions_.begin(), extensions_.end(),
                         [&extension_id](const VeloxExtensionInfo& ext) {
                           return ext.id == extension_id;
                         });
  if (it == extensions_.end()) return false;
  extensions_.erase(it);
  return true;
}

const VeloxExtensionInfo* VeloxExtensionManager::GetExtension(const std::string& extension_id) const {
  for (const auto& ext : extensions_) {
    if (ext.id == extension_id) return &ext;
  }
  return nullptr;
}

std::vector<VeloxExtensionInfo> VeloxExtensionManager::GetInstalledExtensions() const {
  return extensions_;
}

}  // namespace velox
