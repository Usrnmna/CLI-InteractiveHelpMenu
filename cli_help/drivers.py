"""Validate declarative help drivers without importing or evaluating driver code."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re


WORD = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*")
FLAG = re.compile(r"--?[A-Za-z0-9][A-Za-z0-9_-]*")


@dataclass(frozen=True)
class HelpRoute:
    """Describe a fixed help invocation and optional manual, independent of input."""

    arguments: tuple[str, ...]
    manual: str | None
    stop_at_positional: bool = False


@dataclass
class Driver:
    """Associate literal subcommand paths with help routes and global-option arity."""

    paths: dict[tuple[str, ...], HelpRoute] = field(default_factory=dict)
    global_values: frozenset[str] = frozenset()
    global_flags: frozenset[str] = frozenset()


def parse_driver(document: dict) -> tuple[str, Driver]:
    """Reject ambiguous schemas, executable templates, and nonliteral help routes.

    Driver help arguments must begin with an explicit help selector. Drivers are
    trusted local configuration: these checks do not sandbox program startup or
    prove that an arbitrary executable honors its declared help selector.
    """
    allowed = {"command", "global_values", "global_flags", "paths"}
    if not isinstance(document, dict) or set(document) - allowed:
        raise ValueError("A driver requires an object with command, paths, and optional global option lists.")
    name = document.get("command")
    if not isinstance(name, str) or not WORD.fullmatch(name):
        raise ValueError("Driver command must be a literal executable basename.")
    globals_by_kind = {}
    for kind in ("global_values", "global_flags"):
        flags = document.get(kind, [])
        if not isinstance(flags, list) or any(not isinstance(flag, str) or not FLAG.fullmatch(flag) for flag in flags):
            raise ValueError(f"Driver {kind} must contain literal option names.")
        if len(flags) != len(set(flags)):
            raise ValueError(f"Duplicate option in driver {kind}.")
        globals_by_kind[kind] = frozenset(flags)
    if globals_by_kind["global_values"] & globals_by_kind["global_flags"]:
        raise ValueError("A driver global option cannot have conflicting argument arity.")
    routes = document.get("paths")
    if not isinstance(routes, list) or not routes:
        raise ValueError("A driver requires at least one help path.")
    paths = {}
    for route in routes:
        if not isinstance(route, dict) or set(route) - {"command", "help", "man", "stop_at_positional"}:
            raise ValueError("Unknown driver route field.")
        words = route.get("command")
        if not isinstance(words, list) or any(not isinstance(word, str) or not WORD.fullmatch(word) for word in words):
            raise ValueError("Driver path must be a list of literal subcommand words; [] selects root help.")
        arguments = route.get("help", [])
        if not isinstance(arguments, list) or len(arguments) > 16 or any(
            not isinstance(argument, str) or not re.fullmatch(r"[A-Za-z0-9_.:+/=-]+", argument) for argument in arguments
        ):
            raise ValueError("Driver help arguments must be fixed literal words without templates or shell syntax.")
        if arguments and arguments[0] not in ("help", "--help", "-h", "-help"):
            raise ValueError("Driver help arguments must begin with help, --help, -h, or -help.")
        manual = route.get("man")
        if manual is not None and (not isinstance(manual, str) or not WORD.fullmatch(manual)):
            raise ValueError("Driver man must be a literal manual name or null.")
        if not arguments and not manual:
            raise ValueError("A driver route requires a help invocation or manual name.")
        stop = route.get("stop_at_positional", False)
        if not isinstance(stop, bool):
            raise ValueError("stop_at_positional must be a boolean.")
        path = tuple(words)
        if path in paths:
            raise ValueError("Duplicate command path in driver.")
        paths[path] = HelpRoute(tuple(arguments), manual, stop)
    return name, Driver(paths, **globals_by_kind)


def load_driver_files(directory: Path, registry: dict[str, Driver]) -> dict[str, Driver]:
    """Overlay one JSON file per executable onto built-in drivers atomically.

    Matching routes are replaced; other built-in routes remain available. New
    global option declarations extend existing sets without changing their arity.
    No file is imported as code, and no discovery subprocess runs during loading.
    """
    if not directory.is_dir():
        raise ValueError(f"Driver directory does not exist: {directory}")
    result = dict(registry)
    seen = set()
    for path in sorted(directory.glob("*.json")):
        try:
            if path.stat().st_size > 256 * 1024:
                raise ValueError("Driver file exceeds 256 KiB.")
            name, driver = parse_driver(json.loads(path.read_text(encoding="utf-8")))
            if name in seen:
                raise ValueError("Duplicate executable driver in directory.")
            seen.add(name)
            previous = result.get(name, Driver({(): HelpRoute(("--help",), name)}))
            values = previous.global_values | driver.global_values
            flags = previous.global_flags | driver.global_flags
            if values & flags:
                raise ValueError("Driver overlay conflicts with existing global-option arity.")
            result[name] = Driver({**previous.paths, **driver.paths}, values, flags)
        except (OSError, ValueError, RecursionError) as error:
            raise ValueError(f"Invalid driver {path}: {error}") from error
    return result
