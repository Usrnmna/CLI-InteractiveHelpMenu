"""Measure matched full-frame time at both terminal geometries against one serial oracle.

Set MENU_BENCH_DIR to a directory containing before/ and after/ snapshot roots.
Use a controller with the media decoder dependencies. Helpers use the system Python.
"""

import argparse
from contextlib import ExitStack
import fcntl
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import termios
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "phase1"))
import terminal_matrix as matrix

bench = matrix.bench
root = Path(os.environ["MENU_BENCH_DIR"]).resolve()
assert Path(bench.ui.__file__).resolve().parent == root / "before/cli_help"


def compare(case, width, height, override=None):
    """Warm both isolated Bash sessions, then alternate helpers for forty pairs."""
    line = bench.cases[case]
    filename = "git-worktree-remove" if case == "small" else "ffmpeg"
    profile_path = root / "before/profiles" / (filename + ".json")
    if case == "small" and override:
        profile_path = override
    profile = json.loads(profile_path.read_bytes())
    if case == "small" and profile["command"] != ["git", "worktree", "remove"]:
        raise ValueError(f"Expected a git worktree remove profile in {profile_path}")
    steps, _ = matrix.expected(profile, line.split(" ")[-1], height, width)
    with tempfile.TemporaryDirectory() as tmp, ExitStack() as scope:
        screen = bench.TerminalScreen
        scope.enter_context(patch.object(bench, "TerminalScreen", lambda *_: screen(width, height)))
        sessions = {}
        for variant in ("before", "after"):
            folder = Path(tmp, variant)
            folder.mkdir()
            env = dict(CLI_HELP_DISCOVERY="off", CLI_HELP_PYTHON="/usr/bin/python3", PYTHONDONTWRITEBYTECODE="1")
            if case == "small" and override:
                env["CLI_HELP_PROFILES"] = str(override.parent)
            with patch.object(bench.bash, "ROOT", root / variant):
                session = bench.bash.BashSession(folder, extra_environment=env)
            sessions[variant] = session
            scope.callback(session.close)
        for trial in range(41):
            for variant in (("before", "after") if trial % 2 else ("after", "before")):
                session = sessions[variant]
                fcntl.ioctl(session.fd, termios.TIOCSWINSZ, struct.pack("HHHH", height, width, 0, 0))
                session.send("\x15" + line)
                assert session.read_buffer() == (line, len(line))
                data = bench.timed(session, steps)
                assert session.read_buffer() == (line, len(line))
                if trial:
                    print(json.dumps(dict(width=width, case=case, pair=trial, variant=variant, **data)), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=("ffmpeg", "small", "map", "timeout"),
                        default=("ffmpeg", "small", "map", "timeout"))
    parser.add_argument("--git-override", type=lambda name: Path(name).resolve(),
                        help="Use this git worktree remove profile as the small-menu oracle and its directory as the custom collection")
    args = parser.parse_args()
    for width, height in ((80, 24), (60, 16)):
        for case in args.cases:
            compare(case, width, height, args.git_override)
