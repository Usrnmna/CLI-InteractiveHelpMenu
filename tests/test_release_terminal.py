"""Rendered interaction through an installed release candidate's actual Bash adapter."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

from test_terminal_screen import TmuxShell, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT
import test_release_snapshot as packages


@unittest.skipUnless(TMUX_AVAILABLE, "Packaged rendered checks require Linux and tmux")
class PackagedScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_folder = tempfile.TemporaryDirectory(prefix="cli-help-build-")
        cls.addClassCleanup(cls.build_folder.cleanup)
        selected = os.environ.get("CLI_HELP_TEST_RELEASE_DIR")
        cls.output = Path(selected).resolve(strict=True) if selected else Path(cls.build_folder.name) / "candidate"
        if not selected:
            packages.build_release.build(ROOT, cls.output)
        cls.info = packages.verify_candidate(cls.output)
        cls.installer = cls.output / ("cli-interactive-help-v" + cls.info["version"] + "-linux-x86_64.run")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-screen-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.prefix = self.folder / "installed package's runtime"
        environment = {key: value for key, value in os.environ.items() if not key.startswith("CLI_HELP_")
                       and key not in ("BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME", "XDG_DATA_HOME", "TMPDIR")}
        environment.update(HOME=str(self.folder), CLI_HELP_PYTHON=sys.executable,
                           XDG_CONFIG_HOME=str(self.folder / "config-home"),
                           XDG_CACHE_HOME=str(self.folder / "cache-home"),
                           XDG_DATA_HOME=str(self.folder / "data-home"),
                           PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(self.folder))
        result = subprocess.run(["bash", str(self.installer), "install", "--prefix", str(self.prefix), "--no-rc"],
                                env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        terminal = self.folder / "terminal"
        terminal.mkdir()
        self.shell = TmuxShell(terminal, runtime=self.prefix)
        self.addCleanup(self.shell.close)
        self.assertFalse((self.folder / ".bashrc").exists())

    def configure(self, compose_fixture=False):
        """Activate only the installed supplied drivers and harmless pending-command stubs."""
        shell = self.shell
        extra = ""
        if compose_fixture:
            # Compose routes use discovery rather than a bundled static leaf.
            # This deliberately small profile isolates rendered insertion from
            # program availability; the installed driver still resolves parents.
            profiles = shell.folder / "profiles"
            profiles.mkdir()
            profile = {"command": ["docker", "compose", "up"], "description": "Rendered fixture",
                       "categories": [{"name": "Options", "options": [
                           {"flag": "--detach", "summary": "Run containers in the background"}]}]}
            (profiles / "compose.json").write_text(json.dumps(profile))
            extra = "; export CLI_HELP_PROFILES=" + shlex.quote(str(profiles))
        shell.text("docker() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; "
                   "7z() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; "
                   "export CLI_HELP_DRIVERS=" + shlex.quote(str(self.prefix / "config/drivers.example")) + extra)
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.history_markers() == HISTORY)

    def test_installed_parent_route_unicode_midline_resize_and_selection(self):
        self.configure(compose_fixture=True)
        shell = self.shell
        prefix = "docker compose -f 'cafe\u0301界.yml' --profile debug up --det"
        suffix = " 'suffix 日本'"
        shell.text(prefix + suffix)
        for _ in suffix:
            shell.keys("Left")
        before = shell.wait_for(lambda state: state.x == len(PROMPT + prefix))
        menu = shell.open_menu()
        self.assertIn("docker compose up", menu.cells[0])
        self.assertEqual(shell.cancel(), before)
        shell.open_menu()
        small = shell.resize(40, 10)
        self.assertIn("Resize to at least", small.cells[0])
        shell.resize(100, 24)
        shell.keys("Enter")
        expected_prefix = prefix[:-5] + "--detach "
        expected = expected_prefix + suffix[1:]
        after = shell.wait_for(lambda state: state.alternate == 0 and state.x == len(PROMPT + expected_prefix))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertIn("--detach", "".join(after.cells))
        self.assertEqual(shell.read_buffer(), (expected, len(expected_prefix)))
        shell.text("X")
        typed = shell.wait_for(lambda state: state.x == len(PROMPT + expected_prefix) + 1)
        self.assertEqual(typed.history_markers(), HISTORY)
        self.assertFalse(shell.executed.exists())

    def test_installed_attached_only_values_and_native_passive_report(self):
        shell = self.shell
        native = shlex.quote(str(self.prefix / "cli-help"))
        report = self.folder / "doctor.json"
        shell.text(native + " --doctor > " + shlex.quote(str(report)))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        health = json.loads(report.read_text())
        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["configuration"]["escape_delay_ms"], 40)
        self.configure()
        line = "7z x 'archive.7z' -o"
        shell.text(line)
        before = shell.wait_for(lambda state: state.x == len(PROMPT + line))
        shell.open_menu()
        shell.keys("Enter")
        after = shell.wait_for(lambda state: state.alternate == 0 and state.x == len(PROMPT + line))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        shell.text("'café dir' -y")
        expected = "7z x 'archive.7z' -o'café dir' -y"
        before = shell.wait_for(lambda state: state.x == len(PROMPT + expected))
        shell.open_menu()
        self.assertEqual(shell.cancel("C-c"), before)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_missing_interpreter_is_redacted_and_preserves_rendered_pending_input(self):
        self.configure()
        shell = self.shell
        secret = "INTERPRETER_PRIVATE_SENTINEL"
        shell.text("export CLI_HELP_PYTHON=" + shlex.quote(str(self.folder / ("missing-" + secret))))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix = "rsync --ar"
        suffix = " 'BUFFER_PRIVATE_SENTINEL'"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        before = shell.wait_for(lambda state: state.x == len(PROMPT + prefix))
        shell.keys("Escape", "h")
        after = shell.wait_for(lambda state: state.alternate == 0 and
                               "interpreter_unavailable" in " ".join(state.cells))
        error_start = next(index for index, row in enumerate(after.cells) if "interactive-help:" in row)
        error_rows = "\n".join(after.cells[error_start:after.y])
        self.assertNotIn(secret, error_rows)
        self.assertNotIn("BUFFER_PRIVATE_SENTINEL", error_rows)
        self.assertEqual(after.x, before.x)
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())
