"""Unit labels for already validated menu forms. Input tokens always retain their literal spelling."""
from decimal import Decimal
import json
import re

from value_semantics import _unit_text, _explain_node


_TIME = {"0.000000001": ("ns", "nanosecond"), "0.000001": ("µs", "microsecond"),
         "0.001": ("ms", "millisecond"), "1": ("s", "second"), "60": ("min", "minute"),
         "3600": ("h", "hour"), "86400": ("days", "day")}
_BIT_NAMES = {"bps", "b/s", "bit/s", "bits/s", "bits/second", "bit per second", "bits per second"}
_RATE_PROSE = re.compile(r"(?<![a-zA-Z_/])(?:(?i:(?:kilo|mega|giga|tera|k|m|g|t)?bits?)\s*(?:/\s*(?:s|sec(?:ond)?s?)|per\s+seconds?)|(?:[kMGT])?(?:bps|b/s))\b")


def unit_label(unit, node):
    """Return a compact meaning for one input magnitude and its exact-case search aliases."""
    base, factor = unit.get("base"), unit.get("multiplier")
    rate = unit.get("per") == "second"
    aliases = set()
    if base in {"byte", "bit"}:
        symbol = "B" if base == "byte" else "bit"
        label = (("bps" if base == "bit" else "B/s") if rate else symbol)
        if rate and base == "bit":
            aliases.update(_BIT_NAMES)
        if rate and base == "byte":
            aliases.update(("B/s", "bytes/s", "bytes per second"))
        aliases.update((label, base, base + "s") if not rate else (label,))
        for power, names in enumerate(zip(("k", "M", "G", "T", "P", "E"),
                                          ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei")), 1):
            for radix, prefix in zip((1000, 1024), names):
                if factor == str(radix ** power):
                    meaning = prefix + label
                    long = (("kilo", "mega", "giga", "tera", "peta", "exa") if radix == 1000 else
                            ("kibi", "mebi", "gibi", "tebi", "pebi", "exbi"))[power-1] + base
                    suffix = " per second" if rate else ""
                    return meaning, aliases | {meaning, long + suffix, long + "s" + suffix}
        return (label if factor == "1" else f"{factor} {label}"), aliases
    if base == "second" and factor in _TIME and not rate:
        label, name = _TIME[factor]
        aliases.update((name, name + "s", label))
        if label == "µs":
            aliases.update(("us", "μs"))
        return label, aliases
    if base == "hertz" and not rate:
        frequency = Decimal(factor)
        aliases.update(("Hz", "hertz"))
        if "frame rate" in node.get("meaning", "").lower():
            return ("fps" if frequency == 1 else f"{frequency:f} fps"), aliases | {"fps", "frames per second"}
        # Decimal input may exceed Python's integer-string limit. Scale the exact
        # digits directly so large valid profiles still open without rounding.
        whole, _, fraction = format(frequency, "f").partition(".")
        if not fraction.strip("0"):
            for zeros, label, name in ((6, "MHz", "megahertz"), (3, "kHz", "kilohertz")):
                if len(whole) > zeros and whole.endswith("0" * zeros):
                    return f"{whole[:-zeros]} {label}", aliases | {label, name}
        return ("Hz" if frequency == 1 else f"{frequency:f} Hz"), aliases
    if base == "ratio" and factor == "0.01" and unit.get("relative_to") and not rate:
        return "% of " + unit["relative_to"], {"%", "percent", "percentage"}
    if base == "degree" and factor == "1" and not rate:
        return "°", {"°", "degrees", "degree"}
    if base == "custom" and unit.get("name") == "operation" and rate and factor == "1":
        return "IOPS", {"IOPS", "i/o operations per second"}
    label = _unit_text(unit)
    return label, {label} if base else set()


def unit_index(nodes):
    """Collect aliases and a conservative bare-unit group key from active variants and components."""
    aliases = set()
    group = ()
    for node in nodes:
        for form in node.get("forms") or ():
            unit = form.get("unit") or {}
            if not unit.get("base") or not unit.get("multiplier"):
                continue
            label, words = unit_label(unit, node)
            aliases.update(words)
            if (len(nodes) == 1 and (node.get("review") or {}).get("status") == "verified"
                    and node.get("bare") == {"state": "accepted", "form": form["id"]}
                    and node["kind"] in {"quantity", "duration"}):
                group = (label, json.dumps(unit, sort_keys=True), json.dumps(node.get("applicability"), sort_keys=True),
                         node.get("subject", ""))
        for component in node.get("components") or ():
            aliases.update(unit_index((component["semantics"],))[0])
    return frozenset(aliases), group


# Match explicit unit words in imported prose. These are search aliases only.
_PROSE_UNITS = {"nanosecond": "ns", "microsecond": "µs", "millisecond": "ms", "second": "s",
                "minute": "min", "hour": "h", "kilohertz": "kHz", "megahertz": "MHz",
                "hertz": "Hz", "degree": "°", "percent": "%", "percentage": "%",
                "frames per second": "fps", "i/o operations per second": "IOPS",
                "bytes per second": "B/s", "bytes/second": "B/s"}
for prefix, symbol in (("kilo", "k"), ("mega", "M"), ("giga", "G"), ("tera", "T"),
                       ("kibi", "Ki"), ("mebi", "Mi"), ("gibi", "Gi"), ("tebi", "Ti")):
    _PROSE_UNITS[prefix + "byte"] = symbol + "B"
    _PROSE_UNITS[prefix + "bytes per second"] = symbol + "B/s"
_WORD_UNITS = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(_PROSE_UNITS, key=len, reverse=True))
                         + r")s?\b", re.I)

