"""Read-only option text shared by the browser's list, details and search.

Numerical meaning is supplied exclusively by the shared formatter. These helpers
do not select installed-version variants, format inactive declarations, mutate
profiles, perform I/O or inspect a pending command.
"""

from dataclasses import dataclass
import re

from value_semantics import ValueContext, ValueSemanticsError, format_value_semantics


@dataclass(frozen=True)
class ValueText:
    """A compact lead, concise rules and original formatter text for search."""

    compact: str = ""
    lines: tuple[str, ...] = ()
    list_hint: str = ""
    notice: str = ""
    searchable_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class OptionText:
    """Concise display text with original documentation retained for search."""

    compact: str
    details: tuple[str, ...]
    searchable: str
    list_hint: str = ""
    notice: str = ""
    summary: str = ""


# These patterns remove documentation scaffolding, not arbitrary sentences or
# text after a fixed length. Unrecognized prose stays intact so constraints are
# not silently lost when imported help uses an unfamiliar wording.
_METADATA_LINE = re.compile(
    r"^(?:Source|Reference|Evidence|Investigation|Source qualification|"
    r"Reference scope|Numerical source|Shared documentation|Updated|Last updated|Release date|"
    r"Version|Copyright)\s*[:(]", re.I)
_BACKGROUND = re.compile(
    r"^(?:See\b|Refer to\b|For (?:more|further)\b|For example\b|Examples?\s*:|"
    r"Added in\b|Introduced in\b|Since version\b|New in\b|"
    r"Internally\b|Implemented (?:using|with)\b|Implementation (?:details?|notes?)\b|"
    r"(?:Last )?[Uu]pdated (?:on|in)\b|Released on\b|"
    r"Selecting this option\b|The cursor remains\b|Enter and quote\b|Combine with\b|"
    r"Other releases require verification\b)", re.I)
_RELEASE_HEADING = re.compile(
    r"(?:^|(?<=; )|(?<=\. ))(?:[\w./-]+\s+){1,3}v?\d+(?:\.\d+){1,3}(?:[a-z]\d*)?"
    r"(?:\s+\([^)]*\))?(?: reference)?:\s*")


def concise_description(text):
    """Remove recognizable provenance and examples; preserve operational prose.

    Wrapped help paragraphs are joined before sentence deduplication. Decimal
    values, paths, protocol versions and date *formats* are not date metadata.
    Nothing is evaluated, and the supplied source string is never modified.
    """
    paragraphs, current = [], []
    in_code = False
    in_examples = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^(?:Examples?|Usage|Output)\s*:", line, re.I):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            in_examples = True
            continue
        if not line or _METADATA_LINE.match(line):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            if _METADATA_LINE.match(line):
                in_examples = False
            continue
        if in_examples and re.match(r"^(?:Requires?|Must|Only|Cannot|Allowed|Valid|Range|Default)\b", line):
            in_examples = False
        if in_examples or line.startswith(("$ ", "> ", "https://", "http://")):
            continue
        # Strip a release annotation without discarding the rule after it.
        line = re.sub(r"^(?:[\w.-]+\s+){0,3}v?\d+(?:\.\d+){1,3}(?:[a-z]\d*)?:\s*", "", line)
        line = _RELEASE_HEADING.sub("", line)
        line = re.sub(r"\s*\((?:added|introduced|since|version)\s+[^)]*\)", "", line, flags=re.I)
        line = re.sub(r"\bReference scope:.*$", "", line, flags=re.I)
        line = re.sub(r"\s+in [A-Za-z][\w-]* v?\d+(?:\.\d+){1,3}\b", "", line)
        line = re.sub(r"\s+v?\d+(?:\.\d+){1,3}(?= (?:date grammar|defaults|reference)\b)", "", line)
        line = re.sub(r"Releases before \d+(?:\.\d+)+ have ", "Other targets may have ", line)
        line = re.sub(r"\s+such as \d+[a-z]+(?:\d+[a-z]+)*", "", line)
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    sentences, seen = [], set()
    for paragraph in paragraphs:
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", paragraph):
            sentence = re.sub(r"\.{2}$", ".", sentence.strip())
            if not sentence or _BACKGROUND.match(sentence) or sentence == "Documented option":
                continue
            key = sentence.rstrip(".")
            if key not in seen:
                seen.add(key)
                sentences.append(sentence)
    return tuple(sentences)


