"""Opt-in descriptive value contracts, diagnostics, and plain-text explanations.

The APIs inspect supplied dictionaries, including read-only browser presentation;
they do not read files, validate pending operands, resolve programs, or perform
I/O. See docs/numerical-value-contract.md for the version 1 data contract.
"""

from dataclasses import asdict, dataclass, replace
from decimal import Decimal, InvalidOperation
import json
import re


MODES = {"structural", "maintained", "external"}
KINDS = {
    "quantity", "count", "identifier", "index", "level", "enumeration",
    "duration", "timestamp", "duration_expression", "composite", "delegated",
    "nonnumerical", "unresolved",
}
NOTATIONS = {"number", "suffix", "prefix", "literal", "expression"}
BASE_UNITS = {
    "second", "bit", "byte", "metre", "hertz", "ratio", "row", "column",
    "cell", "code_point", "baud", "degree", "kelvin", "custom",
}
FACETS = ("implementation", "version", "platform", "chip")
NODE_FIELDS = {
    "kind", "meaning", "review", "applicability", "bare", "forms", "subject",
    "origin", "ordering", "time_basis", "grammar", "components", "slots",
    "when_absent", "when_value_omitted", "investigation",
}
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z")
VERSION = re.compile(r"[0-9]+(?:\.[0-9]+)*\Z")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.-]*\Z")


@dataclass(frozen=True)
class ValueContext:
    """Locate supplied metadata and optionally check its declared token arity.

    argument_count=None leaves arity unknown; zero describes a fixed flag.
    value_optional=None leaves omission of an operand unknown. These values
    describe existing declarations and never change command consumption.
    """

    source: str = "<memory>"
    command: tuple[str, ...] = ()
    option: str = "<value>"
    pointer: str = "/value_semantics"
    component: tuple[str, ...] = ()
    argument_count: int | None = None
    value_optional: bool | None = None


@dataclass(frozen=True)
class Diagnostic:
    """An actionable, stable-code finding with a JSON-pointer source locator."""

    code: str
    severity: str
    source: str
    pointer: str
    command: tuple[str, ...]
    option: str
    component: tuple[str, ...]
    message: str

    def to_dict(self):
        """Return JSON-compatible data without writing a report."""
        result = asdict(self)
        result["command"] = list(self.command)
        result["component"] = list(self.component)
        return result


class ValueSemanticsError(ValueError):
    """Formatting was requested for structurally invalid metadata."""

    def __init__(self, diagnostics):
        self.diagnostics = tuple(diagnostics)
        super().__init__("; ".join(f"{d.code}: {d.message}" for d in diagnostics))


def _pointer(parent, part):
    return parent + "/" + str(part).replace("~", "~0").replace("/", "~1")


def _number(value):
    """Parse metadata constants only, using finite exact decimal arithmetic."""
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _special_key(value, form):
    """Normalize only declared metadata special values, respecting form case."""
    if form.get("notation") in {"number", "suffix", "prefix"}:
        return _number(value)
    if isinstance(value, str):
        return value.casefold() if form.get("notation") == "literal" and form.get("case") == "insensitive" else value
    return None


def _version(value):
    """Compare dotted numeric releases without inferring prerelease ordering."""
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        return None
    try:
        parts = tuple(int(part) for part in value.split("."))
    except ValueError:
        return None
    while len(parts) > 1 and parts[-1] == 0:
        parts = parts[:-1]
    return parts


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and all(c.isprintable() for c in value)


def _ordered(diagnostics):
    return tuple(sorted(set(diagnostics), key=lambda d: (
        d.source, d.pointer, d.command, d.option, d.component, d.code, d.severity, d.message)))


def _meaning_key(value, omit_scope=False):
    """Compare declarations conservatively, ignoring evidence and optional scope.

    Child applicability remains part of a composite's meaning. Ignoring the
    variant's own scope is appropriate only when comparing overlapping variants.
    """
    if isinstance(value, dict):
        return {key: _meaning_key(item) for key, item in value.items()
                if key != "review" and not (omit_scope and key == "applicability")}
    if isinstance(value, list):
        return [_meaning_key(item) for item in value]
    return value


def _overlap(left, right):
    """Return false only when applicability sets are provably disjoint.

    Unknown/irrelevant/all scopes overlap conservatively. Numeric version
    intervals are half-open; opaque release names support exact sets only.
    """
    left, right = left or {}, right or {}
    for facet in FACETS:
        a, b = left.get(facet) or {}, right.get(facet) or {}
        if a.get("state") != "known" or b.get("state") != "known":
            continue
        if facet != "version":
            if set(a["values"]).isdisjoint(b["values"]):
                return False
            continue
        av, bv = a.get("values"), b.get("values")
        if av is not None and bv is not None:
            normalize = lambda x: _version(x) or x
            if {normalize(x) for x in av}.isdisjoint(normalize(x) for x in bv):
                return False
        elif av is not None or bv is not None:
            values, interval = (av, b) if av is not None else (bv, a)
            parsed = [_version(v) for v in values]
            if all(v is not None for v in parsed):
                low, high = _version(interval.get("min")), _version(interval.get("before"))
                if not any((low is None or v >= low) and (high is None or v < high) for v in parsed):
                    return False
        else:
            amin, amax = _version(a.get("min")), _version(a.get("before"))
            bmin, bmax = _version(b.get("min")), _version(b.get("before"))
            if (amax is not None and bmin is not None and amax <= bmin
                    or bmax is not None and amin is not None and bmax <= amin):
                return False
    return True


