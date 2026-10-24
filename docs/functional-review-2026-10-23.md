# Functional review — 2026-10-23

[Documentation index](README.md) · [Compatibility guide](compatibility.md)

This report preserves the pre-fix review evidence. The subsequent
[fix and compatibility report](review-fixes-2026-10-23.md) records the corrections
to R1/R2, the ten added command paths, and fresh verification results.

The reviewed behavior supports composing option-rich simple commands while
retaining control of execution. Real Bash tests verify that selection changes
the pending line, cancellation preserves it, and help requests do not receive
pending workload arguments. Generated option metadata and terminal resizing
remain significant limits. No production implementation, supported platform,
driver collection, or architecture was changed by this review.

## Evidence and environment

Validation used Ubuntu 24.04 under WSL2 on x86_64, Linux 5.15.153.1,
Bash 5.2.21, Python 3.12.3, GCC 13.3.0, tmux 3.4, and man-db 2.12.0.
The inspected Git base was `797117b1adc052004705850ddd863975e63e7fce`.
Temporary homes, caches, repositories, terminal sockets, and installation
prefixes isolated test operations. No system package installation, personal
shell registration, cloud workload, container workload, or transfer was run.
The full suite includes controlled installation and release-build tests in
temporary directories; those do not establish a new published release.

| Evidence lane | Result | Interpretation |
| --- | --- | --- |
| Initial complete `bash tests/run.sh` | 412 tests; 18 failure outcomes, 154 error outcomes, 1 skip | Includes initial untracked-test defects, fresh-home terminal setup failures, and source changes during packaging checks; not a clean product baseline |
| Complete suite after review additions | 426 tests: 423 passed, 2 expected failures, 1 skip; no failures or errors | Eight preflights passed; full unittest discovery completed in 212.02 seconds |
| Maintained live matrix, four-second source limit | 44 passed, 4 failed, 0 skipped, 1 unsupported | Default harness limit; failures retained |
| Maintained live matrix, fifteen-second source limit | 48 passed, 0 failed, 0 skipped, 1 unsupported | Help/metadata/in-memory insertion evidence at the longer limit |
| Additional live paths at both limits | 5 passed | `grep`, `find`, `tar`, `git rebase`, `docker build` |
| Added composition fixtures | 47 literal before/after scenarios across 44 paths | Exact resolved path, selected flag, final line, and character cursor |
| Added real-terminal cases | 3 passed in focused validation | Multi-value rejection, search/cancel/reopen/insert, Unicode, rendered screen and history |

Failure counts can include multiple subtests within one test method; they must
not be subtracted from test-method totals to infer a pass count. Expected
failures remain unresolved behavior, not passing acceptance tests.

The pre-existing untracked `test_functional_matrix.py` changed during the initial
run. Its initial errors included local-variable shadowing and incomplete mocks;
its subsequent focused run completed 36 tests with one platform-specific skip.
That file and `curses_stub.py` were preserved. Two initial release assertions
compared source snapshots while files were changing. Both passed in the final
run, whose source fingerprints confirmed no changes during verification.
The interrupted final attempt has no completion summary and is not counted as
a completed suite. The single final skip is a Windows-only probe test on Linux;
it does not establish Windows support. The two expected failures are R1 and R2
below. There were no unexpected successes.

## Findings ordered by priority

### R1 — P2: source merging can discard a richer required-value count

Location: [discovery.py](../cli_help/discovery.py), `build_profile`, lines 342–345;
the resulting metadata is consumed by [core.py](../cli_help/core.py), lines
223–226.

When help has `--pair NAME` and a later manual has `--pair name value`, each
source parses independently, but merging retains the first source's one-value
metadata. The metadata upgrade runs only when the previous argument is empty.
Consequently, `tool --pair label --next` is accepted as an editable option slot
even though the second documented value has not been supplied. Selecting another
flag would occupy that value position.

Reproduction:

```bash
PYTHONPATH=cli_help:tests python3 -m unittest \
  test_review_workflows.MetadataReviewTests.test_richer_manual_arity_replaces_an_existing_single_value -v
```

Expected: rejection until both required values are present. Actual: a context is
returned with `--next` as the editable query. The regression is marked as an
expected failure; its source-control assertions run in setup, outside that
marker. This is a controlled conflicting-source reproduction. No specific
installed CLI in the live matrix was shown to trigger that exact conflict.

Recommendation: define and test a deterministic reconciliation rule for argument
count and optionality when both sources already contain argument metadata.
Preserve source disagreements in diagnostics rather than silently assuming that
the first declaration is complete.

### R2 — P2: shrinking wrapped input can duplicate prompt rows

