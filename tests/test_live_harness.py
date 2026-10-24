"""Verify that compatibility reports preserve skipped, unsupported, and failure states."""

import unittest
import contextlib
import io
import json
from unittest.mock import patch

from core import HelpError
from command_paths import load_driver_registry
from discovery import ProbeError, build_profile
from live_compatibility import check_case, main, program_version


class LiveHarnessTests(unittest.TestCase):
    def test_configured_timeout_reaches_discovery_and_is_recorded(self):
        profile = build_profile("tool", [("fixture", "--flag   Description")])
        profile["discovery"] = {"sources": ["tool --help"], "warnings": []}
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch(
            "live_compatibility.discover", return_value=profile
        ) as discover:
            self.assertEqual(check_case(["tool"], {}, timeout=15)["status"], "passed")
        self.assertEqual(discover.call_args.args[1].timeout, 15)
        with patch("sys.argv", ["live_compatibility.py", "--case", "jq", "--timeout", "15"]), patch(
            "live_compatibility.check_case", return_value={"status": "passed"}
        ) as check, patch("live_compatibility.program_version", return_value="jq-1.7"), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 0)
        self.assertEqual(check.call_args.kwargs["timeout"], 15)
        self.assertEqual(json.loads(output.getvalue())["source_timeout_seconds"], 15)

    def test_invalid_timeout_rejects_before_probes(self):
        for value in ("0", "31", "nan", "inf"):
            with self.subTest(value=value), patch("sys.argv", ["live_compatibility.py", "--timeout", value]), patch(
                "live_compatibility.check_case"
            ) as check, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main()
            self.assertEqual(error.exception.code, 2)
            check.assert_not_called()

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
        with patch("live_compatibility.shutil.which", return_value="/fake/npm"), patch(
            "live_compatibility.discover", side_effect=ProbeError("No recognizable option declarations. Help source timed out.")
        ):
            self.assertEqual(check_case(["npm"], {}, allow_empty=True)["status"], "failed")

    def test_usable_profile_reports_real_sources_and_warnings(self):
        profile = build_profile("tool", [("fixture", "--flag   Description")])
        profile["discovery"] = {"sources": ["tool --help"], "warnings": ["Manual unavailable"]}
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch("live_compatibility.discover", return_value=profile):
            result = check_case(["tool"], {}, expected_flags=["--flag"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["option_count"], 1)
        self.assertEqual(result["warnings"], ["Manual unavailable"])

    def test_wrong_arity_and_unsupported_truncation_fail(self):
        profile = build_profile("jq", [("fixture", "--arg   Bind a variable\n-o   Truncated joined option")])
        with patch("live_compatibility.shutil.which", return_value="/fake/jq"), patch("live_compatibility.discover", return_value=profile):
            self.assertEqual(check_case(["jq"], {}, expected_counts={"--arg": 2})["status"], "failed")
            self.assertEqual(check_case(["jq"], {}, excluded=["-o"])["status"], "failed")

    def test_version_probes_use_only_declared_arguments_and_report_failures(self):
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch("live_compatibility.run_probe", return_value="\nTool 2.0\nDetails") as probe:
            self.assertEqual(program_version(["tool", "delete", "private"], ["--version"]), "Tool 2.0")
            self.assertEqual(probe.call_args.args[0], ["/fake/tool", "--version"])
            probe.reset_mock()
            self.assertIsNone(program_version(["tool"], None))
            probe.assert_not_called()
        with patch("live_compatibility.shutil.which", return_value="/fake/tool"), patch("live_compatibility.run_probe", side_effect=HelpError("timed out")):
            self.assertEqual(program_version(["tool"], ["--version"]), {"unavailable": "timed out"})

    def test_selected_known_cases_retain_sentinels_and_require_all_policy(self):
        for strict, expected in ((False, 0), (True, 1)):
            arguments = ["live_compatibility.py", "--case", "npm"] + (["--require-all"] if strict else [])
            with patch("sys.argv", arguments), patch("live_compatibility.check_case", return_value={"command": ["npm"], "status": "unsupported"}) as check, patch("live_compatibility.program_version", return_value="9.2.0"), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), expected)
            self.assertTrue(check.call_args.args[3])
            self.assertEqual(json.loads(output.getvalue())["summary"]["unsupported"], 1)

    def test_tier_filter_and_known_case_assertions(self):
        with patch("sys.argv", ["live_compatibility.py", "--tier", "extended"]), patch("live_compatibility.check_case", return_value={"status": "skipped"}), patch("live_compatibility.program_version", return_value=None), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 0)
        self.assertEqual({record["tier"] for record in json.loads(output.getvalue())["cases"]}, {"extended"})
        with patch("sys.argv", ["live_compatibility.py", "--case", "jq"]), patch("live_compatibility.check_case", return_value={"status": "passed"}) as check, patch("live_compatibility.program_version", return_value="jq-1.7"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 0)
        self.assertIn("--arg", check.call_args.args[2])
        self.assertEqual(check.call_args.args[5]["--arg"], 2)


if __name__ == "__main__":
    unittest.main()
