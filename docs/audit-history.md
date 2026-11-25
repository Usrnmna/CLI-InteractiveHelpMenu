# Development and audit history

The browser began as a way to choose a command option in Bash and return to an editable command line. The early reviews tested that editing boundary. Later audits checked which documented choices the bundled menus described and which options discovery recovered from fixed help and manual replies. The sections below follow that sequence through the three-level menu and release-candidate checks. [Remaining work](../ROADMAP.md#remaining-work)

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

| Development stage | Recorded outcome |
| --- | --- |
| Local test selection | Timing identified duplicate work. Pilot groups for iproute2 and yq exercised ordered selection, full-suite fallback and a historical failure. Result reuse remained conditional. [Timing and selection evidence](test-selection-plan.md) |
| Shared value formatting | Warm FFmpeg first frames improved by 31.0–31.5% in the Stage 1 comparison. The prepared v0.4.0-alpha candidate passed 1,879 tests per Linux target with one Windows-only skip, and its packages were independently reproduced. [Performance evaluation](ffmpeg-menu-performance-plan.md#stage-1-evaluation) · [Candidate verification](release-candidate.md) |
| Simple, Detailed and Expanded menus | Six real-terminal captures covered the three levels at 80×24 and 60×16. The redesign recorded 1,887 passes and one Windows-only skip on each Linux target. Its package checks used fresh builds after the earlier candidate failed the changed source-inventory comparison. [Menu verification](superpowers/plans/2026-11-24-menu-detail-levels-verification.md) |
| Follow-up measurements | Reusing prose reduced warm FFmpeg opening time by 4.4–5.4% in the tested sizes, below the 30% target. Idle redraws and serial profile validation remained candidates for separate experiments. [Measured decisions](menu-cost-measurements.md#decisions) · [Prose-reuse experiment](serial-prose-reuse-experiment.md) |

The candidate predates the three-level menu. Release scope, candidate checks and publication status are tracked in the [project roadmap](../ROADMAP.md#remaining-work). Public images and recordings have their own capture provenance. [Media inventory](assets/README.md)

## Reading the evidence

For an option question, start with the family inventory. For a discovery question, start with the tier and follow the source edition to its manifest. The tests consume several Markdown inventories directly. Raw captures, machine-readable review decisions and rendered terminal checks retain their distinct roles. [Audit procedure](development.md#auditing-command-help) · [Maintained fixtures](../tests/fixtures/) · [Numerical review decisions](numerical-inventory/review.json)

The detailed first-pass narratives and October per-path tables preceding this condensation are available in local Git history at `1f26c69202cbd2231e51889d273a55e6a24c0479`. For example, `git show 1f26c692:docs/rsync-option-audit.md` reads the original option-by-option account. Generated logs under `tests/reports/` are local evidence and can be absent in a fresh checkout.
