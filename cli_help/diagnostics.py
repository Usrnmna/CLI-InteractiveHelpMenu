"""Passive configuration and context reports without discovery or persistence."""

import hashlib
import importlib.util
import json
import locale
import math
import os
from pathlib import Path
import shutil
import sys
import time

from command_paths import help_route, load_driver_registry
from core import find_context, load_profiles, read_json, tokenize, validate_profile
from discovery import (CACHE_VERSION, Settings, cache_identity,
                       module_help_route, read_cache_document)
from errors import HelpError


MAX_CACHE_INSPECTION = 128
REFRESH_GUIDANCE = "Use --discover with the documented command path and --refresh for an explicit active lookup."


def configured_paths(root, expand=True):
    """Report only explicitly selected configuration locations, never other environment values."""
    paths = {"bundled_profiles": str(root / "profiles")}
    for field, variable in (("custom_profiles", "CLI_HELP_PROFILES"), ("drivers", "CLI_HELP_DRIVERS"), ("keys", "CLI_HELP_CONFIG")):
        value = os.environ.get(variable)
        try:
            paths[field] = str(Path(value).expanduser()) if value and expand else value or None
        except RuntimeError as error:
            raise HelpError("A selected configuration location cannot be expanded; inspect the profile, driver, and key paths.",
                            "configuration_invalid") from error
    return paths


def load_configuration(root):
    """Load the same data as the interactive entry point without executing configured code."""
    paths = configured_paths(root)
    profiles = load_profiles(root / "profiles", Path(paths["custom_profiles"]) if paths["custom_profiles"] else None)
    drivers = load_driver_registry(Path(paths["drivers"]) if paths["drivers"] else None)
    return profiles, drivers, Settings.from_environment(), paths


def driver_selection(root, paths):
    """Describe explicit activation without inferring provenance from copied content."""
    selected = paths["drivers"]
    supplied = root / "config/drivers.example"
    return {"source": "CLI_HELP_DRIVERS" if selected else "built_in",
            "directory": selected, "composition": "built_in_then_one_directory",
            "supplied_directory": str(supplied), "supplied_available": supplied.is_dir(),
            "supplied_selected": bool(selected and Path(selected).resolve() == supplied.resolve()),
            "detail": "One explicit directory overlays built-in routes. Copied collections are custom selections; no automatic layering occurs."}


def route_provenance(command, invocation, registry, static_profile=False):
    """Report route ownership without disclosing arbitrary configured operands.

    Drivers may contain private constant arguments or custom manual aliases.
    Only known documentation selectors and resolved command words are displayed;
    the original route remains unchanged for explicitly configured discovery.
    static_profile indicates an exact profile match for the selected path.
    """
    if invocation.module:
        arguments, manual = module_help_route(invocation.module, tuple(command[1:]), invocation.interpreter_options)
        return {"kind": "module_adapter", "help_arguments": list(arguments), "manual": manual}
    name, *words = command
    driver = registry.get(name)
    try:
        route = help_route(name, tuple(words), registry)
    except ValueError:
        return {"kind": "profile_only" if static_profile else "unconfigured", "help_arguments": [], "manual": None,
                "detail": ("An explicit static profile supplies this path; automatic discovery is unconfigured."
                           if static_profile else "An explicit static profile or driver route is required for this path.")}
    arguments = list(route.arguments)
    if name == "pytest" and not words:
        # Match discovery's mandatory project/plugin isolation override.
        arguments = ["--help", "--noconftest"]
    public_words = {"help", "--help", "-h", "-help", "all", "flags", "--noconftest", *words}
    displayed_arguments = [word if word in public_words else "<redacted>" for word in arguments]
    public_manual = route.manual is None or route.manual in {name, "-".join(command)}
    built_in = name in load_driver_registry()
    result = {"kind": "configured" if route.source else "built_in" if built_in else "generic",
              "help_arguments": displayed_arguments, "help_arguments_redacted": displayed_arguments != arguments,
              "manual": route.manual if public_manual else "<redacted>", "manual_redacted": not public_manual,
              "stop_at_positional": route.stop_at_positional,
              "stop_at_options": list(route.stop_at_options)}
    if name == "pytest" and not words:
        result["help_override"] = "pytest_no_conftest"
    if name == "yarn" and words == ["run"]:
        result["help_arguments_pending_identity"] = True
    if route.source:
        result["file"] = route.source
    if driver:
        result["global_options"] = {"composition": "built_in_union_overlay" if built_in else "configured",
                                    "overlay_file": driver.source}
    return result


def source_warning_codes(warnings):
    """Classify stored warnings into fixed labels without returning cached prose."""
    rules = (("timed out", "source_timeout"), ("exceeded", "source_output_limit"),
             ("Cannot start", "source_start_failed"), ("No option declarations", "source_unparsed"),
             ("man executable is unavailable", "manual_unavailable"),
             ("Module identity", "module_identity_unverified"),
             ("System module manuals", "system_manual_version_unverified"))
    result = set()
    for warning in warnings if isinstance(warnings, list) else []:
        matched = {code for fragment, code in rules if isinstance(warning, str) and fragment in warning}
        result.update(matched or {"source_warning"})
    return sorted(result)


