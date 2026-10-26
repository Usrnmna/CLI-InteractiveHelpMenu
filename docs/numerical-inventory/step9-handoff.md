# Final repository configuration review and local handoff

[Implementation inventory](README.md) · [Integrated verification](step8-verification.md) · [Repository policy guide](../development.md#repository-configuration)

This account retains the Step 9 configuration-review snapshot. The subsequent
[maintained debt resolution](debt-resolution.md) completes its recorded strict
debt without reopening configuration or supplying native acceptance evidence.
The later [native/POSIX verification](native-posix-verification.md) supplies
scoped Ubuntu terminal and filesystem evidence with explicit remaining limits.

Step 9 is complete within the final configuration-review and local-handoff scope.
The only source-policy correction excludes checkout-local installed application
data from release-source selection. Numerical migration, runtime integration and
compatibility remain unchanged. Prospective enforcement passes; full maintained
completeness and native terminal acceptance remain unfulfilled.

## Starting and ending state

The starting checkout was clean on `main` at
`45a9c898938ad0a67a440af698378e5da601578e`. The ending branch and revision are
unchanged. The local delta contains six unstaged files: the source-selection
policy, its tests, this new handoff and three documentation links/clarifications.
No pre-existing working-tree edits required reconciliation. Baseline hashes cover
494 tracked files; independent final comparisons preserve all other tracked
bytes and the actual Git index.

| Changed file | Purpose |
| --- | --- |
| [scripts/build_release.py](../../scripts/build_release.py) | Add one exact reserved private-directory prefix to source-selection policy; no build logic changes |
| [tests/test_repository_config.py](../../tests/test_repository_config.py) | Reuse the passive policy loader; test private-directory exclusion, similarly named maintained directories, source growth and effective attributes |
| [docs/development.md](../development.md#repository-configuration) | Explain source selection separately from Git ignore and distinguish declared LF from existing bytes |
| [docs/README.md](../README.md) | Link the final handoff from the development index |
| [docs/numerical-inventory/README.md](README.md) | Link the final configuration evidence and remaining acceptance limits |
| This document | Record the final local result and its reproducible evidence |

## Artifact ownership and policy dispositions

The review follows actual enumeration, serializers, save paths and source roots.
Trackability denotes eligibility under project rules, not staging or publication.

| Artifact class and owner | Maintained or generated disposition |
| --- | --- |
| `cli_help/*.py`, `profiles/*.json`; runtime loader and profile owners | Maintained and trackable; source selection and the existing installer payload globs include numerical modules/profiles |
| `docs/numerical-inventory/review.json`; inventory and coverage tools | Curated review/coverage policy, not generated; trackable and explicitly unmarked as generated |
| `tests/test_*numerical*.py`, contract/policy tests, `tests/fixtures/help/`, `tests/fixtures/value-semantics/` | Maintained tests, raw captures, synthetic specimens and semantic references; trackable and kept distinct |
| Numerical guides and contributor/development references | Maintained Markdown; trackable and eligible for normal documentation scanning |
| `tests/reports/numerical-inventory/`, `tests/reports/ci/`; explicit report writers | Generated local evidence; ignored and excluded from release sources/general link traversal |
| `.cache/`; test harnesses, snapshots and application caches | Disposable/generated evidence; ignored, excluded from source selection and general link traversal |
| `generated-help/`, default installed application data and collection recovery/lock files | Generated or private; established bounded rules apply. Arbitrary custom collection/output paths still require deliberate placement and review |
| Bytecode, owned temporary writes, editor swap files and review backups | Generated/recoverable private state; existing ignore/source rules suffice; nothing is deleted |
| `dist/` versus `releases/` | New local build output remains excluded; curated historical release artifacts remain trackable, byte-preserved and unbuilt |

| Configuration owner reviewed | Disposition and evidence |
| --- | --- |
| [.gitignore](../../.gitignore); applicable nested rules | No change. Effective `check-ignore --no-index` admits maintained inputs and excludes representative reports, caches, sessions, backups, locks, tool credentials and default installed data. No maintained nested override was found in scope |
| [.gitattributes](../../.gitattributes) | No change. Effective text/LF attributes cover numerical Python/JSON/Markdown/captures/YAML; curated review data is not generated/vendored. Binary attributes remain set for media, compressed manuals and native launchers |
| [.editorconfig](../../.editorconfig) | No change. UTF-8/LF defaults, significant fixture/Markdown whitespace and transformation exclusions for generated/binary paths remain suitable. Declared rules were inspected; no native editor ran |
| [.github/workflows/ci.yml](../../.github/workflows/ci.yml) and [tests/run.sh](../../tests/run.sh) | No change. Reconciliation and the same prospective policy have nonignored exit status; unittest discovers the focused tests. Strict debt is not made a mandatory green gate. Named report retention avoids raw captures, caches and full local inventories |
| [.github/dependabot.yml](../../.github/dependabot.yml), issue forms, PR template and [contribution guide](../../.github/CONTRIBUTING.md) | No change. No dependency or permission need arises; existing synthetic-reproduction, evidence and generated-file guidance remains applicable |
| [lychee.toml](../../lychee.toml) and [link retry controller](../../scripts/retry_documentation_links.py) | No change. Private/generated paths are excluded while maintained guides remain included. The initial diagnostic check is followed by the existing strict bounded-retry decision; no live link scan was run |
| [Release-source policy](../../scripts/build_release.py) | One exact exclusion added for `.local/share/cli-interactive-help` at any depth; existing source roots and other private rules remain unchanged |
| [Installer payload selection](../../scripts/installation.py) | No change. Static literal-pattern inspection admits all current runtime Python modules and bundled profiles; no installer/build/package lifecycle ran |

Git ignore already excluded `tools/home/.local/share/cli-interactive-help/`, and
link-scan rules already excluded that directory. The independent source selector
previously admitted its files under the maintained `tools/` root. The added
prefix closes that mismatch without excluding
`cli-interactive-help-reference/`. A new regression failed before the correction
and passed afterward. Inert synthetic growth tests exercise the real selector;
no private profile or installed application is executed or packaged.

Byte inspection found 85 existing CRLF working files: 16 profiles and 69 help
fixtures. Git reports LF index blobs and `text eol=lf` attributes for these paths.
All inspected maintained text decodes as UTF-8; no BOM or missing final newline
was found. Current checkout bytes therefore differ from the declared LF policy.
These files retain their exact starting bytes. No renormalization, raw-capture
rewrite or Git configuration change is part of this review. All six changed or
new maintained files use UTF-8 without BOM and LF.

## Numerical implementation and audit mapping

The existing [contract](../numerical-value-contract.md), shared validator,
formatter, presentation helpers and authoring preparation remain the single
implementation path. The following mapping describes current scope; it does not
assert that every upstream numerical claim or captured option is verified.

| Audit finding | Implementation and remaining boundary |
| --- | --- |
| F1: bandwidth/rate meaning | [Step 3](step3-migration.md#principal-corrections-and-evidence) supplies scoped rate corrections and metadata; [Step 5](step5-presentation.md) exposes units and scale. Unlisted releases and unresolved contracts remain outside verified coverage |
| F2: literal size/frequency scale | Step 3 separates accepted tokens from actual multipliers, including chip/release variants; hardware behavior and unlisted chips are not established |
| F3: time values and expressions | Step 3 distinguishes scalar units, unit-bearing expressions, timestamps, omitted operands and sentinels; delegated/version-specific investigations remain explicit |
| F4: counts, indices, levels and composite meaning | The contract and Step 3 provide relevant subjects/components instead of invented physical units. Remaining text/path/enumeration contracts are included honestly in strict debt |
| F5: source transformations | [Step 4](step4-preservation.md) retains shared prose, ownership, provenance, atomic semantic declarations and cache data. [Step 8](step8-verification.md) records the scalar-arity merge repair; cache generation remains 12 |
| F6: visibility/search | [Step 5](step5-presentation.md) uses derived list/details/search text with accessible qualifications. Portable/fake-window evidence does not supply missing native terminal acceptance |
| F7: future additions | [Step 6](step6-authoring.md) protects authoring lifecycles; [Step 7](step7-enforcement.md) discovers maintained growth and enforces prospective completeness/propagation with exact deferrals. Full maintained strict completeness remains unmet |

The recorded factual evidence is bounded. Examples include rsync 3.4.1,
OpenSSH Portable 9.9p2, FFmpeg 7.1, Go 1.24.0, fzf 0.60.3 and chip-specific
esptool 4.8.1/5.0.2 declarations. The Step 3 account and per-entry provenance own
the authoritative links and exact scopes. Step 9 does not reverify those command
facts, extend them to other releases or infer installed-target/hardware behavior.

## Current inventory and enforcement

Fresh reconciliation reports zero diagnostics and the following unchanged census:

| Count | Definition |
| --- | --- |
| 76 profiles; 96 categories; 942 option/keyword records | Bundled authored records; aliases are separate records |
| 463 value-bearing; 28 keywords; 6 optional-value records | Overlapping subsets of the authored records |
| 22 definitions; 3 positional groups with 6 components | Shared semantic nodes and repeated argument documentation; not extra options |
| 144 built-in paths; 50 driver files with 155 explicit routes | Distinct route sources, including intermediate groups |
| 327 explicit named paths; 165 outside the primary matrix | Reconciled union and its matrix relationship; not complete option coverage |
| 50 implicit driver roots, including 18 implicit-only; 12 module paths; 8 interpreter flag forms | Separate invocation/default observations |
| 162 primary cases and 948 flag expectations; 263 overlapping matrix records | Sentinel/expectation scope, not complete grammars |
| 170 embedded help sources; 7,591 parsed observations | Captures and synthetic sources beyond matrix sentinels |
| 5,243 canonical option/keyword identities | Reconciled logical identities across authored, parsed and declaration-only observations |
| 356 inputs; 6,159 inventory identities | Entire protected census, including sources/routes/categories/definitions |
| 30 numeric fixed spellings; 67 editing scenarios | Candidate spellings and maintained scenarios, not verified numerical facts |

These totals overlap and must not be added together. The wider generic-discovery
surface remains open-ended; installed programs were not enumerated.

Prospective mode passes the active inventory-review, supplied-structure,
maintained-prospective, display/search-propagation and exact-deferral gates.
Strict mode returns exit 1 with **360 incomplete records and 414 errors**:
304 option/keyword records lack metadata, 47 option/keyword records retain
source-derived investigations and nine shared definitions remain source-derived.
Definitions overlap consumers. Missing contracts include text/path values and
named enumerations; this is not a count of proven missing physical units.
The gate reports 504 required contract records, 144 complete records, three
secondary heuristic warnings and ten external informational diagnostics.

The [exact debt policy](step7-enforcement.md#exact-debt-baseline-and-exceptions)
is unchanged; individual exceptions remain empty. Each debt allowance is bound
to its exact source/identity, permitted codes, authored facts and review hash.
Relevant contract, grammar, profile/category, transitive-definition or review
changes invalidate it. New siblings, consumers, profiles or fixtures cannot
inherit it. Resolving debt requires separately authorized migration/evidence
work, not expansion, silent refresh or a factual-status promotion.

No review group, member, fingerprint, criterion, debt row or exception changed.
The Step 9 policy/test/documentation files do not change the protected inventory.

## Verification evidence and limits

| Evidence produced during Step 9 | Result and limit |
| --- | --- |
| Nine repository-policy tests | Passed, including pre-fix failure/repaired success, effective ignore/attributes, source growth and private-prefix counterexample |
| Thirteen documentation retry-controller tests | Passed with process/HTTP/time responses mocked; no real Lychee, HTTP probe or delay |
| Effective current ignore/attribute rules and byte inspection | Maintained numerical inputs eligible; generated/private samples excluded; binary/text policy preserved. Existing CRLF observations retained separately |
| Editor, workflow, runner, upload and link-exclusion inspection | Declared rules/YAML parse and intended gate/failure/report paths pass; no native editor, link scan or hosted workflow result |
| Passive release-source and installer-input inspection | Maintained numerical files eligible and reserved outputs excluded; no archive, native build, install or package-lifecycle claim |
| Fresh inventory and prospective/strict CLI checks | Reconciliation/prospective pass; strict reports the unchanged debt above |
| Final protected-state comparison | Runtime modules, all 76 profiles, 209 fixture files, 11 tracked historical release files, numerical policy/review and all unrelated tracked bytes preserved; revision/index unchanged |

The focused run totals **22 tests passed, no skips**. Normal test discovery
includes the new tests. Process guards permit only read-only Git policy queries
and `git init` inside verified disposable repositories. Network/other processes
are blocked. Temporary directories use inherited Windows permissions beneath
the selected ignored Step 9 cache; application permissions are unchanged.

The existing Step 8 acceptance matrix is retained, not rerun wholesale: 12
criteria passed, AC-02/AC-08 retain native acceptance gaps and AC-04 retains
deferred maintained completeness. Its 379-test selection (362 passed, 17 skipped)
is historical evidence. The recorded Bash signal-pipe and WSL access failures
were not reprobed in Step 9. Native Bash/Readline, POSIX restoration, actual
terminal resize/reopen, installed targets, package lifecycles and hosted CI
remain unestablished by this configuration review.

Generated local evidence resides under `tests/reports/numerical-inventory/`:
`step9-tests.json`, `step9-policies.json`, `step9-verification.json`,
`step9-coverage.json` and `step9-strict.json`. Baseline reports use the
`step9-baseline-` prefix. Deterministic report content uses repository-relative
references; the separately retained local baseline/harness resides under
`.cache/numerical-handoff-step9/`. These outputs remain ignored, are not added to
CI uploads and are not automatically suitable for publication.

## Reproduction and future handoff

Run from the repository root; Python/Git must already be available:

```bash
python -X utf8 -B -m unittest discover -s tests -p test_repository_config.py -v
python -X utf8 -B -m unittest discover -s tests -p test_documentation_links.py -v
python -X utf8 -B scripts/inventory_numerical_descriptions.py --check --summary
python -X utf8 -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --output tests/reports/numerical-inventory/step9-coverage.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --mode strict --output tests/reports/numerical-inventory/step9-strict.json --summary
git check-ignore --no-index tools/home/.local/share/cli-interactive-help/profiles/private.json
git check-attr text eol linguist-generated -- docs/numerical-inventory/review.json
git diff --check
```

The strict command currently exits 1 for documented debt. `check-ignore` returns
1 for a maintained path that is correctly not ignored. No staging is required.
The retained local harnesses reproduce the stronger guarded run and actual
source-list checks without building anything:

```bash
python -X utf8 -B .cache/numerical-handoff-step9/run_policy_tests.py
python -X utf8 -B .cache/numerical-handoff-step9/inspect_policies.py
python -X utf8 -B .cache/numerical-handoff-step9/verify_final.py
```

The local final verifier compares against this review's original baseline;
future deliberate edits require a new baseline, not an automatic refresh of
historical assertions. The general Linux runner includes out-of-scope process,
terminal and package tests and must not be executed blindly under these limits.

Remaining work requires separate scope: investigate/migrate exact strict debt;
obtain accessible native acceptance evidence; and review any discovered factual
or architectural defect before implementation. Arbitrary custom output homes
still need manifest/privacy review. Existing CRLF checkout bytes do not warrant
rewriting captures during this task; any future normalization needs a bounded
byte-preservation decision.

A future commit needs separate authorization and review of the exact intended
diff, local evidence and acknowledged limitations. A claim of full maintained
completeness additionally requires applicable factual evidence, resolved debt,
strict-mode success and removal of resolved allowances. Publication/release
requires separate authorization and its own current source/artifact/native
checks; none is supplied by this passive handoff.

All changes remain local, unstaged and uncommitted. No online GitHub files or
settings, hosted workflows, repository history, remotes, hooks or Git
configuration changed. No additional production migration, command enrichment,
compatibility expansion, runtime redesign, package/release work or unrelated
configuration overhaul was performed.