Location: [terminal regression](../tests/test_terminal_screen.py),
`WrappedResizeTests.test_wrapped_shrink_reopen_preserves_rendered_screen`,
line 228; [Bash integration](../bash/interactive-help.bash), `_cli_help_widget`.

On Bash 5.2.21/tmux 3.4, enter a long wrapped `rsync` command at 100×24, shrink to
60×16, and reopen the browser. Expected: one restored prompt/input display.
Actual: duplicate prompt/input rows after returning from the browser. The
existing expected-failure regression reproduces after terminal setup is fixed.
The separately tested Ctrl-L recovery restores the display. Pending input and
non-execution checks remain independent of the rendered-screen assertion.

```bash
python3 -m unittest discover -s tests -p 'test_terminal_screen.py' -v
```

The [existing investigation](development.md#rendered-screen-regressions) records
an ordinary Bash resize control with similar behavior. Root-cause attribution
to a particular upstream component remains unverified. Recommendation: retain
the regression and documented recovery while testing any workaround against
multiple Bash and terminal versions.

## Compatibility and environment limits

**Discovery latency.** Cached third-party binaries on the Windows-mounted
filesystem showed slow startup. Fixed-route diagnostics measured approximately
2.67 seconds for `docker help run`, 4.38 seconds for Compose help, 2.54 seconds
for Terraform help, and 2.52 seconds for OpenTofu help. The initial Docker run
case lacked sentinel options; a repeat recovered them with both executable and
manual sources. Terraform and OpenTofu repeated successfully at four seconds;
Compose still exceeded four seconds and succeeded at fifteen. These are measured
environment-dependent results, not a parser fix or evidence of acceptable
interactive latency. The browser's default two-second limit was not relaxed.

**GNU find argument metadata.** `find` 4.9.0 exposes `-name`, `-type`, and
`-maxdepth`, and literal insertion succeeds. Its manual declarations use lowercase
placeholders without a separate description column. These declarations currently
produce empty `argument` metadata, so the required-value guard is incomplete.
The added find cases establish option visibility and editing, not complete
predicate parsing or argument enforcement. A reviewed profile is the practical
route for dependable metadata; expression operators and `-exec` remain outside
the tested simple-command workflow.

**Unadapted requested paths.** The following paths fail before discovery with the
supplied registry. This is a compatibility gap, not a failure of an advertised
route. No drivers were added and no target actions were invoked.

| Family | Paths requiring explicit profiles or drivers |
| --- | --- |
| GitHub CLI | `gh pr view`, `gh pr create` |
| Rust Cargo | `cargo test` |
| Docker Compose | `docker compose logs`, `docker compose exec` |
| Kubernetes | `kubectl describe`, `kubectl logs` |
| Helm | `helm upgrade` |
| AWS CLI | `aws s3 sync` |
| rclone | `rclone sync` |

**Documented syntax limits.** Pipelines, redirects, substitutions, unbalanced
quotes, wrappers, and aliases remain unsupported. FFmpeg stream-qualified
switches, GCC comma-joined switches, and 7-Zip attached-value switches are not
offered as truncated substitute flags. Unknown options and short bundles do not
have general argument-arity support. Root npm 9.2.0 remains the expected empty
option-help case; its supported subcommands were checked separately.

**Collection failure semantics.** Existing tests cover invalid input, missing
manuals, locks, stale edits, scan checkpoints, and incomplete saves. Collection
profile/driver/report writes are atomic per file, not one transaction across all
files. Review backups support inspection after partial saves; the review does
not establish automatic rollback of the entire collection.

## Functional coverage

| Area | Evidence | Remaining qualification |
| --- | --- | --- |
| Profiles and precedence | Bundled/custom profiles, exact command identity, static precedence, driver overlays | Curated profiles intentionally contain selected options |
| Option parsing | All 49 maintained corpus cases, captured sentinels, required/optional/paired values, aliases, boolean negation, ANSI and wrapped descriptions | Generated metadata still requires review; R1 and find limitation remain |
| Composition | 47 new combined workflows plus existing all-option mid-line edits; globals, repeated values, quotes, Unicode, suffix text, `--`, runner boundaries | No claim that edited workloads are semantically complete or executable |
| Bash interaction | Existing PTY suite plus two new jq tests; selection, cancel, bindings, search, categories, scrolling, exact line/cursor | Controlled target executables verify invocation boundaries |
| Rendered terminal | Existing tmux suite plus repeated Unicode search/cancel/insert and history checks | R2 persists; other terminal emulators are untested |
| Discovery | Auto/manual/off, fixed routes, cache separation/invalidation, missing sources, timeouts, output bounds, malformed text, subprocess cleanup | Bounds are not an operating-system sandbox |
| Collection workflows | Manual text/roff import, scans, guided review, previews, backups, validation, partial failures | Per-file atomicity only |
| Installation/release/update | Full existing suite in temporary homes and prefixes | No personal installation, hosted CI, publication, or remote delivery validation |

Detailed cases are in [composition fixtures](../tests/fixtures/help/review-workflows.json),
[additional captured help](../tests/fixtures/help/review-additions.json),
[workflow tests](../tests/test_review_workflows.py), and
[new terminal tests](../tests/test_review_terminal.py).

The complete command/version/result matrix follows below. A live pass checks
sentinel flags, declared sentinel argument counts, and literal insertion of every
discovered flag. It does not prove exhaustive option coverage. Additional find
rows deliberately do not claim argument-count coverage. Versions are observed
versions, not recommendations to install those versions.

| Command path | Observed version | Live 4 s / 15 s | Added combined edits |
| --- | --- | --- | --- |
| `7z` | 7-Zip 23.01 (x64) | passed / passed | 1 |
| `7zz` | 7-Zip (z) 23.01 (x64) | passed / passed | 1 |
| `aws ec2 describe-instances` | aws-cli/1.46.1 Python/3.12.3 Linux/5.15.153.1-microsoft-standard-WSL2 botocore/1.43.62 | passed / passed | 1 |
| `aws s3 cp` | aws-cli/1.46.1 Python/3.12.3 Linux/5.15.153.1-microsoft-standard-WSL2 botocore/1.43.62 | passed / passed | 1 |
| `borg create` | borg 1.2.8 | passed / passed | 1 |
| `cargo build` | cargo 1.75.0 | passed / passed | 1 |
| `clang` | Ubuntu clang version 18.1.3 (1ubuntu1) | passed / passed | 0 |
| `cmake` | cmake version 3.28.3 | passed / passed | 0 |
| `convert` | Version: ImageMagick 6.9.12-98 Q16 x86_64 18038 https://legacy.imagemagick.org | passed / passed | 1 |
| `curl` | curl 8.5.0 (libcurl 8.5.0) | passed / passed | 1 |
| `docker build` | Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2 | passed / passed | 2 |
| `docker compose up` | Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2; Compose 2.40.3+ds1-0ubuntu1~24.04.1 | failed / passed | 1 |
| `docker image ls` | Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2 | passed / passed | 1 |
| `docker run` | Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2 | failed / passed | 1 |
| `ffmpeg` | ffmpeg version 6.1.1-3ubuntu5 | passed / passed | 1 |
| `ffprobe` | ffprobe version 6.1.1-3ubuntu5 | passed / passed | 1 |
| `find` | find (GNU findutils) 4.9.0 | passed / passed | 2 |
| `gcc` | gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 | passed / passed | 0 |
| `gh pr list` | gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3) | passed / passed | 1 |
| `gh repo clone` | gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3) | passed / passed | 1 |
| `git commit` | git version 2.43.0 | passed / passed | 1 |
| `git diff` | git version 2.43.0 | passed / passed | 1 |
| `git log` | git version 2.43.0 | passed / passed | 1 |
| `git rebase` | git version 2.43.0 | passed / passed | 2 |
| `grep` | grep (GNU grep) 3.11 | passed / passed | 1 |
| `helm install` | v4.3.1+gc0d08d0 | passed / passed | 1 |
| `jq` | jq-1.7 | passed / passed | 1 |
| `kubectl config view` | Client Version: v1.37.1 | passed / passed | 1 |
| `kubectl get` | Client Version: v1.37.1 | passed / passed | 1 |
| `magick` | Version: ImageMagick 7.1.2-34 Q16-HDRI x86_64 c5d4ca8a0:20261014 https://imagemagick.org | passed / passed | 1 |
| `ninja` | 1.11.1 | passed / passed | 0 |
| `npm` | 9.2.0 | unsupported / unsupported | 0 |
| `npm install` | 9.2.0 | passed / passed | 1 |
| `npm run` | 9.2.0 | passed / passed | 1 |
| `pip` | pip 24.0 (Python 3.12) | passed / passed | 0 |
| `pip download` | pip 24.0 (Python 3.12) | passed / passed | 1 |
| `pip install` | pip 24.0 (Python 3.12) | passed / passed | 1 |
| `pip3 install` | pip 24.0 (Python 3.12) | passed / passed | 0 |
| `pnpm install` | 9.15.9 | passed / passed | 1 |
| `rclone` | rclone v1.60.1-DEV | passed / passed | 0 |
| `rclone copy` | rclone v1.60.1-DEV | passed / passed | 1 |
| `restic backup` | restic 0.16.4 compiled with go1.22.2 on linux/amd64 | passed / passed | 1 |
| `rg` | ripgrep 14.1.0 | passed / passed | 1 |
| `rsync` | rsync  version 3.2.7  protocol version 31 | passed / passed | 1 |
| `tar` | tar (GNU tar) 1.35 | passed / passed | 1 |
| `terraform apply` | Terraform v1.16.6 | passed / passed | 1 |
| `terraform plan` | Terraform v1.16.6 | failed / passed | 1 |
| `tofu apply` | OpenTofu v1.13.1 | passed / passed | 1 |
| `tofu plan` | OpenTofu v1.13.1 | failed / passed | 1 |
| `uv pip install` | uv 0.13.1 (x86_64-unknown-linux-gnu) | passed / passed | 1 |
| `uv run` | uv 0.13.1 (x86_64-unknown-linux-gnu) | passed / passed | 1 |
| `vlc` | VLC version 3.0.20 Vetinari (3.0.20-0-g6f0d0ab126b) | passed / passed | 0 |
| `wget` | GNU Wget 1.21.4 built on linux-gnu. | passed / passed | 1 |
| `yt-dlp` | 2024.04.09 | passed / passed | 0 |

