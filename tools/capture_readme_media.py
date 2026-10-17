#!/usr/bin/env python3
"""Record real Linux terminal sessions and render reproducible README media.

Pillow and pyte are documentation-only dependencies. No runtime UI is mocked;
the renderer receives the application's PTY output, including curses controls.
"""

import codecs
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import pty
import select
import shlex
import signal
import struct
import sys
import tempfile
import termios
import time

from PIL import Image, ImageDraw, ImageFont
import pyte


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/assets"
FONT = Path(os.environ.get("CLI_HELP_MEDIA_FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
COLUMNS, ROWS = 100, 28
BACKGROUND, FOREGROUND = "#101923", "#e4edf5"
COLORS = {"black": "#101923", "red": "#ef798a", "green": "#7fceaa",
          "brown": "#e6c07b", "blue": "#7eaaff", "magenta": "#c792ea",
          "cyan": "#77d6e5", "white": FOREGROUND}
sys.path.insert(0, str(ROOT / "cli_help"))
from manual_import import ManualCollection, atomic_json


class TerminalScreen(pyte.Screen):
    """Preserve the primary screen across curses' xterm alternate-screen mode."""

    primary = None

    def set_mode(self, *modes, **kwargs):
        if kwargs.get("private") and 1049 in modes:
            self.primary = deepcopy((self.buffer, self.cursor, self.margins, self.mode))
            self.reset()
        super().set_mode(*modes, **kwargs)

    def reset_mode(self, *modes, **kwargs):
        if kwargs.get("private") and 1049 in modes and self.primary is not None:
            self.buffer, self.cursor, self.margins, self.mode = self.primary
            self.primary = None
        super().reset_mode(*modes, **kwargs)


class Terminal:
    """Run isolated Bash, capture its output, and retain actual terminal cells."""

    def __init__(self, folder):
        self.folder = folder
        self.screen = TerminalScreen(COLUMNS, ROWS)
        self.stream = pyte.Stream(self.screen)
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self.output = ""
        self.events = []
        self.started = time.monotonic()
        self.marker = folder / "executed"
        self.snapshot = folder / "buffer"
        rcfile = folder / "bashrc"
        rcfile.write_text(
            "PS1='demo $ '; PS2='> '; set +o history\n"
            + "source " + shlex.quote(str(ROOT / "bash/interactive-help.bash")) + "\n"
            + "rsync() { printf executed > " + shlex.quote(str(self.marker)) + "; }\n"
            + "_capture_buffer() { printf '%s\\0%s\\0' \"$READLINE_POINT\" \"$READLINE_LINE\" > "
            + shlex.quote(str(self.snapshot)) + "; }\n"
            + "bind -x '\"\\C-x\\C-g\":_capture_buffer'\n"
        )
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLUMNS, 0, 0))
            environment = {"HOME": str(folder), "PATH": os.environ["PATH"],
                           "TERM": "xterm-256color", "LC_ALL": "C.UTF-8",
                           "CLI_HELP_DISCOVERY": "off", "INPUTRC": "/dev/null"}
            os.execve("/bin/bash", ["bash", "--noprofile", "--rcfile", str(rcfile), "-i"], environment)
        self.until("demo $ ")
        self.send("\x0c", "demo $ ")

    def read(self, timeout=0.1):
        """Decode one available PTY chunk and apply it to the terminal emulator."""
        if not select.select([self.fd], [], [], timeout)[0]:
            return False
        text = self.decoder.decode(os.read(self.fd, 65536))
        self.output += text
        self.stream.feed(text)
        self.events.append([round(time.monotonic() - self.started, 4), "o", text])
        return True

    def until(self, expected):
        """Wait for output produced since the latest input, with a bounded timeout."""
        deadline = time.monotonic() + 8
        while expected not in self.output:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"Missing {expected!r}; output: {self.output[-1500:]!r}")
            self.read()
        while self.read(0.12):
            pass

    def send(self, value, expected=None):
        self.output = ""
        os.write(self.fd, value.encode())
        if expected is not None:
            self.until(expected)
        else:
            while self.read(0.15):
                pass

    def close(self):
        """Terminate the isolated shell without sending an Enter to pending input."""
        os.kill(self.pid, signal.SIGKILL)
        os.waitpid(self.pid, 0)
        os.close(self.fd)


def color(value, default):
    """Translate pyte's named and RGB color values to Pillow colors."""
    if value == "default":
        return default
    return COLORS.get(value, "#" + value if len(value) == 6 else default)