def shell_locale_is_utf8():
    """Inspect the environment's CTYPE encoding independently of Python UTF-8 mode.

    Locale changes are process-local and restored before returning. Python's
    preferred encoding can be UTF-8 while Bash still uses the ASCII C locale.
    """
    previous = locale.setlocale(locale.LC_CTYPE)
    try:
        locale.setlocale(locale.LC_CTYPE, "")
        encoding = (locale.nl_langinfo(locale.CODESET) if hasattr(locale, "nl_langinfo")
                    else locale.getpreferredencoding(False))
        return encoding.lower().replace("-", "") == "utf8"
    except (locale.Error, ValueError):
        return False
    finally:
        locale.setlocale(locale.LC_CTYPE, previous)


def doctor(root):
    """Inspect requirements and data; availability does not establish executable versions."""
    paths = configured_paths(root, expand=False)
    checks = []

    def check(name, success, detail, required=True):
        checks.append({"name": name, "status": "ok" if success else "unavailable",
                       "detail": detail, "required": required})

    check("linux", sys.platform.startswith("linux"), "The interactive runtime requires Linux.")
    check("python", sys.version_info >= (3, 10), "Python 3.10 or newer is required.")
    check("utf8", shell_locale_is_utf8(), "A UTF-8 shell locale is required; Python UTF-8 mode alone is insufficient.")
    check("curses", importlib.util.find_spec("_curses") is not None,
          "Curses availability is inspected without attaching a terminal.")
    for name in ("bash", "stty", "man"):
        checks.append({"name": name, "status": "available" if shutil.which(name) else "unavailable",
                       "executable": shutil.which(name), "required": name != "man",
                       "detail": "Availability only; no program was started. Bash 4.4+ is required." if name == "bash" else "Availability only; no program was started."})
    check("terminal", os.isatty(0) and os.isatty(1), "No terminal was opened; redirected diagnostic output is supported.", False)
    try:
        profiles, drivers, settings, paths = load_configuration(root)
        from ui import load_keys
        load_keys(Path(paths["keys"]) if paths["keys"] else None)
        configuration = {"status": "valid", "profiles": len(profiles), "drivers": len(drivers),
                         "driver_selection": driver_selection(root, paths),
                         "discovery_mode": settings.mode, "source_timeout_seconds": settings.timeout,
                         "cache_ttl_seconds": settings.cache_ttl,
                         "cache_directory": str(settings.cache_dir) if settings.cache_dir else None}
    except (HelpError, OSError, ValueError, ImportError, RuntimeError, RecursionError):
        configuration = {"status": "invalid", "code": "configuration_invalid",
                         "detail": "Inspect the selected profile, driver, key, and discovery settings; no configuration content is included."}
    failed = configuration["status"] != "valid" or any(item["required"] and item["status"] == "unavailable" for item in checks)
    return {"schema_version": 1, "mode": "doctor", "status": "attention_required" if failed else "ok",
            "paths": paths, "checks": checks, "configuration": configuration,
            "execution": "passive; executable versions and interactive rendering are unverified"}


