#!/usr/bin/env python3
"""Capture the five storyboarded Bash sessions using the checkout's adapter and a private tmux."""

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tempfile
import time

import capture_readme_media as media

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_terminal_screen import TmuxShell

OUTPUT = ROOT / "docs/assets/scenarios"
REPORT = ROOT / "tests/reports/scenario-demos"
SIZES = {"apt": (100, 26), "bash": (112, 36), "git": (80, 24), "rsync": (60, 16), "ffmpeg": (120, 30)}


@dataclass
class Frame:
    """A styled pane capture, its visible cursor and its exact text for independent checks."""
    ansi: str
    cells: tuple
    cursor: tuple
    menu: bool


class Recording:
    def __init__(self, name, shell):
        self.name = name
        self.shell = shell
        self.width, self.height = SIZES[name]
        self.evidence = []

    def frame(self, *required):
        """Compare the raw styled capture with tmux's plain cells and check the pane size."""
        state = self.shell.capture()
        assert (state.columns, state.rows) == (self.width, self.height)
        ansi = self.shell.tmux("capture-pane", "-ep", "-t", "screen-test:0.0")
        plain = tuple(line.rstrip() for line in re.sub(r"\x1b\[[0-9;]*m", "", ansi).splitlines())
        assert plain == state.cells, (plain, state.cells)
        visible = "\n".join(plain)
        for expected in required:
            assert expected in visible, (expected, visible)
        if state.alternate:
            assert "Shift+D change view" in plain[0]
        return Frame(ansi, plain, (state.x, state.y), bool(state.alternate))

    def picture(self, frame, caption, full=False):
        """Render captured cells with the repository palette and captions outside the pane."""
        screen = media.TerminalScreen(self.width, self.height)
        media.TerminalStream(screen).feed(frame.ansi.rstrip("\n").replace("\n", "\r\n"))
        assert tuple(line.rstrip() for line in screen.display) == frame.cells
        screen.cursor.x, screen.cursor.y = frame.cursor
        screen.cursor.hidden = frame.menu
        rows = self.height if full or frame.menu else min(self.height, frame.cursor[1] + 3)
        assert media.ImageFont.truetype(str(media.FONT), 18).getlength(caption) < self.width * 11
        title = f"{self.name.upper() if self.name == 'apt' else self.name}   {self.width}×{self.height}   checkout"
        return media.render(screen, title, caption, stop_row=rows)

    def still(self, slug, caption, *required):
        """Write one numbered PNG and retain the original cells for its verification record."""
        frame = self.frame(*required)
        filename = f"{self.name}-{slug}.png"
        self.picture(frame, caption).save(OUTPUT / filename)
        self.evidence.append(dict(file=filename, caption=caption, cells=frame.cells, cursor=frame.cursor))
        return frame

    def pending(self, line, point):
        """Verify the drawn prompt and the actual Readline buffer and cursor without executing it."""
        state = self.shell.wait_for(lambda s: not s.alternate and s.cells[s.y] == ("demo $ " + line).rstrip()
                                   and s.x == len("demo $ ") + point)
        assert self.shell.read_buffer() == (line, point)
        assert not self.shell.executed.exists()
        self.evidence.append(dict(pending=line, point=point, terminal_cursor=[state.x, state.y]))

    def select(self, label):
        """Move through a filtered option list until the exact visible declaration is selected."""
        state = self.shell.capture()
        for _ in range(32):
            if state.selected_row.startswith("> " + label + " "):
                return
            old = state.selected_row
            self.shell.keys("Down")
            state = self.shell.wait_for(lambda s: s.selected_row != old)
        raise AssertionError(f"Unreachable option {label!r}: {state.cells!r}")


@contextmanager
def session(name):
    """Run one scenario in an isolated interactive Bash, retaining the final record on success."""
    with tempfile.TemporaryDirectory(prefix=f"menu-{name}-") as folder:
        shell = TmuxShell(folder)
        try:
            shell.resize(*SIZES[name])
            discovery = "auto" if name in ("apt", "bash") else "off"
            narrow = int(name == "rsync")
            shell.text(f"export CLI_HELP_DISCOVERY={discovery} CLI_HELP_NARROW_MENU={narrow}; PS1='demo $ '; clear")
            shell.keys("Enter")
            shell.wait_for(lambda s: s.cells[0] == "demo $")
            recording = Recording(name, shell)
            yield recording
            (REPORT / f"{name}.json").write_text(json.dumps(dict(size=SIZES[name], discovery=discovery,
                                                               frames=recording.evidence), indent=2) + "\n")
        finally:
            shell.close()


