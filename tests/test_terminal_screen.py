"""Verify real Bash/curses screen cells and scrollback with isolated tmux servers."""

from dataclasses import dataclass
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPT = "screen-test $ "
WRAPPED_LINE = 'rsync "' + "wrapped-path-" * 17 + '" --ar'
HISTORY = tuple(f"HISTORY-{index:03}" for index in range(1, 81))
TMUX_AVAILABLE = sys.platform.startswith("linux") and shutil.which("tmux") is not None


@dataclass(frozen=True)
class ScreenState:
    """Rendered cells, history, and zero-based cursor coordinates at one instant."""

    columns: int
    rows: int
    x: int
    y: int
    alternate: int
    cells: tuple
    history: tuple

    def history_markers(self):
        """Return numbered output independently of viewport reflow and height."""
        return tuple(line for line in self.history + self.cells if line in HISTORY)


class TmuxShell:
    """Own a private tmux socket and shell; never attach to an existing server."""

    def __init__(self, folder, runtime=None, profile_directory=None):
        self.folder = Path(folder)
        runtime = Path(runtime) if runtime is not None else ROOT
        self.socket = self.folder / "tmux.sock"
        self.buffer_file = self.folder / "buffer"
        self.executed = self.folder / "executed"
        config = self.folder / "tmux.conf"
        config.write_text("set -g status off\nset -g history-limit 10000\n"
                          "set -g default-terminal tmux-256color\n")
        self.command = ["tmux", "-S", str(self.socket), "-f", str(config)]
        self.environment = {"PATH": "/usr/bin:/bin", "HOME": str(self.folder),
                            "LC_ALL": "C.UTF-8", "TERM": "tmux-256color"}
        rcfile = self.folder / "bashrc"
        rcfile.write_text(
            f"PS1={shlex.quote(PROMPT)}; PS2='> '; set +o history\n"
            + "source " + shlex.quote(str(runtime / "bash/interactive-help.bash")) + "\n"
            + "rsync() { printf executed > " + shlex.quote(str(self.executed)) + "; }\n"
            + "_screen_snapshot() { printf '%s\\0%s\\0' \"$READLINE_POINT\" \"$READLINE_LINE\" > "
            + shlex.quote(str(self.buffer_file)) + "; }\n"
            + "bind -x '\"\\C-x\\C-g\":_screen_snapshot'\n"
            + "printf '\\033[H\\033[2J'\n"
        )
        environment = [
            "env", "-i", "PATH=/usr/bin:/bin", "TERM=tmux-256color", "LC_ALL=C.UTF-8",
            "HOME=" + str(self.folder), "INPUTRC=/dev/null", "CLI_HELP_DISCOVERY=off",
            "CLI_HELP_PYTHON=" + sys.executable, "PYTHONDONTWRITEBYTECODE=1",
        ]
        if profile_directory is not None:
            environment.append("CLI_HELP_PROFILES=" + str(profile_directory))
        # --norc also suppresses the system interactive startup file. Bootstrap
        # only the inspected test rcfile, before any pending input is supplied.
        shell = shlex.join(environment + ["/bin/bash", "--noprofile", "--norc", "-i"])
        try:
            self.tmux("new-session", "-d", "-s", "screen-test", "-x", "100", "-y", "24", shell)
            self.text("source " + shlex.quote(str(rcfile)))
            self.keys("Enter")
            self.wait_for(lambda state: state.cells[0] == PROMPT.rstrip())
        except BaseException:
            self.close()
            raise

    def tmux(self, *arguments, check=True):
        """Run one bounded command against this test's private server."""
        return subprocess.run(self.command + list(arguments), check=check,
                              capture_output=True, text=True, timeout=5, env=self.environment).stdout

    def close(self):
        """Stop the private server without accepting any pending command."""
        self.tmux("kill-server", check=False)

    def text(self, value):
        """Type literal text; control keys must use keys()."""
        self.tmux("send-keys", "-t", "screen-test:0.0", "-l", "--", value)

    def keys(self, *keys):
        self.tmux("send-keys", "-t", "screen-test:0.0", *keys)

    def capture(self):
        """Read tmux's rendered cells and complete retained history, not raw ANSI."""
        values = self.tmux("display-message", "-p", "-t", "screen-test:0.0",
                           "#{pane_width},#{pane_height},#{cursor_x},#{cursor_y},#{alternate_on}")
        columns, rows, x, y, alternate = map(int, values.strip().split(","))
        lines = tuple(self.tmux("capture-pane", "-p", "-S", "-", "-t", "screen-test:0.0").splitlines())
        return ScreenState(columns, rows, x, y, alternate, lines[-rows:], lines[:-rows])

    def wait_for(self, predicate):
        """Require matching terminal state to remain stable across redraw polling."""
        deadline = time.monotonic() + 8
        previous = None
        stable_since = time.monotonic()
        while time.monotonic() < deadline:
            current = self.capture()
            if current != previous or not predicate(current):
                stable_since = time.monotonic()
            elif time.monotonic() - stable_since >= 0.2:
                return current
            previous = current
            time.sleep(0.05)
        raise AssertionError(f"Terminal did not settle: {current!r}")

    def pending(self, line, bottom=True):
        """Position pending input after numbered output, or at the top control row."""
        if bottom:
            self.text("printf 'HISTORY-%03d\\n' {1..80}")
            self.keys("Enter")
            self.wait_for(lambda state: state.history_markers() == HISTORY and state.y == 23)
        self.text(line)
        return self.wait_for(lambda state: "--ar" in "".join(state.cells))

    def open_menu(self, keys=("Escape", "h")):
        self.keys(*keys)
        return self.wait_for(lambda state: state.alternate == 1 and "Interactive help" in state.cells[0])

    def cancel(self, key="Escape"):
        self.keys(key)
        return self.wait_for(lambda state: state.alternate == 0)

    def resize(self, columns, rows):
        self.tmux("resize-window", "-t", "screen-test:0", "-x", str(columns), "-y", str(rows))
        # Curses polls dimensions every 150 ms; allow at least one polling cycle.
        time.sleep(0.2)
        return self.wait_for(lambda state: (state.columns, state.rows) == (columns, rows))

    def read_buffer(self):
        """Inspect Readline only after visual assertions: bind -x itself redraws."""
        self.buffer_file.unlink(missing_ok=True)
        self.keys("C-x", "C-g")
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.buffer_file.exists():
                fields = self.buffer_file.read_bytes().split(b"\0")
                if len(fields) == 3:
                    return fields[1].decode(), int(fields[0])
            time.sleep(0.02)
        raise AssertionError("Readline buffer snapshot was not completed")


