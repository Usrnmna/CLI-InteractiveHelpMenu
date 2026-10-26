"""Exercise numerical guidance and inert Readline buffers in a real Linux PTY.

tmux supplies rendered cells and a private terminal, not human visual acceptance.
Only harness control lines are submitted to Bash; pending buffers are discarded.
"""

from copy import deepcopy
import json
import os
from pathlib import Path
import shlex
import signal
import sys
import tempfile
import unittest

from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TmuxShell
from test_value_semantics import contract, synthetic_node
from core import validate_profile

if sys.platform.startswith("linux"):
    import termios


def specimen():
    """Extend the labeled synthetic contract without asserting target facts."""
    profile = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
    profile["description"] = "Native specimen: cafe\u0301 界; no target program is executed"
    options = profile["categories"][0]["options"]
    long_value = deepcopy(options[0])
    long_value.update(flag="--very-long-numerical-limit", argument="TIME_AMOUNT_PLACEHOLDER_" * 4,
                      summary="Long synthetic duration cafe\u0301 界",
                      detail="\n".join([f"Explanation line {i}: cafe\u0301 界 and retained source text." for i in range(12)]
                                       + ["END_NATIVE_DETAIL"]))
    unknown = synthetic_node("unresolved", meaning="Unconfirmed specimen scale",
        review={"status": "source_derived", "references": [{"source": "synthetic:native", "locator": "unknown scale"}]},
        bare={"state": "unverified", "reason": "No default scale was established"},
        forms=[{"id": "expression", "notation": "expression", "syntax": "EXPR", "grammar": "Unconfirmed specimen grammar"}],
        investigation="Determine the specimen version and scale")
    options.extend([long_value,
        {"flag": "--uncertain", "argument": "EXPR", "summary": "Unresolved specimen", "value_semantics": contract(unknown)},
        {"flag": "--amount=", "argument": "N", "summary": "Synthetic equals operand"},
        {"flag": "-o", "argument": "PATH", "argument_style": "attached_only", "summary": "Synthetic attached operand"},
        {"flag": "--maybe", "argument": "N", "argument_optional": True, "optional_value_kind": "nonnegative_integer", "summary": "Synthetic optional integer"}])
    profile["categories"].append({"name": "Other", "options": [{"flag": "--other", "summary": "Another inert flag"}]})
    return profile