def apt(rec):
    """Complete an APT verb and a verb-specific flag around the same quoted operand."""
    s = rec.shell
    suffix = " 'graphviz'"
    s.text("apt ins" + suffix)
    s.keys(*["Left"] * len(suffix))
    rec.pending("apt ins" + suffix, len("apt ins"))
    rec.still("1-before", "1/4   Complete the verb before the quoted package name.", "apt ins 'graphviz'")
    s.open_menu()
    rec.select("install")
    rec.still("2-verb", "2/4   Alt-H → install    Complete the APT verb.", "> install [keyword]")
    s.keys("Enter")
    rec.pending("apt install" + suffix, len("apt install "))
    s.text("--sim ")
    s.keys("Left")
    s.open_menu()
    rec.select("--simulate")
    rec.still("3-simulate", "3/4   Alt-H → --simulate    Browse options specific to apt install.",
              "Interactive help | apt install", "> --simulate")
    s.keys("Enter")
    rec.pending("apt install --simulate" + suffix, len("apt install --simulate "))
    rec.still("4-after", "4/4   Enter    Bash keeps the quotes and the command is ready to edit.", "--simulate 'graphviz'")


def bash(rec):
    """Read Bash's installed timeout documentation and fill its argument at the prompt."""
    s = rec.shell
    s.text("builtin read ")
    s.open_menu()
    rec.select("-t timeout")
    rec.still("1-option", "1/3   Alt-H → -t timeout    Bash lists the argument beside its option.", "> -t timeout", "-d delim")
    s.keys("D")
    detailed = s.wait_for(lambda f: "Detailed" in f.cells[0])
    assert "within TIMEOUT seconds" in " ".join(detailed.detail_body)
    s.keys("D")
    expanded = s.wait_for(lambda f: "Expanded" in f.cells[0])
    assert expanded.detail_range[0] == 1
    rec.still("2-timeout", "2/3   Shift+D twice    Read the timeout, default, zero case and exit status together.",
              "within TIMEOUT seconds", "TMOUT", "If TIMEOUT is 0", "greater than 128", "> -t timeout")
    s.keys("Enter")
    rec.pending("builtin read -t ", len("builtin read -t "))
    s.text("5 reply")
    line = "builtin read -t 5 reply"
    rec.pending(line, len(line))
    rec.still("3-value", "3/3   The menu inserted -t. The user typed 5 seconds and the variable name reply.", line)


def git(rec):
    """Show a nested command's dependency and assemble the two switches in Bash."""
    s = rec.shell
    line = "git worktree list "
    s.text(line)
    s.open_menu()
    rec.still("1-scope", "1/4   Alt-H    Seven options belong to git worktree list.", "> --porcelain", "1/7")
    s.keys("Down", "D")
    s.wait_for(lambda f: "Detailed" in f.cells[0])
    rec.still("2-dependency", "2/4   ↓ and Shift+D    NUL-delimited fields require --porcelain.", "> -z ", "Requires --porcelain")
    s.keys("Up", "Enter")
    line += "--porcelain "
    rec.pending(line, len(line))
    rec.still("3-porcelain", "3/4   ↑ and Enter    Insert the stable output format first.", line.rstrip())
    s.open_menu()
    s.keys("Down")
    s.wait_for(lambda f: f.selected_row.startswith("> -z "))
    s.keys("Enter")
    line += "-z "
    rec.pending(line, len(line))
    rec.still("4-final", "4/4   Alt-H → -z → Enter    Both switches are on the pending line.", line.rstrip())


def ffmpeg(rec):
    """Page through codec parameters and prove cancellation restores the midline cursor."""
    s = rec.shell
    prefix, suffix = "ffmpeg ", " 'review clip.mp4'"
    s.text(prefix + suffix)
    s.keys(*["Left"] * len(suffix))
    rec.pending(prefix + suffix, len(prefix))
    s.open_menu()
    s.keys(*["Right"] * 13)
    s.wait_for(lambda f: f.selected_row.startswith("> -alpha_mode "))
    rec.still("1-first", "1/4   Alt-H → Codec parameters    Start at the first of 92 entries.", "> -alpha_mode", "1/92")
    s.keys("PageDown")
    page = s.wait_for(lambda f: f.selected_row and not f.selected_row.startswith("> -alpha_mode "))
    label = page.selected_row.split()[1]
    count = re.search(r"(\d+)/92$", page.cells[3])[1]
    assert 1 < int(count) < 92
    rec.still("2-page", f"2/4   PageDown    The next page selects {label}, entry {count} of 92.", "> " + label + " ", count + "/92")
    s.keys("End")
    s.wait_for(lambda f: f.selected_row.startswith("> -trellis "))
    rec.still("3-last", "3/4   End    Reach the final codec parameter in one keystroke.", "> -trellis", "92/92")
    s.cancel()
    rec.pending(prefix + suffix, len(prefix))
    rec.still("4-restored", "4/4   Esc returns to the edit    The cursor and quoted filename are restored.", suffix)


