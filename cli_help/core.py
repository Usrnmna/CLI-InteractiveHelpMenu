"""Validate help definitions and calculate edits without evaluating shell text."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shlex

from command_paths import load_driver_registry, resolve_path


class HelpError(ValueError):
    """A configuration or command context cannot be handled safely."""


@dataclass(frozen=True)
class Token:
    start: int
    end: int
    value: str


@dataclass(frozen=True)
class Context:
    line: str
    point: int
    start: int
    end: int
    query: str
    profile: dict


def read_json(path: Path):
    """Read a UTF-8 JSON document and report actionable configuration failures."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise HelpError(f"Cannot read {path}: {error}") from error


def require_text(value, label: str, allow_empty=False):
    """Require display text without terminal control characters."""
    if not isinstance(value, str) or (not value and not allow_empty):
        raise HelpError(f"{label} must be a nonempty string.")
    if any(not char.isprintable() and char not in "\n\t" for char in value):
        raise HelpError(f"{label} contains a control character.")


def validate_profile(profile: dict, source: Path):
    """Validate the editable profile schema and restrict insertion to literal flags."""
    if not isinstance(profile, dict):
        raise HelpError(f"{source}: a profile must be an object.")
    command = profile.get("command")
    if not isinstance(command, list) or not command or any(
        not isinstance(word, str) or not re.fullmatch(r"[A-Za-z0-9_.+-]+", word)
        for word in command
    ):
        raise HelpError(f"{source}: command must contain literal command words.")
    require_text(profile.get("description"), f"{source}: description")
    categories = profile.get("categories")
    if not isinstance(categories, list) or not categories:
        raise HelpError(f"{source}: categories must be a nonempty list.")
    category_names = set()
    flags = set()
    for category in categories:
        if not isinstance(category, dict):
            raise HelpError(f"{source}: each category must be an object.")
        require_text(category.get("name"), "Category name")
        require_text(category.get("description", ""), "Category description", True)
        if category["name"] in category_names:
            raise HelpError(f"{source}: duplicate category name.")
        category_names.add(category["name"])
        options = category.get("options")
        if not isinstance(options, list) or not options:
            raise HelpError(f"{source}: each category requires options.")
        for option in options:
            if not isinstance(option, dict):
                raise HelpError(f"{source}: each option must be an object.")
            flag = option.get("flag")
            if not isinstance(flag, str) or not re.fullmatch(r"--?[A-Za-z0-9][A-Za-z0-9_-]*=?", flag):
                raise HelpError(f"{source}: invalid literal option flag: {flag!r}")
            if flag in flags:
                raise HelpError(f"{source}: duplicate option flag: {flag}")
            flags.add(flag)
            require_text(option.get("summary"), "Option summary")
            require_text(option.get("detail", ""), "Option detail", True)
            require_text(option.get("argument", ""), "Option argument", True)
            if not isinstance(option.get("argument_optional", False), bool):
                raise HelpError("argument_optional must be a boolean.")


def load_profiles(bundled: Path, custom: Path | None = None) -> list[dict]:
    """Load bundled profiles, then replace matching command paths with custom files."""
    profiles = {}
    for directory in (bundled, custom):
        if directory is None:
            continue
        if not directory.is_dir():
            raise HelpError(f"Profile directory does not exist: {directory}")
        seen = set()
        for path in sorted(directory.glob("*.json")):
            profile = read_json(path)
            validate_profile(profile, path)
            command = tuple(profile["command"])
            if command in seen:
                raise HelpError(f"Duplicate command profile in {directory}: {' '.join(command)}")
            seen.add(command)
            profiles[command] = profile
    return list(profiles.values())


def tokenize(line: str) -> list[Token]:
    """Locate literal shell words without expansion or execution.

    This prototype accepts a single simple command with balanced quotes and
    escapes. Compound commands, substitutions, and multiline input fail closed.
    """
    if any(char in line for char in "\n\r\x00"):
        raise HelpError("Only single-line simple commands are supported.")
    tokens = []
    index = 0
    while index < len(line):
        if line[index] in " \t":
            index += 1
            continue
        start = index
        quote = None
        while index < len(line):
            char = line[index]
            if quote != "'" and char == "\\":
                index += 2
                if index > len(line):
                    raise HelpError("Complete the trailing escape before opening help.")
                continue
            if char == quote:
                quote = None
            elif quote is None and char in "\"'":
                quote = char
            elif quote is None and char in " \t":
                break
            elif quote != "'" and char in "$`":
                raise HelpError("Shell expansions are not supported in this prototype.")
            elif quote is None and char in "|&;<>()":
                raise HelpError("Pipelines, redirects, and compound commands are not supported.")
            index += 1
        if quote:
            raise HelpError("Close the quoted argument before opening help.")
        raw = line[start:index]
        if raw.startswith("#"):
            raise HelpError("Help is unavailable inside shell comments.")
        try:
            value = shlex.split(raw, posix=True)[0]
        except (ValueError, IndexError) as error:
            raise HelpError("The command contains an unsupported shell word.") from error
        tokens.append(Token(start, index, value))
    return tokens


