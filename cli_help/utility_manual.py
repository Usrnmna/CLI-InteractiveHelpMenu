"""Read the option sections of six independently formatted utility manuals."""

import re


_SECTIONS = {
    "jq": {"INVOKING JQ"}, "rsync": {"OPTIONS", "DAEMON OPTIONS"},
    "rg": {"OPTIONS"}, "wget": {"OPTIONS"}, "xz": {"OPTIONS"}, "gzip": {"OPTIONS"},
}
_SPELLING = re.compile(r"^(--?[A-Za-z0-9][A-Za-z0-9_.-]*|-[.@#:])(?=$|[\s=\[])(.*)$")


def _signature(command, line):
    """Split an actual declaration at the seven-column manpage tag boundary.

    Return (rows, inline prose), including explicit numeric filter slots.
    Ignore nonliteral grammars and descriptive paragraphs in the same column.
    """
    if command == "jq":
        if not line.endswith(":"):
            return [], ""
        line = line[:-1]
    if line in {"--", "--no-OPTION", "-0 ... -9"}:
        return [], ""
    if command == "wget" and line.startswith("--no-follow-ftp is the only way"):
        return [{"flag": "--no-follow-ftp", "argument": "", "argument_optional": False}], line
    if line == "--filters1=filters ... --filters9=filters" and command == "xz":
        return [{"flag": f"--filters{index}=", "argument": "filters", "argument_optional": False}
                for index in range(1, 10)], ""
    if command == "gzip" and line == "-# --fast --best":
        line = "--fast, --best"
    line = line.rstrip(",").replace(", (", ", ").rstrip(")")
    # Short man tags can share their first body line with the declaration.
    match = re.match(r"^(--help|--best|-D|-F|-P)\s+([A-Z].*)$", line)
    inline = match[2] if match else ""
    if match:
        line = match[1]
    parts = re.split(r"(?:,\s+| / | or | and | )(?=-)", line)
    rows = []
    for part in parts:
        match = _SPELLING.fullmatch(part)
        if not match:
            return [], ""
        flag, tail = match[1], match[2].strip()
        optional = tail.startswith("[") and tail.endswith("]")
        if tail.startswith("="):
            flag += "="
            tail = tail[1:]
        # Multiword operands are explicit on jq's variable-binding rows.
        paired = command == "jq" and flag in {"--arg", "--argjson", "--slurpfile", "--rawfile"}
        if not paired and " " in tail:
            return [], ""
        row = {"flag": flag, "argument": tail, "argument_optional": optional}
        if paired:
            row["argument_count"] = 2
        if command == "jq" and flag in {"--from-file", "-f"}:
            row["argument"] = "filename"
        rows.append(row)
    value = next((row for row in rows if row["argument"]), None)
    if value:
        for row in rows:
            if not row["argument"]:
                row.update(argument=value["argument"], argument_optional=value["argument_optional"])
    return rows, inline


def utility_manual_document(lines, command, source, summarize):
    """Read matching installed man(1) pages and retain explicit option owners.

    GNU roff tags appear at indent seven, bodies below that column, and
    subsection titles above it. Consecutive tags without descriptions share
    the next paragraph. Other implementations and stripped excerpts fall back
    to the normal parser. Source line numbers refer to the unmodified input.
    """
    if command not in _SECTIONS or not lines or not lines[0].lower().startswith(command + "(1)"):
        return None
    if not any(line in _SECTIONS[command] for line in lines):
        return None
    entries, positions, shared = [], [], []
    tags, body = [], []
    section = ""

    def finish():
        """Apply one block of source prose to its explicit adjacent tags."""
        plain = "\n".join(body).strip()
        for row, position in tags:
            if isinstance(row, str):
                shared.append({"source": source, "line": position, "section": section,
                               "text": row + ("\n" + plain if plain else ""),
                               "options": [], "association": "unassigned"})
                continue
            detail = plain
            if section == "DAEMON OPTIONS":
                detail = "With --daemon: " + detail
            entries.append({**row, "summary": summarize(detail),
                            "detail": detail + "\nSource: " + source, "category": section.title()})
            positions.append(position)
        tags.clear()
        body.clear()

    for position, raw in enumerate(lines, 1):
        line = raw.strip()
        indent = len(raw) - len(raw.lstrip())
        if line and indent == 0:
            finish()
            section = raw if raw in _SECTIONS[command] else ""
            continue
        if not section:
            continue
        if line and 0 < indent < 7:
            finish()
            continue
        if line.startswith("-") and indent == 7:
            if any(body):
                finish()
            rows, inline = _signature(command, line)
            if not rows:
                finish()
                # Preserve unsupported templates in the source context. A
                # later literal reference in a paragraph is not a declaration.
                tags.append((line, position))
                continue
            tags.extend((row, position) for row in rows)
            if inline:
                body.append(inline)
        elif tags:
            body.append(line)
    finish()
    return {"options": entries, "option_lines": positions, "shared": shared}


