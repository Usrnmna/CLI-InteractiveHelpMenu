"""Read the fixed-column native FFmpeg and FFprobe short-help tables."""

import re


# These native declarations have an omitted metavar in at least one Ubuntu
# client. Only apply them to a recognized native help table and an existing row.
_MISSING_VALUES = {
    "ffmpeg": {"-filter_threads": "threads", "-filter_complex_threads": "threads",
               "-seek_timestamp": "0|1", "-apad": "parameters", "-reinit_filter": "0|1",
               "-discard": "mode", "-disposition": "dispositions"},
    "ffprobe": {"-print_format": "format", "-show_data_hash": "algorithm",
                "-show_log": "loglevel", "-show_optional_fields": "value"},
}


def media_help_document(lines, source):
    """Return a parsed native table, or None for other requests and abbreviated specimens.

    A fixed request, named usage banner and column layout establish each option's
    owner. Per-component AVOption values and defaults stay with their declaration.
    Only literal base spellings can reach insertion, including when a source
    marks the stream specifier optional. Source line numbers stay one-based.
    """
    program = source.partition(" ")[0]
    if program not in _MISSING_VALUES or source != program + " --help":
        return None
    if not any(line.startswith("usage: " + program + " ") for line in lines):
        return None
    rows, locations, variants = {}, [], {}
    section = ""
    active = None
    for number, line in enumerate(lines, 1):
        if line and not line[0].isspace() and line.endswith(":"):
            section = line[:-1]
            active = None
            continue
        if section.endswith(" AVOptions"):
            match = re.fullmatch(r"  (-[a-zA-Z0-9_][\w-]*)\s+(\[<[^>]+>\s*\]|<[^>]+>)\s*([A-Z.]{8,})\s*(.*)", line)
            if match:
                flag, argument, capabilities, prose = match.groups()
                if "X" in capabilities:
                    active = None
                    continue  # Exported component state cannot be set as a command option.
                argument = argument.replace(" ", "")
                summary = prose.split(" (from ")[0].split(" (default ")[0].strip()
                if not summary or summary.startswith("("):
                    summary = "Set " + flag[1:] + " for the applicable component."
                active = [f"{capabilities} {prose}".strip()]
                variants.setdefault(flag, []).append((section.removesuffix(" AVOptions"), active))
                category = "Component AVOptions"
                detail = ""
                optional = False
            else:
                if active is not None and line.startswith("     ") and line.strip():
                    active.append(line.strip())
                continue
        else:
            if not section or not line.startswith("-"):
                continue
            columns = re.split(r"\s{2,}", line.strip(), maxsplit=1)
            if len(columns) != 2:
                continue
            declaration, summary = columns
            match = re.fullmatch(r"(--?[A-Za-z0-9][\w-]*)(\[:<\w+>\])?(?: (.+))?", declaration)
            if not match:
                continue
            flag, selector, argument = match.groups()
            argument = argument or _MISSING_VALUES[program].get(flag, "")
            if flag == "-hide_banner":
                argument = ""
            optional = flag in {"-h", "-help", "--help", "-sources", "-sinks"}
            category = section
            detail = [summary, section + "."]
            if selector:
                detail.append("Declaration: " + declaration + ".")
                if selector == "[:<stream_spec>]":
                    detail.append("Append a colon and stream specifier to select streams, for example :v for video.")
            if flag in {"-h", "-help", "--help"}:
                detail.append("The help topic can be omitted. The -? alias also prints help.")
            detail = "\n".join(detail)
        if flag not in rows:
            rows[flag] = {"flag": flag, "argument": argument, "argument_optional": optional,
                          "summary": summary, "detail": detail, "category": category}
            locations.append(number)
    for flag, row in rows.items():
        # Multiple components frequently share byte-identical defaults and choices.
        # List each owner, retaining each distinct local definition exactly once.
        definitions = {}
        for owner, lines_for_owner in variants.get(flag, ()):
            definitions.setdefault("\n".join(lines_for_owner), []).append(owner)
        parts = [row["detail"]] if row["detail"] else []
        parts.extend(", ".join(dict.fromkeys(owners)) + ": " + explanation
                     for explanation, owners in definitions.items())
        parts.append("Source: " + source)
        row["detail"] = "\n".join(parts)
    return {"options": list(rows.values()), "option_lines": locations, "shared": []}


def media_manual_document(lines, source):
    """Read option definitions in the OPTIONS chapter of the two native section-1 pages.

    POD renders a seven-space declaration indent and a deeper body. Consecutive
    headings share the following explanation. Nested examples, writer settings
    and preset-file fields are outside those declarations.
    """
    if source not in {"man ffmpeg", "man ffprobe"}:
        return None
    program = source.split()[1]
    if not any(line.startswith(program.upper() + "(1)") for line in lines[:5]) or "OPTIONS" not in lines:
        return None
    entries, locations = [], []
    pending, body = [], []
    section = ""

    def finish():
        if pending:
            explanation = "\n".join(body).strip()
            lead = " ".join(explanation.split("\n\n", 1)[0].split())
            summary = re.split(r"(?<=[.!?])\s+(?=[A-Z])", lead, maxsplit=1)[0] or "Documented option"
            for flag, argument, optional, spelling, number in pending:
                entries.append({"flag": flag, "argument": argument, "argument_optional": optional,
                                "summary": summary, "category": section,
                                "detail": spelling + "\n" + explanation + "\nSource: " + source})
                locations.append(number)
        pending.clear()
        body.clear()

    for number in range(lines.index("OPTIONS") + 1, len(lines)):
        line = lines[number]
        if line and not line.startswith(" "):
            break
        if re.match(r"^   \S", line):
            finish()
            section = line.strip()
            continue
        if not section.lower().endswith("options") or section == "AVOptions":
            continue
        if not re.match(r"^       --?\S", line):
            if pending:
                body.append(line.strip())
            continue
        if any(body):
            finish()
        declaration = line.strip()
        signature, *inline = re.split(r"\s{2,}", declaration, maxsplit=1)
        signature = re.sub(r"\s+\([^()]*\)$", "", signature)
        aliases = re.split(r",\s+(?=-)|\s+\|\s+(?=-)", signature)
        parsed = []
        for alias in aliases:
            match = re.fullmatch(r"(--?[a-zA-Z0-9?][\w-]*)(?:\[:\w+\])?(?: (.+))?", alias)
            if match:
                parsed.append(match.groups())
        shared_argument = next((operand for _, operand in reversed(parsed) if operand), "")
        for flag, arg in parsed:
            # Removed/unregistered spellings still have prose in packaged pages.
            if flag in {"-?", "-sbsf", "-show_format_entry"}:
                continue
            argument = arg or shared_argument or _MISSING_VALUES[program].get(flag, "")
            if not argument and program == "ffmpeg":
                argument = {"-max_error_rate": "ratio", "-stream_group": "group",
                            "-map_channel": "channel"}.get(flag, "")
            optional = flag in {"-h", "-help", "--help", "-sources", "-sinks"}
            pending.append((flag, argument, optional, declaration, number + 1))
        body.extend(inline)
    finish()
    return {"options": entries, "option_lines": locations, "shared": []}
