"""Recognize documented command paths without interpreting pending arguments."""

from dataclasses import dataclass
from pathlib import Path

from drivers import Driver, HelpRoute, load_driver_files


# Explicit paths prevent filenames, aliases, and plugin names from becoming
# executable help requests. Extensions require a reviewed help route or profile.
GIT_COMMANDS = frozenset("""
add am apply archive blame branch checkout cherry cherry-pick clean clone commit
describe diff fetch format-patch grep init log merge mv pull push rebase reflog
reset restore revert rm show status switch tag
""".split())
DOCKER_COMMANDS = frozenset("""
attach build commit cp create diff events exec export history images import info
inspect kill load login logout logs pause port ps pull push rename restart rm rmi
run save search start stats stop tag top unpause update version wait
""".split())
DOCKER_GROUPS = {
    "container": "attach commit cp create diff exec export inspect kill logs ls pause port prune rename restart rm run start stats stop top unpause update wait",
    "image": "build history import inspect load ls prune pull push rm save tag",
    "network": "connect create disconnect inspect ls prune rm",
    "volume": "create inspect ls prune rm update",
    "context": "create export import inspect ls rm show update use",
    "system": "df events info prune",
}
BUILTIN_PATHS = {("git", command) for command in GIT_COMMANDS}
BUILTIN_PATHS.update(("docker", command) for command in DOCKER_COMMANDS)
for group, commands in DOCKER_GROUPS.items():
    BUILTIN_PATHS.add(("docker", group))
    BUILTIN_PATHS.update(("docker", group, command) for command in commands.split())

GLOBAL_VALUES = {
    "git": frozenset(("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env")),
    "docker": frozenset(("-c", "--context", "-H", "--host", "--config", "-l", "--log-level",
                         "--tlscacert", "--tlscert", "--tlskey")),
}
GLOBAL_FLAGS = {
    "git": frozenset(("-p", "--paginate", "-P", "--no-pager", "--bare", "--no-replace-objects",
                      "--literal-pathspecs", "--glob-pathspecs", "--noglob-pathspecs", "--icase-pathspecs",
                      "--no-optional-locks", "--no-lazy-fetch")),
    "docker": frozenset(("-D", "--debug", "--tls", "--tlsverify")),
}
DOCKER_POSITIONAL_BOUNDARIES = {("docker", command) for command in ("run", "create", "exec")}
DOCKER_POSITIONAL_BOUNDARIES.update(("docker", "container", command) for command in ("run", "create", "exec"))


@dataclass(frozen=True)
class CommandPath:
    """Store a recognized documentation path and the first command argument index."""

    words: tuple[str, ...]
    argument_start: int


def load_driver_registry(directory: Path | None = None) -> dict[str, Driver]:
    """Construct built-in Git/Docker drivers and overlay optional local JSON files."""
    registry = {}
    for name in GLOBAL_VALUES:
        paths = {(): HelpRoute(("--help",), name)}
        for path in BUILTIN_PATHS:
            if path[0] == name:
                arguments = () if name == "git" else ("help", *path[1:])
                paths[path[1:]] = HelpRoute(arguments, "-".join(path), path in DOCKER_POSITIONAL_BOUNDARIES)
        registry[name] = Driver(paths, GLOBAL_VALUES[name], GLOBAL_FLAGS[name])
    return load_driver_files(directory, registry) if directory is not None else registry


def resolve_path(words: list[str], static_paths: list[tuple[str, ...]], registry=None) -> CommandPath:
    """Resolve completed words before the cursor, skipping known global values.

    Drivers define automatic subcommand adapters. Other executables retain
    literal static-path matching and top-level discovery. Unknown global
    options or command paths in an adapted family fail before any help probe.
    """
    name = words[0]
    registry = load_driver_registry() if registry is None else registry
    driver = registry.get(name)
    if driver is None or not any(driver.paths):
        matches = [path for path in static_paths if tuple(words[:len(path)]) == path]
        path = max(matches, key=len) if matches else (name,)
        return CommandPath(path, len(path))
    index = 1
    while index < len(words) and words[index].startswith("-"):
        word = words[index]
        key, equal, value = word.partition("=")
        if word in driver.global_values:
            if index + 1 >= len(words):
                raise ValueError("Enter the global option's value before opening help.")
            index += 2
        elif equal and key in driver.global_values:
            index += 1
        elif any(word.startswith(flag) and len(word) > len(flag)
                 for flag in driver.global_values if len(flag) == 2):
            index += 1
        elif word in driver.global_flags or (equal and key in driver.global_flags and value in ("true", "false")):
            index += 1
        else:
            raise ValueError(f"Unsupported global option {word!r}; the command path is ambiguous.")
    path = (name,)
    candidates = {(name, *path) for path in driver.paths} | set(static_paths)
    while index < len(words):
        children = {candidate[len(path)] for candidate in candidates
                    if candidate[:len(path)] == path and len(candidate) > len(path)}
        if not children:
            break
        if path in candidates and words[index].startswith("-"):
            # A documented parent command can have options as well as child
            # commands. Its options must not be interpreted as subcommand names.
            break
        if words[index] not in children:
            raise ValueError(f"Unsupported subcommand after {' '.join(path)!r}. Add an explicit profile.")
        path += (words[index],)
        index += 1
    return CommandPath(path, index)


def help_route(name: str, subcommands: tuple[str, ...], registry=None) -> HelpRoute:
    """Return fixed help arguments and a manual name for an allowlisted path.

    Git subcommands use direct manuals to avoid action dispatch and configured
    Git help viewers. Docker uses its help command, never an action command.
    """
    registry = load_driver_registry() if registry is None else registry
    if name in registry and subcommands in registry[name].paths:
        return registry[name].paths[subcommands]
    if not subcommands:
        return HelpRoute(("--help",), name)
    raise ValueError("Automatic discovery does not support this subcommand path. Add a driver or explicit profile.")