def complete_utility_declarations(parsed, command, text, source):
    """Restore explicit alias relationships and fixed-help omissions at audited roots.

    Preserve original description text and source lines. Explicit inverse
    sentences describe the positive declaration, so give the inverse its own
    summary. The full client signatures and their exceptions are recorded in
    docs/essential-utilities.md.
    """
    entries, positions = [], []
    declared = {option["flag"] for option in parsed["options"]}

    def add(spelling, option, line):
        """Add an explicitly referenced, distinct spelling at its source line."""
        if spelling not in declared:
            entries.append({**option, "flag": spelling})
            positions.append(line)
            declared.add(spelling)
    for option, line in zip(parsed["options"], parsed["option_lines"]):
        flag, detail = option["flag"], option["detail"]
        if command == "rsync" and flag == "--no-OPTION" and "turn off an implied OPTION" in detail:
            parsed["shared"].append({"text": flag + " " + option["summary"], "source": source, "line": line,
                                     "section": option["category"], "association": "unassigned", "options": []})
            continue
        if command == "jq" and flag in ("-f", "--from-file") and "load the filter from a file" in detail:
            option["argument"] = option["argument"] or "FILE"
        if command == "wget" and flag == "--hsts-file" and "path of HSTS database" in detail:
            option["argument"] = option["argument"] or "FILE"
        if command == "wget" and flag == "--max-redirect" and "maximum redirections allowed" in detail:
            option["argument"] = option["argument"] or "NUMBER"
        if command == "wget" and flag == "--preferred-location" and "Metalink resources" in detail:
            option["argument"] = option["argument"] or "LOCATION"
        if command == "wget" and flag in {"--input-metalink=", "--metalink-index=", "--metalink-over-http",
                                          "--preferred-location"}:
            option["detail"] += "\nRequires a Wget build with Metalink support."
        if command == "wget" and flag in {"--dns-servers=", "--bind-dns-address="}:
            option["detail"] += "\nRequires a Wget build with c-ares support."
        if command == "curl" and flag in ("-h", "--help") and option["argument"] == "<subject>":
            option.update(argument="[<subject>]", argument_optional=True)
            option["detail"] += "\nOmit the subject for short help, or specify a category or option. Use all for the complete list."
        if ((command, flag) in {("tail", "-f"), ("sort", "-c")} and option["argument"].startswith("[=")
                and re.search(r"(?m)^\s*" + re.escape(flag) + r", --(?:follow|check)\[=", text)):
            option.update(argument="", argument_optional=False)
        if command == "rsync" and flag in ("-N", "--crtimes") and "no crtimes" in text.split("Usage:", 1)[0]:
            option["detail"] += "\nThis build reports no creation-time support."
        entries.append(option)
        positions.append(line)
        if command == "rsync" and (alias := re.search(r"\(aka (--[a-z]+)\)", detail)):
            spelling = alias[1] + ("=" if flag.endswith("=") else "")
            add(spelling, option, line)
        if command == "rg" and flag.startswith("--"):
            aliases = re.findall(r"An alternative spelling for this flag is (--[a-z0-9-]+)\.", detail)
            for alias in aliases:
                add(alias + ("=" if flag.endswith("=") else ""), option, line)
            inverses = re.findall(r"(?m)^This flag can be disabled (?:with|by) ((?:-[A-Za-z]/)?--[a-z0-9-]+)\.$", detail)
            for owner, spelling in (("--pre=", "--no-pre"), ("--encoding=", "--no-encoding"),
                                    ("--context-separator=", "--no-context-separator")):
                if flag == owner and spelling in detail:
                    inverses.append(spelling)
            for inverse in inverses:
                for spelling in inverse.split("/"):
                    summary = {"--no-encoding": "Restore automatic encoding detection.",
                               "--no-pre": "Disable preprocessing of input files.",
                               "--no-context-separator": "Omit context separators, including their line breaks."
                               }.get(spelling, "Disable " + flag.rstrip("=") + ".")
                    add(spelling, {"argument": "", "argument_optional": False,
                                   "category": option["category"], "summary": summary,
                                   "detail": summary + "\n\nSource describes " + flag + ":\n" + detail}, line)
        if command == "wget" and flag == "--adjust-extension" and "--html-extension" in detail:
            add("--html-extension", {**option, "detail": "Historical name for --adjust-extension.\n" + detail}, line)
        if command == "wget" and flag == "--no-iri" and "--iri" in detail:
            add("--iri", {**option, "summary": "Enable internationalized URI support.",
                          "detail": "Source describes --no-iri:\n" + detail}, line)
        if command == "wget" and flag == "--no-check-certificate" and "--check-certificate=quiet" in detail:
            add("--check-certificate", {**option, "summary": "Control server certificate verification.",
                "argument": "[=MODE]", "argument_optional": True,
                "detail": "The quiet setting suppresses invalid-certificate warnings and permits the download.\n\n"
                          "Source describes --no-check-certificate:\n" + detail}, line)
    if command == "rsync" and text[:8].lower() == "rsync(1)":
        _rsync_prose_options(text, add, source)
    parsed.update(options=entries, option_lines=positions)


