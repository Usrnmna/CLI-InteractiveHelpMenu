"""Validate the Ubuntu inventory dispositions and replay the packaged reference without executing targets."""

import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from bash_builtins import BUILTINS
from core import HelpError, validate_profile
from discovery import build_profile
from ubuntu_reference import REFERENCE, reference_profile


def read_rows(name):
    """Read the original tab-delimited image or ranking keys and the batch evidence columns."""
    with (ROOT / "docs/ubuntu-command-coverage" / name).open(encoding="utf-8") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def replay(edition):
    """Check every distinct provider and declaration through the installed menu builder."""
    forms = {}
    identities = set()
    for file in sorted((REFERENCE / edition).glob("*.jsonl")):
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            record = json.loads(line)
            name = record["command"]
            identity = (name, record.get("directory"), tuple(record.get("targets", ())))
            expected_shard = name[0].lower() if name[0].isascii() and name[0].isalnum() else "other"
            if identity in identities or file.stem != expected_shard or not re.fullmatch("[a-f0-9]{64}", record["sha256"]):
                raise ValueError(f"{file}:{number} has a duplicate or invalid reference identity")
            identities.add(identity)
            try:
                profile = reference_profile(record, build_profile, validate_profile)
                count = sum(len(c["options"]) for c in profile["categories"])
                if count != len(record["options"]) + len(record["keywords"]):
                    raise ValueError(f"{name} lost a declaration")
                code = f"R{count}"
            except HelpError as exc:
                if exc.code != "usage_guidance" or record["options"] or record["keywords"]:
                    raise
                code = "L" if record.get("location_only") else "RU"
            forms.setdefault(name, set()).add(code)
    return forms


def check():
    """Reconcile exact inventory keys, image availability, menu sizes and explicit guidance."""
    shipped = read_rows("shipped.tsv")
    kernel = read_rows("kernel-companions.tsv")
    optional = read_rows("optional.tsv")
    if len({r["Command"] for r in shipped}) != len(shipped) or len({r["Canonical filesystem path"] for r in kernel}) != len(kernel):
        raise ValueError("Duplicate shipped command or kernel path")
    representatives = [int(r["Rank if selected"]) for r in optional if r["Ranking representative"] == "yes" and r["Rank if selected"]]
    if sorted(representatives) != list(range(1, 101)):
        raise ValueError("Expected exactly one representative per rank")
    resolute, noble = replay("resolute"), replay("noble")
    profiles = [key.removesuffix(" result") for key in shipped[0] if key.endswith(" result")]
    if len(profiles) != 6:
        raise ValueError("Expected six image profiles")
    guidance = {(row["Command"], image) for row in shipped for image in profiles
                if {"BU", "RU"}.intersection(row[image + " result"].split(", "))}
    reviewed = set()
    for row in read_rows("usage-review.tsv"):
        if not all(row.values()):
            raise ValueError(f"Incomplete usage review for {row['Command']}")
        reviewed.update((row["Command"], image) for image in row["Ubuntu 26.04 profiles"].split(", "))
    if guidance != reviewed:
        raise ValueError(f"Usage disposition differs from image results: {sorted(guidance ^ reviewed)}")

    def check_code(name, code, reference=resolute):
        if code in reference.get(name, set()):
            return
        if code.startswith("B") and name in BUILTINS and (code[1:] == "U" or code[1:].isdigit()):
            return
        if re.fullmatch(r"P\d+", code) and name in {"apt", "apt-get", "apt-cache", "apt-mark", "apt-config", "dpkg", "dpkg-deb", "dpkg-query"}:
            return
        if re.fullmatch(r"S\d+", code):
            profile = next((p for p in static_profiles if p["command"] == [name]), {})
            if sum(len(c["options"]) for c in profile.get("categories", [])) == int(code[1:]):
                return
        raise ValueError(f"{name} has no corresponding menu or guidance for {code}")
    static_profiles = [json.loads(p.read_text()) for p in (ROOT / "profiles").glob("*.json")]
    for row in shipped:
        for image in profiles:
            outcome = row[image + " result"]
            if (outcome == "—") != (not row[image]) or not row["Batch evidence"]:
                raise ValueError(f"{row['Command']} has an inconsistent result for {image}")
            if row[image]:
                for code in outcome.split(", "):
                    check_code(row["Command"], code)
    for row in kernel:
        check_code(Path(row["Canonical filesystem path"]).name, row["Batch root on listed profiles"])
    for row in optional:
        if row["Rank if selected"]:
            check_code(row["Command"], row["Batch root if installed"])
            if row["Noble root if installed"] == "unavailable" and row["Command"] in {"magick", "starship"}:
                continue
            check_code(row["Command"], row["Noble root if installed"], noble)
    print(f"{len(shipped)} shipped names, {len(kernel)} kernel paths, {len(optional)} optional rows, "
          f"{len(representatives)} ranks, {len(resolute)} Resolute and {len(noble)} Noble reference names")


if __name__ == "__main__":
    check()
