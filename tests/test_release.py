"""Build and smoke-test release installers, native launching, and checksum files."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import build_release


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_folder = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.build_folder.cleanup)
        cls.output = Path(cls.build_folder.name) / "release"
        build_release.build(ROOT, cls.output)
        cls.base = "cli-interactive-help-v" + (ROOT / "VERSION").read_text().strip()
        cls.bundle = cls.output / (cls.base + "-linux-x86_64.tar.gz")
        cls.installer = cls.output / (cls.base + "-linux-x86_64.run")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith("CLI_HELP_") and key not in {"BASH_ENV", "ENV", "XDG_DATA_HOME", "TMPDIR"}}
        self.environment.update(HOME=str(self.home), CLI_HELP_PYTHON=sys.executable,
                                PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(self.home))

    def run_command(self, arguments, status=0):
        result = subprocess.run(list(map(str, arguments)), env=self.environment,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        return result

    def extract(self):
        self.run_command(["tar", "-xzf", self.bundle, "-C", self.home])
        return self.home / self.base

    def test_all_checksums_and_source_provenance_match(self):
        for checksum in self.output.glob("*.checksum"):
            for line in checksum.read_text().splitlines():
                expected, name = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), expected)
        info = json.loads((self.output / "BUILD-INFO.json").read_text())
        for name, checksum in info["source_files"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), checksum)

    def test_source_archive_excludes_reports_caches_and_prior_releases(self):
        with tarfile.open(self.output / (self.base + "-source.tar.gz")) as bundle:
            names = bundle.getnames()
            self.assertTrue(all(name.startswith(self.base + "/") for name in names))
            self.assertFalse(any(part in {"reports", "__pycache__", "releases", ".git", ".venv", "dist"}
                                 for name in names for part in Path(name).parts[1:]))
            self.assertIn(self.base + "/scripts/guided_merge.py", names)
            self.assertIn(self.base + "/docs/releases.md", names)
            self.assertIn(self.base + "/tests/test_release.py", names)

    def test_normalized_archives_and_native_build_are_repeatable(self):
        second = self.home / "second"
        build_release.build(ROOT, second)
        for path in self.output.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes(), path.name)

    def test_native_version_check_and_literal_install_path(self):
        runtime = self.extract()
        self.assertTrue((runtime / "cli-help").read_bytes().startswith(b"\x7fELF"))
        self.assertIn("0.1.1-alpha", self.run_command([runtime / "cli-help", "--version"]).stdout)
        self.run_command([runtime / "cli-help", "--check"])
        prefix = self.home / "app's $(touch SHOULD_NOT_EXIST); path"
        self.run_command([runtime / "cli-help", "install", "--prefix", prefix, "--no-rc"])
        self.run_command([prefix / "cli-help", "--check"])
        self.assertFalse((self.home / "SHOULD_NOT_EXIST").exists())
        self.run_command([prefix / "cli-help", "uninstall"])
        self.assertFalse(prefix.exists())

    def test_standalone_launcher_explains_missing_runtime(self):
        native = next(self.output.glob("cli-help-v*-linux-x86_64"))
        self.assertIn("adjacent runtime is missing", self.run_command([native, "--check"], status=1).stderr)

    def test_missing_python_is_reported_without_startup_changes(self):
        runtime = self.extract()
        self.environment["CLI_HELP_PYTHON"] = str(self.home / "no-python")
        self.run_command([runtime / "cli-help", "--check"], status=127)
        self.assertFalse((self.home / ".bashrc").exists())

    def test_self_extracting_install_update_and_uninstall(self):
        self.run_command(["bash", self.installer, "--verify"])
        self.run_command(["bash", self.installer, "install"])
        prefix = self.home / ".local/share/cli-interactive-help"
        startup = (self.home / ".bashrc").read_bytes()
        self.run_command(["bash", self.installer, "update"])
        self.assertEqual((self.home / ".bashrc").read_bytes(), startup)
        self.run_command([prefix / "cli-help", "--check"])
        self.run_command([prefix / "cli-help", "uninstall"])
        self.assertFalse(prefix.exists())
        self.assertFalse(list(self.home.glob("cli-help-installer.*")))

    def test_conflicted_self_extracting_update_retains_review_source_and_edits(self):
        self.run_command(["bash", self.installer, "install", "--no-rc"])
        prefix = self.home / ".local/share/cli-interactive-help"
        profile = prefix / "profiles/rsync.json"
        local = profile.read_bytes() + b"\n "
        profile.write_bytes(local)
        result = self.run_command(["bash", self.installer, "update"], status=2)
        self.assertIn("Source retained for conflict review", result.stdout)
        self.assertEqual(profile.read_bytes(), local)
        sources = list(self.home.glob("cli-help-installer.*/" + self.base + "/review-update.sh"))
        self.assertEqual(len(sources), 1)

    def test_corrupted_installer_payload_is_rejected_before_installation(self):
        corrupted = self.home / "corrupt.run"
        data = bytearray(self.installer.read_bytes())
        data[-15] ^= 1
        corrupted.write_bytes(data)
        result = self.run_command(["bash", corrupted], status=1)
        self.assertIn("checksum", result.stderr)
        self.assertFalse((self.home / ".bashrc").exists())
        self.assertFalse((self.home / ".local/share/cli-interactive-help").exists())

    def test_builder_refuses_existing_output_bad_version_and_missing_compiler(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            build_release.build(ROOT, self.output)
        (self.home / "VERSION").write_text('0.1; touch unexpected')
        with self.assertRaisesRegex(ValueError, "semantic version"):
            build_release.build(self.home, self.home / "output")
        with patch.object(build_release.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "compiler"):
                build_release.build(ROOT, self.home / "no-compiler")


if __name__ == "__main__":
    unittest.main()
