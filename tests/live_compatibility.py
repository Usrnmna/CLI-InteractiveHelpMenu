#!/usr/bin/env python3
"""Produce an opt-in compatibility report using fixed help routes, never actions."""

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option
from discovery import Settings, discover


def check_case(words, registry, expected_flags=(), allow_empty=False):
    """Check discovery and an in-memory edit; missing executables remain explicit."""
    record = {"command": words, "executable": shutil.which(words[0])}
    if not record["executable"]:
        return {**record, "status": "skipped", "reason": "Executable is not installed."}
    try:
        profile = discover(words[0], Settings(cache_ttl=0, timeout=4), subcommands=tuple(words[1:]), driver_registry=registry)
        options = [option for category in profile["categories"] for option in category["options"]]
        flags = {option["flag"] for option in options}
        missing = sorted(set(expected_flags) - flags)
        if missing:
            raise HelpError(f"Expected flags missing: {missing}")
        line = " ".join(words) + " --"
        context = find_context(line, len(line), [profile], driver_registry=registry)
        edited, point = insert_option(context, options[0])
        if not edited.startswith(" ".join(words) + " ") or not 0 <= point <= len(edited):
            raise HelpError("Literal edit invariant failed.")
        return {**record, "status": "passed", "option_count": len(flags), "categories": len(profile["categories"]),
                "sources": profile["discovery"]["sources"], "warnings": profile["discovery"]["warnings"]}
    except (HelpError, ValueError, OSError) as error:
        # npm root output commonly documents commands rather than option lines.
        status = "unsupported" if allow_empty and "No recognizable option declarations" in str(error) else "failed"
        return {**record, "status": status, "reason": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", help="Literal command path, e.g. 'pip install'; repeat for multiple cases")
    parser.add_argument("--drivers", type=Path, help="Optional JSON driver directory")
    parser.add_argument("--report", type=Path, help="Save the JSON report to this path")
    parser.add_argument("--require-all", action="store_true", help="Treat skipped and unsupported cases as failures")
    args = parser.parse_args()
    try:
        configured = args.drivers or (Path(os.environ["CLI_HELP_DRIVERS"]) if os.environ.get("CLI_HELP_DRIVERS") else None)
        registry = load_driver_registry(configured)
        matrix = json.loads((ROOT / "tests/fixtures/help/matrix.json").read_text())
        if args.case:
            cases = [(shlex.split(case), (), False) for case in args.case]
            if any(not words for words, _, _ in cases):
                parser.error("--case requires a command path")
        else:
            cases = [([case["command"]], case["live_flags"], not case["flags"]) for case in matrix]
        records = [check_case(words, registry, flags, allow_empty) for words, flags, allow_empty in cases]
        report = {"checked_at": datetime.now(timezone.utc).isoformat(), "cases": records,
                  "boundary": "Only fixed help/manual routes ran; buffer insertion was checked in memory. No actions, installs, builds, or media processing ran."}
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text + "\n", encoding="utf-8")
        print(text)
        return int(any(record["status"] == "failed" or args.require_all and record["status"] != "passed" for record in records))
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
