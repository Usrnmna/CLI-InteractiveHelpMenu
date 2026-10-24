"""Exercise repeated real-terminal edits with multi-value arguments and Unicode."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from test_bash_pty import BashSession
from test_discovery import write_executable
from test_terminal_screen import HISTORY, PROMPT, TMUX_AVAILABLE, TerminalTestCase


class ReviewPtyTests(unittest.TestCase):
    def setUp(self):
        """Use an instrumented jq executable and an empty manual source."""
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-review-pty-")
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        binaries = folder / "bin"
        binaries.mkdir()
        self.calls = folder / "calls.jsonl"
        self.executed = folder / "executed"
        text = "Options:\n  --arg name value  Bind a variable.\n  -r, --raw-output  Print raw strings.\n"
        write_executable(binaries / "jq", "import pathlib, json, sys\n"
            f"with open({str(self.calls)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            "if sys.argv[1:] == ['--help']:\n"
            f"    print({text!r})\n"
            "else:\n"
            f"    pathlib.Path({str(self.executed)!r}).write_text('pending command executed')\n")
        write_executable(binaries / "man", "print('Manual unavailable')\n")
        self.session = BashSession(folder, extra_environment={
            "PATH": str(binaries) + os.pathsep + "/usr/bin:/bin",
            "CLI_HELP_CACHE_TTL": "0", "HOME": str(folder), "INPUTRC": "/dev/null"})
        self.addCleanup(self.session.close)

    def test_search_cancel_reopen_insert_preserves_multiple_values_and_suffix(self):
        session = self.session
        prefix = "jq --arg label '-café' --ra"
        line = prefix + " '.[]' 'input file.json'"
        session.send(line)
        session.send(b"\x01" + b"\x06" * len(prefix))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.send("/\x15raw\n")
        session.finish(b"\x03")
        self.assertEqual(session.read_buffer(), (line, len(prefix)))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        expected_prefix = "jq --arg label '-café' --raw-output "
        self.assertEqual(session.read_buffer(),
                         (expected_prefix + "'.[]' 'input file.json'", len(expected_prefix)))
        self.assertFalse(self.executed.exists())
        self.assertEqual([json.loads(line) for line in self.calls.read_text().splitlines()],
                         [["--help"], ["--help"]])

    def test_missing_second_value_rejects_edit_and_preserves_buffer(self):
        line = "jq --arg label --ra"
        self.session.send(line)
        self.session.send(self.session.trigger)
        self.session.expect(b"Enter the preceding option's argument")
        self.assertEqual(self.session.read_buffer(), (line, len(line)))
        self.assertFalse(self.executed.exists())
        self.assertEqual([json.loads(line) for line in self.calls.read_text().splitlines()], [["--help"]])


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ReviewScreenTests(TerminalTestCase):
    def test_repeated_unicode_search_cancel_then_insert_preserves_history(self):
        shell = self.start()
        line = 'rsync "café folder" --ar'
        initial = shell.pending(line)
        shell.open_menu()
        shell.keys("/", "C-u")
        shell.text("archive")
        shell.keys("Enter")
        cancelled = shell.cancel("C-c")
        self.assertEqual((cancelled.cells, cancelled.x, cancelled.y),
                         (initial.cells, initial.x, initial.y))
        self.assertEqual(cancelled.history_markers(), HISTORY)
        shell.open_menu()
        shell.keys("Enter")
        expected = 'rsync "café folder" --archive '
        restored = shell.wait_for(lambda state: state.alternate == 0 and
                                 (PROMPT + expected).rstrip() in state.cells)
        self.assertEqual(restored.history_markers(), HISTORY)
        self.assertFalse(shell.executed.exists())
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))


if __name__ == "__main__":
    unittest.main()
