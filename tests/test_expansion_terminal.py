"""Rendered cells and cursor evidence for prefix and structured insertion."""

import json
import shlex
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ExpansionScreenTests(TerminalTestCase):
    def test_optional_numeric_value_preserves_rendered_edit_and_argument_entry(self):
        from test_optional_integer_values import PROFILE

        shell = self.start()
        self.configure(shell, [PROFILE])
        line = "counted -m 2 --qu"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        expected = "counted -m 2 --query "
        self.assert_restored(shell, expected)
        shell.text("'日本'")
        state = shell.wait_for(lambda value: "日本" in "".join(value.cells))
        self.assertEqual(state.x, len(PROMPT + expected + "'日本'") + 2)
        self.assertEqual(shell.read_buffer(), (expected + "'日本'", len(expected + "'日本'")))
        self.assertFalse(shell.executed.exists())

    def configure(self, shell, profiles):
        """Install isolated fixture profiles without invoking any target command."""
        folder = shell.folder / "profiles"
        folder.mkdir()
        for index, profile in enumerate(profiles):
            (folder / f"{index}.json").write_text(json.dumps(profile))
        shell.text("export CLI_HELP_PROFILES=" + shlex.quote(str(folder)))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())

    def pending(self, shell, line):
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.history_markers() == HISTORY)
        shell.text(line)
        return shell.wait_for(lambda state: line in "".join(state.cells))

    def assert_restored(self, shell, line, before=None):
        state = shell.wait_for(lambda state: state.alternate == 0 and line.rstrip() in "".join(state.cells))
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(state.x, (len(PROMPT) + len(line)) % state.columns)
        if before:
            self.assertEqual((state.cells, state.x, state.y), (before.cells, before.x, before.y))
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_prefix_chain_cancel_resize_insert_and_argument_entry(self):
        shell = self.start()
        line = "command sudo -n env NOTE='café' rsync --ar"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel("C-c")
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.resize(40, 10)
        shell.resize(100, 24)
        shell.keys("Enter")
        expected = line[:-4] + "--archive "
        self.assert_restored(shell, expected)
        shell.text("'日本 folder'")
        # Wide characters occupy two rendered cells each; buffer offsets remain
        # Unicode character offsets, independent of terminal column width.
        state = shell.wait_for(lambda state: "日本 folder" in "".join(state.cells))
        self.assertEqual(state.x, len(PROMPT + expected + "'日本 folder'") + 2)
        self.assertEqual(shell.read_buffer(), (expected + "'日本 folder'", len(expected + "'日本 folder'")))

    def test_keyword_selection_and_repeated_group_browser_labels(self):
        shell = self.start()
        fixture = {"command": ["structured"], "description": "Structured fixture",
                   "positional_group": {"argument": "ADDRESS FILE", "argument_count": 2, "repeatable": True},
                   "categories": [{"name": "Selection", "options": [
                       {"kind": "keyword", "flag": "device", "argument": "NAME", "summary": "Choose a device"}]}]}
        self.configure(shell, [fixture])
        line = "structured 0x1000 'café.bin' de"
        before = self.pending(shell, line)
        menu = shell.open_menu()
        self.assertIn("[keyword]", " ".join(menu.cells))
        self.assertIn("ADDRESS FILE", " ".join(menu.cells))
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, line[:-2] + "device ")

    def test_explicit_module_profile_and_joined_selector_cells(self):
        shell = self.start()
        fixture = {"command": ["python3", "-m", "pytest"], "description": "Explicit module profile",
                   "categories": [{"name": "Selection", "options": [
                       {"flag": "--maxfail", "argument": "NUM", "summary": "Stop after NUM failures"}]}]}
        self.configure(shell, [fixture])
        line = "env NOTE=café python3 -I -m pytest --max"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, line[:-5] + "--maxfail ")
        shell.keys("C-u")
        shell.text("ffmpeg -i 'café.mp4' -c:v")
        shell.wait_for(lambda state: "ffmpeg -i" in " ".join(state.cells))
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, "ffmpeg -i 'café.mp4' -c:v ")


if __name__ == "__main__":
    unittest.main()
