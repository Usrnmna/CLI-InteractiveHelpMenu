"""Verify draft editing, recovery evidence, and real terminal preview isolation."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, MAN_TEXT, write_executable
from test_bash_pty import BashSession
from command_paths import load_driver_registry
from core import HelpError, load_profiles, find_context, insert_option
from manual_import import import_manual, atomic_json
from review import ReviewSession, edit_draft, add_option, show


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.output = self.folder / "collection"
        self.source = self.folder / "manual.txt"
        self.source.write_text(MAN_TEXT)
        self.result = import_manual(["newtool", "run"], self.output, text_file=self.source)
        self.report = self.output / "scan-report.json"
        self.original_report = {"schema_version": 1, "summary": {"needs_adjustment": 1},
            "output_directory": "/untrusted/path", "records": [
                {"command": ["newtool", "run"], "status": "needs_adjustment", "generated": True,
                 "manual": "newtool-run", "profile": "/untrusted/profile.json", "issues": [{"code": "root_only"}]},
                {"command": ["missing"], "status": "failed", "generated": False},
                {"command": ["clean"], "status": "success", "generated": False}]}
        atomic_json(self.report, self.original_report)
        self.environment = patch.dict(os.environ)
        self.environment.start()
        os.environ.pop("CLI_HELP_DRIVERS", None)
        os.environ.pop("CLI_HELP_CONFIG", None)

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def changed(self, session, index=0):
        draft = session.open_draft(index)
        document = draft.document()
        document["profile"]["categories"] = [{"name": "Corrected", "options": [
            {"flag": "--corrected", "summary": "Corrected flag", "argument": "VALUE", "argument_optional": True}]}]
        document["driver"]["global_values"] = ["--config"]
        draft.text = json.dumps(document)
        return draft

    def test_save_retains_scan_evidence_and_creates_loadable_corrected_pair_and_backups(self):
        before = Path(self.result["profile"]).read_bytes()
        with ReviewSession(self.report) as session, patch("subprocess.run") as process:
            draft = self.changed(session)
            result = session.save(draft)
            self.assertEqual(session.entries(), [1])
            self.assertEqual(session.entries(True, "newtool"), [0])
            process.assert_not_called()
        saved = json.loads(self.report.read_text())
        self.assertEqual(saved["summary"], self.original_report["summary"])
        self.assertEqual(saved["records"][0]["status"], "needs_adjustment")
        self.assertEqual(saved["records"][0]["issues"], [{"code": "root_only"}])
        review = saved["records"][0]["review"]
        self.assertEqual(review["status"], "resolved")
        self.assertEqual((Path(review["backup"]) / "0.json").read_bytes(), before)
        profiles = load_profiles(self.output / "profiles")
        drivers = load_driver_registry(self.output / "drivers")
        self.assertIn("--config", drivers["newtool"].global_values)
        line = "newtool --config private run --co"
        context = find_context(line, len(line), profiles, driver_registry=drivers,
                               discover=lambda *a, **k: self.fail("Unexpected help probe"))
        self.assertEqual(insert_option(context, profiles[0]["categories"][0]["options"][0])[0],
                         "newtool --config private run --corrected ")
        self.assertEqual(result["option_count"], 1)

    def test_cancelled_draft_changes_nothing_and_releases_locks(self):
        before = self.report.read_bytes(), Path(self.result["profile"]).read_bytes()
        with ReviewSession(self.report) as session:
            self.changed(session)
        self.assertEqual(before, (self.report.read_bytes(), Path(self.result["profile"]).read_bytes()))
        self.assertFalse((self.output / ".review-backups").exists())
        self.assertFalse((self.output / ".scan.lock").exists())
        self.assertFalse((self.output / ".import.lock").exists())

    def test_missing_profile_can_be_constructed_with_guided_option_entry(self):
        with ReviewSession(self.report) as session:
            draft = session.open_draft(1)
            with self.assertRaises(ValueError):
                session.save(draft)
            with patch("builtins.input", side_effect=["Output", "--output", "FILE", "n", "Select output"]):
                add_option(draft)
            result = session.save(draft)
        profile = json.loads(Path(result["profile"]).read_text())
        self.assertEqual(profile["categories"][0]["options"][0]["argument"], "FILE")
        self.assertFalse(profile["categories"][0]["options"][0]["argument_optional"])

    def test_manual_import_changes_draft_only_and_uses_manual_only_route(self):
        with ReviewSession(self.report) as session, patch("manual_import.run_probe") as probe:
            draft = session.open_draft(1)
            session.import_source(draft, "text", str(self.source), "correct-manual")
            self.assertEqual(draft.document()["driver"]["paths"][0]["man"], "correct-manual")
            self.assertEqual(draft.document()["driver"]["paths"][0]["help"], [])
            self.assertEqual(len(session.collection.profiles), 1)
            probe.assert_not_called()
            session.save(draft)

    def test_installed_manual_import_passes_only_fixed_manual_arguments(self):
        with ReviewSession(self.report) as session, patch("manual_import.shutil.which", return_value="/usr/bin/man"), patch(
                "manual_import.run_probe", return_value=MAN_TEXT) as probe:
            draft = session.open_draft(1)
            session.import_source(draft, "page", "different-page", None)
            self.assertEqual(probe.call_args.args[0][-4:], ["-s", "1:8", "--", "different-page"])
            self.assertTrue(probe.call_args.kwargs["check"])

    def test_invalid_flags_identity_driver_routes_and_malformed_shapes_reject_save(self):
        with ReviewSession(self.report) as session:
            for kind in ["flag", "profile_name", "driver_name", "route", "empty", "malformed", "shape"]:
                with self.subTest(kind=kind):
                    draft = self.changed(session)
                    document = draft.document()
                    if kind == "flag":
                        document["profile"]["categories"][0]["options"][0]["flag"] = "--x;touch marker"
                    elif kind == "profile_name":
                        document["profile"]["command"] = ["other"]
                    elif kind == "driver_name":
                        document["driver"]["command"] = "other"
                    elif kind == "route":
                        document["driver"]["paths"][0]["help"] = ["run", "payload"]
                    elif kind == "empty":
                        document["profile"]["categories"] = []
                    elif kind == "shape":
                        document["profile"] = []
                    draft.text = "{" if kind == "malformed" else json.dumps(document)
                    with self.assertRaises(ValueError):
                        session.save(draft)
            self.assertFalse((self.output / ".review-backups").exists())
            self.assertNotIn("review", session.report["records"][0])

    def test_saved_review_becomes_stale_after_profile_or_shared_driver_change(self):
        with ReviewSession(self.report) as session:
            session.save(self.changed(session))
        path = Path(self.result["profile"])
        path.write_text(path.read_text() + " ")
        with ReviewSession(self.report) as session:
            self.assertEqual(session.review_state(session.report["records"][0]), "stale")
            self.assertIn(0, session.entries())

    def test_external_changes_to_selected_files_or_report_prevent_overwrite(self):
        for key in ["profile", "driver", "report"]:
            with self.subTest(key=key), ReviewSession(self.report) as session:
                draft = self.changed(session)
                path = self.report if key == "report" else Path(self.result[key])
                path.write_text(path.read_text() + " ")
                before = path.read_bytes()
                with self.assertRaisesRegex(HelpError, "changed outside"):
                    session.save(draft)
                self.assertEqual(path.read_bytes(), before)

    def test_partial_pair_or_report_write_failure_never_marks_resolved(self):
        for failure in ["driver", "report"]:
            with self.subTest(failure=failure), ReviewSession(self.report) as session:
                draft = self.changed(session)
                def writer(path, document, **kwargs):
                    if (failure == "driver" and path.parent.name == "drivers") or (failure == "report" and path == self.report):
                        raise PermissionError("Fixture write denied")
                    return atomic_json(path, document, **kwargs)
                with patch("manual_import.atomic_json", side_effect=writer), patch("review.atomic_json", side_effect=writer):
                    with self.assertRaisesRegex(HelpError, "Save incomplete"):
                        session.save(draft)
                self.assertNotIn("review", json.loads(self.report.read_text())["records"][0])
                self.assertTrue(list((self.output / ".review-backups").glob("*/manifest.json")))
                with self.assertRaisesRegex(HelpError, "Reopen"):
                    session.save(draft)

    def test_other_routes_and_custom_filenames_are_preserved(self):
        import_manual(["newtool", "inspect"], self.output, text_file=self.source)
        original = Path(self.result["profile"])
        custom = original.with_name("custom.json")
        original.rename(custom)
        with ReviewSession(self.report) as session:
            result = session.save(self.changed(session))
        self.assertEqual(Path(result["profile"]), custom)
        driver = json.loads(Path(result["driver"]).read_text())
        self.assertEqual([route["command"] for route in driver["paths"]], [["run"], ["inspect"]])

    def test_new_external_profile_prevents_a_duplicate_command_save(self):
        with ReviewSession(self.report) as session:
            draft = self.changed(session)
            duplicate = self.output / "profiles" / "external.json"
            duplicate.write_bytes(Path(self.result["profile"]).read_bytes())
            with self.assertRaisesRegex(HelpError, "changed outside"):
                session.save(draft)
            self.assertFalse((self.output / ".review-backups").exists())

    def test_missing_docker_route_preserves_boundary_and_rejects_global_arity_conflict(self):
        self.original_report["records"][1]["command"] = ["docker", "run"]
        atomic_json(self.report, self.original_report)
        with ReviewSession(self.report) as session:
            draft = self.changed(session, 1)
            document = draft.document()
            self.assertTrue(document["driver"]["paths"][0]["stop_at_positional"])
            document["driver"]["global_values"] = []
            document["driver"]["global_flags"] = ["--host"]
            draft.text = json.dumps(document)
            with self.assertRaisesRegex(HelpError, "arity"):
                session.save(draft)

    def test_deeply_nested_editor_json_is_a_recoverable_validation_error(self):
        with ReviewSession(self.report) as session:
            draft = session.open_draft(0)
            draft.text = "[" * 2000 + "]" * 2000
            with self.assertRaises(HelpError):
                session.validate(draft)

    def test_locks_reject_overlapping_scan_import_and_review(self):
        with ReviewSession(self.report):
            with self.assertRaises(HelpError):
                with ReviewSession(self.report):
                    pass
            with self.assertRaises(HelpError):
                import_manual(["newtool"], self.output, text_file=self.source)
        self.assertFalse((self.output / ".scan.lock").exists())

    def test_malformed_report_and_symlink_escape_release_locks(self):
        atomic_json(self.report, {"schema_version": 2})
        with self.assertRaises(HelpError):
            with ReviewSession(self.report):
                pass
        self.assertFalse((self.output / ".scan.lock").exists())
        atomic_json(self.report, self.original_report)
        outside = self.folder / "outside.json"
        outside.write_text(Path(self.result["profile"]).read_text())
        Path(self.result["profile"]).unlink()
        Path(self.result["profile"]).symlink_to(outside)
        with self.assertRaisesRegex(HelpError, "escapes"):
            with ReviewSession(self.report):
                pass
        self.assertFalse((self.output / ".scan.lock").exists())

    def test_unsupported_names_are_visible_but_not_saved(self):
        report = self.original_report
        report["records"][1]["command"] = ["bad name"]
        atomic_json(self.report, report)
        with ReviewSession(self.report) as session:
            self.assertIn(1, session.entries())
            with self.assertRaisesRegex(HelpError, "schema"):
                session.open_draft(1)

    def test_editor_receives_literal_filename_and_preserves_invalid_text(self):
        editor = self.folder / "editor with spaces"
        write_executable(editor, "import pathlib, sys\npathlib.Path(sys.argv[-1]).write_text('{ invalid')\n")
        with ReviewSession(self.report) as session, patch.dict(os.environ, {"VISUAL": shlex.quote(str(editor))}):
            draft = session.open_draft(0)
            edit_draft(draft)
            self.assertEqual(draft.text, "{ invalid")
            with self.assertRaises(ValueError):
                session.save(draft)
        self.assertNotIn("review", json.loads(self.report.read_text())["records"][0])

    def test_diagnostics_escape_terminal_control_sequences(self):
        with patch("builtins.print") as output:
            show({"error": "\x1b]52;payload\x07"})
        rendered = output.call_args.args[0]
        self.assertNotIn("\x1b", rendered)
        self.assertIn("\\u001b", rendered)

    def test_cli_requires_terminal_and_rejects_unrelated_flags(self):
        command = [sys.executable, str(ROOT / "cli_help/main.py"), "--review-report", str(self.report)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("interactive terminal", result.stderr)
        result = subprocess.run(command + ["--replace"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_real_terminal_edit_preview_save_and_cancel_never_run_target(self):
        editor = self.folder / "editor"
        write_executable(editor, "import json, pathlib, sys\np = pathlib.Path(sys.argv[-1])\nd = json.loads(p.read_text())\n"
                         "d['profile']['categories'][0]['options'][0]['flag'] = '--reviewed'\n"
                         "d['driver']['global_flags'] = ['--quiet']\np.write_text(json.dumps(d))\n")
        marker = self.folder / "target-executed"
        write_executable(self.folder / "newtool", f"import pathlib\npathlib.Path({str(marker)!r}).touch()\n")
        shell = BashSession(self.folder, extra_environment={"EDITOR": str(editor), "VISUAL": "",
                            "PATH": str(self.folder) + os.pathsep + os.environ["PATH"]})
        try:
            shell.send(shlex.quote(sys.executable) + " " + shlex.quote(str(ROOT / "cli_help/main.py")) +
                       " --review-report " + shlex.quote(str(self.report)) + "\n")
            shell.expect(b"Review: number")
            shell.send("f\n")
            shell.expect(b"Command contains")
            shell.send("newtool\n")
            shell.expect(b"Review: number")
            shell.send("1\n")
            shell.expect(b"Entry:")
            shell.send("e\n")
            shell.expect(b"Entry:")
            shell.send("p\n")
            shell.expect(b"Help preview")
            shell.send("\n")
            shell.expect(b"Preview selection only: --reviewed")
            shell.expect(b"Entry:")
            shell.send("p\n")
            shell.expect(b"Help preview")
            shell.send(b"\x1b")
            shell.expect(b"Entry:")
            shell.send("s\n")
            shell.expect(b"mark reviewed?")
            shell.send("y\n")
            shell.expect(b"Saved and marked reviewed")
            shell.expect(b"Entry:")
            shell.send("b\n")
            shell.expect(b"Review: number")
            shell.send("f\n")
            shell.expect(b"Command contains")
            shell.send("\n")
            shell.expect(b"Review: number")
            shell.send("2\n")
            shell.expect(b"Entry:")
            shell.send("a\n")
            shell.expect(b"Category")
            shell.send("Output\n")
            shell.expect(b"Literal option flag")
            shell.send("--output\n")
            shell.expect(b"Argument placeholder")
            shell.send("\n")
            shell.expect(b"Summary:")
            shell.send("Unsaved option\n")
            shell.expect(b"Entry:")
            shell.send("b\n")
            shell.expect(b"Discard unsaved draft")
            shell.send("y\n")
            shell.expect(b"Review: number")
            shell.send("q\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
        finally:
            shell.close()
        self.assertFalse(marker.exists())
        self.assertEqual(len(list((self.output / "profiles").glob("*.json"))), 1)
        self.assertEqual(json.loads(self.report.read_text())["records"][0]["review"]["status"], "resolved")
        self.assertIn("--quiet", load_driver_registry(self.output / "drivers")["newtool"].global_flags)


if __name__ == "__main__":
    unittest.main()
