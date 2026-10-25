"""Numerical preservation and change review at existing authoring boundaries.

The helpers operate on supplied documents only. They use the shared structural
validator, preserve inactive evidence in existing documentation records, and do
not classify prose, execute targets or certify upstream facts.
"""

from copy import deepcopy
import hashlib
import json

from errors import HelpError
from value_semantics import Diagnostic, ValueContext, format_value_semantics, validate_profile_semantics, validate_value_semantics


OPTION_FIELDS = ("kind", "argument", "argument_count", "argument_optional", "optional_value_kind",
                 "argument_style", "attached", "bundle", "summary", "detail")
PROFILE_FIELDS = ("command", "description", "identity", "stop_at_positional", "stop_at_options", "imported_from")


class NumericalAuthoringError(HelpError):
    """Expose the shared validator's structured errors without replacing its API."""

    def __init__(self, diagnostics):
        self.diagnostics = tuple(diagnostics)
        super().__init__("\n".join(
            f"{d.source}{d.pointer} [{' '.join(d.command)} {d.option}]: {d.code}: {d.message}"
            for d in diagnostics), "numerical_metadata_invalid")


def validate_authored_profile(profile, source="<authored profile>", *, alias_groups=()):
    """Check supplied optional metadata structurally; absence never requires migration."""
    diagnostics = validate_profile_semantics(profile, source=source, mode="structural", alias_groups=alias_groups)
    errors = [diagnostic for diagnostic in diagnostics if diagnostic.severity == "error"]
    if errors:
        raise NumericalAuthoringError(errors)
    return diagnostics


def _options(profile):
    return {option["flag"]: (option, category) for category in profile.get("categories", [])
            for option in category["options"]}


def _owner(profile, flag):
    """Read only an explicitly recorded semantic owner for the selected entry."""
    document = profile.get("documentation")
    owners = document.get("semantic_sources") if isinstance(document, dict) else None
    return owners.get(flag.rstrip("=")) if isinstance(owners, dict) else None


def _facts(option):
    """Normalize harmless absent/default spellings, without interpreting operands."""
    defaults = {"kind": "flag", "argument": "", "argument_count": 1, "argument_optional": False,
                "optional_value_kind": None, "argument_style": None, "attached": False,
                "bundle": False, "summary": "", "detail": ""}
    return {field: option.get(field, defaults[field]) for field in OPTION_FIELDS}


def referenced_definitions(metadata, definitions):
    """Find the explicit transitive reference closure; cycles never cause recursion."""
    result, pending = {}, [metadata]
    definitions = definitions if isinstance(definitions, dict) else {}
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if set(item) == {"ref"} and isinstance(item["ref"], str):
                name = item["ref"]
                if name not in result:
                    result[name] = definitions.get(name)
                    pending.append(result[name])
            else:
                pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return {name: deepcopy(result[name]) for name in sorted(result)}


def _verified(metadata, definitions):
    """Inspect declared review status, including explicitly referenced components."""
    pending = [metadata, referenced_definitions(metadata, definitions)]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if isinstance(item.get("review"), dict) and item["review"].get("status") == "verified":
                return True
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return False


def driver_context(profile, driver):
    """Identify the selected route's operand boundaries, excluding unrelated routes."""
    driver = driver or {}
    route = next((route for route in driver.get("paths", []) if route["command"] == profile["command"][1:]), {})
    return {"global_values": sorted(driver.get("global_values", [])),
            "global_flags": sorted(driver.get("global_flags", [])),
            "route": {key: route.get(key) for key in ("command", "option_values", "option_flags", "stop_at_options", "stop_at_positional")}}


def review_signature(profile, driver=None):
    """Bind transient review to numerical content and context, independent of ordering."""
    content = {"profile": {key: profile.get(key) for key in PROFILE_FIELDS},
               "options": {flag: {**_facts(option), "value_semantics": option.get("value_semantics")}
                           for flag, (option, _) in sorted(_options(profile).items()) if "value_semantics" in option},
               "definitions": profile.get("value_definitions"),
               "positional_group": profile.get("positional_group"),
               "positional_value_semantics": profile.get("positional_value_semantics"),
               "driver": driver_context(profile, driver) if driver else None,
               "owners": (profile.get("documentation") or {}).get("semantic_sources")
                   if isinstance(profile.get("documentation"), dict) else None}
    return hashlib.sha256(json.dumps(content, ensure_ascii=True, sort_keys=True).encode()).hexdigest()


