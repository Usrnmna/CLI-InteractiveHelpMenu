# Numerical value contract and opt-in APIs

[Documentation index](README.md) · [Profile reference](profiles-and-drivers.md) ·
[Implementation inventory](numerical-inventory/README.md)

The version 1 contract describes accepted values without interpreting the pending
command. Its implementation is [value_semantics.py](../cli_help/value_semantics.py).
Numerical completeness is an explicitly selected validation policy. Profile
loading, browsing and editing do not activate it. The source-preservation merger
and cache explicitly select structural checks for optional metadata; legacy
profiles continue to use the existing profile validator unchanged.

The contract provides Step 2 infrastructure. The
[Step 3 migration](numerical-inventory/step3-migration.md) and
[Step 4 source preservation](numerical-inventory/step4-preservation.md) document
their separate guarantees. [Step 5 presentation and search](numerical-inventory/step5-presentation.md)
uses the formatter in the existing browser. Command-specific enrichment,
authoring integration and a future completeness gate remain separate work.
Passing these APIs does not establish upstream factual accuracy.

## Representation and ownership

Optional `options[].value_semantics` contains:

```json
{
  "schema_version": 1,
  "variants": [
    {"ref": "delay"}
  ]
}
```

Each variant is a complete semantic node, or an exact shared reference. Optional
profile-level `value_definitions` maps stable names to nodes. References can occur
in variants and component semantics. A reference is exactly `{"ref": "name"}`;
overrides are rejected. Definitions describe documentation, not executable code.
Cycles, unknown references, and nesting deeper than 32 levels are errors.

Optional profile-level `positional_value_semantics` describes the existing
`positional_group`. It is a sibling of that group, because the existing group
object accepts only `argument`, `argument_count`, and `repeatable`. The contract
does not alter those fields, option arity, optionality, joined forms, or command
boundaries. A fixed numerical flag can have option-level semantics even without
an argument. Numerical documentation does not make a flag consume an operand.

The [complete synthetic profile](../tests/fixtures/value-semantics/synthetic-profile.json)
demonstrates the format. Its declared behavior is invented for contract tests;
it is not authoritative documentation for any real command. Additional
[focused cases](../tests/test_value_semantics.py) cover the other classifications.
These fixtures reside outside the command-help corpus and do not add supported
routes or production annotations.

## Semantic nodes

The common fields below are required by **maintained** completeness checks,
except where a classification-specific rule states otherwise. Structural mode
allows incomplete drafts but rejects unsupported fields and contradictions.
Display text is nonempty single-line text without control characters. Keys are
case-sensitive. Missing documentation is incomplete, never an implied unit,
default, or approval. Explicit uncertainty uses the states described below.

| Field | Meaning |
| --- | --- |
| `kind` | One classification from the next table; required even in structural mode |
| `meaning` | The specific quantity or value meaning |
| `review` | Evidence status and references |
| `applicability` | Explicit implementation, version, platform, and chip scopes |
| `bare` | Rule for ordinary unsuffixed scalar numbers, separate from literal exceptions |
| `forms` | Nonempty ordered array of accepted form descriptions |
| `when_absent` | Behavior when the entire option is absent |
| `when_value_omitted` | Behavior when the option is present without its operand |

| `kind` | Additional completeness requirements |
| --- | --- |
| `quantity` | A base unit and exact scale for each form, except explicit literal sentinels |
| `duration` | Scalar duration; numerical forms use the `second` base with a multiplier |
| `count` | `subject` states what is counted; no physical unit is required |
| `identifier` | `subject` identifies the namespace or object; not a measurement |
| `index` | `subject` and integer-string `origin` state the indexing convention |
| `level` | `ordering` explains direction; literal choices have individual meanings, other forms require an explicit mapping grammar |
| `enumeration` | Literal choices have individual meanings, other forms require a mapping grammar; no implied numerical ordering |
| `timestamp` | `time_basis` explains epoch/timezone/reference rules and applicable syntax |
| `duration_expression` | `time_basis` explains relative/sign/reference interpretation; forms describe the expression grammar |
| `composite` | `slots` and component semantics describe the existing argument structure |
| `delegated` | `grammar.name` and `grammar.reference` identify the owning grammar; no universal unit |
| `nonnumerical` | Explicit nonnumerical meaning and accepted text grammar or literal forms |
| `unresolved` | `investigation` identifies the precise source/version question; maintained mode rejects unresolved status |

For scalar forms, `number`, `suffix`, and `prefix` are incompatible with
`nonnumerical`, `delegated`, and `composite`; those kinds use an expression grammar
or literal alternatives. This catches an explicit contradiction, not every
possible misclassification. Arbitrary prose cannot be proved numerically correct.

