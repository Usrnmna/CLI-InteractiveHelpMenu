# Numerical presentation and search

[Implementation inventory](README.md) · [Numerical contract](../numerical-value-contract.md) · [Browser controls](../usage.md#browser-controls)

## Scope and corrected omissions

The browser previously searched flags, summaries and detail strings. Argument
placeholders and optional numerical metadata were omitted. List rows placed the
entire declaration before a clipped summary, while selected details began with
category prose. Numerical information could therefore be absent from search or
hidden behind predictable clipping and long contextual descriptions.

Step 5 connects the existing formatter to the list, selected details and search.
Profiles, numerical declarations, discovery requests, parsers, source selection,
merging, cache identity, insertion and authoring behavior are unchanged. The
existing inspection preview uses the same browser and inherits this display.

## One derived explanation

`cli_help/value_semantics.py` retains its default reference-format API and output.
The additive `presentation=True` argument places ordinary bare-number meaning
before the longer purpose statement, places applicability and evidence early,
and includes source references, locators and qualifications. All variants and
components remain present. No installed-version, operating-system or chip match
is inferred. The metadata contract and validation policies are unchanged.

`cli_help/presentation.py` derives immutable `ValueText` and `OptionText` records:

- The compact lead comes from the first formatted line. Only the predictable
  `Value` label is removed and `bare numbers:` becomes `bare:`. Evidence and
  scope markers remain. The full meaning is retained until the list renderer
  applies an explicit cell-budget ellipsis.
- Complete details retain the formatter lines, original summary/detail, complete
  literal declaration and argument guidance, command-wide repeated arguments,
  source review notes, category context and unassigned source context.
- Search retains the original joined flag/summary/detail text, including legacy
  cross-field substring matches, and adds the displayed declaration, argument
  placeholder, numerical explanations and relevant source qualifications.

The browser derives these records once for a modal, read-only profile. Query
changes reuse them without metadata mutation or repeated formatting. Reopening
the browser, including a preview after draft edits, derives new records. No
persistent search index, discovery-cache change or formatted data copy is stored
in profiles. Modifying a profile in place during an open modal is not supported.

## Visible and accessible information

Active numerical guidance starts the selected details before category context
or long summaries. The list reserves space for guidance by abbreviating long
declarations when necessary. The complete flag and placeholder remain accessible
in details, and insertion continues to use the original option object.

Representative presentation from the already reviewed rsync 3.4.1 metadata is:

```text
(scoped) bare: 1024 bytes/second; Maximum socket transfer rate.
```

The complete explanation identifies the exact implementation/version, accepted
suffixes, decimal/binary scales and zero-value behavior. This display unit does
not imply an accepted literal `/second` suffix. Its factual evidence remains the
[Step 3 migration sources](step3-migration.md) and
[reviewed semantic fixture](../../tests/fixtures/value-semantics/migration-evidence.json).
No new upstream behavior is verified by displaying those declarations.

Multiple applicability variants use a compact indication that meaning varies by
applicability. Details retain every variant with its qualifications. Single
scoped variants also remain explicitly scoped; the browser does not treat them
as universal facts about the installed program. Source-derived, synthetic,
unresolved and partial declarations retain their evidence labels and specific
investigation requirements. Counts, indices, identifiers, levels, expressions,
composites and delegated grammars use their existing formatter explanations;
physical units are not invented for them.

List clipping uses an ellipsis measured in terminal cells. Selected details wrap
with the existing Unicode utilities. A `Details start-end/total` line identifies
the visible range and the configured detail-scroll keys when more content exists.
The existing `[` and `]` controls reach the complete explanation. Not every
qualification fits simultaneously at 60 columns by 16 rows. Below that minimum,
the existing resize notice and cancellation behavior remain in effect.

## Search, source notes and uncertainty

Case-insensitive substring matching, category selection, result order and keyboard
controls remain unchanged. Units, exact multipliers, accepted tokens, counted
subjects, index origins, level ordering, special values, argument placeholders,
reference qualifiers and command-wide positional explanations are searchable.
Searchable value text is also available in selected details. Search never parses
an operand, evaluates an expression or runs an example.

Assigned shared explanations preserved in existing option detail remain
searchable. Unassigned shared prose is accessible under an explicit warning that
its relationship to the option is unverified; it does not make every option match
that prose. No association is inferred by the presentation layer.

Step 4 semantic ownership and relevant source diagnostics are shown as source
notes. Competing or incomplete claims produce an early review indication. Existing
source-labeled conflicting prose stays distinguishable and searchable. Inactive
or invalid structured alternatives are identified by source, but are not formatted
into active advice or searched as raw metadata. Detailed inactive declarations
remain in the preserved source data for later review. Presentation does not
resolve factual conflicts or promote an evidence status.

Malformed optional metadata or a formatter failure produces nonfatal guidance
that numerical documentation could not be interpreted safely. Original summary,
detail and argument text remain accessible and searchable. Legacy profiles with
no metadata keep their prose without a completeness gate. Internal diagnostic
codes, raw metadata and schema structures are not shown as value instructions.

## Verification and reconciliation

The focused tests use the existing fake-window browser harness, cell-bound checks
and scripted key sequences. Reviewed migration fixtures supply the factual
expectations; synthetic declarations supply layout and failure cases. Tests block
process launches, target probes and network entry points. A purity check also
blocks file access, writes and expression evaluation during derived-view use.

Coverage includes every opted-in bundled option and positional contract, shared
references, malformed and unresolved data, inactive alternatives, source conflict
prose, and unassigned documentation. Cases distinguish seconds/milliseconds,
bits/bytes, binary/decimal multipliers, unconventional literal size tokens, counts,
indices, levels, identifiers, percentages, expressions and delegated values.
Zero, negative, omitted and unlimited meanings remain accessible. Minimum-size
scrolling, long placeholders, wide/combining characters, control filtering,
shrink/grow/reopen, custom keys, query restoration, read-only preview and exact
literal buffer/cursor edits are checked through the actual browser paths.

Recalculation retains 76 profiles, 942 option records, 327 explicit named paths,
5,243 canonical option/keyword identities, 7,591 parsed observations, 341 input
sources and 6,119 review identities. These counts overlap and are not additive.
The only changed enumerated fingerprint is `source||cli_help/ui.py`, after review
of the display/search delta. AC-08 and F6 record scoped presentation evidence;
all option reviews and numerical evidence classifications remain unchanged.
The focused census does not enumerate every application module: formatter/helper
changes are recorded here and independently compared during final verification.

Run from the repository root without target programs or network operations:

```bash
python -B -m unittest discover -s tests -p test_numerical_presentation.py -v
python -B -m unittest discover -s tests -p test_value_semantics.py -v
python -B -m unittest discover -s tests -p test_numerical_migration.py -v
python -B -m unittest discover -s tests -p test_documentation_preservation.py -v
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
python -B scripts/inventory_numerical_descriptions.py --check --summary
python -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -B cli_help/main.py --check
```

Windows console output uses `python -X utf8 -B`. Broader passive test selections
and static verification are recorded in ignored
`tests/reports/numerical-inventory/step5-*.json`. Existing Windows test temporary
directories use inherited permissions in disposable repository-cache locations;
production permissions are unchanged. Process/target fixtures are excluded or
fully mocked. Native curses/Bash terminal rendering, terminal-emulator resize and
Readline restoration, assistive technology, ambiguous-width/emoji behavior,
installed target versions and hosted CI are not established by fake-window tests.

## Completion boundary

Step 5 implements presentation and search within the existing interface.
Factual gaps from earlier inventory/migration work remain explicit; rendering
does not resolve unknown external units or guarantee complete documentation.
No architectural change or contract redesign is required.

Command-specific enrichment, authoring/import/save changes and global enforcement
remain deferred. The next plan step is Step 6: carry the contract through every
authoring workflow. No later step is implemented here.

The subsequent [Step 6 authoring account](step6-authoring.md) documents preservation
through edits, source replacement, save/reload and inspection. Read-only preview
uses the same presentation path without making draft changes.
