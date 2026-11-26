"""Build offline reference shards from locally rendered, version-labelled Ubuntu manuals.

The source manifest maps invocation names to package, version, page, and a text
file. Input rendering and package acquisition are separate, read-only steps.
Only literal declaration syntax and usage are carried into the installed data.
"""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


ROOT_SECTIONS = {"OPTIONS", "GLOBAL OPTIONS", "GENERAL OPTIONS", "COMMAND LINE OPTIONS",
                 "COMMON OPTIONS", "APPLICATION OPTIONS", "HELP OPTIONS", "COMMAND-LINE OPTIONS", "OPTIONS AND ARGUMENTS", "FLAGS", "SWITCHES"}
FLAG = r"--?[A-Za-z0-9][A-Za-z0-9_-]*(?:[.:][A-Za-z0-9][A-Za-z0-9_-]*)*"
SPELLING = re.compile(FLAG)
VALUE = r"(?:<[^<>\n]+>|[\w/][\w./:|,-]*(?:\.\.\.)?)"
KEYWORDS = {
    "apache2ctl": "start stop restart fullstatus status graceful graceful-stop configtest",
    "apachectl": "start stop restart fullstatus status graceful graceful-stop configtest",
    "usbip": "version help attach detach bind unbind list port",
    "cpupower": "help frequency-info frequency-set idle-info idle-set info set monitor",
    "rtla": "timerlat osnoise", "intel-speed-select": "perf-profile base-freq turbo-freq core-power turbo-mode",
    "zfs": "create destroy snapshot clone list get set mount unmount send receive rollback rename",
    "zpool": "create destroy status list import export scrub clear get set",
    "wg": "show showconf set setconf addconf syncconf genkey genpsk pubkey",
    "wg-quick": "up down save strip", "svn": "add checkout commit diff info log status update",
    "hg": "add clone commit diff log pull push status update", "git-lfs": "track untrack fetch pull push ls-files",
    "direnv": "allow deny edit exec export fetchurl help hook prune reload status stdlib version",
    "nvme": "list list-ctrl list-ns list-subsys id-ctrl id-ns smart-log help",
    "virsh": "list dominfo domstate start shutdown version help",
    "certbot": "run certonly renew certificates plugins delete revoke",
    "rclone": "config copy sync ls lsd check version",
    "borg": "init create list extract check prune info",
    "podman": "build create exec images info inspect logs ps pull push run start stop version",
    "testdisk": "/log /debug /dump /list /version", "photorec": "/log /debug /version",
    "meson": "setup configure compile install test",
    "npm": "install run test", "aptitude": "install remove purge search show update upgrade",
}


SUMMARIES = {
    "smartctl": {"-H": "Show the device health assessment.", "--health": "Show the device health assessment.",
                 "--device": "Select the device or controller type.", "-d": "Select the device or controller type."},
    "sensors": {"-c": "Read the specified sensor configuration file.", "--fahrenheit": "Display temperatures in Fahrenheit."},
    "apache2ctl": {"configtest": "Check the server configuration syntax.", "graceful": "Request a graceful restart."},
    "sshfs": {"-o": "Set a comma-separated list of mount options.", "-p": "Use the specified SSH port."},
    "nginx": {"-t": "Check the configuration syntax and referenced files.", "-c": "Use the specified configuration file."},
    "tree": {"-L": "Limit the displayed directory depth."},
    "turbostat": {"--interval": "Set the interval between measurements in seconds."},
}


def section(text, name):
    """Return the body of one top-level section of a man-db formatted page."""
    match = re.search(r"^" + re.escape(name) + r"\s*$\n(.*?)(?=^\S|\Z)", text, re.M | re.S | re.I)
    return match[1] if match else ""