class _Validator:
    """One recursive implementation for all public validation entry points."""

    def __init__(self, mode, context, definitions):
        if mode not in MODES:
            raise ValueError(f"Validation mode must be one of {sorted(MODES)}")
        self.mode, self.context = mode, context
        self.diagnostics = []
        self.incomplete_paths = []
        self.structural_errors = 0
        self.definitions = definitions if isinstance(definitions, dict) else {}
        if definitions is not None and not isinstance(definitions, dict):
            self.issue("sem_type", "/value_definitions", "Supply a mapping of shared definition names to nodes.")

    def issue(self, code, path, message, *, incomplete=False):
        """Record policy-specific incompleteness separately from contradictions."""
        if incomplete:
            self.incomplete_paths.append(path)
        else:
            self.structural_errors += 1
        if incomplete and self.mode == "structural":
            return
        severity = "warning" if incomplete and self.mode == "external" else "error"
        c = self.context
        self.diagnostics.append(Diagnostic(code, severity, c.source, path, c.command,
                                           c.option, c.component, message))

    def obj(self, value, path, fields):
        if not isinstance(value, dict):
            self.issue("sem_type", path, "Supply an object with documented fields.")
            return False
        for field in sorted(set(value) - fields, key=str):
            self.issue("sem_field", _pointer(path, field), "Remove the unsupported field or use a documented field.")
        return True

    def text(self, value, path, required=False):
        if value is None:
            if required:
                self.issue("sem_incomplete", path, "Document this value's specific meaning.", incomplete=True)
        elif not _text(value):
            self.issue("sem_text", path, "Supply nonempty single-line text without control characters.")

    def texts(self, value, path):
        if not isinstance(value, list) or not value or any(not _text(x) for x in value):
            self.issue("sem_type", path, "Supply a nonempty list of nonempty strings.")
            return False
        if len(set(value)) != len(value):
            self.issue("sem_duplicate", path, "Remove duplicate spellings or scope values.")
        return True

    def enum(self, value, path, choices):
        if not isinstance(value, str) or value not in choices:
            self.issue("sem_choice", path, f"Select one of {', '.join(sorted(choices))}.")
            return False
        return True

    def reference(self, value, path):
        """Check a source locator without accessing or endorsing its contents."""
        if not self.obj(value, path, {"source", "locator", "note"}):
            return
        self.text(value.get("source"), path + "/source", True)
        self.text(value.get("locator"), path + "/locator", True)
        self.text(value.get("note"), path + "/note")

    def review(self, value, path):
        """Check declared evidence status, keeping synthetic sources distinct."""
        if value is None:
            self.issue("sem_review_missing", path, "Record evidence status and references.", incomplete=True)
            return None
        if not self.obj(value, path, {"status", "references", "note"}):
            return None
        status = value.get("status")
        if not self.enum(status, path + "/status", {"verified", "source_derived", "synthetic", "unresolved"}):
            return None
        references = value.get("references")
        if references is None:
            self.issue("sem_provenance_missing", path, "Identify a source and locator; synthetic sources must be labeled.", incomplete=True)
        elif not isinstance(references, list) or not references:
            self.issue("sem_type", path + "/references", "Supply a nonempty reference list.")
        else:
            for i, item in enumerate(references):
                self.reference(item, _pointer(path + "/references", i))
                if (status == "verified" and isinstance(item, dict)
                        and str(item.get("source", "")).startswith("synthetic:")):
                    self.issue("sem_false_verification", path, "Synthetic evidence cannot establish verified upstream semantics.")
        self.text(value.get("note"), path + "/note")
        if status in {"source_derived", "unresolved"}:
            self.issue("sem_review_required", path, "Verify the applicable source before treating this content as maintained numerical documentation.", incomplete=True)
        return status

    def applicability(self, value, path):
        """Check exact scopes and bounded numeric version intervals."""
        if value is None:
            self.issue("sem_applicability_missing", path, "State implementation, version, platform, and chip applicability.", incomplete=True)
            return
        if not self.obj(value, path, set(FACETS)):
            return
        for facet in FACETS:
            item, at = value.get(facet), path + "/" + facet
            if item is None:
                self.issue("sem_applicability_missing", at, "Select known, any, not_applicable, or unverified scope.", incomplete=True)
                continue
            if not self.obj(item, at, {"state", "values", "min", "before", "reason"}):
                continue
            state = item.get("state")
            if not self.enum(state, at + "/state", {"known", "any", "not_applicable", "unverified"}):
                continue
            if state != "known":
                if set(item) & {"values", "min", "before"}:
                    self.issue("sem_scope_conflict", at, "Only known scopes can declare values or version bounds.")
                if state in {"unverified", "not_applicable"}:
                    self.text(item.get("reason"), at + "/reason", True)
                if state == "unverified":
                    self.issue("sem_unverified", at, "Resolve or retain the explicit applicability uncertainty.", incomplete=True)
            elif facet == "version" and "values" not in item:
                if not ("min" in item or "before" in item):
                    self.issue("sem_scope_conflict", at, "Supply an exact version set or a numeric min/before interval.")
                for end in ("min", "before"):
                    if end in item and _version(item[end]) is None:
                        self.issue("sem_version", at + "/" + end, "Use a dotted numeric release bound; represent prereleases as exact values or unresolved scope.")
                low, high = _version(item.get("min")), _version(item.get("before"))
                if low is not None and high is not None and low >= high:
                    self.issue("sem_scope_conflict", at, "The inclusive minimum must precede the exclusive upper bound.")
            else:
                self.texts(item.get("values"), at + "/values")
                if "min" in item or "before" in item:
                    self.issue("sem_scope_conflict", at, "Do not mix exact values with version intervals; only versions support intervals.")
            self.text(item.get("reason"), at + "/reason")

    def unit(self, value, path):
        """Require explicit scale metadata or an honestly unresolved unit."""
        if not self.obj(value, path, {"base", "multiplier", "per", "name", "definition", "relative_to", "state", "reason"}):
            return
        if "state" in value:
            if value.get("state") != "unverified" or set(value) - {"state", "reason"}:
                self.issue("sem_unit_conflict", path, "Use explicit base/multiplier fields, or only state: unverified and its reason.")
            self.text(value.get("reason"), path + "/reason", True)
            self.issue("sem_unverified", path, "Verify the unit and scale; do not infer them from a suffix.", incomplete=True)
            return
        base = value.get("base")
        if base is None:
            self.issue("sem_unit_missing", path, "Specify an actual base unit, rather than size, time, speed, or number.", incomplete=True)
        else:
            self.enum(base, path + "/base", BASE_UNITS)
        factor = _number(value.get("multiplier"))
        if factor is None or factor <= 0:
            self.issue("sem_scale", path + "/multiplier", "Specify a positive exact decimal string multiplier relative to the base unit.")
        if "per" in value:
            self.enum(value["per"], path + "/per", {"second"})
        if base == "custom":
            self.text(value.get("name"), path + "/name", True)
            self.text(value.get("definition"), path + "/definition", True)
        elif "name" in value or "definition" in value:
            self.issue("sem_unit_conflict", path, "Use name/definition only with the custom base unit.")
        if base == "ratio":
            self.text(value.get("relative_to"), path + "/relative_to", True)
        elif "relative_to" in value:
            self.issue("sem_unit_conflict", path, "A relative_to basis belongs to a ratio unit.")

    def bounds(self, value, path):
        """Check a nonempty interval of metadata magnitudes, not target input."""
        if not self.obj(value, path, {"min", "max", "min_inclusive", "max_inclusive"}):
            return
        if not ("min" in value or "max" in value):
            self.issue("sem_bounds", path, "Supply at least one numeric bound, or omit bounds.")
        for end in ("min", "max"):
            if end in value and _number(value[end]) is None:
                self.issue("sem_number", path + "/" + end, "Use an exact finite decimal string for a metadata constant.")
            if end + "_inclusive" in value and (end not in value or type(value[end + "_inclusive"]) is not bool):
                self.issue("sem_bounds", path, "An inclusive flag requires the corresponding bound and a boolean.")
        low, high = _number(value.get("min")), _number(value.get("max"))
        if low is not None and high is not None and (low > high or low == high and (
                value.get("min_inclusive", True) is False or value.get("max_inclusive", True) is False)):
            self.issue("sem_bounds", path, "Declare a nonempty input-magnitude interval.")

    def form(self, value, path, kind):
        """Check accepted spellings, units, and special values for one form."""
        if not self.obj(value, path, {"id", "notation", "syntax", "tokens", "case", "unit", "meaning", "grammar", "bounds", "special_values", "sentinel"}):
            return
        if not isinstance(value.get("id"), str) or not NAME.fullmatch(value["id"]):
            self.issue("sem_id", path + "/id", "Use a stable literal form ID beginning with a letter.")
        notation = value.get("notation")
        if not self.enum(notation, path + "/notation", NOTATIONS):
            return
        if kind in {"nonnumerical", "delegated", "composite"} and notation in {"number", "suffix", "prefix"}:
            self.issue("sem_classification_conflict", path, "Use an expression grammar for this classification, or classify the scalar numerical value accurately.")
        self.text(value.get("syntax"), path + "/syntax", True)
        self.text(value.get("meaning"), path + "/meaning", notation == "literal")
        self.text(value.get("grammar"), path + "/grammar", notation == "expression")
        if "sentinel" in value and (type(value["sentinel"]) is not bool or notation != "literal"):
            self.issue("sem_form_conflict", path, "The sentinel boolean is reserved for an explicit literal exception.")
        if value.get("sentinel") is True and "unit" in value:
            self.issue("sem_unit_conflict", path, "A literal sentinel has an effect rather than a measured quantity; do not assign it a unit.")
        if kind in {"level", "enumeration"} and notation != "literal":
            self.text(value.get("grammar"), path + "/grammar", True)
        if notation in {"suffix", "prefix", "literal"}:
            self.texts(value.get("tokens"), path + "/tokens")
            tokens = value.get("tokens")
            case_matters = isinstance(tokens, list) and any(
                isinstance(t, str) and t.lower() != t.upper() for t in tokens)
            if case_matters or "case" in value:
                self.enum(value.get("case"), path + "/case", {"sensitive", "insensitive", "not_applicable", "unverified"})
            if case_matters and value.get("case") == "not_applicable":
                self.issue("sem_form_conflict", path + "/case", "Alphabetic tokens require a verified case rule or explicit uncertainty.")
            if value.get("case") == "unverified":
                self.issue("sem_unverified", path + "/case", "Verify case acceptance without inventing alternate spellings.", incomplete=True)
        elif "tokens" in value or "case" in value:
            self.issue("sem_form_conflict", path, "Tokens and case rules apply only to suffix, prefix, or literal forms.")
        if "unit" in value:
            self.unit(value["unit"], path + "/unit")
            if kind in {"identifier", "index", "level", "enumeration", "delegated", "nonnumerical", "composite"}:
                self.issue("sem_unit_conflict", path, "This classification needs meaning or component semantics rather than a measurement unit.")
            if (kind == "duration" and isinstance(value["unit"], dict) and "base" in value["unit"]
                    and (value["unit"]["base"] != "second" or "per" in value["unit"])):
                self.issue("sem_unit_conflict", path, "A scalar duration must use seconds as its base, with a suitable multiplier.")
        elif kind in {"quantity", "duration"} and value.get("sentinel") is not True:
            self.issue("sem_unit_missing", path, "Document the base unit and exact multiplier for this numerical form.", incomplete=True)
        if notation == "literal" and "unit" in value:
            # Literal quantities such as 4MB may have a unit and a described value.
            self.text(value.get("meaning"), path + "/meaning", True)
        if "bounds" in value:
            self.bounds(value["bounds"], path + "/bounds")
            if notation not in {"number", "suffix", "prefix"}:
                self.issue("sem_form_conflict", path, "Numeric bounds describe number, suffix, or prefix magnitudes only.")
        specials = value.get("special_values", [])
        if not isinstance(specials, list):
            self.issue("sem_type", path + "/special_values", "Supply a list of exact special values.")
        else:
            seen = set()
            for i, item in enumerate(specials):
                at = _pointer(path + "/special_values", i)
                if not self.obj(item, at, {"value", "meaning"}):
                    continue
                self.text(item.get("value"), at + "/value", True)
                self.text(item.get("meaning"), at + "/meaning", True)
                key = _special_key(item.get("value"), value)
                if notation in {"number", "suffix", "prefix"}:
                    if key is None:
                        self.issue("sem_number", at, "Numeric-form special values must be exact decimal strings.")
                if isinstance(key, (str, Decimal)) and key in seen:
                    self.issue("sem_special_conflict", at, "Declare each special value once with one meaning.")
                if isinstance(key, (str, Decimal)):
                    seen.add(key)

    def rule(self, value, path, forms, operand=False):
        """Check omission/default documentation against explicit form references."""
        if value is None:
            self.issue("sem_omission_missing", path, "Distinguish absent-option behavior from an omitted operand and literal values.", incomplete=True)
            return
        if not self.obj(value, path, {"state", "meaning", "reason", "form", "value"}):
            return
        state = value.get("state")
        if not self.enum(state, path + "/state", {"known", "not_accepted", "not_applicable", "unverified"}):
            return
        self.text(value.get("meaning"), path + "/meaning", state == "known" and "form" not in value)
        self.text(value.get("reason"), path + "/reason", state != "known")
        if state == "unverified":
            self.issue("sem_unverified", path, "Verify this omission rule without inventing a numeric default.", incomplete=True)
        if state != "known" and ("value" in value or "form" in value or "meaning" in value):
            self.issue("sem_default_conflict", path, "Only a known omission rule can declare a meaning or default value.")
        if ("value" in value) != ("form" in value):
            self.issue("sem_default_conflict", path, "A literal default requires both a form reference and a value.")
        if "form" in value and "meaning" in value:
            self.issue("sem_default_conflict", path, "Use a form/value reference or a descriptive meaning, rather than duplicating the default's meaning.")
        if state == "known" and "reason" in value:
            self.issue("sem_default_conflict", path, "Use meaning for a known rule; reason explains other states.")
        if "form" in value:
            form = forms.get(value["form"]) if isinstance(value["form"], str) else None
            if form is None:
                self.issue("sem_form_reference", path + "/form", "Reference a declared form ID.")
            else:
                self.default_value(value.get("value"), form, path)
        if operand and self.context.argument_count == 0 and state != "not_applicable":
            self.issue("sem_arity_conflict", path, "A fixed flag has no operand to omit; use not_applicable.")
        elif operand and self.context.argument_count is not None and self.context.argument_count > 0:
            if self.context.value_optional is False and state not in {"not_accepted", "unverified"}:
                self.issue("sem_arity_conflict", path, "The existing declaration requires an operand; use not_accepted or explicitly unverified omission semantics.")
            if self.context.value_optional is True and state not in {"known", "unverified"}:
                self.issue("sem_arity_conflict", path, "The existing declaration permits an omitted operand; describe its meaning or mark it unverified.")

    def default_value(self, value, form, path):
        """Check declared metadata defaults, never a command-line operand."""
        self.text(value, path + "/value", True)
        notation = form.get("notation")
        if not isinstance(notation, str):
            return  # The form validator already reports the malformed notation.
        if notation == "literal":
            tokens = form.get("tokens", [])
            fold = lambda x: x.casefold() if form.get("case") == "insensitive" else x
            if isinstance(tokens, list) and isinstance(value, str) and fold(value) not in [fold(t) for t in tokens if isinstance(t, str)]:
                self.issue("sem_default_conflict", path, "The default must be one of this literal form's accepted tokens.")
        elif notation in {"number", "suffix", "prefix"}:
            number = _number(value)
            if number is None:
                self.issue("sem_number", path, "Store the default magnitude as an exact decimal string, separately from its input token.")
                return
            specials = form.get("special_values", [])
            if isinstance(specials, list) and any(_special_key(s.get("value"), form) == number for s in specials if isinstance(s, dict)):
                return
            bounds = form.get("bounds", {})
            if isinstance(bounds, dict):
                low, high = _number(bounds.get("min")), _number(bounds.get("max"))
                if (low is not None and (number < low or number == low and bounds.get("min_inclusive") is False)
                        or high is not None and (number > high or number == high and bounds.get("max_inclusive") is False)):
                    self.issue("sem_default_conflict", path, "The default is outside the form's bounds and is not an explicit special value.")

    def node(self, value, path, stack=(), depth=0):
        """Validate and expand a node; references cannot override shared meaning."""
        if depth > 32:
            self.issue("sem_nesting", path, "Limit nested component/reference definitions to 32 levels.")
            return {}
        if not isinstance(value, dict):
            self.issue("sem_type", path, "Supply a semantic node or a shared ref object.")
            return {}
        if "ref" in value:
            ref = value["ref"]
            if set(value) != {"ref"}:
                self.issue("sem_reference_override", path, "A shared reference cannot override fields; declare a separate reviewed definition if meaning differs.")
            if not isinstance(ref, str) or ref not in self.definitions:
                self.issue("sem_reference", path, "Reference an existing value_definitions name.")
                return {}
            if ref in stack or len(stack) >= 32:
                self.issue("sem_reference_cycle", path, "Remove cyclic or excessively deep shared references.")
                return {}
            return self.node(self.definitions[ref], _pointer("/value_definitions", ref), (*stack, ref), depth + 1)
        if not self.obj(value, path, NODE_FIELDS):
            return {}
        incomplete_before = len(self.incomplete_paths)
        kind = value.get("kind")
        if not self.enum(kind, path + "/kind", KINDS):
            return value
        self.text(value.get("meaning"), path + "/meaning", True)
        status = self.review(value.get("review"), path + "/review")
        self.applicability(value.get("applicability"), path + "/applicability")
        for field in ("subject", "ordering", "time_basis", "investigation"):
            needed = (field == "subject" and kind in {"count", "identifier", "index"}
                      or field == "ordering" and kind == "level"
                      or field == "time_basis" and kind in {"timestamp", "duration_expression"}
                      or field == "investigation" and (kind == "unresolved" or status == "unresolved"))
            self.text(value.get(field), path + "/" + field, needed)
        if kind == "index" and "origin" not in value:
            self.issue("sem_index_origin", path + "/origin", "Specify the numeric index origin explicitly.", incomplete=True)
        elif "origin" in value:
            origin = _number(value["origin"])
            if kind != "index" or origin is None or origin != origin.to_integral_value():
                self.issue("sem_index_origin", path + "/origin", "Only indices have an origin, expressed as an exact integer string.")
        if "grammar" in value:
            grammar = value["grammar"]
            if self.obj(grammar, path + "/grammar", {"name", "reference"}):
                self.text(grammar.get("name"), path + "/grammar/name", True)
                self.reference(grammar.get("reference"), path + "/grammar/reference")
        elif kind == "delegated":
            self.issue("sem_grammar_missing", path, "Identify the owning delegated grammar and its reference; do not assign a universal unit.", incomplete=True)
        forms_list = value.get("forms")
        if forms_list is None:
            self.issue("sem_forms_missing", path, "Document accepted numerical forms or the referenced grammar.", incomplete=True)
            forms_list = []
        elif not isinstance(forms_list, list) or not forms_list:
            self.issue("sem_type", path + "/forms", "Supply a nonempty list of accepted forms.")
            forms_list = []
        forms = {}
        tokens = []
        for i, form in enumerate(forms_list):
            self.form(form, _pointer(path + "/forms", i), kind)
            if not isinstance(form, dict):
                continue
            name = form.get("id")
            if isinstance(name, str):
                if name in forms:
                    self.issue("sem_duplicate", path + "/forms", "Form IDs must be unique within a variant.")
                forms[name] = form
            if isinstance(form.get("notation"), str) and form["notation"] in {"literal", "prefix", "suffix"} and isinstance(form.get("tokens"), list):
                for token in form["tokens"]:
                    if not isinstance(token, str):
                        continue
                    for previous, old in tokens:
                        insensitive = form.get("case") in ("insensitive", "unverified") or old.get("case") in ("insensitive", "unverified")
                        same = token.casefold() == previous.casefold() if insensitive else token == previous
                        if same and old.get("notation") == form.get("notation"):
                            self.issue("sem_form_conflict", path + "/forms", "Accepted tokens overlap; describe one interpretation per token and case rule.")
                    tokens.append((token, form))
        self.bare(value.get("bare"), path + "/bare", forms)
        self.rule(value.get("when_absent"), path + "/when_absent", forms)
        self.rule(value.get("when_value_omitted"), path + "/when_value_omitted", forms, operand=True)
        expanded = dict(value)
        if kind == "composite":
            expanded["components"] = self.components(value, path, stack, depth)
        elif "components" in value or "slots" in value:
            self.issue("sem_component_conflict", path, "Only a composite node can declare components and token slots.")
        if kind == "unresolved":
            self.issue("sem_unresolved", path, "Resolve the named investigation; external browsing may retain this diagnostic.", incomplete=True)
        if status == "verified" and (self.uncertain(expanded) or len(self.incomplete_paths) > incomplete_before):
            self.issue("sem_false_verification", path + "/review", "Incomplete or unresolved semantics, unverified fields, and unverified child reviews cannot be presented as verified.")
        return expanded

    def bare(self, value, path, forms):
        """Check the ordinary scalar rule separately from literal exceptions."""
        if value is None:
            self.issue("sem_bare_missing", path, "State whether ordinary bare numbers are accepted and identify their form, or explain another state.", incomplete=True)
            return
        if not self.obj(value, path, {"state", "form", "reason"}):
            return
        state = value.get("state")
        if not self.enum(state, path + "/state", {"accepted", "not_accepted", "not_applicable", "unverified"}):
            return
        if state == "accepted":
            form = forms.get(value.get("form")) if isinstance(value.get("form"), str) else None
            if form is None or form.get("notation") != "number":
                self.issue("sem_bare_conflict", path, "Accepted bare numbers must reference a declared number form.")
        else:
            self.text(value.get("reason"), path + "/reason", True)
            if "form" in value:
                self.issue("sem_bare_conflict", path, "Only accepted bare numbers can reference a form.")
        if state == "unverified":
            self.issue("sem_unverified", path, "Verify the ordinary bare-number interpretation.", incomplete=True)
        number_forms = [f for f in forms.values() if f.get("notation") == "number"]
        if state not in {"accepted", "unverified"} and number_forms:
            self.issue("sem_bare_conflict", path, "A number form accepts ordinary bare numbers and contradicts this state.")
        if state == "accepted" and len(number_forms) != 1:
            self.issue("sem_bare_conflict", path, "Use exactly one ordinary bare-number form per applicability variant.")

    def components(self, value, path, stack, depth):
        """Map described components onto existing token slots without editing arity."""
        slots, components = value.get("slots"), value.get("components")
        if type(slots) is not int or not 1 <= slots <= 16:
            self.issue("sem_component_slots", path + "/slots", "Declare 1-16 existing token slots; joined components may share a slot.")
            slots = None
        if self.context.argument_count is not None and slots is not None and slots != self.context.argument_count:
            self.issue("sem_arity_conflict", path, "Composite slots must match existing argument_count or positional_group arity; do not change insertion metadata.")
        if not isinstance(components, list) or not components:
            self.issue("sem_components_missing", path, "Describe every relevant component and map it to an existing token slot.", incomplete=True)
            return []
        seen, covered, result = set(), set(), []
        for i, component in enumerate(components):
            at = _pointer(path + "/components", i)
            if not self.obj(component, at, {"id", "slot", "required", "semantics"}):
                continue
            name, slot = component.get("id"), component.get("slot")
            if not isinstance(name, str) or not NAME.fullmatch(name):
                self.issue("sem_id", at, "Give each component a stable literal ID.")
                name = str(i)
            if name in seen:
                self.issue("sem_duplicate", at, "Component IDs must be unique.")
            seen.add(name)
            if type(slot) is not int or slot < 1 or slots is not None and slot > slots:
                self.issue("sem_component_slots", at + "/slot", "Reference a declared 1-based token slot.")
            else:
                covered.add(slot)
            if type(component.get("required")) is not bool:
                self.issue("sem_component_required", at, "State whether this grammar component is required.", incomplete=True)
            original = self.context
            self.context = replace(original, component=(*original.component, name), argument_count=None, value_optional=None)
            child = self.node(component.get("semantics"), at + "/semantics", stack, depth + 1)
            self.context = original
            result.append({**component, "semantics": child})
        if slots is not None and covered != set(range(1, slots + 1)):
            self.issue("sem_component_slots", path, "Every declared token slot needs at least one described component.")
        return result

    @staticmethod
    def uncertain(value):
        if isinstance(value, dict):
            return (value.get("kind") == "unresolved" or value.get("state") == "unverified"
                    or isinstance(value.get("status"), str) and value["status"] in {"source_derived", "unresolved", "synthetic"}
                    or any(_Validator.uncertain(v) for v in value.values()))
        return isinstance(value, list) and any(_Validator.uncertain(v) for v in value)

    def contract(self, value):
        """Expand one contract and diagnose conflicting applicability variants."""
        structural_before = self.structural_errors
        at = self.context.pointer
        if value is None:
            self.issue("sem_metadata_missing", at, "Classify this selected value and document its numerical or explicit nonnumerical meaning.", incomplete=True)
            return []
        if not self.obj(value, at, {"schema_version", "variants"}):
            return []
        if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
            self.issue("sem_schema_version", at, "Select schema_version: 1.")
        variants = value.get("variants")
        if not isinstance(variants, list) or not variants:
            self.issue("sem_type", at + "/variants", "Supply at least one applicability variant.")
            return []
        expanded = [self.node(node, _pointer(at + "/variants", i)) for i, node in enumerate(variants)]
        # Malformed structures already have diagnostics; avoid secondary crashes.
        if self.structural_errors == structural_before:
            for i, node in enumerate(expanded):
                for previous in expanded[:i]:
                    if (_overlap(node.get("applicability", {}), previous.get("applicability", {}))
                            and _meaning_key(node, omit_scope=True) != _meaning_key(previous, omit_scope=True)):
                        self.issue("sem_variant_conflict", _pointer(at + "/variants", i),
                                   "Conflicting meanings have scopes that overlap or cannot be proved disjoint; narrow applicability or reconcile the definitions.")
        return expanded