def concise_value_lines(lines):
    """Keep value rules from the shared formatter, omitting audit scaffolding.

    Target-dependent alternatives remain separate, with an applicability warning
    and any platform/chip restrictions. Release identifiers stay in search only.
    Required arity is shown once by option_text; optional omission behavior stays.
    """
    result, seen = [], set()
    specials = {}

    def flush_specials():
        """Group identical sentinel meanings only within their value scope."""
        for (magnitude, meaning), syntaxes in specials.items():
            meaning = " ".join(concise_description(meaning))
            result.append(f"{magnitude} ({', '.join(syntaxes)}): {meaning}")
        specials.clear()

    for line in lines:
        if line.startswith(("Value variant ", "Component ")):
            flush_specials()
            # Repeated forms in different variants are not redundant: each set
            # belongs to its own applicability or positional component.
            seen.clear()
        if line.startswith(("Evidence:", "Investigation:", "Reference:", "Source qualification:",
                            "Subject:", "Option absent:", "Operand omitted: not accepted",
                            "Bare-number rule: not applicable")):
            continue
        special = re.fullmatch(r"Special input (.*), magnitude (.*?): (.*)", line)
        if special:
            syntax, magnitude, meaning = special.groups()
            specials.setdefault((magnitude, meaning), []).append(syntax)
            continue
        if line.startswith("Applies to:"):
            restrictions = re.findall(r"(?:platform|chip): [^;.]+", line)
            restrictions = [item for item in restrictions if "not verified" not in item]
            line = "Applicability unconfirmed" + ("; " + "; ".join(restrictions) if restrictions else "") + "."
        if line.startswith("Delegated grammar:"):
            line = line.split(";", 1)[0] + "."
        line = line.removeprefix("Input VALUE; ")
        line = re.sub(r"^(Input (\S+)); accepted tokens '\2'", r"\1", line)
        if line.startswith(("Value", "Component")):
            line = line.replace("; scoped)", ")").replace(" (scoped)", "")
            line = re.sub(r" \((?:source derived|unresolved|synthetic|not documented)\)(?=:)",
                          " (unverified)", line)
        for sentence in concise_description(line):
            if sentence not in seen:
                seen.add(sentence)
                result.append(sentence)
    flush_specials()
    return tuple(result)


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
            "Value guidance unavailable; units have not been inferred.",
        ), notice="[review]")
    # Multiple scopes stay explicit even when the first explanation is clipped.
    compact = lines[0]
    list_hint = ""
    if compact.startswith(("Value:", "Value (")):
        heading, _, body = compact.partition(": ")
        qualifier = heading.removeprefix("Value").strip()
        # Remove only predictable presentation labels, retaining the bare-number
        # rule, every qualification and the complete unshortened meaning.
        body = "bare: " + body[len("bare numbers: "):] if body.startswith("bare numbers: ") else body
        compact = (qualifier + " " if qualifier else "") + body
        # Only value interpretation adds information worth a second list phrase.
        # Keep its entire qualification and meaning; the renderer may omit the
        # hint when it cannot fit, but must never truncate it into a partial rule.
        if body.startswith(("bare: ", "ordinary bare numbers not accepted")):
            list_hint = compact
    notice = "[unverified]" if ("not verified" in compact or any(
        line.startswith("Evidence: ") and line != "Evidence: verified." for line in lines)) else ""
    if any(line.startswith("Value variant 2") for line in lines):
        compact = "Value varies by applicability; see details."
        lines = ("Value varies by applicability; all documented alternatives follow. No target match is assumed.",) + lines
        list_hint, notice = "", "[varies]"
    return ValueText(compact, concise_value_lines(lines), list_hint, notice, tuple(lines))


def _source_notes(profile, option):
    """Retain associated review evidence for search without activating alternatives."""
    document = profile.get("documentation")
    if not isinstance(document, dict):
        return (), False
    selected = []
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
    return tuple(selected), needs_review


def description_blocks(summary, detail):
    """Join wrapped descriptions and remove repeated summary/detail prose."""
    summary = " ".join(concise_description(summary))
    detail = " ".join(concise_description(detail))
    if summary and detail.startswith(summary) and (
            len(detail) == len(summary) or detail[len(summary)] in " .;:,!?"):
        return concise_description(detail)
    return concise_description(summary + "\n\n" + detail)


def option_text(profile, category, option, *, positional=None):
    """Build concise details without changing stored evidence or legacy search."""
    numerical = value_text(profile, option)
    positional = value_text(profile, profile, positional=True) if positional is None else positional
    notes, needs_review = _source_notes(profile, option)
    lines = list(numerical.lines)
    if needs_review:
        lines.insert(0, "Conflicting or incomplete value guidance; verify before use.")
    # Review warnings precede ordinary prose even if active metadata is absent.
    lines.append("Option: " + option_label(option))
    description = description_blocks(option["summary"], option.get("detail", ""))
    # A grammar copied verbatim into both metadata and prose is shown once.
    value_clauses = {clause.rstrip(".") for line in numerical.lines
                     for clause in line.split("; ")}
    for sentence in description:
        key = sentence.rstrip(".")
        if key not in value_clauses:
            lines.append(sentence)
    if option.get("argument"):
        label = "Optional argument: " if option.get("argument_optional") else "Argument required: "
        if option.get("argument_style") == "attached_only":
            label = "Optional attached argument: " if option.get("argument_optional") else "Attached argument required: "
        lines.append(label.rstrip(": ") + ".")
    # Raw text and formatter evidence remain searchable for compatibility.
    legacy = option["flag"] + " " + option["summary"] + " " + option.get("detail", "")
    searchable = [legacy, option.get("argument", ""), *notes, *numerical.searchable_lines, *lines]
    if profile.get("positional_group"):
        group = profile["positional_group"]
        repeated = "Repeated value group (command-wide): " + group["argument"] + "."
        group_lines = (repeated, *positional.lines)
        lines.extend(group_lines)
        searchable.extend(group_lines)
        searchable.extend(positional.searchable_lines)
    compact = numerical.compact
    list_hint, notice = numerical.list_hint, numerical.notice
    if needs_review:
        compact = "Source review needed; " + (compact or "see details.")
        list_hint, notice = "", "[review]"
    summary = next(iter(concise_description(option["summary"])), "")
    return OptionText(compact, tuple(lines), " ".join(searchable).casefold(), list_hint, notice, summary)
