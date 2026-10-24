"""Rendered evidence for Unicode cell clipping and delayed terminal key sequences."""

import copy
import json
import shlex
import time
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT
from test_argument_syntax import PROFILE


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class SyntaxScreenTests(TerminalTestCase):
    def configure(self, shell, profile, delay=None):
        folder = shell.folder / "profiles"
        folder.mkdir()
        (folder / "fixture.json").write_text(json.dumps(profile))
        extra = " CLI_HELP_ESCAPE_DELAY=" + str(delay) if delay else ""
        shell.text("typed() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; export CLI_HELP_PROFILES="
                   + shlex.quote(str(folder)) + extra)
        shell.keys("Enter")
        shell.wait_for(lambda value: value.cells[value.y] == PROMPT.rstrip())
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda value: value.history_markers() == HISTORY)

    def test_wide_labels_do_not_spill_into_the_next_row(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Mixed 界 cafe\u0301 text",
            "categories": [{"name": "界" * 20, "options": [
                {"flag": "--flag", "summary": "語" * 60, "detail": "界" * 90}]}]})
        shell.text("typed --fl")
        before = shell.wait_for(lambda value: value.x == len(PROMPT + "typed --fl"))
        menu = shell.open_menu()
        self.assertEqual(menu.cells[5].strip(), "")
        self.assertIn("OPTIONS *", menu.cells[3])
        self.assertIn("> --flag", menu.cells[4])
        self.assertEqual(shell.cancel(), before)
        self.assertEqual(shell.read_buffer(), ("typed --fl", len("typed --fl")))
        self.assertFalse(shell.executed.exists())

    def test_combining_buffer_cursor_resize_and_keyboard_selection(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [{"flag": "--flag", "summary": "cafe\u0301 界"}]}]})
        line = "typed 'cafe\u0301界' --fl"
        shell.text(line)
        before = shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        self.assertEqual(shell.cancel("C-c"), before)
        shell.open_menu()
        shell.resize(40, 10)
        shell.resize(100, 24)
        shell.keys("Enter")
        expected = "typed 'cafe\u0301界' --flag "
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + expected))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_attached_only_insertion_retains_payload_and_does_not_execute(self):
        shell = self.start()
        profile = json.loads((ROOT / "profiles/7z-x.json").read_text())
        self.configure(shell, profile)
        shell.text("7z() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda value: value.cells[value.y] == PROMPT.rstrip())
        line = "7z x 'archive.7z' -o"
        shell.text(line)
        shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        shell.keys("Enter")
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        shell.text("'café dir' -y")
        expected = "7z x 'archive.7z' -o'café dir' -y"
        before = shell.wait_for(lambda value: value.x == len(PROMPT + expected))
        shell.open_menu()
        self.assertEqual(shell.cancel(), before)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_declared_bundles_survive_selection_through_bash_adapter(self):
        shell = self.start()
        self.configure(shell, PROFILE)
        shell.text("typed -abn5 --fl")
        shell.wait_for(lambda value: value.x == len(PROMPT + "typed -abn5 --fl"))
        shell.open_menu()
        shell.keys("Enter")
        expected = "typed -abn5 --flag "
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + expected))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_configured_escape_delay_accepts_fragmented_down_key(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [
                {"flag": "--alpha", "summary": "First"}, {"flag": "--beta", "summary": "Second"}]}]}, delay=250)
        shell.text("typed --")
        shell.wait_for(lambda value: value.x == len(PROMPT + "typed --"))
        shell.open_menu()
        shell.text("\x1bO")
        time.sleep(0.08)
        shell.text("B")
        menu = shell.wait_for(lambda value: value.alternate == 1 and "> --beta" in value.cells[5])
        shell.keys("Enter")
        after = shell.wait_for(lambda value: value.alternate == 0 and "--beta" in "".join(value.cells))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), ("typed --beta ", len("typed --beta ")))
        self.assertFalse(shell.executed.exists())

    def test_combining_search_and_fragmented_unmapped_alt_preserve_input(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [
                {"flag": "--alpha", "summary": "cafe\u0301 界"}, {"flag": "--beta", "summary": "Other"}]}]}, delay=250)
        line = "typed --"
        shell.text(line)
        before = shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        shell.text("/")
        shell.keys("C-u")
        shell.text("cafe\u0301")
        shell.keys("Enter")
        menu = shell.wait_for(lambda value: "> --alpha" in value.cells[4] and "--beta" not in "".join(value.cells))
        self.assertIn("cafe\u0301 界", menu.cells[4])
        self.assertEqual(shell.cancel(), before)
        shell.open_menu()
        shell.text("\x1b")
        time.sleep(0.08)
        shell.text("x")
        cancelled = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line))
        self.assertEqual(cancelled, before)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_incomplete_bundle_error_preserves_input_and_reopens(self):
        shell = self.start()
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"][2]["argument_style"] = "attached_only"
        self.configure(shell, profile)
        line = "typed -abn 'REVIEW_PRIVATE_SENTINEL' --fl"
        shell.text(line)
        shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.keys("Escape", "h")
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line)
            and any("interactive-help: option_value_required:" in row for row in value.cells))
        self.assertEqual(after.cells[after.y], PROMPT + line)
        self.assertEqual(after.history_markers(), HISTORY)
        error = next(row for row in after.cells if "interactive-help: option_value_required:" in row)
        self.assertNotIn("REVIEW_PRIVATE_SENTINEL", error)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        shell.keys("C-u")
        shell.text("typed -abn5 --fl")
        before = shell.wait_for(lambda value: value.x == len(PROMPT + "typed -abn5 --fl"))
        shell.open_menu()
        self.assertEqual(shell.cancel(), before)
        self.assertFalse(shell.executed.exists())
