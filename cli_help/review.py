"""Interactively review scan evidence and edit validated documentation drafts."""

from contextlib import ExitStack
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import locale
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import uuid

from command_paths import load_driver_registry
from core import HelpError, read_json, validate_profile
from discovery import Settings, build_profile
from drivers import WORD, parse_driver
from manual_import import ManualCollection, atomic_json, read_manual, validate_documents
from review_forms import FormCancelled, answer, yes_no, edit_options, edit_categories, edit_driver


PAGE_SIZE = 12
MAX_DRAFT_BYTES = 2 * 1024 * 1024
SCAN_STATUSES = {"success", "needs_adjustment", "failed", "skipped", "pending"}


def fingerprint(path):
    """Identify file content for stale-edit detection, including absent files."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


@dataclass
class Draft:
    """Keep editor text, including invalid edits, until save or explicit discard."""

    index: int
    text: str
    original: str
    fingerprints: dict

    def document(self):
        try:
            document = json.loads(self.text)
        except RecursionError as error:
            raise HelpError("The draft JSON is nested too deeply.") from error
        if not isinstance(document, dict) or set(document) != {"profile", "driver"}:
            raise HelpError("The draft requires exactly 'profile' and 'driver' objects.")
        profile = document["profile"]
        if not isinstance(profile, dict) or not isinstance(profile.get("categories"), list):
            raise HelpError("The profile requires an object with a categories list.")
        # Empty categories are permitted while constructing a new profile.
        check = dict(profile)
        if not check["categories"]:
            check["categories"] = [{"name": "Draft", "options": [{"flag": "--draft", "summary": "Draft validation"}]}]
        validate_profile(check, Path("<draft structure>"))
        parse_driver(document["driver"])
        return document


class ReviewSession:
    """Hold scanner/importer locks while reviewing one local collection.

    The report's parent directory is the collection. Embedded destination paths
    are diagnostic data and never authorize reads or writes elsewhere. Original
    scan statuses are retained; review results are separate evidence.
    """

    def __init__(self, report_path):
        self.path = report_path.expanduser().resolve(strict=True)
        self.root = self.path.parent
        self.stack = ExitStack()

    def __enter__(self):
        try:
            lock = self.root / ".scan.lock"
            try:
                descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError as error:
                raise HelpError("A scan or review is active, or .scan.lock requires inspection.") from error
            os.close(descriptor)
            self.stack.callback(lock.unlink, missing_ok=True)
            self.report = read_json(self.path)
            if not isinstance(self.report, dict) or self.report.get("schema_version") != 1 or not isinstance(self.report.get("records"), list):
                raise HelpError("Expected a version 1 scan report with a records list.")
            seen = set()
            for record in self.report["records"]:
                if not isinstance(record, dict):
                    raise HelpError("Each scan record must be an object.")
                command = record.get("command")
                if not isinstance(command, list) or not command or any(not isinstance(word, str) for word in command):
                    raise HelpError("Each scan record requires a command word list.")
                if tuple(command) in seen or not isinstance(record.get("status"), str) or record["status"] not in SCAN_STATUSES:
                    raise HelpError("The report contains duplicate commands or unknown statuses.")
                if "review" in record and not isinstance(record["review"], dict):
                    raise HelpError("A review result must be an object.")
                seen.add(tuple(command))
            for directory in (self.root / "profiles", self.root / "drivers", self.root / ".review-backups"):
                self.local_path(directory)
                if directory.exists():
                    for path in directory.glob("*.json"):
                        self.local_path(path)
            self.collection = self.stack.enter_context(ManualCollection(self.root))
            self.collection_names = self.current_names()
            driver_directory = os.environ.get("CLI_HELP_DRIVERS")
            self.registry = load_driver_registry(Path(driver_directory).expanduser() if driver_directory else None)
            self.report_fingerprint = fingerprint(self.path)
            self.save_failed = False
            return self
        except BaseException:
            self.stack.close()
            raise

    def __exit__(self, *exc):
        self.stack.close()

    def local_path(self, path):
        """Reject symlink escapes from the explicitly selected collection."""
        if not path.resolve().is_relative_to(self.root):
            raise HelpError(f"Collection path escapes its directory: {path.name}")
        return path

    def paths(self, command):
        """Resolve collection-owned names rather than trusting report path fields."""
        profile, driver = self.collection.paths_for(command)
        return self.local_path(profile), self.local_path(driver)

    def current_names(self):
        """Detect externally added or removed files that would invalidate the index."""
        return {self.local_path(path) for directory in ("profiles", "drivers")
                for path in (self.root / directory).glob("*.json")}

    def review_state(self, record):
        """Treat saved reviews as stale when either generated file changes."""
        review = record.get("review", {})
        if review.get("status") != "resolved":
            return "unreviewed"
        if not review.get("profile_sha256") or not review.get("driver_sha256"):
            return "stale"
        try:
            profile, driver = self.paths(record["command"])
            if fingerprint(profile) == review.get("profile_sha256") and fingerprint(driver) == review.get("driver_sha256"):
                return "resolved"
        except (OSError, ValueError):
            pass
        return "stale"

    def entries(self, show_all=False, search=""):
        """Filter report rows while retaining their stable record indices."""
        return [index for index, record in enumerate(self.report["records"])
                if search.casefold() in " ".join(record["command"]).casefold()
                and (show_all or record["status"] in {"needs_adjustment", "failed"}
                     and self.review_state(record) != "resolved")]

    def open_draft(self, index):
        """Load current collection files or create an explicitly incomplete draft."""
        command = self.report["records"][index]["command"]
        if any(not WORD.fullmatch(word) for word in command):
            raise HelpError("This command name is outside the literal driver schema and cannot be repaired here.")
        profile_path, driver_path = self.paths(command)
        profile = read_json(profile_path) if profile_path.exists() else {
            "command": command, "description": "Documentation for " + " ".join(command), "categories": []}
        if driver_path.exists():
            driver = read_json(driver_path)
        else:
            baseline = self.registry.get(command[0])
            driver = {"command": command[0], "global_values": sorted(baseline.global_values) if baseline else [],
                      "global_flags": sorted(baseline.global_flags) if baseline else [], "paths": []}
        if not any(route["command"] == command[1:] for route in driver["paths"]):
            manual = self.report["records"][index].get("manual") or "-".join(command)
            baseline = self.registry.get(command[0])
            route = baseline.paths.get(tuple(command[1:])) if baseline else None
            driver["paths"].append({"command": command[1:], "help": [], "man": manual,
                                    "stop_at_positional": bool(route and route.stop_at_positional)})
        text = json.dumps({"profile": profile, "driver": driver}, ensure_ascii=False, indent=2) + "\n"
        return Draft(index, text, text, {path: fingerprint(path) for path in (profile_path, driver_path)})

    def validate(self, draft):
        """Validate both schemas and command identity without invoking any help route."""
        document = draft.document()
        profile, driver = document["profile"], document["driver"]
        validate_documents(profile, driver)
        command = self.report["records"][draft.index]["command"]
        if profile["command"] != command:
            raise HelpError("The profile and driver must retain the selected command path.")
        return document

    def import_source(self, draft, kind, value, manual, timeout=2.0):
        """Replace a draft profile from a manual source, without writing the collection."""
        if kind not in {"page", "text", "roff"}:
            raise HelpError("Source must be page, text, or roff.")
        document = draft.document()
        command = self.report["records"][draft.index]["command"]
        text, label, manual = read_manual(command, value if kind == "page" else manual,
            text_file=Path(value) if kind == "text" else None,
            man_file=Path(value) if kind == "roff" else None, timeout=timeout)
        profile = build_profile(command, [(label, text)])
        profile["imported_from"] = {"source": label, "manual": manual}
        document["profile"] = profile
        for route in document["driver"]["paths"]:
            if route["command"] == command[1:]:
                route.update(help=[], man=manual)
        draft.text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"

    def save(self, draft):
        """Back up current files, persist validated edits, then record review evidence.

        Writes are atomic per file, not a transaction across the pair and report.
        Backups and unchanged review evidence permit inspection after interruption.
        """
        if self.save_failed:
            raise HelpError("Reopen the review session after inspecting the incomplete save.")
        document = self.validate(draft)
        if self.current_names() != self.collection_names:
            raise HelpError("Files changed outside this review. Reopen the session before saving.")
        for path, expected in {**draft.fingerprints, self.path: self.report_fingerprint}.items():
            self.local_path(path)
            if fingerprint(path) != expected:
                raise HelpError("Files changed outside this review. Reopen the session before saving.")
        backup = self.local_path(self.root / ".review-backups") / uuid.uuid4().hex
        backup.mkdir(parents=True)
        manifest = []
        for number, path in enumerate([*draft.fingerprints, self.path]):
            manifest.append({"path": str(path.relative_to(self.root)), "backup": f"{number}.json" if path.exists() else None})
            if path.exists():
                (backup / f"{number}.json").write_bytes(path.read_bytes())
        atomic_json(backup / "manifest.json", {"files": manifest})
        try:
            result = self.collection.save_documents(document["profile"], document["driver"], replace=True)
            report = deepcopy(self.report)
            profile_path, driver_path = self.paths(result["command"])
            report["records"][draft.index]["review"] = {
                "status": "resolved", "saved_at": datetime.now(timezone.utc).isoformat(),
                **result, "profile_sha256": fingerprint(profile_path), "driver_sha256": fingerprint(driver_path),
                "backup": str(backup), "evidence": "Manually reviewed documentation; target execution was not tested."}
            report["review_summary"] = {state: sum(self.review_state(record) == state for record in report["records"])
                                        for state in ("resolved", "stale", "unreviewed")}
            atomic_json(self.path, report, ascii_only=True)
        except (OSError, ValueError, RecursionError, KeyboardInterrupt) as error:
            self.save_failed = True
            raise HelpError(f"Save incomplete; inspect files and backup {backup}. Reopen the session before retrying.") from error
        self.report = report
        self.report_fingerprint = fingerprint(self.path)
        self.collection_names = self.current_names()
        draft.original = draft.text
        draft.fingerprints = {path: fingerprint(path) for path in (profile_path, driver_path)}
        return result


def edit_draft(draft):
    """Run the configured editor with a temporary JSON file and no shell evaluation."""
    arguments = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi")
    if not arguments:
        raise HelpError("Set VISUAL or EDITOR to an editor executable and optional arguments.")
    with tempfile.TemporaryDirectory(prefix="cli-help-review-") as folder:
        path = Path(folder) / "draft.json"
        path.write_text(draft.text, encoding="utf-8")
        result = subprocess.run([*arguments, str(path)], shell=False)
        if path.stat().st_size > MAX_DRAFT_BYTES:
            raise HelpError("Editor output exceeds 2 MiB; the previous draft was retained.")
        draft.text = path.read_text(encoding="utf-8")
        if result.returncode:
            raise HelpError("The editor exited unsuccessfully; its draft text was retained for correction.")


def preview_profile(profile):
    """Use the real browser in inspection mode, returning no Readline edit response."""
    import curses
    from ui import load_keys, run_browser
    validate_profile(profile, Path("<preview>"))
    config = os.environ.get("CLI_HELP_CONFIG")
    try:
        return curses.wrapper(run_browser, profile, "", load_keys(Path(config).expanduser() if config else None), True)
    except curses.error as error:
        raise HelpError(f"The terminal cannot display the preview: {error}") from error


def show(value):
    """Print report data without interpreting terminal controls from diagnostics."""
    print(json.dumps(value, ensure_ascii=True, indent=2))


def add_option(draft):
    """Prompt for a literal option and validate the resulting draft profile."""
    document = draft.document()
    category_name = answer("Category [Options]: ") or "Options"
    flag = answer("Literal option flag: ")
    argument = answer("Argument placeholder (blank for none): ")
    argument = "" if argument == "/clear" else argument
    optional = yes_no("Optional argument?") if argument else False
    option = {"flag": flag, "summary": answer("Summary: ")}
    if argument:
        option.update(argument=argument, argument_optional=optional)
    profile = document["profile"]
    category = next((item for item in profile["categories"] if item["name"] == category_name), None)
    if category is None:
        category = {"name": category_name, "options": []}
        profile["categories"].append(category)
    category["options"].append(option)
    validate_profile(profile, Path("<new option>"))
    draft.text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def review_entry(session, index):
    """Keep a selected entry's changes in a draft until an explicit save."""
    draft = session.open_draft(index)
    show(session.report["records"][index])
    print("Use Options, Categories, or Driver for guided corrections; JSON editing remains available.")
    print("Guided fields: Enter keeps, /clear empties optional values, /cancel discards the operation.")
    print("Empty profiles require an added option or manual import before preview/save.")
    while True:
        try:
            action = input("Entry: [o]ptions [c]ategories [d]river [a]dd option [e]dit JSON [m]anual import [p]review [v]alidate [s]ave [b]ack: ").strip().lower()
            if action == "e":
                edit_draft(draft)
            elif action == "o":
                edit_options(draft)
            elif action == "c":
                edit_categories(draft)
            elif action == "d":
                edit_driver(draft)
            elif action == "a":
                add_option(draft)
            elif action == "m":
                kind = input("Source [page/text/roff]: ").strip().lower()
                value = input("Manual name or file path: ").strip()
                manual = input("Fallback manual name (blank for command name): ").strip() if kind != "page" else value
                session.import_source(draft, kind, value, manual or None, Settings.from_environment().timeout)
                print("Manual imported into the draft; save is required to update the collection.")
            elif action == "p":
                selected = preview_profile(session.validate(draft)["profile"])
                if selected:
                    print("Preview selection only: " + selected["flag"])
            elif action == "v":
                session.validate(draft)
                print("Valid profile and driver; command execution was not tested.")
            elif action == "s":
                session.validate(draft)
                if input("Save this profile and driver and mark reviewed? [y/N]: ").strip().lower() == "y":
                    show(session.save(draft))
                    print("Saved and marked reviewed. Original scan findings retained.")
            elif action == "b":
                if draft.text == draft.original or input("Discard unsaved draft? [y/N]: ").strip().lower() == "y":
                    return
            else:
                print("Choose an entry action from the menu.")
        except FormCancelled:
            print("Guided operation cancelled; draft unchanged.")
        except (OSError, ValueError, RecursionError) as error:
            show(str(error))
        except KeyboardInterrupt:
            print("\nAction cancelled; the draft remains open. Use back to discard.")


