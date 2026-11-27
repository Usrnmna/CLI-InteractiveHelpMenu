"""Edition-aware APT routes and dpkg option tables for fixed documentation requests."""

import re

from apt_editions import DESCRIPTIONS, NOBLE, RESOLUTE, VERB_HELP
from drivers import Driver, HelpRoute


def apt_declarations(edition, program):
    """Map each verb to its own flag/arity table. @ denotes pre-command options."""
    tables = {}
    for verbs, flags in edition[program]:
        declarations = {flag.rstrip("="): flag.endswith("=") for flag in flags.split()}
        for positive in ("--install-recommends", "--download", "--upgrade", "--remove"):
            if positive in declarations:
                declarations["--no-" + positive[2:]] = False
        if "-q" in declarations:
            declarations["-qq"] = False
        tables.update((verb, declarations) for verb in verbs.split())
    return tables


def apt_drivers():
    """Register immutable root help requests and unambiguous pre-command option arities."""
    drivers = {}
    for program in RESOLUTE:
        paths, values, flags = {}, set(), set()
        for edition in (NOBLE, RESOLUTE):
            for verb, options in apt_declarations(edition, program).items():
                path = () if verb == "@" else (verb,)
                paths[path] = HelpRoute(("--help",), program, stop_at_positional=True)
                values.update(key for key, required in options.items() if required)
                flags.update(key for key, required in options.items() if not required)
        drivers[program] = Driver(paths, frozenset(values - flags), frozenset(flags - values))
    return drivers


APT_DRIVERS = apt_drivers()
APT_VALUES = {
    "--build-profiles": "PROFILE,...", "--cli-version": "VERSION", "--comment": "TEXT",
    "--config-file": "FILE", "--default-release": "RELEASE", "--error-on": "MODE",
    "--file": "FILE", "--format": "FORMAT", "--host-architecture": "ARCH", "--option": "KEY=VALUE",
    "--pkg-cache": "FILE", "--planner": "PLANNER", "--snapshot": "SNAPSHOT", "--solver": "SOLVER",
    "--src-cache": "FILE", "--target-release": "RELEASE", "--with-source": "FILE",
    "-P": "PROFILE,...", "-S": "SNAPSHOT", "-a": "ARCH", "-c": "FILE", "-e": "MODE",
    "-f": "FILE", "-o": "KEY=VALUE", "-p": "FILE", "-s": "FILE", "-t": "RELEASE",
}

# Both reviewed apt(8) editions refer install to apt-get(8), whose --simulate
# entry documents these spellings. Other APT tools can assign -s a different role.
SIMULATION_FLAGS = frozenset({"-s", "--simulate", "--just-print", "--dry-run", "--recon", "--no-act"})
SIMULATION_DETAIL = (
    "Plan: Preview the operations for the current package state without applying them.\n"
    "Locking: APT disables locks during simulation, so the package state can change during the run.\n"
    "Output: Inst means unpack, Conf means configure, and Remv means remove.\n"
    "Brackets: Square brackets mark broken packages, with [] for rare breaks of no consequence.\n"
    "Permissions: A non-root user can get a different plan if some APT configuration is unreadable.\n"
    "Configuration: APT::Get::Simulate enables simulation. "
    "APT::Get::Show-User-Simulation-Note controls the notice shown by default to non-root users.\n"
    "Source: apt-get(8), --simulate."
)


def apt_document(text, command):
    """Select options by the edition printed in root help or the packaged manual footer."""
    name, *path = command
    match = re.search(r"^apt (\d+\.\d+)\.\d+", text, re.I | re.M)
    if not match or match[1] not in {"2.8", "3.2"}:
        return None
    edition = NOBLE if match[1] == "2.8" else RESOLUTE
    verbs = apt_declarations(edition, name)
    verb = path[0] if path else "@"
    rows = []
    if verb in verbs and len(path) <= 1:
        for flag, required in verbs[verb].items():
            summary = DESCRIPTIONS.get(flag) or f"Set the {flag} option for {' '.join(command)}."
            entry = {"flag": flag, "argument": APT_VALUES[flag] if required else "",
                     "summary": summary, "category": "Options"}
            if name in {"apt", "apt-get"} and "--simulate" in verbs[verb] and flag in SIMULATION_FLAGS and not required:
                entry.update(summary=DESCRIPTIONS["--simulate"], detail=SIMULATION_DETAIL)
            if required and len(flag) == 2:
                entry["attached"] = True
            rows.append(entry)
        if not path:
            for child in sorted(verbs.keys() - {"@"}):
                rows.append({"kind": "keyword", "flag": child, "argument": "", "category": "Commands",
                             "summary": VERB_HELP.get(child, f"Select the {child} operation in {name}.")})
    return {"options": rows, "option_lines": [1] * len(rows), "shared": []}


