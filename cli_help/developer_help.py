"""Read declarations in self-identifying developer command documentation."""

import re

from compiler_help import compiler_help_document
from git_manual import git_declarations, git_manual_document


# A formatted stash/worktree page describes multiple commands in one OPTIONS
# list. These owners come from the commands' shared option documentation.
WORKTREE_OWNERS = {
    "-f": ("add", "move", "remove"),
    "-b": ("add",),
    "-d": ("add",),
    "--[no-]checkout": ("add",),
    "--[no-]guess-remote": ("add",),
    "--[no-]track": ("add",),
    "--[no-]relative-paths": ("add", "move", "repair"),
    "--lock": ("add",),
    "-n": ("prune",),
    "--orphan": ("add",),
    "--porcelain": ("list",),
    "-z": ("list",),
    "-q": ("add",),
    "-v": ("list", "prune"),
    "--expire": ("list", "prune"),
    "--reason": ("add", "lock"),
}
# These delegated log/diff switches require a history walk, different inputs
# or working-index entries. Stash list fixes reflog traversal and stash show
# supplies the comparison endpoints. See docs/git-stash-*-inventory.md.
STASH_LOG_INAPPLICABLE = set(
    """
    --source -L --remove-empty --exclude-first-parent-only --not --bisect --cherry-mark
    --cherry-pick --left-only --right-only --cherry --merge --simplify-by-decoration
    --show-pulls --full-history --simplify-merges --ancestry-path --date-order
    --author-date-order --topo-order --reverse --no-walk --do-walk --children --graph
    --graph-lane-limit --graph-indent --no-graph-indent --maximal-only
    --ita-invisible-in-index --ita-visible-in-index
""".split()
)
STASH_DIFF_INAPPLICABLE = set(
    """
    --cached --staged --merge-base --no-index --ours --theirs --base -0 -1 -2 -3
    --ita-visible-in-index --ita-invisible-in-index
""".split()
)


def _entry(flag, argument, syntax, body, source, category="Options", **fields):
    """Keep the original term and all its paragraphs when shortening the visible summary."""
    opening = " ".join(body.split("\n\n", 1)[0].split())
    summary = re.split(r"(?<=[.!?])\s+(?=[A-Z])", opening, maxsplit=1)[0]
    return {
        "flag": flag,
        "argument": argument,
        "summary": summary or syntax,
        "detail": f"{body}\n\nSyntax: {syntax}\nSource: {source}",
        "category": category,
        **fields,
    }


def _go_document(text, source, command):
    """Read tab-indented option tables and the named command's own bracketed synopsis."""
    lines = text.splitlines()
    if not lines or not lines[0].startswith("usage: " + " ".join(command) + " "):
        return None
    options, positions = [], []
    for i, line in enumerate(lines):
        declaration = re.fullmatch(r"\t(-[A-Za-z][\w-]*)(?: (.+))?", line)
        if not declaration:
            continue
        flag, value = declaration.groups()
        body = []
        for continuation in lines[i + 1 :]:
            if continuation and not re.match(r"^\t(?:\t| {2,})", continuation):
                break
            body.append(continuation.strip())
        body = "\n".join(body).strip()
        if body:
            fields = {}
            if flag == "-buildvcs" and "-buildvcs=false" in body:
                value = "[=auto|true|false]"
                fields.update(argument_optional=True, argument_style="equals")
            options.append(_entry(flag, value or "", line.strip(), body, source, **fields))
            positions.append(i + 1)
    for bracket in re.finditer(r"\[(-[\w-]+)(?:(=| )([^\]]+))?\]", lines[0]):
        flag, separator, value = bracket.groups()
        body = next(
            (
                paragraph
                for paragraph in text.split("\n\n")
                if re.search(r"^(?:The |If the )" + re.escape(flag) + r" flag\b", paragraph, re.M)
            ),
            "",
        )
        if body:
            if flag == "-exec":
                # The next paragraph gives the actual invocation and its argv.
                body = body[body.index("If the -exec flag") :]
            options.append(
                _entry(flag + ("=" if separator == "=" else ""), value or "", bracket.group(), body, source)
            )
            positions.append(1)
    return {"options": options, "option_lines": positions, "shared": []}


