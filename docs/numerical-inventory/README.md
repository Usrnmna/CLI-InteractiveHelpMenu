# Numerical description implementation inventory

[Documentation index](../README.md) · [Inventory generator](../../scripts/inventory_numerical_descriptions.py)

This directory owns the reproducible implementation inventory, planning reviews
and acceptance criteria for numerical option descriptions. Step 1 established
the inventory; the [Step 3 bundled migration](step3-migration.md) records current
description corrections and opt-in metadata. Inventory classifications remain
planning annotations rather than a production numerical validation policy.

The supplied `audit_report.rtf` and `recommended_steps.rtf` establish the task
context. Their findings are evidence and recommendations, not authorization for
later implementation steps. The reference revision is
`cda11feb600520d16a3302e96b51ea9895e3a7d2`; current counts are recalculated rather
than asserted as permanent constants.

## Artifacts and regeneration

| Artifact | Ownership |
| --- | --- |
| `scripts/inventory_numerical_descriptions.py` | Maintained repository-only enumeration and annotation reconciliation |
| [review.json](review.json) | Maintained review groups, exact member identities/fingerprints, work items, and acceptance criteria |
| `tests/reports/numerical-inventory/inventory.json` | Regenerable local facts and joined reviews; ignored under the existing report policy |
| [Focused tests](../../tests/test_numerical_inventory.py) | Discovery growth, source relationships, passive operation, output limits, and review integrity |
| [Bundled migration account](step3-migration.md) | Corrected content, scoped source evidence, unresolved investigations and passive verification |
| [Maintained debt resolution](debt-resolution.md) | Subsequent completion of the exact maintained contracts, source corrections, strict success and remaining external/native limits |
| [Diagnostic investigation](diagnostic-investigation.md) | Exact heuristic dispositions, complete external membership tracing, bounded source comparisons and remaining parser/provenance limits |
| [Operand and association repairs](parser-association-repairs.md) | Compound operands, nested context, declared manual scope, exact census changes and passive verification |

Run from the repository root with Python 3.10 or newer:

```bash
python -B scripts/inventory_numerical_descriptions.py --check --summary
python -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
```

On Windows, `python -X utf8 -B` also ensures UTF-8 console output. No dependency
installation, installed target, manual renderer, Git request, or network request
is required. The generator imports the trusted checkout's existing pure help
parsers and structural profile validator. It does not call discovery, probe,
installation, or execution helpers. Routing declarations in the inspected
snapshot are read as AST literals; arbitrary source expressions are not evaluated.

Without `--output`, all results go to stdout. `--summary` limits stdout to counts
and reconciliation totals. `--root` selects a repository snapshot; `--reviews`
selects an annotation file. Output paths are explicit and relative to the current
directory unless absolute. Existing inspected inputs, review annotations, links,
source directories, and unrelated existing files are protected from replacement.
An existing inventory artifact can be regenerated. No output is created by
`--check` alone.

The generated inventory is intentionally compact machine-readable JSON rather
than a second copy of the human report. Large provenance contexts are shared by
digest. Long option details retain a labeled 600-character excerpt and the full
detail's digest; the source locator remains the owner of complete text.

## Current enumeration and counting rules

The current census produces the following overlapping counts. Regeneration,
rather than these recorded totals, establishes coverage after future changes:

| Count | Meaning |
| --- | --- |
| 76 profiles, 96 categories | Bundled authored containers |
| 942 option records, 463 value-bearing records | Authored records, including aliases as separate flags |
| 28 keyword records, 6 optional-value records | Subsets of the authored option total |
| 26 numeric fixed spellings | Parsed literal flags such as `-1`; four incorrect root associations were retired, and digits alone do not establish numerical meaning |
| 3 repeated positional groups, 6 components | Positional documentation outside ordinary options |
| 50 example driver files, 155 declared routes | Explicit JSON routes, including intermediate groups |
| 144 built-in paths | Git/Docker roots and explicit paths |
| 327 explicit named paths | Union of built-ins, explicit driver routes, bundled profiles, and primary matrix cases |
| 165 explicit paths outside the primary matrix | A coverage relationship, not 165 established defects |
| 50 default-driver-root observations, 18 implicit-only roots | Default root behavior distinguished from explicit root declarations |
| 12 interpreter/module invocation paths | Both interpreter spellings with bounded pip/pytest paths; excluded from the 327-path total |
| 162 primary cases, 948 flag expectations | Primary compatibility matrix; expectations are not complete option grammars |
| 263 matrix records | Primary and supplementary lists, intentionally overlapping |
| 170 embedded help sources, 7,548 parsed help observations | All recognized fixture/capture content, beyond sentinels; scoped/nested source-only material remains preserved separately |
| 5,231 canonical option/keyword identities | Authored, parsed, arity-only, and expected identities reconciled by command and flag |
| 358 source files, 6,149 total inventory identities | Includes sources, routes, descriptions, categories, definitions and components; twelve incorrect identities retire and one passive cache-inspection owner is added by the association repairs |
| 22 shared value definitions | Explicit semantic nodes and their separately reviewed consumers |

