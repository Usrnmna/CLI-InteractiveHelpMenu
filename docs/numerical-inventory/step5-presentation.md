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

## Display levels and unit search

The numerical contract supplies validated forms, components, variants, and
applicability to the browser. The reference-format API retains its full evidence.
The terminal shows citations in none of its display levels. Original documentation
and source qualifications remain searchable.

Simple shows each option’s purpose. A shared note names the applicable options
and the unit of their bare inputs. Detailed shows a short example or operational
qualification. Expanded lists syntax, conversions, bounds, special inputs,
defaults, versions, examples and command-wide positional rules when documented.
The `Lines` counter and detail-scroll keys expose longer explanations.

For example, rsync’s bare bandwidth uses `KiB/s`. Its accepted suffixes distinguish
decimal from binary scaling. FFmpeg’s bit-rate conversion table shows the literal
input forms under one `Result (bps)` heading. A search for `bps` includes documented
bit rates in inputs or reported output. Display abbreviations are independent of
the units a command actually accepts. See the [unit examples and scoping
rules](../superpowers/plans/2026-11-24-menu-detail-levels.md#unit-examples-from-the-bundled-menus).

Search retains case-insensitive literal matches over the original flag, summary,
detail, placeholder and evidence. Additional unit aliases use case-sensitive
symbols to distinguish bits from bytes and decimal from binary sizes. The browser
derives the formatted data for each open profile and reuses it during navigation.
The active profile, cache and pending command remain intact.

See the [browser controls](../usage.md#browser-controls) for level switching,
category titles, selected-row recovery, filtering and scrolling.

## Search, source notes and uncertainty

Case-insensitive substring matching, category selection, result order and keyboard
controls remain unchanged. Units, exact multipliers, accepted tokens, counted
subjects, index origins, level ordering, special values, argument placeholders,
reference qualifiers and command-wide positional explanations are searchable.
Selected details contain concise value guidance; search also retains the original
source text and formatter evidence for compatibility. Search never parses
an operand, evaluates an expression or runs an example.

Assigned shared explanations preserved in existing option detail remain
searchable. Unassigned shared prose is omitted from option details and does not
make every option match that prose. No association is inferred by the presentation layer.

Semantic ownership and source diagnostics remain in stored documentation and
search. Competing or incomplete claims produce a concise warning before value
rules. Inactive structured alternatives are never formatted into active advice
or searched as raw metadata. Presentation does not resolve factual conflicts or
promote an evidence status.

Malformed optional metadata or a formatter failure produces nonfatal guidance
that numerical documentation could not be interpreted safely. Original summary,
detail and argument text remain searchable; the display uses the same prose
simplification as profiles without metadata. No completeness gate is added. Internal diagnostic
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
