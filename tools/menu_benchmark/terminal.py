"""Interleave fresh real Bash helpers and time their complete decoded frames."""

import codecs
import fcntl
import json
import os
import select
import shutil
import shlex
import struct
import subprocess
import sys
import tempfile
import termios
import time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

report = Path(os.environ["MENU_BENCH_DIR"]).resolve()
old = report / "before"
oracle = Path(sys.argv[2]) if sys.argv[1:2] == ["--frames"] else old
sys.path[:0] = [str(oracle / part) for part in ("tests", "tools", "cli_help")]

import test_bash_pty as bash
import ui
from capture_readme_media import TerminalScreen, TerminalStream
from test_discovery import make_commands
from test_numerical_presentation import (
    CellScreen,
    first_option,
    specimen,
    synthetic_node,
)

cases = {
    "ffmpeg": "ffmpeg ",
    "map": "ffmpeg -map",
    "timeout": "ffmpeg -rw_timeout",
    "rsync": "rsync --ar",
    "fzf": "fzf ",
    "small": "git worktree remove ",
    "custom": "rsync ",
    "miss": "discover-tool --al",
    "hit": "discover-tool --al",
}
keys = ui.load_keys(None)


def frames(profile, query):
    """Prepare the expected full-screen cells outside the measured helper."""
    browser = ui.Browser(profile, query)
    searching = False
    height, width = 24, 100
    steps = []

    def record(action, key):
        """Append only transitions that produce distinguishable decoded cells."""
        window = CellScreen(height, width)
        ui.draw(window, browser, keys, searching)
        rows = [" " * width for _ in range(height)]
        for (row, column, _), text in window.cells.items():
            rows[row] = rows[row][:column] + text + rows[row][column + len(text) :]
        state = [row.rstrip() for row in rows]
        if steps and state == steps[-1][2]:
            return
        steps.append((action, key, state))

    record("open", None)
    searching = True
    record("search", "/")
    browser.set_query("")
    record("clear", "\x15")
    for action, ch in [("first_key", "m"), ("second_key", "s"), ("no_match", "~")]:
        browser.set_query(browser.query + ch)
        record(action, ch)
    browser.set_query("")
    record("clear_long", "\x15")
    for ch in "'ms'":
        browser.set_query(browser.query + ch)
    record("rapid_formatter", "'ms'")
    browser.set_query("")
    record("clear_formatter", "\x15")
    browser.set_query("a")
    record("short_query", "a")
    browser.set_query("")
    record("clear_short", "\x15")
    searching = False
    record("apply", "\n")
    if len(browser.options()) > 1:
        browser.move_option(1)
        record("row_in_current_category", "j")
    if browser.category + 1 < len(profile["categories"]):
        browser.move_category(1)
        record("next_category", "l")
    elif browser.category:
        browser.move_category(-1)
        record("previous_category", "h")
    if len(browser.options()) > 1:
        browser.move_option(1)
        record("next_row", "j")
    height, width = 16, 60
    record("shrink", (height, width))
    browser.detail_offset += 1
    record("scroll", "]")
    height, width = 24, 100
    record("grow", (height, width))
    return steps


def proc(pid):
    """Read helper memory in KiB, kernel CPU ticks and voluntary switches."""
    status = dict(line.split(":", 1) for line in Path(f"/proc/{pid}/status").read_text().splitlines())
    cpu = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return {k: int(status[k].split()[0]) for k in ("VmRSS", "VmHWM", "voluntary_ctxt_switches")} | {
        "user_ticks": int(cpu[11]),
        "system_ticks": int(cpu[12]),
    }


def timed(session, steps, idle=False):
    """Validate each decoded frame, time it from input and sample the live helper."""
    screen = TerminalScreen(100, 24)
    stream = TerminalStream(screen)
    decoder = codecs.getincrementaldecoder("utf8")()
    latencies = {}
    memory = {}
    result = {"ms": latencies, "memory": memory}
    for name, key, expected in steps:
        start = time.perf_counter_ns()
        if isinstance(key, (list, tuple)):
            fcntl.ioctl(session.fd, termios.TIOCSWINSZ, struct.pack("HHHH", *key, 0, 0))
            screen.resize(*key)
        else:
            session.send(session.trigger if key is None else key)
        while True:
            if not select.select([session.fd], [], [], 3)[0]:
                actual = [row.rstrip() for row in screen.display]
                raise AssertionError(
                    (
                        name,
                        [
                            (i, got, want)
                            for i, (got, want) in enumerate(zip(actual, expected))
                            if got != want
                        ][:5],
                    )
                )
            stream.feed(decoder.decode(os.read(session.fd, 65536)))
            decoded = [row.rstrip() for row in screen.display]
            if decoded == expected:
                latencies[name] = (time.perf_counter_ns() - start) / 1e6
                break
            if time.perf_counter_ns() - start > 5e9:
                raise AssertionError((name, decoded, expected))
        if name == "open":
            (pid,) = Path(f"/proc/{session.pid}/task/{session.pid}/children").read_text().split()
            memory["first"] = proc(pid)
            if idle:
                before_idle = proc(pid)
                result["idle_start"] = time.monotonic_ns()
                time.sleep(10)
                after_idle = proc(pid)
                result["idle_end"] = time.monotonic_ns()
                result["idle"] = {k: after_idle[k] - v for k, v in before_idle.items()}
                memory["idle"] = after_idle
        if name == "short_query":
            memory["short"] = proc(pid)
    memory["navigation"] = proc(pid)
    memory["dismiss"] = proc(pid)
    session.finish("q")
    return result


