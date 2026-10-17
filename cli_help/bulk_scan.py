"""Inventory installed executables and generate documentation without invoking them."""

from collections import Counter
from datetime import datetime, timezone
import fnmatch
import os
from pathlib import Path
import shutil

from command_paths import load_driver_registry
from core import HelpError
from discovery import ProbeError, ProbeExitError, build_profile, clean_output, parse_option_line
from drivers import WORD
from manual_import import ManualCollection, atomic_json, read_manual


def inventory_commands(directories=None) -> tuple[list[dict], list[dict]]:
    """Inventory executable files with PATH precedence, retaining shadowed paths.

    Directories are not traversed recursively. Executable symlinks retain their
    invocation names because aliases may have different manuals. Shell functions
    and builtins are not installed executable files and are not enumerated.
    """
    directories = directories if directories is not None else os.environ.get("PATH", os.defpath).split(os.pathsep)
    commands, warnings, seen = {}, [], set()
    for directory in directories:
        path = Path(directory or ".").expanduser().absolute()
        if str(path) in seen:
            continue
        seen.add(str(path))
        try:
            with os.scandir(path) as entries:
                files = sorted(entries, key=lambda entry: entry.name)
            for entry in files:
                try:
                    if not entry.is_file() or not os.access(entry.path, os.X_OK):
                        continue
                    if entry.name in commands:
                        commands[entry.name]["shadowed"].append(entry.path)
                    else:
                        commands[entry.name] = {"command": [entry.name], "executable": entry.path, "shadowed": []}
                except OSError as error:
                    warnings.append({"path": entry.path, "reason": str(error)})
        except OSError as error:
            warnings.append({"path": str(path), "reason": str(error)})
    return [commands[name] for name in sorted(commands)], warnings


def manual_review_issues(text: str) -> list[dict]:
    """Flag visible declaration forms that the literal-option parser cannot accept.

    This is a review heuristic, not a completeness proof. Description lines can
    resemble declarations; reported samples require manual inspection.
    """
    unsupported = []
    for line in clean_output(text).splitlines():
        candidate = line.strip()
        if candidate.startswith("-") and len(candidate) > 1 and parse_option_line(candidate) is None:
            unsupported.append(candidate[:160])
    if unsupported:
        return [{"code": "unsupported_declarations", "count": len(unsupported), "samples": unsupported[:10],
                 "action": "Review omitted declaration forms and edit the generated profile if required."}]
    return []


def prepare_records(commands, registry, includes, excludes, subcommands):
    """Create deterministic scan jobs without guessing subcommands from filenames."""
    records = []
    for command in commands:
        name = command["command"][0]
        if includes and not any(fnmatch.fnmatchcase(name, pattern) for pattern in includes) or any(
            fnmatch.fnmatchcase(name, pattern) for pattern in excludes
        ):
            records.append({**command, "status": "skipped", "reason": "filtered", "generated": False})
            continue
        if not WORD.fullmatch(name):
            records.append({**command, "status": "needs_adjustment", "reason": "unsupported_command_name", "generated": False,
                            "action": "The literal command-name schema cannot represent this executable name."})
            continue
        driver = registry.get(name)
        root_route = driver.paths.get(()) if driver else None
        jobs = [((), root_route.manual if root_route else name)]
        if subcommands and driver:
            jobs.extend((path, route.manual) for path, route in sorted(driver.paths.items()) if path)
        for path, manual in jobs:
            record = {**command, "command": [name, *path], "manual": manual, "generated": False}
            if not manual:
                record.update(status="needs_adjustment", reason="no_manual_route",
                              action="Add a manual name to the driver or supply a static profile. Executable help is not probed by the scanner.")
            else:
                record.update(status="pending")
            records.append(record)
    return records


