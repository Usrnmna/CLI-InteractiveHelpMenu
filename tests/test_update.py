"""Exercise upgrades, edit preservation, recovery, and installed Bash insertion."""

import json
import os
from pathlib import Path
import py_compile
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_bash_pty import BashSession
from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import installation


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.prefix = self.home / ".local/share/cli-interactive-help"
        self.rc = self.home / ".bashrc"
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith("CLI_HELP_") and key not in {"BASH_ENV", "ENV", "XDG_DATA_HOME"}}
        self.environment.update(HOME=str(self.home), CLI_HELP_PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE="1")
        self.source = self.home / "new source's $(literal)"
        for pattern in installation.PAYLOAD:
            for path in ROOT.glob(pattern):
                target = self.source / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        self.run_script(ROOT / "install.sh")
        self.original_manifest = self.manifest()
        self.changed = "cli_help/core.py"
        with (self.source / self.changed).open("a") as stream:
            stream.write("\n# Updated distribution fixture.\n")

    def run_script(self, script, *args, status=0):
        result = subprocess.run(["bash", str(script), *map(str, args)], env=self.environment,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        return result

    def upgrade(self, *args, status=0):
        return self.run_script(self.source / "update.sh", *args, status=status)

    def manifest(self):
        return json.loads((self.prefix / installation.MARKER).read_text())

    def backups(self):
        return list(self.prefix.parent.glob(self.prefix.name + ".update-backup-*"))

    def direct_update(self):
        """Use the same merge implementation with injectable filesystem failures."""
        with patch.object(installation, "ROOT", self.source):
            return installation.update(self.prefix)

    def test_upgrade_backup_startup_and_idempotence(self):
        before = installation.tree_state(self.prefix)
        startup = self.rc.read_bytes() + b"# additional settings\n"
        self.rc.write_bytes(startup)
        self.rc.chmod(0o640)
        self.upgrade()
        backup = self.backups()[0]
        self.assertEqual(installation.tree_state(backup / "previous"), before)
        self.assertEqual((self.prefix / self.changed).read_bytes(), (self.source / self.changed).read_bytes())
        self.assertEqual(self.rc.read_bytes(), startup)
        self.assertEqual(self.rc.stat().st_mode & 0o777, 0o640)
        self.assertEqual(self.manifest()["rc_file"], self.original_manifest["rc_file"])
        self.assertEqual(self.manifest()["separator"], self.original_manifest["separator"])
        self.assertEqual(json.loads((backup / "report.json").read_text())["updated"], [self.changed])
        self.assertIn("Already up to date", self.upgrade().stdout)
        self.assertEqual(len(self.backups()), 1)
        self.run_script(self.prefix / "uninstall.sh")
        self.assertFalse(self.prefix.exists())
        self.assertEqual(self.rc.read_bytes(), b"# additional settings\n")

    def test_edited_files_settings_extras_and_deletions_are_preserved(self):
        edited = self.prefix / "profiles/rsync.json"
        edited.write_bytes(b"custom profile bytes\n")
        deleted = self.prefix / "profiles/grep.json"
        deleted.unlink()
        extra = self.prefix / "custom/settings.json"
        extra.parent.mkdir()
        extra.write_text("custom settings")
        config = self.home / ".config/cli-help/keys.json"
        config.parent.mkdir(parents=True)
        config.write_text("external settings")
        self.environment["CLI_HELP_KEYS"] = str(config)
        self.environment["CLI_HELP_PROFILES"] = str(self.home / "nonexistent")
        result = self.upgrade(status=2)
        self.assertIn("Manual merge required: profiles/rsync.json", result.stdout)
        self.assertEqual(edited.read_bytes(), b"custom profile bytes\n")
        self.assertFalse(deleted.exists())
        self.assertEqual(extra.read_text(), "custom settings")
        self.assertEqual(config.read_text(), "external settings")
        self.assertEqual(self.manifest()["files"]["profiles/rsync.json"],
                         self.original_manifest["files"]["profiles/rsync.json"])
        backup = self.backups()[0]
        self.assertEqual((backup / "incoming/profiles/rsync.json").read_bytes(),
                         (self.source / "profiles/rsync.json").read_bytes())
        self.run_script(self.prefix / "uninstall.sh")
        self.assertTrue(edited.exists())
        self.assertTrue(extra.exists())

    def test_edited_installed_code_is_never_executed_by_validation(self):
        marker = self.home / "executed"
        (self.prefix / "cli_help/main.py").write_text(f"open({str(marker)!r}, 'w').write('bad')\n")
        self.upgrade(status=2)
        self.assertFalse(marker.exists())

    def test_manual_resolution_to_incoming_copy_restores_normal_ownership(self):
        path = self.prefix / self.changed
        path.write_text("# local edit\n")
        self.upgrade(status=2)
        shutil.copyfile(self.source / self.changed, path)
        self.upgrade()
        self.assertEqual(self.manifest()["files"][self.changed], installation.digest(path.read_bytes()))
        self.assertIn("Already up to date", self.upgrade().stdout)
        self.run_script(self.prefix / "uninstall.sh")
        self.assertFalse(self.prefix.exists())

    def test_manual_merge_remains_a_preserved_customization_on_repeated_updates(self):
        path = self.prefix / self.changed
        merged = (self.source / self.changed).read_bytes() + b"# custom merge\n"
        path.write_bytes(merged)
        self.upgrade(status=2)
        self.upgrade(status=2)
        self.assertEqual(path.read_bytes(), merged)
        self.assertEqual(len(self.backups()), 2)

    def test_symlinked_managed_parent_does_not_modify_external_files(self):
        original = self.prefix / "profiles"
        external = self.home / "external profiles"
        original.rename(external)
        original.symlink_to(external, target_is_directory=True)
        before = installation.tree_state(external)
        self.upgrade(status=2)
        self.assertTrue(original.is_symlink())
        self.assertEqual(installation.tree_state(external), before)

    def test_mode_changes_survive_content_upgrade(self):
        (self.prefix / self.changed).chmod(0o640)
        self.upgrade()
        self.assertEqual((self.prefix / self.changed).stat().st_mode & 0o777, 0o640)

    def test_readonly_managed_file_can_be_updated_without_changing_its_mode(self):
        (self.prefix / self.changed).chmod(0o444)
        self.upgrade()
        self.assertEqual((self.prefix / self.changed).stat().st_mode & 0o777, 0o444)

    def test_same_second_same_size_upgrade_does_not_reuse_old_bytecode(self):
        name = "cli_help/cache_probe.py"
        path = self.prefix / name
        path.write_text("value = 'old'\n")
        py_compile.compile(str(path), doraise=True)
        old_time = path.stat().st_mtime_ns
        manifest = self.manifest()
        manifest["files"][name] = installation.digest(path.read_bytes())
        (self.prefix / installation.MARKER).write_text(json.dumps(manifest))
        (self.source / name).write_text("value = 'new'\n")
        copy = installation.shutil.copyfile

        def same_second_copy(source, destination, *args, **kwargs):
            result = copy(source, destination, *args, **kwargs)
            if Path(destination).name == "cache_probe.py":
                os.utime(destination, ns=(old_time, old_time))
            return result

        with patch.object(installation.shutil, "copyfile", side_effect=same_second_copy):
            self.direct_update()
        result = subprocess.run([sys.executable, "-c", "import cache_probe; print(cache_probe.value)"],
                                cwd=self.prefix / "cli_help", env=self.environment,
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "new\n")

    def test_legacy_manifest_without_updater_is_supported(self):
        (self.prefix / "update.sh").unlink()
        marker = self.prefix / installation.MARKER
        manifest = self.manifest()
        manifest["files"].pop("update.sh")
        marker.write_text(json.dumps(manifest))
        self.upgrade()
        self.assertIn("update.sh", self.manifest()["files"])
        self.assertEqual((self.prefix / "update.sh").stat().st_mode & 0o777, 0o755)

    def test_new_files_and_unmanaged_collisions(self):
        for name in ("new.py", "collision.py"):
            (self.source / "cli_help" / name).write_text("# incoming\n")
        collision = self.prefix / "cli_help/collision.py"
        collision.write_text("# private\n")
        self.upgrade(status=2)
        self.assertEqual(collision.read_text(), "# private\n")
        self.assertNotIn("cli_help/collision.py", self.manifest()["files"])
        self.assertIn("cli_help/new.py", self.manifest()["files"])
        self.run_script(self.prefix / "uninstall.sh")
        self.assertTrue(collision.exists())

    def test_obsolete_files_removed_only_if_unchanged(self):
        manifest = self.manifest()
        for name in ("old.py", "edited_old.py", "missing_old.py"):
            path = self.prefix / "cli_help" / name
            path.write_text("# old\n")
            manifest["files"]["cli_help/" + name] = installation.digest(path.read_bytes())
        (self.prefix / "cli_help/edited_old.py").write_text("# edited\n")
        (self.prefix / "cli_help/missing_old.py").unlink()
        (self.prefix / installation.MARKER).write_text(json.dumps(manifest))
        self.upgrade(status=2)
        self.assertFalse((self.prefix / "cli_help/old.py").exists())
        self.assertNotIn("cli_help/missing_old.py", self.manifest()["files"])
        self.assertEqual((self.prefix / "cli_help/edited_old.py").read_text(), "# edited\n")
        self.assertIn("cli_help/edited_old.py", self.manifest()["files"])

    def test_links_and_replaced_directories_are_preserved_without_following(self):
        external = self.home / "external"
        external.write_text("private")
        target = self.prefix / "profiles/rsync.json"
        target.unlink()
        target.symlink_to(external)
        (self.prefix / "extra-link").symlink_to(self.home / "missing")
        blocked = self.prefix / "config/drivers.example"
        shutil.rmtree(blocked)
        blocked.write_text("replacement")
        self.upgrade(status=2)
        self.assertTrue(target.is_symlink())
        self.assertTrue((self.prefix / "extra-link").is_symlink())
        self.assertEqual(external.read_text(), "private")
        self.assertEqual(blocked.read_text(), "replacement")

    def test_no_rc_custom_prefix_and_unrelated_startup_symlink(self):
        self.run_script(self.prefix / "uninstall.sh")
        self.rc.unlink()
        self.rc.symlink_to(self.home / "absent")
        self.prefix = self.home / "custom app's $(literal)"
        self.run_script(ROOT / "install.sh", "--prefix", self.prefix, "--no-rc")
        self.upgrade("--prefix", self.prefix)
        self.assertIsNone(self.manifest()["rc_file"])
        self.assertTrue(self.rc.is_symlink())

    def test_custom_startup_code_and_edited_block_are_not_evaluated_or_changed(self):
        marker = self.home / "startup-executed"
        content = ("touch " + shlex.quote(str(marker)) + "\n# custom block removed\n").encode()
        self.rc.write_bytes(content)
        self.upgrade()
        self.assertEqual(self.rc.read_bytes(), content)
        self.assertFalse(marker.exists())

    def test_missing_or_unmanaged_installation_and_bad_metadata_fail(self):
        before = installation.tree_state(self.prefix)
        self.upgrade("--prefix", self.home / "missing", status=1)
        unmanaged = self.home / "unmanaged"
        unmanaged.mkdir()
        (unmanaged / "keep").write_text("keep")
        self.upgrade("--prefix", unmanaged, status=1)
        self.assertEqual(installation.tree_state(self.prefix), before)
        marker = self.prefix / installation.MARKER
        for data in ("[]", "{", json.dumps({**self.manifest(), "files": {"../outside": "0" * 64}})):
            marker.write_text(data)
            self.upgrade(status=1)
        self.assertFalse(self.backups())

    def test_source_overlap_and_startup_flags_are_refused(self):
        for args in (("--prefix", self.source), ("--prefix", self.source / "child"),
                     ("--prefix", self.home), ("--no-rc",), ("--rc-file", self.rc)):
            result = subprocess.run(["bash", str(self.source / "update.sh"), *map(str, args)],
                                    env=self.environment, capture_output=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.backups())

    def test_existing_lock_and_symlinked_prefix_refuse_changes(self):
        lock = self.prefix.with_name(self.prefix.name + ".install.lock")
        lock.write_text("active")
        self.upgrade(status=1)
        self.assertEqual(lock.read_text(), "active")
        link = self.home / "linked"
        link.symlink_to(self.prefix, target_is_directory=True)
        self.upgrade("--prefix", link, status=1)
        self.assertFalse(self.backups())

    def test_special_file_refused_without_hanging(self):
        os.mkfifo(self.prefix / "pipe")
        self.upgrade(status=1)
        self.assertFalse(self.backups())

    def test_invalid_incoming_payload_leaves_installation_unchanged(self):
        before = installation.tree_state(self.prefix)
        (self.source / "profiles/rsync.json").write_text("not JSON")
        self.upgrade(status=1)
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.assertFalse(self.backups())
        self.assertFalse(list(self.prefix.parent.glob(".cli-help-stage-*")))

    def test_missing_incoming_payload_leaves_installation_unchanged(self):
        before = installation.tree_state(self.prefix)
        (self.source / "uninstall.sh").unlink()
        self.upgrade(status=1)
        self.assertEqual(installation.tree_state(self.prefix), before)

    def test_copy_failure_leaves_installation_unchanged(self):
        before = installation.tree_state(self.prefix)
        with patch.object(installation.shutil, "copytree", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.direct_update()
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.assertFalse(self.backups())

    def test_concurrent_edit_aborts_before_switch(self):
        copy = installation.shutil.copytree

        def change_after_copy(*args, **kwargs):
            result = copy(*args, **kwargs)
            if Path(args[0]) == self.prefix:
                (self.prefix / "notes.txt").write_text("concurrent edit")
            return result

        with patch.object(installation.shutil, "copytree", side_effect=change_after_copy):
            with self.assertRaisesRegex(ValueError, "changed during staging"):
                self.direct_update()
        self.assertEqual((self.prefix / "notes.txt").read_text(), "concurrent edit")
        self.assertEqual(self.manifest(), self.original_manifest)
        self.assertFalse(self.backups())

    def test_failed_switch_restores_previous_runtime(self):
        before = installation.tree_state(self.prefix)
        rename = Path.rename

        def fail_switch(path, target):
            if path.name == "runtime" and Path(target) == self.prefix:
                raise OSError("switch failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_switch):
            with self.assertRaisesRegex(OSError, "switch failure"):
                self.direct_update()
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.assertTrue((self.backups()[0] / "incoming").is_dir())

    def test_updated_adapter_inserts_without_execution(self):
        self.upgrade()
        shell_dir = self.home / "terminal"
        shell_dir.mkdir()
        shell = BashSession(shell_dir, extra_environment={"PYTHONDONTWRITEBYTECODE": "1"})
        try:
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