def run_review(report_path):
    """Run a paginated terminal review queue, defaulting to unresolved scan issues."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise HelpError("Review requires an interactive terminal on standard input and output.")
    locale.setlocale(locale.LC_ALL, "")
    if locale.getpreferredencoding(False).lower().replace("-", "") != "utf8":
        raise HelpError("A UTF-8 terminal locale is required for review.")
    with ReviewSession(report_path) as session:
        page, show_all, search = 0, False, ""
        print("Scan report review. Changes are saved only through the entry Save action.")
        if session.report.get("errors") or session.report.get("inventory_warnings"):
            show({key: session.report.get(key) for key in ("errors", "inventory_warnings")})
        try:
            while True:
                entries = session.entries(show_all, search)
                page = min(page, max(0, (len(entries) - 1) // PAGE_SIZE))
                print(f"\n{'All entries' if show_all else 'Unresolved issues'} | {len(entries)} entries | page {page + 1}")
                for index in entries[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]:
                    record = session.report["records"][index]
                    name = json.dumps(" ".join(record["command"]), ensure_ascii=True)
                    print(f"{index + 1}. {name}: {record['status']} / {session.review_state(record)}")
                action = input("Review: number | [n]ext [p]revious [f]ilter [a]ll/issues [q]uit: ").strip().lower()
                if action == "q":
                    return 0
                if action == "n":
                    page += 1
                elif action == "p":
                    page = max(0, page - 1)
                elif action == "a":
                    show_all, page = not show_all, 0
                elif action == "f":
                    search, page = input("Command contains (blank clears): ").strip(), 0
                elif action.isdecimal() and int(action) - 1 in entries:
                    try:
                        review_entry(session, int(action) - 1)
                    except (OSError, ValueError) as error:
                        show(str(error))
                else:
                    print("Choose an entry number or a menu action.")
        except (EOFError, KeyboardInterrupt):
            print("\nReview closed; unsaved drafts were discarded.")
            return 130
