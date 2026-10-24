"""Rendered Bash evidence for private driver reports and static-only explanations."""

import json
import shlex
import sys
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, ROOT
from test_workflow_review import SECRET, static_profile
import test_workflow_terminal as workflow_terminal


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class DiagnosticReviewScreenTests(TerminalTestCase):
    pending = workflow_terminal.WorkflowScreenTests.pending
    assert_restored = workflow_terminal.WorkflowScreenTests.assert_restored

    def configure(self, shell, command):
        """Bind passive explanation in a private shell without accepting pending input."""
        profiles = shell.folder / "profiles"
        profiles.mkdir()
        (profiles / "fixture.json").write_text(json.dumps(static_profile(command)))
        drivers = shell.folder / "drivers"
        drivers.mkdir()
        (drivers / "fixture.json").write_text(json.dumps({"command": "fixture", "paths": [{
            "command": [], "help": ["--help", "--token=" + SECRET, "--password", SECRET],
            "man": "private-" + SECRET}]}))
        report = shell.folder / "explanation.json"
        cache = shell.folder / "absent-cache"
        callback = ('_review_explain() { CLI_HELP_LINE="$READLINE_LINE" CLI_HELP_POINT="$READLINE_POINT" '
                    + shlex.quote(sys.executable) + " -B " + shlex.quote(str(ROOT / "cli_help/main.py"))
                    + " --explain > " + shlex.quote(str(report)) + "; }; ")
        shell.text(command[0] + "() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; "
                   + "export CLI_HELP_PROFILES=" + shlex.quote(str(profiles))
                   + " CLI_HELP_DRIVERS=" + shlex.quote(str(drivers))
                   + " CLI_HELP_CACHE_DIR=" + shlex.quote(str(cache)) + "; "
                   + callback + "bind -x " + shlex.quote('"\\C-x\\C-e":_review_explain'))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        return report, cache

    def inspect_pending(self, shell, before, report):
        """Check rendered preservation before using the logical buffer snapshot."""
        shell.keys("C-x", "C-e")
        state = shell.wait_for(lambda value: report.is_file() and report.read_text().endswith("\n") and value == before)
        self.assertEqual(state, before)
        self.assertEqual(state.alternate, 0)
        return json.loads(report.read_text())

    def test_static_only_explanation_preserves_cursor_resize_and_insertion(self):
        shell = self.start()
        report, cache = self.configure(shell, ["echo", "review-leaf"])
        marked = "echo review-leaf --fl@  'café note'"
        _, _, before = self.pending(shell, marked)
        explanation = self.inspect_pending(shell, before, report)
        self.assertEqual(explanation["status"], "ready")
        self.assertEqual(explanation["route"]["kind"], "profile_only")
        self.assert_restored(shell, marked)
        self.assertIn("echo review-leaf", shell.open_menu().cells[0])
        shell.cancel("C-c")
        self.assert_restored(shell, marked)
        shell.open_menu()
        shell.resize(40, 10)
        shell.resize(100, 24)
        shell.keys("Enter")
        self.assert_restored(shell, "echo review-leaf --flag @ 'café note'")
        self.assertFalse(cache.exists())

    def test_private_route_constants_are_omitted_from_actual_bash_diagnostic(self):
        shell = self.start()
        report, cache = self.configure(shell, ["fixture"])
        marked = "fixture --fl@  '" + SECRET + " café'"
        _, _, before = self.pending(shell, marked)
        explanation = self.inspect_pending(shell, before, report)
        self.assertEqual(explanation["status"], "ready")
        self.assertEqual(explanation["route"]["kind"], "configured")
        self.assertTrue(explanation["route"]["help_arguments_redacted"])
        self.assertTrue(explanation["route"]["manual_redacted"])
        self.assertNotIn(SECRET, report.read_text())
        self.assert_restored(shell, marked)
        self.assertFalse(cache.exists())


if __name__ == "__main__":
    unittest.main()
