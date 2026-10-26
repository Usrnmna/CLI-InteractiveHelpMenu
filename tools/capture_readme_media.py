#!/usr/bin/env python3
"""Record real Linux terminal sessions and render reproducible README media.

Pillow and pyte are documentation-only dependencies. No runtime UI is mocked;
the renderer receives the application's PTY output, including curses controls.
"""

import argparse
import codecs
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import pty
import select
import shlex
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time

from PIL import Image, ImageDraw, ImageFont
import pyte


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/assets"
FONT = Path(os.environ.get("CLI_HELP_MEDIA_FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
COLUMNS, ROWS = 100, 24
RSYNC_PREFIX = "rsync --archive --compress --human-readable --itemize-changes --partial "
RSYNC_PATHS = '"/srv/project files/" "/mnt/backup/project files/"'
LS_PREFIX = "ls --all --human-readable "
MEDIA_NAMES = ("help-browser.png", "option-inserted.png", "option-insertion.gif",
               "ls-browser.png", "guided-review.png", "numerical-guidance.png")
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

    def scroll_up(self, count=None):
        """Handle xterm CSI S within the scroll region without moving the cursor."""
        top, bottom = self.margins or (0, self.lines - 1)
        cursor_row = self.cursor.y
        self.cursor.y = bottom
        for _ in range(min(count or 1, bottom - top + 1)):
            self.index()
        self.cursor.y = cursor_row

    def scroll_down(self, count=None):
        """Handle xterm CSI T, the reverse scroll used by curses optimizations."""
        top, bottom = self.margins or (0, self.lines - 1)
        cursor_row = self.cursor.y
        self.cursor.y = top
        for _ in range(min(count or 1, bottom - top + 1)):
            self.reverse_index()
        self.cursor.y = cursor_row


class TerminalStream(pyte.Stream):
    """Decode curses' xterm scroll-up/down sequences missing from pyte 0.8.2."""

    csi = {**pyte.Stream.csi, "S": "scroll_up", "T": "scroll_down"}
    events = pyte.Stream.events | {"scroll_up", "scroll_down"}


class Terminal:
    """Run isolated Bash, capture its output, and retain actual terminal cells."""

    def __init__(self, folder):
        self.folder = folder
        self.screen = TerminalScreen(COLUMNS, ROWS)
        self.stream = TerminalStream(self.screen)
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
            + "rsync() { printf 'rsync\\n' >> " + shlex.quote(str(self.marker)) + "; }\n"
            + "ls() { printf 'ls\\n' >> " + shlex.quote(str(self.marker)) + "; }\n"
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

    def check_buffer(self, expected):
        """Verify the real Readline line/cursor and both target execution guards."""
        self.snapshot.unlink(missing_ok=True)
        self.send("\x18\x07")
        fields = self.snapshot.read_bytes().split(b"\0")
        wanted = [str(len(expected)).encode(), expected.encode(), b""]
        if fields != wanted:
            raise RuntimeError(f"Unexpected Readline buffer: {fields!r}; expected {wanted!r}")
        if self.marker.exists():
            raise RuntimeError(f"Pending target executed: {self.marker.read_text()}")
        return {"pending_line": expected, "cursor": len(expected), "executed": False}


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


class Demonstration:
    """Collect checked terminal states and presentation holds for one shared GIF."""

    def __init__(self):
        self.frames = []
        self.scenes = []

    def frame(self, terminal, command, caption, duration, required=(), absent=(), absent_options=()):
        """Check visible cells before rendering; retain scene evidence locally."""
        text = "\n".join(terminal.screen.display)
        # Readline wraps long pending commands without inserting a newline.
        wrapped_text = "".join(terminal.screen.display)
        for expected in required:
            if expected not in text and expected not in wrapped_text:
                raise RuntimeError(f"Scene {caption!r} lacks {expected!r}:\n{text}")
        for unexpected in absent:
            if unexpected in text:
                raise RuntimeError(f"Scene {caption!r} unexpectedly contains {unexpected!r}:\n{text}")
        if absent_options:
            # Source explanations can legitimately mention other flags. Check
            # scrolled-away rows only in the option pane, not in the details.
            rows = terminal.screen.display
            header = next(i for i, row in enumerate(rows) if "CATEGORIES" in row and "OPTIONS" in row)
            column = rows[header].index("OPTIONS")
            footer = next(i for i in range(header + 1, len(rows)) if rows[i].startswith("Category "))
            options = "\n".join(row[column:] for row in rows[header + 1:footer])
            for unexpected in absent_options:
                if unexpected in options:
                    raise RuntimeError(f"Scene {caption!r} retains an unexpected option row: {unexpected!r}")
        picture = render(terminal.screen, f"CLI Interactive Help Menu | {command}", caption)
        self.frames.append(picture)
        self.scenes.append({"command": command, "caption": caption, "duration_ms": duration,
                            "required": list(required), "absent": list(absent),
                            "absent_options": list(absent_options),
                            "event_count": len(terminal.events),
                            "screen": terminal.screen.display})
        return picture

    def save(self):
        """Encode the checked states with readable holds and a consistent canvas."""
        self.frames[0].save(OUTPUT / "option-insertion.gif", save_all=True,
                            append_images=self.frames[1:],
                            duration=[scene["duration_ms"] for scene in self.scenes],
                            loop=0, optimize=True, disposal=2)


def capture_rsync(folder, demonstration):
    """Tour real category panes, add valued options, and verify cancellation."""
    terminal = Terminal(folder)
    def frame(caption, duration, **checks):
        """Record a checked rsync state with the shared chapter heading."""
        return demonstration.frame(terminal, "rsync", caption, duration, **checks)

    try:
        terminal.send(RSYNC_PREFIX + "--", "rsync --archive")
        frame("1 / 2   rsync | Build on existing options; leave the command pending", 1500)
        terminal.send("\x1bh", "Interactive help")
        terminal.send("\x15")
        frame("Alt-H, Ctrl-U | Browse 29 options across 9 categories", 2500,
              required=("Transfer (4)", "Category 1/9", "Option 1/4", "--archive"),
              absent=("Filter: --",)).save(OUTPUT / "help-browser.png")
        terminal.send("\tlll")
        frame("Tab, Right x3 | Focus categories and browse Output", 1800,
              required=("CATEGORIES *", "Category 4/9", "--progress", "--stats"))
        terminal.send("ll")
        frame("Right x2 | Inspect attribute preservation options", 1800,
              required=("Category 6/9", "--acls", "--xattrs", "--hard-links"))
        terminal.send("\x1b[6~")
        frame("PageDown | Scroll the category pane to Recovery", 2000,
              required=("Category 9/9", "Recovery (3)", "--partial", "--backup-dir="),
              absent=("Transfer (4)",))
        terminal.send("hhhh\tj")
        frame("Network | Bare rates use 1024 bytes/second; scoped to rsync 3.4.1", 2800,
              required=("OPTIONS *", "Category 5/9", "Option 2/4", "1024 bytes/second", "3.4.1")
              ).save(OUTPUT / "numerical-guidance.png")
        terminal.send("/bytes/second\n")
        frame("Search bytes/second | Find displayed numerical meaning", 2200,
              required=("Filter: bytes/second", "--bwlimit=", "1024 bytes/second"))
        terminal.send("\n", "\x1b[?1049l")
        terminal.check_buffer(RSYNC_PREFIX + "--bwlimit=")
        terminal.send("5000 ")
        terminal.check_buffer(RSYNC_PREFIX + "--bwlimit=5000 ")
        frame("Enter inserts --bwlimit= | Type 5000 (KiB/s in rsync 3.4.1)", 1800,
              required=("--bwlimit=5000",))
        terminal.send("\x1bh", "Interactive help")
        terminal.send("/exclude")
        frame("Alt-H, /, exclude | Search another category without losing input", 2000,
              required=("Search (Enter applies, Esc restores): exclude", "--exclude=", "Option 1/2"))
        terminal.send("\n")
        frame("Enter applies the filter | A second Enter selects the option", 900,
              required=("Filter: exclude", "--exclude="))
        terminal.send("\n", "\x1b[?1049l")
        terminal.check_buffer(RSYNC_PREFIX + "--bwlimit=5000 --exclude=")
        final_line = RSYNC_PREFIX + "--bwlimit=5000 --exclude='*.tmp' " + RSYNC_PATHS + " "
        terminal.send("'*.tmp' " + RSYNC_PATHS + " ")
        result = terminal.check_buffer(final_line)
        frame("Type a quoted pattern and paths | Existing options remain intact", 3000,
              required=("--bwlimit=5000", "--exclude='*.tmp'"))
        terminal.send("\x1bh", "Interactive help")
        frame("Alt-H reopens help | Escape will preserve the complete command", 1500,
              required=("Interactive help | rsync",))
        terminal.send("\x1b", "\x1b[?1049l")
        terminal.check_buffer(final_line)
        frame("Escape | Command assembled; still unexecuted", 2000,
              required=("--exclude='*.tmp'",)).save(OUTPUT / "option-inserted.png")
        result.update(cancel_preserved=True, categories=9, options=29)
        return result, terminal.events
    finally:
        terminal.close()


def capture_ls(folder, demonstration):
    """Show all twelve Display choices through actual option-pane scrolling."""
    terminal = Terminal(folder)
    def frame(caption, duration, **checks):
        """Record a checked ls state with the shared chapter heading."""
        return demonstration.frame(terminal, "ls", caption, duration, **checks)

    try:
        terminal.send(LS_PREFIX + "--", "ls --all")
        frame("2 / 2   ls | Explore a longer option list", 1000)
        terminal.send("\x1bh", "Interactive help")
        terminal.send("\x15")
        frame("Alt-H, Ctrl-U | Display contains 12 options", 1500,
              required=("Display (12)", "Option 1/12", "--almost-all", "--color="))
        terminal.send("\x1b[6~")
        frame("PageDown | Scroll the option pane while categories stay visible", 1600,
              required=("Option 8/12", "--size", "Display (12)", "Traversal (3)"),
              absent=("> --all",))
        terminal.send("\x1bOF")
        frame("End | Inspect the selected option's pattern meaning", 1800,
              required=("Option 12/12", "--hide=PATTERN", "Hidden-name wildcard pattern"),
              absent_options=("--almost-all",))
        terminal.send("]" * 16)
        frame("] | Scroll complete details to the literal argument declaration", 2200,
              required=("Option 12/12", "Argument required: PATTERN")
              ).save(OUTPUT / "ls-browser.png")
        terminal.send("\n", "\x1b[?1049l")
        terminal.check_buffer(LS_PREFIX + "--hide=")
        final_line = LS_PREFIX + "--hide='*.tmp' \"/srv/project files/\" "
        terminal.send("'*.tmp' \"/srv/project files/\" ")
        result = terminal.check_buffer(final_line)
        frame("Enter inserts --hide= | Command assembled; still unexecuted", 1800,
              required=("--hide='*.tmp'",))
        result.update(categories=3, options=19, display_options=12)
        return result, terminal.events
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
               first_row=6).save(OUTPUT / "guided-review.png")
        terminal.send("/cancel\n", "Entry:")
        terminal.send("b\n", "Review: number")
        terminal.send("q\n", "demo $ ")
        after = {path: path.read_bytes() for path in collection.rglob("*.json")}
        if after != before:
            raise RuntimeError("Review collection changed without saving")
        return {"collection_unchanged": True, "saved": False}, terminal.events
    finally:
        terminal.close()


def source_fingerprints():
    """Identify the generator, default profiles, and runtime used for each capture."""
    source_paths = [ROOT / "tools/capture_readme_media.py", ROOT / "VERSION",
                    ROOT / "tools/requirements-media.txt"]
    source_paths.extend((ROOT / "cli_help").glob("*.py"))
    source_paths.extend((ROOT / "bash").glob("*.bash"))
    source_paths.extend((ROOT / "profiles").glob("*.json"))
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(source_paths)}


