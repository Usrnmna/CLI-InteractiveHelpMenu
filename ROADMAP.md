# Project roadmap

## Remaining work

### Batch progress

Update the current unit when a provider group, layout checkpoint or target finishes, or when a blocker changes the next action. Count exact invocations in the priority review and unique shipped names in the overall review. Keep per-invocation evidence in the linked inventory.

| Phase | Work | Status | Current unit or next action |
| --- | --- | --- | --- |
| 1 | Ubuntu providers | Complete | Reviewed 57/57 priority invocations and 346/346 shipped names across six images. Added selectable menus for 150 names. [Results and exceptions](docs/ubuntu-coverage-audit.md#phase-1-provider-review) |
| 1 | Terminal baseline and renderer | Complete | [Baselines and two-size fit evidence](docs/audit-history.md#phase-1-details-layout-and-terminal-evidence) ready for reuse. |
| 2 | Terminal integration and visual review | Next | Start the 60×16 routine pass. Track 0/5 routine sizes and 0/7 complete visual reviews. Reuse the rsync captures at two sizes, then check live resize. |
| 3 | Combined verification | Planned | Track focused checks by target, inventory and strict-gate results, then each target’s full result. |

### Ubuntu command coverage expansion

The Phase 1 provider ledger records all 347 invocations and exact image results. Revisit `/usr/bin/ptardiff -h` if the provider resolves the manual/script conflict. The command tables for the shipped `lxc` and `lxd` wrappers depend on the separately installed snap revision. Post-operand choices and unsupported literal shapes remain listed by invocation. [Provider audit](docs/ubuntu-coverage-audit.md#phase-1-provider-review) · [Per-invocation findings](docs/ubuntu-command-coverage/phase1-review.tsv)

### Phase 2 — Verify terminal behavior and review the same captures

Once the renderer is stable, run one compact integration pass at each of the five routine sizes below. Preserve existing coverage at other dimensions and reuse matching assertions. At each routine size, check short-menu spacing and footer clearance, rsync entry order and scrolling, and FFmpeg selection visibility and final-entry reachability. Perform one live wide-to-narrow resize with Details open. Check that columns recalculate, selection stays visible and all details remain reachable.

| Columns × rows | Coverage for this feature | Audit focus |
| --- | --- | --- |
| 60×16 | Routine + visual, baseline | Compact wrapping, scrolling to the last entry and footer clearance. |
| 80×24 | Routine + visual, baseline | Reference frames for both the width-only and height-only comparisons. |
| 100×24 | Routine + visual | Compare with 80×24 for shorter wraps and any column transition at fixed height. |
| 120×30 | Routine + visual | Gutters, wrapped descriptions and the selected entry after paging. |
| 160×40 | Routine + visual | Reading order and name-to-description alignment in a wide frame. |
| 80×40 | Visual only | Compare with 80×24. Equal usable width should preserve column count and wrapping as more rows become visible. |
| 200×50 | Visual only | Three-column maximum, separation between neighboring entries and short-menu footer placement. |

Review the routine passes’ rendered cells and capture the two visual-only sizes with the same inputs. Inspect the short menu and rsync at opening, and FFmpeg after paging and on its final page. Reuse the matching two-size rsync color and monochrome comparisons from Phase 1. Record dimensions, state, action, observed column count and color mode, distinguishing automated checks from visual observations. After a fix, repeat the affected cases and sizes. [Command-help audit procedure](docs/development.md#auditing-command-help)

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