def prepare_profile(previous, candidate, *, reviewed=False, replacement=False, context_changed=False, defer_definition_review=False):
    """Preserve old claims and deactivate stale or inherited verified declarations.

    reviewed is an explicit caller-selected author review, never validator success.
    New complete profiles are accepted as supplied. Changes to existing verified
    claims require a fresh review; ordinary lossless moves require none. Malformed
    edited metadata is left available for correction and rejected by save checks.
    Source replacement retains the complete previous profile as inactive evidence.
    A read-only preview can defer a changed-library review error while its affected
    consumers are deactivated; save callers retain the default blocking behavior.
    """
    result = deepcopy(candidate)
    if previous is None or previous == candidate and not context_changed:
        return result
    old_entries, new_entries = _options(previous), _options(result)
    old_definitions, new_definitions = previous.get("value_definitions", {}), result.get("value_definitions", {})
    broad_change = context_changed or any(previous.get(key) != candidate.get(key) for key in PROFILE_FIELDS)
    document = None

    def records():
        """Access evidence containers only in the detached candidate document."""
        nonlocal document
        if document is None:
            document = result.setdefault("documentation", {})
            if not isinstance(document, dict):
                raise HelpError("Numerical preservation requires a documentation object; correct it in the JSON draft.")
            for field in ("alternatives", "diagnostics", "sources"):
                if not isinstance(document.setdefault(field, []), list):
                    raise HelpError("Numerical preservation requires documentation lists; correct the JSON draft.")
        return document

    def archive(owner, flag, metadata, field, declaration, source):
        """Retain a declaration with its own reference closure and source identity."""
        if metadata is None:
            return
        item = {"source": source, "option": flag, "field": field, "metadata": deepcopy(metadata),
                "definitions": referenced_definitions(metadata, owner.get("value_definitions", {})),
                "definition_scope": "source", "declaration": deepcopy(declaration),
                "command": deepcopy(owner["command"]), "semantic_source": deepcopy(_owner(owner, flag)),
                "imported_from": deepcopy(owner.get("imported_from"))}
        target = records()["sources" if reviewed else "alternatives"]
        if item not in target:
            target.append(item)

    def review_note(flag, message):
        """Deduplicate actionable authoring uncertainty without asserting unit facts."""
        note = {"code": "authoring_semantics_review", "source": "authoring", "command": result["command"],
                "option": flag, "message": message}
        if note not in records()["diagnostics"]:
            records()["diagnostics"].append(note)

    if replacement and previous.get("categories"):
        snapshot = {"source": "prior authored profile (inactive replacement evidence)", "profile": deepcopy(previous)}
        if snapshot not in records()["sources"]:
            records()["sources"].append(snapshot)
        note = {"code": "authoring_source_replaced", "source": "authoring", "command": result["command"],
                "option": "<shared>", "message": "The prior authored profile is retained as inactive source evidence; numerical claims are not reassigned by matching flag names."}
        if note not in records()["diagnostics"]:
            records()["diagnostics"].append(note)

    if isinstance(old_definitions, dict):
        for name, node in old_definitions.items():
            if not isinstance(new_definitions, dict) or name not in new_definitions or node != new_definitions[name]:
                archive(previous, "<definition " + name + ">", {"schema_version": 1, "variants": [{"ref": name}]},
                        "value_definitions", {"name": name}, "prior shared definition")

    # A changed verified library declaration must not retain inherited approval,
    # even when it currently has no consumers. No unit/schema rules are duplicated.
    if not reviewed and isinstance(new_definitions, dict):
        for name, node in new_definitions.items():
            old_node = old_definitions.get(name) if isinstance(old_definitions, dict) else None
            if node != old_node and _verified(node, new_definitions):
                malformed = any(d.severity == "error" for d in validate_value_semantics(
                    {"schema_version": 1, "variants": [node]}, definitions=new_definitions))
                if not malformed:
                    if defer_definition_review:
                        review_note("<definition " + name + ">", "A changed verified definition awaits numerical review. Affected consumers remain inactive in this preview; saving requires review or honestly unverified metadata.")
                        continue
                    raise NumericalAuthoringError([Diagnostic(
                        "authoring_definition_review", "error", "<authored profile>",
                        "/value_definitions/" + name.replace("~", "~0").replace("/", "~1"),
                        tuple(result["command"]), "<definition " + name + ">", (),
                        "Review the changed verified definition and every explicit consumer through Numerical review, or record honest source-derived/unresolved evidence before saving.")])

    for flag, (old, category) in old_entries.items():
        if "value_semantics" in old and (flag not in new_entries or "value_semantics" not in new_entries[flag][0]):
            archive(previous, flag, old["value_semantics"], "value_semantics",
                    {**old, "category_description": category.get("description", "")}, "prior authored declaration")
            owners = records().get("semantic_sources")
            if isinstance(owners, dict):
                owners.pop(flag.rstrip("="), None)

    for flag, (option, category) in new_entries.items():
        if "value_semantics" not in option:
            continue
        old, old_category = old_entries.get(flag, ({}, {}))
        metadata = option["value_semantics"]
        old_metadata = old.get("value_semantics")
        category_change = (category.get("name") == old_category.get("name")
                           and category.get("description", "") != old_category.get("description", ""))
        declaration_change = bool(old) and (_facts(old) != _facts(option) or category_change)
        definitions_change = referenced_definitions(old_metadata, old_definitions) != referenced_definitions(metadata, new_definitions)
        metadata_change = metadata != old_metadata or definitions_change
        impact = broad_change or declaration_change or metadata_change or _owner(previous, flag) != _owner(candidate, flag)
        if not impact:
            continue
        archive(previous, flag, old_metadata, "value_semantics",
                {**old, "category_description": old_category.get("description", "")}, "prior authored declaration")
        # Structural mistakes in an edited declaration must not disappear merely
        # because its previous meaning also needs review. Save reports them.
        malformed = any(d.severity == "error" for d in validate_value_semantics(
            metadata, definitions=new_definitions, context=ValueContext(command=tuple(result["command"]), option=flag,
                argument_count=(option.get("argument_count", 1) if option.get("argument") else 0)
                    if metadata_change else None,
                value_optional=option.get("argument_optional", False) if metadata_change else None)))
        inherited = metadata == old_metadata
        if not reviewed and not malformed and (inherited or _verified(metadata, new_definitions)):
            archive(result, flag, metadata, "value_semantics", option, "edited declaration awaiting numerical review")
            option.pop("value_semantics")
            owners = records().get("semantic_sources")
            if isinstance(owners, dict):
                owners.pop(flag.rstrip("="), None)
            review_note(flag, "Numerical meaning requires review after an identity, argument, prose, shared-definition or source-context edit. Prior declarations remain inactive; correct the JSON metadata and use Numerical review before saving verified changes.")
        elif reviewed and not malformed:
            owners = records().setdefault("semantic_sources", {})
            if not isinstance(owners, dict):
                raise HelpError("Correct semantic source ownership in the JSON draft before acknowledging numerical edits.")
            owners[flag.rstrip("=")] = "authored numerical review"
        elif metadata_change and not malformed:
            # Explicitly revised unverified content may remain active, but it
            # must not inherit the previous declaration's semantic ownership.
            owners = records().get("semantic_sources")
            if isinstance(owners, dict):
                owners.pop(flag.rstrip("="), None)

    field = "positional_value_semantics"
    old_metadata, metadata = previous.get(field), result.get(field)
    positional_change = (broad_change or previous.get("positional_group") != result.get("positional_group")
                         or old_metadata != metadata or _owner(previous, "<positional_group>") != _owner(candidate, "<positional_group>")
                         or referenced_definitions(old_metadata, old_definitions) != referenced_definitions(metadata, new_definitions))
    if old_metadata is not None and positional_change:
        archive(previous, "<positional_group>", old_metadata, field, previous.get("positional_group"), "prior positional declaration")
        if metadata is None:
            owners = records().get("semantic_sources")
            if isinstance(owners, dict):
                owners.pop("<positional_group>", None)
    if metadata is not None and positional_change and not reviewed:
        group = result.get("positional_group") or {}
        edited_metadata = metadata != old_metadata or referenced_definitions(old_metadata, old_definitions) != referenced_definitions(metadata, new_definitions)
        malformed = any(d.severity == "error" for d in validate_value_semantics(metadata, definitions=new_definitions,
            context=ValueContext(command=tuple(result["command"]), option="<positional_group>",
                argument_count=group.get("argument_count", 0) if edited_metadata else None,
                value_optional=False if edited_metadata else None)))
        if not malformed and (metadata == old_metadata or _verified(metadata, new_definitions)):
            archive(result, "<positional_group>", metadata, field, result.get("positional_group"), "edited positional declaration awaiting numerical review")
            result.pop(field)
            owners = records().get("semantic_sources")
            if isinstance(owners, dict):
                owners.pop("<positional_group>", None)
            review_note("<positional_group>", "Repeated-argument numerical meaning requires review; prior components and references remain inactive.")
    elif metadata is not None and positional_change and reviewed:
        owners = records().setdefault("semantic_sources", {})
        if not isinstance(owners, dict):
            raise HelpError("Correct semantic source ownership in the JSON draft before acknowledging numerical edits.")
        owners["<positional_group>"] = "authored numerical review"

    if reviewed and isinstance(result.get("documentation"), dict):
        # Only authoring review notes for explicitly active corrected entries are
        # retired. Source conflicts and inactive declarations remain evidence.
        active = {flag for flag, (option, _) in _options(result).items() if "value_semantics" in option}
        if isinstance(new_definitions, dict):
            active.update("<definition " + name + ">" for name in new_definitions)
        if field in result:
            active.add("<positional_group>")
        notes = result["documentation"].get("diagnostics")
        if isinstance(notes, list):
            notes[:] = [note for note in notes if not (isinstance(note, dict)
                        and note.get("code") == "authoring_semantics_review" and note.get("option") in active)]
        alternatives = result["documentation"].get("alternatives")
        if isinstance(alternatives, list):
            history = records()["sources"]
            for item in list(alternatives):
                if (isinstance(item, dict) and item.get("option") in active
                        and item.get("source") in {"prior authored declaration", "prior positional declaration",
                            "prior shared definition", "edited declaration awaiting numerical review",
                            "edited positional declaration awaiting numerical review"}):
                    if item not in history:
                        history.append(item)
                    alternatives.remove(item)
    return result


