# Numerical description implementation inventory

The inventory reconciles bundled options, discovery fixtures and route declarations with their source-specific reviews. For everyday use of numerical help, see [browser controls](../usage.md#browser-controls). For the wider project, see the [command-help audit history](../audit-history.md).

## Current enumeration and counting rules

| Local checkout, November 26, 2026 | Count | What is counted |
| --- | ---: | --- |
| Bundled profiles and categories | 76 / 302 | Authored containers |
| Option and keyword records | 6,487 | Includes 96 keyword records. Aliases occupy separate rows. |
| Records taking a value | 3,875 | Includes 197 optional-value records |
| Shared value definitions / positional groups | 327 / 3 | A definition may supply multiple options. Each repeated positional group has two components. |
| Applicable numerical or operand contracts | 4,426 | Required option, keyword, positional and definition records under the maintained coverage policy |
| Explicit named paths | 444 | Union of built-ins, driver paths, bundled profiles and primary matrix cases |
| Primary matrix | 162 cases / 948 expectations | Selected assertions about command help |
| Embedded sources / parsed observations | 170 / 7,015 | Includes captured help and synthetic specimens |
| Canonical option and keyword identities | 8,430 | Reconciles authored, parsed, arity-only and expected identities by command and flag |
| Inventory identities / input files | 10,081 / 463 | Includes source, path and component identities as well as options |

These populations overlap. A declared route establishes how help is requested. A fixture establishes what its captured or synthetic text contains. Neither establishes every option available in an installed edition. The 942 original authored records are the baseline for the manual revisits. [Bundled expansion by family](../audit-history.md#bundled-menu-progress)

## Prioritized implementation work

| Development phase | Finding and outcome | Detailed evidence |
| --- | --- | --- |
| 1. Inventory and contract (Steps 1–2) | The original audit flagged rates, suffixes, time expressions and counts. The inventory assigned stable identities. Optional metadata describes bare numbers, literal forms, applicability and evidence. | [Review assignments and original acceptance criteria](review.json) · [Value contract](../numerical-value-contract.md) |
| 2. Migrate and preserve (Steps 3–4) | The first migration supplied metadata on 175 options across 56 profiles. Source parsing, merging and caching retained shared documentation, competing versions and unassigned text. | [Per-family corrections](step3-migration.md) · [Preservation and merge rules](step4-preservation.md) |
| 3. Display, edit and enforce (Steps 5–7) | Search and selected details exposed documented units. Authoring retained inactive evidence when edits invalidated a declaration. Prospective and strict checks distinguished new omissions from the 360 incomplete records then known. | [Presentation](step5-presentation.md) · [Authoring](step6-authoring.md) · [Coverage policy](step7-enforcement.md) |
| 4. Integrate and hand off (Steps 8–9) | End-to-end tests exposed a scalar declaration applied to the wrong operand count. Repository review corrected a release-source exclusion. Windows passive checks and native terminal acceptance were recorded separately. | [Integration and acceptance matrix](step8-verification.md) · [Configuration review](step9-handoff.md) |
| 5. Resolve debt and investigate diagnostics | Evidence review closed the 360 incomplete records in the original 504-contract population. Subsequent investigations corrected operand and section associations while retaining unresolved external facts. | [Debt resolution](debt-resolution.md) · [Diagnostic dispositions](diagnostic-investigation.md) · [Parser repairs](parser-association-repairs.md) |
| 6. Verify terminals and expand the menus | Real Bash/Readline, ext4 and separately qualified 9p checks followed. The family revisits expanded the bundled profiles. The redesigned browser exposes units in all three levels and keeps citations out of terminal explanations. | [Native/POSIX evidence](native-posix-verification.md) · [Historical Linux matrix](full-linux-verification.md) · [Three-level terminal captures](../superpowers/plans/2026-11-24-menu-detail-levels-verification.md) |

## Artifacts and regeneration

Run these commands from the repository root. The first checks the current census and exact review assignments. The second checks maintained contracts, including display and search propagation. The third writes an optional local inventory.

```bash
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
python3 -B scripts/inventory_numerical_descriptions.py --check \
  --output tests/reports/numerical-inventory/inventory.json --summary
```

The [generator](../../scripts/inventory_numerical_descriptions.py) uses the checkout’s parsers and validator without running target programs or rendering manuals. It reads routing literals as data. Generated JSON stores shared provenance by digest and includes the source locator and digest for long excerpts. The curated assignments in [review.json](review.json) remain the maintained input. [Generator tests](../../tests/test_numerical_inventory.py)

## Relationships and review identity

An identity such as `option|rsync|--bwlimit` follows the command and case-sensitive flag across category moves. A trailing equals sign is preserved in the source observation. Short and long spellings have separate identities. Each observation records its role, file and JSON pointer or source line. Versioned claims, guards and references stay attached to their evidence. Unassigned text and unrendered roff keep their source-only status.

Review groups share a rationale. Each member has an exact identity and a source-sensitive fingerprint. New or changed facts require review. Missing, stale, duplicate, conflicting or orphaned assignments fail reconciliation. Inspect the changed source before updating the affected member. A reviewed external observation may still carry an explicit investigation.

## Acceptance and protected behavior

The original S1 criteria covered census, identity stability, reconciliation, passive determinism and output safety. AC-01 through AC-10 covered insertion and cancellation, numerical meaning, source retention, presentation, authoring and future additions. The [criterion-by-criterion matrix](step8-verification.md#acceptance-matrix) identifies which checks passed at that stage and which needed native or factual follow-up.

## Handoff boundary

When a profile, fixture or protected source changes, rerun reconciliation and the coverage gate. For an option change, compare the source edition and literal operand syntax, then inspect its searchable terms and reachable guidance in the menu. The [audit procedure](../development.md#auditing-command-help) describes terminal and compatibility checks. Historical counts in the linked reports refer to the checkout named in each report.
