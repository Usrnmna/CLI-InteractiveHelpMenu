# Numerical coverage enforcement

[Inventory and review](README.md) · [Numerical contract](../numerical-value-contract.md)

## Active policy and readiness

The offline checker selects the existing inventory, shared validator, formatter
and presentation APIs. Numerical interpretation remains owned by
`cli_help/value_semantics.py`. Runtime loading, browsing, discovery, insertion,
and authoring behavior are unchanged by the coverage gate.

```bash
python3 -B scripts/check_numerical_coverage.py --summary
python3 -B scripts/check_numerical_coverage.py --output tests/reports/numerical-inventory/coverage.json --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B -m unittest discover -s tests -p 'test_numerical_coverage.py' -v
```

Without `--summary`, stdout contains full diagnostics and debt identities. Only
explicit `--output` writes a report, inside that snapshot's ignored
`tests/reports/` directory. Existing unrelated files and linked destinations are
rejected. No installation, network access, executable enumeration, target probing
or evaluation of inspected source is involved. `--root` selects a data snapshot;
interpretation modules come from the trusted tool checkout, not that snapshot.

| Check | Active scope | Result |
| --- | --- | --- |
| Inventory/review | Every maintained source, route, category, option/keyword, fixture observation, definition and positional component in the inventory boundary | Missing, stale, duplicate, conflicting or orphaned assignments fail |
| Supplied structure | Optional metadata and definitions in every bundled profile | Shared structural errors fail, independently of debt allowances |
| Maintained prospective | Value-bearing options, optional values, numerical fixed flags, numerically classified keywords/flags, positional groups and shared definitions | Completeness errors fail except unchanged exact legacy debt or an explicitly justified exception |
| Maintained strict | The same records, with no debt suppression | Every completeness error fails; readiness is reported separately |
| Propagation | Every structurally valid supplied active contract, including references and positional guidance | Missing formatter obligations or placeholders in actual details/search construction fail |
| External uncertainty | Raw captures, parsed observations, synthetic reference inputs and matrix evidence | Explicit census/review required; no fabricated complete contract or runtime browsing block |
| Secondary heuristics | Nonnumerical dispositions with suspicious placeholders, prose or structured kinds | Visible review warnings; no automatic reclassification or inferred units |

Initially, 504 records require contracts: 479 option or keyword records, three
positional groups and 22 shared definitions. Of these, 144 pass maintained
validation: 128 options, three groups and 13 definitions. The remaining 360
comprise 304 options without optional metadata, 47 source-derived options and
nine source-derived definitions. Definitions and consumers overlap; these are
record counts, not additive option coverage.

The 304 omissions comprise 198 text/path values, 102 enumerations and four
identifiers. Missing optional metadata does not establish a missing physical
unit or an incorrect description. Source-derived declarations retain their
Step 3 investigations and qualifications. Neither a planning classification nor
a completeness check verifies upstream facts.

The default prospective gate can pass with this explicitly reported debt.
`full_maintained_ready` remains false, and strict mode intentionally exits 1.
Full readiness requires resolving these exact contracts and investigations,
removing resolved baseline rows, and passing strict validation and the other
active gates. Production migration is outside Step 7. There is no blanket
profile, command, directory or historical-count exemption.

## Enumeration and classifications

Coverage follows automatic source enumeration, not a fixed list of numerical
flags. New profiles, categories, options, keywords, fixtures and components need
their own reviewed identities/fingerprints. Required and optional arguments are
selected regardless of placeholder spelling. Numerical fixed spellings and
planning classifications also select operand-free records. All shared
definitions, including unused definitions, and positional groups are selected.
Missing classification fails even when metadata validates. An unresolved
classification selects a contract whose uncertainty requires a specific
completeness exception; it is not a bypass.

Non-value flags need an inventory disposition but do not acquire irrelevant
numerical metadata merely because a profile is maintained. Category/profile
descriptions are contextual review inputs, not values requiring physical units.
Driver/global arity declarations, routes, matrix sentinels and help observations
remain distinct from authored display descriptions. A passing sentinel does not
establish option completeness.

The census also includes these previously unprotected owners:

| Input | Reason for explicit census |
| --- | --- |
| `cli_help/value_semantics.py` | Contract, shared validation and formatter obligations |
| `cli_help/presentation.py` | Shared details/search construction |
| `cli_help/authoring.py` | Preservation and semantic reference ownership |
| `cli_help/manual_import.py` | Import and collection construction |
| `cli_help/bulk_scan.py` | Collection generation and checkpoint ownership |
| `cli_help/review.py` | Draft lifecycle, preview and save |
| `cli_help/review_forms.py` | Guided declaration changes |
| `cli_help/collection.py` | Structural inspection and recovery preflight |
| `scripts/inventory_numerical_descriptions.py` | Source enumeration and reconciliation |
| `scripts/check_numerical_coverage.py` | Policy, exact deferrals and propagation checks |
| `tests/run.sh` | Normal local gate invocation and exit propagation |
| `.github/workflows/ci.yml` | Early gate and named failure report retention |
| All files under `tests/fixtures/value-semantics/` | Semantic references and visibly synthetic specimens |

Initially these are 12 new source owners and three existing reference fixtures.
The 22 definition and three positional-group identities add another 25 entries.
The census grows from 341 to 356 files and from 6,119 to 6,159 identities. No
supported route, production profile or option is added. Six existing positional
component identities remain separate from three new whole-group identities.
New fixtures outside matrix sentinel lists are discovered automatically,
including future semantic-reference fixtures.

## Exact debt baseline and exceptions

`review.json` owns `coverage_policy` alongside the existing curated review groups.
Generated reports never rewrite it. Version 1 uses:

- `legacy_baseline`: origin revision, bounded scope, technical reason,
  invalidation rule and an explicit list of existing incomplete records.
- `exceptions`: individually justified deferrals; initially empty.

Each baseline row has `id`, repository-relative `source`, `fingerprint`,
`review_fingerprint` and exact `codes`. The key is `(source, id)`, so a new file
cannot inherit an existing allowance. The row hash covers the complete authored
option/contract, profile context, category description and transitive referenced
definitions. Offsets and unrelated sibling insertions are excluded. The separate
review hash covers planning decisions, evidence, applicability, references,
investigation and acceptance. Refreshing census hashes cannot refresh it.

This bounded baseline is necessary because additional production migration is
outside Step 7 and prior opt-in work does not cover all maintained values. It
permits only exact pre-existing `sem_metadata_missing`, `sem_review_required` and
`sem_unverified` failures. It cannot admit new requirements, structural errors,
missing classification/review or lost presentation. It records debt rather than
360 claims of adequate content. Existing per-entry review groups and metadata
retain the evidence, applicability and investigations. No refresh command exists.

Individual exceptions additionally require substantive `reason`, `evidence`,
`applicability`, `investigation` and `review_condition` strings. Evidence must be
`source_derived`, `suspected` or `unresolved`, never verified. Codes must exactly
match current completeness diagnostics. Structural, classification,
reconciliation and propagation errors cannot be deferred. Wildcards, duplicate
or conflicting records, unsupported fields, stale hashes, resolved requirements,
orphaned identities and missing review conditions fail.

After a relevant edit, the preferred resolution is a complete applicable
contract. Exceptional deferral needs inspection of changed facts, specific
justification and a deliberate policy edit. Expanding the legacy baseline to
silence failure is not a resolution. No check establishes that a policy edit
received substantive human review. Mutation tests establish that additions and
relevant content/review edits cannot inherit an unchanged allowance.

## Diagnostics and propagation

Diagnostics have stable `code`, `severity`, `gate`, `source`, `pointer`, `command`,
`option`, `component`, `identity` and corrective `message`. Reconciliation also
retains inventory `location`. Numerical codes remain owned by the shared
validator. Severity separates `error`, accepted `debt`, heuristic `warning` and
external `info`. Ordering is deterministic; machine paths, changing timestamps
and pending buffers are absent.
Exception diagnostics also include `policy_source` and the exact row's
`policy_pointer`, including malformed, orphaned and conflicting rows.

