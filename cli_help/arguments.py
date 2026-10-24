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


def option_tokens(word, options, strict=True):
    """Return (name, metadata, payload-present) entries for one completed token.

    Exact names win. Bundles require every member to opt in; a value member
    terminates the bundle. Multiple possible interpretations are rejected.
    No payload text is retained in the result or included in errors.
    """
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
        raise HelpError("An undeclared option or bundle member makes argument arity unknown.", "unsupported_option")
    return []
