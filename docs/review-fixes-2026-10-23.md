# Review fixes and command-path additions

[Documentation index](README.md) · [Original review](functional-review-2026-10-23.md) ·
[Compatibility matrix](compatibility.md)

The follow-up corrects the two confirmed review findings and adds the ten
previously unadapted paths. The Bash/Python architecture, Linux scope, declarative
driver schema, and fixed documentation-only discovery boundary are retained.
No workload, package installation, deployment, transfer, or cloud action is
executed by validation. Existing unrelated files are preserved.

## Corrections

- **R1, argument metadata:** merging help/manual declarations retains the larger
  explicit argument count. At equal count, a required declaration takes precedence
  over an optional one. Conflicting declarations remain identified in option
  details alongside both source descriptions. Cache version 5 invalidates earlier
  inferred metadata. Both source orders, optionality conflicts, incomplete paired
  values, and cache invalidation have regressions. The original expected-failure
  marker is removed.
- **R2, wrapped resize:** a size change during browsing triggers Readline's own
  `clear-screen` after the callback returns. This restores one prompt at the top
  of the viewport, preserving the pending line, cursor, and scrollback in the
  tested environment. Unchanged-size cancellation keeps the original screen.
  The original expected-failure marker is removed. Selection, Ctrl-C, Unicode,
  custom triggers, rebound Ctrl-L, and repeated opening are covered.
- **Negative defaults:** `kubectl logs` exposed a declaration parsing defect in
  `--tail=-1`. A hyphen following `=` belongs to the value rather than a second
  flag. Negative-number and literal-value regressions prevent lost arity.
- **Existing vi configuration:** the documented `vi-insertion` setting maps to
  Bash's actual `vi-insert` keymap. Meta-map shortcuts retain their effective
  escape prefix. Tests cover rebinding, cleanup, and preservation of conflicting
  internal bindings.

