# Project roadmap

## Remaining work

### Batch progress

Update the current unit when a provider group, layout checkpoint or target finishes, or when a blocker changes the next action. Count exact invocations in the priority review and unique shipped names in the overall review. Keep per-invocation evidence in the linked inventory.

| Phase | Work | Status | Current unit or next action |
| --- | --- | --- | --- |
| 3 | Combined verification | Next | Prepare the host, noble310 and noble312 fixtures. Batch the affected rendering and fixed-source checks on each target. |

Phase 2 completed all five routine passes, seven visual reviews and one live resize. Its bounded provider follow-up added zero declarations. [Terminal results by size](docs/audit-history.md#phase-2-terminal-audit) · [Phase 1 provider ledger](docs/ubuntu-command-coverage/phase1-review.tsv)

### Unresolved provider findings

- Reopen `/usr/bin/ptardiff -h` when a revision resolves the manual/script argument conflict.
- Reopen `/usr/sbin/lxc` and `/usr/sbin/lxd` when an applicable image or fixture identifies the installed snap revision and supplies its command tables.
- The ledger retains post-operand choices, plus and punctuation spellings, and options owned by a selected program. Reopen the affected invocation on matching provider evidence or approval for the required argument or literal representation. [Exact dispositions and reopening conditions](docs/ubuntu-coverage-audit.md#phase-2-follow-up-on-retained-guidance)

### Phase 3 — Verify one combined batch

1. Bring the provider changes, renderer, tests and sources together. Prepare the matching fixtures for `host`, `noble310` and `noble312` once. Run affected rendering and fixed-source checks together per target. Reconcile Ubuntu invocation outcomes and numerical facts, validate collections and run the strict numerical gate on the integrated profiles. Record unresolved paths and their evidence before freezing the inputs.
2. Freeze one source snapshot including required untracked files and identify each target’s fixtures. Run **one full offline suite per target** against that snapshot. Independent targets can run concurrently in isolated environments. Report each target as it finishes. If a failure requires an edit, reproduce it with the smallest affected check, then verify the corrected snapshot under the same combined gate. Record versions, snapshot and fixture identities, passes, failures and skips in the audit history. [Batch verification](docs/development.md#auditing-command-help) · [Offline target setup](docs/test-selection-plan.md#reproduce-the-paired-offline-baseline)

## Conditional decisions

| Trigger | Follow-up |
| --- | --- |
| Noble package selection changes | Revisit `magick` and `starship` when reviewing optional installation instructions. Noble's reference archive provides ImageMagick 6 and has no ranked `starship` package. Resolute has both roots. |
| New measurements identify a material runtime cost | Isolate the proposed change, repeat matched timings and confirm behavior. Selective loading, a persistent index or an additional process requires a separate architecture decision. [Performance plan](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Focused test selection still leaves substantial cost | Pilot result reuse for one bounded group. Check invalidation for changed inputs, environments, targets, fixtures and interrupted runs. Record executed, reused, failed and skipped results. Consider CI selection or sharding after local parity and measured savings. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) · [Sharding pilot](docs/test-selection-plan.md#two-shard-host-pilot) |

## How to audit a batch

Follow the [command-help audit procedure](docs/development.md#auditing-command-help) for evidence, reconciliation and verification.

## Recording progress and finishing the audit

Record the next action and any unresolved paths or blockers here. Link family results and their evidence from the [audit history](docs/audit-history.md), which also records completed performance work, edit reviews and release verification.
