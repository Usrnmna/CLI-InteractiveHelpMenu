"""Verify that compatibility reports preserve skipped, unsupported, and failure states."""

import unittest
from unittest.mock import patch

from core import HelpError
from command_paths import load_driver_registry
from discovery import build_profile
from live_compatibility import check_case


class LiveHarnessTests(unittest.TestCase):
    def test_missing_command_is_skipped_without_discovery(self):
        with patch("live_compatibility.shutil.which", return_value=None), patch("live_compatibility.discover") as probe:
            result = check_case(["missing"], load_driver_registry())
        self.assertEqual(result["status"], "skipped")
        probe.assert_not_called()

    def test_missing_expected_flags_is_a_failure(self):
        profile = build_profile("tool", [("fixture", "--flag   Description")])
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch("live_compatibility.discover", return_value=profile):
            result = check_case(["tool"], {}, expected_flags=["--required"])
        self.assertEqual(result["status"], "failed")
        self.assertIn("--required", result["reason"])

    def test_expected_no_options_is_distinct_from_unexpected_failure(self):
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch(
            "live_compatibility.discover", side_effect=HelpError("No recognizable option declarations")
        ):
            self.assertEqual(check_case(["npm"], {}, allow_empty=True)["status"], "unsupported")
            self.assertEqual(check_case(["tool"], {})["status"], "failed")

    def test_usable_profile_reports_real_sources_and_warnings(self):
        profile = build_profile("tool", [("fixture", "--flag   Description")])
        profile["discovery"] = {"sources": ["tool --help"], "warnings": ["Manual unavailable"]}
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch("live_compatibility.discover", return_value=profile):
            result = check_case(["tool"], {}, expected_flags=["--flag"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["option_count"], 1)
        self.assertEqual(result["warnings"], ["Manual unavailable"])


if __name__ == "__main__":
    unittest.main()
