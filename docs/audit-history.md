# Development and audit history

The browser began as a way to choose a command option in Bash and return to an editable command line. The early reviews tested that editing boundary. Later audits checked which documented choices the bundled menus described and which options discovery recovered from fixed help and manual replies. The sections below follow that sequence through the three-level menu and release-candidate checks. [Remaining work](../ROADMAP.md#remaining-work)

## Ubuntu default and optional commands

The Ubuntu batch added edition-aware package-manager and Bash help, a bundled reference for installed commands with missing help, and a root result for every shipped name, kernel companion and ranked optional row. The family audit records source versions, the six image results and the verification matrix. [Ubuntu coverage audit](ubuntu-coverage-audit.md) The corrected combined snapshot passed 2,021 tests with one Windows-only skip on each of the three offline targets. [Verification matrix](ubuntu-coverage-audit.md#combined-offline-matrix-2026-11-26)

## Phase 1 Details layout and terminal evidence

Phase 1 reviewed 347 invocations across 346 previously guidance-only names. The review added 2,199 selectable declarations across 150 names and retained guidance for 197 invocations. The final focused host runs passed 109 provider, argument, discovery and integration tests and 53 renderer and terminal tests. A separate 60×16 Bash/tmux check exercised `xzgrep --reg` with a quoted trailing operand. Escape restored the pending line and cursor, and selecting `--regexp=` preserved the operand. [Provider results and exceptions](ubuntu-coverage-audit.md#phase-1-provider-review)

The pre-edit baseline at `5783021` used the real Bash binding, the bundled rsync profile and an isolated tmux pane. With `CLI_HELP_DISCOVERY=off`, type `rsync --archive --compress --human-readable --itemize-changes --partial --` and press Alt-H, Ctrl-U, Right six times, Down, then D twice. This selects Network, option 2 of 38, `--bwlimit=RATE` in Expanded. Scroll with `]` through the final line. The harness checked that cancellation restored the exact line and cursor and that the guarded rsync function never executed. [Bundled rsync profile](../profiles/rsync.json) · [Terminal harness](../tests/test_terminal_screen.py)

| Capture | Color mode | Accepted-suffix columns | Visible rows at opening / total Details rows |
| --- | --- | ---: | ---: |
| Baseline 60×16 | Monochrome | 1 | 7 / 53 |
| Baseline 80×24 | Monochrome | 1 | 11 / 50 |
| Revised 80×24 | Color and monochrome | 1 | 11 / 50 |
| Revised 160×40 | Color and monochrome | 3 | 19 / 26 |

At 80×24 the one-byte offset form and its two-line explanation appear together on the second page. At 160×40 the first column ends with `NKB · kB/s`, the second begins with `NM or NMiB · MiB/s`, and the third ends with the offset form. Its explanation reaches “granularity” on an indented line below that value. The columns start at cells 0, 54 and 108. Every color frame matched its monochrome counterpart cell for cell. The captured attributes showed underlined literals, normal explanation text, an accent on option names and reverse video on the selection. Both modes used `COLORFGBG=15;0` with `NO_COLOR=1` for monochrome.

Raw JSON frames and the capture driver are retained locally under `tests/reports/phase1-details/`. The files include the input, dimensions, key sequence, scroll ranges, plain cells and styled cells. For Phase 2 use the same rsync state, the three-entry bundled `git worktree remove ` menu in Simple at opening (first option `-f`, final option `-h`), and FFmpeg’s Codec parameters category in Simple (from opening, Right 13 times). Capture FFmpeg at entry 1 (`-alpha_mode`), after PageDown and at End (entry 92, `-trellis`). The stable two-size rsync captures can be reused. [Column and style regressions](../tests/test_detail_columns.py)

## Bash integration, distribution and compatibility

| Period | Change and verification |
| --- | --- |
| October 17, 2026 | The initial browser combined Bash bindings, declarative drivers, documentation discovery and collection review. Per-user installation, removal, conflict review and verified release downloads followed. [Changelog](../CHANGELOG.md) |
| October 23 | On Ubuntu 24.04 WSL2, the pre-fix suite recorded 423 passes, two expected failures and one skip. Conflicting help/manual arity could permit editing inside an unfinished argument. A wrapped line could duplicate the prompt after shrinking the terminal. The follow-up reconciled explicit arity, restored Readline's display and added ten routes. Its suite recorded 437 passes and one Windows-only skip. [Original findings](functional-review-2026-10-23.md) · [Fixes and live checks](review-fixes-2026-10-23.md) |
| Compatibility expansion | The dependency follow-up exercised all 30 previously skipped paths. Across 129 paths it recorded 128 live passes and one usage-only npm root. Its 304 documentation requests matched the route allowlists. The 30-second live harness limit differed from the interactive default. [Dependency follow-up and versions](compatibility-expansion-validation.md) |
| October release | Context handling, diagnostics, guarded package building and update recovery formed part of the published v0.1.2-alpha prerelease. Its release notes identify the tested platform, artifacts and installation limits. [v0.1.2-alpha release notes](release-notes-v0.1.2-alpha.md) |

## Value guidance and terminal presentation

The October work inventoried numerical descriptions, specified units and accepted forms, and carried their provenance through parsing, caching, editing, search and display. The maintained-contract follow-up closed 360 incomplete records, reaching 504 of 504 required contracts at that point. External documentation and heuristic diagnostics had separate evidence and limitations. [Numerical implementation history](numerical-inventory/README.md) · [Debt resolution](numerical-inventory/debt-resolution.md) · [Native terminal and POSIX checks](numerical-inventory/native-posix-verification.md)

The October 26 regression review exercised 942 bundled rows at three sizes. Of 358 named test cases, 182 paths had bundled or fixture documentation and 176 had routing evidence alone. The WSL suite had 1,316 passes and two skips. A separate Windows run passed 402 portable model tests. Parser repairs retained aliases and complete operands, while presentation checks covered exact opening-line deduplication, readable rows and terminal control characters. [Regression review](regression-review.md) · [Machine-readable outcomes](regression-coverage.json)

## Bundled menu progress

During November 21–24 the original **942 rows in 76 profiles** were checked against the applicable manuals. The reconciled menus contained **6,487 selectable rows**. The counts below include separate menu rows for aliases and repeat a spelling when it belongs to multiple command paths. Family reports distinguish selectable rows from unique effects, manual spellings and release-specific behavior.

| Command family | Profiles | Original rows | Reconciled rows | Evidence |
| --- | ---: | ---: | ---: | --- |
| `rsync` | 1 | 29 | 216 | [First pass](rsync-option-audit.md) · [Inventory](rsync-manual-coverage.md#manual-inventory) |
| GNU `tar` | 1 | 12 | 157 | [First pass](tar-option-audit.md) · [Inventory](tar-manual-coverage.md#manual-inventory) |
| GNU `grep` | 1 | 14 | 48 | [First pass](grep-option-audit.md) · [Inventory](grep-manual-coverage.md#manual-inventory) |
| GNU and uutils `ls` | 1 | 19 | 60 | [First pass](ls-option-audit.md) · [Inventory](ls-manual-coverage.md#manual-inventory) |
| OpenSSH — `ssh`, `scp`, `sftp` | 3 | 51 | 96 | [First pass](openssh-option-audit.md) · [Inventory](openssh-manual-coverage.md#manual-inventory) |
| Git — stash and worktree | 11 | 85 | 433 | [First pass](git-stash-worktree-option-audit.md) · [Inventory](git-stash-worktree-manual-coverage.md#menu-inventory) |
| Git — commit and log | 2 | 19 | 332 | [First pass](git-commit-log-option-audit.md) · [Inventory](git-commit-log-manual-coverage.md#manual-inventory) |
| `7z x`, `7zz x` | 2 | 8 | 114 | [First pass](7zip-extraction-option-audit.md) · [Inventory](7zip-extraction-manual-inventory.md#selectable-inventory) · [Verification](7zip-extraction-manual-coverage.md#verification) |
| `fd`, `fdfind` | 2 | 38 | 196 | [First pass](fd-option-audit.md) · [Inventory](fd-manual-inventory.md#option-and-spelling-inventory) · [Verification](fd-manual-coverage.md#compatibility-results) |
| `fzf` | 1 | 17 | 209 | [First pass](fzf-option-audit.md) · [Inventory](fzf-manual-inventory.md#option-effects-and-spellings) · [Verification](fzf-manual-coverage.md#compatibility-results) |
| `ffmpeg` | 1 | 16 | 1,759 | [First pass](ffmpeg-option-audit.md) · [Inventory](ffmpeg-manual-inventory.md#selectable-inventory) · [Verification](ffmpeg-manual-coverage.md#compatibility-results) |
| `yq eval` | 1 | 15 | 69 | [First pass](yq-eval-option-audit.md) · [Inventory](yq-eval-manual-inventory.md#effects-and-spellings) · [Verification](yq-eval-manual-coverage.md#compatibility-results) |
| iproute2 — `ip address`, `ip link`, `ip route`, `ss` | 4 | 36 | 175 | [First pass](iproute2-option-audit.md) · [Inventory](iproute2-manual-coverage.md) · [Verification](iproute2-systemd-openssl-verification.md#compatibility-results) |
| systemd — `systemctl`, `journalctl` | 4 | 50 | 216 | [First pass](systemd-option-audit.md) · [Inventory](systemd-manual-coverage.md) · [Verification](iproute2-systemd-openssl-verification.md#compatibility-results) |
| OpenSSL — `s_client`, `x509`, `dgst` | 3 | 33 | 370 | [First pass](openssl-option-audit.md) · [Inventory](openssl-manual-coverage.md) · [Verification](iproute2-systemd-openssl-verification.md#compatibility-results) |
| `uv` | 5 | 56 | 454 | [First pass](uv-option-audit.md) · [Inventory](uv-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| Ruff — `ruff check`, `ruff format` | 2 | 30 | 92 | [First pass](ruff-option-audit.md) · [Inventory](ruff-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| `pytest` | 1 | 18 | 121 | [First pass](pytest-option-audit.md) · [Inventory](pytest-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| Go — `go build`, `go test`, `go run`, `go mod tidy` | 4 | 44 | 171 | [First pass](go-option-audit.md) · [Inventory](go-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| .NET — `dotnet build`, `publish`, `restore`, `run`, `test` | 5 | 76 | 242 | [First pass](dotnet-option-audit.md) · [Inventory](dotnet-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| `bun run` | 1 | 8 | 121 | [First pass](bun-run-option-audit.md) · [Inventory](bun-run-manual-coverage.md) · [Verification](devtools-batch-verification.md#compatibility-results) |
| Podman — `run`, `build`, `exec`, `logs` | 4 | 44 | 339 | [First pass](podman-option-audit.md) · [Run](podman-run-manual-coverage.md) · [Build, exec and logs](podman-build-exec-logs-manual-coverage.md) |
| PostgreSQL — `psql` | 1 | 21 | 70 | [Inventory](psql-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| Ansible — `ansible-playbook` | 1 | 21 | 61 | [Inventory](ansible-playbook-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| Azure CLI — `az` | 3 | 35 | 50 | [Inventory](azure-cli-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| Google Cloud CLI — `gcloud` | 3 | 34 | 91 | [Inventory](gcloud-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| Espressif — `esptool`, `esptool.py` | 3 | 30 | 77 | [Inventory](esptool-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| PlatformIO — `pio`, `platformio` | 4 | 68 | 98 | [Inventory](platformio-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |
| Arduino — `arduino-cli compile` | 1 | 15 | 50 | [Inventory](arduino-cli-manual-coverage.md) · [Verification](remaining-bundled-verification.md#compatibility-results) |

The iproute2, systemd and OpenSSL revisit closed 642 additional rows. The next six development-tool families added 969, and the last seven families added 273. In that last batch the tests walked all 497 rows on 16 command paths. Each of the three Ubuntu/Python targets recorded 1,581 passes, zero failures and one Windows-only skip. The strict numerical gate covered 4,426 required records. [System-tool batch](iproute2-systemd-openssl-verification.md) · [Development-tool batch](devtools-batch-verification.md) · [Final bundled verification](remaining-bundled-verification.md)

## Discovered command help

The November discovery audits covered **162 paths across 73 executable names**. Source versions describe the documentation replayed. The host and Noble labels describe the systems that drew the menus. A path can appear here and in the bundled inventory because each route exercises a different source of help. [Maintained matrix](../tests/fixtures/help/matrix.json) · [Fixture provenance](../tests/fixtures/help/README.md)

| Tier | Paths | Observed disposition and checks |
| --- | ---: | --- |
| [Essential](essential-discovery-audit.md) | 46 | 45 selectable menus and one usage-only npm root. Historical captures yielded 597 rows, compared with 3,541 on the complete Resolute or vendor inputs. A shared-reader regression in the historical AWS S3 description failed the initial suites. After repair each target recorded 1,708 passes and one skip. [Essential results](essential-discovery-verification.md) |
| [Next](next-discovery-audit.md) | 65 | All 65 routes supplied selectable declarations, totaling 3,399 rows. GCC retained its bounded fixed-help output when the manual exceeded the byte limit. [Developer tools](discovery-next-tools.md) · [Cloud and embedded tools](discovery-cloud-tools.md) |
| [Extended](extended-discovery-audit.md) | 51 | The primary editions yielded 3,711 rows. Of these paths, 47 had their own selectable help, two iproute2 paths gave usage-only diagnostics and two 7-Zip extraction paths reopened root help. Those root replays added 52 row visits. [System tools](discovery-extended-tools.md) · [Media and utilities](discovery-media-utilities.md) |

The combined Next and Extended walks exercised 7,162 row visits per target, including both root replays. The frozen-source suites recorded 1,870 passes and one Windows-only skip per target. The checks examined fixed requests, shell cells, cancellation, exact insertion and the absence of pending-command execution. The underlying inventories preserve source editions, alternate captures and empty results. [Combined verification](next-extended-discovery-verification.md)

## Test selection, menu redesign and release verification

### Test duration and repository workflow

Phases 1–4 completed the focused edit loop, paired timing baseline, duplicate-work reductions and local test selection. The iproute2 and yq pilots verified selection reports, ordered execution, full fallback and detection of a historical yq failure. Full offline checks ran on all three targets. The two-shard timing applies to one host pilot. [Three-target verification](test-selection-plan.md#full-offline-verification) · [Selection pilots](test-selection-plan.md#phase-4-pilot-evidence) · [Host sharding](test-selection-plan.md#two-shard-host-pilot)

The local refresh aligned the README, controls and gallery with the unpacked runtime. Git, the package builder and the link checker account for generated fixture workspaces, and both hosted link-check attempts include the contributor and pull-request guides. [Refresh workflow](local-build-refresh.md) · [Repository configuration](development.md#repository-configuration)

### Menu review and v0.4.0-alpha selection

Stage 1 reused shared value formatting within each menu open. Warm FFmpeg first-frame medians improved by 31.0–31.5% with matching rows. The earlier performance-only v0.4.0-alpha candidate passed 1,879 tests per target with one Windows-only skip, and an independent build reproduced its packages. [Architecture baseline](runtime-architecture.md#local-performance-baseline) · [Stage 1 evaluation](ffmpeg-menu-performance-plan.md#stage-1-evaluation) · [Candidate identity](release-candidate.md#identity-and-evidence-boundaries)

The menu edit review approved implementation of the revised mockups and verification at both terminal sizes. Six real Bash captures show Simple, Detailed and Expanded at 80×24 and 60×16, including the option count at each level. The redesign passed 1,887 tests per target with one Windows-only skip. All 15 package tests used fresh temporary builds after the earlier candidate failed the changed source-inventory comparison. [Approved review and captures](superpowers/plans/2026-11-24-menu-detail-levels.md#review-record) · [Redesign verification](superpowers/plans/2026-11-24-menu-detail-levels-verification.md#regression-results)

The combined v0.4.0-alpha candidate retained that version number because the performance-only build was unpublished. It included shared value formatting, all three menu levels, compact category labels, shared unit notes and unit search. The serial prose-reuse prototype, idle redraw suppression and serial profile-validation changes were outside the frozen candidate. The November 25 capture's 160 runtime, configuration, profile and version fingerprints matched the release-scope checkout at `bc78f9f` and the capture-build manifest. All six public media files matched their recorded hashes. [Version assignment](versioning.md#assigning-the-next-number) · [Release contents](releases.md#version-040---alpha) · [Controls](usage.md#browser-controls) · [Capture provenance](assets/README.md#capture-evidence)

### Follow-up performance decisions

The investigation compared the three-level browser with the saved pre-redesign renderer. It used real Bash terminal frames and controlled discovery fixtures. [Measurement methods](menu-cost-measurements.md#reproducing-the-measurements)

| Area | Result and decision |
| --- | --- |
| Serial prose reuse | Unfiltered FFmpeg opening fell from 546 to 519 ms at 80×24 and from 555 to 530 ms at 60×16. The small Git control changed little. The 4.4–5.4% gain fell below the 30% target, so adoption was deferred. [Experiment](serial-prose-reuse-experiment.md) |
| Idle redraws | Retained. Idle draws fell from 66 to zero per 10 seconds across both tested sizes and menus. Geometry polling, resize recovery and input remained responsive. [Terminal evidence](menu-cost-measurements.md#idle-redraw-experiment) |
| Serial profile validation | Retained. Bundled loader CPU fell from 118.36 to 74.04 ms at the median. The small menu opened faster with and without overrides, and full-set validation and diagnostics matched. [Loader evidence](menu-cost-measurements.md#serial-profile-validation-experiment) |
| Guarded discovery | Deferred. An ordinary valid cache hit made no probes. The guarded yq hit made one required identity probe and took 11 ms. [Discovery evidence](menu-cost-measurements.md#guarded-discovery) |
| Parallel processing | Kept serial execution. Four processes reduced the median FFmpeg opening time from 498 to 323 ms in the pool comparison while peak PSS increased from 42 to 90 MiB. Threads slowed opening. [CPU, memory and compatibility results](menu-cost-measurements.md#worker-pools-and-cpu-limits) |

### Local release verification

Both 0.4 candidates checked 1,003 packaged inputs against their frozen Git sources and reproduced all 11 release files byte for byte. The archives, launcher, embedded installer payload and checksums passed verification. Each candidate was tested with one full offline suite per target. [Build records and digests](release-candidate.md)

| Candidate | Frozen source and results |
| --- | --- |
| Combined v0.4.0-alpha | `cc30ade99d1ddf2f593b409f66bd05dc0029f44c`. Each target recorded 1,888 passes, zero failures and one Windows-only skip. Historical upgrade, update and removal passed on all three targets. The installed Bash adapter matched the six reference frames and preserved the filter, selection, pending command and terminal state at both sizes. The verified local files remain under `dist/candidate-v0.4.0-alpha-combined/`. [Combined verification](release-candidate.md#combined-candidate-verification) |
| v0.4.1-alpha | `cced50757a53612860d34bbcd77b0f2e0d99d0f0`. Idle redraw suppression and faster serial profile validation were included together in the local patch candidate. Each target recorded 1,890 passes and one Windows-only skip. Installed-menu and historical-upgrade checks passed on all three targets. [Patch verification](release-candidate.md#v041-alpha-local-candidate) · [Combined performance verification](menu-cost-measurements.md#combined-offline-verification) |

Publication was skipped for both candidates. If publication resumes with authorization, confirm hosted Linux and documentation checks on the verified commit, create the matching annotated tag, publish the prerelease from a draft and compare the downloads byte for byte with the tested files. [CI scope](development.md#continuous-integration) · [Publication procedure](releases.md#release-provenance-and-publication)

## Reading the evidence

For an option question, start with the family inventory. For a discovery question, start with the tier and follow the source edition to its manifest. The tests consume several Markdown inventories directly. Raw captures, machine-readable review decisions and rendered terminal checks retain their distinct roles. [Audit procedure](development.md#auditing-command-help) · [Maintained fixtures](../tests/fixtures/) · [Numerical review decisions](numerical-inventory/review.json)

The detailed first-pass narratives and October per-path tables preceding this condensation are available in local Git history at `1f26c69202cbd2231e51889d273a55e6a24c0479`. For example, `git show 1f26c692:docs/rsync-option-audit.md` reads the original option-by-option account. Generated logs under `tests/reports/` are local evidence and can be absent in a fresh checkout.
