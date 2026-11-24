"""Interpret native declaration formats used by the system tools in discovery."""

import re


# systemctl prints the same root help and manual for every verb. These options
# have a documented effect on at least one of the three read-only views.
_UNIT_COMMON = set("""
--after --all --before --capsule --failed --full --help --host --introspect-cli
--legend --lines --machine --no-ask-password --no-legend --no-pager --no-warn
--output --plain --quiet --reverse --state --system --type --user --version
--with-dependencies -C -H -M -a -h -l -n -o -q -t
""".split())
_UNIT_EXTRA = {"list-units": {"--recursive", "-r"}, "show": {"--property", "-p", "-P", "--value",
               "--timestamp"}, "status": {"--timestamp"}}

# These columns omit an operand or use punctuation outside the generic
# placeholder grammar. The associated command manuals explain the syntax.
_REQUIRED = {
    "ss": {"-N": "NSNAME", "--net": "NSNAME"},
    "fd": {"-x": "<cmd>...", "--exec": "<cmd>...", "-X": "<cmd>...", "--exec-batch": "<cmd>..."},
    "podman build": {"--pull": "POLICY", "--creds": "USERNAME[:PASSWORD]", "--dns": "ADDRESS",
                     "--platform": "OS/ARCH[/VARIANT]"},
    "podman run": {"--blkio-weight-device": "DEVICE:WEIGHT", "--detach-keys": "SEQUENCE",
                   "--cert-dir": "PATH"},
}

# Each mapping is conditional on finding the alternate spelling in the
# active declaration's own text. Different fd releases expose different aliases.
_FD_ALIASES = {
    "--changed-within": ("--change-newer-than", "--newer", "--changed-after"),
    "--changed-before": ("--change-older-than", "--older"),
    "--one-file-system": ("--mount", "--xdev"), "--quiet": ("--has-results",),
}
_FD_REVERSES = {
    "--hidden": "--no-hidden", "--no-ignore": "--ignore", "--no-ignore-vcs": "--ignore-vcs",
    "--no-require-git": "--require-git", "--absolute-path": "--relative-path", "--follow": "--no-follow",
}


def ssh_manual(lines, source, summarize):
    """Read the option definitions at the main DESCRIPTION indent in the BSD manuals.

    Adjacent syntax alternatives share the explanation following the last tag.
    Stop at the next top-level chapter, before interactive escape commands.
    """
    options, positions, tags, body = [], [], [], []
    section = ""
    def finish():
        prose = "\n".join(body).strip()
        for name in dict.fromkeys(t[0] for t in tags):
            forms = [t for t in tags if t[0] == name]
            syntaxes = list(dict.fromkeys(name + " " + arg for _, arg, _ in forms if arg))
            detail = ("Syntax: " + "\n".join(syntaxes) + "\n" if syntaxes else "") + prose
            options.append(dict(flag=name, argument=forms[0][1], argument_optional=False,
                                summary=summarize(prose), detail=detail + "\nSource: " + source,
                                category="Options"))
            positions.append(forms[0][2])
        tags.clear()
        body.clear()
    for number, raw in enumerate(lines, 1):
        if raw and not raw[0].isspace():
            finish()
            section = raw.strip()
            continue
        if section != "DESCRIPTION":
            continue
        tag = re.fullmatch(r" {7}(-[a-zA-Z0-9])(?: (?! )(.+?))?(?: {2,}(.+))?", raw.rstrip())
        if tag:
            if any(s.strip() for s in body):
                finish()
            flag, argument, inline = tag.groups()
            tags.append((flag, argument or "", number))
            if inline:
                body.append(inline)
        elif tags:
            body.append(raw.strip())
    finish()
    return options, positions


