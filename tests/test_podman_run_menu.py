"""Exercise the bundled Podman menus with discovery disabled and a stub command."""

import json
import re
import shlex
import sys
import unittest

from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from presentation import option_label, option_text


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class PodmanRunMenuTests(TerminalTestCase):
    def pending_command(self, columns, rows, command="run", suffix=" fixture-image"):
        """Open real Bash with the cursor immediately before the existing operand suffix."""
        shell = self.start()
        shell.text("podman() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        shell.resize(columns, rows)
        prefix = "podman " + command + " "
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_every_run_row_and_detail_renders(self):
        """Read each category and compare the visible selection and complete Details pane."""
        self.check_all_rows("run", " fixture-image")

    def test_every_build_exec_and_logs_row_renders(self):
        """Read every new spelling and its complete Details from real terminal cells."""
        for command, suffix in (("build", " ./context"), ("exec", " ctr child --help"), ("logs", " ctr")):
            with self.subTest(command=command):
                self.check_all_rows(command, suffix)

    def check_all_rows(self, command, suffix):
        """Compare each selected row, including its formatted value contract, with the screen."""
        profile = json.loads((ROOT / "profiles" / f"podman-{command}.json").read_text(encoding="utf-8"))
        shell, prefix, suffix = self.pending_command(210, 100, command, suffix)
        shell.open_menu()
        for category_index, category in enumerate(profile["categories"]):
            if category_index:
                shell.keys("Right")
            for index, option in enumerate(category["options"]):
                with self.subTest(flag=option["flag"]):
                    if index:
                        shell.keys("Down")
                    label = option_label(option)
                    state = shell.wait_for(lambda state: "Option: " + label in state.cells)
                    start = next(i for i, line in enumerate(state.cells) if line.startswith("Category "))
                    self.assertTrue(any("> " + option["flag"] in line and option["summary"] in line
                                        for line in state.cells[4:start]), label)
                    progress = state.cells[-3].split()[1]
                    first, last = progress.split("-")
                    visible, total = last.split("/")
                    self.assertEqual((first, visible), ("1", total), label)
                    panel = " ".join(" ".join(state.cells[start + 1:-3]).split())
                    for sentence in re.split(r"(?<=[.!?])\s+", option.get("detail", "")):
                        self.assertIn(sentence, panel)
                    for line in option_text(profile, category, option).details:
                        self.assertIn(" ".join(line.split()), panel)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_volume_suffixes_at_minimum_size(self):
        """Find both mount spellings and read host-side effects before literal insertion."""
        shell, prefix, suffix = self.pending_command(60, 16)
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("private SELinux label")
            shell.keys("Enter")
            state = shell.wait_for(lambda state: state.cells[2] == "Filter: private SELinux label")
            self.assertIn("> --volume VOLUME", state.cells[4])
            self.assertIn("-v VOLUME", state.cells[5])
            shell.keys(*(["]"] * int(state.cells[-3].split("/")[1].split()[0])))
            shell.wait_for(lambda state: "mapped container UID and GID" in
                           " ".join(" ".join(state.cells[8:-3]).split()))
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--volume" + suffix, len(prefix + "--volume ")))
        self.assertFalse(shell.executed.exists())

    def test_revisited_menus_at_minimum_size(self):
        """Search from the unfiltered menu, scroll to an operating rule and edit before a suffix."""
        cases = (
            ("build", " ./context", "/run/secrets/token", "--secret", "does not invalidate"),
            ("exec", " ctr child --env x", "one variable per line", "--env-file", "explicit --env values take precedence"),
            ("logs", " web db", "--until=-10m", "--until", "Calendar times without a zone use UTC."),
        )
        for command, suffix, query, flag, guidance in cases:
            with self.subTest(command=command):
                shell, prefix, suffix = self.pending_command(60, 16, command, suffix)
                for action in ("Escape", "Enter"):
                    menu = shell.open_menu()
                    self.assertEqual(menu.cells[2].rstrip(), "Filter:")
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    state = shell.wait_for(lambda state: state.cells[2] == "Filter: " + query)
                    self.assertIn("> " + flag + " ", state.cells[4])
                    total = int(state.cells[-3].split("/")[1].split()[0])
                    visible = int(state.cells[-3].split()[1].split("-")[1].split("/")[0])
                    for offset in range(1, total - visible + 1):
                        shell.keys("]")
                        state = shell.wait_for(lambda state: int(state.cells[-3].split()[1].split("-")[0]) > offset)
                        if guidance in " ".join(" ".join(state.cells[8:-3]).split()):
                            break
                    self.assertIn(guidance, " ".join(" ".join(state.cells[8:-3]).split()))
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, len(prefix + flag + " ")))
                self.assertFalse(shell.executed.exists())

    def test_exec_child_option_stays_with_child(self):
        """Request help at a child option and verify Readline leaves it in place."""
        shell, prefix, suffix = self.pending_command(80, 24, "exec", " ctr child --env")
        shell.keys("End", "Escape", "h")
        shell.wait_for(lambda state: state.alternate == 0 and "child_argument_boundary" in " ".join(state.cells))
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix + suffix)))
        self.assertFalse(shell.executed.exists())