def dpkg_document(text, name):
    """Read dpkg's Commands and Options tables from fixed --help output.

    Operands precede the aligned prose column and may span multiple words inside
    angle brackets. Alternatives in a command's synopsis are never new aliases.
    """
    if not text.startswith(f"Usage: {name} "):
        return None
    lines = text.splitlines()
    section = None
    options, numbers = [], []
    for index, line in enumerate(lines):
        if line and not line.startswith(" "):
            section = line[:-1] if line in ("Options:", "Commands:") else None
        if not section or not line.lstrip().startswith("-"):
            continue
        # Read only the leading cluster of spellings. -R in the operand
        # alternative of --install belongs to a different dpkg option.
        cluster = re.match(r"(?:--?[^\s,|=<>]+)(?:(?:\||,\s*)--?[^\s,|=<>]+)*", line.lstrip())
        if not cluster:
            continue
        remainder = line.lstrip()[cluster.end():].lstrip()
        if remainder.startswith("<") and "<" in line.lstrip().split()[0] and "=" not in line.lstrip().split()[0]:
            continue  # templated names such as --force-<thing>
        operands = re.match(r"=?((?:\[?<[^>]+>[^\s]*\s*)+)", remainder)
        desc = remainder[operands.end():].strip() if operands else remainder
        if desc.startswith("|"):
            desc = ""
        if not desc and index + 1 < len(lines) and lines[index + 1].startswith(" " * 20):
            desc = lines[index + 1].strip()
        for spelling in re.split(r"\||,\s*", cluster[0]):
            flags = ([spelling.replace("[no-]", ""), spelling.replace("[no-]", "no-")]
                     if "[no-]" in spelling else [spelling])
            for flag in flags:
                if not re.fullmatch(r"--?[A-Za-z0-9][A-Za-z0-9-]*", flag) or flag.endswith("-") or (flag == "--debug" and remainder.startswith("=help")):
                    continue
                if flag == "-Dh":
                    continue
                parts = re.findall(r"<([^>]+)>", operands[0]) if operands else []
                required = re.findall(r"(?<!\[)<([^>]+)>", operands[0]) if operands else []
                entry = {"flag": flag, "summary": desc or line.strip(), "category": section,
                         "detail": line.strip(), "argument": " ".join(required or parts)}
                if required:
                    entry["argument_count"] = len(required)
                elif parts:
                    entry["argument_optional"] = True
                if len(flag) == 2 and parts and section == "Options":
                    entry["attached"] = True
                options.append(entry)
                numbers.append(index + 1)
    return {"options": options, "option_lines": numbers, "shared": []}


def complete_dpkg_manual(parsed, text):
    """Expand parameterized action names and preserve forwarded archive/query operand boundaries."""
    lines = text.splitlines()
    placeholders = {"--assert-feature", "--validate-thing", "--force-things", "--no-force-things",
                    "--refuse-things", "--force-thing"}
    pairs = [(entry, number) for entry, number in zip(parsed["options"], parsed["option_lines"])
             if entry["flag"] not in placeholders]
    forwarded = False
    family = None
    for number, line in enumerate(lines, 1):
        if line and not line[0].isspace():
            forwarded = False
        if re.fullmatch(r" {7}dpkg-(?:deb|query) (?:commands|actions)", line):
            forwarded = True
        if line.startswith("       ") and not line.startswith("        "):
            family = {"--assert-feature": "assert", "--validate-thing string": "validate"}.get(line.strip())
        match = re.fullmatch(r" {11}([a-z]+(?:-[a-z]+)*)", line) if family else None
        if match:
            name = "--" + family + "-" + match[1]
            pairs.append(({"flag": name, "category": "Commands", "summary": lines[number].strip(),
                           "argument": "STRING" if family == "validate" else ""}, number))
        if not forwarded:
            continue
        match = re.fullmatch(r" {11}((?:-[A-Za-z], )?--[a-z-]+) +([a-z-]+(?: +[a-z-]+)?)"
                             r"(?:\.\.\.| +\[.*\])?", line)
        if match:
            for flag in match[1].split(", "):
                pairs = [(entry, n) for entry, n in pairs if entry["flag"] != flag]
                args = match[2].split()
                pairs.append(({"flag": flag, "argument": " ".join(args), "argument_count": len(args),
                               "summary": lines[number].strip(), "category": "Commands"}, number))
    parsed["options"] = [entry for entry, _ in pairs]
    parsed["option_lines"] = [line for _, line in pairs]
