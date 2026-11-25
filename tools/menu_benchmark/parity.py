"""Record ordered view fields, every 60x16 Details page and actual search results."""

import dataclasses
import json
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root / "tests"), str(root / "cli_help")]
import review
import ui
from core import load_profiles
from discovery import build_profile
from test_discovery import HELP_TEXT, MAN_TEXT
from test_numerical_presentation import (
    BrowserLoop,
    CellScreen,
    first_option,
    specimen,
    synthetic_node,
)

keys = ui.load_keys(None)


def fixture():
    """Provide two independently labelled rows sharing one editable definition."""
    profile = specimen({"ref": "size"})
    profile["value_definitions"] = {"size": synthetic_node()}
    profile["command"] = ["rsync"]
    first = first_option(profile)
    profile["categories"][0]["options"].append(dict(first, flag="--second", summary="Second synthetic row"))
    return profile


def capture(label, browser):
    """Emit the complete model, paged Details cells and ordered matches for one open."""
    profile = browser.profile
    command = profile["command"]
    screen = CellScreen(16, 60)
    for category_index, category in enumerate(profile["categories"]):
        browser.category = category_index
        for index, option in enumerate(category["options"]):
            browser.selected = index
            browser.detail_offset = 0
            if hasattr(browser, "level"):
                browser.level = "Expanded"
            lines = []
            while True:
                requested_offset = browser.detail_offset
                ui.draw(screen, browser, keys, preview=label.startswith("preview"))
                cells = {row: text for (row, col, _), text in screen.cells.items() if col == 0}
                if hasattr(browser, "level"):
                    divider = next((r for r, text in cells.items() if "──" in text), None)
                    page = [] if divider is None else [cells[r] for r in range(divider + 1, 14)]
                    counter = next((v for v in screen.cells.values() if re.fullmatch(r"Lines \d+–\d+/\d+", v)), "")
                    first, visible_end, total = map(int, re.findall(r"\d+", counter)) if counter else (1, len(page), len(page))
                else:
                    first, visible_end, total = map(int, re.findall(r"\d+", cells[13].split(" |")[0]))
                    page = [cells.get(row, "") for row in range(8, 8 + visible_end - first + 1)]
                lines.extend(page[len(lines) - (first - 1):])
                if visible_end == total:
                    break
                browser.detail_offset = min(visible_end, total - len(page))
                if browser.detail_offset <= requested_offset:
                    raise AssertionError((label, command, option["flag"], "Details stopped advancing"))
            emit(
                [
                    label,
                    command,
                    category_index,
                    category["name"],
                    index,
                    option["flag"],
                    ui.option_label(option),
                    dataclasses.astuple(browser.text(option)),
                    lines,
                ]
            )
    first = first_option(profile)
    for query in (
        "",
        first["flag"].upper(),
        first["flag"] + " " + first["summary"][:8],
        "'ms'",
        "OPTIONAL AUDIO",
        "Numerical source",
        "NON-MATCH-WORD-999",
        "",
    ):
        browser.set_query(query)
        emit(
            [
                label,
                command,
                query,
                browser.category,
                browser.selected,
                [
                    [option["flag"] for option in browser.options(index)]
                    for index in range(len(profile["categories"]))
                ],
            ]
        )


def emit(data):
    """Write deterministic JSON Lines for byte-for-byte comparisons."""
    print(json.dumps(data, ensure_ascii=True, separators=(",", ":"), default=sorted))


if __name__ == "__main__":
    for profile in load_profiles(root / "profiles"):
        capture("bundled", ui.Browser(profile))
    with tempfile.TemporaryDirectory() as folder:
        Path(folder, "custom.json").write_text(json.dumps(fixture()))
        override = next(
            profile
            for profile in load_profiles(root / "profiles", Path(folder))
            if profile["command"] == ["rsync"]
        )
        capture("custom", ui.Browser(override))
    capture(
        "discovered", ui.Browser(build_profile("discover-tool", [("--help", HELP_TEXT), ("man", MAN_TEXT)]))
    )
    profile = fixture()
    for label in ("preview-original", "preview-edited"):
        if label.endswith("edited"):
            profile["value_definitions"]["size"]["meaning"] = "Changed synthetic amount"
        screen = CellScreen(16, 60, ["\x1b"])
        browser_class = ui.Browser

        def construct(*args):
            """Observe the Browser opened by the real preview entry point."""
            browser = browser_class(*args)
            capture(label, browser)
            return browser

        with (
            BrowserLoop(screen),
            patch.object(ui, "Browser", construct),
            patch("curses.wrapper", lambda func, *args: func(screen, *args)),
        ):
            review.preview_profile(profile)