@unittest.skipUnless(TMUX_AVAILABLE, "Native numerical terminal checks require Linux and tmux")
class NativeNumericalTerminalTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-native-terminal-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        profiles = self.folder / "profiles"
        profiles.mkdir()
        profile = specimen()
        validate_profile(profile, profiles / "specimen.json")
        (profiles / "specimen.json").write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        self.shell = TmuxShell(self.folder, profile_directory=profiles)
        self.addCleanup(self.shell.close)
        self.marker = self.folder / "pending-executed"
        self.control("synthetic-contract() { printf executed > " + shlex.quote(str(self.marker)) + "; }")

    def control(self, command):
        """Submit an inspected harness operation only while Readline is empty."""
        self.shell.text(command)
        self.shell.keys("Enter")
        return self.shell.wait_for(lambda state: state.alternate == 0 and state.cells[state.y] == PROMPT.rstrip())

    def pending(self, line, point=None):
        """Type inert text and optionally position the character cursor."""
        self.shell.text(line)
        if point is not None:
            # Readline movement can group combining characters. Use an ASCII
            # span when possible; the snapshot still checks character offsets.
            if line[point:].isascii():
                self.shell.keys("C-e", *(["C-b"] * (len(line) - point)))
            else:
                self.shell.keys("C-a", *(["C-f"] * point))
        return self.shell.wait_for(lambda state: state.alternate == 0 and "synthetic-contract" in "".join(state.cells))

    def attributes(self):
        """Read this private pane's actual termios attributes without changing them."""
        tty = self.shell.tmux("display-message", "-p", "-t", "screen-test:0.0", "#{pane_tty}").strip()
        descriptor = os.open(tty, os.O_RDWR | os.O_NOCTTY)
        try:
            return termios.tcgetattr(descriptor)
        finally:
            os.close(descriptor)

    def search(self, query):
        self.shell.keys("/", "C-u")
        self.shell.text(query)
        self.shell.keys("Enter")
        return self.shell.wait_for(lambda state: state.alternate == 1 and "Filter: " + query in "".join(state.cells))

    def discard(self):
        """Clear pending text before any subsequent harness control line."""
        self.shell.keys("C-a", "C-k")
        self.shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        self.assertFalse(self.marker.exists())

    def test_units_suffixes_special_meanings_and_complete_details_are_reachable(self):
        self.pending("synthetic-contract --")
        menu = self.shell.open_menu()
        self.assertIn("seconds", "\n".join(menu.cells))
        for query in ("ms", "Unlimited wait", "TIME_AMOUNT_PLACEHOLDER"):
            with self.subTest(query=query):
                matched = self.search(query)
                self.assertNotIn("No matches", "\n".join(matched.cells))
        self.shell.text("]" * 100)
        end = self.shell.wait_for(lambda state: "END_NATIVE_DETAIL" in "\n".join(state.cells))
        self.assertIn("Details", "\n".join(end.cells))
        self.shell.cancel()
        self.assertEqual(self.shell.read_buffer(), ("synthetic-contract --", len("synthetic-contract --")))
        self.assertFalse(self.marker.exists())

    def test_minimum_width_resize_unicode_and_reopen_restore_terminal_and_buffer(self):
        line = "synthetic-contract 'cafe\u0301界' --del 'suffix file'"
        point = len(line) - len(" 'suffix file'")
        self.pending(line, point)
        before = self.attributes()
        self.shell.open_menu()
        minimum = self.shell.resize(60, 16)
        self.assertIn("seconds", "\n".join(minimum.cells))
        self.assertIn("Details", "\n".join(minimum.cells))
        small = self.shell.resize(40, 10)
        self.assertIn("Resize to at least", small.cells[0])
        self.shell.cancel("C-c")
        self.assertEqual(self.attributes(), before)
        self.assertEqual(self.shell.read_buffer(), (line, point))
        self.shell.resize(100, 24)
        self.shell.open_menu()
        self.shell.cancel()
        self.assertEqual(self.attributes(), before)
        self.assertEqual(self.shell.read_buffer(), (line, point))
        self.assertFalse(self.marker.exists())

    def test_literal_forms_and_optional_values_preserve_suffix_and_cursor(self):
        cases = [("--del", "--delay "), ("--amo", "--amount="), ("-o", "-o"), ("--may", "--maybe ")]
        for prefix, inserted in cases:
            with self.subTest(prefix=prefix):
                head = "synthetic-contract " + prefix
                suffix = " 'cafe\u0301界 file'"
                try:
                    self.pending(head + suffix, len(head))
                    self.shell.open_menu()
                    self.shell.cancel("Enter")
                    expected = "synthetic-contract " + inserted + (suffix[1:] if inserted.endswith(" ") else suffix)
                    self.assertEqual(self.shell.read_buffer(), (expected, len("synthetic-contract " + inserted)))
                finally:
                    self.discard()

    def test_expansions_operators_and_boundaries_never_evaluate_pending_text(self):
        location = shlex.quote(str(self.marker))
        payloads = [f"$(printf evaluated > {location})", f"`printf evaluated > {location}`",
                    f"; printf evaluated > {location}", f"| printf evaluated > {location}", f"> {location}"]
        for payload in payloads:
            with self.subTest(payload=payload.split()[0]):
                line = "synthetic-contract " + payload + " --del"
                self.pending(line)
                self.shell.keys("Escape", "h")
                self.shell.wait_for(lambda state: state.alternate == 0 and "interactive-help: unsupported_shell_syntax:" in "\n".join(state.cells))
                self.assertEqual(self.shell.read_buffer(), (line, len(line)))
                self.discard()
        line = "synthetic-contract -- child --del"
        self.pending(line)
        self.shell.keys("Escape", "h")
        self.shell.wait_for(lambda state: "interactive-help:" in "\n".join(state.cells))
        self.assertEqual(self.shell.read_buffer(), (line, len(line)))
        self.assertFalse(self.marker.exists())

    def test_unresolved_guidance_and_search_cancellation_remain_nonfatal(self):
        line = "synthetic-contract --"
        self.pending(line)
        self.shell.open_menu()
        matched = self.search("specimen version")
        self.assertIn("not verified", "\n".join(matched.cells))
        self.shell.keys("/")
        self.shell.text("no-such-entry")
        self.shell.keys("Escape")
        restored = self.shell.wait_for(lambda state: "Filter: specimen version" in "\n".join(state.cells))
        self.assertIn("--uncertain", "\n".join(restored.cells))
        self.shell.cancel()
        self.assertEqual(self.shell.read_buffer(), (line, len(line)))

    def test_external_sigint_restores_termios_and_allows_reopening(self):
        line = "synthetic-contract --del"
        self.pending(line)
        before = self.attributes()
        self.shell.open_menu()
        shell_pid = int(self.shell.tmux("display-message", "-p", "-t", "screen-test:0.0", "#{pane_pid}").strip())
        pending = [shell_pid]
        helpers = []
        while pending:
            pid = pending.pop()
            children = Path(f"/proc/{pid}/task/{pid}/children")
            if not children.exists():
                continue
            for child in map(int, children.read_text().split()):
                pending.append(child)
                arguments = Path(f"/proc/{child}/cmdline").read_bytes().split(b"\0")
                if str(ROOT / "cli_help/main.py").encode() in arguments and b"--bash" in arguments:
                    helpers.append(child)
        self.assertEqual(len(helpers), 1)
        os.kill(helpers[0], signal.SIGINT)
        self.shell.wait_for(lambda state: state.alternate == 0)
        self.assertEqual(self.attributes(), before)
        self.assertEqual(self.shell.read_buffer(), (line, len(line)))
        self.shell.open_menu()
        self.shell.cancel()
        self.assertFalse(self.marker.exists())

    def test_unrelated_bindings_and_shell_options_survive_widget_and_unbind(self):
        before, after = self.folder / "options-before", self.folder / "options-after"
        bindings = self.folder / "remaining-bindings"
        self.control("bind '\"\\C-l\":forward-char'; set +o > " + shlex.quote(str(before)))
        self.pending("synthetic-contract --del")
        self.shell.open_menu()
        self.shell.cancel()
        self.discard()
        self.control("set +o > " + shlex.quote(str(after)) + "; cli_help_unbind; "
                     "{ bind -p; bind -s; bind -X; } > " + shlex.quote(str(bindings)))
        self.assertEqual(before.read_bytes(), after.read_bytes())
        text = bindings.read_text()
        self.assertIn('"\\C-l": forward-char', text)
        self.assertNotIn("\\e[988~", text)
        self.assertNotIn("\\e[989~", text)
        self.assertFalse(self.marker.exists())

    def test_real_authoring_preview_inspects_without_saving_and_restores_terminal(self):
        from manual_import import ManualCollection, atomic_json
        collection = self.folder / "authored"
        with ManualCollection(collection) as writer:
            writer.save(specimen(), "synthetic-contract")
        report = collection / "scan-report.json"
        atomic_json(report, {"schema_version": 1, "records": [
            {"command": ["synthetic-contract"], "status": "needs_adjustment", "generated": True}]})
        before = {path.relative_to(collection): path.read_bytes() for path in collection.rglob("*") if path.is_file()}
        attributes = self.attributes()
        # This is a harness-control invocation, with an empty pending buffer.
        self.shell.text(shlex.join([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--review-report", str(report)]))
        self.shell.keys("Enter")
        self.shell.wait_for(lambda state: "Review: number" in "\n".join(state.cells))
        self.shell.text("1")
        self.shell.keys("Enter")
        self.shell.wait_for(lambda state: "Entry:" in "\n".join(state.cells))
        self.shell.text("p")
        self.shell.keys("Enter")
        preview = self.shell.wait_for(lambda state: state.alternate == 1 and "Help preview" in state.cells[0])
        self.assertIn("seconds", "\n".join(preview.cells))
        self.assertIn("enter inspect", preview.cells[-1])
        self.shell.keys("Enter")
        self.shell.wait_for(lambda state: state.alternate == 0 and "Preview selection only: --delay" in "\n".join(state.cells))
        self.shell.text("b")
        self.shell.keys("Enter")
        self.shell.wait_for(lambda state: "Review: number" in "\n".join(state.cells))
        self.shell.text("q")
        self.shell.keys("Enter")
        self.shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        after = {path.relative_to(collection): path.read_bytes() for path in collection.rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        self.assertEqual(self.attributes(), attributes)
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
