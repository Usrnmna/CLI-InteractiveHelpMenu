"""Temporary Linux benchmark adapter. Loaded only by the experiment wrapper."""

import os
from pathlib import Path


def capacity():
    """Conservatively bound visible CPUs by affinity and inherited cgroup v2 quotas."""
    reported = getattr(os, "process_cpu_count", os.cpu_count)() or 1
    limits = [reported]
    try:
        limits.append(len(os.sched_getaffinity(0)))
    except (AttributeError, OSError):
        pass
    try:
        group = next(row[3:] for row in Path("/proc/self/cgroup").read_text().splitlines()
                     if row.startswith("0::"))
        root = Path("/sys/fs/cgroup")
        path = root / group.lstrip("/")
        while path.is_relative_to(root):
            quota = path / "cpu.max"
            if quota.is_file():
                amount, period = quota.read_text().split()
                if amount != "max":
                    limits.append(max(1, int(amount) // int(period)))
            path = path.parent
    except (OSError, ValueError, StopIteration):
        pass
    return max(1, min(limits))


def prepare(job):
    """Build one ordered batch of views with a batch-local shared-value cache."""
    import ui
    metadata, positional, items = job
    if "BENCH_RESOURCE" in os.environ:
        import threading
        with open(os.environ["BENCH_RESOURCE"] + ".ids", "a") as log:
            print(os.getpid(), threading.get_native_id(), file=log)
    shared = {}
    return [ui.option_text(metadata, category, option, positional=positional, shared_values=shared)
            for category, option in items]


def worker_count(mode, categories):
    """Estimate work from batchable rows and optionally the amount of input prose."""
    if mode == "serial":
        return 1
    if not mode.endswith(("auto", "sized")):
        return int(mode.split("-")[1])
    rows = sum(len(category["options"]) for category in categories)
    count = min(4, capacity(), rows // 320)
    if count > 1 and mode.endswith("sized"):
        characters = sum(len(option["summary"]) + len(option.get("detail", ""))
                         for category in categories for option in category["options"])
        count = min(count, characters // 65536)
    return max(1, count)


def install(mode):
    """Replace construction for this invocation only. Use serial below the automatic cutoff."""
    import ui
    original = ui.Browser.__post_init__

    def construct(browser):
        """Prepare ordered views, shut down the pool and restore serial navigation state."""
        categories = browser.profile["categories"]
        rows = sum(len(cat["options"]) for cat in categories)
        count = worker_count(mode, categories)
        if count == 1:
            return original(browser)
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
        import multiprocessing
        metadata = {key: value for key, value in browser.profile.items() if key != "categories"}
        items = []
        for category in categories:
            heading = {key: value for key, value in category.items() if key != "options"}
            items.extend((heading, option) for option in category["options"])
        positional = ui.value_text(metadata, metadata, positional=True)
        chunk = (rows + count - 1) // count
        jobs = [(metadata, positional, items[start:start + chunk]) for start in range(0, rows, chunk)]
        if mode.startswith("thread"):
            executor = ThreadPoolExecutor(max_workers=count)
        else:
            # Linux-only pilot in a single-threaded helper. Workers never access curses.
            executor = ProcessPoolExecutor(max_workers=count, mp_context=multiprocessing.get_context("fork"))
        with executor:
            views = [view for batch in executor.map(prepare, jobs) for view in batch]
        for (_, option), view in zip(items, views, strict=True):
            browser._text[id(option)] = view
        for index in range(len(categories)):
            if browser.options(index):
                browser.category = index
                break

    if mode != "serial":
        ui.Browser.__post_init__ = construct