def validate_value_semantics(metadata, *, mode="structural", context=None, definitions=None):
    """Return sorted diagnostics for supplied metadata, without side effects.

    structural permits absent/partial metadata. maintained explicitly requires
    complete reviewed documentation. external reports incompleteness as warnings;
    malformed or contradictory declarations remain errors in every mode.
    """
    validator = _Validator(mode, context or ValueContext(), definitions)
    validator.contract(metadata)
    return _ordered(validator.diagnostics)


def validate_profile_semantics(profile, source="<memory>", *, mode="structural", alias_groups=()):
    """Opt-in adapter for an otherwise structurally validated legacy profile.

    Inspect value-bearing entries, entries with explicit metadata, a positional
    group, and optional value_definitions. alias_groups explicitly names related
    flags in this profile; matching summaries never imply a relationship. This
    API does not replace core.validate_profile and is not called by its loader.
    """
    context = ValueContext(source=str(source), command=tuple(profile.get("command", ())))
    validator = _Validator(mode, context, profile.get("value_definitions"))
    for name, value in sorted(validator.definitions.items(), key=lambda item: str(item[0])):
        if not isinstance(name, str) or not NAME.fullmatch(name):
            validator.issue("sem_id", "/value_definitions", "Shared definition names must be stable literal IDs.")
        validator.node(value, _pointer("/value_definitions", name))
    entries, expanded = {}, {}
    for ci, category in enumerate(profile.get("categories", [])):
        for oi, option in enumerate(category.get("options", [])):
            flag = option["flag"]
            at = f"/categories/{ci}/options/{oi}/value_semantics"
            entries[flag] = (option, at, option.get("value_semantics"))
    if profile.get("positional_group") is not None:
        entries["<positional_group>"] = (profile["positional_group"], "/positional_value_semantics",
                                          profile.get("positional_value_semantics"))
    elif "positional_value_semantics" in profile:
        validator.issue("sem_arity_conflict", "/positional_value_semantics", "Positional semantics require an existing positional_group declaration.")
    for flag, (option, at, metadata) in entries.items():
        if not option.get("argument") and "value_semantics" not in option:
            continue
        validator.context = replace(context, option=flag, pointer=at,
                                    argument_count=option.get("argument_count", 1) if option.get("argument") else 0,
                                    value_optional=option.get("argument_optional", False))
        before = len(validator.diagnostics)
        nodes = validator.contract(metadata)
        if not any(d.severity == "error" for d in validator.diagnostics[before:]):
            expanded[flag] = nodes
    validator.context = context
    for group in alias_groups:
        validator.context = context
        if not isinstance(group, (tuple, list)) or len(group) < 2 or any(not isinstance(x, str) for x in group):
            validator.issue("sem_alias_group", "", "Each explicit alias group needs at least two literal flag names.")
            continue
        if len(set(group)) != len(group) or any(flag not in entries for flag in group):
            validator.issue("sem_alias_group", "", "Alias groups must contain distinct existing entry names.")
            continue
        first, _, _ = entries[group[0]]
        for flag in group[1:]:
            option, at, _ = entries[flag]
            arity = lambda o: (o.get("argument_count", 1) if o.get("argument") else 0, o.get("argument_optional", False))
            left, right = expanded.get(group[0]), expanded.get(flag)
            canonical = lambda nodes: sorted(json.dumps(_meaning_key(n), sort_keys=True) for n in nodes)
            if arity(first) != arity(option) or (left is not None and right is not None
                    and canonical(left) != canonical(right)):
                validator.context = replace(context, option=flag)
                validator.issue("sem_alias_conflict", at, f"Reconcile meaning, applicability, and existing arity with explicitly related entry {group[0]}.")
    return _ordered(validator.diagnostics)


