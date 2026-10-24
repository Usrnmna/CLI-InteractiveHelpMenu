#!/usr/bin/env python3
"""Produce an opt-in compatibility report using fixed help routes, never actions."""

import argparse
import json
import os
import platform
from pathlib import Path
import shlex
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option
from discovery import ProbeError, Settings, clean_output, discover, run_probe


def check_case(words, registry, expected_flags=(), allow_empty=False, excluded=(), expected_counts=None, timeout=4):
    """Check discovery and an in-memory edit; missing executables remain explicit."""
    record = {"command": words, "executable": shutil.which(words[0])}
    if not record["executable"]:
        return {**record, "status": "skipped", "reason": "Executable is not installed."}
    try:
        profile = discover(words[0], Settings(cache_ttl=0, timeout=timeout), subcommands=tuple(words[1:]), driver_registry=registry)
        options = [option for category in profile["categories"] for option in category["options"]]
        flags = {option["flag"] for option in options}
        missing = sorted(set(expected_flags) - flags)
        if missing:
            raise HelpError(f"Expected flags missing: {missing}")
        unexpected = sorted(set(excluded) & flags)
        if unexpected:
            raise HelpError(f"Unsupported syntax was truncated into flags: {unexpected}")
        by_flag = {option["flag"]: option for option in options}
        for flag, count in (expected_counts or {}).items():
            option = by_flag.get(flag, {})
            if not option.get("argument") or option.get("argument_count", 1) != count:
                raise HelpError(f"Incorrect argument count for {flag}: expected {count}")
        line = " ".join(words) + " --"
        context = find_context(line, len(line), [profile], driver_registry=registry)
        for option in options:
            edited, point = insert_option(context, option)
            expected = " ".join(words) + " " + option["flag"] + ("" if option["flag"].endswith("=") else " ")
            if edited != expected or point != len(edited):
                raise HelpError("Literal edit invariant failed.")
        return {**record, "status": "passed", "option_count": len(flags), "categories": len(profile["categories"]),
                "sources": profile["discovery"]["sources"], "warnings": profile["discovery"]["warnings"]}
    except (HelpError, ValueError, OSError) as error:
        # npm root output commonly documents commands rather than option lines.
        expected_empty = allow_empty and not isinstance(error, ProbeError) and "No recognizable option declarations" in str(error)
        status = "unsupported" if expected_empty else "failed"
        return {**record, "status": status, "reason": str(error)}


def program_version(words, arguments):
    """Read a matrix-defined version route; custom cases never invent one."""
    executable = shutil.which(words[0])
    if not executable or not arguments:
        return None
    try:
        output = clean_output(run_probe([executable, *arguments], 10, max_bytes=65536, check=True))
        return next((line.strip() for line in output.splitlines() if line.strip()), None)
    except (HelpError, OSError) as error:
        return {"unavailable": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", help="Literal command path, e.g. 'pip install'; repeat for multiple cases")
    parser.add_argument("--drivers", type=Path, help="Optional JSON driver directory")
    parser.add_argument("--tier", action="append", choices=("essential", "next", "extended"), help="Select matrix tiers; default: all")
    parser.add_argument("--report", type=Path, help="Save the JSON report to this path")
    parser.add_argument("--require-all", action="store_true", help="Treat skipped and unsupported cases as failures")
    parser.add_argument("--timeout", type=float, default=4, help="Seconds per help/manual source, 0.05-30 (default: 4)")
    args = parser.parse_args()
    if not 0.05 <= args.timeout <= 30:
        parser.error("--timeout must be between 0.05 and 30 seconds")
    if args.case and args.tier:
        parser.error("Choose --case or --tier, not both.")
    try:
        configured = args.drivers or (Path(os.environ["CLI_HELP_DRIVERS"]) if os.environ.get("CLI_HELP_DRIVERS") else ROOT / "config/drivers.example")
        registry = load_driver_registry(configured)
        matrix = json.loads((ROOT / "tests/fixtures/help/matrix.json").read_text())
        if args.case:
            by_command = {case["command"]: case for case in matrix}
            cases = [by_command.get(" ".join(shlex.split(case)), {"command": case}) for case in args.case]
            if any(not shlex.split(case["command"]) for case in cases):
                parser.error("--case requires a command path")
        else:
            cases = [case for case in matrix if not args.tier or case["tier"] in args.tier]
        records = []
        versions = {}
        for case in cases:
            words = shlex.split(case["command"])
            record = check_case(words, registry, case.get("live_flags", ()), case.get("allow_empty", False),
                                case.get("excluded", ()), case.get("live_argument_counts", {}), timeout=args.timeout)
            if words[0] not in versions:
                versions[words[0]] = program_version(words, case.get("version_args"))
            record.update(tier=case.get("tier", "custom"), package=case.get("package"), version=versions[words[0]])
            records.append(record)
        summary = {status: sum(record["status"] == status for record in records)
                   for status in ("passed", "failed", "skipped", "unsupported")}
        report = {"checked_at": datetime.now(timezone.utc).isoformat(), "cases": records,
                  "source_timeout_seconds": args.timeout,
                  "platform": platform.platform(), "python": platform.python_version(), "drivers": str(configured), "summary": summary,
                  "boundary": "Only fixed help/manual/version routes ran; every discovered flag was checked for literal insertion in memory. No actions, installs, builds, or media processing ran."}
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
