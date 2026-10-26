# Numerical metadata through authoring workflows

[Implementation inventory](README.md) · [Numerical contract](../numerical-value-contract.md) · [Review controls](../review.md)

The subsequent [native/POSIX verification](native-posix-verification.md) supplies
real read-only preview, terminal restoration and ext4 process/filesystem evidence,
with separate 9p results and limits. The verification section below retains the
original Step 6 passive scope and platform exclusions.

## Scope and inspected paths

Step 6 preserves numerical declarations through existing help-content authoring.
The contract, shared validator, formatter, browser, discovery parser and merge
rules are unchanged. No production profile is migrated and no numerical
completeness gate is activated.

| Path and owner | Preservation and validation boundary |
| --- | --- |
| Text/manual import: `manual_import.import_manual`, `ManualCollection.save` | Preserve parsed prose and source records. Explicit source replacement retains the prior profile as inactive evidence. Supplied optional metadata is structurally checked before writes. |
| Bulk generation: `bulk_scan.scan_record` | The existing per-record path delegates to the same collection writer. Captured/mocked source responses exercise this transformation without scanning installed programs or running renderers. |
| Draft load and raw JSON: `review.Draft`, `edit_draft` | Whole documents retain supported fields. Invalid editor text remains recoverable. Numerical reconciliation compares the edited document with its saved baseline. |
| Guided option/category/driver operations: `review_forms.apply_document` | Detached edits preserve unrelated content. Complete operations validate before replacing draft text. Potentially stale declarations remain inactive with source evidence and review guidance. |
| Numerical review: `review.review_numerical` | Displays active explanations, reference consumers, unannotated values and structured diagnostics. Explicit acknowledgement preserves the declared evidence status; it does not assign verified status. |
| Preview: `ReviewSession.validate(numerical=False)`, `preview_profile` | Reconcile a copy without changing draft text or files. Malformed optional metadata retains the browser's nonfatal fallback. |
| Save/reload: `ReviewSession.save`, `ManualCollection.save_documents` | Recheck supplied metadata before writes, retain existing backups/conflict checks, and serialize complete documents. Direct collection saves also check changes against the existing profile. |
| Inspection/recovery: `collection.numerical_findings`, `inspect_state`, `restore_review_backup` | Report structural errors and explicit uncertainty without requiring metadata on legacy entries. Recovery reaches the same structural pair validator before its existing guarded writes. |

The local workflow report enumerates functions/methods and CLI entry points from
syntax trees without evaluating source declarations. General package-update text
merging and arbitrary external file edits are file operations outside these
help-content authoring interfaces. They are not modified or claimed to provide
semantic authoring guarantees. Content subsequently entering review/save/inspect
encounters those boundaries; no global file-writer interception is introduced.

## Change-impact policy

`cli_help/authoring.py` supplies one pure reconciliation path. It compares actual
declarations and explicit shared references rather than inferring units from
names, placeholders or keyword matches.

| Change | Handling |
| --- | --- |
| Unchanged content, option/category reordering, category moves or lossless renaming | Preserve metadata, definitions, evidence and applicability. Missing/default spellings introduced by existing guided forms do not alone invalidate meaning. |
| Flag/command identity, argument presence, placeholder, count, optionality, value style, bundle or boundary change | Retained numerical declarations require review. A changed placeholder does not prove that units changed; it makes the previous association uncertain. |
| Summary/detail, relevant contextual description, provenance or semantic-owner change | Treat inherited numerical declarations as requiring review rather than asserting a factual unit defect. |
| Explicit numerical correction retaining verified claims | Require acknowledgement of the current authored declarations through Numerical review. Validation success and a documentation URL do not supply that acknowledgement. |
| Changed verified shared definition, including an unused definition | Reject save with `authoring_definition_review` until explicit review or honestly unverified metadata is supplied. The report identifies every explicit consumer. |
| Structurally invalid edited metadata, dangling references, cycles or inconsistent components | Retain the editable draft and report shared-validator diagnostics. No existing valid file is overwritten. |
| Deleted entry, removed metadata or deleted definition | Retain its prior numerical declaration, reference closure and owning source context as inactive evidence. Remaining consumers and definitions are not deleted automatically. |
| Source re-import/replacement | Retain the complete previous profile in `documentation.sources`. Do not attach old numerical claims to fresh source observations merely because flag names match. |

Relevant driver changes are restricted to the selected route's argument/boundary
context and global operand declarations. Unrelated routes are not treated as
semantic changes. Existing command-path restrictions still reject renaming a
selected review entry to another command. Direct reconciliation also prevents
automatic transfer of verified claims across identities.

Original declarations use the existing `documentation.alternatives` records,
including `metadata`, source-scoped `definitions`, `declaration`, command,
imported provenance and semantic ownership. No new production semantics schema
or persistent lifecycle state is introduced. Potentially stale inherited declarations are removed
from active numerical guidance while their review notes remain visible. Legacy
summary/detail text remains available; source review is still required when that
prose itself is uncertain.

After explicit numerical review, prior authoring declarations move to inactive
source history and the active declaration records authored ownership. This does
not resolve independent external-source conflicts or discard their alternatives.
Repeated preparation is deterministic and deduplicates retained evidence.
Source snapshots increase profile size; existing inspection/editor limits remain
applicable, and no automatic pruning or new archive system is introduced.

## Existing controls and the correction workflow

Guided fields maintain ordinary descriptions and argument declarations. The full
numerical contract, shared definitions, positional components and review evidence
remain editable through the existing **Edit JSON** action; a second schema editor
is not introduced.

1. Use **Options**, **Categories**, **Driver** or **Edit JSON** to make the edit.
   Guided operations report numerical declarations retained for review.