class TerminalTestCase(unittest.TestCase):
    def start(self):
        """Register cleanup before returning an isolated interactive shell."""
        folder = tempfile.TemporaryDirectory(prefix="cli-help-screen-")
        self.addCleanup(folder.cleanup)
        shell = TmuxShell(folder.name)
        self.addCleanup(shell.close)
        return shell


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ScreenTests(TerminalTestCase):
    def test_top_and_bottom_cancellation_restore_cells_cursor_and_history(self):
        for bottom in (False, True):
            for line in ("rsync --ar", WRAPPED_LINE):
                for cancel_key in ("Escape", "C-c"):
                    with self.subTest(bottom=bottom, wrapped=line == WRAPPED_LINE, key=cancel_key):
                        shell = self.start()
                        before = shell.pending(line, bottom)
                        if bottom:
                            self.assertEqual(before.y, 23)
                        menu = shell.open_menu()
                        self.assertIn("enter insert", menu.cells[-1])
                        self.assertEqual(shell.cancel(cancel_key), before)
                        shell.open_menu()
                        self.assertEqual(shell.cancel(), before)
                        self.assertEqual(shell.read_buffer(), (line, len(line)))
                        self.assertFalse(shell.executed.exists())

    def test_insertion_across_bottom_margin_preserves_scrollback(self):
        shell = self.start()
        # End three columns before the margin; --archive adds six characters.
        line = 'rsync "' + "x" * (97 - len(PROMPT) - len('rsync "" --ar')) + '" --ar'
        before = shell.pending(line)
        self.assertEqual((before.x, before.y), (97, 23))
        shell.open_menu()
        shell.keys("Enter")
        after = shell.wait_for(lambda state: state.alternate == 0)
        expected = line[:-4] + "--archive "
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual("".join(after.cells[-2:]), (PROMPT + expected).rstrip())
        self.assertEqual((after.x, after.y), (3, 23))
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_resize_below_minimum_and_back_restores_primary_screen(self):
        shell = self.start()
        before = shell.pending(WRAPPED_LINE)
        shell.open_menu()
        small = shell.resize(40, 10)
        self.assertIn("Resize to at least", small.cells[0])
        restored = shell.resize(100, 24)
        self.assertIn("Interactive help", restored.cells[0])
        self.assertEqual(shell.cancel(), before)
        self.assertFalse(shell.executed.exists())


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class WrappedResizeTests(TerminalTestCase):
    """Verify stable redisplay and exact input after shrinking wrapped commands."""

    def setUp(self):
        self.shell = self.start()
        self.shell.pending(WRAPPED_LINE)
        self.shell.open_menu()
        resized = self.shell.resize(60, 16)
        self.assertIn("Interactive help", resized.cells[0])
        self.first_exit = self.shell.cancel()
        self.shell.open_menu()
        self.second_exit = self.shell.cancel()
        # Buffer and execution checks are independent of rendered comparisons.
        self.assertEqual(self.first_exit.history_markers(), HISTORY)
        self.assertEqual(self.second_exit.history_markers(), HISTORY)
        self.assertEqual(self.shell.read_buffer(), (WRAPPED_LINE, len(WRAPPED_LINE)))
        self.assertFalse(self.shell.executed.exists())

    def test_wrapped_shrink_reopen_preserves_rendered_screen(self):
        """Readline redraw after a size change remains stable on reopening."""
        self.assertEqual(self.second_exit, self.first_exit)

    def test_ctrl_l_recovers_one_prompt_and_retains_scrollback(self):
        self.shell.keys("C-l")
        recovered = self.shell.wait_for(lambda state: state.cells[0].startswith(PROMPT))
        expected = PROMPT + WRAPPED_LINE
        expected_rows = tuple(expected[index:index + 60] for index in range(0, len(expected), 60))
        self.assertEqual(recovered.cells[:len(expected_rows)], expected_rows)
        self.assertTrue(all(not line for line in recovered.cells[len(expected_rows):]))
        self.assertEqual((recovered.x, recovered.y), (len(expected) % 60, len(expected_rows) - 1))
        self.assertEqual(recovered.history_markers(), HISTORY)
        self.assertEqual(self.shell.read_buffer(), (WRAPPED_LINE, len(WRAPPED_LINE)))
        self.assertFalse(self.shell.executed.exists())


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ResizeBindingTests(TerminalTestCase):
    def test_resize_with_custom_binding_unicode_midline_and_rebound_control_l(self):
        for accept in (False, True):
            with self.subTest(accept=accept):
                shell = self.start()
                shell.text("CLI_HELP_KEY='\\C-x\\C-h'; cli_help_bind; bind '\"\\C-l\":forward-char'")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                prefix = 'rsync "日本 café ' + 'wrapped-' * 25 + '" --ar'
                suffix = ' "target dir"'
                shell.pending(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                shell.open_menu(("C-x", "C-h"))
                shell.resize(60, 16)
                after = shell.cancel("Enter" if accept else "C-c")
                expected_prefix = prefix[:-4] + '--archive ' if accept else prefix
                expected = expected_prefix + (suffix[1:] if accept else suffix)
                # Recovery invokes the function directly, independent of the
                # user's Ctrl-L binding, and retains all earlier output.
                self.assertTrue(after.cells[0].startswith(PROMPT))
                self.assertEqual(sum(PROMPT in row for row in after.cells), 1)
                self.assertEqual(after.history_markers(), HISTORY)
                if accept:
                    # Insertion leaves point at the quoted positional token;
                    # reopen from the preceding option, an editable location.
                    shell.keys("Left")
                    after = shell.wait_for(lambda state: state.alternate == 0)
                shell.open_menu(("C-x", "C-h"))
                self.assertEqual(shell.cancel(), after)
                self.assertEqual(shell.read_buffer(), (expected, len(expected_prefix) - int(accept)))
                self.assertFalse(shell.executed.exists())