def _git_blocks(lines, heading):
    """Yield literal DocBook terms and their indented definitions in one named section."""
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return
    stop = next((i for i in range(start, len(lines)) if lines[i] and not lines[i][0].isspace()), len(lines))
    terms = [i for i in range(start, stop) if lines[i].strip()]
    if not terms:
        return
    indent = len(lines[terms[0]]) - len(lines[terms[0]].lstrip())
    i = start
    while i < stop:
        raw = lines[i]
        if not raw.strip() or len(raw) - len(raw.lstrip()) != indent:
            i += 1
            continue
        first = i
        term = [raw.strip()]
        i += 1
        while i < stop and lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) == indent:
            term.append(lines[i].strip())
            i += 1
        body = []
        while i < stop and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
            body.append(lines[i].strip())
            i += 1
        if any(body):
            yield first + 1, " ".join(term), "\n".join(body).strip()


def _git_family(text, source, command, scope):
    """Scope shared stash and worktree definitions to the selected path and its fixed manual."""
    if len(command) not in (2, 3) or command[1] not in ("stash", "worktree"):
        return None
    family = command[1]
    leaf = command[2] if len(command) == 3 else ""
    lines = text.splitlines()
    if family == "stash" and leaf in ("list", "show"):
        if leaf == "list" and scope != "stash_reflog":
            return None
        owner = "log" if leaf == "list" else "diff"
        result = git_manual_document(lines, source, ["git", owner])
        if result is None:
            return None
        excluded = STASH_LOG_INAPPLICABLE if leaf == "list" else STASH_DIFF_INAPPLICABLE
        rejected = {
            n
            for o, n in zip(result["options"], result["option_lines"])
            if o["flag"].rstrip("=") in excluded
        }
        for n in sorted(rejected):
            end = n
            while end < len(lines) and (
                not lines[end].strip()
                or len(lines[end]) - len(lines[end].lstrip())
                > len(lines[n - 1]) - len(lines[n - 1].lstrip())
            ):
                end += 1
            result["shared"].append(
                {
                    "source": source,
                    "line": n,
                    "section": "Source-specific options: " + owner + " (Options)",
                    "association": "unassigned",
                    "options": [],
                    "text": "\n".join(lines[n - 1 : end]).strip(),
                }
            )
        selected = [
            (o, n)
            for o, n in zip(result["options"], result["option_lines"])
            if o["flag"].rstrip("=") not in excluded
        ]
        result.update(options=[o for o, n in selected], option_lines=[n for o, n in selected])
        return result
    if not lines or not re.match(r"^GIT-" + family.upper() + r"\(1\)\s+Git Manual\s+", lines[0]):
        return None
    if family == "stash" and leaf not in ("", "push", "pop", "apply"):
        return None
    command_blocks = list(_git_blocks(lines, "COMMANDS"))
    owner = leaf or ("push" if family == "stash" else "")
    options, positions = [], []
    syntax = ""
    for n, term, body in command_blocks:
        word = term.split()[0]
        if not re.fullmatch("[a-z][a-z-]*", word):
            continue
        if not leaf:
            options.append(_entry(word, "", term, body, source, "Commands", kind="keyword"))
            positions.append(n)
        if word == owner:
            syntax = term
            if family == "stash" and "--message" in term:
                for flag in ("-m", "--message"):
                    options.append(
                        _entry(flag, "<message>", term, "Name the new stash entry.\n\n" + body, source)
                    )
                    positions.append(n)
    if not owner:
        return {"options": options, "option_lines": positions, "shared": []}
    for n, term, body in _git_blocks(lines, "OPTIONS"):
        if not term.startswith("-") or term == "--":
            continue
        main = re.split(r"[, =]", term, maxsplit=1)[0]
        if family == "worktree":
            if owner not in WORKTREE_OWNERS.get(main, ()):
                continue
        elif not any(
            re.search(r"(?<![\w-])" + re.escape(o["flag"].rstrip("=")) + r"(?![\w-])", syntax)
            for o in git_declarations(term)
        ):
            continue
        for option in git_declarations(term):
            flag = option["flag"]
            # In a shared signature the prose may open with an applicability
            # note, and a later paragraph can describe a different command.
            paragraphs = body.split("\n\n")
            applicable = [s for s in paragraphs if not s.startswith("This option is only valid")]
            first = next((s for s in applicable if re.search(r"\b" + re.escape(owner) + r"\b", s)), None)
            lead = first or (applicable or paragraphs)[0]
            intro = " ".join(lead.split())
            if flag.startswith("--no-") and flag not in intro:
                intro = "Disable " + flag[5:].replace("-", " ") + "."
            effect = re.split(r"(?<=[.!?])\s+(?=[A-Z])", intro, maxsplit=1)[0]
            entry = _entry(flag, option["argument"], term, body, source)
            entry.update(summary=effect, argument_optional=option["argument_optional"])
            options.append(entry)
            positions.append(n)
    return {"options": options, "option_lines": positions, "shared": []}


