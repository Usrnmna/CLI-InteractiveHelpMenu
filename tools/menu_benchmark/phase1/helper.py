#!/usr/bin/python3
"""Start the normal Bash helper after installing the requested temporary adapter."""

import sys
import os
from pathlib import Path

script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
import main
from workers import install

install(os.environ["BENCH_WORKERS"])
if "BENCH_RESOURCE" in os.environ:
    import json
    import resource
    import threading
    import multiprocessing
    import ui
    import time
    draws = []
    draw = ui.draw

    def counted(*args):
        """Record completed draws in instrumented runs."""
        result = draw(*args)
        draws.append(time.monotonic_ns())
        return result

    ui.draw = counted
    status = main.main()

    def cpu(who):
        """Return cumulative user and system seconds for the named resource group."""
        usage = resource.getrusage(who)
        return usage.ru_utime + usage.ru_stime
    with open(os.environ["BENCH_RESOURCE"], "a") as stream:
        print(json.dumps(dict(cpu=cpu(0) + cpu(-1), draws=draws,
                              workers=len(multiprocessing.active_children()), threads=threading.active_count())), file=stream)
    raise SystemExit(status)
raise SystemExit(main.main())
