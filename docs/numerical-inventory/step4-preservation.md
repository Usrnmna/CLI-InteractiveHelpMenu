# Numerical documentation preservation

[Implementation inventory](README.md) · [Numerical contract](../numerical-value-contract.md) ·
[Discovery and execution boundaries](../discovery-and-safety.md)

Discovery now retains detached source documentation, source-qualified merge
alternatives and optional numerical metadata through cache serialization.
Preservation does not establish the truth of an upstream numerical claim.
No command-specific enrichment, numerical formatter integration, authoring
integration or global completeness policy is introduced.

## Owners and data paths

The starting revision is `1d7d80a0cb15e106b381469b3854bfbb33d26f05`.
The existing runtime owner is [discovery.py](../../cli_help/discovery.py).

| Path | Preservation boundary |
| --- | --- |
| Captured/formatted help or rendered manual text → `parse_help_document` | Options retain inline text; detached definitions retain source, line and section context |
| `parse_help` | Compatible option-list view; profile builders use the document view to retain unassigned material |
| `build_profile` → `merge_profiles` | Per-source text and optional semantic declarations are merged without evaluating source text |
| Cache write/read | Complete JSON profile round trip, bounded file I/O, identity/TTL checks and explicit structural metadata checks |
| Exact static/custom profile selection | Existing whole-profile precedence and discovery bypass remain unchanged |

Manual import, bulk generation and review-from-source already use the shared
builder. Their source construction benefits from this correction; their editing,
saving and collection workflows are unchanged and are not claimed to preserve
metadata through every later operation. Raw roff is not interpreted by this
parser; an existing renderer must supply formatted text through its established
route. No renderer or target executable was invoked during verification.

No new runtime module or dependency is required. The existing version 1
numerical contract is unchanged. The additive retention fields below belong to
the existing profile `documentation` container, not to `value_semantics`.

## Shared documentation association

The previous parser could append a footer to the final option, or treat a
definition ending in a colon as a heading and discard its body. GNU `SIZE`,
`NUM` and `KEYDEF` explanations therefore did not reliably reach their options.

The document parser separates clearly detached definition paragraphs and their
footer continuations. It associates a paragraph using:

1. A definition's leading declared metavariable, such as `SIZE` or `NUM`, matched
   exactly against argument placeholders in the same source.
2. An explicit literal option reference when no leading metavariable definition
   determines the target.
3. Explicit aliases from the same parsed declaration.

A metavariable definition takes precedence over incidental option mentions
inside its explanation. For example, `sort` key syntax mentions `-t`, `-b` and
`--debug`; that does not make those flags take `KEYDEF`. Likewise, the display
default paragraph explicitly naming `--block-size` is not assigned to `du`
`--threshold` merely because both accept the shared `SIZE` grammar.

Association does not depend on command names or numerical keyword guesses. A
previously unseen placeholder such as `AMOUNT` follows the same rule. Source
section headings remain attached so a chip, platform or release qualification
does not disappear when a definition moves into an option's detail text.

Unassigned paragraphs remain in `documentation.shared`. A detached definition
without a declared target produces `shared_documentation_unassigned`; it is not
assigned a guessed unit. General footer prose and tables without a supported
association also remain source material. Continuation examples inside a shared
paragraph do not become insertable options. Explicit subsequent option sections
can resume declaration parsing.

The existing coreutils 9.4 captures establish the regression examples:

| Source | Recovered information |
| --- | --- |
| `df` | Display-default rules and binary/decimal `SIZE` suffix definitions on `--block-size`/`-B`; column-list grammar on `--output` |
| `du` | `SIZE` grammar on block-size and threshold options; display environment defaults remain specific to block-size |
| `head`, `tail` | `NUM` multiplier grammar on byte and line counts, including explicit short aliases |
| `sort` | Percentage/default memory scaling on buffer size; one-based field/character positions on key definitions |
| `cp` | Additional named grammar/footer associations recovered by the same general rule; no numerical classification is invented |

