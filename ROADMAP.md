# Project roadmap

## Remaining work

**Next in engineering** is to measure how long the current three-level menu takes to open, starting with FFmpeg and a small Git menu for comparison. **Next in documentation** is to correct the menu plan’s stale review status. These can proceed independently. Preparing a release can also proceed once its contents are chosen. A performance experiment becomes a release dependency only if its change is included.

| Phase | Current status | Completion evidence |
| --- | --- | --- |
| 1. Investigate menu performance (original roadmap task 4) | Next | A measured decision for each of the four investigations below |
| 2. Reconcile the menu record and choose release contents | Review correction ready now. Release scope pending | Correct review entry and a documented list of changes to ship |
| 3. Verify the release candidate | Pending final source selection | Reproducible artifacts and results for the exact release inputs |
| 4. Publish and verify distribution | Pending candidate verification, hosted checks and release authorization | Published assets match the verified files and the tag identifies the tested commit |

### Phase 1 — Measure the remaining menu costs

Use the implemented menu as the baseline. The earlier Stage 1 experiment already established the benefit of reusing shared value formatting. In the later three-pair menu check, median FFmpeg opening time went from 508 to 528 ms while other suites were running. Repeat under matched conditions before attributing that difference to a particular operation. [Stage 1 measurements](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) · [Three-level menu measurements](docs/superpowers/plans/2026-11-24-menu-detail-levels-verification.md#color-and-performance-checks)

1. **Opening and interaction.** Time the first complete frame for FFmpeg and the Git control. Separate summary and detail preparation from search matching, declaration-width calculation and text wrapping. Measure time from a keystroke to the updated screen for filtering, selecting a row and changing detail level. Check that matches, ordering and visible guidance stay correct. [Prose and redraw experiments](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws)
2. **Idle redraws.** Keep the menu open at a fixed size for matched 10-second intervals. Record redraw count, CPU time and context switches. Resize while idle, then navigate, insert and cancel to check recovery. [Measurement protocol](docs/ffmpeg-menu-performance-plan.md#before-and-after-measurement)
3. **Startup profile loading.** Measure elapsed time, CPU and peak memory as the profile collection grows. Identify the cost of reading profiles unrelated to the pending command. Document how any proposed change would preserve longest-command matching, custom overrides, invalid-file handling and full validation through `--check`. [Loading investigation](docs/runtime-architecture.md#optimization-candidates)
4. **Guarded discovery.** Compare an ordinary cache hit, a miss and a route that checks the installed executable’s identity. Count probes and time identity checks, help collection, parsing and cache I/O separately. Check stale entries, identity mismatches and failed probes against the expected fallback. [Discovery investigation](docs/runtime-architecture.md#optimization-candidates)
5. **Record the decisions.** For each investigation, record the affected menus, measured cost, correctness constraints and a decision to proceed or defer. Where a change is justified, identify the smallest experiment and its acceptance checks. Architecture changes require separate approval. [Timing, memory and correctness criteria](docs/ffmpeg-menu-performance-plan.md#before-and-after-measurement)

### Phase 2 — Close the menu record and select release contents

1. **Correct the review record.** The menu plan’s final human-review row still says implementation is on hold. Update it to record approval of the mockups and link the six real terminal captures. Simple, Detailed, Expanded, unit search and full category titles have already been implemented and verified. [Menu review record](docs/superpowers/plans/2026-11-24-menu-detail-levels.md#review-record) · [Rendered verification](docs/superpowers/plans/2026-11-24-menu-detail-levels-verification.md)
2. **Identify the changes to ship.** The prepared `v0.4.0-alpha` performance candidate predates the three-level menu. Record whether the menu ships with that performance change or as a later step. Apply the versioning rules to the chosen batch and align `VERSION`, the changelog and release notes. The proposed performance release numbers depend on what actually ships. [Version assignment](docs/versioning.md#assigning-the-next-number) · [Candidate contents](docs/releases.md#version-040---alpha)
3. **Check the public description against that scope.** Confirm the README, controls guide and media captions describe the selected version. Existing candidate screenshots have dated provenance. Link the current terminal captures when describing the new menu. If new public recordings are selected, complete the media work under [Conditional decisions](#conditional-decisions) before packaging them.

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
| Phase 1 identifies a material runtime cost | Test the specific remedy in isolation and repeat the matched measurements and behavior checks. Possible remedies include reusing cleaned prose, caching active matches or wrapped text, suppressing idle redraws and reducing redundant discovery. Selective loading, a persistent index or an additional process needs a separate architecture decision. [Performance experiments](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Validated test selection still leaves substantial cost | Pilot Phase 5 result reuse for one bounded group. Prove invalidation for changed inputs, environments, targets, fixtures and interrupted runs. Report executed, reused, failed and skipped outcomes separately. Consider CI selection or sharding after local parity and measured savings. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) · [Sharding pilot](docs/test-selection-plan.md#two-shard-host-pilot) |
| New demonstration media will ship | Update the rsync and ls capture expectations for the current layout. Regenerate and inspect the assets, including selected cells, pending command, cursor and nonexecution markers. [Capture procedure](docs/assets/README.md#regeneration) |
| Packaged guides need roadmap navigation | Choose between including the root roadmap in the source archive and linking to the checkout. Verify links from an extracted archive if package policy changes. [Archive contents](docs/releases.md#build-from-source) |
| Hosted link coverage is extended to the two Markdown files under `.github/` | Add both paths to the main CI check and its bounded retry. Verify the two input lists agree. [Current CI coverage](docs/development.md#continuous-integration) |

### Completed work supporting these phases

- **Test selection, original tasks 1–2.** Phases 4a and 4b verified selection reports, ordered local execution, full fallback and the historical yq failure. [Pilot evidence](docs/test-selection-plan.md#phase-4-pilot-evidence)
- **Shared value formatting, original task 3.** Warm FFmpeg first-frame medians improved by 31.0–31.5% with all-row parity. The earlier local candidate passed 1,879 tests per target with one Windows-only skip, and an isolated rebuild reproduced its packages. [Performance decision](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) · [Candidate record](docs/release-candidate.md)
- **Three-level menu and category labels.** The browser and preview support all three levels. Simple gives unused space back to the option list. The redesign passed 1,887 tests on each of the three Linux targets with one Windows-only skip. The 15 package tests used fresh temporary builds after the earlier candidate failed the source-inventory check. [Terminal captures and test results](docs/superpowers/plans/2026-11-24-menu-detail-levels-verification.md#regression-results)

## Purpose and scope

The completed audits cover both the bundled descriptions and the help produced through maintained discovery routes. The two inventories overlap and measure different things. The [documentation index](docs/README.md) covers operating instructions, architecture, authoring and release procedures.

## Bundled menu progress

**Complete.** The first pass covered all 942 original entries across the 76 profiles. The final seven families completed the full manual comparison on their first pass, covering the remaining 224 original entries. The last two columns link the reconciled manual inventories and the rendered Details verification. The Podman revisits added 295 selectable rows (152 run,
124 build, 13 exec and six logs). GNU tar added 145, rsync added 187, GNU grep added 34, ls added 41, OpenSSH added 45, Git stash/worktree added 348, Git commit/log added 313, 7-Zip extraction added 106, fd/fdfind added 158, fzf added 192, FFmpeg added 1,743 and yq eval added 54.
The combined revisit added 139 iproute2, 166 systemd and 337 OpenSSL rows.
The six development-tool families added 969 rows to the previous 5,245.
The final seven families added 273 rows to the previous 6,214. The bundled total is **6,487 rows across 76 profiles**, compared with the historical 942. [Bundled profiles](profiles/) · [Final bundled verification](docs/remaining-bundled-verification.md#compatibility-results)

| Command family or commands | Profiles | Baseline entries | First-pass review | Manual options | Menu Details |
| --- | ---: | ---: | --- | --- | --- |
| `rsync` | 1 | 29 | Complete locally. [First-pass audit](docs/rsync-option-audit.md) | Complete · [216 options and 306 distinct spellings](docs/rsync-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/rsync-manual-coverage.md#verification) |
| GNU `tar` | 1 | 12 | Complete locally. [First-pass audit](docs/tar-option-audit.md) | Complete · [157 options and 59 aliases](docs/tar-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/tar-manual-coverage.md#verification) |
| GNU `grep` | 1 | 14 | Complete locally. [First-pass audit](docs/grep-option-audit.md) | Complete · [48 options, 38 literal aliases and a numeric shorthand](docs/grep-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/grep-manual-coverage.md#verification) |
| GNU and uutils `ls` | 1 | 19 | Complete locally. [First-pass audit](docs/ls-option-audit.md) | Complete · [60 options and 27 aliases](docs/ls-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/ls-manual-coverage.md#verification) |
| OpenSSH — `ssh`, `scp`, `sftp` | 3 | 51 | Complete locally. [First-pass audit](docs/openssh-option-audit.md) | Complete · [46 ssh, 24 scp and 26 sftp options](docs/openssh-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/openssh-manual-coverage.md#verification) |
| Git — stash and worktree | 11 | 85 | Complete locally. [First-pass audit](docs/git-stash-worktree-option-audit.md) | Complete · [433 rows and 365 path-specific effects](docs/git-stash-worktree-manual-coverage.md#menu-inventory) | Complete on all three targets · [menu and suite results](docs/git-stash-worktree-manual-coverage.md#verification) |
| Git — commit and log | 2 | 19 | Complete locally. [First-pass audit](docs/git-commit-log-option-audit.md) | Complete · [98 commit and 234 log rows](docs/git-commit-log-manual-coverage.md#manual-inventory) | Complete on all three targets · [menu and suite results](docs/git-commit-log-manual-coverage.md#verification) |
| `7z x`, `7zz x` | 2 | 8 | Complete locally. [Manual comparison and sandbox results](docs/7zip-extraction-option-audit.md) | Complete · [57 choices per executable](docs/7zip-extraction-manual-inventory.md#selectable-inventory) | Complete on all three targets · [menu and suite results](docs/7zip-extraction-manual-coverage.md#verification) |
| `fd`, `fdfind` | 2 | 38 | Complete locally. [Manual comparison and sandbox results](docs/fd-option-audit.md) | Complete · [58 option families and 98 spellings per menu](docs/fd-manual-inventory.md#option-and-spelling-inventory) | Complete on all three targets · [menu and suite results](docs/fd-manual-coverage.md#compatibility-results) |
| `fzf` | 1 | 17 | Complete locally. [Manual comparison and sandbox results](docs/fzf-option-audit.md) | Complete · [191 effects and 209 selectable spellings](docs/fzf-manual-inventory.md#option-effects-and-spellings) | Complete on all three targets · [menu and suite results](docs/fzf-manual-coverage.md#compatibility-results) |
| `ffmpeg` | 1 | 16 | Complete locally. [Manual comparison and sandbox results](docs/ffmpeg-option-audit.md) | Complete · [1,759 selectable spellings and release inventories](docs/ffmpeg-manual-inventory.md#selectable-inventory) | Complete on all three targets · [menu and suite results](docs/ffmpeg-manual-coverage.md#compatibility-results) |
| `yq eval` | 1 | 15 | Complete locally. [Manual comparison and sandbox results](docs/yq-eval-option-audit.md) | Complete · [51 effects and 18 aliases](docs/yq-eval-manual-inventory.md#effects-and-spellings) | Complete on all three targets · [menu and suite results](docs/yq-eval-manual-coverage.md#compatibility-results) |
| iproute2 — `ip address`, `ip link`, `ip route`, `ss` | 4 | 36 | Complete locally. [Manual comparison and sandbox results](docs/iproute2-option-audit.md) | Complete · [175 selectable rows](docs/iproute2-manual-coverage.md) | Complete on all three targets · [combined results](docs/iproute2-systemd-openssl-verification.md#compatibility-results) |
| systemd — `systemctl`, `journalctl` | 4 | 50 | Complete locally. [Manual comparison and sandbox results](docs/systemd-option-audit.md) | Complete · [216 selectable rows](docs/systemd-manual-coverage.md) | Complete on all three targets · [combined results](docs/iproute2-systemd-openssl-verification.md#compatibility-results) |
| OpenSSL — `s_client`, `x509`, `dgst` | 3 | 33 | Complete locally. [Manual comparison and sandbox results](docs/openssl-option-audit.md) | Complete · [370 selectable rows](docs/openssl-manual-coverage.md) | Complete on all three targets · [combined results](docs/iproute2-systemd-openssl-verification.md#compatibility-results) |
| `uv` | 5 | 56 | Complete locally. [Manual comparison and sandbox results](docs/uv-option-audit.md) | Complete · [454 selectable rows](docs/uv-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| Ruff — `ruff check`, `ruff format` | 2 | 30 | Complete locally. [Manual comparison and sandbox results](docs/ruff-option-audit.md) | Complete · [92 selectable rows](docs/ruff-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| `pytest` | 1 | 18 | Complete locally. [Manual comparison and sandbox results](docs/pytest-option-audit.md) | Complete · [121 selectable rows](docs/pytest-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| Go — `go build`, `go test`, `go run`, `go mod tidy` | 4 | 44 | Complete locally. [Manual comparison and sandbox results](docs/go-option-audit.md) | Complete · [171 selectable rows](docs/go-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| .NET — `dotnet build`, `publish`, `restore`, `run`, `test` | 5 | 76 | Complete locally. [Manual comparison and sandbox results](docs/dotnet-option-audit.md) | Complete · [242 selectable rows](docs/dotnet-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| `bun run` | 1 | 8 | Complete locally. [Manual comparison and sandbox results](docs/bun-run-option-audit.md) | Complete · [121 selectable rows](docs/bun-run-manual-coverage.md) | Complete on all three targets · [combined results](docs/devtools-batch-verification.md#compatibility-results) |
| Podman — `run`, `build`, `exec`, `logs` | 4 | 44 | Complete locally. [Manual comparison and sandbox results](docs/podman-option-audit.md) | Complete · [168 run spellings](docs/podman-run-manual-coverage.md#option-inventory) and [171 build, exec and logs spellings](docs/podman-build-exec-logs-manual-coverage.md#build-inventory) | Complete on all three targets · [run](docs/podman-run-manual-coverage.md#verification) and [build, exec and logs](docs/podman-build-exec-logs-manual-coverage.md#verification) |
| PostgreSQL — `psql` | 1 | 21 | Complete locally · [family audit](docs/psql-manual-coverage.md) | Complete · [70 selectable rows](docs/psql-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| Ansible — `ansible-playbook` | 1 | 21 | Complete locally · [family audit](docs/ansible-playbook-manual-coverage.md) | Complete · [61 selectable rows](docs/ansible-playbook-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| Azure CLI — `az` | 3 | 35 | Complete locally · [family audit](docs/azure-cli-manual-coverage.md) | Complete · [50 selectable rows](docs/azure-cli-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| Google Cloud CLI — `gcloud` | 3 | 34 | Complete locally · [family audit](docs/gcloud-manual-coverage.md) | Complete · [91 selectable rows](docs/gcloud-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| Espressif — `esptool`, `esptool.py` | 3 | 30 | Complete locally · [family audit](docs/esptool-manual-coverage.md) | Complete · [77 selectable rows](docs/esptool-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| PlatformIO — `pio`, `platformio` | 4 | 68 | Complete locally · [family audit](docs/platformio-manual-coverage.md) | Complete · [98 selectable rows](docs/platformio-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |
| Arduino — `arduino-cli compile` | 1 | 15 | Complete locally · [family audit](docs/arduino-cli-manual-coverage.md) | Complete · [50 selectable rows](docs/arduino-cli-manual-coverage.md) | Complete on all three targets · [combined results](docs/remaining-bundled-verification.md#compatibility-results) |

## Manual-coverage revisit

The family table links each original review, reconciled inventory and rendered-menu result. For newly added options or a changed source edition, use the [batch audit procedure](docs/development.md#auditing-command-help).

## Reducing test duration

**Complete — Phases 1–4.** The focused edit loop, paired timing baseline and measured duplicate-work reductions have [three-target evidence](docs/test-selection-plan.md#full-offline-verification). The two-shard timing is a host pilot. The default audit gate remains one full offline run per target on the combined batch. The [local selector pilot](docs/test-selection-plan.md#phase-4-pilot-evidence) verified both Phase 4 checkpoints. Phase 5 remains a [conditional decision](#conditional-decisions).

## Runtime performance follow-up

**Complete — baseline and Stage 1.** The [architecture baseline](docs/runtime-architecture.md#local-performance-baseline) and [Stage 1 evaluation](docs/ffmpeg-menu-performance-plan.md#stage-1-evaluation) record opening costs, correctness and the decision to retain shared value formatting. The remaining investigations are listed in [Phase 1](#phase-1--measure-the-remaining-menu-costs).

## Discovered command help

**Complete.** The [compatibility matrix](tests/fixtures/help/matrix.json) lists 162 maintained
command paths across 73 executable names in three tiers. The [combined verification](docs/next-extended-discovery-verification.md#full-suite-matrix) records the final 116 routes and full suites. The matrix and
bundled inventories overlap. Count a bundled review against a discovery path
only when the audit also checks the help produced through that route.

| Matrix tier | Paths | Description review |
| --- | ---: | --- |
| Essential | 46 | Complete on all three targets. The 46 reviews cover 45 selectable menus and the usage-only npm root. [Route inventory](docs/essential-discovery-audit.md) · [Test results](docs/essential-discovery-verification.md) |
| Next | 65 | Complete on all three targets, 65/65 selectable menus. [Next route inventory](docs/next-discovery-audit.md) |
| Extended | 51 | Complete on all three targets, 51/51 paths. There are 47 selectable leaf or root menus, two usage-only diagnostics and two extraction paths served by root documentation. [Extended route inventory](docs/extended-discovery-audit.md) |

For each path, identify its help source and version. Compare what the menu
displays with the applicable manual and available versioned help capture.
Some fixtures are synthetic or excerpted, and some root commands provide only
usage information. Record those outcomes explicitly. If a qualification appears
in a capture but disappears from the menu, trace it through parsing and
rendering, retain the original capture and add a regression for the loss.
See the [fixture provenance guide](tests/fixtures/help/README.md).

## How to audit a batch

Use the [command-help audit procedure](docs/development.md#auditing-command-help) for reference selection, alias reconciliation, terminal checks and one full offline matrix per integrated batch.

## Recording progress and finishing the audit

For future profile or route changes, update the affected family or tier row and its evidence. A bundled review closes when each applicable option and alias is accounted for, distinct options are selectable, material Details are reachable, and the terminal and sandbox checks pass. A discovery review also needs the fixed source, edition and actual disposition of each route, including empty or fallback results. Record the exact path and blocker for a partial batch.

For open development tasks, update the status in [remaining work](#remaining-work), link the completion evidence and identify the next actionable step in each open phase. Keep experiment results with the plan and dated test outcomes with the verification report.
