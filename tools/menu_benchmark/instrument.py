#!/usr/bin/python3
"""Collect helper CPU phases and draw timestamps in a separate invocation."""

import json
import os
import sys
import time
from pathlib import Path

script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
import main
import ui

phases = {}
draws = []


def instrument(owner, name):
    """Record the first successful call and each redraw completion using separate clocks."""
    original = getattr(owner, name)

    def measured(*args, **kw):
        start = time.process_time_ns()
        result = original(*args, **kw)
        phases.setdefault(name, (time.process_time_ns() - start) / 1e6)
        if name == "draw":
            draws.append(time.monotonic_ns())
        return result

    setattr(owner, name, measured)


for owner, name in (
    (main, "load_profiles"),
    (main, "find_context"),
    (ui.Browser, "__post_init__"),
    (ui, "draw"),
):
    instrument(owner, name)
status = main.main()
with open(os.environ["STAGE1_PHASES"], "a") as out:
    print(json.dumps(dict(phases=phases, draws=draws)), file=out)
raise SystemExit(status)
