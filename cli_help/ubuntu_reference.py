"""Resolve Ubuntu's packaged documentation for installed commands with missing help."""

import json
import os
import shutil
from pathlib import Path
import re

from errors import HelpError


REFERENCE = Path(__file__).resolve().parents[1] / "config" / "ubuntu-reference"
NAME = re.compile(r"(?:[\w.+][\w.+-]*|\[|gnu\[)\Z", re.ASCII)
BIN_DIRS = {"/usr/bin", "/usr/sbin", "/usr/games", "/snap/bin"}


def ubuntu_edition():
    """Identify supported images without running a program or sourcing OS shell text."""
    for filename in ("/etc/os-release", "/usr/lib/os-release"):
        try:
            fields = dict(line.split("=", 1) for line in Path(filename).read_text().splitlines()
                          if "=" in line and not line.startswith("#"))
        except OSError:
            continue
        if fields.get("ID", "").strip('"') == "ubuntu":
            return {"24.04": "noble", "26.04": "resolute"}.get(fields.get("VERSION_ID", "").strip('"'))
        break
    return None


def reference_record(name, executable):
    """Read a single alphabetical shard for a system executable and its Ubuntu edition.

    A same-named custom executable, a different provider behind an alternatives
    link, or a different kernel tool directory cannot inherit another tool's record.
    """
    if not NAME.fullmatch(name) or name in (".", ".."):
        return None
    directory = str(Path(executable).parent.resolve())
    if directory not in BIN_DIRS and not re.fullmatch(r"/usr/lib/linux-tools-[\d.-]+", directory):
        return None
    return lookup_record(name, ubuntu_edition(), directory, os.path.realpath(executable))


def lookup_record(name, edition, directory, target):
    """Match the reference identity against an observed image path or an installed executable."""
    if edition not in {"noble", "resolute"} or not NAME.fullmatch(name) or name in (".", ".."):
        return None
    initial = name[0].lower() if name[0].isascii() and name[0].isalnum() else "other"
    source = REFERENCE / edition / (initial + ".jsonl")
    prefix = '{"command":' + json.dumps(name) + ","
    try:
        with source.open(encoding="utf-8") as lines:
            for line in lines:
                if not line.startswith(prefix):
                    continue
                record = json.loads(line)
                if record.get("directory", directory) != directory:
                    continue
                targets = record.get("targets")
                if not targets and (not target.startswith("/usr/") or target.startswith("/usr/local/")):
                    continue
                if targets and target not in targets:
                    continue
                if directory.startswith("/usr/lib/linux-tools-") and record.get("kernel") != directory:
                    continue
                return record
    except FileNotFoundError:
        pass
    return None


def installed_reference(record):
    """Reject a known revision mismatch using passive local dpkg metadata.

    Documentation can live in a separate package that minimal installations
    omit. A verified image target can still use the labelled release reference.
    """
    if record.get("location_only"):
        return
    if "snap_revision" in record:
        try:
            revision = (Path("/snap") / record["package"] / "current").readlink().name
        except OSError:
            revision = None
        if revision != record["snap_revision"]:
            raise HelpError(f"Consult {record['page']} for the installed {record['package']} snap. "
                            f"The reference covers revision {record['snap_revision']}.", "usage_guidance")
        if not record.get("launcher_package"):
            return
    provider = record.get("launcher_package", record["package"])
    expected = record.get("launcher_version", record["version"])
    try:
        with Path("/var/lib/dpkg/status").open(encoding="utf-8", errors="replace") as status:
            package = version = state = ""
            for line in status:
                if line.startswith("Package: "):
                    package = line[9:].strip()
                elif line.startswith("Version: "):
                    version = line[9:].strip()
                elif line.startswith("Status: "):
                    state = line[8:].strip()
                elif not line.strip():
                    if package == provider and state.endswith(" installed"):
                        if version != expected:
                            raise HelpError(f"Installed {package} {version} differs from the Ubuntu reference "
                                            f"{expected}. Consult {record['page']} for the installed edition.",
                                            "usage_guidance")
                        return
                    package = version = state = ""
            if not record.get("targets"):
                raise HelpError(f"The installed package database does not identify {record['package']} "
                                f"as the provider for this reference. Consult {record['page']}.", "usage_guidance")
    except OSError:
        return


def keyword_prefix(command, query):
    """Check partial root keywords against passive reference data before permitting discovery."""
    executable = shutil.which(command)
    if not executable:
        return False
    record = reference_record(Path(command).name, executable)
    return bool(record and any(word.startswith(query) for word in record["keywords"]))


def reference_profile(record, build_profile, validate):
    """Reconstruct a conservative root menu from reviewed literal declarations.

    The standard parser supplies presentation and preservation metadata. The
    recorded synopsis determines the arity and permitted insertion form. An
    empty declaration list yields reachable source and usage guidance.
    """
    name = record["command"]
    source = f"Ubuntu reference {record['package']} {record['version']}, {record['page']}"
    usage = record.get("usage") or name
    if record.get("location_only"):
        raise HelpError(usage + " Command-specific declarations still need review.", "usage_guidance")
    guidance = f"{usage} — see {record['page']} in {record['package']} {record['version']}."
    if record.get("documentation"):
        guidance += " " + record["documentation"]
    if not record["options"] and not record["keywords"]:
        raise HelpError(guidance, "usage_guidance")
    options = []
    shapes = {}
    for flag, arg, count, optional, style in record["options"]:
        detail = record.get("descriptions", {}).get(flag)
        summary = detail or (f"{flag} {arg}" if arg else f"{flag} ({record['page']})")
        options.append(f"  {flag}    {summary}")
        shapes[flag] = (arg, count, optional, style, summary)
    categories = []
    if options:
        # Parse the normalized declaration column as a generic utility. Some
        # edition-specific live adapters require a complete native manual.
        parsed = build_profile(["ubuntu-reference"], [(source, "Options:\n" + "\n".join(options))])
        rows = []
        for category in parsed["categories"]:
            for row in category["options"]:
                if row["flag"] not in shapes:
                    continue
                arg, count, optional, style, summary = shapes[row["flag"]]
                row = {"flag": row["flag"], "summary": summary, "detail": guidance}
                if count:
                    row.update(argument=arg, argument_count=count, argument_optional=optional)
                    if count == 1:
                        row["argument_style"] = style
                rows.append(row)
        if len(rows) != len(shapes):
            raise HelpError(f"Inspect the packaged declarations for {name}.", "reference_invalid")
        categories.append({"name": "Options", "options": rows})
    if record["keywords"]:
        categories.append({"name": "Commands", "options": [
            {"kind": "keyword", "flag": word, "summary": record.get("descriptions", {}).get(word, f"{name} {word}"),
             "detail": guidance} for word in record["keywords"]]})
    profile = {"command": [name], "description": guidance, "stop_at_positional": True, "categories": categories,
               "discovery": {"scope": "top-level", "sources": [source], "warnings": [],
                             "reference_sha256": record["sha256"]}}
    validate(profile, Path("<Ubuntu reference>"))
    return profile