The audit's principal profile and explicit-path counts match. Broader observation
counts are new enumeration results, not evidence of additional verified command
support. These totals must not be added together. Fixture excerpts, synthetic
specimens, source requests, and declared routes establish different boundaries.

The review retains 12 `shared_documentation_preserved` identities, 23
`source_text_preserved` identities and 4,215 `investigate` dispositions, with
additional exact bounded-review and context-investigation groups described in
the [diagnostic investigation](diagnostic-investigation.md).
There are 4,237 unresolved classifications, principally external observations and
arity-only declarations. Subsequent maintained debt resolution completes 351
option/keyword contracts and nine definitions; the original 128 verified
option records and six positional components remain separately reviewed.
All 479 maintained option/keyword contracts, three positional groups and 22
definitions now pass strict validation. Every identity has a disposition, but
this is not a completed semantic audit of external manuals or installed versions.
Step 7 added 25 `existing_declaration_enumerated` records and protected the
relevant numerical, authoring and validation owners. The Step 1 counts of 341
sources and 6,119 identities remain historical evidence rather than requirements.

## Relationships and review identity

The `entries` array preserves each logical identity and all observed sources:

- `option|rsync|--bwlimit` identifies an option independently of its category or
  current array position. A trailing equals sign is retained in observations but
  removed from this logical key. Case remains significant.
- Short and long aliases remain separate identities. Explicit declaration aliases
  appear in observations; matching summaries alone do not establish aliasing.
- Matrix expectations and routing arity declarations set `display_content: false`.
  They do not invent displayed descriptions or authoritative units.
- Version-specific flag/arity assertions and keyword sentinels remain explicit
  expectations. A textual keyword sentinel is not promoted into an insertable
  menu keyword.
- Routes carry distinct origin roles, an explicit-child relationship, and a
  maintained-content indicator. Having children does not prove a group has no
  options, and having parsed content does not prove complete coverage.
- `<selected-python> -m ...` is a capture ownership placeholder, not an executable
  name or a newly supported route. Captures do not establish which interpreter
  spelling selected the module.
- `source.path` is repository-relative. `pointer` locates JSON data; `text_line`
  refers to the decoded help string. Ordinary text observations use `line`.

Provenance resides in `contexts`, referenced by observations. Recorded versions,
requests, chip/identity guards and source URLs remain evidence; the generator
does not perform those requests. The [source preservation reference](step4-preservation.md)
defines bounded shared-footer association; ambiguous associations and unsupported
formats remain explicit limitations. Raw roff is indexed as unrendered;
manual rendering is not performed. Source-only or unassigned content must not be
reported as a verified complete option inventory.

Generic executable discovery is open-ended. The tool neither scans `PATH` nor
enumerates installed programs. Unusual or newly introduced routing declaration
syntax requires a reader update rather than evaluation of source expressions.

Review groups share descriptive rationale, while exact IDs and source-sensitive
fingerprints enumerate their members. The generated entry retains its current
placeholder, summary, source, category, and applicability context alongside its
review-group reference. This avoids thousands of duplicated paragraphs.

New entries receive `review_missing`; changed facts receive `review_stale`.
Duplicate membership, conflicting decisions, orphaned members, invalid groups,
missing fixtures, and unassigned parsed text are reported separately.
`--check` fails for reconciliation problems. It does not fail merely because an
explicit review disposition requires investigation, and it is not Step 2's
future numerical-quality gate.

Regeneration never rewrites `review.json`. Review the exact changed source before
updating its annotation, fingerprint, or group. Do not bulk-refresh fingerprints
to suppress errors. A new source observation can require renewed review even
when the command and flag name are unchanged. Unrelated source offsets are not
part of option identity. Source-file identities deliberately track the complete
normalized text so newly added source content also requires census acknowledgment.

## Prioritized implementation work

The machine-readable `system_work_items` and review groups identify owners,
sources, evidence status, applicability, proposed actions, priority, later plan
steps, verification requirements, and acceptance criteria.

| Priority | Finding | Recommended later work | Plan steps |
| --- | --- | --- | --- |
| P1 | F1 rates | Verify base rate, bit/byte meaning, suffixes and special cases for rsync, FFmpeg and related entries | 2, 3 |
| P1 | F2 scale | Preserve command-specific flash tokens and verify scale/version/chip interpretation; do not universalize suffixes | 2, 3 |
| P1 | F3 time | Separate seconds, unit-bearing durations, calendar/relative expressions and sentinel behavior | 2, 3 |
| P2 | F4 numerical meaning | Explain counts, levels, widths, mixed percentages, identifiers and composite/delegated forms | 2, 3 |
| P1 | F5 source handling | Preserve shared GNU definitions, report conflicting sources and review relevant cache behavior | 4, 6, 8 |
| P2 | F6 display | Expose essential meaning early and retain it through search, wrapping and scrolling | 5, 8 |
| P1 | F7 future enforcement | Establish the shared contract, maintain it through authoring, and discover new maintained entries automatically | 2, 6, 7, 8 |

