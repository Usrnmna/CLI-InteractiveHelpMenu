# Functional review — 2026-10-23

This historical review checked whether option selection edited a pending Bash command, whether cancellation restored it, and which arguments reached documentation probes. Two confirmed findings were fixed in the subsequent [correction and compatibility report](review-fixes-2026-10-23.md). [Development timeline](audit-history.md)

## Evidence and environment

The review used Ubuntu 24.04 under WSL2, Bash 5.2.21, Python 3.12.3 and tmux 3.4 on x86_64, from Git base `797117b1adc052004705850ddd863975e63e7fce`. Disposable homes, installations and repositories isolated the checks.

| Evidence lane | Result | Interpretation |
| --- | --- | --- |
| Initial complete `bash tests/run.sh` | 412 tests; 18 failure outcomes, 154 error outcomes, 1 skip | Includes initial untracked-test defects, fresh-home terminal setup failures, and source changes during packaging checks; not a clean product baseline |
| Complete suite after review additions | 426 tests: 423 passed, 2 expected failures, 1 skip; no failures or errors | Eight preflights passed; full unittest discovery completed in 212.02 seconds |
| Maintained live matrix, four-second source limit | 44 passed, 4 failed, 0 skipped, 1 unsupported | Default harness limit; failures retained |
| Maintained live matrix, fifteen-second source limit | 48 passed, 0 failed, 0 skipped, 1 unsupported | Help/metadata/in-memory insertion evidence at the longer limit |
| Additional live paths at both limits | 5 passed | `grep`, `find`, `tar`, `git rebase`, `docker build` |
| Added composition fixtures | 47 literal before/after scenarios across 44 paths | Exact resolved path, selected flag, final line, and character cursor |
| Added real-terminal cases | 3 passed in focused validation | Multi-value rejection, search/cancel/reopen/insert, Unicode, rendered screen and history |

The initial run included untracked-test defects and packaging checks on changing files. Failure and error counts can include several subtests per method. An interrupted later attempt had no completion summary. The completed run had stable source fingerprints. Its two expected failures were R1 and R2 below. The skip covered the Windows-specific probe.

## Findings ordered by priority

### R1 — P2: source merging can discard a richer required-value count

A controlled help declaration gave `--pair` one required value. The manual gave it two. Source merging retained the first count and allowed a new option where the second value belonged. The review reproduced the conflict with a fixture. The live matrix did not identify an installed program exhibiting this particular conflict. [Metadata regression](../tests/test_review_workflows.py)

### R2 — P2: shrinking wrapped input can duplicate prompt rows

After shrinking a wrapped `rsync` command from 100×24 to 60×16 and reopening the menu, Bash 5.2.21 and tmux 3.4 displayed duplicate prompt rows. Ctrl-L restored the display. Buffer preservation and nonexecution had their own assertions. Ordinary Bash resize controls also exhibited similar behavior. [Rendered-screen regression](../tests/test_terminal_screen.py) · [Investigation](development.md#rendered-screen-regressions)

## Compatibility and environment limits

- The four-second live failures were Docker run, Compose up, Terraform plan and OpenTofu plan. All passed at fifteen seconds. Compose still exceeded four seconds in a repeat. The browser retained its two-second default.
- GNU find 4.9.0 exposed `-name`, `-type` and `-maxdepth`, but its lowercase manual placeholders could lose required-value metadata. The examples established literal editing only.
- Ten requested paths lacked adapters. The follow-up added GitHub PR view/create, Cargo test, Compose logs/exec, kubectl describe/logs, Helm upgrade, AWS S3 sync and rclone sync.
- Pipelines, redirects, substitutions, aliases, shell wrappers and incomplete quotes were outside the reviewed simple-command syntax. The npm 9.2.0 root supplied usage only. Subcommands were checked separately.

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

The live pass checked fixed requests, sentinel flags, their declared arity and literal insertion. The 47 composition scenarios used independent before/after buffers across 44 paths. For the full per-path version and outcome table, read `git show 1f26c692:docs/functional-review-2026-10-23.md` from the checkout.

## Where the add-on is most useful

The reviewed workflows included nested command paths, quoted or repeated values, Unicode suffixes and edits in the middle of a line. They established the returned text, cursor and probe arguments. Tool-specific workload validity and execution were outside those checks.

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

The ignored directory `tests/reports/functional-review-2026-10-23/` held the baseline, interrupted attempt, completed suite, environment fingerprints, both timed live runs and the per-command coverage matrix. Fresh checkouts retain the regression tests and fixtures. Other terminal emulators and program editions require their own evidence.