def _unit_text(unit):
    """Describe actual scale without interpreting the accepted token spelling."""
    if not isinstance(unit, dict) or unit.get("base") not in BASE_UNITS or "multiplier" not in unit:
        reason = unit.get("reason") if isinstance(unit, dict) else None
        return "unit/scale not verified" + (" (" + reason + ")" if reason else "")
    base, factor = unit["base"], unit["multiplier"]
    names = {"second": "seconds", "bit": "bits", "byte": "bytes", "metre": "metres",
             "hertz": "hertz", "ratio": "of", "row": "terminal rows", "column": "columns",
             "cell": "display cells", "code_point": "Unicode code points", "baud": "baud",
             "degree": "degrees", "kelvin": "kelvin", "custom": unit.get("name") or "custom units"}
    text = names[base] if factor == "1" and base != "ratio" else f"{factor} {names[base]}"
    if base == "ratio":
        text += " " + (unit.get("relative_to") or "an unverified reference quantity")
    if unit.get("per"):
        text += "/second"
    if base == "custom":
        text += " (" + (unit.get("definition") or "definition not verified") + ")"
    return text


def _scope_text(scope):
    """Retain explicit qualifications and label unresolved applicability."""
    scope = scope or {}
    parts = []
    for facet in FACETS:
        item = scope.get(facet) or {}
        state = item.get("state")
        if state == "known":
            if "values" in item:
                detail = ", ".join(item["values"])
            else:
                detail = "; ".join(label + item[end] for end, label in (("min", ">= "), ("before", "< ")) if end in item)
            parts.append(f"{facet}: {detail}")
        elif state in {"unverified", None}:
            parts.append(f"{facet}: not verified" + (" (" + item["reason"] + ")" if item.get("reason") else ""))
    return "; ".join(parts)


