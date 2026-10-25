"""Read-only option text shared by the browser's list, details and search.

Numerical meaning is supplied exclusively by the shared formatter. These helpers
do not select installed-version variants, format inactive declarations, mutate
profiles, perform I/O or inspect a pending command.
"""

from dataclasses import dataclass

from value_semantics import ValueContext, ValueSemanticsError, format_value_semantics


@dataclass(frozen=True)
class ValueText:
    """A compact lead and the complete, unwrapped explanation it comes from."""

    compact: str = ""
    lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class OptionText:
    """Derived display text; searchable content is a subset of accessible details."""

    compact: str
    details: tuple[str, ...]
    searchable: str


def option_label(option):
    """Show the existing literal declaration without changing insertion fields."""
    separator = ("" if option.get("argument_style") == "attached_only" or option["flag"].endswith("=")
                 else "=" if option.get("argument_style") == "equals" else " ")
    label = option["flag"] + (separator + option["argument"] if option.get("argument") else "")
    return label + (" [keyword]" if option.get("kind") == "keyword" else "")


def value_text(profile, entry, *, positional=False):
    """Format optional active metadata safely, retaining all applicability variants.

    A missing optional field preserves legacy presentation. An invalid supplied
    field produces nonfatal guidance without exposing schema diagnostics as value
    instructions. Shared definitions and existing arity are passed unchanged.
    """
    field = "positional_value_semantics" if positional else "value_semantics"
    if field not in entry:
        return ValueText()
    group = profile.get("positional_group", {}) if positional else entry
    context = ValueContext(
        command=tuple(profile["command"]), option="<positional_group>" if positional else entry["flag"],
        pointer="/" + field,
        argument_count=group.get("argument_count", 1) if group.get("argument") else 0,
        value_optional=group.get("argument_optional", False),
    )
    try:
        lines = format_value_semantics(entry[field], context=context,
                                       definitions=profile.get("value_definitions"), presentation=True)
    except (ValueSemanticsError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
        return ValueText("Value guidance unavailable; review needed.", (
            "Value guidance unavailable: numerical documentation could not be interpreted safely.",
            "Consult the original description and source documentation; units have not been inferred.",
        ))
    # Multiple scopes stay explicit even when the first explanation is clipped.
    compact = lines[0]
    if compact.startswith(("Value:", "Value (")):
        heading, _, body = compact.partition(": ")
        qualifier = heading.removeprefix("Value").strip()
        # Remove only predictable presentation labels, retaining the bare-number
        # rule, every qualification and the complete unshortened meaning.
        body = "bare: " + body[len("bare numbers: "):] if body.startswith("bare numbers: ") else body
        compact = (qualifier + " " if qualifier else "") + body
    if any(line.startswith("Value variant 2") for line in lines):
        compact = "Value varies by applicability; see details."
        lines = ("Value varies by applicability; all documented alternatives follow. No target match is assumed.",) + lines
    return ValueText(compact, tuple(lines))


def _source_notes(profile, option):
    """Expose relevant preserved review evidence without activating alternatives.

    Unassigned shared documentation is explicitly command context and is not an
    option search term. Inactive structured declarations remain inactive; their
    source ownership is visible, while raw metadata is never presented as advice.
    """
    document = profile.get("documentation")
    if not isinstance(document, dict):
        return (), (), False
    selected, contextual = [], []
    needs_review = False
    identity = option["flag"].rstrip("=")
    owners = document.get("semantic_sources", {})
    if isinstance(owners, dict):
        for key, label in ((identity, "Numerical source"), ("<positional_group>", "Repeated-value source")):
            if isinstance(owners.get(key), str):
                selected.append(label + ": " + owners[key])
    diagnostics = document.get("diagnostics")
    for note in diagnostics if isinstance(diagnostics, list) else ():
        if not isinstance(note, dict) or not isinstance(note.get("message"), str):
            continue
        at = str(note.get("option", "")).rstrip("=")
        if at in {identity, "<positional_group>"}:
            needs_review = True
            source = note.get("source") if isinstance(note.get("source"), str) else "unspecified source"
            selected.append(f"Source review ({source}): " + note["message"])
    alternatives = document.get("alternatives")
    for item in alternatives if isinstance(alternatives, list) else ():
        if not isinstance(item, dict):
            continue
        if str(item.get("option", "")).rstrip("=") in {identity, "<positional_group>"}:
            needs_review = True
            source = item.get("source") if isinstance(item.get("source"), str) else "an unspecified source"
            selected.append("Unselected numerical declaration from " + source
                            + "; retained for review, not applied as value guidance.")
    shared = document.get("shared")
    for item in shared if isinstance(shared, list) else ():
        if isinstance(item, dict) and not item.get("options") and isinstance(item.get("text"), str):
            source = item.get("source") if isinstance(item.get("source"), str) else "unspecified source"
            contextual.extend(("Unassigned source documentation (relationship to this option is unverified):",
                               source + ": " + item["text"]))
    return tuple(selected), tuple(contextual), needs_review


def option_text(profile, category, option, *, positional=None):
    """Build accessible details and substring search text from one explanation.

    Profile-wide repeated-argument guidance is labeled and searchable wherever it
    is accessible. Unassigned source prose remains accessible context without
    making every option match claims that have no established association.
    """
    numerical = value_text(profile, option)
    positional = value_text(profile, profile, positional=True) if positional is None else positional
    notes, contextual, needs_review = _source_notes(profile, option)
    lines = list(numerical.lines)
    if needs_review:
        lines.insert(0, "Source review needed; competing or incomplete claims remain unselected. Consult the source notes below.")
    # Review warnings precede ordinary prose even if active metadata is absent.
    lines.extend(notes)
    lines.append("Option: " + option_label(option))
    lines.append(option["summary"])
    if option.get("detail"):
        lines.append(option["detail"])
    if option.get("argument"):
        label = "Optional argument: " if option.get("argument_optional") else "Argument required: "
        if option.get("argument_style") == "attached_only":
            label = "Optional attached argument: " if option.get("argument_optional") else "Attached argument required: "
        lines.append(label + option["argument"] + ". Enter its value after insertion.")
    # Only explicitly displayed option/argument/value text enters search.
    legacy = option["flag"] + " " + option["summary"] + " " + option.get("detail", "")
    searchable = [legacy, *lines]
    if profile.get("positional_group"):
        group = profile["positional_group"]
        repeated = ("Repeated value group (command-wide): " + group["argument"]
                    + ". Enter each complete group manually; placeholders are never inserted.")
        group_lines = (repeated, *positional.lines)
        lines.extend(group_lines)
        searchable.extend(group_lines)
    if category.get("description"):
        lines.append(category["description"])
    lines.extend(contextual)
    compact = numerical.compact
    if needs_review:
        compact = "Source review needed; " + (compact or "see details.")
    return OptionText(compact, tuple(lines), " ".join(searchable).casefold())