def _podman_manual(lines, source, command, summarize):
    """Read an entire Podman option paragraph under its three-space Markdown heading.

    A complex inline value such as --volume, -v=[[SOURCE:]DEST[:OPTIONS]]
    remains syntax. The heading starts a new owner even when the value has
    deeper nesting or spaces. Tables, examples and suffix rules stay with it.
    """
    rows, positions = [], []
    in_options = False
    headings = []
    for index, raw in enumerate(lines):
        if raw and not raw[0].isspace():
            if in_options:
                break
            in_options = raw == "OPTIONS"
        elif in_options and re.match(r"^   --?[A-Za-z0-9]", raw):
            headings.append(index)
    else:
        index = len(lines)
    for start, end in zip(headings, [*headings[1:], index]):
        tag = lines[start].strip()
        body = "\n".join(line.strip() for line in lines[start + 1:end]).strip()
        forms = list(re.finditer(r"(?:^|, )(--?[A-Za-z0-9][\w-]*)(?=$|[,= ])", tag))
        for form in forms:
            flag = form[1]
            if (command == ["podman", "build"] and flag == "--runtime"
                    or command == ["podman", "run"] and flag == "--link-local-ip"):
                continue
            operand = tag.split("=", 1)[1].split(", -", 1)[0] if "=" in tag else ""
            optional = command == ["podman", "build"] and flag == "--pull"
            if flag == "--logsplit":
                operand = ""  # Optional Boolean assignment, usable as a bare switch.
            rows.append(dict(flag=flag, argument=operand, argument_optional=optional,
                             summary=summarize(body), detail="Syntax: " + tag + "\n" + body
                             + "\nSource: " + source, category="Options"))
            positions.append(start + 1)
    return rows, positions


def _alias_rows(rows, positions):
    """Copy the syntax of explicitly documented fd aliases and label negative switches."""
    existing = {o["flag"] for o in rows}
    for row, position in list(zip(rows, positions)):
        original = row["flag"]
        reverse = _FD_REVERSES.get(original)
        text = " ".join(row["detail"].split())
        for alias in (*_FD_ALIASES.get(original, ()), *((reverse,) if reverse else ())):
            if alias in existing or not re.search(r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])", text):
                continue
            summary = f"Reverse the effect of {original}." if alias == reverse else row["summary"]
            details = (summary + "\n" if alias == reverse else f"Alias for {original}.\n") + row["detail"]
            rows.append({**row, "flag": alias, "summary": summary, "detail": details})
            positions.append(position)
            existing.add(alias)


def _literal_alternatives(rows, positions, lines, source, program):
    """Recover literal long options printed after an unrepresentable punctuation alias."""
    existing = {o["flag"].rstrip("=") for o in rows}
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*\+[a-z],\s+(--[a-z-]+)\s*(.*)", line) if program == "fzf" else None
        if program == "psql":
            match = re.match(r"^\s*-\?,\s+(--help)\[=\w+\]\s+(.*)", line)
        if not match:
            continue
        flag, prose = match.groups()
        if flag in existing:
            continue
        if not prose and number < len(lines):
            prose = lines[number].strip()
        existing.add(flag)
        rows.append(dict(flag=flag, argument="TOPIC" if program == "psql" else "",
                         argument_optional=program == "psql", summary=prose or "Documented option",
                         detail=line.strip() + "\n" + prose + "\nSource: " + source, category="Options"))
        positions.append(number)


