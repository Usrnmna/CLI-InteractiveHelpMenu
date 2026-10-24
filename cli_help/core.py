"""Validate help definitions and calculate edits without evaluating shell text."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shlex

from command_paths import load_driver_registry, resolve_path
from invocation import module_driver, resolve_invocation
from errors import HelpError
from arguments import VALUE_STYLES, option_tokens, value_forms


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
    if not isinstance(profile.get("stop_at_positional", False), bool):
        raise HelpError("stop_at_positional must be a boolean.")
    boundaries = profile.get("stop_at_options", [])
    if not isinstance(boundaries, list) or any(not isinstance(flag, str) or not re.fullmatch(r"--?[A-Za-z0-9][A-Za-z0-9_-]*", flag) for flag in boundaries):
        raise HelpError("stop_at_options must contain literal option names.")
    if profile.get("identity") not in (None, "mikefarah-yq-v4", "javascript-yarn", "esptool-v4", "esptool-v5"):
        raise HelpError("Unknown executable identity requirement.")
    identity_names = {"mikefarah-yq-v4": {"yq"}, "javascript-yarn": {"yarn"},
                      "esptool-v4": {"esptool", "esptool.py"}, "esptool-v5": {"esptool", "esptool.py"}}
    if profile.get("identity") and command[0] not in identity_names[profile["identity"]]:
        raise HelpError("Executable identity requirement does not match the profile command.")
    group = profile.get("positional_group")
    if group is not None:
        if not isinstance(group, dict) or set(group) != {"argument", "argument_count", "repeatable"}:
            raise HelpError("positional_group requires argument, argument_count and repeatable.")
        require_text(group["argument"], "Positional group argument")
        if type(group["argument_count"]) is not int or not 2 <= group["argument_count"] <= 16 or group["repeatable"] is not True:
            raise HelpError("A repeated positional group requires 2-16 values and repeatable: true.")
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
            kind = option.get("kind", "flag")
            pattern = r"[A-Za-z][A-Za-z0-9_-]*" if kind == "keyword" else r"--?[A-Za-z0-9][A-Za-z0-9_-]*(?::[A-Za-z0-9][A-Za-z0-9_-]*)*=?"
            if not isinstance(kind, str) or kind not in {"flag", "keyword"} or not isinstance(flag, str) or not re.fullmatch(pattern, flag):
                raise HelpError(f"{source}: invalid literal option flag; inspect the literal flag schema.")
            if flag in flags:
                raise HelpError(f"{source}: duplicate option flag: {flag}")
            flags.add(flag)
            require_text(option.get("summary"), "Option summary")
            require_text(option.get("detail", ""), "Option detail", True)
            require_text(option.get("argument", ""), "Option argument", True)
            if not isinstance(option.get("argument_optional", False), bool):
                raise HelpError("argument_optional must be a boolean.")
            if not isinstance(option.get("attached", False), bool):
                raise HelpError("attached must be a boolean.")
            if option.get("attached") and (kind != "flag" or not option.get("argument")):
                raise HelpError("Attached values require a flag with an argument.")
            count = option.get("argument_count", 1)
            if type(count) is not int or not 1 <= count <= 16 or (count > 1 and not option.get("argument")):
                raise HelpError("argument_count must be an integer from 1 to 16; multiple values require an argument.")
            if "argument_style" in option:
                if (not isinstance(option["argument_style"], str) or option["argument_style"] not in VALUE_STYLES or not option.get("argument") or kind != "flag"
                        or count != 1 or "attached" in option
                        or flag.endswith("=") and option["argument_style"] != "equals"):
                    raise HelpError("argument_style requires one flag value, a supported style, and no legacy attached field.")
            if not isinstance(option.get("bundle", False), bool):
                raise HelpError("bundle must be a boolean.")
            if option.get("bundle") and (kind != "flag" or not re.fullmatch(r"-[A-Za-z0-9]", flag)
                    or count != 1 or option.get("argument_optional")
                    or option.get("argument") and not value_forms(option) & {"separate", "attached"}):
                raise HelpError("Bundle members require single-character flags and unambiguous required-value forms.")
            if "optional_value_kind" in option:
                if (option["optional_value_kind"] != "nonnegative_integer" or not option.get("argument")
                        or not option.get("argument_optional") or count != 1
                        or option.get("argument_style") not in (None, "separate")):
                    raise HelpError("optional_value_kind requires nonnegative_integer and one optional argument.")
    all_options = [option for category in categories for option in category["options"]]
    if any(option.get("argument_style") or option.get("bundle") for option in all_options):
        canonical_flags = [option["flag"].rstrip("=") for option in all_options]
        if len(canonical_flags) != len(set(canonical_flags)):
            raise HelpError("Explicit argument syntax requires unique option names, including equals spellings.")


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
        raise HelpError("Only single-line simple commands are supported.", "unsupported_shell_syntax")
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
                    raise HelpError("Complete the trailing escape before opening help.", "incomplete_escape")
                continue
            if char == quote:
                quote = None
            elif quote is None and char in "\"'":
                quote = char
            elif quote is None and char in " \t":
                break
            elif quote != "'" and char in "$`":
                raise HelpError("Shell expansions are not supported in this prototype.", "unsupported_shell_syntax")
            elif quote is None and char in "|&;<>()":
                raise HelpError("Pipelines, redirects, and compound commands are not supported.", "unsupported_shell_syntax")
            index += 1
        if quote:
            raise HelpError("Close the quoted argument before opening help.", "incomplete_quote")
        raw = line[start:index]
        if raw.startswith("#"):
            raise HelpError("Help is unavailable inside shell comments.", "comment_context")
        try:
            value = shlex.split(raw, posix=True)[0]
        except (ValueError, IndexError) as error:
            raise HelpError("The command contains an unsupported shell word.", "unsupported_shell_syntax") from error
        tokens.append(Token(start, index, value))
    return tokens


def find_context(line: str, point: int, profiles: list[dict], discover=None, driver_registry=None,
                 observe=None) -> Context:
    """Resolve the longest literal command profile and the editable option span.

    Bash's bind -x interface exposes character offsets in a UTF-8 locale,
    rather than the byte offsets used internally by the Readline library.
    An optional observer receives resolved path and invocation metadata before
    lookup, allowing passive reports to reuse parsing without receiving operands.
    """
    if not 0 <= point <= len(line):
        raise HelpError("The cursor offset is outside the command line.", "invalid_cursor")
    try:
        line.encode("utf-8")
    except UnicodeError as error:
        raise HelpError("The command line must contain valid UTF-8 text.", "invalid_encoding") from error
    tokens = tokenize(line)
    if not tokens:
        raise HelpError("Type a supported command followed by a space first.", "command_required")
    # Validate the editable position before permitting any discovery subprocess.
    if point <= tokens[0].end:
        raise HelpError("Move the cursor after the command or subcommand and a space.", "cursor_before_arguments")
    active = next((token for token in tokens if token.start <= point <= token.end), None)
    start, end = (active.start, active.end) if active else (point, point)
    query = active.value if active else ""
    if active and "=" in query:
        raise HelpError("Move the cursor outside the attached option value.", "cursor_in_value")
    words = [token.value for token in tokens if token.end <= start]
    driver_registry = load_driver_registry() if driver_registry is None else driver_registry
    try:
        invocation = resolve_invocation(words)
        executable_name = Path(tokens[invocation.executable_index].value).name
        if (not re.fullmatch(r"[A-Za-z0-9_.+][A-Za-z0-9_.+-]*", executable_name) or executable_name in {".", ".."}):
            # Explicit static definitions retain their literal command names.
            # Unrecognized option-looking words must not become diagnostic
            # command names, because they can contain attached secret values.
            if not any(profile["command"][0] == executable_name for profile in profiles):
                raise HelpError("Use a literal executable name before opening help.", "invalid_executable")
        target_words = [invocation.name, *words[invocation.argument_start:]]
        target_registry = ({invocation.module: module_driver(invocation.module)}
                           if invocation.module else driver_registry)
        path = resolve_path(target_words, [] if invocation.module else
                            [tuple(profile["command"]) for profile in profiles], target_registry)
    except HelpError:
        raise
    except ValueError as error:
        raise HelpError(str(error)) from error
    argument_start = invocation.argument_start + path.argument_start - 1
    profile_path = path.words
    if invocation.module:
        # Explicit interpreter/module profiles are separate from ordinary pip
        # profiles; a different pip executable must never supply this context.
        profile_path = (Path(tokens[invocation.executable_index].value).name, "-m", *path.words)
    resolved_driver = target_registry.get(path.words[0])
    resolved_route = resolved_driver.paths.get(path.words[1:]) if resolved_driver else None
    scoped_values = (resolved_driver.global_values if resolved_driver and len(path.words) == 1
                     else resolved_route.option_values if resolved_route else ())
    scoped_flags = (resolved_driver.global_flags if resolved_driver and len(path.words) == 1
                    else resolved_route.option_flags if resolved_route else ())
    if (active and query not in scoped_values and query not in scoped_flags
            and any(len(flag) == 2 and query.startswith(flag) and len(query) > len(flag) for flag in scoped_values)):
        # Driver arity remains authoritative even when help parsing has not
        # marked a short parent/global option's attached argument explicitly.
        raise HelpError("Move the cursor outside the attached option value.", "cursor_in_value")
    if observe is not None:
        # Passive diagnostics share the exact resolver; only the resolved path
        # and invocation identity leave this boundary, never pending operands.
        observe(path.words, profile_path, invocation)
    matches = [profile for profile in profiles if tuple(profile["command"]) == profile_path]
    if active and not query.startswith("-") and not (query and any(
        option.get("kind") == "keyword" and option["flag"].startswith(query)
        for profile in matches for category in profile["categories"] for option in category["options"]
    )):
        raise HelpError("Move the cursor to an empty argument or an option name, or a documented keyword.", "cursor_in_operand")
    if matches and matches[0].get("identity"):
        if discover is None:
            raise HelpError("This profile requires executable identity verification through discovery.")
        discover(tokens[invocation.executable_index].value, subcommands=path.words[1:])
    if not matches and discover is not None:
        # Only the executable and a recognized documentation path cross this
        # boundary. Pending global options, values, and action arguments do not.
        executable = tokens[invocation.executable_index].value
        if invocation.module:
            matches = [discover(executable, subcommands=path.words[1:], module=invocation.module,
                                interpreter_options=invocation.interpreter_options)]
        else:
            matches = [discover(executable, subcommands=path.words[1:]) if len(path.words) > 1
                       else discover(executable)]
    if not matches:
        raise HelpError("No matching help profile. Use --list-commands to list profiles.", "profile_missing")
    profile = max(matches, key=lambda item: len(item["command"]))
    command_end = tokens[argument_start - 1].end
    if point <= command_end:
        raise HelpError("Move the cursor after the command or subcommand and a space.", "cursor_before_arguments")
    previous = [token.value for token in tokens[argument_start:] if token.end <= start]
    options = {option["flag"].rstrip("="): option for category in profile["categories"] for option in category["options"]}
    # Explicit route arity also protects operands omitted from leaf help, such
    # as kubectl's inherited namespace. These entries validate context only;
    # they do not create undocumented browser selections or override profiles.
    if resolved_route:
        for flag in resolved_route.option_values:
            options.setdefault(flag, {"argument": "VALUE", "attached": len(flag) == 2})
        for flag in resolved_route.option_flags:
            options.setdefault(flag, {"argument": ""})
    if active:
        keyword_match = bool(query) and any(option.get("kind") == "keyword" and option["flag"].startswith(query) for option in options.values())
        if "=" in query or not (query.startswith("-") or keyword_match):
            raise HelpError("Move the cursor to an empty argument, an option name, or a documented keyword.", "cursor_in_operand")
        # A joined payload is a real value, never an editable flag prefix.
        if query not in options and any((option.get("attached") or len(key) == 2 and option.get("argument"))
               and query.startswith(key) and len(query) > len(key)
               for key, option in options.items()):
            raise HelpError("Move the cursor outside the attached option value.", "cursor_in_value")
        if query not in options:
            parsed = option_tokens(query, options, strict=False)
            if parsed:
                raise HelpError("Move to an empty argument; an existing bundle or attached payload cannot be replaced.", "cursor_in_bundle")
    values_remaining = 0
    strict_value = False
    optional_integer_pending = False
    driver = driver_registry.get(path.words[0])
    route = driver.paths.get(path.words[1:]) if driver else None
    stop_at_positional = profile.get("stop_at_positional", False) or route is not None and route.stop_at_positional
    boundary_options = set(profile.get("stop_at_options", [])) | set(route.stop_at_options if route else ())
    group = profile.get("positional_group")
    group_values = 0
    for word in previous:
        if optional_integer_pending:
            optional_integer_pending = False
            # Only an explicitly typed optional integer can consume a separate
            # token. Other optional values retain the conservative boundary.
            if re.fullmatch(r"[0-9]+", word):
                continue
        if group_values:
            # An option-looking file cannot complete an esptool-style positional
            # pair: quoting does not hide its leading dash from the target CLI.
            if word.startswith("-"):
                raise HelpError("Complete the repeated positional argument group before an option or -- marker.", "positional_group_incomplete")
            group_values = (group_values + 1) % group["argument_count"]
            continue
        if values_remaining:
            if strict_value and (not word or word.startswith("-") and not re.fullmatch(r"-[0-9]+(?:\.[0-9]+)?", word)):
                raise HelpError("Complete the declared value; attach dash-leading nonnumeric values explicitly.", "option_value_required")
            values_remaining -= 1
            continue
        if word == "--":
            raise HelpError("Options cannot be inserted after the -- end-of-options marker.", "end_of_options")
        if word.partition("=")[0] in boundary_options:
            raise HelpError("Options cannot be inserted after this command's child-argument boundary.", "child_argument_boundary")
        key, equal, _ = word.partition("=")
        if invocation.module == "pip" and key == "--python":
            raise HelpError("pip --python changes the interpreter; this module form is unsupported.")
        parsed = option_tokens(word, options)
        option = parsed[-1][1] if parsed else {}
        attached = parsed[-1][2] if parsed else False
        if any(name in boundary_options for name, _, _ in parsed):
            raise HelpError("Move before the declared child-argument boundary.", "child_argument_boundary")
        if group and not option and not word.startswith("-"):
            group_values = 1
            continue
        if group and not option:
            raise HelpError("An unrecognized option makes the structured argument position ambiguous.", "unsupported_option")
        if stop_at_positional:
            if not word.startswith("-") and option.get("kind") != "keyword":
                raise HelpError("Move the cursor before the first positional argument to insert this command's options.", "child_argument_boundary")
            if not option:
                raise HelpError("An unrecognized option or short-option bundle makes the argument position ambiguous.", "unsupported_option")
        if option.get("argument") and not option.get("argument_optional", False):
            values_remaining = max(0, option.get("argument_count", 1) - int(bool(equal) or attached))
            strict_value = bool(option.get("argument_style") or len(parsed) > 1)
        optional_integer_pending = option.get("optional_value_kind") == "nonnegative_integer" and not (equal or attached)
    if values_remaining:
        raise HelpError("Enter the preceding option's argument before choosing another option.", "option_value_required")
    if optional_integer_pending and active and re.fullmatch(r"[0-9]+", query):
        raise HelpError("Move the cursor outside the optional integer argument.", "cursor_in_value")
    if group_values:
        raise HelpError("Complete the repeated positional argument group before choosing an option.", "positional_group_incomplete")
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
    if option.get("argument_style") == "equals" and not flag.endswith("="):
        flag += "="
    suffix = context.line[context.end:]
    has_separator = bool(suffix) and suffix[0] in " \t"
    joined = flag.endswith("=") or option.get("argument_style") == "attached_only"
    separator = "" if joined or has_separator else " "
    replacement = flag + separator
    line = context.line[:context.start] + replacement + suffix
    point = context.start + len(replacement)
    if not joined and not separator and has_separator:
        point += 1
    return line, point
