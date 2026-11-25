"""Capture every page for every FFmpeg and small Git option at both menu sizes.

Pass an isolated snapshot root. Each JSON line identifies an observed page or
an ordered search result. Compare stdout across roots before interpreting timings.
"""

import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root / "cli_help"), str(root / "tests")]
from test_numerical_presentation import CellScreen
import ui

assert Path(ui.__file__).resolve().parent == root / "cli_help"
keys = ui.load_keys()
counter = re.compile(r"Lines (\d+)–(\d+)/(\d+)")


def emit(record):
    """Serialize each page deterministically, including text, position and attributes."""
    print(json.dumps(record, separators=(",", ":"), ensure_ascii=True))


def pages(browser, screen, identity):
    """Follow the displayed page counter through the final line of the selected view."""
    browser.detail_offset = 0
    while True:
        ui.draw(screen, browser, keys)
        emit(["page", *identity, browser.detail_offset, sorted(screen.cells.items())])
        span = next((m for value in screen.cells.values() if (m := counter.fullmatch(value))), None)
        if not span:
            return
        first, last, total = map(int, span.groups())
        if last == total:
            return
        assert first == browser.detail_offset + 1 and last >= first
        browser.detail_offset = last


for name in ("ffmpeg", "git-worktree-remove"):
    profile = json.loads((root / "profiles" / (name + ".json")).read_bytes())
    for height, width in ((24, 80), (16, 60)):
        screen = CellScreen(height, width)
        browser = ui.Browser(profile)
        for ci, category in enumerate(profile["categories"]):
            browser.category = ci
            for oi, option in enumerate(category["options"]):
                browser.selected = oi
                for level in ui.LEVELS:
                    browser.level = level
                    pages(browser, screen, [name, width, ci, oi, option["flag"], level])
        for query in ("bps", "bits per second", "B/s", "ms", "µs", "FPS", "OPTIONAL AUDIO",
                      "-map", "-rw_timeout", "force", "Numerical source", "NO-MATCH-999", ""):
            browser.set_query(query)
            order = [[row["flag"] for row in browser.options(i)] for i in range(len(profile["categories"]))]
            for level in ui.LEVELS:
                browser.level = level
                ui.draw(screen, browser, keys)
                emit(["search", name, width, query, level, browser.category, browser.selected,
                      order, sorted(screen.cells.items())])