def scan_record(record, collection, registry, timeout, replace):
    """Render one manual, classify its evidence, and persist only validated output."""
    command = record["command"]
    if collection.contains(command) and not replace:
        return {**record, "status": "skipped", "reason": "existing_entry",
                "action": "Existing profile or route preserved. Use --replace only to regenerate this entry."}
    try:
        text, label, manual = read_manual(command, record["manual"], timeout=timeout)
    except ProbeExitError as error:
        # man-db reserves exit status 16 for a missing requested manual page.
        if error.returncode == 16:
            return {**record, "status": "needs_adjustment", "reason": "missing_manual",
                    "action": "Install the matching manual, configure a different manual name, or import supplied documentation."}
        return {**record, "status": "failed", "reason": "renderer_exit", "error": str(error),
                "action": "Check the manual renderer and its dependencies."}
    except (OSError, ProbeError, HelpError) as error:
        return {**record, "status": "failed", "reason": "manual_read_failed", "error": str(error),
                "action": "Inspect the rendering error, timeout, permissions, or output limit before retrying."}
    try:
        profile = build_profile(command, [(label, text)])
    except HelpError as error:
        return {**record, "status": "needs_adjustment", "reason": "unparsed_manual", "error": str(error),
                "action": "The manual has no usable option declarations. Supply a curated profile or a better manual source."}
    profile["imported_from"] = {"source": label, "manual": manual}
    driver = registry.get(command[0])
    issues = manual_review_issues(text)
    if len(command) == 1 and driver and any(driver.paths):
        issues.append({"code": "root_only", "action": "This profile covers root options. Use --scan-subcommands for driver-declared paths."})
    try:
        result = collection.save(profile, manual, replace, driver_defaults=driver)
    except (OSError, ValueError) as error:
        return {**record, "status": "failed", "reason": "write_failed", "error": str(error),
                "action": "Inspect destination permissions and the profile/driver pair; a complete profile may precede a failed driver write."}
    return {**record, **result, "status": "needs_adjustment" if issues else "success", "generated": True,
            "issues": issues, "reason": "review_generated_profile" if issues else "manual_imported"}


def scan_installed(output_dir: Path, directories=None, includes=(), excludes=(), limit=0,
                   subcommands=False, timeout=2.0, replace=False, registry=None, progress=None) -> dict:
    """Generate a manual-only collection with atomic, per-entry JSON checkpoints.

    Existing entries are skipped before rendering unless replacement is explicit.
    Interruptions preserve completed output and mark remaining jobs skipped. A
    scan-wide lock prevents competing scans from overwriting each other's report;
    the collection lock also excludes concurrent single-manual imports.
    """
    if not isinstance(limit, int) or limit < 0 or not 0.05 <= timeout <= 30:
        raise HelpError("Scan limit must be nonnegative and timeout must be 0.05-30 seconds.")
    registry = load_driver_registry() if registry is None else registry
    commands, warnings = inventory_commands(directories)
    destination = output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    lock = destination / ".scan.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise HelpError(f"Another scan is active or interrupted: {lock}. Inspect that scan before removing its lock.") from error
    os.close(descriptor)
    report_path = destination / "scan-report.json"
    report = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
              "finished": False, "interrupted": False, "report": str(report_path),
              "output_directory": str(destination), "inventory_count": len(commands),
              "inventory_warnings": warnings, "errors": [],
              "settings": {"include": list(includes), "exclude": list(excludes), "limit": limit,
                           "subcommands": subcommands, "timeout": timeout, "replace": replace},
              "records": prepare_records(commands, registry, includes, excludes, subcommands),
              "evidence_boundary": "Only man is invoked. Generated options and argument arity are inferred; success does not prove complete command compatibility."}

    def checkpoint():
        counts = Counter(record["status"] for record in report["records"])
        report["summary"] = {status: counts[status] for status in ("success", "needs_adjustment", "failed", "skipped", "pending")}
        report["summary"]["generated"] = sum(record["generated"] for record in report["records"])
        # POSIX filenames can contain undecodable bytes represented as Python
        # surrogates. Escaped JSON preserves those inventory entries safely.
        atomic_json(report_path, report, ascii_only=True)

    try:
        checkpoint()
        try:
            if not shutil.which("man"):
                raise HelpError("The man executable is unavailable; no commands were invoked.")
            with ManualCollection(destination) as collection:
                attempted = 0
                for index, record in enumerate(report["records"]):
                    if record["status"] != "pending":
                        continue
                    preserved = collection.contains(record["command"]) and not replace
                    if not preserved:
                        if limit and attempted >= limit:
                            record.update(status="skipped", reason="limit")
                            continue
                        attempted += 1
                    report["records"][index] = scan_record(record, collection, registry, timeout, replace)
                    checkpoint()
                    if progress:
                        progress(report["records"][index])
        except KeyboardInterrupt:
            report["interrupted"] = True
        except (OSError, ValueError) as error:
            report["errors"].append(str(error))
        for record in report["records"]:
            if record["status"] == "pending":
                record.update(status="skipped", reason="interrupted" if report["interrupted"] else "scan_error")
                record["action"] = "Retry the scan; inspect any partial profile/driver pair before using --replace."
        report["finished"] = True
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        checkpoint()
        return report
    finally:
        lock.unlink(missing_ok=True)
