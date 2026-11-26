"""Interpret declared value forms and opt-in short bundles without shell evaluation."""

from errors import HelpError


VALUE_STYLES = {"separate", "equals", "attached", "attached_only"}


def value_forms(option):
    """Return accepted spellings; absent metadata preserves the legacy grammar."""
    style = option.get("argument_style")
    if style:
        return {"separate": {"separate"}, "equals": {"equals"},
                "attached": {"separate", "attached"}, "attached_only": {"attached"}}[style]
    return {"separate", "equals"} | ({"attached"} if option.get("attached") else set())


def _seven_zip_tokens(word, options, strict):
    """Resolve the longest ASCII switch name before interpreting its attached suffix."""
    if not word.startswith("-"):
        return []
    # Compare only the name. Paths and passwords can contain case-sensitive
    # text, Unicode or an equals sign as their first literal character.
    def matches(key, option):
        if key == "--":
            return word == "--"
        # A declared method property ending in '=' owns that spelling.
        # A joined native property such as -mmemuse2g still belongs to -m.
        literal = option.get("flag", key)
        prefix = word[:len(literal)]
        return (prefix.isascii() and prefix.lower() == literal.lower()
                or word.isascii() and word.lower() == key.lower())

    name = max((key for key, option in options.items() if matches(key, option)), key=len, default=None)
    if name is None:
        if not strict:
            return []
        raise HelpError("Unrecognized extraction switch.", "unsupported_option")
    option = options[name]
    suffix = word[len(name):]
    if not suffix:
        if option.get("argument") and not option.get("argument_optional"):
            raise HelpError("Complete the switch's attached value.", "option_value_required")
    elif option.get("argument_style") == "equals":
        if not suffix.startswith("="):
            raise HelpError("Use the declared equals spelling.", "unsupported_value_form")
        if len(suffix) == 1 and not option.get("argument_optional"):
            raise HelpError("Complete the attached argument.", "option_value_required")
    elif not option.get("argument") or "attached" not in value_forms(option):
        raise HelpError("This extraction switch does not take a suffix.", "unsupported_value_form")
    return [(name, option, bool(suffix))]


def _ffmpeg_tokens(word, options, strict, *, partial_inventory=False):
    """Resolve FFmpeg option arity while leaving file paths and stream specifiers opaque."""
    if word == "-" or not word.startswith("-"):
        return []
    if word in options:
        return [(word, options[word], False)]
    # FFmpeg has no short bundles or attached payloads. A partial option
    # at the cursor, including a search with no matches yet, can be replaced.
    if not strict:
        return []
    # A file-loaded value and a stream-qualified value consume the same number
    # of arguments as the declared base option. The client validates the scope.
    name = word.replace("-/", "-", 1) if word.startswith("-/") else word
    base = name.split(":", 1)[0]
    if base in options and "=" not in base:
        return [(base, options[base], False)]
    if partial_inventory:
        return []  # A fixed discovery response may omit a valid advanced option.
    raise HelpError("Unknown FFmpeg option or operand spelling.", "unsupported_option")


def option_tokens(word, options, strict=True, *, switch_syntax=None, partial_inventory=False):
    """Return (name, metadata, payload-present) entries for one completed token.

    Exact names win. Bundles require every member to opt in; a value member
    terminates the bundle. Multiple possible interpretations are rejected.
    No payload text is retained in the result or included in errors.
    """
    if switch_syntax == "7zip":
        return _seven_zip_tokens(word, options, strict)
    if switch_syntax == "ffmpeg":
        return _ffmpeg_tokens(word, options, strict, partial_inventory=partial_inventory)
    key, equal, payload = word.partition("=")
    if word in options or equal and key in options:
        option = options.get(word, options.get(key))
        if equal and not option.get("argument") and any(item.get("bundle") or item.get("argument_style") for item in options.values()):
            raise HelpError("This declared flag has no value form.", "unsupported_value_form")
        if option.get("argument") and option.get("argument_style"):
            if not equal and option.get("argument_optional"):
                return [(key, option, False)]
            form = "equals" if equal else "separate"
            if form not in value_forms(option):
                raise HelpError("Use the declared argument spelling; attached-only values must share the option token.",
                                "option_value_required" if option.get("argument_style") == "attached_only" else "unsupported_value_form")
            if equal and not payload and not option.get("argument_optional"):
                raise HelpError("Complete the attached argument before another option.", "option_value_required")
        return [(key, option, bool(equal))]
    # Some commands spell a count directly as -NUMBER. Exact flags above
    # retain priority (for example a literal -1), and no following word is consumed.
    if word.startswith("-") and word[1:].isascii() and word[1:].isdigit():
        for name, option in options.items():
            if option.get("numeric_shorthand"):
                return [(name, option, True)]
    attached = [[(name, option, True)] for name, option in options.items()
                if option.get("argument") and "attached" in value_forms(option)
                and word.startswith(name) and len(word) > len(name)]
    bundled = []
    rejected_value_form = None
    enabled = any(option.get("bundle") for option in options.values())
    if enabled and word.startswith("-") and not word.startswith("--") and len(word) > 2:
        for index, char in enumerate(word[1:], 1):
            name = "-" + char
            option = options.get(name, {})
            if not option.get("bundle"):
                bundled = []
                break
            remainder = word[index + 1:]
            if option.get("argument"):
                form = "attached" if remainder else "separate"
                if form not in value_forms(option):
                    rejected_value_form = "unsupported_value_form" if remainder else "option_value_required"
                    bundled = []
                    break
                bundled.append((name, option, bool(remainder)))
                break
            bundled.append((name, option, False))
    candidates = attached + ([bundled] if bundled else [])
    # A one-member value bundle is the same spelling as ordinary attachment.
    unique = {tuple((name, payload) for name, _, payload in entries): entries for entries in candidates}
    if len(unique) > 1:
        raise HelpError("The short token has ambiguous declared interpretations; use separate options.", "ambiguous_short_token")
    if unique:
        return next(iter(unique.values()))
    if rejected_value_form:
        raise HelpError("Complete the bundle's value using its declared spelling, or enter the options separately.", rejected_value_form)
    declared_forms = any(option.get("argument_style") for option in options.values())
    if (enabled or declared_forms) and word.startswith("-") and (strict or not word.startswith("--") and len(word) > 2):
        # Only the active token can be an incomplete single-dash option name.
        # An unknown member after a declared bundle starter still makes it opaque.
        if not strict and not options.get(word[:2], {}).get("bundle") and any(name.startswith(word) for name in options):
            return []
        raise HelpError("An undeclared option or bundle member makes argument arity unknown.", "unsupported_option")
    return []