P1/P2/P3 are planning priorities, not a runtime severity policy. The original
79-entry set is a seed rather than an exclusion list. Additional examined records
include GNU byte/size suffixes, sort memory and key syntax, Git fetch counts,
XZ thread counts, module timeouts, IP keywords, delegated configuration, and
VLC's unresolved synthetic numeric scales. Serial settings and legacy/chip
observations and unreviewed versions retain explicit investigation requirements. Neither a missing detail
field nor a numeric-looking name alone establishes a unit defect.

## Acceptance and protected behavior

The full criteria are maintained in `review.json`; the following separation
prevents Step 1 checks from being represented as completed runtime fixes.

| Criteria | Verification status and scope |
| --- | --- |
| S1-01 input census | Independently compare file, profile, matrix and driver counts and compare enumerated routes with the existing passive registry loader |
| S1-02 stable review | Exercise unrelated insertion and automatic profile/fixture growth; existing identities remain associated and new identities require review |
| S1-03 reconciliation | Reject missing, stale, duplicate, conflicting and orphaned review assignments |
| S1-04 passive determinism | Block process/network entry points, inspect hostile snapshot declarations without execution, compare input hashes and repeat output |
| S1-05 explicit output | Default to stdout and reject input, annotation and unrelated-file replacement |
| AC-01 to AC-03 protected runtime | Step 3 compares protected declarations and passive buffer/cursor behavior; integrated navigation and runtime verification remain deferred |
| AC-04 to AC-06 numerical evidence | Step 3 records scoped source verification and explicit investigations; complete installed-version and external-help verification remains open |
| AC-07 source preservation | Step 4 verifies bounded shared-text association, source conflicts, metadata retention and cache invalidation; arbitrary external formats and factual completeness remain unverified |
| AC-08 presentation | Step 5 checks formatter propagation, visible cells, supported minimum sizes, Unicode, wrapping, scrolling, scripted resize/reopen and search with fake windows; native terminal/Readline acceptance remains separate |
| AC-09 authoring | Step 6 verifies import/edit/preview/save/reload, stale claims, explicit review, definitions and numerical inspection; native POSIX restoration/terminal acceptance remain platform limits |
| AC-10 future checks | Step 7 checks prospective completeness, exact debt validity and display/search propagation; the subsequent debt-resolution follow-up satisfies strict maintained readiness without changing those checks |

Focused verification runs on Windows with Python 3.13. The tests use disposable
snapshots in the existing ignored `.cache/` area and do not invoke target
executables, manual renderers, shell workloads, or network operations. The full
Linux/WSL suite and terminal/live-help checks are outside this Step 1 proof.
There is no claim of hosted CI, physical-device behavior, or installed-version
validation.

## Handoff boundary

Step 1 established the inventory and acceptance-criteria implementation. The
inventory generator does not change production descriptions, routes, parsing,
caching, rendering, insertion or GitHub settings. Repository policy and CI
reconciliation are documented separately in the
[development guide](../development.md#repository-configuration).
The guide is linked from the documentation index.

The [Step 2 numerical value contract](../numerical-value-contract.md) now provides
opt-in metadata validation and explanation formatting. It does not promote these
planning annotations into verified semantics or activate a completeness gate.
Step 2 left enumeration unchanged; Step 7 extends its census as described below.
Step 3 updates only the exact review
members and fingerprints justified by the inspected authored-content changes.

The [Step 3 migration account](step3-migration.md) distinguishes verified
corrections, adequate summaries, source-derived records and remaining external
work. The [Step 4 preservation account](step4-preservation.md) records the parser,
merge and cache guarantees and narrowly justified annotation updates.
The [Step 5 presentation account](step5-presentation.md) records consistent value
guidance, search coverage, applicability and passive layout verification.
Reconciliation is not production numerical-quality enforcement. Native terminal
acceptance and global enforcement remain separate work.

The [Step 6 authoring account](step6-authoring.md) records subsequent numerical
preservation, scoped structural validation and explicit review. Native platform
acceptance and the future global completeness gate remain separate.

The [Step 7 coverage policy and contributor workflow](step7-enforcement.md)
defines prospective checks, exact legacy debt, structured diagnostics and
separate strict-readiness reporting. Inventory reconciliation remains distinct
and never verifies upstream numerical facts.

The [Step 8 integrated verification account](step8-verification.md) joins the
existing acceptance criteria to passive test evidence, documents the bounded
scalar-arity merge repair and distinguishes native/platform gaps from portable
success. Per-criterion records reside beside the existing criteria in review.json;
generated outcomes remain under the ignored report directory.

The [Step 9 configuration review and local handoff](step9-handoff.md) records
effective ignore/attribute/editor/workflow/source-selection policies, one bounded
private-output exclusion and fresh local verification. At that review,
prospective enforcement passed; strict completeness and native acceptance
remained unfulfilled. The handoff preserves the distinction between its
configuration evidence and historical Steps 1–8 results.

The [maintained debt-resolution follow-up](debt-resolution.md) records the later
zero-debt strict result, source-bound corrections and unchanged enforcement.
Historical step accounts retain their original counts and blocked/deferred
outcomes. External-help completeness and native acceptance remain separate.
