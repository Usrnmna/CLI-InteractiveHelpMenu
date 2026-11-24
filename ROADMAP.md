# Project roadmap

**Next task — complete the first-pass `psql` audit.** Start with its [21 bundled rows](profiles/psql.json) and reconcile the command with the upstream and both Ubuntu manuals. All 60 previously audited profiles have now completed their manual-coverage revisits. The [six-family verification record](docs/devtools-batch-verification.md) closes the final 18 menus.
The [combined iproute2, systemd and OpenSSL revisit](docs/iproute2-systemd-openssl-verification.md) is complete.
The [yq eval revisit](docs/yq-eval-manual-coverage.md),
[FFmpeg revisit](docs/ffmpeg-manual-coverage.md),
[fzf revisit](docs/fzf-manual-coverage.md),
[fd and fdfind revisit](docs/fd-manual-coverage.md),
[7-Zip extraction revisit](docs/7zip-extraction-manual-coverage.md),
[Git commit and log revisit](docs/git-commit-log-manual-coverage.md) and
[stash and worktree revisit](docs/git-stash-worktree-manual-coverage.md) are complete.
The [OpenSSH family revisit](docs/openssh-manual-coverage.md) is complete.
The [ls revisit](docs/ls-manual-coverage.md), [GNU grep revisit](docs/grep-manual-coverage.md),
[rsync client and daemon revisit](docs/rsync-manual-coverage.md), [GNU tar revisit](docs/tar-manual-coverage.md)
and [Podman family revisit](docs/podman-option-audit.md) are complete.

## Purpose and scope

The Interactive Help Menu helps a Bash user understand an option, select it
and continue editing the pending command. The current development goal is to
make the first line of help easy to scan while keeping the details needed to
choose and use each option correctly. Coverage includes bundled command
descriptions, options, operands and keywords, plus help displayed through
maintained discovery routes. The [project overview](README.md) describes the
product; the [documentation index](docs/README.md) covers its other capabilities.

Use this page to locate the next unfinished command and record progress.
Keep the detailed findings with each family audit. Update this roadmap when
a batch finishes, a source discrepancy blocks work, or the scope changes.

## Bundled menu progress

The first pass reviewed 718 of the 942 entries originally bundled, covering 60
of 76 profiles. The remaining 224 original entries span 16 profiles. These are
baseline counts. The number of options documented in the manuals must be
established separately for each command.

The last two columns track the revisit of the 60 previously audited profiles.
Record each family’s option counts, detail gaps and test evidence in its linked
audit. For a partial family, name the next command or option there and at the
top of this page. The Podman revisits added 295 selectable rows (152 run,
124 build, 13 exec and six logs). GNU tar added 145, rsync added 187, GNU grep added 34, ls added 41, OpenSSH added 45, Git stash/worktree added 348, Git commit/log added 313, 7-Zip extraction added 106, fd/fdfind added 158, fzf added 192, FFmpeg added 1,743 and yq eval added 54.
The combined revisit added 139 iproute2, 166 systemd and 337 OpenSSL rows.
The six development-tool families added 969 rows to the previous 5,245.
The bundled total is **6,214 rows across 76 profiles**, compared with the historical 942.

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
| `psql` | 1 | 21 | Next | — | — |
| `ansible-playbook`, `az`, `gcloud` | 7 | 90 | Pending | — | — |
| `esptool`, `esptool.py`, `pio`, `platformio`, `arduino-cli` | 8 | 113 | Pending | — | — |

## Manual-coverage revisit

