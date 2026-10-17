"""Verify conflict choices, stale input rejection, backups, and terminal review."""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_update
from test_bash_pty import BashSession
from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import installation
import update_review as review


class UpdateReviewTests(unittest.TestCase):
    run_script = test_update.UpdateTests.run_script
    upgrade = test_update.UpdateTests.upgrade
    manifest = test_update.UpdateTests.manifest
    backups = test_update.UpdateTests.backups

    def setUp(self):
        test_update.UpdateTests.setUp(self)
        self.name = "cli_help/core.py"
        self.local = (self.prefix / self.name).read_bytes() + b"\n# local customization\n"
        (self.prefix / self.name).write_bytes(self.local)
        self.new_report()

    def new_report(self):
        existing = set(self.backups())
        self.upgrade(status=2)
        self.report = (set(self.backups()) - existing).pop() / "report.json"

    def session(self):
        return review.ReviewSession(self.report)

    def review_backups(self):
        return list(self.prefix.parent.glob(self.prefix.name + ".update-review-backup-*"))

    def test_incoming_choice_backs_up_local_and_adopts_ownership(self):
        session = self.session()
        original = installation.tree_state(self.prefix)
        report = self.report.read_bytes()
        startup = self.rc.read_bytes()
        session.choose(self.name, "incoming")
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)
        backup = session.save()
        self.assertEqual(installation.tree_state(backup / "previous"), original)
        self.assertEqual(self.report.read_bytes(), report)
        self.assertEqual(self.rc.read_bytes(), startup)
        incoming = (self.source / self.name).read_bytes()
        self.assertEqual((self.prefix / self.name).read_bytes(), incoming)
        self.assertEqual(self.manifest()["files"][self.name], installation.digest(incoming))
        self.assertEqual(self.session().status(self.name), "saved incoming")
        self.run_script(self.prefix / "uninstall.sh")
        self.assertFalse(self.prefix.exists())

    def test_keep_local_remains_protected_from_update_and_uninstall(self):
        session = self.session()
        before = self.manifest()
        session.choose(self.name, "local")
        session.save()
        self.assertEqual(self.manifest(), before)
        self.assertEqual(self.session().status(self.name), "saved local")
        self.upgrade(status=2)
        self.run_script(self.prefix / "uninstall.sh")
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)

    def test_edited_merge_remains_custom_and_cannot_execute_itself(self):
        marker = self.home / "executed"
        merged = f"from pathlib import Path\nPath({str(marker)!r}).touch()\n".encode()
        session = self.session()
        session.choose(self.name, "edit", merged)
        session.save()
        self.assertFalse(marker.exists())
        self.assertEqual((self.prefix / self.name).read_bytes(), merged)
        self.assertNotEqual(self.manifest()["files"][self.name], installation.digest(merged))
        self.run_script(self.prefix / "uninstall.sh")
        self.assertTrue((self.prefix / self.name).exists())

    def test_exact_incoming_edit_is_adopted(self):
        session = self.session()
        incoming = session.content(self.name, incoming=True)
        session.choose(self.name, "edit", incoming)
        session.save()
        self.assertEqual(self.manifest()["files"][self.name], installation.digest(incoming))

    def test_deleted_local_can_be_kept_or_restored(self):
        (self.prefix / self.name).unlink()
        self.new_report()
        session = self.session()
        session.choose(self.name, "local")
        session.save()
        self.assertFalse((self.prefix / self.name).exists())
        session.choose(self.name, "incoming")
        session.save()
        self.assertEqual((self.prefix / self.name).read_bytes(), (self.source / self.name).read_bytes())

    def test_incoming_deletion_removes_only_selected_obsolete_file(self):
        name = "cli_help/obsolete.py"
        (self.prefix / name).write_bytes(b"# locally edited\n")
        manifest = self.manifest()
        manifest["files"][name] = installation.digest(b"# old\n")
        (self.prefix / installation.MARKER).write_text(json.dumps(manifest))
        self.new_report()
        session = self.session()
        session.choose(name, "incoming")
        backup = session.save()
        self.assertFalse((self.prefix / name).exists())
        self.assertNotIn(name, self.manifest()["files"])
        self.assertEqual((backup / "previous" / name).read_bytes(), b"# locally edited\n")
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)

    def test_unmanaged_collision_requires_explicit_incoming_choice(self):
        name = "cli_help/new.py"
        (self.prefix / name).write_text("# custom\n")
        (self.source / name).write_text("# incoming\n")
        self.new_report()
        session = self.session()
        session.choose(name, "local")
        session.save()
        self.assertNotIn(name, self.manifest()["files"])
        session.choose(name, "incoming")
        session.save()
        self.assertEqual(self.manifest()["files"][name], installation.digest(b"# incoming\n"))

    def test_symlink_conflict_can_be_kept_but_never_followed(self):
        outside = self.home / "outside"
        outside.write_text("private")
        path = self.prefix / self.name
        path.unlink()
        path.symlink_to(outside)
        self.new_report()
        session = self.session()
        for choice in ("incoming", "edit"):
            with self.assertRaisesRegex(ValueError, "Symlink"):
                session.choose(self.name, choice, b"# merge\n")
        session.choose(self.name, "local")
        session.save()
        self.assertTrue(path.is_symlink())
        self.assertEqual(outside.read_text(), "private")

    def test_directory_conflict_is_not_removed(self):
        path = self.prefix / self.name
        path.unlink()
        path.mkdir()
        (path / "keep").write_text("keep")
        self.new_report()
        session = self.session()
        with self.assertRaises(ValueError):
            session.choose(self.name, "incoming")
        self.assertEqual((path / "keep").read_text(), "keep")

    def test_modified_incoming_is_rejected_before_review(self):
        (self.report.parent / "incoming" / self.name).write_text("# tampered\n")
        with self.assertRaisesRegex(ValueError, "Incoming distribution changed"):
            self.session()

    def test_invalid_report_paths_duplicates_and_versions_are_rejected(self):
        original = json.loads(self.report.read_text())
        bad = [[], {**original, "schema_version": 99},
               {**original, "preserved": [{"path": "../../outside", "reason": "bad"}]},
               {**original, "preserved": original["preserved"] * 2},
               {**original, "incoming_files": {"cli_help/not-there.py": None}}]
        for value in bad:
            with self.subTest(value=value):
                self.report.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    self.session()
        self.assertFalse(self.review_backups())

    def test_moved_report_or_symlinked_state_is_rejected(self):
        moved = self.home / "report.json"
        moved.write_bytes(self.report.read_bytes())
        with self.assertRaises(ValueError):
            review.ReviewSession(moved)
        (self.report.parent / review.STATE).symlink_to(self.home / "missing")
        with self.assertRaises(ValueError):
            self.session()

    def test_malformed_saved_decisions_are_rejected(self):
        session = self.session()
        session.choose(self.name, "local")
        session.save()
        path = self.report.parent / review.STATE
        original = json.loads(path.read_text())
        for decision in (None, {"choice": "execute"}, {"choice": "local", "local": [], "incoming": {}}):
            path.write_text(json.dumps({**original, "decisions": {self.name: decision}}))
            with self.assertRaises(ValueError):
                self.session()

    def test_stale_local_report_incoming_and_state_stop_save(self):
        for target in (self.prefix / self.name, self.report,
                       self.report.parent / "incoming" / self.name, self.report.parent / review.STATE):
            with self.subTest(target=target):
                session = self.session()
                session.choose(self.name, "incoming")
                before = target.read_bytes() if target.exists() else None
                target.write_bytes((before or b"") + b" ")
                with self.assertRaises(ValueError):
                    session.save()
                if before is None:
                    target.unlink()
                else:
                    target.write_bytes(before)
        self.assertFalse(self.review_backups())

    def test_stale_manifest_after_later_update_is_rejected(self):
        with (self.source / "cli_help/ui.py").open("a") as stream:
            stream.write("\n# next version\n")
        self.upgrade(status=2)
        with self.assertRaisesRegex(ValueError, "metadata changed"):
            self.session()

    def test_local_edit_invalidates_saved_decision(self):
        session = self.session()
        session.choose(self.name, "local")
        session.save()
        (self.prefix / self.name).write_bytes(self.local + b"# another edit\n")
        self.assertEqual(self.session().status(self.name), "pending")

    def test_existing_install_lock_stops_save(self):
        session = self.session()
        session.choose(self.name, "incoming")
        lock = self.prefix.with_name(self.prefix.name + ".install.lock")
        lock.write_text("active")
        with self.assertRaises(FileExistsError):
            session.save()
        self.assertEqual(lock.read_text(), "active")
        self.assertFalse(self.review_backups())

    def test_failed_state_write_rolls_back_files_and_manifest(self):
        session = self.session()
        session.choose(self.name, "incoming")
        original = installation.tree_state(self.prefix)
        write = review.atomic_json

        def fail_state(path, value):
            if path.name == review.STATE:
                raise OSError("state write failed")
            return write(path, value)

        with patch.object(review, "atomic_json", side_effect=fail_state):
            with self.assertRaises(OSError):
                session.save()
        self.assertEqual(installation.tree_state(self.prefix), original)
        self.assertFalse((self.report.parent / review.STATE).exists())
        self.assertTrue((self.review_backups()[0] / "failed-runtime").is_dir())

    def test_failed_runtime_switch_restores_original(self):
        session = self.session()
        session.choose(self.name, "incoming")
        original = installation.tree_state(self.prefix)
        rename = Path.rename

        def fail_switch(path, target):
            if path.name == "runtime" and Path(target) == self.prefix:
                raise OSError("switch failed")
            return rename(path, target)

        with patch.object(Path, "rename", fail_switch):
            with self.assertRaises(OSError):
                session.save()
        self.assertEqual(installation.tree_state(self.prefix), original)

    def test_interrupt_during_state_save_restores_original(self):
        session = self.session()
        session.choose(self.name, "incoming")
        original = installation.tree_state(self.prefix)
        write = review.atomic_json

        def interrupt_state(path, value):
            if path.name == review.STATE:
                raise KeyboardInterrupt()
            return write(path, value)

        with patch.object(review, "atomic_json", side_effect=interrupt_state):
            with self.assertRaises(KeyboardInterrupt):
                session.save()
        self.assertEqual(installation.tree_state(self.prefix), original)

    def test_interrupt_after_state_replacement_restores_runtime_and_state(self):
        for existing_state in (False, True):
            with self.subTest(existing_state=existing_state):
                session = self.session()
                if existing_state:
                    session.choose(self.name, "local")
                    session.save()
                before = installation.tree_state(self.prefix)
                state_path = self.report.parent / review.STATE
                state_bytes = state_path.read_bytes() if state_path.exists() else None
                session.choose(self.name, "incoming")
                write = review.atomic_json

                def interrupt_after_write(path, value):
                    write(path, value)
                    if path == state_path:
                        raise KeyboardInterrupt()

                with patch.object(review, "atomic_json", side_effect=interrupt_after_write):
                    with self.assertRaises(KeyboardInterrupt):
                        session.save()
                self.assertEqual(installation.tree_state(self.prefix), before)
                self.assertEqual(state_path.read_bytes() if state_path.exists() else None, state_bytes)
                self.session()

    def test_empty_review_state_is_refused(self):
        (self.report.parent / review.STATE).write_bytes(b"")
        with self.assertRaises(ValueError):
            self.session()

    def test_invalid_json_merge_is_rejected(self):
        name = "profiles/rsync.json"
        with (self.prefix / name).open("a") as stream:
            stream.write("\n ")
        self.new_report()
        with self.assertRaises(ValueError):
            self.session().choose(name, "edit", b"{ invalid")

    def test_unchanged_readonly_mode_survives_resolution(self):
        (self.prefix / self.name).chmod(0o444)
        session = self.session()
        session.choose(self.name, "incoming")
        session.save()
        self.assertEqual((self.prefix / self.name).stat().st_mode & 0o777, 0o444)

    def test_concurrent_edit_during_staging_stops_switch(self):
        session = self.session()
        session.choose(self.name, "incoming")
        copy = review.shutil.copytree

        def edit_after_copy(*args, **kwargs):
            result = copy(*args, **kwargs)
            if Path(args[0]) == self.prefix:
                (self.prefix / "notes").write_text("new edit")
            return result

        with patch.object(review.shutil, "copytree", side_effect=edit_after_copy):
            with self.assertRaises(ValueError):
                session.save()
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)
        self.assertEqual((self.prefix / "notes").read_text(), "new edit")

    def test_legacy_report_remains_reviewable_with_warning_flag(self):
        report = json.loads(self.report.read_text())
        for field in ("schema_version", "incoming_files", "installed_manifest_sha256"):
            report.pop(field)
        self.report.write_text(json.dumps(report))
        session = self.session()
        self.assertTrue(session.legacy)
        session.choose(self.name, "incoming")
        session.save()
        self.assertEqual(self.session().status(self.name), "saved incoming")

    def test_invalid_editor_syntax_preserves_existing_choice(self):
        session = self.session()
        session.choose(self.name, "local")
        with self.assertRaises(SyntaxError):
            session.choose(self.name, "edit", b"def broken(\n")
        self.assertEqual(session.status(self.name), "queued local")

    def test_editor_arguments_are_literal_and_failed_draft_is_retained(self):
        editor = self.home / "editor's path"
        editor.write_text("import pathlib, sys\np = pathlib.Path(sys.argv[-1])\np.write_text('# edited merge\\n')\n")
        command = shlex.join([sys.executable, str(editor)])
        session = self.session()
        with patch.dict(os.environ, {"VISUAL": command}):
            session.edit(self.name)
        self.assertEqual(session.choices[self.name], ("edit", b"# edited merge\n"))
        editor.write_text("import sys\nsys.exit(1)\n")
        with patch.dict(os.environ, {"VISUAL": command}):
            with self.assertRaisesRegex(ValueError, "Editor failed"):
                session.edit(self.name)
        self.assertEqual(len(list(self.report.parent.glob("review-draft-*"))), 2)
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)

    def test_display_escapes_terminal_sequences_and_paginates(self):
        output = io.StringIO()
        with redirect_stdout(output), patch("builtins.input", return_value="q") as answer:
            review.paged(["\x1b[31m\u202eunsafe\n"] * 25)
        self.assertNotIn("\x1b", output.getvalue())
        self.assertNotIn("\u202e", output.getvalue())
        self.assertEqual(output.getvalue().count("unsafe"), 20)
        answer.assert_called_once()

    def test_binary_and_oversized_text_refuse_editing(self):
        for data in (b"\0binary", b"\xff", b"x" * (review.MAX_TEXT_BYTES + 1)):
            with self.assertRaises(ValueError):
                review.text_content(data)
        (self.prefix / self.name).write_bytes(b"\0binary")
        self.new_report()
        session = self.session()
        session.choose(self.name, "incoming")
        session.save()
        self.assertEqual((self.prefix / self.name).read_bytes(), (self.source / self.name).read_bytes())

    def test_quit_discard_and_empty_save_do_not_mutate_runtime(self):
        original = installation.tree_state(self.prefix)
        session = self.session()
        with self.assertRaises(ValueError):
            session.save()
        with patch("builtins.input", side_effect=["1", "k", "q", "y"]), redirect_stdout(io.StringIO()):
            review.interactive(session)
        self.assertEqual(installation.tree_state(self.prefix), original)
        self.assertFalse(self.review_backups())

    def test_cli_requires_terminal(self):
        result = subprocess.run(["bash", str(ROOT / "review-update.sh"), str(self.report)],
                                env=self.environment, text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires a terminal", result.stderr)

    def test_real_terminal_diff_replace_save_and_insertion(self):
        folder = self.home / "terminal"
        folder.mkdir()
        shell = BashSession(folder, extra_environment={"PYTHONDONTWRITEBYTECODE": "1"})
        try:
            shell.send("bash " + shlex.quote(str(self.prefix / "review-update.sh")) + " " +
                       shlex.quote(str(self.report)) + "\n")
            shell.expect(b"Review >")
            shell.send("1\n")
            shell.expect(b"Choice >")
            shell.send("d\n")
            shell.expect(b"--- local/cli_help/core.py")
            shell.expect(b"Choice >")
            shell.send("r\n")
            shell.expect(b"Review >")
            shell.send("s\n")
            shell.expect(b"Apply queued choices with backups?")
            shell.send("y\n")
            shell.expect(b"Choices saved.")
            shell.expect(b"Review >")
            shell.send("q\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
            shell.send("cli_help_unbind; source " + shlex.quote(str(self.prefix / "bash/interactive-help.bash")) + "\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
            shell.open("rsync --ar")
            shell.finish("\n")
            self.assertEqual(shell.read_buffer(), ("rsync --archive ", 16))
            self.assertFalse(shell.executed.exists())
        finally:
            shell.close()


if __name__ == "__main__":
    unittest.main()