Step 1 classifications remain planning decisions, not metadata to auto-import:

| Planning classification | Contract choices after source review |
| --- | --- |
| `quantity` | `quantity` or scalar `duration` |
| `count` | `count` |
| `identifier_or_index` | Distinguish `identifier` and `index` |
| `level_or_enumeration` | Distinguish ordered `level` and `enumeration` |
| `timestamp_or_duration_expression` | Distinguish `timestamp`, `duration_expression`, or scalar `duration` |
| `composite`, `delegated_value`, `nonnumerical`, `unresolved` | Corresponding `composite`, `delegated`, `nonnumerical`, `unresolved` |

An existing annotation, candidate keyword, missing detail string, or successful
representation in this schema does not verify upstream meaning.

## Bare numbers, forms, and units

`bare` has one of these shapes:

```json
{"state": "accepted", "form": "seconds"}
```

```json
{"state": "not_accepted", "reason": "Ordinary values require a suffix"}
```

```json
{"state": "not_applicable", "reason": "The value is an opaque host name"}
```

```json
{"state": "unverified", "reason": "The captured help does not specify a default unit"}
```

`accepted` references exactly one `number` form. `not_accepted` means the grammar
rejects ordinary bare numbers. `not_applicable` means a scalar bare-number rule
does not describe this grammar. `unverified` means the rule is unknown. An
explicit literal `0` disabling a timeout can coexist with `not_accepted` for
ordinary numbers. No empty field stands in for these distinctions.

A form has a stable `id`, `notation`, and displayed `syntax`. Notations are:

| Notation | Additional fields |
| --- | --- |
| `number` | Ordinary unsuffixed numerical magnitude |
| `suffix` | `tokens` lists literal suffix spellings; alphabetic tokens require a `case` rule |
| `prefix` | `tokens` and `case` describe literal prefixes, such as a base or sign prefix |
| `literal` | `tokens`, `case`, and `meaning` describe exact alternatives; `sentinel: true` marks an exception with an effect rather than a quantity |
| `expression` | `grammar` explains accepted syntax; this is documentation, not an evaluated pattern |

Optional form `meaning` provides additional context. `bounds` and `special_values`
are described below. Separate forms may represent percentages, absolute values,
or expression alternatives. Mixed expressions and component relationships must
be stated in their grammar; token lists alone do not imply combinability.
Overlapping tokens within the same notation and case rules are errors.
Only literal forms can declare the optional boolean `sentinel`; a sentinel
cannot also have a measurement unit. For example, a duration's literal `0`
disabling a timer is a sentinel, while a literal `4MB` size requires an actual unit.
Case rules are `sensitive`, `insensitive`, or explicitly `unverified`. For tokens
without letter-case distinctions, such as `0` and `%`, `case` may be omitted or
set to `not_applicable`. Alphabetic tokens cannot claim that case is irrelevant.
Unknown case rules receive external diagnostics and conservatively overlap
other case variants until verified.

A numerical unit is independent of the accepted token:

```json
{
  "id": "binary-size",
  "notation": "suffix",
  "syntax": "NMB",
  "tokens": ["MB"],
  "case": "sensitive",
  "unit": {"base": "byte", "multiplier": "1048576"}
}
```

This **synthetic** form means 1,048,576 bytes per input magnitude despite its
literal spelling. Neither this example nor a unit name establishes that any real
command accepts `MB`, `MiB`, `/s`, case variations, or a particular multiplier.
The formatter never converts the value or substitutes a token.

`unit.base` uses a small explicit vocabulary: `second`, `bit`, `byte`, `metre`,
`hertz`, `ratio`, `row`, `column`, `cell`, `code_point`, `baud`, `degree`, `kelvin`,
or `custom`. A `custom` base requires `name` and an explicit `definition`, for
example a documented Unicode width algorithm. Vague words such as `size`,
`speed`, `time`, or `number` are not base units. A positive exact decimal-string
`multiplier` states the scale. Optional `per: "second"` describes rates. A
`ratio` requires `relative_to`; for percentages use multiplier `"0.01"` and
separately declare the accepted `%` token. Other denominators can use a properly
defined custom base; there is no universal dimensional-conversion engine.

An explicitly unknown unit is `{"state": "unverified", "reason": "..."}` with
no base or multiplier. Nonnumerical values, indices, identifiers, levels,
enumerations, delegated grammars, and composite containers do not receive
physical units. Composite components can have their own quantities. Units on
literal numerical choices describe the whole fixed quantity; units on numerical
forms describe one input magnitude. This distinction must agree with `syntax`
and `meaning` during source review.

