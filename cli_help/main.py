#!/usr/bin/env python3
"""Entry point and NUL-delimited Bash buffer-edit protocol."""

import argparse
import json
import locale
import os
from pathlib import Path
import sys

from core import HelpError, find_context, insert_option, load_profiles
from discovery import Settings, discover
from command_paths import load_driver_registry


ROOT = Path(__file__).resolve().parent.parent


def choose_option(context, keys):
    """Attach curses to /dev/tty while reserving stdout for the edit response."""
    import curses
    from ui import run_browser

    saved_input = os.dup(0)
    saved_output = os.dup(1)
    try:
        with open("/dev/tty", "r+b", buffering=0) as terminal:
            os.dup2(terminal.fileno(), 0)
            os.dup2(terminal.fileno(), 1)
            try:
                return curses.wrapper(run_browser, context.profile, context.query, keys)
            except curses.error as error:
                raise HelpError(f"The terminal cannot display the browser: {error}") from error
    finally:
        os.dup2(saved_input, 0)
        os.dup2(saved_output, 1)
        os.close(saved_input)
        os.close(saved_output)


def main():
    """Validate inputs, run the selector, and emit edits only after acceptance."""
    parser = argparse.ArgumentParser(description="Browse command help without executing the pending command.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bash", action="store_true", help="Read the buffer and character cursor from CLI_HELP_LINE/CLI_HELP_POINT")
    mode.add_argument("--list-commands", action="store_true", help="List available command profiles")
    mode.add_argument("--check", action="store_true", help="Validate profiles and key configuration")
    mode.add_argument("--list-drivers", action="store_true", help="List built-in and configured driver paths")
    mode.add_argument("--import-man", metavar="COMMAND", nargs="+", help="Import manual documentation as a profile and manual-only driver")
    mode.add_argument("--scan-installed", action="store_true", help="Bulk import installed commands' manuals without executing the commands")
    mode.add_argument("--review-report", type=Path, metavar="REPORT", help="Interactively correct and preview a scan collection")
    mode.add_argument("--discover", metavar="COMMAND", nargs="+", help="Print discovered help for a command and optional subcommand path as JSON")
    parser.add_argument("--refresh", action="store_true", help="Bypass the cache with --discover")
    parser.add_argument("--man-page", help="Manual page name for --import-man; defaults to the hyphenated command path")
    manual_input = parser.add_mutually_exclusive_group()
    manual_input.add_argument("--man-text", type=Path, help="Rendered UTF-8 manual text to import")
    manual_input.add_argument("--man-file", type=Path, help="Local roff or compressed manual file to render and import")
    parser.add_argument("--output-dir", type=Path, help="Destination containing profiles/ and drivers/ for import or scan")
    parser.add_argument("--replace", action="store_true", help="Allow import or scan to replace existing matching profiles/routes")
    parser.add_argument("--scan-path", action="append", type=Path, help="Inventory this directory instead of PATH; repeat for multiple directories")
    parser.add_argument("--include", action="append", help="Include executable basenames matching this glob; repeat to add patterns")
    parser.add_argument("--exclude", action="append", help="Exclude executable basenames matching this glob")
    parser.add_argument("--limit", type=int, help="Maximum manual scan jobs; zero means unlimited")
    parser.add_argument("--scan-subcommands", action="store_true", help="Also scan manual paths declared by loaded drivers")
    parser.add_argument("--strict-scan", action="store_true", help="Return failure if the scan reports entries needing adjustment")
    args = parser.parse_args()
    if args.refresh and not args.discover:
        parser.error("--refresh requires --discover COMMAND")
    if args.import_man and not args.output_dir:
        parser.error("--import-man requires --output-dir")
    if args.scan_installed and not args.output_dir:
        parser.error("--scan-installed requires --output-dir")
    if not args.import_man and any((args.man_page, args.man_text, args.man_file)):
        parser.error("Manual input options require --import-man")
    if not (args.import_man or args.scan_installed) and (args.output_dir or args.replace):
        parser.error("Output and replacement options require --import-man or --scan-installed")
    if not args.scan_installed and (any((args.scan_path, args.include, args.exclude, args.scan_subcommands, args.strict_scan)) or args.limit is not None):
        parser.error("Scan options require --scan-installed")
    try:
        if args.review_report:
            from review import run_review
            return run_review(args.review_report)
        if args.scan_installed:
            from bulk_scan import scan_installed
            driver_directory = os.environ.get("CLI_HELP_DRIVERS")
            registry = load_driver_registry(Path(driver_directory).expanduser() if driver_directory else None)
            report = scan_installed(args.output_dir, args.scan_path, args.include or (), args.exclude or (),
                                    args.limit or 0, args.scan_subcommands, Settings.from_environment().timeout,
                                    args.replace, registry,
                                    progress=lambda record: print(f"{' '.join(record['command'])}: {record['status']} ({record['reason']})", file=sys.stderr))
            print(json.dumps({key: report[key] for key in ("report", "summary", "inventory_count", "inventory_warnings", "errors", "interrupted")}, indent=2))
            if report["interrupted"]:
                return 130
            return int(bool(report["errors"] or report["inventory_warnings"] or report["summary"]["failed"] or
                            args.strict_scan and report["summary"]["needs_adjustment"]))
        if args.import_man:
            from manual_import import import_manual
            result = import_manual(args.import_man, args.output_dir, args.man_page, args.man_text,
                                   args.man_file, Settings.from_environment().timeout, args.replace)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        custom = os.environ.get("CLI_HELP_PROFILES")
        profiles = load_profiles(ROOT / "profiles", Path(custom).expanduser() if custom else None)
        driver_directory = os.environ.get("CLI_HELP_DRIVERS")
        drivers = load_driver_registry(Path(driver_directory).expanduser() if driver_directory else None)
        if args.list_drivers:
            for name, driver in sorted(drivers.items()):
                for path in sorted(driver.paths):
                    print(" ".join((name, *path)))
            return 0
        if args.list_commands:
            for profile in profiles:
                print(" ".join(profile["command"]))
            return 0
        settings = Settings.from_environment()
        if args.discover:
            print(json.dumps(discover(args.discover[0], settings, args.refresh, tuple(args.discover[1:]), drivers), ensure_ascii=False, indent=2))
            return 0
        from ui import load_keys
        config = os.environ.get("CLI_HELP_CONFIG")
        keys = load_keys(Path(config).expanduser() if config else None)
        if args.check:
            print(f"Validated {len(profiles)} command profiles, {len(drivers)} drivers, browser keybindings, and discovery settings.")
            return 0
        locale.setlocale(locale.LC_ALL, "")
        if locale.getpreferredencoding(False).lower().replace("-", "") != "utf8":
            raise HelpError("A UTF-8 shell locale is required.")
        context = find_context(os.environ.get("CLI_HELP_LINE", ""), int(os.environ.get("CLI_HELP_POINT", "0")), profiles,
                               discover=lambda command, subcommands=(): discover(command, settings, subcommands=subcommands, driver_registry=drivers),
                               driver_registry=drivers)
        selected = choose_option(context, keys)
        if selected is None:
            return 0
        line, point = insert_option(context, selected)
        response = f"{point}\0{line}\0".encode("utf-8", "surrogateescape")
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()
        return 0
    except (HelpError, OSError, ValueError, ImportError) as error:
        print(f"\ninteractive-help: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
