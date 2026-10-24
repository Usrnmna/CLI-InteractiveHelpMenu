"""Read-only consistency and guarded, byte-preserving review-backup recovery."""

import copy
import hashlib
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
from collection import inspect_collection, restore_review_backup, RecoveryIncomplete
from core import HelpError
from manual_import import ManualCollection, atomic_json, atomic_bytes
from review import ReviewSession
from review_forms import edit_options
from test_argument_syntax import PROFILE


SECRET = "PRIVATE_COLLECTION_SENTINEL"


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "collection"
        self.profile = copy.deepcopy(PROFILE)
        self.profile["imported_from"] = {"manual": "typed", "source": "Fixture"}
        with ManualCollection(self.root) as collection:
            self.paths = collection.save(self.profile, "typed")
        self.report = self.root / "scan-report.json"
        atomic_json(self.report, {"schema_version": 1, "finished": True, "records": [
            {"command": ["typed"], "status": "needs_adjustment", "generated": True}]})

    def backup(self):
        """Generate a real review backup through the existing save workflow."""
        original = Path(self.paths["profile"]).read_bytes()
        previous = set((self.root / ".review-backups").iterdir()) if (self.root / ".review-backups").exists() else set()
        with patch.dict(os.environ, {"CLI_HELP_DRIVERS": ""}), ReviewSession(self.report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            document["profile"]["description"] = "Changed café description"
            draft.text = json.dumps(document, ensure_ascii=False)
            session.save(draft)
        name = next(iter(set((self.root / ".review-backups").iterdir()) - previous)).name
        return name, original

    def codes(self):
        return {item["code"] for item in inspect_collection(self.root)["findings"]}

    def test_complete_collection_is_read_only_and_snapshot_is_stable(self):
        original_open = os.open
        def read_only(path, flags, *arguments, **keywords):
            self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            return original_open(path, flags, *arguments, **keywords)
        with patch("subprocess.Popen", side_effect=AssertionError("Target started")), \
             patch("os.mkdir", side_effect=AssertionError("Write")), patch("os.replace", side_effect=AssertionError("Write")), \
             patch("os.open", side_effect=read_only):
            first = inspect_collection(self.root)
            second = inspect_collection(self.root)
        self.assertEqual(first["status"], "ok")
        self.assertEqual(first["snapshot"], second["snapshot"])
        self.assertEqual(first["files"], second["files"])
        self.assertNotIn("categories", json.dumps(first))

    def test_missing_pairs_duplicates_invalid_json_and_stale_evidence(self):
        extra = self.root / "profiles/duplicate.json"
        extra.write_bytes(Path(self.paths["profile"]).read_bytes())
        self.assertIn("duplicate_profile", self.codes())
        extra.unlink()
        Path(self.paths["driver"]).unlink()
        self.assertTrue({"profile_route_missing", "scan_pair_missing"} <= self.codes())
        Path(self.paths["profile"]).write_text('{"private":"' + SECRET)
        report = inspect_collection(self.root)
        self.assertIn("collection_json_invalid", {item["code"] for item in report["findings"]})
        self.assertNotIn(SECRET, json.dumps(report))

    def test_review_hashes_and_interrupted_scan_are_distinguished(self):
        self.backup()
        Path(self.paths["profile"]).write_text(json.dumps(self.profile))
        self.assertIn("review_evidence_stale", self.codes())
        report = json.loads(self.report.read_text())
        report.update(finished=False, interrupted=True)
        atomic_json(self.report, report)
        self.assertIn("scan_incomplete", self.codes())

    def test_lock_presence_is_uncertain_and_blocks_recovery(self):
        name, _ = self.backup()
        (self.root / ".import.lock").write_text(SECRET)
        report = inspect_collection(self.root)
        self.assertIn("lock_ownership_uncertain", {item["code"] for item in report["findings"]})
        self.assertNotIn(SECRET, json.dumps(report))
        with self.assertRaises(HelpError) as raised:
            restore_review_backup(self.root, name, report["snapshot"])
        self.assertEqual(raised.exception.code, "collection_locked")
        self.assertEqual((self.root / ".import.lock").read_text(), SECRET)

    def test_backup_restoration_is_explicit_byte_preserving_and_repeatable(self):
        name, original = self.backup()
        Path(self.paths["profile"]).write_text(SECRET)
        before = inspect_collection(self.root)
        result = restore_review_backup(self.root, name, before["snapshot"])
        self.assertEqual(result["status"], "restored")
        self.assertEqual(Path(self.paths["profile"]).read_bytes(), original)
        retained = Path(result["backup"])
        self.assertTrue(retained.is_dir())
        if sys.platform.startswith("linux"):
            self.assertEqual(retained.stat().st_mode & 0o777, 0o700)
        self.assertTrue(any(path.read_bytes() == SECRET.encode() for path in retained.glob("*.json")))
        after = inspect_collection(self.root)
        self.assertFalse(any(item["severity"] == "error" for item in after["findings"]))
        repeated = restore_review_backup(self.root, name, after["snapshot"])
        self.assertEqual(repeated["status"], "unchanged")
        self.assertEqual(inspect_collection(self.root)["snapshot"], after["snapshot"])

    def test_stale_snapshot_and_changed_sources_refuse_writes(self):
        name, _ = self.backup()
        before = inspect_collection(self.root)
        Path(self.paths["profile"]).write_text(SECRET)
        with self.assertRaises(HelpError) as raised:
            restore_review_backup(self.root, name, before["snapshot"])
        self.assertEqual(raised.exception.code, "collection_changed")
        self.assertEqual(Path(self.paths["profile"]).read_text(), SECRET)
        self.assertFalse((self.root / ".import.lock").exists())

    def test_failure_retains_backup_and_releases_only_owned_locks(self):
        name, _ = self.backup()
        before = inspect_collection(self.root)
        calls = 0
        def fail_second(path, data, **kwargs):
            nonlocal calls
            if path.parent.name in ("profiles", "drivers") or path.name == "scan-report.json":
                calls += 1
            if calls == 2:
                raise OSError(SECRET)
            return atomic_bytes(path, data, **kwargs)
        with patch("collection.atomic_bytes", side_effect=fail_second), self.assertRaises(RecoveryIncomplete) as raised:
            restore_review_backup(self.root, name, before["snapshot"])
        self.assertTrue(raised.exception.backup.is_dir())
        self.assertNotIn(SECRET, str(raised.exception))
        self.assertFalse((self.root / ".scan.lock").exists())
        self.assertFalse((self.root / ".import.lock").exists())

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX special-file checks")
    def test_symlink_escapes_and_fifo_entries_are_not_followed_or_blocking(self):
        target = Path(self.temporary.name) / "outside.json"
        target.write_text(SECRET)
        (self.root / "profiles/escape.json").symlink_to(target)
        os.mkfifo(self.root / "drivers/pipe.json")
        report = inspect_collection(self.root)
        self.assertFalse(report["inspection_complete"])
        self.assertTrue({"unsafe_collection_path", "unsafe_collection_file"} <= {item["code"] for item in report["findings"]})
        self.assertNotIn(SECRET, json.dumps(report))
        self.assertEqual(target.read_text(), SECRET)

    def test_unsafe_backup_manifest_cannot_write_outside_collection(self):
        name, _ = self.backup()
        manifest = self.root / ".review-backups" / name / "manifest.json"
        manifest.write_text(json.dumps({"files": [{"path": "../" + SECRET, "backup": "0.json"}]}))
        report = inspect_collection(self.root)
        self.assertIn("backup_manifest_invalid", {item["code"] for item in report["findings"]})
        with self.assertRaises(HelpError) as raised:
            restore_review_backup(self.root, name, report["snapshot"])
        self.assertNotIn(SECRET, str(raised.exception))
        self.assertFalse((Path(self.temporary.name) / SECRET).exists())

    def test_guided_review_preserves_and_explicitly_clears_value_form_metadata(self):
        with patch.dict(os.environ, {"CLI_HELP_DRIVERS": ""}), ReviewSession(self.report) as session:
            draft = session.open_draft(0)
            with patch("builtins.input", side_effect=["e", "4", "", "Revised output", "", "", "n"]), patch("builtins.print"):
                edit_options(draft)
            session.save(draft)
            saved = json.loads(Path(self.paths["profile"]).read_text())
            option = saved["categories"][0]["options"][3]
            self.assertEqual(option["argument_style"], "attached_only")
            self.assertEqual(saved["categories"][0]["options"][0]["bundle"], True)
        with patch.dict(os.environ, {"CLI_HELP_DRIVERS": ""}), ReviewSession(self.report) as session:
            draft = session.open_draft(0)
            with patch("builtins.input", side_effect=["e", "4", "", "", "", "/clear"]), patch("builtins.print"):
                edit_options(draft)
            session.save(draft)
        option = json.loads(Path(self.paths["profile"]).read_text())["categories"][0]["options"][3]
        self.assertNotIn("argument_style", option)
        self.assertNotIn("argument", option)

    def test_staging_rechecks_target_sources_and_lock_ownership(self):
        for changed in ("target", "source", "lock", "other_metadata"):
            with self.subTest(changed=changed):
                name, _ = self.backup()
                before = inspect_collection(self.root)
                original_atomic = atomic_bytes
                injected = False
                def change_before_replace(path, data, **kwargs):
                    nonlocal injected
                    if kwargs.get("before_replace") and not injected:
                        injected = True
                        selected = (self.root / "profiles/new.json" if changed == "other_metadata" else
                                    Path(self.paths["profile"]) if changed == "target" else
                                    self.root / ".review-backups" / name / "0.json" if changed == "source" else
                                    self.root / ".scan.lock")
                        selected.write_text(SECRET)
                    return original_atomic(path, data, **kwargs)
                with patch("collection.atomic_bytes", side_effect=change_before_replace), self.assertRaises(RecoveryIncomplete) as raised:
                    restore_review_backup(self.root, name, before["snapshot"])
                self.assertTrue(raised.exception.backup.exists())
                self.assertNotIn(SECRET, str(raised.exception))
                if changed == "target":
                    self.assertEqual(Path(self.paths["profile"]).read_text(), SECRET)
                if changed == "lock":
                    self.assertEqual((self.root / ".scan.lock").read_text(), SECRET)
                    (self.root / ".scan.lock").unlink()
                if changed == "other_metadata":
                    self.assertEqual((self.root / "profiles/new.json").read_text(), SECRET)
                # Restore the fixture for the next independent injected race.
                Path(self.paths["profile"]).write_text(json.dumps(self.profile))

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX pinned-directory checks")
    def test_parent_symlink_swap_cannot_redirect_a_recovery_write(self):
        name, _ = self.backup()
        before = inspect_collection(self.root)
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        external = outside / Path(self.paths["profile"]).name
        external.write_text(SECRET)
        swapped = False
        def swap_parent(path, data, **kwargs):
            nonlocal swapped
            if kwargs.get("before_replace") and not swapped:
                swapped = True
                (self.root / "profiles").rename(self.root / "saved-profiles")
                (self.root / "profiles").symlink_to(outside, target_is_directory=True)
            return atomic_bytes(path, data, **kwargs)
        with patch("collection.atomic_bytes", side_effect=swap_parent), self.assertRaises(RecoveryIncomplete):
            restore_review_backup(self.root, name, before["snapshot"])
        self.assertEqual(external.read_text(), SECRET)
        self.assertFalse(any(outside.glob(".cli-help-write-*")))

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX pinned-root checks")
    def test_root_swap_cannot_create_or_remove_external_locks(self):
        name, _ = self.backup()
        before = inspect_collection(self.root)
        outside = Path(self.temporary.name) / "external-collection"
        outside.mkdir()
        original = self.root.with_name("saved-collection")
        original_open = os.open
        swapped = False
        def swap_root(path, flags, *arguments, **keywords):
            nonlocal swapped
            if path == ".scan.lock" and flags & os.O_CREAT and not swapped:
                swapped = True
                self.root.rename(original)
                self.root.symlink_to(outside, target_is_directory=True)
            return original_open(path, flags, *arguments, **keywords)
        with patch("os.open", side_effect=swap_root), self.assertRaises(HelpError):
            restore_review_backup(self.root, name, before["snapshot"])
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((original / ".scan.lock").exists())
        self.assertFalse((original / ".import.lock").exists())

    def test_invalid_backup_schema_never_echoes_configuration_values(self):
        name, _ = self.backup()
        source = self.root / ".review-backups" / name / "0.json"
        profile = copy.deepcopy(self.profile)
        option = {"flag": "--" + SECRET, "summary": "Private"}
        profile["categories"][0]["options"] = [option, option]
        source.write_text(json.dumps(profile))
        before = inspect_collection(self.root)
        with self.assertRaises(HelpError) as raised:
            restore_review_backup(self.root, name, before["snapshot"])
        self.assertEqual(raised.exception.code, "invalid_backup")
        self.assertNotIn(SECRET, str(raised.exception))
        result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--recover-collection", str(self.root),
                                 "--restore-backup", name, "--expect-snapshot", before["snapshot"]],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_inspection_limits_and_incomplete_backup_do_not_trigger_repair(self):
        name, _ = self.backup()
        backup = self.root / ".review-backups" / name
        (backup / "0.json").unlink()
        self.assertIn("backup_manifest_invalid", self.codes())
        (self.root / "profiles/.cli-help-write-interrupted.tmp").write_text(SECRET)
        self.assertIn("temporary_write_present", self.codes())
        with patch("collection.MAX_ENTRIES", 2), patch("subprocess.Popen", side_effect=AssertionError("Target started")):
            report = inspect_collection(self.root)
        self.assertFalse(report["inspection_complete"])
        self.assertIn("collection_limit", {item["code"] for item in report["findings"]})
        self.assertNotIn(SECRET, json.dumps(report))

    def test_invalid_canonical_report_and_noncanonical_notes_are_distinct(self):
        notes = self.root / "notes.txt"
        notes.write_text(SECRET)
        for document in ({}, [], {"schema_version": 1, "records": "invalid"}):
            atomic_json(self.report, document)
            self.assertIn("scan_report_invalid", self.codes())
        self.assertEqual(notes.read_text(), SECRET)

    def test_cli_inspection_emits_safe_json_and_requires_explicit_recovery_choices(self):
        Path(self.paths["profile"]).write_text(SECRET)
        result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--check-collection", str(self.root)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--recover-collection", str(self.root)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
