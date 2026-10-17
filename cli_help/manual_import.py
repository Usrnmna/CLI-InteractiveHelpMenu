"""Import manual documentation into reusable profiles and manual-only drivers."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from core import HelpError, load_profiles, read_json, validate_profile
from discovery import MAX_OUTPUT_BYTES, build_profile, run_probe
from drivers import WORD, parse_driver
from command_paths import load_driver_registry


def read_manual(command: list[str], manual: str | None = None, text_file: Path | None = None,
                man_file: Path | None = None, timeout: float = 2.0) -> tuple[str, str, str]:
    """Read rendered text or render a selected local/installed page with bounded man.

    No target executable lookup or invocation is required. Local roff and gzip
    files are rendered by man; rendered UTF-8 text is read directly. Manual
    rendering inherits the same process limits as ordinary discovery.
    """
    if not command or any(not isinstance(word, str) or not WORD.fullmatch(word) for word in command):
        raise HelpError("Import requires literal command and subcommand names, without pending arguments.")
    manual = manual or "-".join(command)
    if not WORD.fullmatch(manual):
        raise HelpError("The manual page name must be literal, without paths or options.")
    if text_file and man_file:
        raise HelpError("Select one manual input file format.")
    source = text_file or man_file
    if source:
        source = source.expanduser().resolve(strict=True)
        if not source.is_file() or source.stat().st_size > MAX_OUTPUT_BYTES:
            raise HelpError(f"Manual input must be a regular file no larger than {MAX_OUTPUT_BYTES} bytes.")
    if text_file:
        return source.read_text(encoding="utf-8"), f"Imported manual text: {source.name}", manual
    renderer = shutil.which("man")
    if not renderer:
        raise HelpError("The man executable is required for rendering. Use --man-text for pre-rendered text.")
    arguments = [os.path.abspath(renderer), "-P", "/bin/cat", "--no-hyphenation", "--no-justification"]
    arguments += ["-l", "--", str(source)] if man_file else ["-s", "1:8", "--", manual]
    label = f"Imported local manual: {source.name}" if man_file else f"man {manual}"
    return run_probe(arguments, timeout, check=True), label, manual


def atomic_json(path: Path, document: dict, ascii_only=False):
    """Replace a single JSON document atomically, leaving no temporary file behind."""
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, ensure_ascii=ascii_only, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


class ImportConflict(HelpError):
    """An existing profile or route requires explicit replacement authorization."""


def validate_documents(profile: dict, document: dict):
    """Check a profile/driver pair against the schemas and built-in overlay rules."""
    validate_profile(profile, Path("<edited profile>"))
    command = profile["command"]
    name, driver = parse_driver(document)
    if name != command[0] or tuple(command[1:]) not in driver.paths:
        raise HelpError("The driver must describe the profile's command path.")
    baseline = load_driver_registry().get(name)
    if baseline and ((baseline.global_values | driver.global_values) & (baseline.global_flags | driver.global_flags)):
        raise HelpError("Driver overlay conflicts with built-in global-option arity.")
    if len(json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8")) + 1 > 256 * 1024:
        raise HelpError("Driver file exceeds 256 KiB.")


class ManualCollection:
    """Lock and index a collection once for single imports or large batches.

    All importer writers share this lock. Each JSON file is atomic, but the
    profile/driver pair is not a filesystem transaction. An interrupted pair
    can be reconciled by repeating the import with explicit replacement.
    """

    def __init__(self, output_dir: Path):
        self.destination = output_dir.expanduser().resolve()
        self.driver_directory = self.destination / "drivers"
        self.profile_directory = self.destination / "profiles"
        self.lock = self.destination / ".import.lock"
        self.drivers = {}
        self.profiles = {}

    def __enter__(self):
        self.destination.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise HelpError(f"Another import is active or interrupted: {self.lock}. Inspect the importer before removing its lock.") from error
        os.close(descriptor)
        try:
            if self.driver_directory.exists():
                load_driver_registry(self.driver_directory)
                for path in sorted(self.driver_directory.glob("*.json")):
                    document = read_json(path)
                    self.drivers[document["command"]] = (path, document)
            if self.profile_directory.exists():
                load_profiles(self.profile_directory)
                for path in sorted(self.profile_directory.glob("*.json")):
                    self.profiles[tuple(read_json(path)["command"])] = path
            return self
        except BaseException:
            self.lock.unlink(missing_ok=True)
            raise

    def __exit__(self, *exc):
        self.lock.unlink(missing_ok=True)

    def contains(self, command: list[str]) -> bool:
        """Detect either half of an existing profile/route pair before rendering."""
        _, document = self.drivers.get(command[0], (None, {"paths": []}))
        return tuple(command) in self.profiles or any(route["command"] == command[1:] for route in document["paths"])

    def paths_for(self, command: list[str]) -> tuple[Path, Path]:
        """Reuse existing filenames or derive deterministic destinations for a pair."""
        identity = hashlib.sha256(json.dumps(command).encode()).hexdigest()[:12]
        profile = self.profiles.get(tuple(command), self.profile_directory / ("-".join(command) + "-" + identity + ".json"))
        driver = self.drivers.get(command[0], (self.driver_directory / (command[0] + ".json"), None))[0]
        return profile, driver

    def save(self, profile: dict, manual: str, replace=False, driver_defaults=None) -> dict:
        """Save a validated profile and merge its manual-only driver route."""
        validate_profile(profile, Path("<imported manual>"))
        command = profile["command"]
        if self.contains(command) and not replace:
            raise ImportConflict("This command already has an imported profile or driver route. Use --replace to update it.")
        initial = {"command": command[0], "paths": []}
        if driver_defaults:
            initial.update(global_values=sorted(driver_defaults.global_values), global_flags=sorted(driver_defaults.global_flags))
        _, document = self.drivers.get(command[0],
            (self.driver_directory / (command[0] + ".json"), initial))
        previous = next((route for route in document["paths"] if route["command"] == command[1:]), {})
        if not previous and driver_defaults:
            route = driver_defaults.paths.get(tuple(command[1:]))
            if route and route.stop_at_positional:
                previous = {"stop_at_positional": True}
        routes = [route for route in document["paths"] if route["command"] != command[1:]]
        routes.append({**previous, "command": command[1:], "help": [], "man": manual})
        document = {**document, "paths": routes}
        return self.save_documents(profile, document, replace)

    def save_documents(self, profile: dict, document: dict, replace=False) -> dict:
        """Validate and persist an edited profile/driver pair under the collection lock.

        Explicit replacement permits corrections to driver metadata. Built-in
        global-option arity remains enforced by the normal driver overlay rules.
        """
        validate_documents(profile, document)
        command = profile["command"]
        if self.contains(command) and not replace:
            raise ImportConflict("This command already has an imported profile or driver route. Use --replace to update it.")
        profile_path, driver_path = self.paths_for(command)
        atomic_json(profile_path, profile)
        self.profiles[tuple(command)] = profile_path
        atomic_json(driver_path, document)
        self.drivers[command[0]] = (driver_path, document)
        return {"command": command, "profile": str(profile_path), "driver": str(driver_path),
                "profile_directory": str(self.profile_directory), "driver_directory": str(self.driver_directory),
                "option_count": sum(len(category["options"]) for category in profile["categories"])}


def import_manual(command: list[str], output_dir: Path, manual: str | None = None,
                  text_file: Path | None = None, man_file: Path | None = None,
                  timeout: float = 2.0, replace=False) -> dict:
    """Convert one manual and preserve existing entries unless replacement is explicit."""
    text, label, manual = read_manual(command, manual, text_file, man_file, timeout)
    profile = build_profile(command, [(label, text)])
    profile["imported_from"] = {"source": label, "manual": manual}
    with ManualCollection(output_dir) as collection:
        return collection.save(profile, manual, replace)
