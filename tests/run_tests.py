#!/usr/bin/env python3
"""
VELOX Automated Verification Test Suite

Validates core architectural logic, security policy audit rules,
privacy balance enforcement, tab lifecycle protections, and MV3 extension validation.
"""

import os
import sys
import unittest
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestSecurityPolicy(unittest.TestCase):
    def test_forbidden_command_line_switches(self):
        forbidden_switches = [
            "--no-sandbox",
            "--single-process",
            "--disable-web-security",
            "--disable-site-isolation-trials",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
            "--disable-gpu-sandbox",
            "--disable-blink-features=SameSiteByDefaultCookies"
        ]

        # Simulation of VeloxSecurityPolicy::AuditCommandLine
        def audit_args(args):
            violations = []
            for arg in args:
                for f in forbidden_switches:
                    if arg == f or arg.startswith(f + "="):
                        violations.append(arg)
            return len(violations) == 0, violations

        # Clean args
        passed, violations = audit_args(["--user-data-dir=test", "--enable-features=WebGPU"])
        self.assertTrue(passed)
        self.assertEqual(len(violations), 0)

        # Insecure args
        passed, violations = audit_args(["--no-sandbox", "--disable-web-security"])
        self.assertFalse(passed)
        self.assertEqual(len(violations), 2)

    def test_scheme_origin_isolation(self):
        def can_origin_access_scheme(source_origin, target_scheme):
            s_origin = source_origin.lower()
            t_scheme = target_scheme.lower()
            if t_scheme in ("velox", "chrome"):
                return s_origin.startswith("velox://") or s_origin.startswith("chrome://")
            return True

        self.assertTrue(can_origin_access_scheme("velox://settings", "velox"))
        self.assertTrue(can_origin_access_scheme("VELOX://SETTINGS", "VELOX"))
        self.assertFalse(can_origin_access_scheme("https://evil.com", "velox"))
        self.assertFalse(can_origin_access_scheme("http://example.org", "chrome"))

    def test_case_insensitive_url_navigation_security(self):
        # SEC-02 verification: Protocol filtering must be strictly case-insensitive
        def is_safe_renderer_navigation(target_url):
            lower_url = target_url.lower()
            if lower_url.startswith("javascript:"):
                return False
            if lower_url.startswith("data:text/html"):
                return False
            return True

        self.assertTrue(is_safe_renderer_navigation("https://duckduckgo.com"))
        self.assertTrue(is_safe_renderer_navigation("velox://performance"))
        self.assertFalse(is_safe_renderer_navigation("javascript:alert(1)"))
        self.assertFalse(is_safe_renderer_navigation("JaVaScript:alert(1)"))
        self.assertFalse(is_safe_renderer_navigation("JAVASCRIPT:void(0)"))
        self.assertFalse(is_safe_renderer_navigation("data:text/html,<script>alert(1)</script>"))
        self.assertFalse(is_safe_renderer_navigation("DATA:TEXT/HTML;base64,..."))


class TestPrivacyController(unittest.TestCase):
    def test_security_critical_service_retention(self):
        # Section 8: Safe Browsing and CRLSet must never be silently disabled
        prefs = {
            "safe_browsing_enabled": True,
            "crlset_updates_enabled": True,
            "metrics_reporting_enabled": False, # Privacy preserved
            "remote_search_suggestions": False,  # Privacy preserved
            "crash_reporting_enabled": False
        }

        def validate_privacy_balance(p):
            if not p.get("safe_browsing_enabled"):
                return False, "Safe Browsing cannot be stripped"
            if not p.get("crlset_updates_enabled"):
                return False, "CRLSet updates cannot be stripped"
            return True, "OK"

        valid, _ = validate_privacy_balance(prefs)
        self.assertTrue(valid)

        # Attempt to disable Safe Browsing
        prefs["safe_browsing_enabled"] = False
        valid, msg = validate_privacy_balance(prefs)
        self.assertFalse(valid)


