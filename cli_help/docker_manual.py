"""Read the run and image-list OPTIONS tables in Docker's packaged manuals."""

import re


def option_term(line, following):
    """Recognize a table term with an aligned, inline or indented explanation."""
    if not line.startswith("       -"):
        return None
    columns = re.split(r"\s{2,}|(?<=\[\]) (?=[A-Z])", line.strip(), maxsplit=1)
    if len(columns) == 1 and not following.startswith("        "):
        return None
    match = re.fullmatch(r"(?:(-[a-zA-Z])(?:,\s*|\|))?(--[\w-]+)(.*)", columns[0])
    return (columns, match) if match else None


def without_groff_warnings(lines):
    """Rejoin stdout around groff diagnostics interleaved in the probe's combined pipe."""
    result = list(lines)
    for index, line in enumerate(result):
        prefix, warning, _ = line.partition("troff:<standard input>:")
        if not warning or ": warning" not in line:
            continue
        following = index + 1
        while following < len(result) and re.match(r"^<standard input>:\d+: warning", result[following]):
            result[following] = ""
            following += 1
        result[index] = prefix
        if prefix.strip() and following < len(result):
            result[index] += result[following]
            result[following] = ""
    return result


def docker_manual_document(lines, source, command):
    """Read declarations from a matching Docker manual, retaining their parameter descriptions.

    Both pages use the same DOCKER(1) title. Check NAME for the exact subject.
    The run manual prints a separate indented lead, then paragraphs at term
    indentation. Image ls puts its lead on the term line. Boolean examples
    spell out true/false, accepted as an explicit assignment, not as a required
    following operand. The original declaration remains available in Details.
    """
    if (tuple(command) not in (("docker", "run"), ("docker", "image", "ls")) or not lines
            or not lines[0].startswith("DOCKER(1)") or "OPTIONS" not in lines
            or not any(line.lstrip().startswith("-".join(command) + " - ") for line in lines[:8])):
        return None
    entries, positions = [], []
    # Discovery captures stderr and stdout together. A groff table-width
    # warning can occur mid-definition; it is not a new manual section.
    lines = without_groff_warnings(lines)
    index = lines.index("OPTIONS") + 1
    while index < len(lines):
        raw = lines[index]
        if raw.strip() and not raw[0].isspace():
            break
        index += 1
        term = option_term(raw, lines[index] if index < len(lines) else "")
        if term is None:
            continue
        start = index
        columns, match = term
        signature, *inline = columns
        short, name, value = match.groups()
        value = value.strip()
        if value in ("=true|false", "[true|false]", "true|false", "[=false]", "[=true]"):
            argument = ""
        elif value or name in ("--stop-timeout", "--storage-opt"):
            argument = value.removeprefix("=")
            if argument in ("", "[]", '""'):
                argument = "VALUE"
        else:
            argument = ""
        body = inline[:]
        while index < len(lines):
            line = lines[index]
            if line and not line[0].isspace():
                break
            if (index and not lines[index - 1].strip()
                    and option_term(line, lines[index + 1] if index + 1 < len(lines) else "")):
                break
            body.append(line.strip())
            index += 1
        detail = "\n".join(body).strip()
        lead = " ".join(detail.split("\n\n", 1)[0].splitlines())
        summary = re.split(r"(?<=[.!?])\s+(?=[A-Z])", lead, maxsplit=1)[0] or "Documented option"
        if name == "--kernel-memory":
            summary = "Accept a legacy kernel memory limit (Docker 29.1.3 ignores it)."
            detail = ("Docker CLI 29.1.3 accepts the value for compatibility. It has no effect on the container. "
                      "The installed manual describes earlier behavior:\n" + detail)
        for flag in (short, name):
            if flag:
                entries.append({"flag": flag, "argument": argument, "argument_optional": False,
                                "summary": summary, "detail": f"{detail}\n\nSyntax: {signature}\nSource: {source}",
                                "category": "Options"})
                positions.append(start)
    return {"options": entries, "option_lines": positions, "shared": []}
