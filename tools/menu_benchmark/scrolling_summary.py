#!/usr/bin/env python3
"""Open the actual options browser on the rsync bandwidth summary for a keyboard comparison."""

import argparse
import curses
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cli_help"))
from ui import load_keys, run_browser


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="start with scrolling disabled")
    args = parser.parse_args()
    os.environ["CLI_HELP_SCROLL_SUMMARIES"] = "0" if args.static else "1"
    profile = json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))
    profile["categories"] = [next(c for c in profile["categories"] if c["name"] == "Network")]
    curses.wrapper(run_browser, profile, "--bwlimit=", load_keys(), True)