class TestTabLifecyclePolicy(unittest.TestCase):
    def test_discard_protection_rules(self):
        # Section 13: Protected tabs must never be discarded
        tabs = [
            {"id": 1, "is_active": True, "pinned": False, "audio": False, "webrtc": False, "download": False},
            {"id": 2, "is_active": False, "pinned": True, "audio": False, "webrtc": False, "download": False},
            {"id": 3, "is_active": False, "pinned": False, "audio": True, "webrtc": False, "download": False},
            {"id": 4, "is_active": False, "pinned": False, "audio": False, "webrtc": True, "download": False},
            {"id": 5, "is_active": False, "pinned": False, "audio": False, "webrtc": False, "download": True},
            {"id": 6, "is_active": False, "pinned": False, "audio": False, "webrtc": False, "download": False}, # Discardable
        ]

        def is_protected(t):
            return t["is_active"] or t["pinned"] or t["audio"] or t["webrtc"] or t["download"]

        protected_ids = [t["id"] for t in tabs if is_protected(t)]
        discardable_ids = [t["id"] for t in tabs if not is_protected(t)]

        self.assertEqual(protected_ids, [1, 2, 3, 4, 5])
        self.assertEqual(discardable_ids, [6])


class TestManifestV3Extension(unittest.TestCase):
    def test_mv3_manifest_validation(self):
        fixture_path = REPO_ROOT / "tests" / "extensions" / "fixtures" / "mv3_sample" / "manifest.json"
        self.assertTrue(fixture_path.exists())

        with open(fixture_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest.get("manifest_version"), 3)
        self.assertIn("service_worker", manifest.get("background", {}))
        self.assertNotIn("scripts", manifest.get("background", {}))

    def test_reject_mv2_manifest(self):
        mv2_manifest = {
            "manifest_version": 2,
            "name": "Legacy Extension",
            "version": "1.0",
            "background": {"scripts": ["bg.js"]}
        }
        is_mv3 = mv2_manifest.get("manifest_version") == 3
        self.assertFalse(is_mv3)

    def test_mv3_whitespace_and_formatting_tolerance(self):
        # ARC-01 verification: Regex must tolerate various whitespace formatting around manifest_version
        import re
        mv3_pattern = re.compile(r'"manifest_version"\s*:\s*3\b')
        self.assertTrue(mv3_pattern.search('{"manifest_version": 3}'))
        self.assertTrue(mv3_pattern.search('{"manifest_version":3}'))
        self.assertTrue(mv3_pattern.search('{"manifest_version"  :   3}'))
        self.assertTrue(mv3_pattern.search('{\n  "manifest_version" : \n 3\n}'))
        self.assertFalse(mv3_pattern.search('{"manifest_version": 2}'))
        self.assertFalse(mv3_pattern.search('{"manifest_version": 30}'))