def render(screen, title, caption, first_row=0):
    """Render a terminal viewport with separate captions; optionally omit scrollback."""
    font = ImageFont.truetype(str(FONT), 18)
    cell_width, cell_height = round(font.getlength("M")), 24
    padding, top = 24, 62
    width = COLUMNS * cell_width + padding * 2
    height = (ROWS - first_row) * cell_height + top + 64
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 42), fill="#1e2c3c")
    draw.text((padding, 10), title, font=font, fill="#8cdef0")
    for row in range(first_row, ROWS):
        for column in range(COLUMNS):
            char = screen.buffer[row][column]
            foreground = color(char.fg, FOREGROUND)
            background = color(char.bg, BACKGROUND)
            if char.reverse:
                foreground, background = background, foreground
            x, y = padding + column * cell_width, top + (row - first_row) * cell_height
            draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), fill=background)
            draw.text((x, y), char.data, font=font, fill=foreground, stroke_width=int(char.bold))
    if not screen.cursor.hidden and screen.cursor.y >= first_row:
        x = padding + min(screen.cursor.x, COLUMNS - 1) * cell_width
        y = top + (screen.cursor.y - first_row) * cell_height
        draw.rectangle((x, y + 21, x + cell_width - 1, y + 23), fill="#77d6e5")
    draw.line((padding, height - 49, width - padding, height - 49), fill="#34495e")
    draw.text((padding, height - 37), caption, font=font, fill="#a4b8cb")
    return image


def capture_browser(folder):
    """Capture Alt-H, interactive search, and insertion; assert no execution."""
    terminal = Terminal(folder)
    frames, durations = [], []

    def frame(caption, duration):
        frames.append(render(terminal.screen, "CLI Interactive Help Menu | Bash", caption))
        durations.append(duration)

    try:
        terminal.send("rsync --", "rsync --")
        frame("1 / 4   Type a command; leave it pending", 1500)
        terminal.send("\x1bh", "Interactive help")
        frame("2 / 4   Alt-H opens categorized help", 2100)
        frames[-1].save(OUTPUT / "help-browser.png")
        terminal.send("/")
        frame("3 / 4   Press / to search", 800)
        for value in ("ar", "ch", "ive"):
            terminal.send(value)
            frame("3 / 4   Search for archive", 450)
        terminal.send("\n")
        frame("3 / 4   Enter applies the search filter", 1700)
        terminal.send("\n", "\x1b[?1049l")
        terminal.send("\x18\x07")
        cursor, line, empty = terminal.snapshot.read_bytes().split(b"\0")
        assert (cursor, line, empty) == (b"16", b"rsync --archive ", b"")
        assert not terminal.marker.exists(), "Pending command executed"
        frame("4 / 4   --archive inserted | command remains unexecuted", 3500)
        frames[0].save(OUTPUT / "option-insertion.gif", save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, optimize=True, disposal=2)
        frames[-1].save(OUTPUT / "option-inserted.png")
        return {"pending_line": line.decode(), "cursor": int(cursor), "executed": False,
                "duration_ms": sum(durations), "frames": len(frames)}, terminal.events
    finally:
        terminal.close()


def capture_review(folder):
    """Open the actual guided form against a temporary illustrative collection."""
    collection = folder / "collection"
    profile = {"command": ["example", "convert"], "description": "Example conversion options.",
               "categories": [{"name": "Output", "options": [
                   {"flag": "--output", "argument": "FILE", "summary": "Write converted output",
                    "detail": "Choose the destination file."},
                   {"flag": "--verbose", "summary": "Show conversion details"}]}]}
    driver = {"command": "example", "paths": [
        {"command": ["convert"], "help": [], "man": "example-convert"}]}
    with ManualCollection(collection) as destination:
        destination.save_documents(profile, driver)
    report = collection / "scan-report.json"
    atomic_json(report, {"schema_version": 1, "records": [
        {"command": ["example", "convert"], "status": "needs_adjustment", "generated": True}]})
    before = {path: path.read_bytes() for path in collection.rglob("*.json")}
    terminal = Terminal(folder)
    try:
        command = shlex.join([sys.executable, str(ROOT / "cli_help/main.py"), "--review-report", str(report)])
        terminal.send(command + "\n", "Review: number")
        for value, expected in [("1", "Entry:"), ("o", "Options: [e]"), ("e", "Select number"),
                                ("1", "Literal flag ("), ("", "Summary ("),
                                ("Choose the output file", "Detail ("), ("", "Argument placeholder (")]:
            terminal.send(value + "\n", expected)
        render(terminal.screen, "Guided review | example convert",
               "Example collection | Edit fields without JSON; save explicitly",
               first_row=10).save(OUTPUT / "guided-review.png")
        terminal.send("/cancel\n", "Entry:")
        terminal.send("b\n", "Review: number")
        terminal.send("q\n", "demo $ ")
        assert all(path.read_bytes() == original for path, original in before.items())
        return terminal.events
    finally:
        terminal.close()


def main():
    """Write public media and local capture evidence; temporary drafts are removed."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evidence = ROOT / "tests/reports/readme-media"
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cli-help-media-") as temporary:
        folder = Path(temporary)
        browser = folder / "browser"
        review = folder / "review"
        browser.mkdir()
        review.mkdir()
        result, browser_events = capture_browser(browser)
        review_events = capture_review(review)
    for name, events in [("browser", browser_events), ("review", review_events)]:
        header = {"version": 2, "width": COLUMNS, "height": ROWS, "env": {"TERM": "xterm-256color"}}
        (evidence / (name + ".cast")).write_text("\n".join(json.dumps(item) for item in [header, *events]) + "\n")
    (evidence / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print("Saved README media to", OUTPUT)


if __name__ == "__main__":
    main()