## Bounds, special values, and defaults

`bounds` applies to the numerical magnitude in one form:

```json
{"min": "1", "max": "100", "min_inclusive": true, "max_inclusive": false}
```

An omitted endpoint is unbounded **within the declared interval**. Inclusivity
defaults to true. These mathematical defaults do not assign a target's omitted
option behavior. At least one endpoint is required if `bounds` is present.
Numbers in metadata are normalized mathematical magnitudes expressed as finite
exact decimal strings, including zero or negative
values; floats, booleans, exponent strings, infinity, and NaN are rejected.
They are separate from a form's numeral spelling; `syntax` and `grammar` must
explain any hexadecimal or other accepted input notation. Indices require an
integer-string origin. Metadata constants are compared using
decimal arithmetic; user input is never parsed or converted.

`special_values` is an optional list such as:

```json
[{"value": "0", "meaning": "Unlimited records"}]
```

Special values are scoped to their form and may lie outside its ordinary bounds.
Numerically equivalent duplicates such as `0` and `0.0` are rejected. An empty
list declares no special cases; absence makes no claim about factual coverage.
No command universally treats zero or negative values as unlimited.

Each omission rule selects `known`, `not_accepted`, `not_applicable`, or
`unverified`. Non-known states require `reason`. A known rule uses exactly one
of these representations:

```json
{"state": "known", "form": "records", "value": "0"}
```

```json
{"state": "known", "meaning": "The implementation chooses a platform-dependent worker count"}
```

The referenced form supplies units and special-value meaning, preventing a
second contradictory description of the same default. Numeric defaults outside
ordinary bounds require an explicit special-value declaration. Literal defaults
must match a declared token. Expression defaults remain descriptive; their target
grammar is not evaluated.

`when_absent` describes the entire option being absent. `when_value_omitted`
describes an operand omitted after a supplied option. With an arity context, a
required operand permits `not_accepted` or `unverified`; an optional operand
permits `known` or `unverified`; a fixed flag requires `not_applicable`. Defaults
must not be inferred from the placeholder, `argument_optional`, or a literal zero.
For nested grammar components, explain an inapplicable option-absence rule with
`not_applicable`; outer option rules need not be duplicated into child meanings.

## Applicability and provenance

Every node has `applicability` facets `implementation`, `version`, `platform`,
and `chip`. Each facet selects:

- `{"state": "known", "values": ["explicit-name"]}` for exact named scopes.
- `{"state": "any"}` for an explicitly documented unrestricted scope.
- `{"state": "not_applicable", "reason": "..."}` for an irrelevant dimension.
- `{"state": "unverified", "reason": "..."}` for an unresolved boundary.

Version scopes may instead use `{"state": "known", "min": "1.2", "before": "2"}`.
Bounds are dotted numeric releases with inclusive `min` and exclusive `before`;
either end may be omitted. Numeric trailing zeros compare equally. Opaque release
or prerelease spellings require exact `values`; no general SemVer inference is
performed. Exact implementation/platform/chip names are case-sensitive sets.
Their real-world equivalence, aliases, and chip families require source review.

Variants must be provably disjoint if their meanings differ. Unknown, irrelevant,
missing, and unrestricted facets conservatively overlap. An opaque version set
cannot be proved disjoint from a numeric interval by guessing version order.
Meaning comparison ignores review evidence and the variant's own scope, while
retaining component applicability. Prose and forms are compared conservatively;
logically equivalent descriptions may require consolidation. The API neither
detects an installed version nor chooses a runtime variant.

`review` contains a `status` and nonempty `references`. Statuses are:

- `verified`: externally reviewed for the stated applicability; incomplete or
  explicitly uncertain semantics cannot carry this claim, even in structural mode.
- `source_derived`: extracted/source-derived material requiring verification.
- `unresolved`: an explicit outstanding investigation.
- `synthetic`: invented contract data, never upstream verification.

A reference has `source`, `locator`, and optional `note`. A source is an
authoritative documentation URL, implementation reference, or an explicitly
labeled synthetic reference. Locators identify the relevant option, section,
revision, or fixture rule. Synthetic references start with `synthetic:`.
Verified nodes cannot use synthetic evidence or unverified children. An optional
review `note` records additional qualification.
An unresolved review also requires the node's specific `investigation` text,
even when the likely classification is already known.

The validator checks the declaration and its consistency, not a source's
authority, availability, accuracy, version coverage, or completeness. It does not
fetch references. Source-derived/unresolved content fails maintained completeness
and produces external warnings. Synthetic data can pass completeness tests while
remaining visibly synthetic; that result is not production semantic approval.