def main():
    """Write public media and local capture evidence; temporary drafts are removed."""
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT,
                        help="Destination for the named public images and animation")
    parser.add_argument("--evidence", type=Path, default=ROOT / "tests/reports/readme-media",
                        help="Private destination for raw terminal output and capture assertions")
    args = parser.parse_args()
    OUTPUT = args.output.resolve()
    evidence = args.evidence.resolve()
    if OUTPUT == evidence:
        parser.error("Public media and private evidence require separate destinations")
    sources = source_fingerprints()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cli-help-media-") as temporary:
        folder = Path(temporary)
        browser = folder / "rsync"
        ls = folder / "ls"
        review = folder / "review"
        browser.mkdir()
        ls.mkdir()
        review.mkdir()
        demonstration = Demonstration()
        result, browser_events = capture_rsync(browser, demonstration)
        ls_result, ls_events = capture_ls(ls, demonstration)
        review_result, review_events = capture_review(review)
    demonstration.save()
    for name, events in [("browser", browser_events), ("ls", ls_events), ("review", review_events)]:
        header = {"version": 2, "width": COLUMNS, "height": ROWS, "env": {"TERM": "xterm-256color"}}
        (evidence / (name + ".cast")).write_text("\n".join(json.dumps(item) for item in [header, *events]) + "\n")
    # Keep machine paths and capture provenance with local evidence, separate
    # from public media. Hashes identify the working tree even before a commit.
    if source_fingerprints() != sources:
        raise RuntimeError("Capture sources changed during recording; regenerate the media")
    result.update(
        schema_version=2,
        demonstrations={"rsync": dict(result), "ls": ls_result},
        frames=len(demonstration.frames),
        duration_ms=sum(scene["duration_ms"] for scene in demonstration.scenes),
        captured_at=datetime.now(timezone.utc).isoformat(),
        application_version=(ROOT / "VERSION").read_text().strip(),
        python=platform.python_version(),
        bash=subprocess.check_output(["bash", "--version"], text=True).splitlines()[0],
        terminal={"columns": COLUMNS, "rows": ROWS, "term": "xterm-256color"},
        dependencies={name: version(name) for name in ("Pillow", "pyte", "wcwidth")},
        review=review_result,
        sources=sources,
        assets={name: hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest()
                for name in MEDIA_NAMES},
    )
    (evidence / "scenes.json").write_text(json.dumps(demonstration.scenes, indent=2) + "\n")
    (evidence / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print("Saved README media to", OUTPUT)


if __name__ == "__main__":
    main()
