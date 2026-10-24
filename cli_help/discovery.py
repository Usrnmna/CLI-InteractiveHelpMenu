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
import stat
import subprocess
import tempfile
import time

from core import HelpError, validate_profile
from command_paths import help_route
from invocation import INTERPRETER_FLAGS, PIP_MODULE_COMMANDS


# Limits apply per source. Two sources are queried on an uncached auto lookup.
MAX_OUTPUT_BYTES = 512 * 1024
MAX_CACHE_BYTES = 2 * 1024 * 1024
CACHE_VERSION = 10
FLAG_PATTERN = re.compile(r"(?<![\w=:-])(--?[A-Za-z0-9][A-Za-z0-9_-]*(?::[A-Za-z0-9][A-Za-z0-9_-]*)*)(?=$|[\s,=\[<])")
# These are interpreter switches with no separate values or code operands.
# Module routes are deliberately independent of user-editable driver files.
MODULE_INTERPRETER_OPTIONS = INTERPRETER_FLAGS
PARENTHESIZED_TYPE = r"\((?:string|list|integer|long|double|float|map|blob|timestamp)\)"
ARGUMENT_PATTERN = re.compile(
    r"^(<[^<>]+>|\[[^\[\]]+\][A-Z][A-Z0-9_/-]*|\[[^\[\]]+\]|\{[^{}]+\}|#[0-9]+|"
    + PARENTHESIZED_TYPE + r"|[A-Z][A-Z0-9_-]*(?:=[A-Z][A-Z0-9_-]*)?)(?=$|[\s,])"
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
        super().__init__(f"Help source exited with status {returncode}; check the renderer and documentation availability.",
                         "probe_exit")


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


def run_probe(argv: list[str], timeout: float, max_bytes=MAX_OUTPUT_BYTES, check=False,
              environment_overrides: dict | None = None) -> str:
    """Collect a bounded help response without a shell, stdin, pager, or working files.

    A separate process group permits cleanup of ordinary descendants on timeout,
    cancellation, output overflow, and normal completion. A program that escapes
    that group or ignores --help is outside this containment guarantee.
    """
    with tempfile.TemporaryDirectory(prefix="cli-help-probe-") as directory:
        environment = probe_environment()
        if Path(argv[0]).name == "ansible-playbook":
            # Current Ansible requires UTF-8 even for --help and --version.
            # Keep English output and exclude caller-controlled locale values.
            environment.update({"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"})
        if environment_overrides:
            environment.update(environment_overrides)
        try:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=directory, env=environment,
                                       start_new_session=True)
        except OSError as error:
            raise ProbeError("Cannot start help source; check executable availability and permissions.", "probe_start") from error
        output = bytearray()
        deadline = time.monotonic() + timeout
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise ProbeError(f"Help source timed out after {timeout:g} seconds.", "probe_timeout")
                    for key, _ in selector.select(remaining):
                        chunk = os.read(key.fd, min(65536, max_bytes - len(output) + 1))
                        if not chunk:
                            selector.unregister(key.fileobj)
                            break
                        output.extend(chunk)
                        if len(output) > max_bytes:
                            raise ProbeError(f"Help source exceeded {max_bytes} bytes.", "probe_output_limit")
            try:
                process.wait(timeout=max(0.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired as error:
                raise ProbeError(f"Help source timed out after {timeout:g} seconds.", "probe_timeout") from error
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
    # A compression-level range is not an alias declaration. Preserve literal
    # numeric flags elsewhere. Check before splitting alignment columns so tabs
    # or multiple spaces cannot turn the first endpoint into a partial flag.
    if re.match(r"^-[0-9]\s+(?:\.\.\.|…)\s+-[0-9](?:\s|$)", stripped):
        return None
    columns = re.split(r"\s{2,}|\t+", stripped, maxsplit=1)
    signature = columns[0]
    # systemd presents short/long aliases separated by one space. Restrict
    # normalization to a leading short flag directly followed by a long flag;
    # embedded examples, values, and arbitrary adjacent flags remain prose.
    signature = re.sub(r"^(-[A-Za-z0-9])\s+(?=--[A-Za-z0-9])", r"\1, ", signature)
    # A selector placeholder is not a literal option. In particular, rejecting
    # the whole declaration prevents -c[:stream_specifier] becoming bare -c.
    if re.search(r"--?[A-Za-z0-9][A-Za-z0-9_-]*(?:\[:|:<)", signature):
        return None
    summary = columns[1].strip() if len(columns) == 2 else ""
    # Preset/memory tables contain bare numeric switches followed exclusively
    # by numeric cells. They are data rows, not option declarations.
    if re.fullmatch(r"-[0-9]", signature) and re.fullmatch(
            r"(?:[0-9.]+|[KMGT]?i?B|N/A)(?:\s+(?:[0-9.]+|[KMGT]?i?B|N/A))*", summary):
        return None
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
        if index and not re.search(r"(?:[,|]|\bor)\s*$", signature[matches[index - 1].end():match.start()]):
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
                payload = value.group(1)
                # A quoted example wrapping into prose must not replace a real
                # optional declaration with an inferred required fragment.
                if payload.startswith(("'", '"')) and (len(payload) < 2 or payload[-1] != payload[0]):
                    return None
                flag += "="
                argument = payload
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
            elif ":" in flag and re.fullmatch(r"[a-z][a-z0-9_-]*", tail):
                # FFmpeg's concrete stream-selector declarations use lowercase
                # codec metavariables even without a separate description.
                argument, tail = tail, ""
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

    lines = clean_output(text).splitlines()
    # Manual declarations often place a lowercase metavariable on its own
    # line. A more deeply indented following paragraph distinguishes those
    # declarations from single-column descriptions such as '-h help'.
    next_indents = [0] * len(lines)
    next_indent = 0
    for index in range(len(lines) - 1, -1, -1):
        next_indents[index] = next_indent
        if lines[index].strip():
            next_indent = len(lines[index]) - len(lines[index].lstrip())
    for line_index, raw in enumerate(lines):
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
            if (indentation >= 4 and next_indents[line_index] > indentation
                    and re.fullmatch(r"[a-z][a-z0-9_-]*", summary)
                    and not any(option["argument"] for option in active_options)):
                for option in active_options:
                    option["argument"] = summary
                summary = ""
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
                old_count = previous.get("argument_count", 1) if previous["argument"] else 0
                new_count = entry.get("argument_count", 1) if entry["argument"] else 0
                # Prefer the larger explicit arity. At equal arity, a required
                # declaration takes precedence over an optional one so another
                # flag cannot silently occupy a documented required value.
                old_optional = previous.get("argument_optional", False)
                new_optional = entry.get("argument_optional", False)
                if old_count and new_count and (old_count, old_optional) != (new_count, new_optional):
                    previous["detail"] += ("\n\nArgument declarations disagree across sources; "
                                           "the larger value count, then required values, take precedence.")
                if new_count > old_count or (new_count == old_count and old_optional and not new_optional):
                    previous.update({key: entry[key] for key in ("flag", "argument", "argument_optional")})
                    previous.pop("argument_count", None)
                    if new_count > 1:
                        previous["argument_count"] = new_count
                continue
            by_flag[identity] = entry
    if not by_flag:
        raise HelpError("No recognizable option declarations were found for the selected command.", "help_unparsed")
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


def read_cache_document(path: Path):
    """Read a bounded regular cache file without following links or blocking on FIFOs.

    Nonblocking open plus descriptor validation closes the check/open race for
    special files. The actual byte limit also applies if the file grows after
    its metadata was checked. Cache failures remain misses at the caller.
    """
    if path.is_symlink():
        raise ValueError("Cache entries must be regular files, not symbolic links.")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_CACHE_BYTES:
            raise ValueError("Cache entry is not a size-bounded regular file.")
        output = bytearray()
        while len(output) <= MAX_CACHE_BYTES:
            chunk = os.read(descriptor, min(65536, MAX_CACHE_BYTES + 1 - len(output)))
            if not chunk:
                break
            output.extend(chunk)
        if len(output) > MAX_CACHE_BYTES:
            raise ValueError("Cache entry exceeds its read limit.")
        return json.loads(output.decode("utf-8"))
    finally:
        os.close(descriptor)


def read_cache(path: Path, identity: dict, ttl: int) -> dict | None:
    """Accept only fresh, size-bounded, schema-valid cached profiles for this lookup."""
    try:
        document = read_cache_document(path)
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


def module_help_route(module: str, subcommands: tuple[str, ...], interpreter_options: tuple[str, ...]):
    """Return reviewed module help operands without consulting executable drivers.

    Interpreter flags retain the selected installation's documentation context.
    Only fixed pip help routes and pytest help are allowed; pending operands,
    Python code, module paths, plugin names, and interpreter option values never
    enter a discovery request.
    """
    if any(option not in MODULE_INTERPRETER_OPTIONS for option in interpreter_options):
        raise HelpError("Unsupported Python interpreter option for module help.")
    if module == "pip" and (not subcommands or
                            len(subcommands) == 1 and subcommands[0] in PIP_MODULE_COMMANDS):
        arguments = ("help", *subcommands) if subcommands else ("--help",)
        manual = "-".join((module, *subcommands))
    elif module == "pytest" and not subcommands:
        arguments = ("--help", "--noconftest")
        manual = "pytest"
    else:
        raise HelpError("Unsupported Python module or module command path for help.")
    return [*interpreter_options, "-m", module, *arguments], manual


def module_fingerprint(executable, module, interpreter_options, timeout):
    """Fingerprint fixed module-version output without evaluating Python code.

    This auto-mode request runs before cache reuse. Version and import-location
    changes invalidate pip/pytest documentation under an unchanged interpreter.
    An unverified response disables caching for the request; same-version local
    edits remain subject to TTL or explicit refresh. Raw output is never saved.
    """
    arguments = [executable, *interpreter_options, "-m", module, "--version"]
    overrides = None
    if module == "pytest":
        arguments.append("--noconftest")
        overrides = {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    output = clean_output(run_probe(arguments, timeout, check=True,
                                    environment_overrides=overrides)).strip()
    if not re.match(r"^" + module + r"\s+[0-9]+\.[0-9]+", output):
        raise ProbeError("Module version response was not recognized; cache reuse is disabled.", "module_version_unverified")
    return hashlib.sha256(output.encode("utf-8")).hexdigest()


def cache_identity(command_path, executable, help_arguments, manual_name, manual, settings,
                   module=None, interpreter_options=()):
    """Build filesystem-derived lookup identity without invoking any program."""
    identity = {"version": CACHE_VERSION, "command": list(command_path), "executable": executable_identity(executable),
                "help_arguments": list(help_arguments), "manual_name": manual_name,
                "mode": settings.mode, "manual": executable_identity(manual) if manual else None,
                "manpath": os.environ.get("MANPATH", ""), "timeout": settings.timeout}
    if module is not None:
        identity.update({"module": module, "interpreter_options": list(interpreter_options),
                         "home_identity": hashlib.sha256(os.environ.get("HOME", "").encode()).hexdigest()})
        venv_config = Path(executable).parent.parent / "pyvenv.cfg"
        identity["venv_config"] = executable_identity(str(venv_config)) if venv_config.is_file() else None
    return identity


def verify_command_variant(name: str, executable: str, settings: Settings, subcommands=()) -> str:
    """Identify tools whose names or command spelling differ across products.

    Only fixed version or root help requests are issued. Manual-only mode cannot
    establish executable identity and therefore leaves these routes explicit.
    """
    if settings.mode != "auto":
        raise HelpError(f"The {name} executable variant cannot be identified in manual-only mode; use an explicit reviewed profile.")
    arguments = ["--help"] if name in ("esptool", "esptool.py") else ["--version"]
    output = clean_output(run_probe([executable, *arguments], settings.timeout)).strip()
    if name == "yq":
        if not re.search(r"github\.com/mikefarah/yq", output, re.IGNORECASE) or not re.search(r"version\s+v?4\.", output):
            raise HelpError("The yq eval route requires Mike Farah yq v4; this executable has a different or unverified implementation.")
    elif name == "yarn":
        match = re.fullmatch(r"v?([0-9]+)\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", output)
        if not match or int(match.group(1)) < 1:
            raise HelpError("JavaScript Yarn is required; this executable has a different or unverified implementation (including cmdtest yarn).")
    else:
        match = re.search(r"\besptool(?:\.py)?\s+v?([0-9]+)\.[0-9]+", output, re.IGNORECASE)
        if not match:
            raise HelpError("The esptool version could not be identified from fixed root help.")
        major = int(match.group(1))
        if subcommands and ((subcommands[0] == "write-flash" and major < 5) or
                            (subcommands[0] == "write_flash" and major >= 5)):
            raise HelpError("esptool write-flash requires v5 or newer; write_flash is the explicitly separate legacy route.")
        # Keep identity compact rather than caching the complete root help text.
        output = match.group(0)
    return clean_output(output).strip()


def discover(command: str, settings: Settings, refresh=False, subcommands=(), driver_registry=None,
             module: str | None = None, interpreter_options=()) -> dict:
    """Discover fixed executable or selected-interpreter module documentation.

    Module profiles use their logical module command for insertion and record
    the selected interpreter separately. Editable drivers cannot substitute an
    executable, module, interpreter switch, or module help route.
    """
    if settings.mode == "off":
        raise HelpError("No static profile matches and automatic discovery is disabled.", "discovery_disabled")
    name = Path(command).name
    if not re.fullmatch(r"[A-Za-z0-9_.+][A-Za-z0-9_.+-]*", name) or name in (".", ".."):
        raise HelpError("Discovery requires a literal executable name.")
    if module is not None:
        if name not in ("python", "python3"):
            raise HelpError("Module help requires a selected python or python3 executable.")
        help_arguments, manual_name = module_help_route(module, tuple(subcommands), tuple(interpreter_options))
    else:
        if interpreter_options:
            raise HelpError("Interpreter options require a supported module invocation.")
        try:
            route = help_route(name, tuple(subcommands), driver_registry)
            help_arguments, manual_name = list(route.arguments), route.manual
        except ValueError as error:
            raise HelpError(str(error)) from error
    command_path = [module or name, *subcommands]
    if name == "pytest" and not subcommands and module is None:
        # Fixed help must not load project conftest modules or installed
        # third-party plugins, even when a driver supplies a root route.
        help_arguments = ["--help", "--noconftest"]
    executable = shutil.which(command)
    if not executable:
        raise HelpError("Installed executable not found; check the selected executable and PATH.", "executable_missing")
    executable = os.path.abspath(executable)
    variant = (verify_command_variant(name, executable, settings, subcommands)
               if name in ("yq", "yarn", "esptool", "esptool.py") else None)
    if name == "yarn" and tuple(subcommands) == ("run",) and int(variant.lstrip("v").split(".")[0]) >= 2:
        # Modern Yarn has overload-specific help. Classic Yarn treats this
        # spelling as a script operand, so it is selected only after identity.
        help_arguments = ["run", "-h=1"]
    manual = shutil.which("man")
    manual = os.path.abspath(manual) if manual else None
    identity = cache_identity(command_path, executable, help_arguments, manual_name, manual, settings,
                              module, interpreter_options)
    freshness_warning = None
    cache_verified = True
    if module is not None and settings.mode == "auto":
        try:
            identity["module_fingerprint"] = module_fingerprint(executable, module, interpreter_options, settings.timeout)
        except ProbeError as error:
            # A failed freshness check never licenses reuse of old metadata.
            # Fresh help remains useful when --version is unavailable or slow.
            cache_verified = False
            reason = " timed out" if error.code == "probe_timeout" else " could not be verified"
            freshness_warning = "Module identity" + reason + "; this request bypasses cache reads and writes."
    if variant:
        identity["variant"] = variant
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    cache_path = settings.cache_dir / f"{digest}.json" if settings.cache_dir and settings.cache_ttl and cache_verified else None
    if cache_path and not refresh:
        profile = read_cache(cache_path, identity, settings.cache_ttl)
        if profile is not None:
            return profile
    sources = []
    warnings = []
    if freshness_warning:
        warnings.append(freshness_warning)
    probe_failed = False
    probes = []
    if settings.mode == "auto" and help_arguments:
        probes.append((" ".join([name, *help_arguments]), [executable, *help_arguments]))
    if manual and manual_name and (module is None or settings.mode == "man"):
        probes.append((f"man {manual_name}", [manual, "-P", "/bin/cat", "--no-hyphenation", "--no-justification", "-s", "1:8", "--", manual_name]))
        if module is not None:
            warnings.append("System module manuals do not establish the selected interpreter's installed module version.")
    elif manual_name and module is None:
        warnings.append("The man executable is unavailable.")
    elif module is not None and settings.mode == "man":
        warnings.append("The man executable is unavailable.")
    for label, argv in probes:
        try:
            if (module == "pytest" or name == "pytest") and argv[0] == executable:
                output = run_probe(argv, settings.timeout,
                                   environment_overrides={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
            else:
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
    if module is not None:
        profile["discovery"].update({"module": module, "interpreter_options": list(interpreter_options),
                                    "scope": "python-module"})
    if variant:
        profile["discovery"]["variant"] = variant
    if warnings:
        profile["description"] += " Some help sources were unavailable."
    if cache_path:
        write_cache(cache_path, identity, profile)
    return profile
