"""Recognize a bounded invocation grammar without evaluating shell words."""

from dataclasses import dataclass
from pathlib import Path
import re

from drivers import Driver, HelpRoute


ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=.*", re.DOTALL)
LOOKUP_VARIABLES = frozenset({"PATH", "PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "MANPATH", "LD_PRELOAD", "LD_LIBRARY_PATH"})
INTERPRETER_FLAGS = frozenset({"-I", "-E", "-s", "-S", "-B", "-u", "-O", "-OO"})
PIP_MODULE_COMMANDS = frozenset({"install", "uninstall", "download", "list"})


def module_driver(module: str) -> Driver:
    """Supply immutable module grammar, independent of executable driver overlays."""
    paths = {(): HelpRoute(("--help",), module)}
    if module == "pip":
        paths.update({(command,): HelpRoute(("help", command), "pip-" + command)
                      for command in PIP_MODULE_COMMANDS})
        return Driver(paths,
                      frozenset({"--proxy", "--timeout", "--retries", "--log", "--keyring-provider"}),
                      frozenset({"--isolated", "--no-input", "--disable-pip-version-check", "--no-color",
                                 "-v", "--verbose", "-q", "--quiet"}))
    return Driver(paths)


@dataclass(frozen=True)
class Invocation:
    """Locate the target word while retaining all original token offsets."""

    executable_index: int
    argument_start: int
    name: str
    module: str | None = None
    interpreter_options: tuple[str, ...] = ()


def assignment_name(word):
    """Return a literal assignment name and reject documentation lookup changes."""
    match = ASSIGNMENT.fullmatch(word)
    if not match:
        return None
    name = match.group(1)
    if name in LOOKUP_VARIABLES or name.startswith(("PYTHON", "LD_", "DYLD_")):
        raise ValueError(f"Environment assignment {name} changes lookup or loading; this prefix form is unsupported.")
    return name


def resolve_invocation(words: list[str]) -> Invocation:
    """Strip recognized prefix syntax and allowlisted Python module invocation.

    Prefixes select local documentation only: privilege, environment and working
    directory changes are never applied to probes. Lookup-changing forms fail
    closed. The command builtin can only precede external prefixes.
    """
    index = 0
    external_prefix = False
    while index < len(words):
        name = Path(words[index]).name
        if name not in {"sudo", "env", "command"}:
            break
        if name == "command" and (external_prefix or words[index] != "command"):
            raise ValueError("The command builtin is supported only before external prefixes.")
        index += 1
        if name == "command":
            if index < len(words) and words[index] == "--":
                index += 1
            elif index < len(words) and words[index].startswith("-"):
                raise ValueError("Only command [--] is supported; lookup and query forms are unsupported.")
            continue
        external_prefix = True
        flags = {"-n", "--non-interactive", "-E", "--preserve-env", "-H", "--set-home", "-k", "--reset-timestamp"} if name == "sudo" else set()
        values = {"-u", "--user", "-g", "--group", "-p", "--prompt"} if name == "sudo" else {"-u", "--unset"}
        while index < len(words) and words[index].startswith("-"):
            word = words[index]
            if word == "--":
                index += 1
                break
            key, equal, value = word.partition("=")
            if word in flags:
                index += 1
                continue
            if key in values:
                if not equal:
                    index += 1
                    if index >= len(words) or words[index].startswith("-"):
                        raise ValueError(f"Complete the {name} option value before opening help.")
                    value = words[index]
                if not value:
                    raise ValueError(f"The {name} option requires a nonempty value.")
            else:
                short = next((flag for flag in values if len(flag) == 2 and word.startswith(flag) and len(word) > 2), None)
                if short is None:
                    raise ValueError(f"Unsupported or lookup-changing {name} option {word!r}.")
                value = word[2:]
            if name == "env":
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                    raise ValueError("The env unset name must be a literal environment variable identifier.")
                assignment_name(value + "=")
            index += 1
        while index < len(words) and assignment_name(words[index]) is not None:
            index += 1
    if index >= len(words):
        raise ValueError("Type a target command after the recognized prefix.")
    if ASSIGNMENT.fullmatch(words[index]):
        raise ValueError("Leading shell assignments require an explicit env prefix.")
    executable_index = index
    name = Path(words[index]).name
    if name not in {"python", "python3"}:
        return Invocation(index, index + 1, name)
    index += 1
    options = []
    while index < len(words) and words[index] in INTERPRETER_FLAGS:
        options.append(words[index])
        index += 1
    if index >= len(words) or words[index] != "-m":
        raise ValueError("Python help supports only recognized interpreter flags followed by -m pip or -m pytest.")
    index += 1
    if index >= len(words) or words[index] not in {"pip", "pytest"}:
        raise ValueError("Only the pip and pytest Python modules are supported.")
    return Invocation(executable_index, index + 1, words[index], words[index], tuple(options))