1. **Inventory the manual before editing the profile.** For each exact command
   path, list the options in the upstream and both Ubuntu release references
   described below. Record aliases, argument forms, applicable versions and
   source sections. Map each spelling to its current menu entry or mark it
   missing. Use the previous audit’s manual-only list as a starting point.
   The [Podman audit](docs/podman-option-audit.md) gives examples, while the
   [tar audit](docs/tar-option-audit.md#manual-only-coverage) lists 157 Ubuntu
   long spellings outside its original 12 rows. That list includes aliases.
2. **Add the missing options.** Give each distinct applicable option a
   selectable entry. Account for every documented alias and check that its
   relationship to the option is discoverable. Preserve existing literal
   spellings, value guidance and command boundaries. Qualify version- or
   mode-specific options where they apply. If a command path cannot represent
   an option faithfully, record the exact blocker and keep that item open.
3. **Revisit Details on existing and new rows.** Keep the summary to one short
   statement of what the option does. Put syntax, defaults, interactions,
   units, side effects and version differences in Details when they change what
   someone would type or expect. The [Podman run revisit](docs/podman-run-manual-coverage.md#material-changes)
   shows how to retain host ownership and SELinux labeling effects in volume
   Details while keeping the row summary short.
4. **Close each family against its inventory.** Record the distinct options
   found, options already covered, rows added, aliases accounted for and
   remaining gaps. Record material detail gaps fixed or still open separately.
   Verify the added and revised entries using the terminal and sandbox checks
   below. Mark each coverage column verified only when its inventory reconciles,
   its open gaps are resolved and its checks pass. Apply the same coverage
   standard when the first pass resumes with `psql`.

## Reducing test duration

The [test selection plan](docs/test-selection-plan.md#phase-status-and-gates) records the focused edit loop, completed three-target timing baseline and verified reductions in duplicate work. The next testing task is the [Phase 4 report-only selection pilot](docs/test-selection-plan.md#4-add-explicit-selection-for-local-audits) for iproute2 and yq. Compare proposed selections against full runs and replay the historical yq failure before enabling selected execution. Persistent result reuse follows validation of selection and invalidation rules.

## Runtime performance follow-up

The [terminal runtime analysis](docs/runtime-architecture.md#local-performance-baseline)
records local costs for eager profile loading, large-menu text preparation and
idle wakeups. The [command menu performance plan](docs/ffmpeg-menu-performance-plan.md)
proposes shared value formatting for all command menus, checks search and
Details parity per command, and uses FFmpeg as the large-menu benchmark.
[Open investigations](docs/runtime-architecture.md#optimization-candidates)
cover redraws on unchanged timeouts, candidate-only profile loading and the cost
of discovery checks for guarded commands.

## Discovered command help

The [compatibility matrix](tests/fixtures/help/matrix.json) lists 162 maintained
command paths across 73 executable names at the pilot baseline. The matrix and
bundled inventories overlap. Count a bundled review against a discovery path
only when the audit also checks the help produced through that route.

| Matrix tier | Paths | Description review |
| --- | ---: | --- |
| Essential | 46 | Pending |
| Next | 65 | Pending |
| Extended | 51 | Pending |

For each path, identify its help source and version. Compare what the menu
displays with the applicable manual and available versioned help capture.
Some fixtures are synthetic or excerpted, and some root commands provide only
usage information. Record those outcomes explicitly. If a qualification appears
in a capture but disappears from the menu, trace it through parsing and
rendering, retain the original capture and add a regression for the loss.
See the [fixture provenance guide](tests/fixtures/help/README.md).

## How to audit a batch

Group consecutive command families into one verification batch when their profile and
manual changes can be reviewed independently. Record the included command paths
up front. Check each family’s inventory, executable fixtures and rendered menus
as soon as they are ready. Include shared parser, insertion and historical
capture tests that consume the changed data. Run the strict numerical review
against the integrated profiles. Once focused checks pass, take snapshots of the
same combined source and run the full suite once on each of the three targets.
Link every covered family to that matrix and list any blocked command separately.
If a full run finds a regression, fix it, repeat its focused checks and obtain
full verification of the corrected snapshot. Keep release-specific skips visible.

1. **Establish the reference.** Inventory the command paths, selectable entries
   and aliases. Compare them with the upstream manual and the Ubuntu 24.04 and
   26.04 man pages where available. Record the actual versions, source links
   and any differences. For tools without a distribution man page, use
   version-matched official command documentation and identify the missing source.
2. **Decide what belongs on screen.** Give each row a short explanation of its
   effect. Keep details that change the invocation or result, including operand
   requirements, units, defaults, order, interactions, side effects and version
   limits. Remove duplicated wording and generic menu instructions. Keep useful
   manual terms searchable. Preserve precise numerical and argument guidance
   when changing prose. An entry can pass review with its existing wording.
3. **Account for gaps.** Use the [manual-coverage revisit](#manual-coverage-revisit)
   to add missing options and restore material details. Record exact blockers
   and affected versions in the family audit so unfinished work remains visible.
4. **Verify the rendered result.** Inspect every added or revised row and its Details
   pane in a real terminal. At the 60×16 minimum, scroll to a consequential
   qualification and check that it is reachable. Search for a familiar manual
   term. Verify cancellation preserves the buffer and cursor, and selection
   inserts the intended spelling without executing the pending command.
5. **Run the compatibility checks.** Use the offline sandbox for focused tests
   while editing. At the end of a batch run the full suite on Ubuntu 26.04 with
   Python 3.14 and Ubuntu 24.04 with Python 3.10 and 3.12. Record pass, failure
   and skip counts with the environment. Record hosted CI separately when
   evidence for the revision is available. The [sandbox guide](docs/development.md#isolated-local-debugging)
   covers setup, targets and including new files.

## Recording progress and finishing the audit

For a partial batch, replace the status in its row with the exact command paths
reviewed, a link to the findings, any unresolved item and the next unchecked
path. Split a grouped row when that makes the remaining work clearer. Update
the **Next task** at the top. If profiles or matrix routes change, reconcile the
counts against the two linked inventories.

Bundled manual coverage is complete when each applicable documented option
and alias is accounted for, each distinct option is selectable, material details
are reachable in the menu, and the terminal and three sandbox checks pass.
The overall project also requires a source-backed review of every maintained
discovery path. Link the verification evidence from each family or route here.