def find_context(line: str, point: int, profiles: list[dict], discover=None, driver_registry=None) -> Context:
    """Resolve the longest literal command profile and the editable option span.

    Bash's bind -x interface exposes character offsets in a UTF-8 locale,
    rather than the byte offsets used internally by the Readline library.
    """
    if not 0 <= point <= len(line):
        raise HelpError("The cursor offset is outside the command line.")
    try:
        line.encode("utf-8")
    except UnicodeError as error:
        raise HelpError("The command line must contain valid UTF-8 text.") from error
    tokens = tokenize(line)
    if not tokens:
        raise HelpError("Type a supported command followed by a space first.")
    # Validate the editable position before permitting any discovery subprocess.
    if point <= tokens[0].end:
        raise HelpError("Move the cursor after the command or subcommand and a space.")
    active = next((token for token in tokens if token.start <= point <= token.end), None)
    start, end = (active.start, active.end) if active else (point, point)
    query = active.value if active else ""
    if active and (not query.startswith("-") or "=" in query):
        raise HelpError("Move the cursor to an empty argument or an option name.")
    words = [token.value for token in tokens if token.end <= start]
    words[0] = Path(words[0]).name
    driver_registry = load_driver_registry() if driver_registry is None else driver_registry
    try:
        path = resolve_path(words, [tuple(profile["command"]) for profile in profiles], driver_registry)
    except ValueError as error:
        raise HelpError(str(error)) from error
    matches = [profile for profile in profiles if tuple(profile["command"]) == path.words]
    if not matches and discover is not None:
        # Only the executable and a recognized documentation path cross this
        # boundary. Pending global options, values, and action arguments do not.
        matches = [discover(tokens[0].value, subcommands=path.words[1:]) if len(path.words) > 1
                   else discover(tokens[0].value)]
    if not matches:
        raise HelpError(f"No help profile for {words[0]!r}. Use --list-commands to list profiles.")
    profile = max(matches, key=lambda item: len(item["command"]))
    command_end = tokens[path.argument_start - 1].end
    if point <= command_end:
        raise HelpError("Move the cursor after the command or subcommand and a space.")
    previous = [token.value for token in tokens[path.argument_start:] if token.end <= start]
    options = {option["flag"].rstrip("="): option for category in profile["categories"] for option in category["options"]}
    needs_value = False
    driver = driver_registry.get(path.words[0])
    route = driver.paths.get(path.words[1:]) if driver else None
    stop_at_positional = route is not None and route.stop_at_positional
    for word in previous:
        if needs_value:
            needs_value = False
            continue
        if word == "--":
            raise HelpError("Options cannot be inserted after the -- end-of-options marker.")
        key, equal, _ = word.partition("=")
        option = options.get(key, {})
        if stop_at_positional:
            if not word.startswith("-"):
                raise HelpError("Move the cursor before the first positional argument to insert this command's options.")
            if not option:
                raise HelpError("An unrecognized option or short-option bundle makes the argument position ambiguous.")
        needs_value = bool(option.get("argument")) and not option.get("argument_optional", False) and not equal
    if needs_value:
        raise HelpError("Enter the preceding option's argument before choosing another option.")
    return Context(line, point, start, end, query, profile)


def insert_option(context: Context, option: dict) -> tuple[str, int]:
    """Replace only the active option token and return the buffer and character cursor.

    Insertable text is restricted to validated profile flags. No shell program,
    expression, completion script, or command under construction is evaluated.
    """
    allowed = [item for category in context.profile["categories"] for item in category["options"]]
    if option not in allowed:
        raise HelpError("The selected option is absent from the active profile.")
    flag = option["flag"]
    suffix = context.line[context.end:]
    has_separator = bool(suffix) and suffix[0] in " \t"
    separator = "" if flag.endswith("=") or has_separator else " "
    replacement = flag + separator
    line = context.line[:context.start] + replacement + suffix
    point = context.start + len(replacement)
    if not flag.endswith("=") and not separator and has_separator:
        point += 1
    return line, point
