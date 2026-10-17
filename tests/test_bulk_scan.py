"""Exercise batch inventory, report classification, preservation, and command isolation."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from bulk_scan import inventory_commands, scan_installed
from command_paths import load_driver_registry
from core import HelpError, load_profiles, find_context, insert_option
from drivers import parse_driver
from manual_import import ManualCollection


GOOD = "OPTIONS\n  --alpha   Enable alpha\n  --output FILE   Select output\n"
PARTIAL = GOOD + "  -Wl,<options>   Unsupported joined syntax\n"


class BulkScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.bin = self.folder / "bin"
        self.bin.mkdir()
        self.renderers = self.folder / "renderers"
        self.renderers.mkdir()
        self.output = self.folder / "collection"
        self.log = self.folder / "manual-calls"
        self.marker = self.folder / "target-executed"
        write_executable(self.renderers / "man",
                         "import json, sys\n"
                         f"with open({str(self.log)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                         "name = sys.argv[-1]\n"
                         "if name == 'missing':\n    print('No manual entry'); sys.exit(16)\n"
                         "if name == 'broken':\n    print('Renderer error'); sys.exit(2)\n"
                         "if name == 'empty':\n    print('A manual with no option declarations'); sys.exit(0)\n"
                         "if name == 'slow':\n    import time; time.sleep(5)\n"
                         "if name == 'huge':\n    print('x' * 600000); sys.exit(0)\n"
                         f"print({PARTIAL!r} if name == 'partial' else {GOOD!r})\n")
        self.environment = patch.dict(os.environ, {"PATH": str(self.renderers)})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def command(self, name):
        path = self.bin / name
        write_executable(path, f"import pathlib\npathlib.Path({str(self.marker)!r}).touch()\n")
        return path

    def scan(self, **kwargs):
        return scan_installed(self.output, directories=[self.bin], **kwargs)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_inventory_preserves_precedence_aliases_and_ignores_nonexecutables(self):
        self.command("alpha")
        (self.bin / "alias").symlink_to(self.bin / "alpha")
        (self.bin / "broken-link").symlink_to(self.bin / "absent")
        (self.bin / "directory").mkdir()
        (self.bin / "plain").write_text("not executable")
        other = self.folder / "other"
        other.mkdir()
        write_executable(other / "alpha", "pass\n")
        commands, warnings = inventory_commands([self.bin, self.bin, other])
        self.assertEqual([entry["command"] for entry in commands], [["alias"], ["alpha"]])
        self.assertEqual(commands[1]["executable"], str(self.bin / "alpha"))
        self.assertEqual(commands[1]["shadowed"], [str(other / "alpha")])
        self.assertEqual(warnings, [])

    def test_report_distinguishes_success_failure_and_manual_adjustment(self):
        for name in ["good", "partial", "missing", "empty", "broken"]:
            self.command(name)
        report = self.scan()
        records = {record["command"][0]: record for record in report["records"]}
        self.assertEqual(report["summary"], {"success": 1, "needs_adjustment": 3, "failed": 1,
                                            "skipped": 0, "pending": 0, "generated": 2})
        self.assertTrue(records["partial"]["generated"])
        self.assertEqual(records["partial"]["issues"][0]["code"], "unsupported_declarations")
        self.assertEqual(records["missing"]["reason"], "missing_manual")
        self.assertEqual(records["empty"]["reason"], "unparsed_manual")
        self.assertEqual(records["broken"]["reason"], "renderer_exit")
        self.assertEqual(json.loads(Path(report["report"]).read_text()), report)
        self.assertFalse(self.marker.exists())
        self.assertTrue(all(call[:-1] == ["-P", "/bin/cat", "--no-hyphenation", "--no-justification", "-s", "1:8", "--"] for call in self.calls()))

    def test_generated_collection_loads_and_requires_no_discovery_for_insertion(self):
        self.command("good")
        report = self.scan()
        profiles = load_profiles(self.output / "profiles")
        registry = load_driver_registry(self.output / "drivers")
        self.assertEqual(registry["good"].paths[()].arguments, ())
        context = find_context("good --al", 9, profiles, driver_registry=registry,
                               discover=lambda *args, **kwargs: self.fail("Unexpected probe"))
        self.assertEqual(context.profile["command"], ["good"])
        option = next(option for category in context.profile["categories"] for option in category["options"]
                      if option["flag"] == "--alpha")
        self.assertEqual(insert_option(context, option), ("good --alpha ", 13))
        self.assertFalse(self.marker.exists())
        self.assertEqual(report["summary"]["generated"], 1)

    def test_repeat_skips_existing_entries_before_rendering(self):
        self.command("good")
        first = self.scan()
        profile = Path(first["records"][0]["profile"])
        before = profile.read_bytes()
        second = self.scan()
        self.assertEqual(second["records"][0]["reason"], "existing_entry")
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(profile.read_bytes(), before)
        self.scan(replace=True)
        self.assertEqual(len(self.calls()), 2)

    def test_glob_filters_and_limit_report_unprocessed_commands(self):
        for name in ["aa", "ab", "ac", "other"]:
            self.command(name)
        report = self.scan(includes=["a*"], excludes=["ab"], limit=1)
        reasons = {record["command"][0]: record.get("reason") for record in report["records"]}
        self.assertEqual(reasons, {"aa": "manual_imported", "ab": "filtered", "ac": "limit", "other": "filtered"})
        self.assertEqual([call[-1] for call in self.calls()], ["aa"])

    def test_unrepresentable_and_undecodable_names_are_reported_without_probe(self):
        self.command("bad name")
        filename = os.fsencode(self.bin) + b"/bad-\xff"
        descriptor = os.open(filename, os.O_CREAT | os.O_WRONLY, 0o700)
        os.close(descriptor)
        report = self.scan()
        self.assertEqual(report["summary"]["needs_adjustment"], 2)
        self.assertEqual(self.calls(), [])
        self.assertEqual(json.loads(Path(report["report"]).read_text()), report)

    def test_limit_counts_attempts_without_counting_preserved_entries(self):
        for name in ["aa", "bb", "broken", "cc"]:
            self.command(name)
        self.assertEqual(self.scan(limit=1)["summary"]["generated"], 1)
        self.assertEqual(self.scan(limit=1)["summary"]["generated"], 1)
        report = self.scan(limit=1)
        self.assertEqual(report["summary"]["failed"], 1)
        self.assertEqual(report["records"][-1]["reason"], "limit")
        self.assertEqual([call[-1] for call in self.calls()], ["aa", "bb", "broken"])

    def test_missing_path_directory_is_recorded_and_other_directories_scan(self):
        self.command("good")
        report = scan_installed(self.output, directories=[self.folder / "missing", self.bin])
        self.assertEqual(len(report["inventory_warnings"]), 1)
        self.assertEqual(report["summary"]["generated"], 1)

    def test_empty_and_relative_path_entries_match_shell_inventory(self):
        self.command("good")
        original = os.getcwd()
        try:
            os.chdir(self.folder)
            commands, _ = inventory_commands(["bin", "bin"])
            self.assertEqual(len(commands), 1)
            os.chdir(self.bin)
            commands, _ = inventory_commands([""])
            self.assertEqual(commands[0]["executable"], str(self.bin / "good"))
            with patch.dict(os.environ, {"PATH": ":" + str(self.bin)}):
                commands, _ = inventory_commands()
                self.assertEqual(len(commands), 1)
                self.assertEqual(commands[0]["executable"], str(self.bin / "good"))
        finally:
            os.chdir(original)

    def test_timeout_and_oversized_manuals_do_not_stop_other_entries(self):
        for name in ["good", "huge", "slow"]:
            self.command(name)
        report = self.scan(timeout=0.1)
        self.assertEqual(report["summary"]["generated"], 1)
        self.assertEqual(report["summary"]["failed"], 2)
        self.assertFalse(self.marker.exists())

    def test_missing_man_is_a_reported_global_failure(self):
        self.command("good")
        with patch("bulk_scan.shutil.which", return_value=None):
            report = self.scan()
        self.assertTrue(report["errors"])
        self.assertEqual(report["records"][0]["reason"], "scan_error")
        self.assertFalse(self.log.exists())

    def test_interruption_checkpoints_results_and_marks_remaining_jobs(self):
        for name in ["aa", "bb", "cc"]:
            self.command(name)
        def progress(record):
            raise KeyboardInterrupt
        report = self.scan(progress=progress)
        self.assertTrue(report["interrupted"])
        self.assertEqual(report["summary"]["generated"], 1)
        self.assertEqual(report["summary"]["skipped"], 2)
        self.assertEqual(json.loads((self.output / "scan-report.json").read_text()), report)
        self.assertFalse((self.output / ".import.lock").exists())
        self.assertFalse((self.output / ".scan.lock").exists())
        resumed = self.scan()
        self.assertEqual(resumed["summary"]["generated"], 2)
        self.assertEqual(len(self.calls()), 3)

    def test_failed_driver_write_is_reported_and_partial_profile_is_preserved(self):
        from manual_import import atomic_json
        self.command("good")
        def writer(path, document, **kwargs):
            if path.parent.name == "drivers":
                raise PermissionError("fixture write denied")
            return atomic_json(path, document, **kwargs)
        with patch("manual_import.atomic_json", side_effect=writer):
            report = self.scan()
        self.assertEqual(report["records"][0]["reason"], "write_failed")
        self.assertEqual(len(list((self.output / "profiles").glob("*.json"))), 1)
        self.assertEqual(self.scan()["records"][0]["reason"], "existing_entry")
        self.assertEqual(self.scan(replace=True)["summary"]["generated"], 1)

    def test_invalid_destination_collection_is_preserved_without_rendering(self):
        self.command("good")
        folder = self.output / "drivers"
        folder.mkdir(parents=True)
        path = folder / "bad.json"
        path.write_text("invalid json")
        report = self.scan()
        self.assertTrue(report["errors"])
        self.assertEqual(path.read_text(), "invalid json")
        self.assertFalse(self.log.exists())

    def test_collection_lock_and_scan_lock_prevent_overlapping_writes(self):
        self.command("good")
        with ManualCollection(self.output):
            report = self.scan()
            self.assertTrue(report["errors"])
            self.assertTrue((self.output / ".import.lock").exists())
        lock = self.output / ".scan.lock"
        lock.touch()
        with self.assertRaises(HelpError):
            self.scan()
        self.assertTrue(lock.exists())
        self.assertFalse(self.log.exists())

    def test_declared_subcommands_use_only_fixed_manual_names_and_preserve_arity(self):
        self.command("newtool")
        _, driver = parse_driver({"command": "newtool", "global_values": ["--config"], "paths": [
            {"command": [], "man": "newtool"},
            {"command": ["run"], "help": ["help", "run"], "man": "different-page", "stop_at_positional": True},
            {"command": ["no-man"], "help": ["help", "no-man"]}]})
        report = self.scan(registry={"newtool": driver}, subcommands=True)
        self.assertEqual([call[-1] for call in self.calls()], ["newtool", "different-page"])
        registry = load_driver_registry(self.output / "drivers")
        self.assertIn("--config", registry["newtool"].global_values)
        self.assertTrue(registry["newtool"].paths[("run",)].stop_at_positional)
        self.assertEqual(registry["newtool"].paths[("run",)].arguments, ())
        self.assertEqual(report["summary"]["generated"], 2)
        self.assertFalse(self.marker.exists())

    def test_empty_inventory_and_invalid_limits_have_clear_results(self):
        report = self.scan()
        self.assertEqual(report["inventory_count"], 0)
        self.assertEqual(report["summary"]["generated"], 0)
        for kwargs in [{"limit": -1}, {"timeout": float("nan")}, {"timeout": 31}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(HelpError):
                self.scan(**kwargs)

    def test_cli_summary_report_and_exit_policies(self):
        self.command("good")
        self.command("missing")
        argv = [sys.executable, str(ROOT / "cli_help/main.py"), "--scan-installed", "--scan-path", str(self.bin),
                "--output-dir", str(self.output)]
        result = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["summary"]["needs_adjustment"], 1)
        self.assertTrue(Path(summary["report"]).is_file())
        result = subprocess.run(argv + ["--strict-scan"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        result = subprocess.run(argv + ["--limit", "-1"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
