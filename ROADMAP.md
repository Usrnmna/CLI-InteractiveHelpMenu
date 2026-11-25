# Project roadmap

**Next — evaluate shared value formatting per browser open.** Task 3 in [remaining work](#remaining-work) links the Stage 1 baseline and parity criteria.

## Remaining work

The roadmap tracks both program changes and project maintenance. Only changes to the working program qualify for a [proposed alpha release](docs/versioning.md#proposed-targets).

Two required deliverables remain. Count each numbered row once. The checklists and measurement protocols in the linked plans supply its acceptance tests. **Next** is ready to start, **Pending** has yet to start, **In progress** means work has begun, and **Complete** requires linked evidence. Use **Blocked** with the failed prerequisite and next action. **Conditional** items have a separate decision gate.

| Workstream and task | Status | Dependency and evidence needed to close |
| --- | --- | --- |
| 1. Test selection, Phase 4a — explain a proposed selection | Complete | Compared scoped and full reports against discovery, exercised missing and moved inputs and reproduced the historical yq failure. [Pilot evidence](docs/test-selection-plan.md#phase-4-pilot-evidence) |
| 2. Test selection, Phase 4b — execute a validated selection locally | Complete | Ordered IDs matched execution on each scoped snapshot. The historical replay preserved its failure, full fallback ran, and the integrated offline matrix passed on all three targets. [Selection evidence](docs/test-selection-plan.md#phase-4-pilot-evidence) |
| 3. Menu performance, Stage 1 — evaluate shared value formatting per browser open | Next | Independent of test selection. Capture baseline text for every bundled row plus custom, discovered and preview cases. Compare the candidate for exact search, labels and ordered Details parity. Report per-command CPU, paired terminal latency, memory and regressions against the proposed FFmpeg target. Record the decision to retain, revise or discard the candidate. [Implementation checklist and measurement protocol](docs/ffmpeg-menu-performance-plan.md#implementation-stages) |
| 4. Menu performance — resolve the remaining investigations | Pending | Use task 3 measurements for prose preparation and redraws. Measure startup profile loading and guarded discovery separately. Record cost, affected menus, correctness constraints and a proceed/defer decision for each. Any change to architecture needs a separate decision. [Runtime investigations](docs/runtime-architecture.md#optimization-candidates) · [Prose and redraw experiments](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |

### Conditional decisions

- **Phase 5 local result reuse.** Proceed only if validated selection leaves substantial cost. For one bounded group, prove invalidation for input, environment, target, fixture and interrupted-run changes. Report executed, reused, failed and skipped outcomes separately. Consider CI selection or sharding only after local parity and measured savings. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) · [Two-shard pilot](docs/test-selection-plan.md#two-shard-host-pilot)
- **Further runtime changes.** Results of task 4 determine whether to try prose caching, idle redraw suppression, candidate-only profile loading or cheaper guarded discovery. A persistent index, worker or daemon would need a separate architecture decision. [Acceptance measures](docs/ffmpeg-menu-performance-plan.md#before-and-after-measurement)
- **Source archive navigation.** Decide whether to ship the root roadmap or provide a checkout link in packaged guides. The current builder omits the root file. If package policy changes, check navigation in an extracted source archive. [Archive contents](docs/releases.md#build-from-source)
- **Hosted documentation coverage.** Local reviewers can include the two Markdown files under `.github/` explicitly. If the same coverage is wanted on pushes, add them to the CI link check and its bounded retry, then confirm both input lists. [Current CI scope](docs/development.md#continuous-integration)
- **New demonstration media.** Before publishing a fresh recording, update the generator’s rsync and ls scene expectations for the expanded profiles. Require the rendered cells, pending lines, cursors and nonexecution markers to pass. The existing assets retain their dated provenance. [Capture scope and reproduction](docs/assets/README.md#regeneration)

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

**Complete — baseline and exploratory prototype.** The [terminal baseline](docs/runtime-architecture.md#local-performance-baseline) measures eager loading, startup and idle work. The [FFmpeg experiment](docs/ffmpeg-menu-performance-plan.md#earlier-prototype-results) used a temporary wrapper on an earlier profile inventory. Tasks 3 and 4 track the proposed changes and their verification.

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

For open development tasks, update the status in [remaining work](#remaining-work), link the acceptance evidence and move **Next** to the first actionable row. Keep experiment results with the plan and dated test outcomes with the verification report.
