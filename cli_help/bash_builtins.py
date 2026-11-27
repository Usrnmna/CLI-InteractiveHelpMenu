"""Read Bash's own help topics without evaluating any pending shell words."""

import re

from errors import HelpError


# Names returned by compgen -b on both supported Ubuntu Bash editions.
BUILTINS = frozenset("""
. : [ alias bg bind break builtin caller cd command compgen complete compopt continue
declare dirs disown echo enable eval exec exit export false fc fg getopts hash help
history jobs kill let local logout mapfile popd printf pushd pwd read readarray readonly
return set shift shopt source suspend test times trap true type typeset ulimit umask
unalias unset wait
""".split())

# Bash explicitly refers these names to the corresponding builtin's options.
RELATED = {"[": "test", "local": "declare", "readarray": "mapfile", "typeset": "declare"}
# 'help' accepts patterns. The names below come only from BUILTINS, and the
# fixed script passes each name as a quoted argument, never as shell code.
HELP_SCRIPT = 'builtin help -- "$1"'


def focused_topic(topic, label, source):
    """Lead with the selected Bash declaration, keeping the rest of the topic in source order.

    Bash aligns descriptions with tabs or spaces. Join only the indented continuation
    lines belonging to this row. Unrecognized topics keep their original layout.
    """
    if not source.startswith(RELATED.get(topic, topic) + ": "):
        return ""
    lines = source.expandtabs(8).splitlines()
    declaration = re.compile(r"^ {6}" + re.escape(label) + r" +(\S.*)$")
    for index, raw in enumerate(lines[1:], 1):
        match = declaration.fullmatch(raw)
        if not match:
            continue
        end = index + 1
        words = [match[1]]
        while end < len(lines) and lines[end].startswith(" " * 12) and lines[end].strip():
            words.append(lines[end].strip())
            end += 1
        # Skip only the selected row in the reference below. Keep command-wide
        # rules, examples and all neighboring declarations available by scrolling.
        return "\n".join(["Behavior: " + " ".join(words), "Builtin reference:",
                          lines[0].partition(": ")[2], *lines[1:index], *lines[end:]])
    return ""


def builtin_profile(name, text, specification):
    """Build a selectable topic from the installed Bash synopsis and declaration rows.

    The caller supplies only successful output for an allowlisted name and its
    documented synonym. Shell operators and option operands remain literal.
    Optionless topics return their usage through the normal terminal diagnostic.
    """
    usage, _, body = text.partition("\n")
    spec, _, details = specification.partition("\n")
    if not usage.startswith(name + ": ") or not spec.startswith(RELATED.get(name, name) + ": "):
        raise HelpError("Bash returned a different help topic.", "help_source_scope")
    synopsis = usage[len(name) + 2:]
    summary = body.strip().split("\n", 1)[0]
    arguments = dict(re.findall(r'(?<![\w-])(-[A-Za-z@])(?:\|\+o)? ([a-z][\w:-]*)(?=[] |])', spec + " "))
    # These operands are explicit in the help synopsis or the named option row.
    if name == "jobs":
        arguments.pop("-x", None)  # child argv begins here
    options = {}
    for line in details.expandtabs(8).splitlines():
        match = re.match(r'^ {6}(-[A-Za-z@])(?: ([A-Za-z][\w:-]*))?\s{2,}(\S.*)$', line)
        if not match:
            continue
        flag, operand, meaning = match.groups()
        argument = arguments.get(flag) or operand or ""
        options.setdefault(flag, {"flag": flag, "argument": argument, "summary": meaning.strip()})
    # Some topics describe switches only in prose. Expand only literal switches
    # in option groups from the SYNOPSIS, never example lines from the body.
    for group in re.findall(r'(?:\[|\|| )-([A-Za-z@]+)(?=[] |])', spec):
        if group in {"sigspec", "switch"} or group == "N" and name in {"dirs", "popd", "pushd"}:
            continue
        for letter in group:
            flag = "-" + letter
            options.setdefault(flag, {"flag": flag, "argument": arguments.get(flag, ""),
                                      "summary": f"{synopsis}. See help {name} for {flag}."})
    if name in ("test", "["):
        for flag, arg, meaning in re.findall(r'^ {6}(-\w) (\w+)\s{2,}(True .+)$', details, re.M):
            options[flag] = {"flag": flag, "argument": arg, "summary": meaning}
        options["-n"] = {"flag": "-n", "argument": "STRING", "summary": "True if STRING is nonempty."}
    if name in {"dirs", "popd", "pushd"}:
        options.pop("-N", None)  # -N in these synopses stands for a stack index.
    if not options:
        raise HelpError(f"{synopsis} — {summary}  See Bash help for this topic with help '{name}'.", "usage_guidance")
    for option in options.values():
        option["detail"] = specification
        if option["flag"] == "-o" and name == "set":
            option["argument_optional"] = True
    profile = {"command": ["builtin", name], "description": summary,
               "categories": [{"name": "Bash builtin", "description": synopsis, "options": list(options.values())}],
               "stop_at_positional": True}
    if name == "jobs":
        profile["stop_at_options"] = ["-x"]
    return profile
