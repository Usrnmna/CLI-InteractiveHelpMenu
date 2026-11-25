# Project roadmap

## Remaining work

**Remaining engineering experiments** cover unchanged idle redraws and serial profile validation. The serial prose-reuse follow-up measured a 4.4–5.4% improvement in warm FFmpeg opening time and fell below the 30% target. [Prose-reuse results](docs/serial-prose-reuse-experiment.md)

**Next release decision** is which program changes to ship. The menu review, documentation and local demonstration media now reflect the three-level browser. Release verification starts once the exact contents are selected. [Review record](docs/superpowers/plans/2026-11-24-menu-detail-levels.md#review-record) · [Capture provenance](docs/assets/README.md)

| Phase | Current status | Completion evidence |
| --- | --- | --- |
| 1. Investigate menu performance (original roadmap task 4) | Complete | [Five measured decisions and follow-up acceptance checks](docs/menu-cost-measurements.md#decisions) |
| 2. Reconcile the menu record and choose release contents | Review and local media complete. Release scope pending | Selected changes and source revision |
| 3. Verify the release candidate | Pending final source selection | Reproducible artifacts and results for the exact release inputs |
| 4. Publish and verify distribution | Pending candidate verification, hosted checks and release authorization | Published assets match the verified files and the tag identifies the tested commit |

### Phase 1 — Measure the remaining menu costs

**Complete.** The investigation used the implemented three-level menu, the saved pre-redesign renderer, real Bash terminal frames and controlled discovery fixtures. Production optimization and architecture decisions remain separate. [Methods, environment and commands](docs/menu-cost-measurements.md#reproducing-the-measurements)

| Investigation | Decision and next step |
| --- | --- |
| Opening and interaction | **Experiment complete. Defer adoption.** At 80×24, serial prose reuse reduced unfiltered FFmpeg opening from 546 to 519 ms. At 60×16 it reduced opening from 555 to 530 ms. The small Git control showed little change. [Matched timings and verification](docs/serial-prose-reuse-experiment.md) |
| Idle redraws | **Proceed** with skipping a draw on an unchanged timeout. Retain geometry polling and resize recovery. Both controls redrew 66 times per idle 10 seconds. [Idle evidence](docs/menu-cost-measurements.md#idle-redraws) |
| Startup profile loading | **Proceed** with a serial text-validation experiment. Loading 76 files took 118 ms, compared with 0.4 ms for the selected Git file alone. Preserve full validation and override semantics. [Loading evidence](docs/menu-cost-measurements.md#startup-profile-loading) |
| Guarded discovery | **Defer** a change. An ordinary valid hit made zero probes. A guarded yq hit spent 11 ms and made one required identity probe. [Discovery evidence](docs/menu-cost-measurements.md#guarded-discovery) |
| Multi-core processing | **Defer pools and retain serial execution.** Four processes improved FFmpeg opening from 498 to 323 ms in the pool comparison, but peak PSS rose from 42 to 90 MiB. Threads slowed opening. Any production process architecture requires separate approval. [CPU limits, workload crossover and compatibility](docs/menu-cost-measurements.md#worker-pools-and-cpu-limits) |

### Phase 2 — Close the menu record and select release contents

1. **Review record complete.** The user approved the revised mockups. A fresh local build reproduced the six documented terminal frames. [Decision](docs/superpowers/plans/2026-11-24-menu-detail-levels.md#review-record) · [Rendered verification](docs/superpowers/plans/2026-11-24-menu-detail-levels-verification.md)
2. **Identify the changes to ship.** The prepared `v0.4.0-alpha` performance candidate predates the three-level menu. Record whether the menu ships with that performance change or as a later step. Apply the versioning rules to the chosen batch and align `VERSION`, the changelog and release notes. The proposed performance release numbers depend on what actually ships. [Version assignment](docs/versioning.md#assigning-the-next-number) · [Candidate contents](docs/releases.md#version-040---alpha)
3. **Compare the selected release with the local documentation.** The public guides and six media assets depict the local three-level browser. When the release inputs are chosen, check that their runtime and profiles match the captured build. [Asset provenance](docs/assets/README.md#regeneration)

### Phase 3 — Build and test the selected candidate

1. **Freeze the source inputs.** Identify the reviewed release commit. Include the runtime modules, tests and documentation intended for that release. Build from its clean checkout into a fresh output directory and keep earlier candidate files intact. [Build procedure](docs/releases.md#build-from-source)
2. **Verify the artifacts.** Compare the source inventory and manifest hashes with the commit’s Git blobs. Verify individual and aggregate checksums, archive contents, launcher and installer payloads. Rebuild independently and compare the resulting files byte for byte. [Candidate checks](docs/release-candidate.md#final-source-and-package-checks) · [Reproducibility](docs/release-candidate.md#reproducibility-and-reporting)
3. **Test the exact candidate.** Run the full offline suite on Ubuntu 26.04 with Python 3.14 and Ubuntu 24.04 with Python 3.10 and 3.12. Point the package tests at the candidate artifacts. Exercise install, historical upgrade, update and removal, plus the installed Bash menu, insertion, cancellation and terminal restoration. If the menu redesign is included, confirm the three levels and selected category at 80×24 and 60×16. Record per-target passes, failures, skips and artifact identity. [Sandbox procedure](docs/development.md#isolated-local-debugging) · [Package and terminal checks](docs/release-candidate.md#final-source-and-package-checks)

### Phase 4 — Publish the verified prerelease

1. **Confirm hosted checks** on the exact release commit, including the configured Linux jobs and documentation links. Resolve failures against that revision. [CI scope](docs/development.md#continuous-integration)
2. **Tag and publish when authorized.** Create the matching annotated tag on the verified commit. Prepare a draft prerelease, keep latest-stable selection disabled, attach the verified artifacts and checksums, and record the commit and verification results in the release body.
3. **Verify the download.** Compare the published files byte for byte with the tested local artifacts. Record the tag, commit and release link when the comparison passes. [Publication procedure](docs/releases.md#release-provenance-and-publication)

### Conditional decisions

| Trigger | Follow-up and evidence needed |
| --- | --- |
| Phase 1 identifies a material runtime cost | Test the specific remedy in isolation and repeat the matched measurements and behavior checks. The first prose-reuse experiment fell below its target. Remaining candidates include idle redraw suppression and faster serial profile validation. Selective loading, a persistent index or an additional process needs a separate architecture decision. [Performance experiments](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
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

**Complete — baseline and Stage 1.** The [architecture baseline](docs/runtime-architecture.md#local-performance-baseline) and [Stage 1 evaluation](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) record opening costs, correctness and the decision to retain shared value formatting. [Phase 1](#phase-1--measure-the-remaining-menu-costs) completed the five remaining investigations. The [decision table](docs/menu-cost-measurements.md#decisions) records the next experiments and their acceptance checks.

## Discovered command help

**Complete.** The maintained discovery matrix covers 162 paths across 73 executable names. The Essential, Next and Extended tier summaries identify selectable menus, usage-only diagnostics and root-help fallbacks. [Discovery results by tier](docs/audit-history.md#discovered-command-help) · [Fixture editions](tests/fixtures/help/README.md)

## How to audit a batch

Use the [command-help audit procedure](docs/development.md#auditing-command-help) for reference selection, alias reconciliation, terminal checks and one full offline matrix per integrated batch.

## Recording progress and finishing the audit

For future profile or route changes, update the affected family or tier row and its evidence. A bundled review closes when each applicable option and alias is accounted for, distinct options are selectable, material Details are reachable, and the terminal and sandbox checks pass. A discovery review also needs the fixed source, edition and actual disposition of each route, including empty or fallback results. Record the exact path and blocker for a partial batch.

For open development tasks, update the status in [remaining work](#remaining-work), link the completion evidence and identify the next actionable step in each open phase. Keep experiment results with the plan and dated test outcomes with the verification report.
