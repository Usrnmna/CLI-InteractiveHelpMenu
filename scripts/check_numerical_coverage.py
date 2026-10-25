"""Check maintained numerical coverage offline, without loading target code.

The inventory owns discovery/reconciliation; value_semantics owns numerical
validation and formatting. This adapter selects policy, checks propagation and
accounts for exact pre-existing migration debt. It never changes inspected data.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOL_ROOT / "scripts"))
sys.path.insert(0, str(TOOL_ROOT / "cli_help"))
import inventory_numerical_descriptions as inventory
from authoring import referenced_definitions
from core import HelpError
import presentation
from value_semantics import (
    ValueContext, ValueSemanticsError, format_value_semantics,
    validate_profile_semantics, validate_value_semantics,
)


ARTIFACT_KIND = "numerical_coverage"
BASELINE_CODES = {"sem_metadata_missing", "sem_review_required", "sem_unverified"}
CONTEXT_FIELDS = {"categories", "value_definitions", "positional_value_semantics"}
NUMERICAL_CLASSES = inventory.CLASSIFICATIONS - {"nonnumerical", "unresolved"}
HASH = re.compile(r"[0-9a-f]{64}\Z")
PLACEHOLDER = re.compile(r"\b(?:N|NUM|COUNT|BYTES|SECONDS|MILLISECONDS|SIZE|RATE|DURATION|PERCENT)\b", re.I)
NUMERICAL_PROSE = re.compile(r"\b(?:milliseconds?|seconds?|microseconds?|kibibytes?|mebibytes?|"
                             r"bytes?|bits?|percent(?:age)?|baud|hertz)\b", re.I)


def identity(kind, command, name=""):
    """Use inventory identities; aliases remain separate unless explicitly related."""
    return "|".join((kind, " ".join(command), name.rstrip("=") if kind in {"option", "keyword"} else name))


def profile_records(profile, source):
    """Enumerate authored records, retaining actual arity and complete source text.

    The source path disambiguates repeated observations of a logical identity.
    JSON offsets locate diagnostics but do not define identity or debt validity.
    """
    command = tuple(profile["command"])
    for ci, category in enumerate(profile["categories"]):
        for oi, option in enumerate(category["options"]):
            kind = "keyword" if option.get("kind") == "keyword" else "option"
            pointer = f"/categories/{ci}/options/{oi}/value_semantics"
            yield {"id": identity(kind, command, option["flag"]), "source": source,
                   "kind": kind, "profile": profile, "category": category, "option": option,
                   "metadata": option.get("value_semantics"), "context": ValueContext(
                       source=source, command=command, option=option["flag"], pointer=pointer,
                       argument_count=option.get("argument_count", 1) if option.get("argument") else 0,
                       value_optional=option.get("argument_optional", False))}
    if profile.get("positional_group"):
        group = profile["positional_group"]
        yield {"id": identity("positional_group", command), "source": source,
               "kind": "positional_group", "profile": profile, "category": {}, "option": group,
               "metadata": profile.get("positional_value_semantics"), "context": ValueContext(
                   source=source, command=command, option="<positional_group>", pointer="/positional_value_semantics",
                   argument_count=group["argument_count"], value_optional=False)}
    definitions = profile.get("value_definitions", {})
    for name, node in sorted(definitions.items()) if isinstance(definitions, dict) else ():
        pointer = "/value_definitions/" + name.replace("~", "~0").replace("/", "~1")
        yield {"id": identity("value_definition", command, name), "source": source,
               "kind": "value_definition", "profile": profile, "category": {}, "option": {},
               "metadata": {"schema_version": 1, "variants": [node]}, "context": ValueContext(
                   source=source, command=command, option="<definition:" + name + ">", pointer=pointer)}


def record_fingerprint(record):
    """Bind deferrals to authored meaning, grammar, context and reference closure.

    An unrelated sibling insertion/reordering leaves this hash unchanged. Changes
    to an owning profile's identity/context or a referenced definition do not.
    """
    profile = record["profile"]
    return inventory.digest({
        "id": record["id"], "source": record["source"], "option": record["option"],
        "metadata": record["metadata"], "category_description": record["category"].get("description", ""),
        "profile_context": {k: v for k, v in profile.items() if k not in CONTEXT_FIELDS},
        "definitions": referenced_definitions(record["metadata"], profile.get("value_definitions")),
    })


def review_fingerprint(group):
    """Pin substantive review decisions independently from refreshed source hashes."""
    return inventory.digest({key: group.get(key) for key in sorted(inventory.REVIEW_FIELDS)})


def needs_contract(record, classification):
    """Select values, numerical fixed flags, keywords, groups and definitions."""
    option = record["option"]
    return (record["kind"] in {"value_definition", "positional_group"} or bool(option.get("argument"))
            or numeric_spelling(record)
            or record["metadata"] is not None or "value_semantics" in option
            or classification in NUMERICAL_CLASSES or classification == "unresolved")


def numeric_spelling(record):
    """Recognize fixed numerical spellings, without treating protocol digits as values."""
    pattern = r"-?\d+(?:\.\d+)?" if record["kind"] == "keyword" else r"-\d+"
    return bool(re.fullmatch(pattern, record["option"].get("flag", "")))


def diagnostic(code, gate, message, record=None, *, severity="error", source="", pointer="", **extra):
    """Build portable structured policy diagnostics alongside shared diagnostics."""
    context = record["context"] if record else ValueContext(source=source, pointer=pointer)
    return {"code": code, "severity": severity, "gate": gate, "source": context.source,
            "pointer": context.pointer, "command": list(context.command), "option": context.option,
            "component": list(context.component), "identity": record["id"] if record else "",
            "message": message, **extra}


def shared_diagnostic(item, gate, record=None):
    result = item.to_dict()
    result.update(gate=gate, identity=record["id"] if record else "")
    if record and record["kind"] == "value_definition":
        start = record["context"].pointer
        result["pointer"] = result["pointer"].replace(start + "/variants/0", start, 1)
    return result


def semantic_nodes(metadata, definitions):
    """Visit explicit declarations, without interpreting prose or accepted values."""
    pending = [metadata, referenced_definitions(metadata, definitions)]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if "kind" in item:
                yield item
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def heuristic_signals(record, classification):
    """Surface disagreements; a signal never assigns units or changes classification.

    Names containing digits and words such as unit, PORT or volume alone are not
    evidence of a numerical quantity. Explicit review remains necessary even when
    these conservative heuristics find nothing.
    """
    if classification != "nonnumerical":
        return []
    option = record["option"]
    signals = []
    if PLACEHOLDER.search(option.get("argument", "")) or numeric_spelling(record):
        signals.append("numerical_placeholder")
    if NUMERICAL_PROSE.search(option.get("summary", "") + " " + option.get("detail", "")):
        signals.append("numerical_prose")
    nodes = list(semantic_nodes(record["metadata"], record["profile"].get("value_definitions")))
    if any(node.get("kind") not in {"nonnumerical", "unresolved", "delegated"} for node in nodes):
        signals.append("classification_disagreement")
    return [diagnostic("coverage_" + signal, "heuristic",
                       "Review the nonnumerical disposition against the source. Resolve the discrepancy or document why it is valid; no unit is inferred.",
                       record, severity="warning") for signal in signals]


def propagation_diagnostics(record):
    """Check actual shared details/search construction against formatter obligations.

    Independent semantic expectations and omission mutations in the tests also
    exercise the browser draw/search paths. This invariant alone does not prove
    factual correctness, native terminal behavior or arbitrary layout reachability.
    """
    if record["metadata"] is None or record["kind"] == "value_definition":
        return []
    profile, context = record["profile"], record["context"]
    try:
        expected = format_value_semantics(record["metadata"], context=context,
                                           definitions=profile.get("value_definitions"), presentation=True)
        if record["kind"] == "positional_group":
            # Command-wide positional text is displayed/searchable with each option.
            views = [presentation.option_text(profile, c, o) for c in profile["categories"] for o in c["options"]]
        else:
            views = [presentation.option_text(profile, record["category"], record["option"])]
    except (ValueSemanticsError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
        return [diagnostic("coverage_presentation_failure", "propagation",
                           "Restore safe presentation of supplied metadata; inspect the shared structural diagnostics.", record)]
    diagnostics = []
    if not views:
        diagnostics.append(diagnostic("coverage_details_missing", "propagation",
                                      "Provide an accessible existing details path for positional meaning.", record))
    for view in views:
        if any(line not in view.details for line in expected):
            diagnostics.append(diagnostic("coverage_details_missing", "propagation",
                                          "Restore the complete formatted meaning and qualifications in accessible details.", record))
        if any(line.casefold() not in view.searchable for line in expected):
            diagnostics.append(diagnostic("coverage_search_missing", "propagation",
                                          "Include displayed numerical meaning and qualifications in the shared search text.", record))
        placeholder = record["option"].get("argument", "")
        if placeholder and placeholder.casefold() not in view.searchable:
            diagnostics.append(diagnostic("coverage_placeholder_missing", "propagation",
                                          "Keep the argument placeholder searchable without changing insertion.", record))
    return diagnostics


def check_profile(profile, source, *, alias_groups=()):
    """Use the shared structural validator, including only explicitly supplied aliases."""
    return [shared_diagnostic(item, "structural") for item in
            validate_profile_semantics(profile, source=source, alias_groups=alias_groups)]


def deferrals(policy, records, failures, groups):
    """Validate exact baseline/exception records; never create or refresh them.

    Only maintained-completeness diagnostics can be deferred. Structural,
    classification, reconciliation and propagation failures remain hard errors.
    No wildcard, source-parent or inherited exception is supported.
    """
    diagnostics, accepted, seen = [], {}, set()
    source = inventory.REVIEW_PATH.as_posix()
    policy_pointer = "/coverage_policy"
    current_row = None

    def issue(code, message, record=None):
        item = diagnostic(code, "exceptions", message, record, source=source, pointer=policy_pointer,
                          policy_source=source, policy_pointer=policy_pointer)
        if record is None and isinstance(current_row, dict) and isinstance(current_row.get("id"), str):
            item["identity"] = current_row["id"]
            parts = item["identity"].split("|", 2)
            if len(parts) == 3:
                item["command"], item["option"] = parts[1].split(), parts[2]
        diagnostics.append(item)

    if not isinstance(policy, dict) or type(policy.get("format_version")) is not int or policy.get("format_version") != 1 or set(policy) - {
            "format_version", "legacy_baseline", "exceptions"}:
        issue("coverage_policy_invalid", "Supply coverage_policy version 1 with the documented baseline and exceptions lists.")
        return accepted, diagnostics
    baseline = policy.get("legacy_baseline", {})
    text_fields = {"reason", "scope", "invalidation"}
    if (not isinstance(baseline, dict) or set(baseline) != text_fields | {"origin_revision", "entries"}
            or any(not isinstance(baseline.get(k), str) or not baseline[k].strip() for k in text_fields)
            or not isinstance(baseline.get("origin_revision"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", baseline["origin_revision"])):
        issue("coverage_baseline_invalid", "Record the exact legacy-baseline origin, bounded scope, reason and invalidation condition.")
        baseline = {"entries": []}
    for kind, rows in (("baseline", baseline.get("entries")), ("exception", policy.get("exceptions"))):
        list_pointer = "/coverage_policy/legacy_baseline/entries" if kind == "baseline" else "/coverage_policy/exceptions"
        policy_pointer = list_pointer
        if not isinstance(rows, list):
            issue("coverage_exception_invalid", "Baseline entries and exceptions must be explicit lists.")
            continue
        required = {"id", "source", "fingerprint", "review_fingerprint", "codes"}
        if kind == "exception":
            required |= {"reason", "evidence", "applicability", "investigation", "review_condition"}
        for index, row in enumerate(rows):
            policy_pointer, current_row = list_pointer + "/" + str(index), row
            if (not isinstance(row, dict) or set(row) != required
                    or any(not isinstance(row.get(k), str) or not row[k].strip() for k in required - {"codes"})
                    or not isinstance(row.get("codes"), list) or not row["codes"]
                    or any(not isinstance(code, str) for code in row["codes"])):
                issue("coverage_exception_invalid", "Supply the exact documented fields, identity, source and deferred diagnostic codes.")
                continue
            key = (row["source"], row["id"])
            record = records.get(key)
            if any(character in row["id"] + row["source"] for character in "*?[]"):
                issue("coverage_exception_broad", "Replace wildcard/parent exemptions with exact existing record identities.", record)
                continue
            if key in seen:
                issue("coverage_exception_duplicate", "Remove duplicate or conflicting deferrals for this source and identity.", record)
                continue
            seen.add(key)
            if record is None:
                issue("coverage_exception_orphan", "Remove or reassess the exception; this maintained record no longer exists.")
                continue
            group = groups.get(record.get("review_group"), {})
            if (not HASH.fullmatch(row["fingerprint"]) or not HASH.fullmatch(row["review_fingerprint"])
                    or row["fingerprint"] != record_fingerprint(record)
                    or row["review_fingerprint"] != review_fingerprint(group)):
                issue("coverage_exception_stale", "Inspect the changed facts/review. Complete the contract or explicitly reassess this exact deferral; refreshing census hashes does not renew it.", record)
                continue
            codes = set(row["codes"])
            actual = {item["code"] for item in failures.get(key, [])}
            if (len(codes) != len(row["codes"]) or codes != actual or not codes
                    or kind == "baseline" and not codes <= BASELINE_CODES):
                issue("coverage_exception_requirements", "Defer only the exact current completeness failures; remove resolved, unsupported or expanded requirements.", record)
                continue
            if kind == "exception" and (row["evidence"] not in {"source_derived", "suspected", "unresolved"}
                    or any(len(row[k].strip()) < 16 for k in ("reason", "applicability", "investigation", "review_condition"))):
                issue("coverage_exception_reason", "Provide substantive technical scope, investigation and review condition; unresolved content cannot be excepted as verified.", record)
                continue
            accepted[key] = kind
    return accepted, diagnostics


def check_coverage(root, reviews, *, mode="prospective"):
    """Return a deterministic report; inspect sources without writing or probing.

    prospective permits only unchanged, explicitly recorded migration debt.
    strict reports every maintained completeness failure even when deferred.
    Neither mode changes ordinary runtime loading or external browsing policy.
    """
    if mode not in {"prospective", "strict"}:
        raise ValueError("Coverage mode must be prospective or strict")
    report = inventory.build_inventory(root, reviews)
    entries = {entry["id"]: entry for entry in report["entries"]}
    groups = {group["id"]: group for group in report["review_groups"]}
    diagnostics, records, failures = [], {}, {}
    for item in report["diagnostics"]:
        entry = entries.get(item["location"])
        observation = entry["observations"][0] if entry else {}
        source = observation.get("source", {})
        diagnostics.append(diagnostic(item["code"], "reconciliation", item["message"],
                                      source=source.get("path", inventory.REVIEW_PATH.as_posix()),
                                      pointer=source.get("pointer", ""), location=item["location"],
                                      identity=entry["id"] if entry else "",
                                      command=entry["command"] if entry else [], option=entry["name"] if entry else "<value>"))
    reader = inventory.Inventory(root)
    profiles = [(item["path"], reader.json(Path(item["path"]), "bundled_profile")) for item in report["sources"]
                if "bundled_profile" in item["roles"]]
    counts = Counter(profiles=len(profiles))
    for source, profile in profiles:
        diagnostics.extend(check_profile(profile, source))
        for record in profile_records(profile, source):
            key = (record["source"], record["id"])
            if key in records:
                diagnostics.append(diagnostic("coverage_record_duplicate", "classification",
                                              "Disambiguate duplicate maintained records; no exception may select multiple owners.", record))
            records[key] = record
            entry = entries.get(record["id"], {})
            record["review_group"] = entry.get("review_group")
            classification = groups.get(record["review_group"], {}).get("classification")
            counts[record["kind"] + "_records"] += 1
            if classification not in inventory.CLASSIFICATIONS:
                diagnostics.append(diagnostic("coverage_classification_missing", "classification",
                                              "Provide an explicit reviewed planning classification; metadata is not automatically promoted into a review decision.", record))
            diagnostics.extend(heuristic_signals(record, classification))
            if not needs_contract(record, classification):
                continue
            counts["contract_required_records"] += 1
            items = validate_value_semantics(record["metadata"], mode="maintained", context=record["context"],
                                             definitions=profile.get("value_definitions"))
            failures[key] = [shared_diagnostic(item, "maintained", record) for item in items]
            if not items:
                counts["complete_records"] += 1
            for node in semantic_nodes(record["metadata"], profile.get("value_definitions")):
                review = node.get("review")
                if isinstance(review, dict) and review.get("status") == "synthetic":
                    diagnostics.append(diagnostic("coverage_synthetic_production", "classification",
                                                  "Keep synthetic evidence in fixtures; production declarations need applicable substantive evidence.", record))
            # Structural failures already have actionable diagnostics; the UI's
            # nonfatal fallback is tested separately and is not verified guidance.
            if not validate_value_semantics(record["metadata"], context=record["context"],
                                             definitions=profile.get("value_definitions")):
                diagnostics.extend(propagation_diagnostics(record))
    accepted, policy_diagnostics = deferrals(reviews.get("coverage_policy"), records, failures, groups)
    diagnostics.extend(policy_diagnostics)
    debt = []
    for key, items in sorted(failures.items()):
        if not items:
            continue
        record = records[key]
        debt.append({"id": record["id"], "source": record["source"], "kind": record["kind"],
                     "codes": sorted({item["code"] for item in items}), "deferred_by": accepted.get(key)})
        for item in items:
            if key in accepted:
                item = {**item, "severity": "debt" if mode == "prospective" else "error", "deferred_by": accepted[key]}
            diagnostics.append(item)
    # Raw observations remain census/review obligations, not verified contracts.
    external = [entry for entry in report["entries"] if entry["kind"] in {"option", "keyword"}
                and not any(o["role"] == "bundled_option" for o in entry["observations"])
                and any(o["role"] in {"fixture_help", "captured_help"} for o in entry["observations"])]
    external_groups = Counter(entry.get("review_group") or "<unreviewed>" for entry in external)
    for name, count in sorted(external_groups.items()):
        group = groups.get(name, {})
        if group.get("evidence") != "verified":
            diagnostics.append(diagnostic("coverage_external_uncertainty", "external",
                f"{count} external-only logical entries in review group {name} retain {group.get('evidence', 'unreviewed')} evidence; inspect the inventory's exact observations and investigations.",
                severity="info", source=inventory.REVIEW_PATH.as_posix(), pointer="/groups/" + name))
    diagnostics = sorted({inventory.encoded(item): item for item in diagnostics}.values(), key=inventory.encoded)
    errors = sum(item["severity"] == "error" for item in diagnostics)
    return {"artifact_kind": ARTIFACT_KIND, "format_version": 1, "mode": mode,
            "passed": not errors, "full_maintained_ready": not debt and not errors,
            "active_gates": ["inventory_review", "supplied_structure", "maintained_" + mode,
                             "display_search_propagation", "exact_deferrals"],
            "counts": dict(sorted(counts.items())), "inventory_counts": report["counts"],
            "diagnostic_counts": dict(sorted(Counter(item["severity"] for item in diagnostics).items())),
            "debt_counts": dict(sorted(Counter(item["kind"] for item in debt).items())),
            "external_only_logical_entries": len(external), "remaining_debt": debt, "diagnostics": diagnostics,
            "limits": "Structure, consistency and tested propagation are enforced. Upstream factual truth, all possible numerical prose, installed versions and native terminals are not established. External observations are not complete option grammars."}


def write_report(root, destination, report):
    """Write only explicitly selected ignored report locations, never input files."""
    destination = Path(destination)
    if any(path.is_symlink() or getattr(path, "is_junction", lambda: False)() for path in (destination, *destination.parents)):
        raise ValueError("Report destination must not traverse links")
    allowed = (Path(root) / "tests/reports").resolve()
    target = destination.resolve()
    if allowed not in target.parents:
        raise ValueError("Select an explicit destination under this snapshot's tests/reports")
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=inventory.unique_object)
        if not isinstance(previous, dict) or previous.get("artifact_kind") != ARTIFACT_KIND:
            raise ValueError("Existing destination is not a numerical coverage report")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(inventory.encoded(report, pretty=True), encoding="utf-8", newline="\n")


def main(argv=None):
    """Run the offline gate; default to stdout and propagate all hard failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=TOOL_ROOT, help="Repository snapshot; inspected code is never imported")
    parser.add_argument("--reviews", type=Path, help="Curated inventory review and exact coverage policy")
    parser.add_argument("--mode", choices=("prospective", "strict"), default="prospective")
    parser.add_argument("--output", type=Path, help="Explicit ignored tests/reports JSON destination")
    parser.add_argument("--summary", action="store_true", help="Print aggregate results; --output still retains full diagnostics")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        review_file = args.reviews or root / inventory.REVIEW_PATH
        reviews = json.loads(review_file.read_text(encoding="utf-8"), object_pairs_hook=inventory.unique_object)
        report = check_coverage(root, reviews, mode=args.mode)
        if args.output:
            write_report(root, args.output, report)
        output = {k: v for k, v in report.items() if k not in {"diagnostics", "remaining_debt"}} if args.summary else report
        print(inventory.encoded(output, pretty=True), end="")
        return 0 if report["passed"] else 1
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, HelpError) as error:
        print(f"Numerical coverage input/output error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