def rsync(rec):
    """Measure the live selected-row animation and encode its complete two-second opening hold."""
    s = rec.shell
    scenes = []

    def add(frame, caption, ms):
        scenes.append((frame, caption, ms))

    s.text("rsync ")
    rec.pending("rsync ", 6)
    add(rec.frame("demo $ rsync"), "Alt-H    Open help on the pending rsync command.", 1000)
    s.open_menu()
    s.keys(*["Down"] * 6)
    s.wait_for(lambda f: any(v.startswith("> Network") for v in f.cells))
    add(rec.frame("> Network"), "↓ to Network    Choose the transfer settings.", 1000)
    s.keys("Right")
    s.wait_for(lambda f: any(v.startswith("> --compress") for v in f.cells))
    add(rec.frame("> --compress"), "→ options    Move down to the bandwidth limit.", 900)

    s.keys("Down")
    motion = []
    previous = None
    start = time.monotonic()
    while time.monotonic() - start < 8:
        ansi = s.tmux("capture-pane", "-ep", "-t", "screen-test:0.0")
        cells = tuple(v.rstrip() for v in re.sub(r"\x1b\[[0-9;]*m", "", ansi).splitlines())
        row = next((i for i, v in enumerate(cells) if v.startswith("> --bwlimit=RATE")), None)
        if row is not None and previous != cells[row]:
            motion.append((time.monotonic(), Frame(ansi, cells, (0, 0), True)))
            previous = cells[row]
            if previous.endswith("KiB/s)"):
                break
        time.sleep(.012)
    assert len(motion) >= 3 and motion[-1][1].cells[row].endswith("KiB/s)")
    first = motion[0][1].cells
    assert first[row].endswith("…")
    column = first[row].index("Limit bandwidth")
    elapsed = [round((ts - motion[0][0]) * 1000) for ts, _ in motion]
    assert 1950 <= elapsed[1] <= 2100, elapsed
    for i, (_, frame) in enumerate(motion):
        assert frame.cells[:row] + frame.cells[row+1:] == first[:row] + first[row+1:]
        assert frame.cells[row][:column] == first[row][:column]
        # GIF delay is quantized to centiseconds; keep the configured opening hold exact.
        delay = 2000 if i == 0 else 1000 if i == len(motion)-1 else round((elapsed[i+1]-elapsed[i])/10)*10
        add(frame, "Bare rate in KiB/s    Only the clipped summary moves.", delay)
    time.sleep(1)
    assert rec.frame().cells == motion[-1][1].cells
    s.keys("Enter")
    prefix = "rsync --bwlimit="
    rec.pending(prefix, len(prefix))
    add(rec.frame(prefix), "Enter    Insert the flag and leave the cursor after =.", 900)
    line = prefix + "5000 'project files/' backup/"
    s.text(line[len(prefix):])
    rec.pending(line, len(line))
    add(rec.frame(line), "Type 5000    The limit is 5000 KiB/s.", 2100)
    pictures = [rec.picture(frame, caption, full=True) for frame, caption, _ in scenes]
    delays = [ms for _, _, ms in scenes]
    filename = OUTPUT / "rsync-bandwidth.gif"
    pictures[0].save(filename, save_all=True, append_images=pictures[1:], duration=delays, loop=0, disposal=1)
    with media.Image.open(filename) as gif:
        assert gif.n_frames == len(scenes)
        for i, delay in enumerate(delays):
            gif.seek(i)
            assert gif.info["duration"] == delay
    rec.evidence.append(dict(file=filename.name, observed_motion_ms=elapsed, encoded_ms=delays,
                             frames=[dict(caption=c, cells=f.cells) for f, c, _ in scenes]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="any of apt, bash, git, rsync, ffmpeg; default: all five")
    args = parser.parse_args()
    actions = {"apt": apt, "bash": bash, "git": git, "rsync": rsync, "ffmpeg": ffmpeg}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    for name in args.names or actions:
        if name not in actions:
            parser.error(f"Unknown scenario: {name}")
        with session(name) as recording:
            actions[name](recording)
        print(f"{name}: verified at {SIZES[name]}", flush=True)
