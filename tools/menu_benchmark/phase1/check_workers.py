"""Check equality, search ordering and adapter teardown on a supported interpreter."""

import json
import multiprocessing
from pathlib import Path
import signal
import sys
import sysconfig
import threading
from unittest.mock import patch

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "cli_help"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui
import workers
from core import load_profiles


def check_profile(profile):
    """Compare full view fields, lazy guidance and ordered matches with the serial browser."""
    for mode in ("thread-2", "process-2", "process-auto"):
        reference = ui.Browser(profile)
        with patch.object(ui.Browser, "__post_init__", ui.Browser.__post_init__):
            workers.install(mode)
            actual = ui.Browser(profile)
        for cat in profile["categories"]:
            for option in cat["options"]:
                left, right = reference.text(option), actual.text(option)
                assert left == right
                assert (left.detailed, left.expanded, left.prose_units) == (right.detailed, right.expanded, right.prose_units)
        for query in ("", "BPS", "bits per second", "'ms'", "optional audio", "NO-MATCH-999", ""):
            for browser in (reference, actual):
                browser.set_query(query)
            assert reference.category == actual.category, (profile["command"], mode, query)
            for n in range(len(profile["categories"])):
                assert reference.options(n) == actual.options(n)
        assert not multiprocessing.active_children() and threading.active_count() == 1


def interrupt(signum, frame):
    raise KeyboardInterrupt


def teardown(ffmpeg):
    """Interrupt the parent during active work and reject malformed work inside a batch."""
    for mode in ("thread-2", "process-2"):
        with patch.object(ui.Browser, "__post_init__", ui.Browser.__post_init__):
            workers.install(mode)
            signal.signal(signal.SIGALRM, interrupt)
            signal.setitimer(signal.ITIMER_REAL, 0.08)
            try:
                ui.Browser(ffmpeg)
                raise AssertionError("interruption missed construction")
            except KeyboardInterrupt:
                pass
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            assert not multiprocessing.active_children() and threading.active_count() == 1
            with patch.dict(ffmpeg["categories"][0]["options"][0], summary=None):
                try:
                    ui.Browser(ffmpeg)
                    raise AssertionError("malformed task returned normally")
                except (TypeError, AttributeError):
                    pass
            assert not multiprocessing.active_children() and threading.active_count() == 1


if __name__ == "__main__":
    profiles = load_profiles(ROOT / "profiles")
    if "--all" not in sys.argv:
        profiles = [p for p in profiles if p["command"] in (["ffmpeg"], ["git", "worktree", "remove"])]
    for profile in profiles:
        check_profile(profile)
    teardown(next(p for p in profiles if p["command"] == ["ffmpeg"]))
    print(json.dumps(dict(python=sys.version, implementation=sys.implementation.name,
                          gil=getattr(sys, "_is_gil_enabled", lambda: True)(),
                          free_threaded=sysconfig.get_config_var("Py_GIL_DISABLED"),
                          capacity=workers.capacity(), menus=len(profiles),
                          rows=sum(len(c["options"]) for p in profiles for c in p["categories"]))))