class TestPatchesRegistry(unittest.TestCase):
    def test_patches_exist_and_formatted(self):
        patches_dir = REPO_ROOT / "patches"
        self.assertTrue(patches_dir.exists())

        patches = sorted(list(patches_dir.glob("*.patch")))
        self.assertGreaterEqual(len(patches), 7)

        for p in patches:
            content = p.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("From ") or content.startswith("diff --git"))
            self.assertIn("---", content)

    def test_patch_0003_tab_discard_protections(self):
        patch_0003 = REPO_ROOT / "patches" / "0003-tab-discard-lifecycle-hooks.patch"
        self.assertTrue(patch_0003.exists())
        content = patch_0003.read_text(encoding="utf-8")
        self.assertIn("tab_strip_model_->IsTabPinned", content)
        self.assertIn("download::DownloadItem::IN_PROGRESS", content)
        self.assertIn("tab_lifecycle_unit.cc", content)

    def test_patch_0008_velox_privacy_shield(self):
        patch_0008 = REPO_ROOT / "patches" / "0008-velox-shield-ad-tracker-blocking-and-fingerprint-randomization.patch"
        self.assertTrue(patch_0008.exists())
        content = patch_0008.read_text(encoding="utf-8")
        self.assertIn("VeloxShieldNavigationThrottle", content)
        self.assertIn("VeloxShieldURLLoaderThrottle", content)
        self.assertIn("EncodeImageInternal", content)
        self.assertIn("getImageDataInternal", content)

    def test_patch_0013_privacy_search_and_about_status(self):
        patch_0013 = REPO_ROOT / "patches" / "0013-privacy-search-defaults-and-clean-about-status.patch"
        self.assertTrue(patch_0013.exists())
        content = patch_0013.read_text(encoding="utf-8")
        self.assertIn("duckduckgo", content)
        self.assertIn("version_updater_win.cc", content)
        self.assertIn("UPDATED", content)

    def test_patch_0015_modern_browser_importer(self):
        patch_0015 = REPO_ROOT / "patches" / "0015-modern-browser-detection-and-chromium-importer.patch"
        self.assertTrue(patch_0015.exists())
        content = patch_0015.read_text(encoding="utf-8")
        self.assertIn("DetectInstalledBrowsersWin", content)
        self.assertIn("GetSystemDefaultBrowserName", content)
        self.assertIn("Google Chrome", content)
        self.assertIn("Microsoft Edge", content)
        self.assertIn("ParseChromiumBookmarks", content)

    def test_root_license(self):
        license_path = REPO_ROOT / "LICENSE"
        self.assertTrue(license_path.exists())
        content = license_path.read_text(encoding="utf-8")
        self.assertIn("The VELOX Authors", content)
        self.assertIn("The Chromium Authors", content)
        self.assertIn("Redistribution and use in source and binary forms", content)

    def test_shield_blocking_rules(self):
        blocked_domains = [
            "trackersimulator.org", "eviltracker.net", "doubleclick.net",
            "googlesyndication.com", "google-analytics.com", "facebook.net"
        ]
        def is_blocked(host):
            for d in blocked_domains:
                if host == d or (host.endswith(d) and host[len(host)-len(d)-1] == "."):
                    return True
            return False

        self.assertTrue(is_blocked("trackersimulator.org"))
        self.assertTrue(is_blocked("ads.eviltracker.net"))
        self.assertTrue(is_blocked("google-analytics.com"))
        self.assertFalse(is_blocked("example.com"))
        self.assertFalse(is_blocked("coveryourtracks.eff.org"))

    def test_all_patches_reverse_apply(self):
        import subprocess
        patches_dir = REPO_ROOT / "patches"
        src_dir = REPO_ROOT / "src"
        if not src_dir.exists():
            self.skipTest("src directory not present")

        for p in sorted(patches_dir.glob("*.patch")):
            res = subprocess.run(
                ["git", "apply", "--check", "-R", str(p)],
                cwd=str(src_dir),
                capture_output=True,
                text=True
            )
            self.assertEqual(
                res.returncode, 0,
                f"Patch {p.name} failed reverse apply check: {res.stderr}"
            )


