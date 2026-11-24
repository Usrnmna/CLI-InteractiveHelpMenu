"""Read option-definition lists in the formatted Git manuals used by discovery."""

import re

# Other Git routes can borrow a different command's manual with an explicit
# resolution scope. Only these routes have verified their *own* page layout.
REVIEWED = frozenset(("commit", "log", "diff", "status", "show", "fetch", "switch"))
DIFF_FORMS = {"--cached": "Compare the index with a commit.", "--staged": "Compare the index with a commit.",
              "--merge-base": "Use the merge base as the comparison's starting point.",
              "--no-index": "Compare two paths on the filesystem."}
# These definition lists share one paragraph across opposite settings.
# Give the highlighted spelling its own effect and keep the original group
# explanation, with its defaults and interactions, in Details.
GROUP_EFFECTS = {
    "--verify": "Enable the pre-commit and commit-msg hooks.",
    "--no-verify": "Bypass the pre-commit and commit-msg hooks.",
    "--no-gpg-sign": "Disable commit signing.",
    "--no-decorate": "Hide ref names next to commits.",
    "--min-parents=": "Show commits with at least this many parents.",
    "--max-parents=": "Show commits with at most this many parents.",
    "--no-min-parents": "Clear the minimum parent count.",
    "--no-max-parents": "Clear the maximum parent count.",
    "--no-column": "Display untracked files without columns.",
    "--no-relative": "Cancel relative diff paths and the subtree restriction.",
}

# Where the manual opens with an example, omitted default or background
# paragraph, the menu needs an action before presenting that context.
DIFF_EFFECTS = {
    "--compact-summary": "Include creation, deletion and mode changes in the diffstat.",
    "--numstat": "Print added and deleted line counts with each path.",
    "--full-index": "Show full before-and-after object names on patch index lines.",
    "--abbrev": "Abbreviate object names while keeping each prefix unique.",
    "-l": "Limit the exhaustive rename and copy search.",
    "--diff-filter=": "Filter changed paths by change type.",
    "--relative": "Restrict output to a subtree and show paths relative to it.",
}
PRETTY_EFFECTS = {
    "--pretty": "Choose how to display commit records.",
    "--format=": "Choose how to display commit records.",
    "--encoding=": "Recode commit messages into the requested character encoding.",
    "--abbrev-commit": "Show a unique prefix of each commit ID.",
    "--expand-tabs": "Expand tabs in displayed commit messages.",
    "--expand-tabs=": "Expand tabs in displayed commit messages.",
}
ROUTE_EFFECTS = {
    "commit": {
        "--reset-author": "Assign authorship of the resulting commit to the committer.",
        "--trailer": "Add a trailer to the commit message.",
        "--allow-empty": "Allow a commit whose tree matches its parent.",
        "-o": "Commit the named paths and leave other staged changes out.",
        "--only": "Commit the named paths and leave other staged changes out.",
        "-v": "Show the staged diff in the commit message template.",
        "--verbose": "Show the staged diff in the commit message template.",
        "--dry-run": "Preview which paths would be committed.",
    },
    "log": {
        **PRETTY_EFFECTS, **DIFF_EFFECTS,
        "--decorate-refs=": "Include matching refs in commit decorations.",
        "--decorate-refs-exclude=": "Exclude matching refs from commit decorations.",
        "--clear-decorations": "Clear earlier decoration filters and include all refs.",
        "--exclude-hidden=": "Exclude refs hidden by the selected Git service.",
        "--single-worktree": "Limit worktree-specific ref selection to the current worktree.",
        "--bisect": "Include the bad bisection revision and exclude the good ones.",
        "--cherry-pick": "Omit patch-equivalent commits across a symmetric difference.",
        "--cherry": "Mark patch-equivalent commits on the right side and omit merges.",
        "--merge": "Show commits touching conflicted paths.",
        "--show-pulls": "Include merges that first brought selected changes into a branch.",
        "--simplify-merges": "Remove redundant merges from the selected full history.",
        "--ancestry-path": "Restrict a revision range to an ancestry path.",
        "--date=": "Choose the display format for human-readable dates.",
        "--show-linear-break": "Separate nonconsecutive branches in flat history output.",
    },
    "diff": DIFF_EFFECTS,
    "show": {**PRETTY_EFFECTS, **DIFF_EFFECTS},
    "status": {"-v": "Include the staged diff.", "--verbose": "Include the staged diff."},
    "fetch": {
        "--deepen=": "Extend history from the current shallow boundary.",
        "--unshallow": "Fetch missing history to remove shallow-repository limits.",
        "--negotiation-tip=": "Restrict the local tips used for negotiation.",
        "--negotiate-only": "Report common ancestors without fetching objects.",
        "--refetch": "Fetch objects again as a fresh clone would.",
        "--refmap=": "Set the refspec used to map explicitly fetched refs.",
        "--tags": "Fetch all remote tags in addition to the selected refs.",
        "-t": "Fetch all remote tags in addition to the selected refs.",
        "--upload-pack": "Choose the upload-pack program on the remote.",
        "--auto-gc": "Run automatic maintenance after the fetch if needed.",
        "--auto-maintenance": "Run automatic maintenance after the fetch if needed.",
    },
    "switch": {
        "--guess": "Create a local branch from a matching remote-tracking branch.",
        "-m": "Use a three-way merge to carry local changes to the new branch.",
        "--merge": "Use a three-way merge to carry local changes to the new branch.",
        "--conflict=": "Choose how merge conflicts are displayed.",
    },
}

