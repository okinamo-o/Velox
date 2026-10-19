#!/usr/bin/env python3
"""
VELOX Widevine DRM & Protected Media Architecture Test Suite
"""

import os
import sys
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import install_widevine

class TestWidevineArchitecture(unittest.TestCase):
    def test_gn_args_enable_widevine(self):
        args_file = REPO_ROOT / "src" / "out" / "Default" / "args.gn"
        self.assertTrue(args_file.exists())
        content = args_file.read_text(encoding="utf-8")
        self.assertIn("enable_widevine = true", content)

    def test_generated_widevine_buildflags(self):
        header_file = REPO_ROOT / "src" / "out" / "Default" / "gen" / "third_party" / "widevine" / "cdm" / "buildflags.h"
        self.assertTrue(header_file.exists())
        content = header_file.read_text(encoding="utf-8")
        self.assertIn("#define BUILDFLAG_INTERNAL_ENABLE_WIDEVINE() (1)", content)
        self.assertIn("#define BUILDFLAG_INTERNAL_ENABLE_WIDEVINE_CDM_COMPONENT() (1)", content)

    def test_widevine_inspector_and_manifest(self):
        appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        cdm_dir = appdata / "Velox" / "Application" / "134.0.6998.178" / "WidevineCdm"
        if not cdm_dir.exists():
            self.skipTest("WidevineCdm directory not provisioned on this machine")

        info = install_widevine.inspect_widevine_directory(cdm_dir)
        self.assertIsNotNone(info)
        self.assertTrue(info["is_complete"])
        self.assertTrue(info["version"].startswith("4."))
        self.assertTrue(Path(info["dll_path"]).exists())
        self.assertTrue(Path(info["manifest_path"]).exists())

        # Validate manifest content
        with open(info["manifest_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertIn("version", manifest)
        self.assertIn("x-cdm-codecs", manifest)

if __name__ == "__main__":
    unittest.main()