# Only these queries require scanning prose for additional (nonliteral) matches.
PROSE_ALIAS_QUERIES = frozenset(_BIT_NAMES | set(_PROSE_UNITS.values()))



def search_alias(query):
    """Fold spelled-out unit names while keeping case-sensitive symbols such as B/s intact."""
    folded = query.casefold()
    if " " in folded or folded.removesuffix("s") in _PROSE_UNITS:
        return folded
    return query


def prose_aliases(text):
    """Index explicit operational unit expressions without inferring an input grammar."""
    aliases = set(_BIT_NAMES) if _RATE_PROSE.search(text) else set()
    for match in _WORD_UNITS.finditer(text):
        aliases.add(_PROSE_UNITS[match.group(1).lower()])
    return aliases


def expanded_rules(nodes):
    """Render the full active rules with conversions scoped to each variant or component."""
    result = []
    for i, node in enumerate(nodes, 1):
        title = f"Value variant {i}" if len(nodes) > 1 else "Value"
        result.extend(_expanded_node(node, title))
    return tuple(result)


def _expanded_node(node, title):
    """Compact input forms while retaining bounds, token case, special values and applicability."""
    forms = node.get("forms") or []
    # Reuse the formatter for non-form rules (including special defaults).
    lines = _explain_node({**node, "components": []}, title, presentation=True)
    forms_display = []
    notes = []
    table = len(forms) > 1 and all((f.get("unit") or {}).get("base") == "bit"
                                   and f["unit"].get("per") == "second" and f["unit"].get("multiplier") for f in forms)
    if table:
        forms_display.append("Input             Result (bps)")
    for form in forms:
        syntax = form.get("syntax") or form["id"]
        tokens = form.get("tokens", [])
        if form["notation"] == "suffix" and syntax.startswith("N") and tokens:
            syntax = " or ".join("N" + token for token in tokens)
        elif tokens and tokens != [syntax]:
            syntax += " (" + ", ".join(tokens) + ")"
        unit = form.get("unit")
        if table:
            factor = Decimal(unit["multiplier"])
            value = "N" if factor == 1 else f"N × {factor:,f}"
            forms_display.append(f"{syntax:<18}{value}" if len(syntax) < 18 else f"{syntax}  {value}")
        else:
            label = unit_label(unit, node)[0] if unit and unit.get("base") and unit.get("multiplier") else ""
            forms_display.append("Input " + syntax + (" · " + label if label else ""))
        for key in ("meaning", "grammar"):
            if form.get(key):
                notes.append((syntax, form[key]))
        if form.get("case") in ("sensitive", "insensitive", "unverified"):
            notes.append((syntax, "Token case unverified." if form["case"] == "unverified" else "Tokens are case " + form["case"] + "."))
        bounds = form.get("bounds") or {}
        if bounds:
            low = "[" if "min" in bounds and bounds.get("min_inclusive", True) else "("
            high = "]" if "max" in bounds and bounds.get("max_inclusive", True) else ")"
            notes.append((syntax, f"Range {low}{bounds.get('min', '-infinity')}, {bounds.get('max', '+infinity')}{high}."))
        if unit and not (unit.get("base") and unit.get("multiplier")):
            notes.append((syntax, "Unit/scale not verified. " + (unit.get("reason") or "")))
        if not unit and node["kind"] in {"quantity", "duration"} and not form.get("sentinel"):
            notes.append((syntax, "Unit/scale not verified."))
    grouped = {}
    for syntax, note in notes:
        grouped.setdefault(note, []).append(syntax)
    for note, syntaxes in grouped.items():
        forms_display.append(", ".join(dict.fromkeys(syntaxes)) + ": " + note)
    rest = []
    for line in lines:
        if line.startswith(("Input ", "Evidence:", "Investigation:", "Reference:", "Source qualification:")):
            continue
        if line.startswith("Delegated grammar:"):
            line = line.partition(";")[0] + "."
        rest.append(line)
    # A variant or component heading precedes the forms it qualifies.
    if title != "Value" or not table:
        forms_display[:0] = rest[:1]
        rest = rest[1:]
    forms_display.extend(rest)
    for component in node.get("components") or ():
        heading = f"Component {component['id']} (token slot {component['slot']}, "
        heading += ("required" if component.get("required") else "optional") + ")"
        forms_display.extend(_expanded_node(component["semantics"], heading))
    return forms_display
