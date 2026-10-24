"""Independent regressions for argument and collection review findings."""

import copy
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
from collection import inspect_collection, restore_review_backup
from core import HelpError, find_context, validate_profile
from manual_import import ManualCollection, atomic_json
from review import ReviewSession
from test_argument_syntax import PROFILE


SECRET = "REVIEW_PRIVATE_SENTINEL"


class SyntaxReviewTests(unittest.TestCase):
    def test_known_bundle_reports_missing_and_unsupported_value_forms(self):
        for style, token, code in (("attached_only", "-abn", "option_value_required"),
                                   ("separate", "-abn" + SECRET, "unsupported_value_form")):
            profile = copy.deepcopy(PROFILE)
            profile["categories"][0]["options"][2]["argument_style"] = style
            validate_profile(profile, Path("fixture"))
            line = "typed " + token + " --fl"
            with self.subTest(style=style):
                with self.assertRaises(HelpError) as raised:
                    find_context(line, len(line), [profile])
                self.assertEqual(raised.exception.code, code)
                self.assertNotIn(SECRET, str(raised.exception))


class CollectionReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cli-help-review-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "collection"
        self.profile = {"command": ["reviewfixture"], "description": "Fixture",
                        "categories": [{"name": "Options", "options": [{"flag": "--flag", "summary": "Flag"}]}]}
        with ManualCollection(self.root) as collection:
            self.paths = collection.save(self.profile, "reviewfixture")
        self.report = self.root / "scan-report.json"
        atomic_json(self.report, {"schema_version": 1, "finished": True, "records": [
            {"command": ["reviewfixture"], "status": "needs_adjustment", "generated": True}]})

    def backup(self):
        """Create an actual review manifest without invoking the documented target."""
        with patch.dict(os.environ, {"CLI_HELP_DRIVERS": ""}), ReviewSession(self.report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            document["profile"]["description"] = "Changed description"
            draft.text = json.dumps(document)
            session.save(draft)
        folder = next((self.root / ".review-backups").iterdir())
        return folder, json.loads((folder / "manifest.json").read_text())

    def contents(self):
        return {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def test_collection_directory_names_cannot_be_regular_files(self):
        (self.root / ".review-backups").mkdir()
        for name in ("profiles", "drivers", ".review-backups"):
            with self.subTest(name=name):
                original = self.root / name
                saved = self.root / (name + "-saved")
                original.rename(saved)
                original.write_text(SECRET)
                try:
                    report = inspect_collection(self.root)
                    self.assertEqual(report["status"], "invalid")
                    self.assertFalse(report["inspection_complete"])
                    self.assertIn("collection_layout_invalid", {item["code"] for item in report["findings"]})
                    self.assertNotIn(SECRET, json.dumps(report))
                finally:
                    original.unlink()
                    saved.rename(original)

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX symbolic-link race")
    def test_directory_swap_never_enumerates_external_names(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / (SECRET + ".json")).write_text("private")
        original = self.root / "profiles"
        original_is_dir = Path.is_dir
        swapped = False
        def swap(path):
            nonlocal swapped
            result = original_is_dir(path)
            if path == original and result and not swapped:
                swapped = True
                original.rename(self.root / "saved-profiles")
                original.symlink_to(outside, target_is_directory=True)
            return result
        with patch.object(Path, "is_dir", swap):
            report = inspect_collection(self.root)
        self.assertTrue(swapped)
        self.assertFalse(report["inspection_complete"])
        self.assertNotIn(SECRET, json.dumps(report))

    def test_json_directories_are_not_valid_metadata_or_reports(self):
        self.report.unlink()
        self.report.mkdir()
        report = inspect_collection(self.root)
        self.assertEqual(report["status"], "invalid")
        self.assertFalse(report["inspection_complete"])
        self.assertIn("unsafe_collection_file", {item["code"] for item in report["findings"]})

    def test_backup_driver_schema_failures_are_safe_rejections(self):
        folder, manifest = self.backup()
        item = next(item for item in manifest["files"] if item["path"].startswith("drivers/"))
        source = folder / item["backup"]
        for document in ([], None, SECRET, 3):
            with self.subTest(document=type(document).__name__):
                source.write_text(json.dumps(document))
                report = inspect_collection(self.root)
                before = self.contents()
                with self.assertRaises(HelpError) as raised:
                    restore_review_backup(self.root, folder.name, report["snapshot"])
                self.assertEqual(raised.exception.code, "invalid_backup")
                self.assertNotIn(SECRET, str(raised.exception))
                result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"),
                    "--recover-collection", str(self.root), "--restore-backup", folder.name,
                    "--expect-snapshot", report["snapshot"]], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["code"], "invalid_backup")
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotIn(SECRET, result.stdout + result.stderr)
                self.assertEqual(before, self.contents())

    def test_noncanonical_manifest_targets_are_rejected_before_writes(self):
        folder, manifest = self.backup()
        item = next(item for item in manifest["files"] if item["path"].startswith("profiles/"))
        original = item["path"]
        for target in (original.replace("profiles/", "profiles/./"), original.replace("profiles/", "profiles//")):
            with self.subTest(target=target):
                item["path"] = target
                atomic_json(folder / "manifest.json", manifest)
                report = inspect_collection(self.root)
                self.assertIn("backup_manifest_invalid", {item["code"] for item in report["findings"]})
                before = self.contents()
                with patch("collection.atomic_bytes", side_effect=AssertionError("Unexpected write")), self.assertRaises(HelpError) as raised:
                    restore_review_backup(self.root, folder.name, report["snapshot"])
                self.assertEqual(raised.exception.code, "invalid_backup")
                self.assertEqual(before, self.contents())

    def test_scan_boolean_fields_and_version_keep_their_declared_types(self):
        valid = json.loads(self.report.read_text())
        variants = [{**valid, "schema_version": True}, {**valid, "finished": SECRET},
                    {**valid, "interrupted": []},
                    {**valid, "records": [{**valid["records"][0], "generated": SECRET}]}]
        for document in variants:
            with self.subTest(document=document):
                atomic_json(self.report, document)
                report = inspect_collection(self.root)
                self.assertIn("scan_report_invalid", {item["code"] for item in report["findings"]})
                self.assertNotIn(SECRET, json.dumps(report))