## Components and explicit relationships

A composite's `slots` is the number of existing token positions in one argument
group, from 1 to 16. Each component has stable `id`, 1-based `slot`, boolean
`required`, and `semantics` containing a node or shared reference. Every slot must
have described content. Several joined components can share one slot: `HOST:PORT`
has one token slot and two components. `ADDRESS FILE` has two slots. The grammar
states separators, ordering, and optional syntax. The component count is not
automatically equal to `argument_count`.

At the profile adapter boundary, `slots` must equal the existing option
`argument_count` or the existing positional group's arity. `repeatable` remains
owned by the positional group; a component's `required` documents only its inner
grammar. No field changes insertion, cursor placement, or argument consumption.

Shared references expand without overrides. Explicit `alias_groups` passed to
the profile API require matching meaning, applicability, operand count, and
optionality. Alias spelling and summaries are not compared or inferred.
Variant order alone does not change alias meaning; different form prose/order
may conservatively require review. Unknown group members and duplicate names are
diagnosed. No new production alias-routing grammar is introduced.

## Validation APIs and diagnostics

The APIs accept dictionaries already loaded by the caller. They perform no file
reads, writes, network requests, target probes, expression evaluation, or pending
value validation. Inputs are not mutated. The profile adapter expects a profile
that has passed `core.validate_profile`; it does not duplicate the legacy schema.

```python
from value_semantics import (
    ValueContext, format_value_semantics,
    validate_profile_semantics, validate_value_semantics,
)

diagnostics = validate_profile_semantics(
    profile, "fixtures/synthetic.json", mode="maintained",
    alias_groups=[("--delay", "-d")],
)

context = ValueContext(
    source="fixtures/synthetic.json", command=("synthetic-contract",),
    option="--delay", pointer="/categories/0/options/0/value_semantics",
    argument_count=1, value_optional=False,
)
diagnostics = validate_value_semantics(
    option["value_semantics"], mode="external", context=context,
    definitions=profile.get("value_definitions"),
)
lines = format_value_semantics(
    option["value_semantics"], context=context,
    definitions=profile.get("value_definitions"),
)
```

Imports above follow the existing application module convention with `cli_help/`
on `sys.path`; package imports from `cli_help.value_semantics` also work. All
public APIs reside in one module; no loader hook or CLI flag has been added.

| Mode | Missing/partial content | Malformed or contradictory content |
| --- | --- | --- |
| `structural` (default) | Permitted, including absent legacy metadata | Error diagnostics |
| `maintained` | Error diagnostics; completeness is explicitly selected | Error diagnostics |
| `external` | Warning diagnostics, including unresolved evidence | Error diagnostics; callers decide presentation without blocking browsing |

The adapter examines value-bearing options, options with explicit semantics,
positional groups, and shared definitions. Unannotated boolean flags are skipped.
It does not enumerate future commands, classify arbitrary descriptions, or search
all fixtures. Step 1 census/review reconciliation remains a separate check. Future
inventory-wide completeness and heuristic disagreement policies belong to later
steps; this API is not such a gate.

Results are deterministic tuples of frozen `Diagnostic` records, sorted by
source, pointer, command, option, component, code, severity, and message. Each
record has those fields plus `message`; `to_dict()` returns JSON-compatible data.
`source` is supplied by the caller and should be repository-relative for portable
reports. `pointer` is a JSON pointer. A shared-definition failure points into
`/value_definitions/<name>` while retaining the affected command, option, and
component. Component IDs form the nested `component` tuple. No reports are written.

Common codes include:

| Codes | Correction |
| --- | --- |
| `sem_type`, `sem_field`, `sem_choice`, `sem_schema_version`, `sem_id`, `sem_text`, `sem_duplicate` | Repair the unsupported shape, field, spelling, ID, or duplicate declaration |
| `sem_metadata_missing`, `sem_incomplete`, `sem_forms_missing` | Complete selected value documentation |
| `sem_unit_missing`, `sem_scale`, `sem_unit_conflict` | State a real base unit and unambiguous scale |
| `sem_bare_missing`, `sem_bare_conflict` | Reconcile ordinary bare-number acceptance with number forms |
| `sem_bounds`, `sem_number`, `sem_special_conflict`, `sem_default_conflict`, `sem_form_reference` | Reconcile constants, interval, sentinel, and default references |
| `sem_classification_conflict`, `sem_index_origin`, `sem_grammar_missing` | Correct the classification or supply its required numerical/grammar meaning |
| `sem_component_slots`, `sem_components_missing`, `sem_component_required`, `sem_component_conflict`, `sem_arity_conflict` | Describe existing components without changing arity |
| `sem_scope_conflict`, `sem_version`, `sem_variant_conflict`, `sem_applicability_missing` | Resolve applicability or conflicting variants |
| `sem_reference`, `sem_reference_override`, `sem_reference_cycle`, `sem_nesting`, `sem_alias_group`, `sem_alias_conflict` | Repair explicit shared/alias relationships |
| `sem_review_missing`, `sem_provenance_missing`, `sem_review_required`, `sem_unverified`, `sem_unresolved`, `sem_false_verification` | Supply evidence or retain honest unresolved status |
| `sem_form_conflict`, `sem_omission_missing` | Resolve overlapping forms or undocumented omission behavior |