def complete_system_document(parsed, lines, source, command, summarize):
    """Correct a recognized native response in place, preserving its source line numbers."""
    if not command or not lines:
        return
    program = command[0]
    page = source.removeprefix("man ")
    manual = source.startswith("man ") and bool(re.match(r"[\w.+-]+\(\d\w*\)", lines[0], re.I))
    first = lines[0].strip()
    if program == "podman" and manual and page == "-".join(command):
        rows, positions = _podman_manual(lines, source, command, summarize)
        if rows:
            parsed["options"], parsed["option_lines"] = rows, positions
        return
    if command == ["ip", "address"] and manual and page == "ip-address":
        # The next bare keyword or object heading closes a negative selector.
        for row, position in zip(parsed["options"], parsed["option_lines"]):
            paragraph = []
            for body in lines[position:]:
                if not body.strip() or len(body) - len(body.lstrip()) <= 7:
                    break
                paragraph.append(body.strip())
            if paragraph:
                prose = " ".join(paragraph)
                row.update(summary=summarize(prose), detail=prose + "\nSource: " + source)
        # This pair is defined in one paragraph under the positive names.
        for i, line in enumerate(lines):
            if line.strip() == "dynamic and permanent":
                paragraph = []
                for body in lines[i + 1:]:
                    if not body.strip():
                        break
                    paragraph.append(body.strip())
                explanation = " ".join(paragraph)
                for flag, summary in (("-dynamic", "List only permanent IPv6 addresses."),
                                      ("-permanent", "List only dynamically configured IPv6 addresses.")):
                    if flag in explanation:
                        parsed["options"].append(dict(flag=flag, argument="", argument_optional=False,
                            summary=summary, detail=explanation + "\nSource: " + source, category="Options"))
                        parsed["option_lines"].append(i + 1)
        return
    if program in {"ssh", "scp", "sftp"} and manual and page == program and first.lower().startswith(program + "(1)"):
        rows, positions = ssh_manual(lines, source, summarize)
        if rows:
            parsed["options"], parsed["option_lines"] = rows, positions
        return
    specific_help = {
        "systemctl": first.startswith("systemctl ["), "journalctl": first.startswith("journalctl ["),
        "fd": first.startswith("A program to find entries"), "fdfind": first.startswith("A program to find entries"),
        "ss": first.startswith("Usage: ss "), "fzf": (first.lower().startswith("usage: fzf ")
                or first.startswith("fzf is an interactive filter")),
        "psql": first.startswith("psql is the PostgreSQL"), "podman": any(
            l.strip().startswith("podman " + " ".join(command[1:]) + " [options]") for l in lines[:18]),
        "openssl": first.startswith("Usage: " + " ".join(command[1:]) + " "),
    }
    if program not in specific_help or not (manual or specific_help[program]):
        return
    if manual and page not in {program, "-".join(command)}:
        return
    family = "fd" if program == "fdfind" else program
    required = _REQUIRED.get(" ".join(command), _REQUIRED.get(family, {}))
    rows, positions = [], []
    section = ""
    sections = []
    for line in lines:
        if line and not line[0].isspace():
            section = line
        sections.append(section)
    for row, position in zip(parsed["options"], parsed["option_lines"]):
        raw = lines[position - 1]
        flag = row["flag"].rstrip("=")
        if manual:
            section = sections[position - 1]
            allowed = section == "OPTIONS" or program == "journalctl" and (
                section.endswith(" OPTIONS") or section == "COMMANDS")
            if not allowed:
                continue
            if program == "podman" and (not raw.startswith("   -") or flag in {"--runtime", "--link-local-ip"}):
                continue
            if program == "fzf" and not raw.startswith("       -"):
                continue
            if program == "openssl" and flag == "-digest":
                continue  # A placeholder for an algorithm name.
        if program == "systemctl" and len(command) == 2 and command[1] in _UNIT_EXTRA:
            if flag not in _UNIT_COMMON | _UNIT_EXTRA[command[1]]:
                continue
        if flag in required:
            row["argument"] = required[flag]
            row["argument_optional"] = False
            if flag == "--pull" and command == ["podman", "build"]:
                row.update(argument_optional=True, argument_style="equals")
                row["summary"] = "Choose when to pull the base image."
                row["detail"] = ("Bare --pull means always. Attach the explicit policy with '='. "
                                 "On Ubuntu 24.04 and 26.04 newer maps to missing. "
                                 "The false policy maps to missing on Ubuntu 24.04 and never on Ubuntu 26.04.\n"
                                 + row["detail"])
        if not manual and program == "podman" and flag in {"--disable-content-trust", "--compress"}:
            row["summary"] = "Accept a compatibility switch with no effect."
        if not manual and program == "ss" and flag in {"-A", "--query", "--socket"}:
            row["summary"] = "Select the socket tables to display."
        if not manual and family == "fd" and flag in {"-x", "--exec", "-X", "--exec-batch"}:
            row["summary"] = ("Run the command once per result." if flag in {"-x", "--exec"}
                              else "Run the command with a batch of results.")
        if program == "psql" and flag == "--help":
            # The values 'commands' and 'variables' are optional topics. Bare
            # --help prints command-line help and takes no following word.
            row.update(flag="--help=", argument="TOPIC", argument_optional=True)
            if not manual:
                row["summary"] = "Show help for command-line options, commands or variables."
                row["detail"] = ("Use --help by itself, or attach =options, =commands or =variables. "
                                 "Quote the short alias as '-?' in Bash to prevent filename expansion.\nSource: " + source)
        if program == "journalctl" and flag in {"--list-catalog", "--dump-catalog"}:
            row.update(argument="", argument_optional=False)
        if program == "openssl" and not manual:
            signature = re.match(r"^ (-[\w-]+) (\+int|[A-Z0-9]+(?:\|[A-Z0-9]+)+)(?:\s|$)", raw)
            if signature and signature[1] == flag:
                row["argument"] = signature[2]
                row["summary"] = summarize(raw[signature.end():].strip())
                row["detail"] = row["detail"].removeprefix(signature[2] + " ")
        if program == "fzf" and flag == "--listen":
            row.update(flag="--listen", argument="SOCKET_PATH|[ADDR:]PORT" if "SOCKET_PATH" in raw
                       else "[ADDR:]PORT", argument_optional=True)
        if program == "fzf" and flag == "--listen" and "--listen-unsafe[" in raw:
            rows.append({**row, "flag": "--listen-unsafe",
                         "summary": "Allow remote execution actions on the listening server.",
                         "detail": "Unlike --listen, remote execution actions are allowed.\n" + row["detail"]})
            positions.append(position)
        rows.append(row)
        positions.append(position)
    if family == "fd":
        _alias_rows(rows, positions)
    if program in {"fzf", "psql"}:
        _literal_alternatives(rows, positions, lines, source, program)
    if program == "fzf":
        spellings = {row["flag"]: row for row in rows}
        for raw in lines:
            # Older fzf has a standalone +i. More recent help pairs +i with
            # a long name. Keep both searchable using the existing dash grammar.
            match = re.match(r"^\s*\+([a-z])(?:,\s+(--[a-z-]+))?\s+(.*)", raw.rstrip())
            if match and (owner := spellings.get(match[2] or ("-" + match[1]))):
                if raw.strip() not in owner["detail"]:
                    owner["detail"] += "\n" + raw.strip()
    parsed["options"], parsed["option_lines"] = rows, positions


