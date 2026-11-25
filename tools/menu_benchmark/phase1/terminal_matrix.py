"""Replay complete current-renderer frames with equal helper wrappers for all pool policies.

Run from the project root with the media decoder installed. Set MENU_BENCH_DIR
to a directory whose 'before' entry points to the current checkout.
"""

import argparse
import fcntl
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import termios
import threading
from contextlib import ExitStack

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import terminal as bench
from workers import capacity, worker_count


def expected(profile, query, height, width, idle=False):
    """Generate complete cells from the unmodified serial code outside timed sessions."""
    browser = bench.ui.Browser(profile, query)
    result = []

    def frame(name, key, searching=False):
        """Render one expected state, preserving the full geometry and clipped cells."""
        window = bench.CellScreen(height, width)
        bench.ui.draw(window, browser, bench.keys, searching)
        lines = [" " * width for _ in range(height)]
        for (r, c, _), text in window.cells.items():
            lines[r] = lines[r][:c] + text + lines[r][c + len(text):]
        result.append((name, key, [line.rstrip() for line in lines]))

    frame("open", None)
    if idle:
        height, width = (16, 60) if width == 80 else (24, 80)
        frame("after_idle_resize", (height, width))
    for level in ("Detailed", "Expanded", "Simple"):
        browser.level = level
        frame(level, "D")
    if len(browser.options()) > 1:
        browser.move_option(1)
        frame("row", "j")
    frame("search", "/", True)
    browser.set_query(browser.query + "b")
    frame("first_key", "b", True)
    for letter in "ps":
        browser.set_query(browser.query + letter)
    frame("unit_search", "ps", True)
    browser.set_query("")
    frame("short_query", "\x15", True)
    frame("apply", "\n")
    height, width = (16, 60) if width == 80 else (24, 80)
    frame("resize", (height, width))
    return result, browser.options()[browser.selected]


def sample_tree(pid, stop, record):
    """Sample simultaneous RSS and proportional resident memory of shell children, excluding Bash."""
    def descendants(pid):
        """Read each child PID recursively while the process tree is live."""
        children = Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
        return [int(child) for child in children] + [p for child in children for p in descendants(child)]
    while not stop.is_set():
        try:
            group = descendants(pid)
            totals = [0, 0]
            for child in group:
                fields = Path(f"/proc/{child}/smaps_rollup").read_text().splitlines()
                for i, label in enumerate(("Rss:", "Pss:")):
                    totals[i] += int(next(line for line in fields if line.startswith(label)).split()[1])
            for i in range(2):
                record[i] = max(record[i], totals[i])
        except (FileNotFoundError, ProcessLookupError, StopIteration):
            pass
        stop.wait(0.005)