## Where the add-on is most useful

1. **Long commands with infrequently recalled options.** Curated `rsync`, `grep`,
   `tar`, and Git profiles provide immediate descriptions without help-process
   startup. Tested workflows preserve quoted paths, filters, existing values, and
   command suffixes while an option is inserted.
2. **Supported nested command families.** Git, Docker, package tools, kubectl,
   AWS, and Terraform/OpenTofu benefit from path-specific option lists. Global
   configuration values and sibling command paths are kept distinct. Driver
   activation and explicit route coverage remain prerequisites.
3. **Data and media commands with ordinary literal options.** jq's paired values
   and FFmpeg/ImageMagick's supported flags benefit from descriptions and exact
   cursor placement. Tool-specific syntax and command semantics still need
   operator knowledge.
4. **Reusable local help collections.** Manual import and guided correction are
   useful where generated metadata is incomplete or automatic probing is slow.
   Corrected profiles can be browsed with discovery disabled.

Priority order for follow-up is R1 metadata reconciliation, R2 display behavior,
then explicit drivers for commonly requested missing paths. Compose `exec`
requires an explicit child-command boundary. `find` needs accurate reviewed
argument metadata before its value guard can be relied upon. Compatibility
expansion should retain independent sentinels and fixed documentation routes.

## Reproduction and local evidence

