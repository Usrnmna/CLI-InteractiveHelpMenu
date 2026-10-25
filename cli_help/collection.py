"""Inspect local collections and restore existing review backups with explicit guards."""

from contextlib import ExitStack, contextmanager
import hashlib
from itertools import islice
import json
import os
from pathlib import Path
import re
import stat
import uuid

from core import validate_profile
from command_paths import load_driver_registry
from drivers import parse_driver
from errors import HelpError
from manual_import import atomic_bytes, validate_documents
from value_semantics import ValueContext, validate_profile_semantics, validate_value_semantics


MAX_ENTRIES = 4096
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_COLLECTION_BYTES = 64 * 1024 * 1024
LOCKS = (".scan.lock", ".import.lock")


def numerical_findings(profile, source):
    """Describe optional numerical errors and pending reviews without I/O or mutation."""
    structural = validate_profile_semantics(profile, source=source, mode="structural")
    warnings = []

    def supplied_warnings(metadata, flag, pointer, arity=None, optional=None):
        """Select external uncertainty policy only for an explicitly supplied field."""
        context = ValueContext(source=source, command=tuple(profile["command"]), option=flag,
                               pointer=pointer, argument_count=arity, value_optional=optional)
        warnings.extend(diagnostic for diagnostic in validate_value_semantics(metadata, mode="external",
            context=context, definitions=profile.get("value_definitions")) if diagnostic.severity == "warning")

    for ci, category in enumerate(profile["categories"]):
        for oi, option in enumerate(category["options"]):
            if "value_semantics" in option:
                supplied_warnings(option["value_semantics"], option["flag"], f"/categories/{ci}/options/{oi}/value_semantics",
                    option.get("argument_count", 1) if option.get("argument") else 0, option.get("argument_optional", False))
    if "positional_value_semantics" in profile:
        supplied_warnings(profile["positional_value_semantics"], "<positional_group>", "/positional_value_semantics",
                          (profile.get("positional_group") or {}).get("argument_count", 0), False)
    definitions = profile.get("value_definitions")
    if isinstance(definitions, dict):
        for name in sorted(definitions):
            pointer = "/value_definitions/" + name.replace("~", "~0").replace("/", "~1")
            supplied_warnings({"schema_version": 1, "variants": [{"ref": name}]}, "<definition " + name + ">", pointer)
    findings = [{"code": diagnostic.code, "severity": diagnostic.severity,
                 "locations": [source + diagnostic.pointer], "detail": diagnostic.message,
                 "diagnostic": diagnostic.to_dict()}
                for diagnostic in (*structural, *warnings)]
    document = profile.get("documentation")
    if isinstance(document, dict) and isinstance(document.get("diagnostics"), list):
        for note in document["diagnostics"]:
            if isinstance(note, dict) and note.get("code") == "authoring_semantics_review":
                findings.append({"code": "authoring_semantics_review", "severity": "warning", "locations": [source],
                                 "detail": "Numerical declarations remain inactive pending authored review; inspect source evidence in the profile.",
                                 "command": profile["command"], "option": note.get("option")})
    return findings


class RecoveryIncomplete(HelpError):
    """Retain the safe backup location when per-file restoration is interrupted."""
    def __init__(self, backup):
        super().__init__("Recovery stopped after preserving originals; inspect the retained backup.", "recovery_incomplete")
        self.backup = backup


def validate_scan_report(document):
    """Validate evidence structure without trusting embedded filesystem paths."""
    if (not isinstance(document, dict) or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1 or not isinstance(document.get("records"), list)):
        raise ValueError("Invalid report structure")
    if any(field in document and type(document[field]) is not bool for field in ("finished", "interrupted")):
        raise ValueError("Invalid report state")
    seen = set()
    for record in document["records"]:
        if not isinstance(record, dict) or not isinstance(record.get("command"), list) or not record["command"]:
            raise ValueError("Invalid record structure")
        if any(not isinstance(word, str) for word in record["command"]):
            raise ValueError("Invalid command identity")
        command = tuple(record["command"])
        if command in seen or record.get("status") not in {"success", "needs_adjustment", "failed", "skipped", "pending"}:
            raise ValueError("Invalid record identity or status")
        if not isinstance(record.get("review", {}), dict):
            raise ValueError("Invalid review evidence")
        if "generated" in record and type(record["generated"]) is not bool:
            raise ValueError("Invalid generation evidence")
        seen.add(command)
    return document["records"]