def developer_help_document(text, source, command, parse_generic=None, scope=None):
    """Return a path-specific parsed document for a recognized help layout, or None."""
    if command in (["cmake"], ["clang"]):
        return compiler_help_document(text, source, command)
    if (
        command
        and command[0] == "go"
        and tuple(command[1:]) in {("build",), ("test",), ("run",), ("mod", "tidy")}
    ):
        return _go_document(text, source, command)
    if command and command[0] == "git":
        return _git_family(text, source, command, scope)
    if not parse_generic:
        return None
    if command == ["ninja"] and (text.startswith("usage: ninja [options]") or text.startswith("NINJA(1)")):
        result = parse_generic(text, source)
        if re.search(r"(?m)^\s*-t TOOL\b", text) and "further flags are passed to the tool" in text:
            result["stop_at_options"] = ["-t"]
            for option in result["options"]:
                if option["flag"] == "-t":
                    option["argument_style"] = "attached"
        return result
    if command == ["gcc"] and text.startswith("Usage: gcc [options] file..."):
        result = parse_generic(text, source)
        for option in result["options"]:
            signature = re.search(r"(?m)^  (--help=\{[^\n]+)", text)
            if option["flag"] == "--help" and signature:
                option.update(argument="[=CLASS[,...]]", argument_optional=True)
                option["detail"] += (
                    "\n\nChoose option classes with " + signature[1].strip().rstrip(".") + "."
                )
            if (
                option["flag"].rstrip("=") == "-save-temps"
                and "  -save-temps " in text
                and "  -save-temps=" in text
            ):
                option.update(flag="-save-temps", argument="[=arg]", argument_optional=True)
                option["detail"] += (
                    "\n\nUse -save-temps alone, or attach the location with -save-temps=arg."
                )
        return result
    if command == ["bun", "run"] and text.startswith("Usage: bun run [flags]"):
        parsed = parse_generic(text, source)
        for option in parsed["options"]:
            name = option["flag"].rstrip("=")
            if name in {"--inspect", "--inspect-brk", "--inspect-wait", "--config", "-c"}:
                # Bun prints <val> for these optional parser inputs too. A
                # space before the script must not turn its path into a value.
                option.update(flag=name, argument_optional=True, argument_style="equals")
                option["detail"] += (
                    "\n\nUse the bare flag for the default, or attach an explicit value with =."
                )
        return parsed
    if command[0] == "dotnet" and "Usage:" in text and "  " + " ".join(command) + " " in text:
        result = parse_generic(text, source)
        for n, line in enumerate(text.splitlines(), 1):
            match = re.fullmatch(r"  (-\?, -h, --help)\s{2,}(.+)", line)
            if match:
                for flag in ("-h", "--help"):
                    result["options"].append(_entry(flag, "", *match.groups(), source))
                    result["option_lines"].append(n)
        return result
    return None