The shared validator diagnoses exact generic meaning/subject labels such as
“size”, “speed”, “time” or “number” with `sem_meaning_vague` in completeness modes.
It does not interpret arbitrary prose. Quantities still require actual units
and scale; counts require subjects, indices origins and delegated values their
grammar. Literal tokens do not imply conventional scale. Structural and
completeness modes remain distinct.

The checker compares formatter obligations with actual shared presentation,
not persisted explanation copies. Independent reference tests verify rsync's
byte rate, suffix spellings and version scope through browser details, search
and fake-window drawing. Deliberate omission of details/search content fails.
Positional meaning is checked through existing option-details paths. Existing
presentation tests cover wrapping, scrolling and qualified alternatives; native
terminal behavior remains a separate verification boundary.

Explicit alias groups supplied to `check_profile(..., alias_groups=...)` use the
shared validator. Current production profiles do not declare persisted alias
groups. Similar summaries and aliases in unrelated external captures are not
authority for bundled alias semantics. Definitions are checked independently
and at explicit consumers.

Heuristics flag numerical placeholders, unit prose or incompatible structured
kinds under nonnumerical dispositions. Names with digits, systemd `--unit`, a
serial-device `PORT`, mounted `--volume`, opaque IDs and delegated configuration
are not quantities by name alone. Current warnings for `fd --print0`,
`fdfind --print0` and `tar --totals` concern output bytes rather than numerical
operands; their nonnumerical dispositions remain appropriate. Warnings stay
visible and nonfatal. Review resolves a signal by explaining the source in its
exact review group or correcting demonstrated misclassification. Arbitrary
wording, hidden grammars and misleading factual claims can escape heuristics;
explicit review and upstream documentation remain necessary.

## Contributor workflow and local integration

1. Add/change maintained content. Preserve raw captures and label synthetic
   references. Target probes are unnecessary for this offline gate.
2. Regenerate inventory and inspect each changed observation. Assign exact IDs
   to appropriate review groups. Planning classes do not become verified metadata.
3. For selected authored values, document numerical meaning or explicit
   nonnumerical/delegated interpretation with the existing contract. Record forms,
   scale, bare rules, relevant omission/sentinels and applicable provenance.
   Verify factual claims against applicable authoritative sources.
4. Run coverage and inspect full diagnostics. Correct errors, review signals and
   actual displayed/searchable text. Inspect referenced definitions and consumers.
5. If a precise unresolved case must remain, document its bounded investigation
   and review condition before adding an exact exception. Do not enlarge the
   legacy baseline. Remove resolved debt and stale rows explicitly.
6. Run focused tests and the existing suite on a supported platform. Full strict
   readiness remains separate from prospective protection.

`tests/run.sh` uses the same prospective command as the early Linux CI step.
Normal unittest discovery includes `test_numerical_coverage.py`. The early step
retains `tests/reports/ci/numerical-coverage.json` through the existing always-run
upload. Nonzero statuses propagate. No hosted workflow is triggered by local
verification. Other jobs, dependencies, permissions, publishing and Git
configuration remain unchanged.

## Verification boundary and next step

Focused tests cover growth, classifications, contract failures, exact deferrals,
changed definitions/reviews, external fixture census, propagation omissions,
valid unitless/grammar forms, deterministic output and input immutability.
Disposable snapshots and process/network tripwires protect the execution boundary.
The full gate intentionally remains incomplete as described above.

The local Windows/Python 3.13 verification ran 367 tests: 350 passed and 17
platform-dependent cases were skipped, with no failures. The report records
selected passive tests, excluded process fixtures and inherited-permission
temporary-directory accommodations. Native POSIX restoration, real terminals
and hosted CI were not exercised. Workflow YAML and failure/report integration
were checked locally. Git for Windows Bash could not create its signal pipe
(Win32 error 5), so Bash syntax validation was not established on this host.

Subsequent [Step 8 integrated verification](step8-verification.md) records current
cross-component tests, a bounded scalar-arity repair and remaining native gaps.
Command-specific enrichment, additional migration,
release work and unrelated configuration changes remain outside this step.
Prospective success does not establish every numerical factual claim, installed
version behavior or universal external-help completeness.
