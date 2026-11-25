"""Queue cancellation during startup and verify the Bash line, terminal and helper cleanup."""

import json
from pathlib import Path
import sys
import tempfile
import termios
import time

sys.path.insert(0, str(Path.cwd() / "tests"))
from test_bash_pty import BashSession


def measure(session):
    """Send q 70 ms after curses enters the alternate screen and time Readline recovery."""
    line = "ffmpeg "
    session.send(line)
    assert session.read_buffer() == (line, len(line))
    before = termios.tcgetattr(session.fd)
    session.send(session.trigger)
    session.expect(b"\x1b[?1049h")
    time.sleep(0.07)
    children = Path(f"/proc/{session.pid}/task/{session.pid}/children")
    helper = int(children.read_text().strip())
    workers = Path(f"/proc/{helper}/task/{helper}/children").read_text().split()
    threads = len(list(Path(f"/proc/{helper}/task").iterdir()))
    start = time.perf_counter()
    session.finish("q")
    assert session.read_buffer() == (line, len(line))
    elapsed = (time.perf_counter() - start) * 1000
    assert not children.read_text().strip() and not any(Path("/proc", pid).exists() for pid in workers)
    assert termios.tcgetattr(session.fd) == before
    return dict(ms=elapsed, children=len(workers), threads=threads)


if __name__ == "__main__":
    helper = Path(__file__).resolve().with_name("helper.py")
    for mode in ("serial", "thread-auto", "process-auto"):
        environment = dict(CLI_HELP_DISCOVERY="off", CLI_HELP_PYTHON=str(helper), BENCH_WORKERS=mode)
        for trial in range(6):
            with tempfile.TemporaryDirectory() as folder:
                session = BashSession(folder, extra_environment=environment)
                try:
                    print(json.dumps(dict(mode=mode, trial=trial, **measure(session))), flush=True)
                finally:
                    session.close()
