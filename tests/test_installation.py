"""Test installation and removal in isolated homes, including real Bash insertion."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_bash_pty import BashSession
from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import installation


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.prefix = self.home / ".local/share/cli-interactive-help"
        self.rc = self.home / ".bashrc"
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith("CLI_HELP_") and key not in {"BASH_ENV", "ENV", "XDG_DATA_HOME"}}
        self.environment.update(HOME=str(self.home), CLI_HELP_PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE="1")

    def run_script(self, action, *args, success=True, script=None):
        """Run the public Bash entrypoint without inheriting a real user installation."""
        result = subprocess.run(["bash", str(script or ROOT / (action + ".sh")), *map(str, args)],
                                env=self.environment, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_install_reinstall_and_uninstall_restore_original_rc_bytes_and_mode(self):
        original = b"# existing settings\r\nexport EXAMPLE='unchanged'"  # No final newline.
        self.rc.write_bytes(original)
        self.rc.chmod(0o640)
        self.run_script("install")
        installed = self.rc.read_bytes()
        self.assertTrue(installed.startswith(original))
        self.assertEqual(self.rc.stat().st_mode & 0o777, 0o640)
        self.assertTrue((self.prefix / "cli_help/main.py").is_file())
        self.assertFalse((self.prefix / "tests").exists())
        backups = list(self.home.glob(".bashrc.cli-help-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.run_script("install")
        self.assertEqual(self.rc.read_bytes(), installed)
        self.assertEqual(len(list(self.home.glob(".bashrc.cli-help-backup-*"))), 1)
        result = subprocess.run([str(self.prefix / "uninstall.sh")], env=self.environment,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.rc.read_bytes(), original)
        self.assertFalse(self.prefix.exists())
        self.run_script("uninstall")

    def test_custom_destination_startup_file_and_shell_metacharacters_are_literal(self):
        prefix = self.home / "app's data $(touch SHOULD_NOT_EXIST); x"
        rc = self.home / "custom bashrc"
        self.run_script("install", "--prefix", prefix, "--rc-file", rc)
        result = subprocess.run(["bash", "--noprofile", "--rcfile", str(rc), "-i", "-c",
                                 'printf "\\0%s" "$_CLI_HELP_ROOT"'], env=self.environment,
                                cwd=self.home, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split("\0")[-1], str(prefix))
        self.assertFalse((self.home / "SHOULD_NOT_EXIST").exists())
        self.run_script("uninstall", "--prefix", prefix)
        self.assertEqual(rc.read_bytes(), b"")

    def test_xdg_destination_and_no_rc_mode(self):
        self.environment["XDG_DATA_HOME"] = str(self.home / "data")
        prefix = self.home / "data/cli-interactive-help"
        self.run_script("install", "--no-rc")
        self.assertFalse(self.rc.exists())
        self.assertTrue((prefix / "profiles/rsync.json").is_file())
        self.run_script("install", "--no-rc")
        self.run_script("uninstall", script=prefix / "uninstall.sh")
        self.assertFalse(prefix.exists())

    def test_uninstall_preserves_user_edits_extra_files_and_external_configuration(self):
        self.run_script("install")
        profile = self.prefix / "profiles/rsync.json"
        profile.write_text('{"custom": true}\n')
        extra = self.prefix / "notes.txt"
        extra.write_text("keep")
        config = self.home / ".config/cli-help/drivers/custom.json"
        config.parent.mkdir(parents=True)
        config.write_text("keep")
        self.run_script("uninstall")
        self.assertTrue(profile.exists())
        self.assertEqual(extra.read_text(), "keep")
        self.assertEqual(config.read_text(), "keep")
        self.assertFalse((self.prefix / "bash/interactive-help.bash").exists())
        self.assertFalse((self.prefix / installation.MARKER).exists())

    def test_uninstall_preserves_later_startup_edits(self):
        self.rc.write_bytes(b"# before\n")
        self.run_script("install")
        with self.rc.open("ab") as stream:
            stream.write(b"export AFTER=1\n")
        self.run_script("uninstall")
        self.assertEqual(self.rc.read_bytes(), b"# before\nexport AFTER=1\n")

    def test_missing_startup_file_does_not_prevent_removal(self):
        self.run_script("install")
        self.rc.unlink()
        self.run_script("uninstall")
        self.assertFalse(self.prefix.exists())
        self.assertFalse(self.rc.exists())

    def test_modified_or_ambiguous_startup_block_prevents_removal(self):
        self.run_script("install")
        original = self.rc.read_bytes()
        for data in (original.replace(b"source ", b"echo "), original + original,
                     original.replace(installation.END, b"# missing end")):
            with self.subTest(data=data):
                self.rc.write_bytes(data)
                self.run_script("uninstall", success=False)
                self.assertEqual(self.rc.read_bytes(), data)
                self.assertTrue((self.prefix / "cli_help/main.py").exists())

    def test_preexisting_unmanaged_directory_is_never_overwritten(self):
        self.prefix.mkdir(parents=True)
        sentinel = self.prefix / "keep.txt"
        sentinel.write_text("keep")
        self.run_script("install", success=False)
        self.run_script("uninstall", success=False)
        self.assertEqual(sentinel.read_text(), "keep")
        self.assertFalse(self.rc.exists())

    def test_symlinked_destination_startup_and_parents_are_rejected(self):
        real = self.home / "real"
        real.mkdir()
        alias = self.home / "alias"
        alias.symlink_to(real, target_is_directory=True)
        self.run_script("install", "--prefix", alias / "app", success=False)
        self.rc.symlink_to(real / "rc")
        self.run_script("install", success=False)
        self.assertFalse(self.prefix.exists())
        self.assertEqual(list(real.iterdir()), [])

    def test_replaced_installed_file_symlink_is_not_followed_or_deleted(self):
        self.run_script("install")
        target = self.home / "private-data"
        target.write_text("keep")
        path = self.prefix / "profiles/rsync.json"
        path.unlink()
        path.symlink_to(target)
        self.run_script("uninstall")
        self.assertTrue(path.is_symlink())
        self.assertEqual(target.read_text(), "keep")

    def test_tampered_manifest_cannot_delete_outside_payload(self):
        self.run_script("install")
        marker = self.prefix / installation.MARKER
        original = json.loads(marker.read_text())
        for name in ("../../.bashrc", "/tmp/outside", "notes.txt", "cli_help/nested/other.py"):
            with self.subTest(name=name):
                modified = {**original, "files": {name: "0" * 64}}
                marker.write_text(json.dumps(modified))
                self.run_script("uninstall", success=False)
                self.assertTrue((self.prefix / "cli_help/main.py").is_file())
        marker.write_text("[]")
        result = self.run_script("uninstall", success=False)
        self.assertNotIn("Traceback", result.stderr)

    def test_existing_lock_stops_mutation(self):
        self.prefix.parent.mkdir(parents=True)
        lock = self.prefix.with_name(self.prefix.name + ".install.lock")
        lock.write_text("active")
        self.run_script("install", success=False)
        self.assertEqual(lock.read_text(), "active")
        self.assertFalse(self.rc.exists())

    def test_invalid_paths_and_argument_combinations_fail_before_installing(self):
        for args in (("--prefix", "/"), ("--prefix", self.home), ("--prefix", ROOT),
                     ("--prefix", str(self.home / "newline") + "\npath"),
                     ("--no-rc", "--rc-file", self.rc),
                     ("--rc-file", self.prefix / "rc")):
            with self.subTest(args=args):
                self.run_script("install", *args, success=False)
        self.environment["XDG_DATA_HOME"] = "relative"
        self.run_script("install", success=False)
        self.assertFalse(self.rc.exists())

    def test_changed_installation_or_different_settings_require_explicit_removal(self):
        self.run_script("install")
        self.run_script("install", "--no-rc", success=False)
        (self.prefix / "cli_help/core.py").write_text("# local modification\n")
        self.run_script("install", success=False)

    def test_custom_rc_uninstall_ignores_an_unrelated_symlinked_default_rc(self):
        self.rc.symlink_to(self.home / "unrelated")
        custom = self.home / "custom-rc"
        self.run_script("install", "--rc-file", custom)
        self.run_script("uninstall")
        self.assertTrue(self.rc.is_symlink())
        self.assertFalse(self.prefix.exists())

    def test_installer_never_executes_existing_startup_code(self):
        marker = self.home / "startup-executed"
        original = ("touch " + shlex.quote(str(marker)) + "\n").encode()
        self.rc.write_bytes(original)
        self.run_script("install")
        self.run_script("uninstall")
        self.assertFalse(marker.exists())
        self.assertEqual(self.rc.read_bytes(), original)

    def test_unmatched_existing_marker_prevents_new_installation(self):
        original = b"# settings\n" + installation.BEGIN + b"\n"
        self.rc.write_bytes(original)
        self.run_script("install", success=False)
        self.assertFalse(self.prefix.exists())
        self.assertEqual(self.rc.read_bytes(), original)

    def test_missing_python_fails_without_files_or_startup_changes(self):
        self.environment["CLI_HELP_PYTHON"] = str(self.home / "no-python")
        self.run_script("install", success=False)
        self.assertFalse(self.prefix.exists())
        self.assertFalse(self.rc.exists())

    def test_validation_failure_leaves_no_installed_runtime(self):
        self.prefix.parent.mkdir(parents=True)
        with patch.object(installation.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "check")):
            with self.assertRaises(subprocess.CalledProcessError):
                installation.install(self.prefix, self.rc)
        self.assertFalse(self.prefix.exists())
        self.assertFalse(self.rc.exists())
        self.assertFalse(list(self.prefix.parent.glob(".cli-help-stage-*")))

    def test_failed_rc_update_rolls_back_the_new_payload(self):
        self.prefix.parent.mkdir(parents=True)
        self.rc.write_bytes(b"# original\n")
        with patch.object(installation, "write_rc", side_effect=OSError("read-only")):
            with self.assertRaises(OSError):
                installation.install(self.prefix, self.rc)
        self.assertFalse(self.prefix.exists())
        self.assertEqual(self.rc.read_bytes(), b"# original\n")

    def test_installed_adapter_inserts_without_executing_the_pending_command(self):
        self.run_script("install")
        shell_dir = self.home / "terminal"
        shell_dir.mkdir()
        shell = BashSession(shell_dir, extra_environment={"PYTHONDONTWRITEBYTECODE": "1"})
        try:
            # Switch the real PTY session from the checkout adapter to the installed copy.
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
