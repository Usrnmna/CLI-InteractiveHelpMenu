"""Protect static contexts, private driver operands, and aligned help parsing."""

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import help_route, load_driver_registry
from core import find_context
from diagnostics import doctor, explain
from discovery import Settings, build_profile, discover, parse_help


SECRET = "PRIVATE_DRIVER_REVIEW_SENTINEL"


def static_profile(command):
    """Supply explicit metadata without introducing an automatic help route."""
    return {"command": command, "description": "Review fixture",
            "categories": [{"name": "Options", "options": [
                {"flag": "--flag", "summary": "Fixture flag"}]}]}


class DiagnosticReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.profiles = self.folder / "profiles"
        self.profiles.mkdir()
        self.drivers = self.folder / "drivers"
        self.drivers.mkdir()
        self.environment = patch.dict(os.environ, {
            "CLI_HELP_PROFILES": str(self.profiles), "CLI_HELP_DRIVERS": str(self.drivers),
            "CLI_HELP_CONFIG": "", "CLI_HELP_DISCOVERY": "auto",
            "CLI_HELP_CACHE_DIR": str(self.folder / "absent-cache"), "CLI_HELP_CACHE_TTL": "86400",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_static_nested_profiles_remain_explainable_in_every_mode(self):
        for name in ("uninstalled-fixture", "echo", "git"):
            profile = static_profile([name, "review-leaf"])
            (self.profiles / (name + ".json")).write_text(json.dumps(profile))
            line = name + " review-leaf --fl"
            self.assertEqual(find_context(line, len(line), [profile]).profile, profile)
            for mode in ("off", "man", "auto"):
                with self.subTest(name=name, mode=mode), patch.dict(os.environ, {"CLI_HELP_DISCOVERY": mode}):
                    report = explain(ROOT, line, len(line))
                self.assertEqual(report["status"], "ready", report)
                self.assertEqual(report["code"], "context_valid")
                self.assertEqual(report["profile"]["kind"], "custom")
                self.assertEqual(report["route"]["kind"], "profile_only")
                self.assertEqual(report["route"]["help_arguments"], [])
                self.assertIsNone(report["route"]["manual"])
                self.assertEqual(report["cache"]["status"], "disabled" if mode == "off" else "not_applicable")

    def write_private_driver(self):
        """Create synthetic private constants whose diagnostic disclosure is forbidden."""
        document = {"command": "fixture", "paths": [{"command": [],
            "help": ["--help", "--token=" + SECRET, "--password", SECRET],
            "man": "private-" + SECRET}]}
        path = self.drivers / "fixture.json"
        path.write_text(json.dumps(document))
        return path, document

    def test_missing_intermediate_route_does_not_claim_a_static_profile(self):
        document = {"command": "fixture", "paths": [{"command": ["group", "leaf"],
                    "help": ["help", "group", "leaf"], "man": None}]}
        (self.drivers / "fixture.json").write_text(json.dumps(document))
        with patch("subprocess.Popen", side_effect=AssertionError("Target process started")):
            report = explain(ROOT, "fixture group --", len("fixture group --"))
        self.assertEqual(report["route"]["kind"], "unconfigured")
        self.assertEqual(report["profile"]["kind"], "discovery_required")
        self.assertEqual(report["status"], "needs_discovery")
        self.assertNotEqual(report["status"], "ready")

    def test_private_fixed_arguments_and_manual_aliases_are_redacted_without_mutating_routes(self):
        path, document = self.write_private_driver()
        before = path.read_bytes()
        with patch("subprocess.Popen", side_effect=AssertionError("Target process started")):
            for mode in ("off", "man", "auto"):
                with self.subTest(mode=mode), patch.dict(os.environ, {"CLI_HELP_DISCOVERY": mode}):
                    report = explain(ROOT, "fixture --", len("fixture --"))
                    health = doctor(ROOT)
                self.assertNotIn(SECRET, json.dumps([report, health]))
                self.assertEqual(report["route"]["help_arguments"], ["--help", "<redacted>", "<redacted>", "<redacted>"])
                self.assertTrue(report["route"]["help_arguments_redacted"])
                self.assertEqual(report["route"]["manual"], "<redacted>")
                self.assertTrue(report["route"]["manual_redacted"])
        route = help_route("fixture", (), load_driver_registry(self.drivers))
        self.assertEqual(list(route.arguments), document["paths"][0]["help"])
        self.assertEqual(route.manual, document["paths"][0]["man"])
        self.assertEqual(path.read_bytes(), before)

    def test_public_cli_diagnostics_redact_configuration_and_pending_values(self):
        self.write_private_driver()
        (self.profiles / "echo.json").write_text(json.dumps(static_profile(["echo", "review-leaf"])))
        for mode, line in (("--doctor", "fixture --"), ("--explain", "fixture --"),
                           ("--explain", "echo review-leaf --fl '" + SECRET + "'")):
            environment = dict(os.environ, CLI_HELP_LINE=line,
                               CLI_HELP_POINT=str(line.index("--fl") + 4 if "--fl" in line else len(line)))
            result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), mode],
                                    env=environment, capture_output=True, text=True, timeout=10)
            with self.subTest(mode=mode, line=line):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(SECRET, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                if "review-leaf" in line:
                    self.assertEqual(report["status"], "ready")
                    self.assertEqual(report["route"]["kind"], "profile_only")
        self.assertFalse((self.folder / "absent-cache").exists())

    def test_new_reports_never_start_targets_or_write_files(self):
        self.write_private_driver()
        (self.profiles / "echo.json").write_text(json.dumps(static_profile(["echo", "review-leaf"])))
        original_open = io.open

        def read_only(file, mode="r", *args, **kwargs):
            self.assertFalse(any(character in mode for character in "wax+"), mode)
            return original_open(file, mode, *args, **kwargs)

        with patch("subprocess.Popen", side_effect=AssertionError("Target process started")), \
             patch("discovery.run_probe", side_effect=AssertionError("Probe started")), \
             patch("os.mkdir", side_effect=AssertionError("Directory created")), \
             patch("os.replace", side_effect=AssertionError("File replaced")), \
             patch("discovery.write_cache", side_effect=AssertionError("Cache written")), \
             patch("io.open", side_effect=read_only):
            reports = [doctor(ROOT), explain(ROOT, "fixture --", len("fixture --")),
                       explain(ROOT, "echo review-leaf --fl", len("echo review-leaf --fl"))]
        self.assertNotIn(SECRET, json.dumps(reports))
        self.assertEqual(reports[-1]["status"], "ready")

    def test_pytest_report_matches_the_mandatory_fixed_request(self):
        document = {"command": "pytest", "paths": [{"command": [],
                    "help": ["help", "--token=" + SECRET], "man": None}]}
        (self.drivers / "pytest.json").write_text(json.dumps(document))
        report = explain(ROOT, "pytest --", len("pytest --"))
        self.assertEqual(report["route"]["help_arguments"], ["--help", "--noconftest"])
        self.assertEqual(report["route"]["help_override"], "pytest_no_conftest")
        self.assertNotIn(SECRET, json.dumps(report))
        with patch("discovery.shutil.which", side_effect=lambda name: None if name == "man" else "/fixed/pytest"), \
             patch("discovery.executable_identity", return_value={"fixture": True}), \
             patch("discovery.run_probe", return_value="Options:\n  --flag  Fixture flag\n") as probe:
            discover("pytest", Settings(cache_ttl=0), driver_registry=load_driver_registry(self.drivers))
        self.assertEqual(probe.call_args.args[0], ["/fixed/pytest", "--help", "--noconftest"])

    def test_version_dependent_yarn_help_is_not_reported_as_verified(self):
        with patch.dict(os.environ, {"CLI_HELP_DRIVERS": str(ROOT / "config/drivers.example")}), \
             patch("subprocess.Popen", side_effect=AssertionError("Target process started")):
            report = explain(ROOT, "yarn run --", len("yarn run --"))
        self.assertTrue(report["route"]["help_arguments_pending_identity"])


class AlignedRangeReviewTests(unittest.TestCase):
    def test_numeric_ranges_are_excluded_before_column_splitting(self):
        for left in (" ", "  ", "\t", " \t "):
            for right in (" ", "  ", "\t"):
                for dots in ("...", "…"):
                    declaration = "  -0" + left + dots + right + "-9  Compression range"
                    with self.subTest(declaration=declaration):
                        self.assertEqual(parse_help("Options:\n" + declaration, "fixture"), [])
        profile = build_profile("gzip", [("fixture", "Options:\n  -1, --fast  Fast compression\n")])
        self.assertEqual({option["flag"] for category in profile["categories"] for option in category["options"]},
                         {"-1", "--fast"})


if __name__ == "__main__":
    unittest.main()