def main():
    """Warm both snapshots and alternate revision order for each selected case."""
    repeats = int(sys.argv[1])
    selected = sys.argv[2:] or list(cases)
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        _, probe, executed = make_commands(folder)
        custom = folder / "custom"
        custom.mkdir()
        profile = specimen({"ref": "amount"})
        profile["command"] = ["rsync"]
        profile["value_definitions"] = {"amount": synthetic_node()}
        first = first_option(profile)
        profile["categories"][0]["options"].append(dict(first, flag="--second"))
        (custom / "override.json").write_text(json.dumps(profile))
        for name in selected:
            line = cases[name]
            query = line.split(" ")[-1]
            discover = name in ("miss", "hit")
            env = {
                "CLI_HELP_DISCOVERY": "auto" if discover else "off",
                "PATH": str(folder / "bin") + ":/usr/bin:/bin",
                "CLI_HELP_PYTHON": "/usr/bin/python3",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            if name == "custom":
                env["CLI_HELP_PROFILES"] = str(custom)
            if discover:
                oracle_env = dict(env, HOME=str(folder), LC_ALL="C.UTF-8",
                                  CLI_HELP_CACHE_DIR=str(folder / "oracle-cache"))
                expected_profile = json.loads(
                    subprocess.check_output(
                        ["/usr/bin/python3", str(old / "cli_help/main.py"), "--discover", "discover-tool"],
                        env=oracle_env,
                    )
                )
            elif name == "custom":
                expected_profile = profile
            else:
                filename = "git-worktree-remove" if name == "small" else line.split()[0]
                expected_profile = json.loads((old / "profiles" / f"{filename}.json").read_text())
            # Draw each revision's expected screen with its own presentation code.
            steps = {}
            for variant in ("before", "after"):
                raw = subprocess.check_output(
                    [sys.executable, __file__, "--frames", str(report / variant), query],
                    input=json.dumps(expected_profile), text=True)
                steps[variant] = json.loads(raw)
            with ExitStack() as scope:
                sessions = {}
                for variant, root in [("before", old), ("after", report / "after")]:
                    local = folder / (variant + "-" + name)
                    local.mkdir()
                    if os.getenv("STAGE1_INSTRUMENT"):
                        env.update(
                            CLI_HELP_PYTHON=str(Path(__file__).with_name("instrument.py").resolve()),
                            STAGE1_PHASES=str(report / f"phase-{variant}-{name}.jsonl"),
                        )
                    with patch.object(bash, "ROOT", root):
                        session = bash.BashSession(local, extra_environment=env)
                    scope.callback(session.close)
                    # Shell function catches an accidental dispatch of the pending command.
                    session.send(
                        line.split()[0]
                        + "() { echo invoked > "
                        + shlex.quote(str(session.executed))
                        + "; }\n"
                    )
                    session.expect(b"__HELP_TEST_PROMPT__")
                    sessions[variant] = session
                for i in range(repeats + 1):
                    for variant in ("before", "after") if i % 2 == 0 else ("after", "before"):
                        session = sessions[variant]
                        session.send("\x15" + line)
                        assert session.read_buffer() == (line, len(line))
                        if name == "miss":
                            shutil.rmtree(session.folder / "cache", ignore_errors=True)
                        probe.unlink(missing_ok=True)
                        sample = timed(session, steps[variant], idle=bool(os.getenv("STAGE1_IDLE")) and i > 0)
                        assert not session.executed.exists() and not executed.exists()
                        assert session.read_buffer() == (line, len(line))
                        if discover:
                            assert probe.exists() == (name == "miss" or i == 0), (name, i, probe.exists())
                        if i:
                            print(json.dumps(dict(case=name, pair=i, revision=variant, **sample)), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--frames"]:
        print(json.dumps(frames(json.load(sys.stdin), sys.argv[3])))
    else:
        main()