def align_system_manual(parsed, command, source, profiles):
    """Return a manual whose syntax matches the installed client, preserving its input.

    The OpenSSL binary lists the features compiled into this build. An edition's
    generic manual can also document switches compiled out of that binary.
    """
    if not source.startswith("man ") or not profiles or command[0] not in {
            "podman", "openssl", "systemctl", "journalctl", "fzf", "psql", "ss", "fdfind"}:
        return parsed
    expected = command[0] + " " if command[0] != "openssl" else " ".join(command) + " "
    native = next((p for p in profiles if p["documentation"]["source"].startswith(expected)), None)
    if native is None:
        return parsed
    client = {o["flag"].rstrip("="): o for c in native["categories"] for o in c["options"]}
    rows, positions = [], []
    for row, number in zip(parsed["options"], parsed["option_lines"]):
        flag = row["flag"].rstrip("=")
        if command[0] == "openssl" and flag in {"-ssl3", "-sctp", "-sctp_label_bug"} and flag not in client:
            continue
        if flag in client:
            row = dict(row)
            original = client[flag]
            # Keep prose from both sources while using the executable's native syntax.
            for key in ("flag", "argument", "argument_count", "argument_optional", "argument_style"):
                if key in original:
                    row[key] = original[key]
                else:
                    row.pop(key, None)
        rows.append(row)
        positions.append(number)
    return {**parsed, "options": rows, "option_lines": positions}