The immutable [capture manifest](../../tests/fixtures/help/workflow-baseline-captured.json)
records GNU coreutils 9.4. The authoritative reference is the
[version 9.4 manual source](https://raw.githubusercontent.com/coreutils/coreutils/v9.4/doc/coreutils.texi),
especially **Block size**, **head invocation**, **tail invocation** and
**sort invocation**. The separate
[preservation evidence fixture](../../tests/fixtures/value-semantics/preservation-evidence.json)
records bounded expectations. This evidence does not establish behavior for
every coreutils release or other programs with the same names.

## Merge rules

First-source summary, category membership and root declarations retain
precedence. A generated `Documented option` fallback can be replaced by a useful
later summary. Empty fields do not erase useful text. Later summaries and details
remain in the selected option's detail text, with source attribution; a later
category's name and description are retained when they qualify that text.
Source-specific category contexts are also retained in the provenance records.

The existing discovery arity rule remains: prefer a larger explicit operand
count, then a required operand over an optional operand at equal count. Repeated
source observations are deduplicated by literal flag with trailing `=` normalized,
as before. Every repeated observation is structurally checked before the final
profile is validated. The winning operand declaration is copied coherently.
No command path, supported route or insertion policy is added.

Optional semantic declarations are handled separately from prose:

- Metadata is copied as a whole declaration with its review status,
  applicability, forms, defaults and provenance. Individual numerical fields
  are never assembled from different sources.
- Each source resolves references against its own definitions before merging.
  A missing reference cannot bind accidentally to an earlier source's name.
- Later sources receive deterministic definition namespaces; all exact `ref`
  objects are rebound together. Nested references are supported. Literal tokens
  and numerical scale strings are not rewritten.
- Compatible first-source metadata retains precedence. A valid later declaration
  can populate an absent field when it fits the selected declaration and identity.
  Other declarations remain qualified alternatives rather than being discarded.
- A semantic declaration's source operand count must match the selected count.
  Structural validity alone does not establish that association for scalar nodes.
  The Step 8 correction retains mismatched declarations as inactive evidence;
  a winning source can supply its own compatible composite metadata.
- Overlapping contradictory metadata, unmatched identity, or incompatible arity
  produces a structured review diagnostic. Disjoint version scopes are not
  called a unit conflict merely because their meanings differ.
- Invalid optional metadata remains inactive source evidence. Valid independent
  definitions and legacy option text remain usable. This is structural checking,
  not a completeness requirement for old profiles.
- Positional metadata remains beside the existing positional group. Later source
  groups do not replace the first profile's group. Incompatible declarations and
  metadata retain their original source context as alternatives.

Explicit aliases are not inferred from matching summaries. Static-profile
loading still replaces a matching bundled profile with its custom profile; it
does not call the source merger or automatically combine live help with a static
profile. External prose never creates verified structured numerical metadata.

## Retained data and diagnostics

| `documentation` field | Purpose |
| --- | --- |
| `sources` | Original documentation/discovery provenance plus category and protected profile context for each source |
| `shared` | Source paragraph, original section, line, text, target flags and association method |
| `semantic_sources` | Selected semantic owner by canonical flag or `<positional_group>`; ownership survives subsequent merging and cache reload |
| `alternatives` | Unselected or invalid declarations, retaining source and definition scope |
| `diagnostics` | Structured code, severity, source, command, option and explanation; underlying validator diagnostics where applicable |

An alternative with `definition_scope: "profile"` references the merged profile's
definitions. A source-scoped alternative retains its original definitions and may
intentionally remain malformed or unresolved evidence. It is not active metadata
and must not be treated as verified content. Original opaque documentation fields
remain in source provenance rather than being silently coerced.

Diagnostic codes include `shared_documentation_unassigned`,
`numerical_text_review`, `source_definitions_invalid`, `source_semantics_invalid`,
`source_identity_review`, `semantics_arity_review`, `value_semantics_conflict` and
`positional_semantics_review`. Stored discovery warnings retain these codes;
the existing passive diagnostic interface continues to redact arbitrary prose.

Plain-text comparison uses numerical terms only to identify possible source
disagreements. It does not prove a contradiction, parse command operands, choose
a scale or assign units. Legitimate conversions, examples and version differences
can trigger review; subtle contradictions without recognizable terms can be
missed. Structured variant checks provide stronger consistency evidence but still
cannot prove factual accuracy. Both source explanations remain available.

## Cache behavior

The existing cache identity design is unchanged. Generation revision
`CACHE_VERSION = 12` includes Step 8's operand-count ownership correction and
invalidates interpreted profiles made with previous
parsing/merging rules through the normal key mechanism. Old files are neither
deleted nor rewritten merely because the revision changed.

The JSON payload preserves the complete profile, including retained documentation,
definitions, positional semantics, applicability and uncertainty. Cache reads and
writes explicitly select structural numerical validation. Malformed active
metadata is not accepted as a cache hit or newly persisted. Incomplete drafts,
unresolved semantics and legacy profiles without metadata remain permitted when
structurally valid. No maintained-completeness policy is activated.

Existing size limits, atomic replacement, command/identity checks, TTL, refresh,
source fallback, module freshness and guarded-tool policies remain in effect.
Failed cache storage does not prevent browsing. No new version request, target
probe or cache-directory scan is introduced. Manual-page changes and same-version
local edits retain their previously documented TTL/refresh limits.

## Verification and reconciliation

Recalculation preserves 76 profiles, 942 option records, 327 explicit named paths,
5,243 canonical option/keyword identities, 7,591 parsed observations, 341 input
files and 6,119 total review identities. These overlapping counts are not additive.

Exactly 35 external description fingerprints change across `cp`, `df`, `du`,
`head`, `tail` and `sort`, plus the source fingerprint for `discovery.py`.
All non-description observation facts remain identical, including source
relationships, flags, categories, argument declarations and optionality. The
12 audit-seed shared-definition reviews now record preserved documentation.
Other classifications, including unresolved classifications, are retained;
preserving a source does not verify its numerical claims. Unaffected review
members and fingerprints remain unchanged.

Focused tests cover the captures, generic and ambiguous placeholders, multiline
manual text, source/category qualifications, definition collisions and nested
references, aliases, conflicting/disjoint semantics, positional groups, malformed
metadata, unresolved states, cache misses/hits/round trips/invalidation, input
immutability and literal buffer edits. Existing migrated metadata supplies
representative times, rates, binary/decimal scales, literal tokens, counts,
indices, levels, percentages, composites, delegated values and special cases.
Its declarations and formatter explanations are compared before and after
transformation without claiming newly verified upstream facts.

Run from the repository root without target programs or network operations:

```bash
python -B -m unittest discover -s tests -p test_documentation_preservation.py -v
python -B -m unittest discover -s tests -p test_value_semantics.py -v
python -B -m unittest discover -s tests -p test_numerical_migration.py -v
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
python -B scripts/inventory_numerical_descriptions.py --check --summary
python -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -B cli_help/main.py --check
```

On Windows, `python -X utf8 -B` selects UTF-8 output. The new tests allocate
disposable locations under the ignored repository cache and block process and
network entry points. The broader passive regression selection excludes tests
that execute process fixtures. Existing Windows test directory/cache parents use
inherited-permission disposable directories; production cache permissions remain
unchanged. Two POSIX-specific filesystem cases remain platform skips. Reports
under `tests/reports/numerical-inventory/step4-*.json` record the exact selections
and environmental accommodation without changing CI or repository configuration.

## Completion boundary

Step 4 is complete within the documented parser, source-merging and cache
boundaries. There is no remaining implementation decision requiring an
architectural change. Arbitrary help formats, ambiguous associations, external
factual completeness and the Step 3 evidence investigations remain explicit
limits rather than silently inferred semantics.

No production profile, target route, discovery execution policy, UI, search,
insertion, guided editor or Git/GitHub configuration is changed. Raw captures and
historical releases remain intact. Formatter presentation, command-specific
enrichment, authoring and global enforcement are deferred. The next plan step is
Step 5: make numerical meaning consistently visible and searchable.

The subsequent [Step 5 presentation account](step5-presentation.md) records the
formatter/search integration and scoped fake-window evidence. Its presentation
changes do not alter the preservation, merging or cache rules documented here.

The subsequent [Step 8 integration verification](step8-verification.md) corrects
the narrow scalar-arity association defect and advances generation 11 to 12.
Other merge precedence, discovery requests and cache policies remain unchanged.