def _explain_node(node, label="Value", *, presentation=False):
    """Explain one declaration, optionally placing interpretation and scope first.

    Presentation order changes emphasis only. Reference output remains compatible;
    neither mode selects applicability variants or interprets pending operands.
    """
    kind = node["kind"]
    forms = node.get("forms") or []
    bare = node.get("bare") or {}
    first = f"{label}: {node.get('meaning') or 'meaning not documented'}"
    meaning_first = first
    if bare.get("state") == "accepted":
        form = next(f for f in forms if f["id"] == bare["form"])
        subject = node.get("subject") or node.get("meaning") or "meaning not documented"
        if kind == "count":
            subject = "count of " + subject
        elif kind == "identifier":
            subject = "identifier for " + subject
        elif kind == "index":
            subject = "index into " + subject
        first += "; bare numbers: " + (_unit_text(form.get("unit")) if kind in {"quantity", "duration"} or "unit" in form
                                       else subject)
    elif bare.get("state") == "not_accepted":
        first += "; ordinary bare numbers not accepted"
    elif bare.get("state") in {None, "unverified"}:
        first += "; bare-number meaning not verified"
    if kind == "unresolved":
        first += "; unresolved"
    scope = _scope_text(node.get("applicability"))
    status = (node.get("review") or {}).get("status", "not documented").replace("_", " ")
    if presentation:
        meaning = meaning_first[len(label) + 2:]
        interpretation = first[len(meaning_first):].removeprefix("; ")
        qualification = []
        if status != "verified":
            qualification.append(status)
        if scope:
            qualification.append("scoped")
        if qualification:
            label += " (" + "; ".join(qualification) + ")"
        first = label + ": " + (interpretation + "; " if interpretation else "") + meaning
    lines = [first + "."]
    if presentation:
        if scope:
            lines.append("Applies to: " + scope + ". Matching to an installed target is not established here.")
        lines.append("Evidence: " + status + ".")
        if node.get("investigation"):
            lines.append("Investigation: " + node["investigation"] + ".")
    if bare.get("state") in {"not_accepted", "not_applicable", "unverified"}:
        lines.append(f"Bare-number rule: {bare['state'].replace('_', ' ')}; {bare.get('reason') or 'reason not documented'}.")
    for field, title in (("subject", "Subject"), ("origin", "Index origin"), ("ordering", "Ordering"), ("time_basis", "Time basis")):
        if node.get(field) is not None:
            lines.append(f"{title}: {node[field]}.")
    for form in forms:
        text = f"Input {form.get('syntax') or form['id']}"
        if form.get("tokens"):
            token_label = "accepted tokens" if form["notation"] == "literal" else "literal " + form["notation"] + " tokens"
            text += "; " + token_label + " " + ", ".join(repr(x) for x in form["tokens"])
            case = form.get("case", "not_applicable")
            if case != "not_applicable":
                text += " (case " + case + ")"
        if "unit" in form:
            text += "; meaning: " + _unit_text(form["unit"])
        elif kind in {"quantity", "duration"} and form.get("sentinel") is not True:
            text += "; unit/scale not verified"
        for field in ("meaning", "grammar"):
            if form.get(field):
                text += "; " + form[field]
        bounds = form.get("bounds", {})
        if bounds:
            text += "; magnitude range " + ("[" if "min" in bounds and bounds.get("min_inclusive", True) else "(")
            text += bounds.get("min", "-infinity") + ", " + bounds.get("max", "+infinity")
            text += "]" if "max" in bounds and bounds.get("max_inclusive", True) else ")"
        lines.append(text + ".")
        for special in form.get("special_values", []):
            lines.append(f"Special input {form.get('syntax') or form['id']}, magnitude {special.get('value') or '?'}: {special.get('meaning') or 'meaning not documented'}.")
    if not forms:
        lines.append("Accepted forms: not documented.")
    for field, title in (("when_absent", "Option absent"), ("when_value_omitted", "Operand omitted")):
        rule = node.get(field) or {}
        detail = rule.get("meaning") or rule.get("reason") or "not verified"
        if rule.get("state") == "known" and "value" in rule:
            form = next(f for f in forms if f["id"] == rule["form"])
            key = _special_key(rule["value"], form)
            special = next((s for s in form.get("special_values", [])
                            if key is not None and _special_key(s.get("value"), form) == key), None)
            detail = (special.get("meaning") if special else form.get("meaning")) or (
                _unit_text(form.get("unit")) if "unit" in form else node.get("subject") or node.get("meaning") or "meaning not documented")
            detail += (f" (literal {rule['value']})" if form.get("notation") == "literal" else
                       f" (input {form.get('syntax') or form['id']}; magnitude {rule['value']})")
        state = rule.get("state", "unverified").replace("_", " ")
        lines.append(f"{title}: " + ("" if state == "known" else state + "; ") + detail + ".")
    if "grammar" in node:
        grammar = node["grammar"]
        reference = grammar["reference"]
        lines.append(f"Delegated grammar: {grammar.get('name', 'name not documented')}; {reference.get('source', '?')} {reference.get('locator', '')}.")
    for component in node.get("components", []):
        component_label = f"Component {component['id']} (token slot {component['slot']}, "
        component_label += ("required" if component.get("required") else "optional") + ")"
        lines.extend(_explain_node(component["semantics"], component_label, presentation=presentation))
    if not presentation:
        if scope:
            lines.append("Applies to: " + scope + ".")
        lines.append("Evidence: " + status + ".")
        if node.get("investigation"):
            lines.append("Investigation: " + node["investigation"] + ".")
    else:
        for reference in (node.get("review") or {}).get("references") or []:
            text = "Reference: " + (reference.get("source") or "source not documented")
            text += " — " + (reference.get("locator") or "locator not documented")
            if reference.get("note"):
                text += "; " + reference["note"]
            lines.append(text + ".")
        if (node.get("review") or {}).get("note"):
            lines.append("Source qualification: " + node["review"]["note"] + ".")
    return lines


def format_value_semantics(metadata, *, context=None, definitions=None, presentation=False):
    """Return plain-text lines, optionally emphasizing interpretation for browsing.

    Structural errors raise ValueSemanticsError with structured diagnostics.
    Partial or unresolved content is labeled explicitly rather than completed by
    guessing. Form and component order follows the supplied documented order.
    presentation=True places bare-number meaning, scope and evidence early and
    includes reference locators; default reference output remains unchanged.
    """
    validator = _Validator("structural", context or ValueContext(), definitions)
    nodes = validator.contract(metadata)
    diagnostics = _ordered(validator.diagnostics)
    if any(d.severity == "error" for d in diagnostics):
        raise ValueSemanticsError(diagnostics)
    if not nodes:
        return ("Value meaning: not documented.",)
    lines = []
    for i, node in enumerate(nodes):
        lines.extend(_explain_node(node, f"Value variant {i + 1}" if len(nodes) > 1 else "Value",
                                   presentation=presentation))
    return tuple(lines)
