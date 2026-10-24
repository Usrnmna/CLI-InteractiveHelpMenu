"""Rendered Bash evidence for workflow routes, inherited arity, and GNU expressions."""

import json
import shlex
import sys
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT
from test_workflow_baseline import profile_for


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class WorkflowScreenTests(TerminalTestCase):
    def configure(self, shell, command, live=False):
        """Use isolated captured metadata or one instrumented fixed-help executable."""
        profile = profile_for(command)
        name = command.split()[0]
        if live:
            from test_workflow_baseline import CASES, FIXTURES
            case = next(case for case in CASES if case["command"] == command)
            text = (FIXTURES / case["fixture"]).read_text()
            executable = shell.folder / name
            log = shell.folder / "probes.jsonl"
            executable.write_text("#!" + sys.executable + "\nimport json,sys\nfrom pathlib import Path\n"
                                  + "args=sys.argv[1:]\n"
                                  + "with open(" + repr(str(log)) + ", 'a') as stream: stream.write(json.dumps(args)+'\\n')\n"
                                  + "if args == ['help', 'exec']: print(" + repr(text) + ")\n"
                                  + "else: Path(" + repr(str(shell.executed)) + ").write_text('unexpected dispatch')\n")
            executable.chmod(0o755)
            environment = "export PATH=" + shlex.quote(str(shell.folder)) + ":/usr/bin:/bin CLI_HELP_DISCOVERY=auto CLI_HELP_CACHE_DIR=" + shlex.quote(str(shell.folder / "cache"))
        else:
            folder = shell.folder / "profiles"
            folder.mkdir()
            (folder / "fixture.json").write_text(json.dumps(profile))
            environment = "export CLI_HELP_PROFILES=" + shlex.quote(str(folder))
        # An accidental acceptance of the pending command is recorded without
        # starting a third-party workload; discovery excludes shell functions.
        shell.text(name + "() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; "
                   + environment + "; export CLI_HELP_DRIVERS=" + shlex.quote(str(ROOT / "config/drivers.example")))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())

    def pending(self, shell, marked):
        """Position a character cursor after generating numbered scrollback."""
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.history_markers() == HISTORY)
        point = marked.index("@")
        line = marked.replace("@", "")
        shell.text(line)
        shell.wait_for(lambda state: line in "".join(state.cells))
        if point < len(line):
            shell.keys(*(["Left"] * (len(line) - point)))
        return line, point, shell.wait_for(lambda state: state.x == (len(PROMPT) + point) % state.columns)

    def assert_restored(self, shell, marked):
        """Require rendered cells, cursor, alternate-screen restoration, and history."""
        point = marked.index("@")
        line = marked.replace("@", "")
        state = shell.wait_for(lambda state: state.alternate == 0 and line.rstrip() in "".join(state.cells))
        self.assertEqual(state.x, (len(PROMPT) + point) % state.columns)
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (line, point))
        self.assertFalse(shell.executed.exists())
        return state

    def test_compose_run_midline_service_boundary_cancel_resize_and_reopen(self):
        shell = self.start()
        self.configure(shell, "docker compose run")
        pending = "docker compose -f 'café.yml' run --rm@ web sh -c 'printf test'"
        _, _, before = self.pending(shell, pending)
        self.assertIn("docker compose run", shell.open_menu().cells[0])
        self.assertEqual(shell.cancel("C-c"), before)
        shell.open_menu()
        shell.resize(30, 8)
        shell.resize(100, 24)
        shell.keys("Enter")
        self.assert_restored(shell, "docker compose -f 'café.yml' run --rm @web sh -c 'printf test'")

    def test_github_repeated_filters_and_json_preserve_literal_suffix(self):
        shell = self.start()
        self.configure(shell, "gh issue list")
        self.pending(shell, "gh issue -R o/r list --label bug --label=café --json number,title --lim@ 20")
        self.assertIn("gh issue list", shell.open_menu().cells[0])
        shell.cancel()
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, "gh issue -R o/r list --label bug --label=café --json number,title --limit @20")

    def test_sed_expression_literal_insertion_and_attached_value_rejection(self):
        shell = self.start()
        self.configure(shell, "sed")
        self.pending(shell, "sed -e 's/a b/café/g' --qu@  'source file'")
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, "sed -e 's/a b/café/g' --quiet @ 'source file'")
        shell.keys("C-e", "C-u")
        line = "sed -i.bak file"
        shell.text(line)
        shell.keys(*(["Left"] * len(".bak file")))
        shell.keys("Escape", "h")
        state = shell.wait_for(lambda value: value.alternate == 0 and "cursor_in_value" in " ".join(value.cells))
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(state.x, len(PROMPT + "sed -i"))
        self.assertEqual(shell.read_buffer(), (line, len("sed -i")))
        self.assertFalse(shell.executed.exists())

    def test_kubectl_live_fixed_help_warm_cache_and_child_separator(self):
        shell = self.start()
        self.configure(shell, "kubectl exec", live=True)
        pending = "kubectl exec pod --namespace demo -c app --tt@ -- sh --flag"
        _, _, before = self.pending(shell, pending)
        self.assertIn("kubectl exec", shell.open_menu().cells[0])
        self.assertEqual(shell.cancel(), before)
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, "kubectl exec pod --namespace demo -c app --tty @-- sh --flag")
        probes = [json.loads(line) for line in (shell.folder / "probes.jsonl").read_text().splitlines()]
        self.assertEqual(probes, [["help", "exec"]])
        shell.keys("C-e")
        shell.keys("Escape", "h")
        state = shell.wait_for(lambda value: value.alternate == 0 and "end_of_options" in " ".join(value.cells))
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(state.x, len(PROMPT + pending.replace("--tt@", "--tty")))
        self.assertFalse(shell.executed.exists())


if __name__ == "__main__":
    unittest.main()
