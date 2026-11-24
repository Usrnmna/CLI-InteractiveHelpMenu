"""Read compiler help tables while respecting literal spellings and build-tool modes."""

import re

# Only these CMake mode selectors apply at the root outside the configure and
# built-in help sections. Their remaining options belong to individual modes.
CMAKE_MODES = {
    "BUILD A PROJECT": "--build",
    "INSTALL A PROJECT": "--install",
    "OPEN A PROJECT": "--open",
    "RUN A SCRIPT": "-P",
    "RUN A COMMAND-LINE TOOL": "-E",
    "RUN THE FIND-PACKAGE TOOL": "--find-package",
    "RUN A WORKFLOW PRESET": "--workflow",
}


def _manual_terms(lines, cmake):
    """Yield formatted manual terms with their original definitions and section ownership."""
    section = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if line and not line.startswith(" "):
            section = line
            continue
        if not re.match(r"^ {7}-", line):
            continue
        n = i
        term = line.strip()
        while term.endswith(",") and i < len(lines) and re.match(r"^ {7}-", lines[i]):
            term += " " + lines[i].strip()
            i += 1
        # Groff puts short terms and their description on the same line.
        pieces = re.split(r"\s{2,}|(?<=--help) (?=[A-Z])", term, maxsplit=1)
        term = pieces[0]
        body = pieces[1:]
        while i < len(lines) and (not lines[i].strip() or lines[i].startswith(" " * 8)):
            body.append(lines[i].strip())
            i += 1
        if cmake and section not in {"GENERATE A PROJECT BUILDSYSTEM", "VIEW HELP"}:
            if term.split()[0] != CMAKE_MODES.get(section):
                continue
        if any(body):
            yield n, term, "\n".join(body).strip()


def _help_terms(lines, cmake):
    """Read the fixed option columns without treating examples or generators as rows."""
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if line == "Generators" and cmake:
            return
        if not line.startswith("  -"):
            continue
        n = i
        if cmake:
            term, separator, rest = line[2:].partition("= ")
            term = term.rstrip()
            body = [rest] if separator else []
        else:
            # LLVM pads short terms to the description column. Long terms
            # have no inline description and continue at that same column.
            padded = len(line) > 26 and line[25] == " " and line[26].isupper()
            if not padded and len(line) > 26 and line[25] == " ":
                padded = not (line.endswith(">") and line.count("  ") == 1)
            term = (line[2:25] if padded else line[2:]).strip()
            body = [line[26:]] if padded else []
        while i < len(lines) and lines[i].startswith(" " * 8):
            body.append(lines[i].strip().removeprefix("= "))
            i += 1
        if any(body):
            yield n, term, "\n".join(body).strip()


def _declarations(signature, cmake):
    """Yield supported literal spellings with their insertion style and operand shape."""
    for part in re.split(r",\s*(?=[-/])| (?=-[A-Za-z])", signature):
        part = part.strip()
        if cmake and re.match(r"^-LR?\[A\]\[H\]", part):
            prefix, _, arg = part.partition("[A][H]")
            for suffix in ("", "A", "H", "AH"):
                yield prefix + suffix, arg.strip(), {}
            continue
        match = re.fullmatch(r"(--?[a-zA-Z0-9][\w.-]*)(?:([= <\[])(.*))?", part)
        if not match:
            continue
        flag, delimiter, tail = match.groups()
        if delimiter == "<" and (flag.endswith(("-", "_")) or "> <" in tail):
            continue  # A compiler option template with a variable name.
        fields = {}
        arg = ((delimiter or "") + (tail or "")).strip()
        if cmake and flag in ("--workflow", "-E"):
            arg = ""
        elif delimiter == "=":
            arg = tail or "<value>"
            if ">" in arg and re.search(r">\s+<", arg):
                fields["argument_count"] = 2
            flag += "="
        elif delimiter == "<":
            fields["argument_style"] = "attached_only"
        elif delimiter == "[" and arg.startswith("[="):
            fields["argument_optional"] = True
            fields["argument_style"] = "equals"
        elif arg.startswith("["):
            fields["argument_optional"] = True
        yield flag, arg, fields


def compiler_help_document(text, source, command):
    """Return the compiler's bounded top-level declarations for a recognized page or banner."""
    if command not in (["cmake"], ["clang"]):
        return None
    cmake = command == ["cmake"]
    manual = text.startswith(command[0].upper() + "(1)")
    help_banner = "Usage\n\n  cmake [options]" if cmake else "OVERVIEW: clang LLVM compiler"
    if not manual and not text.startswith(help_banner):
        return None
    lines = text.splitlines()
    terms = _manual_terms(lines, cmake) if manual else _help_terms(lines, cmake)
    options, positions = [], []
    for n, signature, body in terms:
        for flag, arg, fields in _declarations(signature, cmake):
            if flag in ("-version", "--version") and cmake:
                arg = "[<file>]"
                fields["argument_optional"] = True
            if cmake and flag == "--help" and arg:
                fields["argument_optional"] = True
            if not cmake and flag == "-Ofast" and arg:
                fields["argument_optional"] = True
            lead = body.split("\n\n", 1)[0].replace("\n", " ")
            summary = re.split(r"(?<=[.!?])\s+(?=[A-Z])", lead, maxsplit=1)[0]
            options.append(
                {
                    "flag": flag,
                    "argument": arg,
                    "summary": summary,
                    "category": "Options",
                    "detail": f"{body}\n\nSyntax: {signature}\nSource: {source}",
                    **fields,
                }
            )
            positions.append(n)
    # A bare and a joined form describe one switch with an optional value.
    bare = {o["flag"] for o in options if not o["argument"]}
    optional = {o["flag"][:-1] for o in options if o["flag"].endswith("=") and o["flag"][:-1] in bare}
    for option in options:
        name = option["flag"].rstrip("=")
        if name in optional:
            option.update(flag=name, argument="[=value]", argument_optional=True, argument_style="equals")
    result = {"options": options, "option_lines": positions, "shared": []}
    if cmake:
        # CMake dispatches these modes before entering the configure parser.
        # -P and --find-package use the ordinary parser; -P documents the
        # existing -- delimiter for arguments passed unchanged to a script.
        dispatch = {"-E", "--build", "--install", "--open", "--workflow"}
        result["stop_at_options"] = sorted({o["flag"] for o in options} & dispatch)
    return result