def declarations(line):
    """Read entire, unambiguous declaration columns. Keep joined and optional forms distinct."""
    column = re.split(r"\s{2,}", re.sub(r",\s+(?=-)", ",", line.strip()), maxsplit=1)[0]
    # Each alias can carry its own operand. A final operand can describe all aliases.
    column = re.split(r"\s+(?=(?:Display|Print|Show|Use|Enable|Disable|Specify|Output|Set|display|print|show)\s)", column, maxsplit=1)[0]
    column = re.sub(r"^-(?:\?|\x2a),\s*(?=--)", "", column)
    column = re.sub(r" \((--[a-zA-Z0-9-]+)\)$", r",\1", column)
    column = re.sub(r"\s+\|\s+(?=-)", ",", column)
    items = re.split(r"(?:,\s*|\s+|\|)(?=--?)", column)
    aliases, shapes = [], {}
    for item in items:
        match = SPELLING.match(item)
        if not match:
            return []
        flag = match[0]
        tail = item[match.end():].rstrip(",")
        if not tail:
            aliases.append(flag)
            continue
        opt = tail.startswith("[") or tail.startswith(" [")
        style = "equals" if tail.startswith(("=", "[=")) else "separate"
        if not tail.startswith((" ", "=", "[", "<")):
            return []
        if tail.startswith("<"):
            style = "attached_only"
        arg = tail.strip()
        if opt:
            if not arg.endswith("]"):
                return []
            arg = arg[1:-1]
        arg = arg.removeprefix("=")
        if not re.fullmatch(VALUE + r"(?: " + VALUE + r"){0,3}", arg):
            return []
        parts = re.findall(VALUE, arg)
        # Several lowercase English words after a switch usually begin the
        # explanation, not a documented fixed tuple of required arguments.
        if len(parts) > 1 and not all(p.startswith("<") or p.isupper() for p in parts):
            return []
        if len(parts) > 1 and (style != "separate" or opt):
            return []
        shape = (" ".join(p.strip("<>") for p in parts), len(parts), opt, style)
        shapes[flag] = shape
        aliases.append(flag)
    if len({s[:3] for s in shapes.values()}) > 1:
        return []
    common = next(iter(shapes.values()), ("", 0, False, ""))
    rows = []
    for flag in aliases:
        arg, count, optional, style = shapes.get(flag, common)
        if len(flag) == 2 and style == "equals":
            style = "separate"
        rows.append((flag, arg, count, optional, style))
    return rows