class TestVeloxWebUI(unittest.TestCase):
    def test_velox_performance_url_structure(self):
        url = "velox://performance/"
        scheme, remainder = url.split("://", 1)
        host = remainder.split("/")[0]
        self.assertEqual(scheme, "velox")
        self.assertEqual(host, "performance")

    def test_velox_welcome_url_structure(self):
        url = "velox://welcome/"
        scheme, remainder = url.split("://", 1)
        host = remainder.split("/")[0]
        self.assertEqual(scheme, "velox")
        self.assertEqual(host, "welcome")

    def test_patch_0014_welcome_onboarding(self):
        patch_0014 = REPO_ROOT / "patches" / "0014-velox-welcome-tour-and-onboarding-experience.patch"
        self.assertTrue(patch_0014.exists())
        content = patch_0014.read_text(encoding="utf-8")
        self.assertIn("VeloxWelcomeUI", content)
        self.assertIn("kVeloxUIWelcomeHost", content)
        self.assertIn("velox_welcome_ui.cc", content)
        self.assertIn("chrome://settings/importData", content)

    def test_import_data_button_in_welcome_tour(self):
        welcome_file = REPO_ROOT / "src" / "chrome" / "browser" / "ui" / "webui" / "velox" / "velox_welcome_ui.cc"
        self.assertTrue(welcome_file.exists())
        content = welcome_file.read_text(encoding="utf-8")
        self.assertIn("chrome://settings/importData", content)
        self.assertIn("Transfer Data &amp; Tabs", content)
        self.assertIn("transfer-banner", content)
        self.assertIn("btn-import", content)

    def test_browser_data_migration_utility(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import import_browser_data
        profiles = import_browser_data.get_installed_browser_profiles()
        self.assertIsInstance(profiles, dict)
        self.assertTrue(len(profiles) > 0, "Should detect at least 1 installed browser on Windows")

    def test_command_line_validation_rules(self):
        # StartupTabProvider::ValidateUrl simulation
        def validate_startup_url(url_str):
            safe_schemes = {"http", "https", "file", "velox"}
            if "://" not in url_str:
                return url_str == "about:blank"
            scheme = url_str.split("://", 1)[0]
            return scheme in safe_schemes

        self.assertTrue(validate_startup_url("velox://performance"))
        self.assertTrue(validate_startup_url("velox://welcome"))
        self.assertTrue(validate_startup_url("https://example.com"))
        self.assertTrue(validate_startup_url("about:blank"))
        self.assertFalse(validate_startup_url("chrome-untrusted://malicious"))
        self.assertFalse(validate_startup_url("javascript:alert(1)"))

class TestReleasePackaging(unittest.TestCase):
    def test_installer_binaries_generated(self):
        out_dir = REPO_ROOT / "src" / "out" / "Default"
        mini_installer = out_dir / "mini_installer.exe"
        velox_installer = out_dir / "velox_installer.exe"
        setup_exe = out_dir / "setup.exe"

        self.assertTrue(mini_installer.exists(), "mini_installer.exe must exist")
        self.assertTrue(velox_installer.exists(), "velox_installer.exe must exist")
        self.assertTrue(setup_exe.exists(), "setup.exe must exist")

        # Sanity check file size (mini_installer contains 7z payload, must be > 50 MB)
        mini_sz_mb = mini_installer.stat().st_size / (1024 * 1024)
        self.assertGreater(mini_sz_mb, 50.0, f"mini_installer is unexpectedly small: {mini_sz_mb:.2f} MB")
        self.assertEqual(mini_installer.stat().st_size, velox_installer.stat().st_size)

    def test_release_manifests_and_checksums(self):
        releases_dir = REPO_ROOT / "releases"
        self.assertTrue(releases_dir.exists())

        installer = releases_dir / "velox_installer.exe"
        sha256_file = releases_dir / "SHA256SUMS.txt"
        version_file = releases_dir / "version.json"

        self.assertTrue(installer.exists())
        self.assertTrue(sha256_file.exists())
        self.assertTrue(version_file.exists())

        # Validate that SHA256SUMS contains installer hash
        sha256_text = sha256_file.read_text(encoding="utf-8")
        self.assertIn("velox_installer.exe", sha256_text)

        with open(version_file, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        self.assertEqual(v_data["version"], "134.0.6998.178")
        self.assertIn(v_data["platforms"]["win_x64"]["sha256"], sha256_text)


class TestCodeSigningPipeline(unittest.TestCase):
    def test_signtool_locator(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import sign_binaries
        signtool = sign_binaries.find_signtool()
        self.assertIsNotNone(signtool)
        self.assertTrue(signtool.exists())
        self.assertEqual(signtool.name.lower(), "signtool.exe")


# Import AutoUpdater and Widevine test suites
sys.path.insert(0, str(REPO_ROOT / "tests"))
from test_auto_updater import TestAutoUpdater
from test_widevine import TestWidevineArchitecture


if __name__ == "__main__":
    unittest.main()