def _rsync_prose_options(text, add, source):
    """Recover named client switches in option prose, never arbitrary example words.

    Each spelling below is a literal entry in the 3.2.7 and 3.4.1 client
    option tables. Publish it only where the installed manual actually names
    it. An accepted tag alone does not establish its presence in this source.
    """
    forms = {
        "--no-D": "Omit device and special-file preservation.",
        "--no-R --no-relative": "Omit leading source path components.",
        "--no-blocking-io": "Use nonblocking remote-shell I/O.",
        "--no-compress": "Clear the selected compression method.",
        "--no-d --no-dirs": "Disable copying directory entries without recursion.",
        "--no-g": "Use the destination group instead of preserving the source group.",
        "--no-h --no-human-readable": "Print numbers as plain digits.",
        "--no-iconv": "Disable filename character-set conversion.",
        "--no-links": "Skip symbolic links instead of copying them as links.",
        "--no-old-args": "Restore remote-shell argument protection.",
        "--no-o --no-owner": "Omit preservation of file owners.",
        "--no-p --no-perms": "Use destination permission defaults.",
        "--no-r": "Disable recursion.",
        "--no-s --no-secluded-args": "Pass remote arguments through the shell.",
        "--no-super": "Disable privileged receiver behavior.",
        "--msgs2stderr": "Write all messages directly to standard error.",
        "--no-msgs2stderr": "Route remote messages through the client.",
        "--old-compress": "Select classic zlib compression.",
        "--new-compress": "Select zlibx compression.",
        "--protect-args": "Send protected remote arguments through the rsync protocol.",
    }
    names = {name: meaning for spellings, meaning in forms.items() for name in spellings.split()}
    line = 1
    for paragraph in text.split("\n\n"):
        mentioned = set(re.findall(r"(?<![\w=-])--[\w-]+", re.sub(r"(?<=-)\n\s*", "", paragraph)))
        for name in sorted(mentioned & names.keys()):
            add(name, {"summary": names[name], "argument": "", "argument_optional": False, "category": "Options",
                       "detail": names[name] + "\n\n" + paragraph.strip() + "\nSource: " + source}, line)
        line += paragraph.count("\n") + 2