def run(args):
    """Rotate policy order within each block and keep each open in a fresh helper."""
    cpus = sorted(os.sched_getaffinity(0))
    if args.cpus:
        os.sched_setaffinity(0, cpus[:args.cpus])
    root = Path.cwd()
    screen = bench.TerminalScreen
    height, width = (16, 60) if args.width == 60 else (24, 80)
    bench.TerminalScreen = lambda *_: screen(width, height)
    if args.idle:
        original_proc = bench.proc

        def switches(pid):
            """Include involuntary context switches in the two idle checkpoints."""
            result = original_proc(pid)
            fields = Path(f"/proc/{pid}/status").read_text().splitlines()
            result["nonvoluntary"] = int(next(row for row in fields if row.startswith("nonvoluntary_ctxt_switches:")).split()[1])
            return result
        bench.proc = switches
    for case in args.cases:
        filename = "git-worktree-remove" if case == "small" else "ffmpeg"
        line = bench.cases[case]
        profile = json.loads((root / "profiles" / (filename + ".json")).read_text())
        if args.rows:
            # An evenly spaced FFmpeg subset retains authentic prose and definitions.
            total = sum(len(c["options"]) for c in profile["categories"])
            keep = {i * total // args.rows for i in range(min(args.rows, total))}
            cursor = 0
            for category in profile["categories"]:
                options = category["options"]
                category["options"] = [opt for i, opt in enumerate(options, cursor) if i in keep]
                cursor += len(options)
            profile["categories"] = [c for c in profile["categories"] if c["options"]]
        if args.compact:
            if not args.rows:
                raise ValueError("Compact synthetic rows require --rows")
            for category in profile["categories"]:
                for option in category["options"]:
                    option.update(summary="Show option", detail="")
                    option.pop("value_semantics", None)
        rows = sum(len(c["options"]) for c in profile["categories"])
        steps, selected = expected(profile, line.split(" ")[-1], height, width, args.idle)
        modes = args.modes.split(",")
        with tempfile.TemporaryDirectory() as scratch, ExitStack() as stack:
            sessions = {}
            for mode in modes:
                folder = Path(scratch, mode)
                folder.mkdir()
                env = dict(CLI_HELP_DISCOVERY="off", CLI_HELP_PYTHON=str(HERE / "helper.py"),
                           BENCH_WORKERS=mode, PYTHONDONTWRITEBYTECODE="1")
                if args.rows:
                    custom = folder / "profiles"
                    custom.mkdir()
                    (custom / "subset.json").write_text(json.dumps(profile))
                    env["CLI_HELP_PROFILES"] = str(custom)
                if args.resources or args.idle:
                    env["BENCH_RESOURCE"] = str(folder / "resources")
                session = bench.bash.BashSession(folder, extra_environment=env)
                stack.callback(session.close)
                sessions[mode] = session
            for index in range(args.repeats + 1):
                offset = index % len(modes)
                for mode in modes[offset:] + modes[:offset]:
                    session = sessions[mode]
                    fcntl.ioctl(session.fd, termios.TIOCSWINSZ, struct.pack("HHHH", height, width, 0, 0))
                    session.send("\x15" + line)
                    assert session.read_buffer() == (line, len(line))
                    ids = session.folder / "resources.ids"
                    ids.unlink(missing_ok=True)
                    peaks = [0, 0]
                    stop = threading.Event()
                    if args.resources:
                        sampler = threading.Thread(target=sample_tree, args=(session.pid, stop, peaks))
                        sampler.start()
                    before_tty = termios.tcgetattr(session.fd)
                    normal_finish = session.finish
                    accept = args.idle and index % 2 == 0
                    if accept:
                        session.finish = lambda key: normal_finish("\n")
                    try:
                        sample = bench.timed(session, steps, idle=bool(args.idle and index))
                    finally:
                        session.finish = normal_finish
                        stop.set()
                        if args.resources:
                            sampler.join()
                    expected_edit = (line, len(line))
                    if accept:
                        from core import find_context, insert_option
                        expected_edit = insert_option(find_context(line, len(line), [profile]), selected)
                    assert session.read_buffer() == expected_edit
                    if args.idle:
                        assert termios.tcgetattr(session.fd) == before_tty
                    if args.resources or args.idle:
                        usage = json.loads((session.folder / "resources").read_text().splitlines()[-1])
                        draws = usage.pop("draws")
                        assert usage.pop("workers") == 0 and usage["threads"] == 1
                        sample.update(usage, peak_rss_pss_kib=peaks,
                                      executing_workers=len(set(ids.read_text().splitlines())) if ids.exists() else 1)
                        if "idle_start" in sample:
                            sample["idle_draws"] = sum(sample["idle_start"] <= t <= sample["idle_end"] for t in draws)
                    workers = worker_count(mode, profile["categories"])
                    if index:
                        print(json.dumps(dict(case=case, mode=mode, width=width, capacity=capacity(),
                                              workers=workers, rows=rows, trial=index, **sample)), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, choices=(60, 80), default=80)
    parser.add_argument("--compact", action="store_true", help="Use minimal prose in the custom row-size control")
    parser.add_argument("--rows", type=int, help="Evenly spaced rows in a custom FFmpeg override")
    parser.add_argument("--cpus", type=int, default=0)
    parser.add_argument("--repeats", type=int, default=40)
    parser.add_argument("--modes", default="serial,thread-2,process-2,thread-auto,process-auto")
    parser.add_argument("--resources", action="store_true")
    parser.add_argument("--idle", action="store_true")
    parser.add_argument("cases", nargs="+", choices=("ffmpeg", "small", "map", "timeout"))
    run(parser.parse_args())