def manual_record(name, source, body):
    """Extract root declarations at the left edge of option tables and retain the source digest."""
    synopsis = section(body, "SYNOPSIS") or section(body, "SYNTAX")
    signature = next((" ".join(p.split()) for p in synopsis.strip().split("\n\n")
                      if re.match(r"(?:usage:\s*)?(?:/\S*/)?"+ re.escape(name) + r"(?:\s|$)", p.lstrip(), re.I)), "")
    if not signature:
        signature = next((line.strip() for line in synopsis.splitlines()
                          if re.match(r"^\s*(?:usage:\s*)?(?:/[^ ]*/)?"+re.escape(name)+r"(?:\s|$)", line, re.I)), "")
    # Omit prose and lengthy examples. Full use remains available via the named page.
    signature = re.sub(r"^usage:\s*", "", signature, flags=re.I)
    if len(signature) > 420:
        signature = signature[:390].rsplit(" ", 1)[0] + " …"
    if not re.match(r"(?:\$ )?(?:/\S+/)?[\w.+\[-]+(?:\s|$)", signature):
        signature = ""
    options, conflicts = {}, set()
    active = False
    heading = parent_heading = ""
    for line in body.splitlines():
        subheading = re.fullmatch(r" {1,3}[A-Z][A-Z ]+:?", line)
        if line and (not line[0].isspace() or subheading):
            heading = line.strip().upper().rstrip(":")
            if not subheading:
                parent_heading = heading
            active = (parent_heading in ROOT_SECTIONS or heading in ROOT_SECTIONS or heading.startswith("OPTIONS " + name.upper() + " ") or name in {"tree", "eza"} and heading.endswith("OPTIONS")
                      or name == "valgrind" and heading in {"BASIC OPTIONS", "TOOL SELECTION OPTIONS"}
                      or name == "ctest" and heading == "RUN TESTS"
                      or name in {"ninja", "fish", "virsh", "identify", "convert", "mogrify", "compare"} and heading == "DESCRIPTION"
                      or name == "zsh" and heading == "INVOCATION" or heading == "DESCRIPTION" and
                      (source["package"].startswith(("grub-", "grub2-", "gettext")) or source["package"] in {"diffutils",
                                            "coreutils", "coreutils-from-gnu", "coreutils-from-uutils", "gnu-coreutils"}))
        if heading == "DESCRIPTION" and line.strip().casefold() in {
            "the options are as follows:", "options:", "command options:", "command-line options:"}:
            active = True
        if name == "mysql" and line.startswith("       •   --"):
            active = True
            line = "       " + line.strip()[1:].lstrip()
        if name in {"identify", "convert", "mogrify", "compare"} and line.startswith("         -"):
            line = line[2:]
        if name == "virsh":
            line = line.replace("       • -", "       -", 1)
        if name == "fish":
            line = line.replace(" or --", ", --")
        if ((name == "locale" and heading == "DESCRIPTION") or
                (name == "btrfsck" and heading in {"SAFE OR ADVISORY OPTIONS", "DANGEROUS OPTIONS"})):
            active = True
        if name in {"info", "infobrowser", "mbimcli", "zenity"} and re.fullmatch(r"   [A-Za-z][^:]+ [Oo]ptions:", line):
            active = True
            heading = "OPTIONS"
        if heading in ROOT_SECTIONS or parent_heading in ROOT_SECTIONS:
            # man-db pads the declaration column differently for BSD, GNU and
            # hand-authored pages. Restrict parsing to the outer table margin.
            declaration_indent = re.match(r"^ {4,10}-(?=[a-zA-Z0-9-])", line)
            if name == "bpftrace" and line.startswith("   -"):
                declaration_indent = True
        else:
            declaration_indent = re.match(r"^ {7}-", line)
        if not active or not declaration_indent:
            continue
        declaration = re.sub(r"'(\w+)'", r"\1", line) if name.startswith("ansible") else line
        for row in declarations(declaration):
            flag = row[0]
            if flag in options and options[flag] != row:
                conflicts.add(flag)
            options[flag] = row
    # Simple bracket groups are independent root declarations only before the
    # first subcommand or positional operand. Nested and repeated forms stay in usage.
    synopsis_name = name.removesuffix("-bpfcc") if source["package"] == "bpfcc-tools" else name
    if name == "ftp" and source["page"] == "tnftp(1)":
        synopsis_name = "tnftp"
    for line in synopsis.splitlines():
        match = re.match(r"^\s*" + re.escape(synopsis_name) + r"\s+((?:\[[^\[\]\n]+\]\s*)+)", line)
        if not match:
            continue
        for group in re.findall(r"\[([^\[\]]+)\]", match[1]):
            if not re.fullmatch(r"(?:-[A-Za-z0-9]|--[a-z][a-z0-9-]*)(?: [A-Za-z][A-Za-z0-9_-]*)?", group.strip()):
                continue
            for row in declarations(group):
                if row[0] not in conflicts:
                    options.setdefault(row[0], row)
    if name == "turbostat":
        for flag, arg in (("--interval", "SECONDS"), ("--out", "FILE"), ("--cpu", "CPU-SET"),
                          ("--quiet", ""), ("--Summary", ""), ("--show", "COUNTERS"), ("--hide", "COUNTERS")):
            if re.search(r"^ {7}" + re.escape(flag) + r"(?: |$)", body, re.M):
                options[flag] = (flag, arg, int(bool(arg)), False, "separate" if arg else "")
    if name == "x86_energy_perf_policy":
        for short, flag, arg in (("-c", "--cpu", "CPU-LIST"), ("-p", "--pkg", "PKG-LIST"),
                                 ("-a", "--all", "VALUE"), ("-v", "--version", ""),
                                 ("-m", "--hwp-min", "VALUE"), ("-M", "--hwp-max", "VALUE")):
            if f"{short}, {flag} " in body:
                for spelling in (short, flag):
                    options[spelling] = (spelling, arg, int(bool(arg)), False, "separate" if arg else "")
    if name == "cmake":
        for flag, arg in (("-S", "path-to-source"), ("-B", "path-to-build"), ("-G", "generator-name")):
            if f"       {flag} <{arg}>" in body:
                options[flag] = (flag, arg, 1, False, "separate")
    if name == "mysql" and "--password[=password], -p[password]" in body:
        options["--password"] = ("--password", "password", 1, True, "equals")
        options["-p"] = ("-p", "password", 1, True, "attached_only")
    if name == "zsh" and "Take the first argument as a command" in body:
        options["-c"] = ("-c", "COMMAND", 1, False, "separate")
    if name == "expect" and "[ -c cmds ]" in body:
        options["-c"] = ("-c", "COMMAND", 1, False, "separate")
        for letter in "dfinv":
            if f"The -{letter} flag" in body or f"-{letter} causes Expect" in body:
                options["-" + letter] = ("-" + letter, "FILE" if letter == "f" else "",
                                          int(letter == "f"), False, "separate" if letter == "f" else "")
    if name == "qpdf" and "qpdf --help[={topic|--option}]" in body:
        options["--help"] = ("--help", "TOPIC", 1, True, "equals")
    if name == "podman":
        for flag, argument in re.findall(r"^   (--[a-z-]+)=([a-z]+)\s*$", section(body, "GLOBAL OPTIONS"), re.M):
            options[flag] = (flag, argument, 1, False, "equals")
    if name == "inxi":
        for short, long in re.findall(r"^ {7}(-[A-Za-z]) , (--[a-z-]+) *$", body, re.M):
            if long in {"--audio", "--basic", "--battery", "--cpu", "--disk", "--graphics", "--network"}:
                options[short] = (short, "", 0, False, "")
                options[long] = (long, "", 0, False, "")
    if name == "atop" and "atop -G" in synopsis and "atop -B" in synopsis:
        for flag in ("-B", "-G"):
            options[flag] = (flag, "", 0, False, "")
    if name == "nginx" and "-?, -h" in body:
        options["-h"] = ("-h", "", 0, False, "")
    if name == "npx" and "npx --package=foo" in body:
        for flag in ("--package", "-p", "--call", "-c"):
            if flag in body:
                options[flag] = (flag, "PACKAGE" if flag in ("--package", "-p") else "COMMAND",
                                 1, False, "equals" if flag == "--package" else "separate")
    if name == "sshfs" and re.search(r"^       -o opt,\[opt", body, re.M):
        options["-o"] = ("-o", "OPTION[,OPTION...]", 1, False, "separate")
        conflicts.discard("-o")
    if name == "jq":
        for column in re.findall(r"^       (--[\w-]+(?: [^:\n]+)?):$", section(body, "INVOKING JQ"), re.M):
            # jq's manual uses slash-separated aliases and lowercase metavariables.
            for spelling in column.split(" and "):
                parts = spelling.replace(" / ", ",").split()
                if len(parts) > 1:
                    parts[1:] = [p.upper() for p in parts[1:]]
                for row in declarations(" ".join(parts)):
                    options[row[0]] = row
    if name == "appres" and "[-1] [-V]" in synopsis:
        for row in declarations("-1,-V"):
            options[row[0]] = row
    if name in {"ntfs-3g", "lowntfs-3g", "mount.ntfs", "mount.ntfs-3g", "mount.lowntfs-3g"} and "[-o option[,...]]" in synopsis:
        options["-o"] = ("-o", "OPTION[,OPTION...]", 1, False, "separate")
    for flag in conflicts:
        options.pop(flag, None)
    keywords = [k for k in KEYWORDS.get(name, "").split()
                if re.search(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", body)]
    if name in {"gio", "gtk4-builder-tool", "gtk4-image-tool", "gtk4-path-tool", "gtk4-rendernode-tool",
                "udisksctl", "wpctl", "snap", "dconf", "gsettings", "gdbus", "gapplication"}:
        examples = body if name == "snap" else section(body, "COMMANDS") if name == "wpctl" else synopsis
        pattern = (r"^\s*(?:Usage: )?" + re.escape(name) +
                   r" (?:\[OPTIONS\] )?([a-z][a-z0-9-]*)(?:\s|$)")
        keywords = list(dict.fromkeys(re.findall(pattern, examples, re.M)))
    if name in {"btrfs", "aspell", "lvm"}:
        for line in section(body, "COMMANDS").splitlines():
            entry = re.match(r"^       ([a-z][\w-]*)(?=, -| <| {2,}\S|$)", line)
            if entry or (name == "btrfs" and (entry := re.match(r"^       ([a-z][\w-]*) [A-Z]", line))):
                keywords.append(entry[1])
    if name in {"fwupdmgr", "fwupdtool"}:
        keywords = re.findall(r"^       ([a-z][\w-]+): [A-Z]", body, re.M)
    if name == "dpkg-maintscript-helper":
        keywords = re.findall(r"^       ([a-z][\w-]+) ", section(body, "COMMANDS AND PARAMETERS"), re.M)
    if name == "cryptsetup":
        verbs = ("open close status resize refresh reencrypt create luksFormat luksOpen luksSuspend luksResume "
                 "luksAddKey luksRemoveKey luksChangeKey luksConvertKey luksKillSlot erase luksErase luksUUID "
                 "isLuks luksDump luksHeaderBackup luksHeaderRestore luksConvertKey token convert benchmark")
        keywords = [verb for verb in dict.fromkeys(verbs.split()) if re.search(r"^       "+verb+r"(?: |$)", body, re.M)]
    keywords = list(dict.fromkeys(keywords))
    if name in {"gh", "caddy", "git-lfs", "nvme"}:
        # These root manuals name individual commands by their own manual pages.
        # In GitHub CLI, only the top-level command groups belong to the root.
        links = re.findall(r"(?<![\w-])" + re.escape(name) + r"-([a-z][a-z0-9-]+)\([18]\)", body)
        if name == "nvme":
            links = [word for word in links if word in KEYWORDS[name].split()]
        if name == "gh":
            links = [word for word in links if "-" not in word]
        keywords = list(dict.fromkeys([*keywords, *links]))
    summaries = {}
    # Explicitly curated descriptions for the first optional packages and kernel tools.
    for flag, meaning in SUMMARIES.get(name, {}).items():
        if flag in options or flag in keywords:
            summaries[flag] = meaning
    if not signature and not options and not keywords:
        # A multi-call manual may use the upstream spelling in its synopsis.
        # Its NAME description remains available offline on a minimized image.
        purpose = re.split(r"\s+(?:-|—|–)\s+", " ".join(section(body, "NAME").split()), maxsplit=1)
        if len(purpose) == 2 and len(purpose[1]) <= 280:
            signature = f"{name} — {purpose[1]}"
    return {**({"descriptions": summaries} if summaries else {}), "package": source["package"], "version": source["version"], "page": source["page"],
            "sha256": hashlib.sha256(body.encode()).hexdigest(), "usage": signature,
            "options": list(options.values()), "keywords": keywords}


def write_shards(destination, records):
    """Write deterministic JSON Lines grouped by initial character for small, passive lookups."""
    groups = defaultdict(list)
    for name, record in sorted(records.items()):
        shard = name[0].lower() if name[0].isascii() and name[0].isalnum() else "other"
        for variant in record.get("variants", [record]):
            groups[shard].append(json.dumps({"command": name, **variant}, ensure_ascii=False, separators=(",", ":")))
    destination.mkdir(parents=True, exist_ok=True)
    for shard, lines in groups.items():
        (destination / (shard + ".jsonl")).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    sources = json.loads(args.manifest.read_text(encoding="utf-8"))
    records = {}
    for name, value in sources.items():
        variants = []
        for source in value.get("variants", [value]):
            file = args.manifest.parent / source["file"]
            if "declarations" in source:
                # Captures, applet listings, and package location guidance can
                # have separately transcribed and independently checked syntax.
                record = {key: source[key] for key in ("package", "version", "page")}
                record.update(source["declarations"])
                record["sha256"] = hashlib.sha256(file.read_bytes()).hexdigest()
            else:
                record = manual_record(name, source, file.read_text(encoding="utf-8"))
            for key in ("targets", "kernel", "directory", "location_only", "documentation", "snap_revision",
                        "launcher_package", "launcher_version"):
                if key in source:
                    record[key] = source[key]
            variants.append(record)
        records[name] = {"variants": variants}
    write_shards(args.destination, records)


if __name__ == "__main__":
    main()