def inspect_cache(command, executable_word, invocation, settings, registry):
    """Read bounded candidate envelopes; unperformed identity probes remain explicit.

    Module and guarded-tool cache keys depend on active version evidence. Passive
    inspection may locate a candidate but never declares that evidence current.
    No cached prose, arbitrary warnings, or subprocess output enters the report.
    """
    summary = {"status": "disabled", "ttl_seconds": settings.cache_ttl,
               "freshness": "ttl_and_executable_identity", "refresh_guidance": REFRESH_GUIDANCE}
    if invocation.module and settings.mode == "auto":
        summary["freshness"] = "fixed_module_version_before_each_cache_read; unchanged-version edits require TTL or refresh"
    if settings.mode == "off" or not settings.cache_ttl or settings.cache_dir is None:
        return summary, None
    name = Path(executable_word).name
    guarded = name in {"yq", "yarn", "esptool", "esptool.py"}
    needs_identity = guarded or bool(invocation.module and settings.mode == "auto")
    if invocation.module:
        arguments, manual_name = module_help_route(invocation.module, tuple(command[1:]), invocation.interpreter_options)
    else:
        try:
            route = help_route(name, tuple(command[1:]), registry)
        except ValueError:
            summary["status"] = "not_applicable"
            summary["detail"] = "No automatic discovery route is configured for this command path."
            summary["refresh_guidance"] = "Supply or edit an explicit static profile, or configure a reviewed driver route."
            return summary, None
        arguments, manual_name = list(route.arguments), route.manual
        if name == "pytest" and len(command) == 1:
            arguments = ["--help", "--noconftest"]
    executable = shutil.which(executable_word)
    if not executable:
        summary["status"] = "executable_missing"
        return summary, None
    manual = shutil.which("man")
    expected = cache_identity(command, os.path.abspath(executable), arguments, manual_name,
                              os.path.abspath(manual) if manual else None, settings,
                              invocation.module, invocation.interpreter_options)
    summary["status"] = "miss"
    candidates = []
    try:
        if needs_identity:
            # Iteration is bounded even when a cache directory contains many entries.
            from itertools import islice
            candidates = list(islice(settings.cache_dir.glob("*.json"), MAX_CACHE_INSPECTION + 1))
            summary["inspection_limited"] = len(candidates) > MAX_CACHE_INSPECTION
            candidates = candidates[:MAX_CACHE_INSPECTION]
        else:
            digest = hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()
            candidates = [settings.cache_dir / (digest + ".json")]
        matches = []
        for path in candidates:
            try:
                document = read_cache_document(path)
                identity = document["identity"]
                compared = {key: value for key, value in expected.items() if not (guarded and key == "help_arguments")}
                if not isinstance(identity, dict) or any(identity.get(key) != value for key, value in compared.items()):
                    continue
                if identity.get("version") != CACHE_VERSION:
                    continue
                profile = document["profile"]
                validate_profile(profile, path)
                if profile["command"] != list(command):
                    continue
                age = time.time() - document["created"]
                if not math.isfinite(age) or age < 0:
                    continue
                matches.append((age, profile))
            except (OSError, ValueError, KeyError, TypeError, RecursionError):
                continue
        if not matches:
            return summary, None
        age, profile = min(matches, key=lambda entry: entry[0])
        fresh = age < settings.cache_ttl
        discovery = profile.get("discovery", {})
        warnings = discovery.get("warnings", []) if isinstance(discovery, dict) else []
        summary.update({"status": ("candidate_requires_verification" if needs_identity else "available") if fresh else "expired",
                        "age_seconds": round(age, 3), "source_warning_count": len(warnings) if isinstance(warnings, list) else 0,
                        "source_warnings": source_warning_codes(warnings)})
        return summary, profile if fresh else None
    except OSError:
        summary["status"] = "unavailable"
        return summary, None


def profile_origin(profile_path, paths):
    """Locate exact static-profile provenance without exposing profile contents."""
    for kind, directory in (("custom", paths["custom_profiles"]), ("bundled", paths["bundled_profiles"])):
        if directory:
            for path in sorted(Path(directory).glob("*.json")):
                document = read_json(path)
                if isinstance(document, dict) and document.get("command") == list(profile_path):
                    return {"kind": kind, "file": str(path)}
    return {"kind": "discovery_required"}


def explain(root, line, point):
    """Explain the buffer/cursor using the real context validator and no target probes."""
    report = {"schema_version": 1, "mode": "explain", "status": "rejected",
              "code": "configuration_invalid", "execution": "passive; pending input omitted"}
    try:
        profiles, registry, settings, paths = load_configuration(root)
        report["driver_selection"] = driver_selection(root, paths)
        tokens = tokenize(line)
        observed = {}

        def observe(command, profile_path, invocation):
            cache, cached_profile = inspect_cache(command, tokens[invocation.executable_index].value,
                                                 invocation, settings, registry)
            observed.update({"cache_profile": cached_profile, "invocation": invocation})
            origin = profile_origin(profile_path, paths)
            report.update({"resolved_command": list(command), "profile": origin,
                           "route": route_provenance(command, invocation, registry, origin["kind"] in {"bundled", "custom"}),
                           "cache": cache, "discovery_mode": settings.mode})

        def passive_lookup(executable, subcommands=(), **module):
            if settings.mode == "off":
                raise HelpError("Discovery is disabled; an ordinary static profile is required.", "discovery_disabled")
            if report["profile"]["kind"] in {"bundled", "custom"}:
                raise HelpError("The guarded profile requires active executable verification.", "identity_verification_required")
            if observed.get("cache_profile") is not None:
                report["profile"] = {"kind": "cached"}
                return observed["cache_profile"]
            raise HelpError("Documentation requires an explicit help/manual lookup; passive inspection performs none.", "discovery_required")

        find_context(line, point, profiles, discover=passive_lookup, driver_registry=registry, observe=observe)
        unverified = report.get("profile", {}).get("kind") == "cached" and report["cache"]["status"] == "candidate_requires_verification"
        report.update({"status": "metadata_unverified" if unverified else "ready",
                       "code": "identity_verification_required" if unverified else "context_valid",
                       "detail": "Cached metadata was used only for passive argument checks; active identity remains unverified." if unverified else "The editable position is valid for the available metadata; no insertion or execution occurred."})
    except HelpError as error:
        report.update({"code": error.code, "detail": str(error) if error.code != "invalid_configuration" else "The configuration or command context is unsupported; inspect the documented constraints."})
        if error.code in {"discovery_required", "identity_verification_required", "discovery_disabled"}:
            report["status"] = "needs_discovery"
    except (OSError, ValueError, ImportError, RuntimeError, RecursionError):
        report.update({"code": "inspection_failed", "detail": "Passive inspection could not read or validate the selected configuration and cache."})
    return report
