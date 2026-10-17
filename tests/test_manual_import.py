"""Verify manual imports, reusable drivers, and preservation of existing entries."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, MAN_TEXT, write_executable
from command_paths import load_driver_registry, help_route
from core import HelpError, find_context, insert_option, load_profiles
from manual_import import import_manual, read_manual


class ManualImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.source = self.folder / "manual.txt"
        self.source.write_text(MAN_TEXT)
        self.destination = self.folder / "collection"

    def tearDown(self):
        self.temp.cleanup()

    def test_text_import_creates_loadable_profile_and_manual_only_driver(self):
        with patch("manual_import.run_probe") as probe:
            result = import_manual(["newtool", "convert"], self.destination, text_file=self.source)
        probe.assert_not_called()
        registry = load_driver_registry(Path(result["driver_directory"]))
        self.assertEqual(help_route("newtool", ("convert",), registry).arguments, ())
        self.assertEqual(help_route("newtool", ("convert",), registry).manual, "newtool-convert")
        profiles = load_profiles(ROOT / "profiles", Path(result["profile_directory"]))
        line = "newtool convert --al"
        context = find_context(line, len(line), profiles, driver_registry=registry,
                               discover=lambda *args, **kwargs: self.fail("Imported static profile triggered discovery"))
        option = context.profile["categories"][0]["options"][0]
        self.assertEqual(insert_option(context, option)[0], "newtool convert --alpha ")

    def test_multiple_imports_merge_subcommand_routes(self):
        first = import_manual(["newtool", "convert"], self.destination, text_file=self.source)
        second = import_manual(["newtool", "inspect"], self.destination, text_file=self.source)
        self.assertEqual(first["driver"], second["driver"])
        self.assertNotEqual(first["profile"], second["profile"])
        driver = json.loads(Path(first["driver"]).read_text())
        self.assertEqual([route["command"] for route in driver["paths"]], [["convert"], ["inspect"]])
        load_driver_registry(self.destination / "drivers")
        load_profiles(ROOT / "profiles", self.destination / "profiles")

    def test_reimport_requires_replace_and_preserves_existing_files(self):
        first = import_manual(["newtool"], self.destination, text_file=self.source)
        before = {name: Path(first[name]).read_bytes() for name in ("profile", "driver")}
        self.source.write_text("OPTIONS\n  --changed   New option\n")
        with self.assertRaisesRegex(HelpError, "--replace"):
            import_manual(["newtool"], self.destination, text_file=self.source)
        for name, content in before.items():
            self.assertEqual(Path(first[name]).read_bytes(), content)
        result = import_manual(["newtool"], self.destination, text_file=self.source, replace=True)
        profile = json.loads(Path(result["profile"]).read_text())
        self.assertEqual(profile["categories"][0]["options"][0]["flag"], "--changed")

    def test_overlay_preserves_global_options_other_routes_and_positional_boundary(self):
        first = import_manual(["newtool", "convert"], self.destination, text_file=self.source)
        path = Path(first["driver"])
        driver = json.loads(path.read_text())
        driver["global_values"] = ["--config"]
        driver["paths"][0]["stop_at_positional"] = True
        driver["paths"].append({"command": ["inspect"], "help": ["help", "inspect"]})
        path.write_text(json.dumps(driver))
        import_manual(["newtool", "convert"], self.destination, text_file=self.source, replace=True)
        result = json.loads(path.read_text())
        self.assertEqual(result["global_values"], ["--config"])
        self.assertTrue(next(route for route in result["paths"] if route["command"] == ["convert"])["stop_at_positional"])
        self.assertEqual(next(route for route in result["paths"] if route["command"] == ["inspect"])["help"], ["help", "inspect"])

    def test_custom_filenames_are_reused_without_duplicate_profiles(self):
        first = import_manual(["newtool"], self.destination, text_file=self.source)
        renamed_profile = Path(first["profile"]).with_name("custom.json")
        renamed_driver = Path(first["driver"]).with_name("custom.json")
        Path(first["profile"]).rename(renamed_profile)
        Path(first["driver"]).rename(renamed_driver)
        result = import_manual(["newtool"], self.destination, text_file=self.source, replace=True)
        self.assertEqual(Path(result["profile"]), renamed_profile)
        self.assertEqual(Path(result["driver"]), renamed_driver)

    def test_invalid_or_empty_input_creates_no_configuration(self):
        for text in ["No option declarations", "", "Usage: example --run FILE"]:
            self.source.write_text(text)
            with self.subTest(text=text), self.assertRaises(HelpError):
                import_manual(["newtool"], self.destination, text_file=self.source)
            self.assertFalse(self.destination.exists())

    def test_oversized_and_missing_input_fail_without_output(self):
        self.source.write_bytes(b"x" * (512 * 1024 + 1))
        with self.assertRaises(HelpError):
            import_manual(["newtool"], self.destination, text_file=self.source)
        with self.assertRaises(OSError):
            import_manual(["newtool"], self.destination, text_file=self.folder / "missing")
        self.assertFalse(self.destination.exists())

    def test_invalid_command_and_manual_names_never_probe(self):
        with patch("manual_import.run_probe") as probe:
            for command, manual in [(["../tool"], None), (["tool", "--flag"], None), (["tool"], "-a"),
                                    (["tool"], "$(bad)"), ([], None)]:
                with self.subTest(command=command, manual=manual), self.assertRaises(HelpError):
                    import_manual(command, self.destination, manual=manual)
        probe.assert_not_called()

    def test_exclusive_lock_prevents_lost_updates(self):
        self.destination.mkdir()
        lock = self.destination / ".import.lock"
        lock.write_text("active")
        with self.assertRaisesRegex(HelpError, "import is active"):
            import_manual(["newtool"], self.destination, text_file=self.source)
        self.assertEqual(lock.read_text(), "active")
        self.assertFalse((self.destination / "drivers").exists())

    def test_rendered_page_uses_only_man_and_fixed_arguments(self):
        binaries = self.folder / "bin"
        binaries.mkdir()
        log = self.folder / "man-calls"
        marker = self.folder / "target-executed"
        write_executable(binaries / "man", "import json, pathlib, sys\n"
                         f"pathlib.Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]))\nprint({MAN_TEXT!r})\n")
        write_executable(binaries / "newtool", f"import pathlib\npathlib.Path({str(marker)!r}).touch()\n")
        with patch.dict(os.environ, {"PATH": str(binaries)}):
            import_manual(["newtool", "convert"], self.destination, manual="custom-page")
        self.assertEqual(json.loads(log.read_text())[-4:], ["-s", "1:8", "--", "custom-page"])
        self.assertFalse(marker.exists())

    def test_local_roff_path_is_passed_literally_to_man(self):
        source = self.folder / "manual with spaces.1"
        source.write_text(".TH SAMPLE 1\n")
        with patch("manual_import.shutil.which", return_value="/fake/man"), patch("manual_import.run_probe", return_value=MAN_TEXT) as probe:
            read_manual(["newtool"], man_file=source)
        self.assertEqual(probe.call_args.args[0][-3:], ["-l", "--", str(source.resolve())])

    def test_unavailable_renderer_allows_text_but_not_raw_manual(self):
        with patch("manual_import.shutil.which", return_value=None):
            read_manual(["newtool"], text_file=self.source)
            with self.assertRaises(HelpError):
                read_manual(["newtool"], man_file=self.source)

    def test_corrupt_existing_driver_is_preserved(self):
        directory = self.destination / "drivers"
        directory.mkdir(parents=True)
        path = directory / "newtool.json"
        path.write_text("invalid json")
        with self.assertRaises(ValueError):
            import_manual(["newtool"], self.destination, text_file=self.source)
        self.assertEqual(path.read_text(), "invalid json")
        self.assertFalse((self.destination / ".import.lock").exists())
        self.assertFalse((self.destination / "profiles").exists())

    def test_cli_import_reports_paths_and_requires_destination(self):
        result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), "--import-man", "newtool", "convert",
                                 "--man-text", str(self.source), "--output-dir", str(self.destination)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(Path(json.loads(result.stdout)["profile"]).is_file())
        result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), "--import-man", "newtool"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--output-dir", result.stderr)


if __name__ == "__main__":
    unittest.main()
