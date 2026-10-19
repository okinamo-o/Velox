#!/usr/bin/env python3
"""
Test Suite for VELOX Remote Auto-Updater
"""

import sys
import json
import hashlib
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_update

class TestAutoUpdater(unittest.TestCase):
    def test_version_comparison(self):
        # Equal versions
        self.assertEqual(check_update.compare_versions("134.0.6998.178", "134.0.6998.178"), 0)
        self.assertEqual(check_update.compare_versions("1.0.0", "1.0.0.0"), 0)

        # Older local version (update available)
        self.assertEqual(check_update.compare_versions("134.0.6998.178", "134.0.6998.179"), -1)
        self.assertEqual(check_update.compare_versions("134.0.6998.178", "134.1.0.0"), -1)
        self.assertEqual(check_update.compare_versions("134.0.6998.178", "135.0.0.0"), -1)

        # Newer local version (ahead of remote)
        self.assertEqual(check_update.compare_versions("135.0.0.0", "134.0.6998.178"), 1)
        self.assertEqual(check_update.compare_versions("134.0.6999.0", "134.0.6998.178"), 1)

    def test_version_manifest_schema(self):
        manifest_path = REPO_ROOT / "releases" / "version.json"
        self.assertTrue(manifest_path.exists())

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest.get("name"), "VELOX Browser")
        self.assertTrue(manifest.get("version"))
        self.assertEqual(manifest.get("channel"), "stable")
        
        platforms = manifest.get("platforms", {})
        self.assertIn("win_x64", platforms)
        win_x64 = platforms["win_x64"]
        self.assertTrue(win_x64.get("installer_filename").endswith(".exe"))
        self.assertTrue(win_x64.get("installer_url").startswith("https://"))
        self.assertEqual(len(win_x64.get("sha256", "")), 64) # Valid SHA-256 hex string

    def test_sha256_verification(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
            test_content = b"VELOX-SECURE-UPDATE-PAYLOAD-SIMULATION"
            tmp.write(test_content)
            tmp_path = Path(tmp.name)

        try:
            expected_hash = hashlib.sha256(test_content).hexdigest()
            tampered_hash = hashlib.sha256(b"CORRUPTED").hexdigest()

            # Test correct hash
            valid, actual = check_update.verify_file_sha256(tmp_path, expected_hash)
            self.assertTrue(valid)
            self.assertEqual(actual, expected_hash)

            # Test corrupted / mismatched hash
            valid, _ = check_update.verify_file_sha256(tmp_path, tampered_hash)
            self.assertFalse(valid)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_simulated_remote_update_workflow(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            mock_manifest = {
                "name": "VELOX Browser",
                "version": "135.0.7000.0",
                "release_notes_url": "https://github.com/velox-browser/velox/releases/tag/v135.0.7000.0",
                "platforms": {
                    "win_x64": {
                        "installer_url": "https://updates.veloxbrowser.com/velox_installer.exe",
                        "sha256": "0" * 64
                    }
                }
            }
            json.dump(mock_manifest, tmp)
            mock_path = tmp.name

        try:
            manifest = check_update.fetch_manifest(mock_path)
            self.assertEqual(manifest["version"], "135.0.7000.0")
            cmp = check_update.compare_versions("134.0.6998.178", manifest["version"])
            self.assertEqual(cmp, -1, "Should flag newer version as update available")
        finally:
            Path(mock_path).unlink(missing_ok=True)

    def test_reject_missing_sha256_in_download(self):
        # SEC-01 fix verification: download_installer must abort if sha256 is missing or invalid
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "installer.exe"
            # Missing SHA-256
            self.assertFalse(check_update.download_installer("http://example.com/installer.exe", target_file, expected_sha256=None))
            # Malformed SHA-256 (not 64 chars)
            self.assertFalse(check_update.download_installer("http://example.com/installer.exe", target_file, expected_sha256="abc"))

if __name__ == "__main__":
    unittest.main()
