"""Bounded discovery of literal option definitions from help output and man pages.

Discovery launches fixed help routes or manual lookups, never the pending
action or its arguments. Man-only mode avoids invoking the target executable.
Neither mechanism is an operating-system sandbox for arbitrary programs.
"""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import tempfile
import time

from core import HelpError, validate_profile
from command_paths import help_route


# Limits apply per source. Two sources are queried on an uncached auto lookup.
MAX_OUTPUT_BYTES = 512 * 1024
MAX_CACHE_BYTES = 2 * 1024 * 1024
CACHE_VERSION = 4
FLAG_PATTERN = re.compile(r"(?<![\w-])(--?[A-Za-z0-9][A-Za-z0-9_-]*)(?=$|[\s,=\[<])")
PARENTHESIZED_TYPE = r"\((?:string|list|integer|long|double|float|map|blob|timestamp)\)"
ARGUMENT_PATTERN = re.compile(
    r"^(<[^<>]+>|\[[^\[\]]+\][A-Z][A-Z0-9_-]*|\[[^\[\]]+\]|\{[^{}]+\}|"
    + PARENTHESIZED_TYPE + r"|[A-Z][A-Z0-9_-]*)(?=$|[\s,])"
)
ANSI_PATTERN = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b\[[0-?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class Settings:
    """Expose discovery policy and cache timing without executable configuration."""

    mode: str = "auto"
    timeout: float = 2.0
    cache_ttl: int = 86400
    cache_dir: Path | None = None

    @classmethod
    def from_environment(cls):
        """Validate exported policy values and select the per-user cache directory."""
        mode = os.environ.get("CLI_HELP_DISCOVERY", "auto")
        if mode not in ("auto", "man", "off"):
            raise HelpError("CLI_HELP_DISCOVERY must be auto, man, or off.")
        try:
            timeout = float(os.environ.get("CLI_HELP_DISCOVERY_TIMEOUT", "2"))
            ttl = int(os.environ.get("CLI_HELP_CACHE_TTL", "86400"))
        except ValueError as error:
            raise HelpError("Discovery timeout and cache TTL must be numbers.") from error
        if not 0.05 <= timeout <= 30 or not 0 <= ttl <= 604800:
            raise HelpError("Discovery timeout must be 0.05-30 seconds; cache TTL must be 0-604800 seconds.")
        default = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "cli-interactive-help"
        cache_dir = Path(os.environ.get("CLI_HELP_CACHE_DIR", str(default))).expanduser()
        return cls(mode, timeout, ttl, cache_dir)


class ProbeError(HelpError):
    """A help source exceeded a bound or could not be read."""


class ProbeExitError(ProbeError):
    """A renderer or lookup returned a nonzero exit status when success was required."""

    def __init__(self, returncode: int, output: str):
        self.returncode = returncode
        self.output = output
        super().__init__(f"Help source exited with status {returncode}: {clean_output(output).strip()[:300]}")


def probe_environment() -> dict:
    """Keep executable lookup and manual search paths while excluding shell hooks.

    The pending buffer, shell function exports, pager settings, and startup-file
    variables are not inherited by help processes. English plain text improves
    parsing consistency. HOME remains available for normal program startup.
    """
    environment = {key: os.environ[key] for key in ("PATH", "HOME", "MANPATH") if key in os.environ}
    environment.update({"LC_ALL": "C", "LANG": "C", "TERM": "dumb", "COLUMNS": "100",
                        "MANWIDTH": "100", "PAGER": "/bin/cat", "MANPAGER": "/bin/cat",
                        "MANOPT": "", "GROFF_NO_SGR": "1", "NO_COLOR": "1"})
    return environment


def run_probe(argv: list[str], timeout: float, max_bytes=MAX_OUTPUT_BYTES, check=False) -> str:
    """Collect a bounded help response without a shell, stdin, pager, or working files.

    A separate process group permits cleanup of ordinary descendants on timeout,
    cancellation, output overflow, and normal completion. A program that escapes
    that group or ignores --help is outside this containment guarantee.
    """
    with tempfile.TemporaryDirectory(prefix="cli-help-probe-") as directory:
        try:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=directory, env=probe_environment(),
                                       start_new_session=True)
        except OSError as error:
            raise ProbeError(f"Cannot start help source: {error}") from error
        output = bytearray()
        deadline = time.monotonic() + timeout
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise ProbeError(f"Help source timed out after {timeout:g} seconds.")
                    for key, _ in selector.select(remaining):
                        chunk = os.read(key.fd, min(65536, max_bytes - len(output) + 1))
                        if not chunk:
                            selector.unregister(key.fileobj)
                            break
                        output.extend(chunk)
                        if len(output) > max_bytes:
                            raise ProbeError(f"Help source exceeded {max_bytes} bytes.")
            try:
                process.wait(timeout=max(0.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired as error:
                raise ProbeError(f"Help source timed out after {timeout:g} seconds.") from error
            # Nonzero status is common for --help; manual import and scanning
            # require renderer success to distinguish missing pages from prose.
            decoded = output.decode("utf-8", errors="replace")
            if check and process.returncode:
                raise ProbeExitError(process.returncode, decoded)
            return decoded
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            process.stdout.close()


def clean_output(text: str) -> str:
    """Remove ANSI styling, manual-page overstrikes, and terminal control codes."""
    text = ANSI_PATTERN.sub("", text).replace("\r\n", "\n").replace("\r", "\n")
    # A stack processes long overstrike runs in one pass. Repeated regex
    # substitution can take quadratic time on a bounded but hostile response.
    characters = []
    for char in text:
        if char == "\b":
            if characters and characters[-1] != "\n":
                characters.pop()
        else:
            characters.append(char)
    text = "".join(characters)
    text = text.translate(str.maketrans({"‐": "-", "‑": "-", "−": "-"}))
    return "".join(char for char in text if char.isprintable() or char in "\n\t")


def parse_option_line(line: str) -> tuple[list[dict], str] | None:
    """Recognize option declarations, aliases, and common argument placeholders.

    Only a line beginning with a literal flag is eligible. Descriptions and
    example command lines never become insertion strings. Argument inference is
    deliberately conservative because help text has no universal schema.
    """
    stripped = line.strip()
    if not stripped.startswith("-"):
        return None
    # Git documents a numeric shorthand before literal aliases. The shorthand
    # itself is not insertable, but the explicitly separated aliases are.
    stripped = re.sub(r"^-<[^<>]+>,\s*(?=-)", "", stripped)
    # pnpm's explicit negation shorthand describes two literal boolean flags.
    stripped = re.sub(r"--\[no-\]([A-Za-z0-9][A-Za-z0-9_-]*)(?=$|\s)",
                      r"--\1, --no-\1", stripped)
    # Wget aligns aliases with multiple spaces after the comma; those spaces
    # belong to the declaration rather than the description column.
    stripped = re.sub(r"([,|])\s+(?=--?[A-Za-z0-9])", r"\1 ", stripped)
    columns = re.split(r"\s{2,}|\t+", stripped, maxsplit=1)
    signature = columns[0]
    summary = columns[1].strip() if len(columns) == 2 else ""
    typed_value = re.match("^(" + PARENTHESIZED_TYPE + r")(?=$|\s)", summary)
    if typed_value:
        signature += " " + typed_value.group(1)
        summary = summary[typed_value.end():].strip()
    # kubectl prints defaults followed by a colon on a separate declaration
    # line. Boolean defaults do not make a flag require a following value.
    if not summary and signature.endswith(":") and "=" in signature:
        signature = signature[:-1]
        signature = re.sub(r"=(?:true|false)(?=$|,\s*--?)", "", signature)
    matches = list(FLAG_PATTERN.finditer(signature))
    if not matches or matches[0].start() != 0:
        return None
    options = []
    for index, match in enumerate(matches):
        # Subsequent matches must be part of an alias declaration, not prose.
        if index and not signature[matches[index - 1].end():match.start()].rstrip().endswith((",", "|", "or")):
            break
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(signature)
        raw_tail = signature[match.end():stop]
        # Commas may separate aliases, but joined payloads such as GCC's
        # -Wl,<options> cannot be represented by the literal insertion grammar.
        if raw_tail.startswith(",") and not re.fullmatch(r",\s*", raw_tail):
            return None
        tail = re.sub(r"(?:[,|]|\bor)\s*$", "", raw_tail.strip()).strip()
        flag = match.group(1)
        argument = ""
        optional = False
        argument_count = 1
        if tail.startswith("[=") and "]" in tail:
            argument, _, remainder = tail[2:].partition("]")
            argument = "[=" + argument + "]"
            optional = True
            tail = remainder.strip()
        elif tail.startswith("="):
            value = re.match(r"=([^\s,]+)", tail)
            if value:
                flag += "="
                argument = value.group(1)
                tail = tail[value.end():].strip()
        else:
            # jq consumes both a variable name and a value/file. Treat only
            # explicit paired metavariables as two values, not multiword prose.
            pair = re.match(r"(?:name|NAME|<name>)\s+(?:value|VALUE|<value>|file|FILE|<file>)(?=$|\s)", tail)
            value = ARGUMENT_PATTERN.match(tail)
            if pair:
                argument, tail, argument_count = pair.group(), tail[pair.end():].strip(), 2
            elif re.fullmatch(r"'[^'\n]+'|\"[^\"\n]+\"", tail):
                # Terraform documents -var with a quoted key=value example.
                argument, tail = tail, ""
            elif value:
                argument = value.group(1)
                optional = argument.startswith("[") and argument.endswith("]")
                tail = tail[value.end():].strip()
            elif summary and re.fullmatch(r"[a-z][A-Za-z0-9_\[\],:=./ -]*", tail):
                # A separate declaration column can contain lowercase types,
                # multiword FFmpeg placeholders, or structured metadata syntax.
                argument, tail = tail, ""
        if tail and index == len(matches) - 1 and not summary:
            summary = tail
        option = {"flag": flag, "argument": argument, "argument_optional": optional}
        if argument_count != 1:
            option["argument_count"] = argument_count
        options.append(option)
    # Shared argument syntax usually appears only after the last alias.
    argument_owner = next((option for option in reversed(options) if option["argument"]), None)
    if argument_owner:
        for option in options:
            if not option["argument"]:
                option["argument"] = argument_owner["argument"]
                option["argument_optional"] = argument_owner["argument_optional"]
                if "argument_count" in argument_owner:
                    option["argument_count"] = argument_owner["argument_count"]
    return options, summary


def parse_help(text: str, source: str) -> list[dict]:
    """Extract categories and multiline descriptions from formatted help text."""
    entries = []
    heading = "Options"
    active_options = []
    active_heading = heading
    description = []
    skip_section = False

    def finish():
        if not active_options:
            return
        paragraphs = "\n".join(description).strip()
        summary = next((line for line in description if line), "Documented option")
        for option in active_options:
            entries.append({**option, "summary": summary, "detail": paragraphs + f"\nSource: {source}",
                            "category": active_heading})

    for raw in clean_output(text).splitlines():
        line = raw.strip()
        indentation = len(raw) - len(raw.lstrip())
        is_heading = bool(line) and indentation <= 3 and len(line) <= 72 and not line.startswith("-") and (
            line.endswith(":") or line.isupper() and any(char.isalpha() for char in line)
        )
        if is_heading:
            finish()
            active_options = []
            description = []
            heading = line.rstrip(":").strip().title()
            skip_section = heading.lower() in ("example", "examples", "usage", "synopsis", "see also")
            continue
        if skip_section:
            continue
        parsed = parse_option_line(raw)
        if parsed is None and heading.lower().endswith("options"):
            parsed = parse_bracketed_options(line)
        if parsed:
            finish()
            active_options, summary = parsed
            active_heading = heading
            description = [summary] if summary else []
        elif active_options:
            description.append(line)
    finish()
    return entries


def parse_bracketed_options(line: str) -> tuple[list[dict], str] | None:
    """Read npm-style bracketed option groups inside an explicit options section.

    Only flags, pipe-separated aliases, angle-bracket values, repetition dots,
    and balanced square brackets are permitted. Outer brackets mark optional
    options, not optional values; a selected option may still require a value.
    """
    if not line.startswith("[") or not line.endswith("]"):
        return None
    pattern = re.compile(r"(--?[A-Za-z0-9][A-Za-z0-9_-]*(?:\|--?[A-Za-z0-9][A-Za-z0-9_-]*)*)(?:[ \t]+(<[^<>\n]+>))?")
    matches = list(pattern.finditer(line))
    remainder = pattern.sub("", line)
    if not matches or not re.fullmatch(r"[\[\]. \t]*", remainder):
        return None
    depth = 0
    for char in remainder:
        depth += (char == "[") - (char == "]")
        if depth < 0:
            return None
    if depth:
        return None
    options = []
    for match in matches:
        for flag in match.group(1).split("|"):
            options.append({"flag": flag, "argument": match.group(2) or "", "argument_optional": False})
    return options, ""


def build_profile(command: str | list[str], sources: list[tuple[str, str]]) -> dict:
    """Merge help and manual definitions, preserving richer manual descriptions."""
    command = [command] if isinstance(command, str) else command
    display_name = " ".join(command)
    by_flag = {}
    for source, text in sources:
        for entry in parse_help(text, source):
            identity = entry["flag"].rstrip("=")
            if identity in by_flag:
                previous = by_flag[identity]
                previous["detail"] += "\n\n" + entry["detail"]
                if not previous["argument"] and entry["argument"]:
                    previous.update({key: entry[key] for key in ("flag", "argument", "argument_optional")})
                    if "argument_count" in entry:
                        previous["argument_count"] = entry["argument_count"]
                continue
            by_flag[identity] = entry
    if not by_flag:
        raise HelpError(f"No recognizable option declarations were found for {command!r}.")
    categories = {}
    for entry in by_flag.values():
        category = entry.pop("category")
        categories.setdefault(category, []).append(entry)
    profile = {"command": command, "description": f"Discovered help for {display_name}; arguments and categories are inferred.",
               "categories": [{"name": name, "description": "Automatically extracted command documentation.", "options": options}
                              for name, options in categories.items()]}
    validate_profile(profile, Path("<discovered help>"))
    return profile


def executable_identity(path: str) -> dict:
    """Identify the selected executable and its target without changing argv[0]."""
    stat = os.stat(path)
    return {"path": path, "target": os.path.realpath(path), "mtime_ns": stat.st_mtime_ns,
            "size": stat.st_size, "inode": stat.st_ino, "device": stat.st_dev}


def read_cache(path: Path, identity: dict, ttl: int) -> dict | None:
    """Accept only fresh, size-bounded, schema-valid cached profiles for this lookup."""
    try:
        if path.stat().st_size > MAX_CACHE_BYTES:
            return None
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("identity") != identity:
            return None
        age = time.time() - document["created"]
        if not 0 <= age < ttl:
            return None
        profile = document["profile"]
        validate_profile(profile, path)
        if profile["command"] != identity["command"]:
            return None
        return profile
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        return None


def write_cache(path: Path, identity: dict, profile: dict):
    """Atomically store a profile; unavailable cache storage does not block browsing."""
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        document = json.dumps({"identity": identity, "created": time.time(), "profile": profile}, ensure_ascii=False)
        if len(document.encode("utf-8")) > MAX_CACHE_BYTES:
            return
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(document)
        os.replace(temporary, path)
    except OSError:
        pass
    finally:
        if temporary:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def discover(command: str, settings: Settings, refresh=False, subcommands=(), driver_registry=None) -> dict:
    """Discover a recognized command path using fixed routes without pending args."""
    if settings.mode == "off":
        raise HelpError("No static profile matches and automatic discovery is disabled.")
    name = Path(command).name
    if not re.fullmatch(r"[A-Za-z0-9_.+][A-Za-z0-9_.+-]*", name) or name in (".", ".."):
        raise HelpError("Discovery requires a literal executable name.")
    try:
        route = help_route(name, tuple(subcommands), driver_registry)
        help_arguments, manual_name = list(route.arguments), route.manual
    except ValueError as error:
        raise HelpError(str(error)) from error
    command_path = [name, *subcommands]
    executable = shutil.which(command)
    if not executable:
        raise HelpError(f"Installed executable not found: {command!r}")
    executable = os.path.abspath(executable)
    manual = shutil.which("man")
    manual = os.path.abspath(manual) if manual else None
    identity = {"version": CACHE_VERSION, "command": command_path, "executable": executable_identity(executable),
                "help_arguments": help_arguments, "manual_name": manual_name,
                "mode": settings.mode, "manual": executable_identity(manual) if manual else None,
                "manpath": os.environ.get("MANPATH", ""), "timeout": settings.timeout}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    cache_path = settings.cache_dir / f"{digest}.json" if settings.cache_dir and settings.cache_ttl else None
    if cache_path and not refresh:
        profile = read_cache(cache_path, identity, settings.cache_ttl)
        if profile is not None:
            return profile
    sources = []
    warnings = []
    probe_failed = False
    probes = []
    if settings.mode == "auto" and help_arguments:
        probes.append((" ".join([name, *help_arguments]), [executable, *help_arguments]))
    if manual and manual_name:
        probes.append((f"man {manual_name}", [manual, "-P", "/bin/cat", "--no-hyphenation", "--no-justification", "-s", "1:8", "--", manual_name]))
    elif manual_name:
        warnings.append("The man executable is unavailable.")
    for label, argv in probes:
        try:
            output = run_probe(argv, settings.timeout)
            if parse_help(output, label):
                sources.append((label, output))
            else:
                warnings.append(f"No option declarations were parsed from {label}.")
        except ProbeError as error:
            probe_failed = True
            warnings.append(f"{label}: {error}")
    try:
        profile = build_profile(command_path, sources)
    except HelpError as error:
        explanation = " ".join(warnings)
        error_type = ProbeError if probe_failed else HelpError
        raise error_type(f"{error} {explanation} Add a custom profile for this command.") from error
    profile["discovery"] = {"sources": [label for label, _ in sources], "warnings": warnings,
                            "executable": executable, "scope": "subcommand" if subcommands else "top-level"}
    if warnings:
        profile["description"] += " Some help sources were unavailable."
    if cache_path:
        write_cache(cache_path, identity, profile)
    return profile