For example, a selected quantity with no form unit produces `sem_unit_missing`
in maintained mode at the form's pointer. `base: "speed"` produces `sem_choice`
in every mode. A negative scale produces `sem_scale`. A `number` form combined
with `bare.state: "not_accepted"` produces `sem_bare_conflict`. An overlapping
seconds/milliseconds variant produces `sem_variant_conflict`; an explicitly
unresolved external record produces warnings, not invented units.

## Formatter contract

`format_value_semantics(metadata, *, context=None, definitions=None, presentation=False)` returns a
tuple of plain-text lines. It first checks structural consistency. Invalid
metadata raises `ValueSemanticsError`, retaining its structured `diagnostics`.
Absent metadata returns `("Value meaning: not documented.",)`. Incomplete and
unresolved drafts state what is unverified rather than guessing or omitting it.

The first line states meaning and ordinary bare-number interpretation. Subsequent
lines cover accepted input tokens and their actual scale, count/index/level
meaning, grammar, bounds, special values, omission behavior, components,
implementation/version qualifications, and evidence status. For the synthetic
delay fixture, representative lines include:

```text
Value: Maximum synthetic wait; bare numbers: seconds.
Input Nms; literal suffix tokens 'ms' (case sensitive); meaning: 0.001 seconds; magnitude range (0, +infinity).
Special input N, magnitude 0: Unlimited wait.
```

Exact scale is preferred over a potentially misleading abbreviated unit. Input
tokens and display meaning remain separate. Form, component, and variant order
follow documented input order, while mapping-key order cannot change output.
No shortening, wrapping, searching, terminal control, or insertion occurs here.
`presentation=True` places bare-number interpretation before the longer meaning,
labels scope and evidence in the lead, moves complete applicability and evidence
early, and includes source references, locators and qualifications. Every variant
and component remains; no target applicability match is inferred. Default output
and the data contract remain unchanged. The
[presentation and search reference](numerical-inventory/step5-presentation.md)
describes the shared derived text, browser integration and layout evidence.

## Verification and remaining limits

Run from the repository root, without target probes or network operations:

```bash
python -B -m unittest discover -s tests -p test_value_semantics.py -v
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
python -B scripts/inventory_numerical_descriptions.py --check --summary
```

On Windows, `python -X utf8 -B` also selects UTF-8 console output. The new tests
are discovered by the existing suite; CI and repository policy are unchanged.
No dependency installation is needed. Synthetic cases distinguish seconds and
milliseconds, bits and bytes, decimal and binary sizes, unusual literal tokens,
counts, indices, levels, mixed percentages, composite/delegated values, sentinel
and omission behavior, version conflicts, and deliberately invalid declarations.
Purity checks block file access, process creation, network sockets, and expression
evaluation during API use, and compare inputs before and after.

Contract tests establish representation, structural consistency, selected completeness,
deterministic formatting, and legacy compatibility. They do not verify real
rsync/esptool/Go/FFmpeg versions, upstream factual accuracy, target grammar
acceptance, terminal rendering, or runtime integration. Bounds, all legal
suffixes, special-case completeness, custom definitions, and applicability
claims still require authoritative review. A misclassification concealed in
free prose remains dependent on source review and future heuristics. No pending
command or operational value is evaluated.

Step 1 annotations are not promoted or refreshed by these APIs. The
[Step 3 bundled migration](numerical-inventory/step3-migration.md) records
source-reviewed descriptions, opt-in metadata and unresolved investigations.
Its authored-source changes require narrowly justified inventory fingerprint
updates. The shared contract APIs remain unchanged. Step 4 preserves those
declarations through source merging and cache round trips with structural checks
only. Source-derived records retain their review diagnostics. Step 5 integrates
the opt-in presentation order into the existing read-only browser and search;
authoring preservation and global completeness enforcement remain separate.