The binding approach uses documented Readline macros and functions from the
[GNU Bash manual](https://tiswww.case.edu/php/chet/bash/bashref.html#Readline-Init-File-Syntax).
The runtime uses two reserved dispatch sequences rather than evaluating pending
text or synthesizing terminal input. Details are in the
[rendered-screen notes](development.md#rendered-screen-regressions).

## Added compatibility

The supplied driver collection must be enabled as described in the
[compatibility guide](compatibility.md#enable-the-drivers).

| Path | Fixed documentation request | Boundary and representative coverage |
| --- | --- | --- |
| `gh pr view` | `gh help pr view` | PR positional argument, JSON fields, jq expression, comments/web flags |
| `gh pr create` | `gh help pr create` | Quoted Unicode title/body, repeated reviewers, base branch, draft |
| `cargo test` | `cargo test --help` | Global configuration, features, manifest path, test filter; rejects options after `--` |
| `docker compose logs` | `docker compose logs --help` | Root context, multiple services, tail/since values, follow/no-color |
| `docker compose exec` | `docker compose exec --help` | Repeated environment values, user/workdir, no-TTY; stops at service before the child command |
| `kubectl describe` | `kubectl help describe` | Context/namespace globals, selectors, resource positional arguments |
| `kubectl logs` | `kubectl help logs` | Kubeconfig/namespace globals, pod/container, negative tail, follow/previous |
| `helm upgrade` | `helm help upgrade` | Release/chart positionals, repeated values files, set-string, install/timeout |
| `aws s3 sync` | `aws s3 sync help` | Profile/region globals, source/destination, repeated filters, dryrun/delete |
| `rclone sync` | `rclone sync --help` | Config/transfers globals, quoted paths, create-empty-src-dirs |

The offline corpus now contains 59 paths across the same 34 executable names.
Each new path has captured local help provenance, independently stated option
and argument expectations, fixed-route assertions, and two literal combined
edits. Existing corpus tests exercise every offered fixture flag, arity guards,
and executable sentinels. The sentinel tests confirm that pending arguments
are never forwarded to documentation requests. The original five extra live
paths (`grep`, `find`, `tar`, `git rebase`, `docker build`) are checked separately.

Rclone 1.60.1's subcommand help exposes a small set of sync-specific options;
the root `help flags` route retains global-option discovery. Compose-level
options between `compose` and the subcommand are outside the current resolver.
GNU find's lowercase manual-placeholder limitation from the review remains
outside these corrections. No complete workload-semantics guarantee is implied.

## Verification

Validation uses Ubuntu 24.04 under WSL2, Bash 5.2.21, Python 3.12.3, tmux 3.4,
GCC 13.3.0, isolated homes/caches/configuration, and the already available tool
versions. No system packages are installed. The full-suite recorder verifies
source fingerprints remain stable during execution.

| Evidence | Result |
| --- | --- |
| Complete Linux suite | 438 tests: **437 passed, 1 skipped, 0 failures/errors, 0 expected failures**; 226.56 seconds |
| Preflight checks | All six Bash syntax checks and both configuration checks passed |
| Maintained live matrix, 4-second limit | **58 passed, 0 failed, 0 skipped, 1 unsupported** |
| Maintained live matrix, 15-second limit | **58 passed, 0 failed, 0 skipped, 1 unsupported** |
| Additional live paths at each limit | **5 passed**: grep, find, tar, git rebase, Docker build |
| New command paths | **10 of 10 passed** at both limits, with no source warnings |
| Source stability | No source changes during the full suite or either live run |

The single skip is a Windows-specific probe test running on Linux. Npm root
help remains intentionally unsupported; its install/run paths pass separately.
All earlier expected-failure markers associated with R1/R2 are removed, and both
regressions pass as ordinary tests. The runtime and test behavior were unchanged
after verification; subsequent edits finalize this report and correct a stale
test docstring.

| New path | Observed tool version | 4 s / 15 s |
| --- | --- | --- |
| `gh pr view`, `gh pr create` | gh 2.45.0, Ubuntu 2.45.0-1ubuntu0.3 | passed / passed |
| `cargo test` | Cargo 1.75.0 | passed / passed |
| `docker compose logs`, `docker compose exec` | Docker 29.1.3; Compose 2.40.3+ds1-0ubuntu1~24.04.1 | passed / passed |
| `kubectl describe`, `kubectl logs` | kubectl client v1.37.1 | passed / passed |
| `helm upgrade` | v4.3.1+gc0d08d0 | passed / passed |
| `aws s3 sync` | aws-cli 1.46.1, botocore 1.43.62, Python 3.12.3 | passed / passed |
| `rclone sync` | v1.60.1-DEV | passed / passed |

The four-second run no longer reproduced the original review's startup-time
failures. This is a measured result for this environment, not a guarantee of
cold-start performance or of the browser's unchanged two-second default.
Seven existing paths retain secondary-source warnings: GCC's manual exceeds
the output bound, and the VLC, pip install/download, pip3 install, and npm
install/run manuals yield no recognizable declarations. Their executable-help
sources satisfy the required sentinels. Warnings remain in both live reports.

A stopped diagnostic attempt exposed an escaped-quote parsing error in the new
binding-conflict check; that error was corrected before the final run. An earlier
complete attempt had one stale inventory assertion expecting 49 paths. Only that
assertion was updated to 59 in the pre-existing functional-matrix file; its other
content and the curses stub are preserved. These earlier logs are retained as
`suite-interrupted.log` and `suite-inventory-stale.*`, separately from final evidence.

Local machine-readable evidence is under
`tests/reports/review-fixes-2026-10-23/`. The full suite uses `suite.json`,
`suite.log`, and `suite-environment.json`; live runs use separate `live-4s/` and
`live-15s/` directories with per-path versions, sources, warnings, and statuses.
`verification-summary.json` aggregates the final outcomes, and
`coverage-matrix.json` combines all 64 live paths with their versions, routes,
statuses, and source warnings. The Compose plugin version is recorded separately
because the harness's Docker version request reports the client version.
The generated reports follow the existing Git-ignore policy. Maintained tests,
captured excerpts, and this report remain part of the source collection.

Reproduce with:

```bash
python3 tests/functional_review.py --suite suite --output tests/reports/fixes-new-run
python3 tests/functional_review.py --live --live-timeout 4 --output tests/reports/live-new-run
```

Use `--prepend-path` for existing tool directories and `--compose-plugin-dir`
for a locally available Compose plugin. A separate run with `--live-timeout 15`
distinguishes slow help startup from unavailable declarations. The browser's
default two-second discovery timeout remains unchanged. Missing tools are skips,
failed probes are failures, and npm root's empty option help remains unsupported.
Other Bash versions, terminal emulators, Linux distributions, and tool versions
remain unverified by this environment.