The existing full-suite entry point remains:

```bash
bash tests/run.sh
```

The review recorder adds per-test JSON outcomes, successful/failing subtest
records, source fingerprints, dependency versions, and an isolated home:

```bash
python3 tests/functional_review.py --suite review \
  --output tests/reports/review-new-run
python3 tests/functional_review.py --live --live-timeout 15 \
  --output tests/reports/review-live-new-run
```

The recorder uses `/usr/bin:/bin` unless existing tool directories are added with
repeated `--prepend-path /absolute/directory` arguments. A locally available
Compose plugin can be selected with `--compose-plugin-dir /absolute/directory`.
It does not install missing tools. The original live harness also accepts
`--timeout 15` and records that limit. Use distinct report directories to retain
comparisons between environments and limits.

Local evidence resides under `tests/reports/functional-review-2026-10-23/`:

| File | Contents |
| --- | --- |
| `baseline.log`, `baseline-summary.json` | Initial complete suite and its diagnostic outcomes |
| `final-suite.log` | Interrupted attempt; no completion claim |
| `completed-suite.log`, `completed-suite.json` | Stable complete run and individual outcomes |
| `completed-suite-environment.json` | Environment, dependency versions, source fingerprints |
| `live-programs.json`, `live-additions.json` | Original four-second live run |
| `live-15s/live-programs.json`, `live-15s/live-additions.json` | Full fifteen-second rerun |
| `probe-diagnostics.json` | Measured fixed-route retries and source warnings |
| `metadata-observations.json` | Source-merge and find metadata observations; Compose plugin version |
| `coverage-matrix.json` | Combined per-command versions, outcomes, scenarios, and gaps |
| `review-summary.json` | Aggregate final outcomes, findings, and verification limits |

Generated reports remain ignored by Git under the existing repository policy.
The maintained report, regression tests, and compact fixtures provide durable
reproduction instructions. Linux distributions other than the recorded Ubuntu
environment, other program versions, actual workload execution, and terminal
emulators outside the tested PTY/tmux configurations remain unverified.

The final run passed all six Bash syntax checks and both configuration checks
(default configuration and supplied drivers). Subsequent changes were limited
to finalizing this report; the tested runtime, fixtures, and test code remained
unchanged. The JSON report retains individual outcomes and subtest records.