2. When a declaration was made inactive, inspect `documentation.alternatives`.
   Restore only corrected metadata to the intended active field. Restore required
   definitions from its source-scoped closure under appropriate names; do not
   assume a same-named current definition means the same thing.
3. Correct meaning, forms, applicability, provenance, review status and any
   investigation using the [existing contract](../numerical-value-contract.md).
   Preserve source-derived or unresolved status when evidence remains incomplete.
4. Select **n — Numerical review**. Inspect explanations, diagnostics, explicit
   definition consumers and unannotated value-bearing entries. Missing metadata
   does not by itself classify an argument as numerical or establish a defect.
5. Acknowledge the current declarations only after reviewing their cited scope
   and evidence. The acknowledgement is a transient draft baseline, not a stored
   approval record or a change to `review.status`. Lossless moves retain it;
   later semantic changes require fresh review.
6. Preview the explanation and search behavior, then use the existing Validate
   and Save actions. Pending numerical review is reported before the existing
   save confirmation. Save remains explicit; preview writes neither files nor
   draft text.

New complete profiles supplied to the collection API retain their declared
metadata. The API does not establish the truth of that declaration. For changes
to existing content, programmatic callers can explicitly select
`numerical_reviewed=True` only after the corresponding source review. It must not
be derived from a successful validator result.

`validate_authored_profile(profile, source, alias_groups=...)` delegates to the
shared structural validator and raises `NumericalAuthoringError` with structured
diagnostics. Explicit alias groups can be supplied by callers that own that
relationship. No persisted alias grammar is invented and matching summaries are
not treated as alias declarations. Shared references are checked and scoped using
the existing contract. Maintained completeness remains a separately selected API
policy and is not enabled by saving or inspecting legacy profiles.

## Preview, uncertainty and recovery

Preview deactivates potentially stale guidance in a temporary view. It can defer
a changed-library review error while withholding its affected active consumers.
Saving retains the blocking review requirement. Structurally malformed optional
metadata uses the existing browser fallback without turning preview into a strict
loading gate. Invalid JSON or legacy command grammar still requires correction.

Collection findings include shared `sem_*` diagnostics with source, pointer,
command, option/component and correction guidance. Explicit source-derived,
unresolved or incomplete metadata produces warnings; malformed active metadata
produces errors. Absent legacy fields do not generate completeness findings.
Pending inactive authoring declarations produce `authoring_semantics_review`.
Inactive evidence is not validated or presented as an active numerical claim.

Existing locks, file-change checks, per-file atomic writes, save-failure handling,
backups and byte-preserving recovery remain. Pair/report writes are not a single
filesystem transaction. Cancellation changes no saved files, and recovery does
not automatically promote inactive declarations, delete files or break locks.
Restored candidates must pass the existing pair checks plus structural validation
of supplied optional numerical metadata before any restoration writes.

## Verification and limits

Focused tests cover guided and raw edits, mocked editor invocation, replacement
imports, fixed bulk records, shared definitions, positional components, explicit
aliases, review acknowledgement, preview, save/reload, cancellation, concurrency
and failed saves. Lossless serialization/reordering checks enumerate every bundled
profile; real semantic expectations remain grounded in the existing migration
fixtures. Synthetic lifecycle changes do not establish new upstream behavior.

The passive harness blocks process launches, target probes and network entry
points. Windows test directories use inherited permissions only in selected
disposable repository-cache locations; production permissions are unchanged.
The native Bash fixture is replaced by a stand-in that refuses construction, and
terminal/process fixtures are excluded. Native POSIX collection descriptor,
symlink and restoration scenarios remain platform exclusions. WSL enumeration
was denied on this host, so no WSL or native Linux result is claimed. The new
numerical findings and pre-write validation are tested directly, while unchanged
filesystem/recovery mechanics receive independent source comparisons.

Run focused checks without target programs or network operations:

```bash
python -B -m unittest discover -s tests -p test_numerical_authoring.py -v
python -B -m unittest discover -s tests -p test_value_semantics.py -v
python -B -m unittest discover -s tests -p test_numerical_migration.py -v
python -B -m unittest discover -s tests -p test_documentation_preservation.py -v
python -B -m unittest discover -s tests -p test_numerical_presentation.py -v
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
python -B scripts/inventory_numerical_descriptions.py --check --summary
python -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -B cli_help/main.py --check
```

On Windows, `python -X utf8 -B` also selects UTF-8 console output. Exact passive
test selections, exclusions, workflow enumeration and static comparisons are
recorded under ignored `tests/reports/numerical-inventory/step6-*.json`.

At Step 6 the census contained 76 profiles, 942 option records, 327 explicit named
paths, 5,243 canonical option/keyword identities, 7,591 parsed observations,
341 input sources and 6,119 review identities. Counts overlap and are not
additive. That focused census did not fingerprint these authoring owners; no
entry fingerprint or numerical evidence classification is refreshed. AC-09 and
F7 record the scoped authoring implementation and its platform limits.

Step 6 is complete within these help-content authoring boundaries. Numerical
truth, complete external grammars and native terminal/POSIX acceptance retain
their stated evidence limits. No architectural decision blocks this implementation.
Command-specific enrichment, global enforcement, CI and Git/GitHub configuration
are unchanged. The next plan step is Step 7: enforce future coverage automatically.

Subsequent [Step 7 enforcement](step7-enforcement.md) adds those protected owners
and prospective checks. [Step 8 integration verification](step8-verification.md)
records current cross-component evidence, unchanged migration debt and native
acceptance limits. The preceding counts and boundaries describe Step 6 itself.