def numerical_review(profile):
    """Return inspectable numerical text, explicit consumers and structured checks."""
    entries = []

    def entry(flag, metadata, arity, optional):
        context = ValueContext(command=tuple(profile["command"]), option=flag, argument_count=arity, value_optional=optional)
        try:
            lines = format_value_semantics(metadata, context=context, definitions=profile.get("value_definitions"), presentation=True)
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
            lines = ("Numerical metadata needs correction; see structured diagnostics.",)
        return {"option": flag, "definitions": list(referenced_definitions(metadata, profile.get("value_definitions"))), "explanation": lines}

    for flag, (option, _) in _options(profile).items():
        if "value_semantics" not in option:
            continue
        entries.append(entry(flag, option["value_semantics"], option.get("argument_count", 1) if option.get("argument") else 0,
                             option.get("argument_optional", False)))
    if "positional_value_semantics" in profile:
        entries.append(entry("<positional_group>", profile["positional_value_semantics"], (profile.get("positional_group") or {}).get("argument_count", 0), False))
    definitions = profile.get("value_definitions")
    consumers = ({name: [entry["option"] for entry in entries if name in entry["definitions"]]
                  for name in definitions} if isinstance(definitions, dict) else {})
    document = profile.get("documentation")
    sources = {}
    if isinstance(document, dict):
        sources["diagnostics"] = deepcopy(document.get("diagnostics", []))
        for field in ("sources", "alternatives", "shared"):
            records = document.get(field)
            sources[field] = [{key: deepcopy(record[key]) for key in ("source", "option", "field", "command") if key in record}
                              for record in records if isinstance(record, dict)] if isinstance(records, list) else []
    return {"command": profile["command"], "entries": entries, "definition_consumers": consumers,
            "unannotated_values": [{"option": flag, "argument": option["argument"]}
                                   for flag, (option, _) in _options(profile).items() if option.get("argument") and "value_semantics" not in option],
            "diagnostics": [d.to_dict() for d in validate_profile_semantics(profile, mode="structural")],
            "source_notes": sources,
            "evidence_limit": "Structural consistency and successful preview do not verify upstream numerical claims."}