def local_path(root, relative):
    """Reject traversal and symlinks, including links into the selected root."""
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(part in ("..", ".") for part in path.parts):
        raise HelpError("A collection path is unsafe; no external path is followed.", "unsafe_collection_path")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise HelpError("A collection path is a symbolic link; inspect it locally.", "unsafe_collection_path")
    return current


def backup_items(document):
    """Validate existing review manifests without following recorded paths."""
    if not isinstance(document, dict) or set(document) != {"files"} or not isinstance(document["files"], list) or not document["files"]:
        raise ValueError("Invalid backup manifest")
    targets, sources = set(), set()
    for item in document["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "backup"}:
            raise ValueError("Invalid backup entry")
        target, source = item["path"], item["backup"]
        if not isinstance(target, str):
            raise ValueError("Invalid backup target")
        path = Path(target)
        if (path.is_absolute() or target != path.as_posix() or ".." in path.parts or target in targets or not target.endswith(".json")
                or not (len(path.parts) == 2 and path.parts[0] in ("profiles", "drivers") or target == "scan-report.json")):
            raise ValueError("Invalid backup target")
        if source is not None and (not isinstance(source, str) or not re.fullmatch(r"[0-9]+\.json", source) or source in sources):
            raise ValueError("Invalid backup source")
        targets.add(target)
        sources.add(source)
    return document["files"]


@contextmanager
def directory_descriptor(root, relative, expected=None):
    """Pin a collection directory without following swapped parent symlinks."""
    with ExitStack() as stack:
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        stack.callback(os.close, descriptor)
        if Path(relative).is_absolute():
            raise HelpError("Unsafe recovery directory.", "unsafe_collection_path")
        parts = Path(relative).parts if relative != "." else ()
        for part in parts:
            if part in ("..", "."):
                raise HelpError("Unsafe recovery directory.", "unsafe_collection_path")
            descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            stack.callback(os.close, descriptor)
        metadata = os.fstat(descriptor)
        if expected is not None and (metadata.st_dev, metadata.st_ino) != (expected["device"], expected["inode"]):
            raise HelpError("A recovery directory changed; repeat inspection.", "collection_changed")
        yield descriptor


def read_entry(root, relative):
    """Read one bounded regular file without waiting on special files or following links."""
    path = local_path(root, relative)
    with directory_descriptor(root, str(path.parent.relative_to(root))) as parent:
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=parent)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
            raise HelpError("Collection entries must be bounded regular files.", "unsafe_collection_file")
        data = bytearray()
        while len(data) <= MAX_FILE_BYTES:
            chunk = os.read(descriptor, min(65536, MAX_FILE_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        after = os.fstat(descriptor)
        if len(data) > MAX_FILE_BYTES or (before.st_ino, before.st_mtime_ns, before.st_ctime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_ctime_ns, after.st_size):
            raise HelpError("The collection changed during inspection; repeat the check.", "collection_changed")
        identity = file_identity(before, hashlib.sha256(data).hexdigest())
        return bytes(data), identity
    finally:
        os.close(descriptor)


def file_identity(metadata, digest):
    """Use one identity representation for bounded files and newly created empty locks."""
    return {"device": metadata.st_dev, "inode": metadata.st_ino, "size": metadata.st_size,
            "mtime_ns": metadata.st_mtime_ns, "ctime_ns": metadata.st_ctime_ns, "sha256": digest}


def snapshot_digest(entries):
    """Bind an operator choice to file identities and content, without returning contents."""
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def validated_driver(document):
    """Apply both local schema and built-in overlay arity constraints."""
    name, driver = parse_driver(document)
    baseline = load_driver_registry().get(name)
    if baseline and (baseline.global_values | driver.global_values) & (baseline.global_flags | driver.global_flags):
        raise ValueError("Conflicting global arity")
    return name, driver


def inspect_state(directory):
    """Return a public report and private bounded bytes for validation/recovery."""
    root = directory.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise HelpError("Select an existing collection directory.", "collection_missing")
    root_stat = root.stat()
    entries, data, findings = {".": {"kind": "directory", "device": root_stat.st_dev, "inode": root_stat.st_ino}}, {}, []
    complete = True
    visited = 0
    total_bytes = 0

    def finding(code, severity, locations, detail):
        findings.append({"code": code, "severity": severity, "locations": locations, "detail": detail})

    def visit(relative, depth=0):
        nonlocal complete, visited, total_bytes
        if visited >= MAX_ENTRIES or total_bytes > MAX_COLLECTION_BYTES:
            if complete:
                finding("collection_limit", "error", [], "Inspection entry limit reached.")
            complete = False
            return
        visited += 1
        try:
            path = local_path(root, relative)
            is_directory = path.is_dir()
            if relative in ("profiles", "drivers", ".review-backups") and not is_directory:
                raise HelpError("A collection directory is not a directory; inspect it locally.", "collection_layout_invalid")
            if is_directory:
                if relative.endswith(".json"):
                    raise HelpError("JSON metadata must be regular files, not directories.", "unsafe_collection_file")
                with directory_descriptor(root, relative) as descriptor:
                    metadata = os.fstat(descriptor)
                    entries[relative] = {"kind": "directory", "device": metadata.st_dev, "inode": metadata.st_ino}
                    with os.scandir(descriptor) as iterator:
                        names = sorted(entry.name for entry in islice(iterator, MAX_ENTRIES + 1))
                if len(names) > MAX_ENTRIES or depth > 3:
                    raise HelpError("Inspection limits reached; narrow the collection before recovery.", "collection_limit")
                for name in names:
                    visit(str(Path(relative) / name), depth + 1)
            else:
                if len(entries) >= MAX_ENTRIES:
                    raise HelpError("Inspection limits reached; narrow the collection before recovery.", "collection_limit")
                raw, identity = read_entry(root, relative)
                total_bytes += len(raw)
                if total_bytes > MAX_COLLECTION_BYTES:
                    raise HelpError("Collection byte limit reached.", "collection_limit")
                entries[relative], data[relative] = identity, raw
                if Path(relative).name.startswith(".cli-help-write-"):
                    finding("temporary_write_present", "warning", [relative], "An interrupted write may require manual inspection; no temporary file is promoted automatically.")
        except (OSError, ValueError, RuntimeError) as error:
            complete = False
            finding(getattr(error, "code", "collection_unreadable"), "error", [relative],
                    "The entry is unsafe, unreadable, changing, or exceeds inspection limits; no contents are included.")

    for name in ("profiles", "drivers", ".review-backups", *LOCKS):
        path = root / name
        if path.exists() or path.is_symlink():
            visit(name)
    with directory_descriptor(root, ".", entries["."]) as descriptor:
        with os.scandir(descriptor) as iterator:
            names = sorted(entry.name for entry in islice(iterator, MAX_ENTRIES + 1))
    if len(names) > MAX_ENTRIES:
        complete = False
        finding("collection_limit", "error", [], "Too many root entries for bounded inspection.")
    for name in names[:MAX_ENTRIES]:
        if name.endswith(".json") or name.startswith(".cli-help-write-"):
            visit(name)
    for lock in LOCKS:
        if lock in entries:
            finding("lock_ownership_uncertain", "warning", [lock],
                    "A lock exists. Age and PID absence do not establish ownership or staleness; stop and inspect writers before manual removal.")
    profiles, drivers, documents = {}, {}, {}
    for relative, raw in data.items():
        if not relative.endswith(".json"):
            continue
        try:
            document = json.loads(raw)
            documents[relative] = document
            if Path(relative).parent == Path("profiles"):
                validate_profile(document, Path("<collection profile>"))
                findings.extend(numerical_findings(document, relative))
                command = tuple(document["command"])
                if command in profiles:
                    finding("duplicate_profile", "error", [relative, profiles[command][0]], "Multiple profiles declare the same command path.")
                profiles[command] = (relative, document)
            elif Path(relative).parent == Path("drivers"):
                if len(raw) > 256 * 1024:
                    raise ValueError("Driver exceeds its schema limit")
                name, driver = validated_driver(document)
                if name in drivers:
                    finding("duplicate_driver", "error", [relative, drivers[name][0]], "Multiple files declare the same executable driver.")
                drivers[name] = (relative, document, driver)
        except (ValueError, TypeError, KeyError, RecursionError):
            severity = "warning" if relative.startswith(".review-backups/") else "error"
            finding("collection_json_invalid", severity, [relative], "JSON or schema validation failed; inspect the file locally.")
    for command, (relative, profile) in profiles.items():
        driver = drivers.get(command[0])
        route = driver[2].paths.get(command[1:]) if driver else None
        if route is None:
            finding("profile_route_missing", "error" if profile.get("imported_from") else "warning", [relative],
                    "No paired explicit driver route exists. Pure static collections may intentionally omit drivers.")
        elif not isinstance(profile.get("imported_from", {}), dict):
            finding("import_metadata_invalid", "warning", [relative], "Imported provenance requires an object.")
        elif profile.get("imported_from", {}).get("manual") not in (None, route.manual):
            finding("manual_metadata_mismatch", "warning", [relative, driver[0]], "Imported manual provenance differs from the driver route.")
    for name, (relative, _, driver) in drivers.items():
        if any((name, *path) not in profiles for path in driver.paths):
            finding("driver_profile_missing", "warning", [relative], "A driver route has no static profile; discovery-only routes may be intentional.")
    for relative, document in documents.items():
        if "/" in relative or relative != "scan-report.json" and (not isinstance(document, dict) or "records" not in document):
            continue
        try:
            validate_scan_report(document)
            if not document.get("finished") or document.get("interrupted"):
                finding("scan_incomplete", "warning", [relative], "Scan evidence records an incomplete or interrupted operation.")
            seen = set()
            for record in document["records"]:
                command = tuple(record["command"])
                if not command or any(not isinstance(word, str) for word in command) or command in seen:
                    raise ValueError
                seen.add(command)
                pair = profiles.get(command)
                driver = drivers.get(command[0])
                route = driver[2].paths.get(command[1:]) if driver else None
                if record.get("generated") and (pair is None or route is None):
                    finding("scan_pair_missing", "error", [relative], "Recorded generated output is missing a profile or driver route.")
                review = record.get("review", {})
                if review.get("status") == "resolved":
                    if pair is None or driver is None or any(
                            entries[path].get("sha256") != review.get(field)
                            for path, field in ((pair[0], "profile_sha256"), (driver[0], "driver_sha256"))):
                        finding("review_evidence_stale", "warning", [relative], "Reviewed files differ from recorded review fingerprints.")
        except (ValueError, TypeError, KeyError, AttributeError):
            finding("scan_report_invalid", "error", [relative], "Scan/review evidence has an invalid structure or duplicate identities.")
    backups = sorted({Path(name).parts[1] for name in data if name.startswith(".review-backups/") and Path(name).name == "manifest.json"})
    for name in backups:
        manifest = ".review-backups/" + name + "/manifest.json"
        try:
            for item in backup_items(documents.get(manifest)):
                if item["backup"] is not None and ".review-backups/" + name + "/" + item["backup"] not in data:
                    raise ValueError("Missing backup source")
        except (ValueError, TypeError):
            finding("backup_manifest_invalid", "warning", [manifest], "The backup manifest is invalid or references missing data; retain it for local inspection.")
    for name, entry in entries.items():
        if entry.get("kind") == "directory" and Path(name).parent == Path(".review-backups") and name + "/manifest.json" not in data:
            finding("backup_manifest_missing", "warning", [name], "A retained backup directory lacks a readable manifest; inspect it before recovery.")
    status = "invalid" if any(item["severity"] == "error" for item in findings) else "attention_required" if findings else "ok"
    report = {"schema_version": 1, "mode": "check_collection", "status": status, "directory": str(root),
              "inspection_complete": complete, "snapshot": snapshot_digest(entries), "files": entries,
              "findings": findings, "review_backups": backups,
              "execution": "passive; no targets, discovery, writes, or lock changes"}
    return root, report, data


def inspect_collection(directory):
    """Expose only safe locations, reason codes, and snapshot evidence."""
    return inspect_state(directory)[1]


def restore_review_backup(directory, backup_name, expected_snapshot):
    """Restore a validated existing review backup after an explicit snapshot choice.

    Existing scanner/importer locks exclude cooperative writers. Every source
    and target is rechecked before replacement. Originals are backed up first;
    interruption retains that backup. No lock is inferred stale or removed.
    """
    root, report, data = inspect_state(directory)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", backup_name):
        raise HelpError("Select a literal backup identifier from collection inspection.", "invalid_backup")
    if not report["inspection_complete"] or report["snapshot"] != expected_snapshot:
        raise HelpError("Collection evidence is incomplete or changed; repeat inspection.", "collection_changed")
    if any(lock in report["files"] for lock in LOCKS):
        raise HelpError("Lock ownership is uncertain; inspect and stop writers before recovery.", "collection_locked")
    prefix = ".review-backups/" + backup_name + "/"
    try:
        manifest = json.loads(data[prefix + "manifest.json"])
        plan = {}
        for item in backup_items(manifest):
            target, source = item["path"], item["backup"]
            path = Path(target)
            local_path(root, target)
            if target in plan or not target.endswith(".json") or not (
                    len(path.parts) == 2 and path.parts[0] in ("profiles", "drivers") or target == "scan-report.json"):
                raise ValueError
            if source is None:
                if (root / target).exists():
                    raise HelpError("This backup requires deleting a later file; retain it for explicit manual review.", "restore_requires_removal")
                continue
            if not isinstance(source, str) or not re.fullmatch(r"[0-9]+\.json", source):
                raise ValueError
            raw = data[prefix + source]
            plan[target] = (prefix + source, json.loads(raw))
        effective = {name: json.loads(raw) for name, raw in data.items()
                     if name.endswith(".json") and Path(name).parent in (Path("profiles"), Path("drivers")) and name not in plan}
        effective.update({name: document for name, (_, document) in plan.items()})
        profiles = [document for name, document in effective.items() if Path(name).parent == Path("profiles")]
        drivers = [document for name, document in effective.items() if Path(name).parent == Path("drivers")]
        drivers_by_name = {}
        for document in drivers:
            name, _ = validated_driver(document)
            if name in drivers_by_name:
                raise ValueError
            drivers_by_name[name] = document
        for profile in profiles:
            validate_profile(profile, Path("<restored profile>"))
            driver = drivers_by_name.get(profile["command"][0])
            if driver is None:
                raise ValueError
            validate_documents(profile, driver)
        if len(profiles) != len({tuple(profile["command"]) for profile in profiles}):
            raise ValueError
        for name in effective:
            raw = data[plan[name][0]] if name in plan else data[name]
            if Path(name).parent == Path("drivers") and len(raw) > 256 * 1024:
                raise ValueError
        for name, (_, document) in plan.items():
            if len(Path(name).parts) == 1:
                validate_scan_report(document)
    except HelpError as error:
        if error.code == "restore_requires_removal":
            raise
        raise HelpError("The selected backup does not restore valid metadata; inspect it locally.", "invalid_backup") from None
    except (KeyError, ValueError, TypeError, RecursionError):
        raise HelpError("The selected backup is incomplete, invalid, or does not restore a valid pair.", "invalid_backup") from None
    plan = {target: value for target, value in plan.items() if data.get(target) != data[value[0]]}
    if not plan:
        return {"schema_version": 1, "mode": "recover_collection", "status": "unchanged", "restored": []}
    owned = {}
    with ExitStack() as stack:
        root_fd = stack.enter_context(directory_descriptor(root, ".", report["files"]["."]))
        for lock in LOCKS:
            try:
                descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=root_fd)
                owned[lock] = file_identity(os.fstat(descriptor), hashlib.sha256(b"").hexdigest())
                os.close(descriptor)
            except FileExistsError:
                raise HelpError("A collection writer acquired a lock; repeat inspection after it finishes.", "collection_locked") from None
            def release(name=lock):
                try:
                    metadata = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
                    if stat.S_ISREG(metadata.st_mode) and file_identity(metadata, hashlib.sha256(b"").hexdigest()) == owned[name]:
                        os.unlink(name, dir_fd=root_fd)
                except (OSError, ValueError):
                    pass
            stack.callback(release)
        _, current, _ = inspect_state(root)
        observed = {name: value for name, value in current["files"].items() if name not in owned}
        if snapshot_digest(observed) != expected_snapshot:
            raise HelpError("The collection changed before recovery; no files were restored.", "collection_changed")
        backup = local_path(root, ".review-backups") / ("recovery-" + uuid.uuid4().hex)
        with directory_descriptor(root, ".review-backups", report["files"].get(".review-backups")) as parent:
            os.mkdir(backup.name, mode=0o700, dir_fd=parent)
            backup_fd = os.open(backup.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        stack.callback(os.close, backup_fd)
        originals = []
        for index, target in enumerate(plan):
            original = data.get(target)
            originals.append({"path": target, "backup": str(index) + ".json" if original is not None else None})
            if original is not None:
                atomic_bytes(backup / (str(index) + ".json"), original, directory_fd=backup_fd)
        atomic_bytes(backup / "manifest.json", (json.dumps({"files": originals}, indent=2) + "\n").encode(), directory_fd=backup_fd)
        expected_metadata = {name: identity for name, identity in report["files"].items()
                             if name.endswith(".json") and Path(name).parent in (Path("."), Path("profiles"), Path("drivers"))}

        def recheck_metadata():
            """Reject new, removed, or changed metadata that would invalidate the plan."""
            names = set()
            for parent in (".", "profiles", "drivers"):
                if parent not in report["files"]:
                    if (root / parent).exists() or (root / parent).is_symlink():
                        raise HelpError("The collection metadata changed; repeat inspection.", "collection_changed")
                    continue
                with directory_descriptor(root, parent, report["files"][parent]) as descriptor:
                    with os.scandir(descriptor) as iterator:
                        children = [entry.name for entry in islice(iterator, MAX_ENTRIES + 1)]
                    if len(children) > MAX_ENTRIES:
                        raise HelpError("Collection bounds changed; repeat inspection.", "collection_changed")
                    names.update(str(Path(parent) / name) for name in children if name.endswith(".json"))
            if names != set(expected_metadata):
                raise HelpError("The collection metadata changed; repeat inspection.", "collection_changed")
            if any(read_entry(root, name)[1] != identity for name, identity in expected_metadata.items()):
                raise HelpError("The collection metadata changed; repeat inspection.", "collection_changed")
        try:
            for target, (source, document) in plan.items():
                def recheck():
                    """Repeat evidence checks after staging, immediately before replacement."""
                    recheck_metadata()
                    for name in (source, prefix + "manifest.json", *owned):
                        expected = owned.get(name, report["files"].get(name))
                        if read_entry(root, name)[1] != expected:
                            raise HelpError("Source evidence or lock ownership changed; retain the recovery backup.", "collection_changed")
                    path = local_path(root, target)
                    actual = read_entry(root, target)[1] if path.exists() else None
                    if actual != report["files"].get(target):
                        raise HelpError("A target changed before replacement; retain the recovery backup.", "collection_changed")
                recheck()
                path = local_path(root, target)
                relative_parent = str(path.parent.relative_to(root))
                if relative_parent not in report["files"]:
                    raise HelpError("A recovery directory changed; repeat inspection.", "collection_changed")
                with directory_descriptor(root, relative_parent, report["files"].get(relative_parent)) as target_fd:
                    atomic_bytes(path, data[source], directory_fd=target_fd, before_replace=recheck)
                restored_identity = read_entry(root, target)[1]
                if restored_identity["sha256"] != report["files"][source]["sha256"]:
                    raise HelpError("A restored target changed; retain the recovery backup.", "collection_changed")
                expected_metadata[target] = restored_identity
        except (OSError, ValueError, KeyboardInterrupt):
            raise RecoveryIncomplete(backup) from None
    return {"schema_version": 1, "mode": "recover_collection", "status": "restored",
            "backup": str(backup), "restored": list(plan), "boundary": "Atomic per file; no multi-file transaction or target execution."}