def git_declarations(signature):
    """Read each literal separately so inverse flags cannot inherit an operand.

    Only an unqualified short alias can inherit the following long spelling's
    value. Explicit negative shorthand denotes two switches. Git documents
    the numeric shorthand as a placeholder and -L as two shapes of one operand.
    """
    options = []
    for part in re.split(r"(?:,\s+|(?<=\d)\s+)(?=-)", signature):
        if part == "-<number>":
            continue
        match = re.fullmatch(r"(--(?:\[no-\])?[\w-]+|-[A-Za-z0-9])(.*)", part)
        if not match:
            continue
        flag, tail = match.groups()
        value = tail.strip()
        if value and value[0] not in "=<[(:":  # a prose subheading
            continue
        optional = value.startswith("[")
        if value.startswith("="):
            flag += "="
            value = value[1:]
            optional = False
        spellings = [flag]
        if flag.startswith("--[no-]"):
            stem = flag[7:]
            spellings = ["--" + stem, "--no-" + stem]
        for name in spellings:
            options.append({"flag": name, "argument": value, "argument_optional": optional})
    for index, option in enumerate(options[:-1]):
        following = options[index + 1]
        if (len(option["flag"]) == 2 and not option["argument"] and following["flag"].startswith("--")
                and following["argument"]):
            option.update(argument=following["argument"], argument_optional=following["argument_optional"])
    return options


def git_manual_document(lines, source, command):
    """Return a parsed, self-identified formatted page, or None for another format.

    DocBook renders each top-level option term before a deeper definition. Use
    those paragraph boundaries so a patch example or a quoted git-config flag
    cannot become a menu entry. Preserve the term and complete definition.
    """
    if (len(command) != 2 or command[0] != "git" or command[1] not in REVIEWED or not lines or
            not re.match(r"^" + re.escape("-".join(command).upper()) + r"\(1\)\s+Git Manual\s+", lines[0])):
        return None
    entries, positions = [], []
    section = ""
    index = 0
    while index < len(lines):
        start = index
        raw = lines[index]
        index += 1
        if raw and not raw[0].isspace():
            section = raw
            continue
        if section not in ("OPTIONS", "DIFF FORMATTING", "DESCRIPTION"):
            continue
        # Groff's term indent depends on its device and output width. The
        # preceding blank and the indented definition identify the list.
        term = raw.lstrip()
        indent = len(raw) - len(term)
        diff_form = section == "DESCRIPTION" and command[1] == "diff" and term.startswith("git diff ")
        previous = lines[start - 1] if start else ""
        new_paragraph = not previous.strip() or len(previous) - len(previous.lstrip()) < indent
        if ((not diff_form and (section == "DESCRIPTION" or not term.startswith("-")))
                or indent == 0 or not new_paragraph):
            continue
        while (term.endswith(",") and index < len(lines)
               and lines[index].lstrip().startswith("-")):
            term += " " + lines[index].strip()
            index += 1
        body = []
        while index < len(lines):
            line = lines[index]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            body.append(line.strip())
            index += 1
        paragraphs = "\n".join(body).strip()
        if not paragraphs:
            continue
        # A repeated short spelling with two operand syntaxes still inserts a
        # single flag. The unmodified term keeps both forms in the Details pane.
        emitted = set()
        options = git_declarations(term)
        if diff_form:
            # The manual declares these modes in its invocation forms. Each
            # description belongs to that form, including its alias, exit
            # status and path restrictions.
            options = [{"flag": flag, "argument": "", "argument_optional": False}
                       for flag in DIFF_FORMS
                       if flag in term or flag == "--staged" and "--staged is a synonym of --cached" in paragraphs]
        for option in options:
            flag = option["flag"]
            if flag in emitted:
                continue
            emitted.add(flag)
            diff_context = command[1] in ("diff", "log", "show") and flag in ("-U", "--unified=")
            if diff_context:
                # Git's diff option table marks this operand optional even
                # though git-diff(1) prints <n>. Commit's -U has a separate
                # definition that requires an argument.
                option["argument_optional"] = True
            if option["argument_optional"] and len(flag) == 2:
                option["argument_style"] = "attached_only"
            elif option["argument_optional"] and (option["argument"].startswith("[=") or diff_context):
                option["argument_style"] = "equals"
            opening = " ".join(paragraphs.split("\n\n", 1)[0].splitlines())
            lead = DIFF_FORMS[flag] if diff_form else re.split(r"(?<=[.!?])\s+(?=[A-Z])", opening, maxsplit=1)[0]
            if flag.startswith("--no-") and "," in term and not lead.startswith(("Do not", "Disable")):
                lead = "Use the negated form of --" + flag[5:] + "."
            if "," in term:
                lead = GROUP_EFFECTS.get(flag, lead)
            lead = ROUTE_EFFECTS[command[1]].get(flag, lead)
            detail = paragraphs
            if diff_context:
                detail += "\n\nWith no value, use the default patch context. Attach an explicit count, as in -U0 or --unified=0."
            if command[1] == "commit" and flag == "--verify":
                detail = ("A later --verify restores hook checks after -n or --no-verify. "
                          "The manual's shared description refers to the bypass forms:\n" + detail)
            entries.append({**option, "summary": lead, "category": section.title(),
                            "detail": f"{detail}\n\nSyntax: {term}\nSource: {source}"})
            positions.append(start + 1)
    return {"options": entries, "option_lines": positions, "shared": []}
