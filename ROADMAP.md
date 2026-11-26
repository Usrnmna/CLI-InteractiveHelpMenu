# Project roadmap

## Remaining work

**v0.4.1-alpha local candidate — awaiting the maintainer's source commit.** Both improvements met their acceptance checks. The experiment matrix passed 1,890 tests per target using temporary builds. Exact-package verification for the new version is pending. [Performance evidence](docs/menu-cost-measurements.md#combined-offline-verification) · [Candidate record](docs/release-candidate.md#v041-alpha-local-candidate)

- [x] Select idle redraw suppression and faster serial profile validation as one patch in the 0.4 plan.
- [ ] Freeze the candidate source at a maintainer-confirmed commit.
- [ ] Build twice from that revision and verify all 11 files against the source and the independent rebuild.
- [ ] Run one full offline matrix with the first build and record the installed-terminal and lifecycle results.

**v0.4.0-alpha verification is complete.** The earlier candidate remains unpublished and its artifacts are preserved in `dist/candidate-v0.4.0-alpha-combined/`. The table below records its phases. Phase 4 publication is skipped for both candidates. Phase 5 test-result reuse remains conditional. [Frozen v0.4.0-alpha evidence](docs/release-candidate.md#combined-candidate-verification) · [Conditional work](#conditional-decisions)

| Phase | Current status | Completion evidence |
| --- | --- | --- |
| 1. Investigate menu performance (original roadmap task 4) | Complete | [Five measured decisions and follow-up acceptance checks](docs/menu-cost-measurements.md#decisions) |
| 2. Reconcile the menu record and choose release contents | Complete | [Scope and version decision](#phase-2--close-the-menu-record-and-select-release-contents) and [terminal evidence](docs/superpowers/plans/2026-11-24-menu-detail-levels.md#review-record) |
| 3. Verify the release candidate | Complete | [Exact source, reproducible artifacts and installed-terminal results](docs/release-candidate.md#combined-candidate-verification) |
| 4. Publish and verify distribution | Skipped | If publication resumes, confirm hosted checks on the release commit and verify the published downloads. |

### Phase 1 — Measure the remaining menu costs

**Complete.** The investigation used the implemented three-level menu, the saved pre-redesign renderer, real Bash terminal frames and controlled discovery fixtures. Production optimization and architecture decisions remain separate. [Methods, environment and commands](docs/menu-cost-measurements.md#reproducing-the-measurements)

| Investigation | Decision and next step |
| --- | --- |
| Opening and interaction | **Experiment complete. Defer adoption.** At 80×24, serial prose reuse reduced unfiltered FFmpeg opening from 546 to 519 ms. At 60×16 it reduced opening from 555 to 530 ms. The small Git control showed little change. [Matched timings and verification](docs/serial-prose-reuse-experiment.md) |
| Idle redraws | **Complete. Retain.** Idle draws fell from 66 to zero per 10 seconds across both sizes and menus. Geometry polling, resize recovery and input remained responsive. [PTY evidence and acceptance checks](docs/menu-cost-measurements.md#idle-redraw-experiment) |
| Startup profile loading | **Complete. Retain.** Bundled loader CPU fell from 118.36 to 74.04 ms at the median. The small menu opened faster with and without overrides, with matching full-set validation and diagnostics. [Load, frame and parity evidence](docs/menu-cost-measurements.md#serial-profile-validation-experiment) |
| Guarded discovery | **Defer** a change. An ordinary valid hit made zero probes. A guarded yq hit spent 11 ms and made one required identity probe. [Discovery evidence](docs/menu-cost-measurements.md#guarded-discovery) |
| Multi-core processing | **Defer pools and retain serial execution.** Four processes improved FFmpeg opening from 498 to 323 ms in the pool comparison, but peak PSS rose from 42 to 90 MiB. Threads slowed opening. Any production process architecture requires separate approval. [CPU limits, workload crossover and compatibility](docs/menu-cost-measurements.md#worker-pools-and-cpu-limits) |

### Phase 2 — Close the menu record and select release contents

1. **Review record complete.** The user approved the revised mockups for implementation and requested verification at both sizes. The implementation record links the six actual FFmpeg frames, including the number of options visible at each level. [Design decision and terminal captures](docs/superpowers/plans/2026-11-24-menu-detail-levels.md#review-record)
2. **Release contents selected.** The v0.4.0-alpha candidate includes per-open reuse of shared value formatting together with Simple, Detailed and Expanded, compact category labels, shared unit notes and unit search. This is the first shipping batch in the 0.4 series. The performance-only candidate remained unpublished, so the combined batch retains `v0.4.0-alpha`. The serial prose-reuse prototype, idle-redraw suppression and serial profile-validation experiments are outside that frozen version. [Version assignment](docs/versioning.md#assigning-the-next-number) · [Changelog](CHANGELOG.md#version-040---alpha)
3. **Documentation and captures checked.** The README, controls guide and gallery describe the selected menu. All 160 runtime, configuration, profile and version fingerprints from the November 25 capture match the release-scope checkout at `bc78f9f` and the capture-build manifest. All six public media files match the recorded hashes. The existing media cover the selected behavior. Phase 3 records the exact release commit and package identities. [Controls](docs/usage.md#browser-controls) · [Capture provenance](docs/assets/README.md#capture-evidence) · [Release notes](docs/releases.md#version-040---alpha)

### Phase 3 — Build and test the selected candidate

1. **Source frozen.** Commit `cc30ade99d1ddf2f593b409f66bd05dc0029f44c` contains the selected formatting improvement, the three-level menu and the Phase 2 release documentation. The two builds used separate clean detached checkouts.
2. **Artifacts verified.** All 1,003 packaged source hashes matched the selected Git blobs. Both archives, the launcher, the embedded installer payload and the checksums passed verification. All 11 upload files matched the independent rebuild byte for byte. [Build commands and digests](docs/release-candidate.md#combined-candidate-verification)
3. **Candidate tested.** Each of the three full offline runs passed 1,888 tests with zero failures and one Windows-only skip. The first build passed historical upgrade, update and removal on every target. The installed Bash adapter matched the six reference frames and preserved the filtered selection, pending command and terminal at 80×24 and 60×16. [Environment, results and installed-menu checks](docs/release-candidate.md#combined-candidate-verification)

### Phase 4 — Publish the verified prerelease

**Skipped for this roadmap.** Use the following procedure if publication is authorized later.

1. **Confirm hosted checks** on the exact release commit, including the configured Linux jobs and documentation links. Resolve failures against that revision. [CI scope](docs/development.md#continuous-integration)
2. **Tag and publish when authorized.** Create the matching annotated tag on the verified commit. Prepare a draft prerelease, keep latest-stable selection disabled, attach the verified artifacts and checksums, and record the commit and verification results in the release body.
3. **Verify the download.** Compare the published files byte for byte with the tested local artifacts. Record the tag, commit and release link when the comparison passes. [Publication procedure](docs/releases.md#release-provenance-and-publication)

### Conditional decisions

| Trigger | Follow-up and evidence needed |
| --- | --- |
| Phase 1 identifies a material runtime cost | Test the specific remedy in isolation and repeat the matched measurements and behavior checks. The prose-reuse experiment fell below its target. Both idle redraw suppression and faster serial profile validation met their acceptance checks. Selective loading, a persistent index or an additional process needs a separate architecture decision. [Performance experiments](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Validated test selection still leaves substantial cost | Pilot Phase 5 result reuse for one bounded group. Prove invalidation for changed inputs, environments, targets, fixtures and interrupted runs. Report executed, reused, failed and skipped outcomes separately. Consider CI selection or sharding after local parity and measured savings. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) · [Sharding pilot](docs/test-selection-plan.md#two-shard-host-pilot) |

### Completed work supporting these phases

- **Documentation, media and repository configuration.** The [local gallery](docs/assets/README.md) shows the unpacked runtime and the [audit history](docs/audit-history.md) traces the evidence from the original reviews through the current menu. Git, the package builder and the link checker recognize generated fixture workspaces. Both hosted link-check attempts now include the contributor and pull-request guides. [Refresh workflow](docs/local-build-refresh.md) · [Repository settings](docs/development.md#repository-configuration)

- **Test selection, original tasks 1–2.** Phases 4a and 4b verified selection reports, ordered local execution, full fallback and the historical yq failure. [Pilot evidence](docs/test-selection-plan.md#phase-4-pilot-evidence)
- **Shared value formatting, original task 3.** Warm FFmpeg first-frame medians improved by 31.0–31.5% with all-row parity. The earlier local candidate passed 1,879 tests per target with one Windows-only skip, and an isolated rebuild reproduced its packages. [Performance decision](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) · [Candidate record](docs/release-candidate.md)
- **Three-level menu and category labels.** The browser and preview support all three levels. Simple gives unused space back to the option list. The redesign passed 1,887 tests on each of the three Linux targets with one Windows-only skip. The 15 package tests used fresh temporary builds after the earlier candidate failed the source-inventory check. [Terminal captures and test results](docs/superpowers/plans/2026-11-24-menu-detail-levels-verification.md#regression-results)

## Purpose and scope

The completed audits cover both the bundled descriptions and the help produced through maintained discovery routes. The two inventories overlap and measure different things. The [documentation index](docs/README.md) covers operating instructions, architecture, authoring and release procedures.

## Bundled menu progress

**Complete.** The manual audits reconciled 942 original rows into 6,487 selectable rows across 76 profiles. The [family-by-family results](docs/audit-history.md#bundled-menu-progress) include first-pass findings, reconciled inventories, terminal checks and edition limits for all 29 families.

## Manual-coverage revisit

The [family table](docs/audit-history.md#bundled-menu-progress) links each original review, reconciled inventory and rendered-menu result. For newly added options or a changed source edition, use the [batch audit procedure](docs/development.md#auditing-command-help).

## Reducing test duration

**Complete — Phases 1–4.** The focused edit loop, paired timing baseline and measured duplicate-work reductions have [three-target evidence](docs/test-selection-plan.md#full-offline-verification). The two-shard timing is a host pilot. The default audit gate remains one full offline run per target on the combined batch. The [local selector pilot](docs/test-selection-plan.md#phase-4-pilot-evidence) verified both Phase 4 checkpoints. Phase 5 remains a [conditional decision](#conditional-decisions).

## Runtime performance follow-up

**Complete — baseline and Stage 1.** The [architecture baseline](docs/runtime-architecture.md#local-performance-baseline) and [Stage 1 evaluation](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) record opening costs, correctness and the decision to retain shared value formatting. [Phase 1](#phase-1--measure-the-remaining-menu-costs) completed the five remaining investigations. The [decision table](docs/menu-cost-measurements.md#decisions) records the completed experiments, decisions and acceptance checks.

## Discovered command help

**Complete.** The maintained discovery matrix covers 162 paths across 73 executable names. The Essential, Next and Extended tier summaries identify selectable menus, usage-only diagnostics and root-help fallbacks. [Discovery results by tier](docs/audit-history.md#discovered-command-help) · [Fixture editions](tests/fixtures/help/README.md)

## How to audit a batch

Use the [command-help audit procedure](docs/development.md#auditing-command-help) for reference selection, alias reconciliation, terminal checks and one full offline matrix per integrated batch.

## Recording progress and finishing the audit

For future profile or route changes, update the affected family or tier row and its evidence. A bundled review closes when each applicable option and alias is accounted for, distinct options are selectable, material Details are reachable, and the terminal and sandbox checks pass. A discovery review also needs the fixed source, edition and actual disposition of each route, including empty or fallback results. Record the exact path and blocker for a partial batch.

For open development tasks, update the status in [remaining work](#remaining-work), link the completion evidence and identify the next actionable step in each open phase. Keep experiment results with the plan and dated test outcomes with the verification report.
