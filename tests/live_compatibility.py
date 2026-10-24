#!/usr/bin/env python3
"""Produce an opt-in compatibility report using fixed help routes, never actions."""

import argparse
import json
import os
import platform
import re
from pathlib import Path
import shlex
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import help_route, load_driver_registry
from core import HelpError, find_context, insert_option, read_json, validate_profile
from discovery import ProbeError, Settings, clean_output, discover, run_probe, verify_command_variant


def check_case(words, registry, expected_flags=(), allow_empty=False, excluded=(), expected_counts=None, timeout=4, case_metadata=None):
    """Check discovery and an in-memory edit; missing executables remain explicit."""
    record = {"command": words, "executable": shutil.which(words[0])}
    if not record["executable"]:
        return {**record, "status": "skipped", "reason": "Executable is not installed."}
    if case_metadata and (case_metadata.get("curator") or case_metadata.get("curated_profile")):
        return check_curated_case(words, registry, record, case_metadata, timeout)
    try:
        profile = discover(words[0], Settings(cache_ttl=0, timeout=timeout), subcommands=tuple(words[1:]), driver_registry=registry)
        options = [option for category in profile["categories"] for option in category["options"]]
        flags = {option["flag"] for option in options}
        expected_flags = list(expected_flags)
        expected_counts = dict(expected_counts or {})
        if case_metadata and case_metadata.get("version_sentinels"):
            variant = profile["discovery"].get("variant", "")
            major = variant.lstrip("v").split(".")[0]
            sentinels = case_metadata["version_sentinels"].get(major)
            if sentinels is None:
                return {**record, "status": "unsupported", "reason": "No maintained sentinel set for this installed major version."}
            expected_flags.extend(sentinels.get("flags", []))
            expected_counts.update(sentinels.get("argument_counts", {}))
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
        status = "unsupported" if expected_empty or unsupported_variant(error) else "failed"
        return {**record, "status": status, "reason": str(error)}


def unsupported_variant(error):
    """Keep known product/version mismatches distinct from probe failures."""
    return not isinstance(error, ProbeError) and any(term in str(error) for term in (
        "different or unverified", "write-flash requires", "version could not be identified"))


def check_curated_case(words, registry, record, case, timeout):
    """Verify fixed route help separately from curated syntax and literal edits.

    Some leaf manuals document a family, and ip help consists of keyword grammar.
    Raw sentinel checks establish documentation presence, not generic-parser arity
    or exhaustive support. Profile metadata remains independently fixture-tested.
    """
    try:
        path = ROOT / "profiles" / case.get("profile", "-".join(words) + ".json")
        profile = read_json(path)
        validate_profile(profile, path)
        if profile["command"] != words:
            raise HelpError("Curated profile command differs from the maintained route.")
        settings = Settings(cache_ttl=0, timeout=timeout)
        variant = None
        if profile.get("identity"):
            variant = verify_command_variant(words[0], record["executable"], settings, words[1:])
        route = help_route(words[0], tuple(case.get("documentation_path", words[1:])), registry)
        probes = []
        if route.arguments:
            arguments = ("--help", "--noconftest") if words == ["pytest"] else route.arguments
            probes.append((" ".join([words[0], *arguments]), [record["executable"], *arguments]))
        manual = shutil.which("man")
        if manual and route.manual:
            probes.append(("man " + route.manual, [manual, "-P", "/bin/cat", "--no-hyphenation",
                           "--no-justification", "-s", "1:8", "--", route.manual]))
        sources, warnings = [], []
        for label, argv in probes:
            output = clean_output(run_probe(argv, timeout, **(
                {"environment_overrides": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}}
                if words == ["pytest"] and argv[0] == record["executable"] else {})))
            if output.strip():
                sources.append((label, output))
            else:
                warnings.append("Empty documentation source: " + label)
        text = "\n".join(output for _, output in sources)
        sentinels = list(case.get("live_flags", [])) + list(case.get("keyword_sentinels", []))
        if not sentinels:
            raise HelpError("Curated live verification requires independent route documentation sentinels.")
        missing = [flag for flag in sentinels if not re.search(
            r"(?<![\w-])" + re.escape(flag.rstrip("=")) + r"(?![\w-])", text)]
        if missing:
            raise HelpError(f"Fixed route documentation is missing curated sentinels: {missing}")
        options = [option for category in profile["categories"] for option in category["options"]]
        line = " ".join(words) + " --"
        context = find_context(line, len(line), [profile], driver_registry=registry,
                               discover=lambda *args, **kwargs: profile)
        for option in options:
            suffix = "" if option["flag"].endswith("=") or option.get("argument_style") == "attached_only" else " "
            expected = " ".join(words) + " " + option["flag"] + suffix
            if insert_option(context, option) != (expected, len(expected)):
                raise HelpError("Curated literal insertion invariant failed.")
        return {**record, "status": "passed", "evidence": "fixed-route documentation sentinels and curated literal edits",
                "option_count": len(options), "sources": [label for label, _ in sources], "warnings": warnings,
                "variant": variant, "verified_documentation_tokens": sentinels,
                "arity_evidence": "Independent deterministic fixtures; raw live help presence does not verify arity."}
    except (HelpError, ValueError, OSError) as error:
        return {**record, "status": "unsupported" if unsupported_variant(error) else "failed", "reason": str(error)}


def program_version(words, arguments):
    """Read a matrix-defined version route; custom cases never invent one."""
    executable = shutil.which(words[0])
    if not executable or not arguments:
        return None
    try:
        output = clean_output(run_probe([executable, *arguments], 10, max_bytes=65536, check=True))
        if Path(words[0]).name in {"esptool", "esptool.py"}:
            # Current esptool.py prints an alias deprecation notice before its
            # version. Preserve the actual identity instead of that warning.
            version = re.search(r"^esptool(?:\.py)?\s+v?[0-9]+\.[0-9]+(?:\.[0-9]+)?\b.*$", output, re.MULTILINE)
            if version:
                return version.group(0).strip()
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
                                case.get("excluded", ()), case.get("live_argument_counts", {}), timeout=args.timeout,
                                case_metadata=case)
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
