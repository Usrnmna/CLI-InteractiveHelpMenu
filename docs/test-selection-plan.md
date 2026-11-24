# Plan for shorter local test runs

Use repeatable focused commands and the timed full-suite baseline to identify expensive checks. Then reduce measured duplicate work and validate test selection against the full suite. Start with iproute2 and use the yq revisit to test whether selection catches dependencies in shared test modules. [Roadmap](../ROADMAP.md#reducing-test-duration) · [Offline runner](../tests/run_sandbox.py) · [Full suite](../tests/run.sh)

## Baseline

| Local target | Focused yq checks | Full suite | Full result |
| --- | ---: | ---: | --- |
| Ubuntu 26.04.1, Python 3.14.4 | 26.8 s | 17m 59s | 1,524 passed, one platform skip |
| Ubuntu 24.04.5, Python 3.10.20 | 34.6 s | 20m 58s | 1,524 passed, one platform skip |
| Ubuntu 24.04.5, Python 3.12.3 | 27.4 s | 18m 26s | 1,524 passed, one platform skip |

The 21 focused checks covered the yq audit. These unittest times came from concurrent local runs and exclude sandbox startup, package extraction and suite preflight. The first full runs caught a test in `test_system_dependency_followup.py` that assumed the 4.54.1 help capture covered every current yq spelling. Searching for test filenames containing `yq` would have missed it. The final focused set includes that test. [Yq verification](yq-eval-manual-coverage.md#compatibility-results) · [Historical capture check](../tests/test_system_dependency_followup.py)

A spot check on Ubuntu 26.04.1 with Python 3.14.4 timed the FFmpeg Bash/tmux walk at 33.5 s, its simulated route inventory at 12.5 s, and the strict numerical gate at 5.7 s. The six existing iproute2 checks below passed in 4.0 s of unittest time across two invocations. These single samples identify candidates and give the pilot a starting point. Use the timed full suite to rank the complete set.

## 1. Shorten the edit loop with the current runner

Run a focused check on `host` during an edit. When the batch is ready for rendered verification, run the same family checks on `host`, `noble310` and `noble312` before the required full runs. Run the strict numerical gate after a reviewed change to profile facts or fingerprints. During development, continue to include each required untracked test, fixture and audit file with a separate `--include`. [Sandbox instructions](development.md#isolated-local-debugging) · [Batch verification](../ROADMAP.md#how-to-audit-a-batch)

This command exercises the existing iproute2 editor regressions and its four route-inventory tests. Set `target` to a prepared sandbox. As the revisit adds tests, append its inventory, real-client fixtures and four menu checks to the family selection.

```bash
target=host
python3 -I tests/run_sandbox.py --target "$target" -- bash -ec '
    PYTHONPATH=tests python3 -m unittest -v \
      test_expansion_systems.SystemsExpansionTests.test_ip_keywords_are_literal_arguments_and_values_are_not_keywords \
      test_expansion_terminal.ExpansionScreenTests.test_ip_route_prefix_modifiers_at_minimum_size
    python3 -m unittest discover -s tests -p test_regression_inventory.py -v \
      -k "*.test_path_*_ip_address" -k "*.test_path_*_ip_link" \
      -k "*.test_path_*_ip_route" -k "*.test_path_*_ss"
'
```

## 2. Time the actual full suite

Set `CLI_HELP_TEST_TIMING=1` when invoking the local sandbox runner or
`bash tests/run.sh`. The runner prints the location of a new
`events.jsonl` under ignored `tests/reports/timing/`. Redirect the command's
output to an ignored log to retain the normal verbose transcript.
[Suite entry point](../tests/run.sh) · [Timing runner](../tests/timed_unittest.py) · [Sandbox runner](../tests/run_sandbox.py)

Each event carries a monotonic timestamp. The sandbox records snapshot
creation, backend launch and archive extraction. The interval from
`extraction-end` to `suite-start` covers the fixture wrapper and the suite
launch. Standalone suite runs start at `suite-start`. The shell records
syntax, numerical review, both collection checks and the unittest phase.
Unittest records discovery, ordered IDs, case durations and outcomes. A
fixture callback outside a case has its own outcome record. The remaining
unittest time includes class and module fixtures, reporting and runner
overhead. The interval from the applicable start event to `first-failure`
gives time to the first reported failure. For failed subtests, this reflects
when that interpreter reports the failure to the result object.

A full sandbox report has a `sandbox-end` exit code and a `suite-end` exit
code. Missing end events identify interrupted runs or phases that could
not report. A preflight failure has a `suite-end` event naming the failed
phase and no discovery events. Reports use the sandbox's stdout stream
to return records while leaving unittest's verbose stderr stream in place.
When stdout goes to a terminal, timed sandbox stdout is relayed through a
pipe and forwarded by line.

### Reproduce the paired offline baseline

Use the prepared `noble310` and `noble312` images and the package loaders
used by the preceding audits. Keep the checkout, fixture bytes and image
tags fixed between waves. Include the two new Python files until they are
tracked, along with any required untracked project inputs.
[Ubuntu package and loaders](ffmpeg-manual-coverage.md#reproducing-the-sandbox-checks) · [Pinned yq executables](yq-eval-manual-coverage.md#reproduction) · [Sandbox setup](development.md#isolated-local-debugging)

```bash
mkdir -p tests/reports/timing
logs=$(mktemp -d tests/reports/timing/reproduce-XXXXXXXX)
run_timing_target() {
    local target=$1 mode=$2 name path
    local -a opts=() packages
    for path in tests/{timed_unittest,test_timed_unittest}.py \
        tests/reports/ffmpeg-revisit/suite-env.sh \
        tests/reports/fzf-revisit/env.sh \
        tests/reports/yq-revisit/yq-{4.44.3,4.54.3}; do
        opts+=(--include "$path")
    done
    if [[ $target == host ]]; then
        packages=(0.67.0-1.deb 10.3.0-2ubuntu1.deb openssh-resolute-server.deb)
    else
        packages=(0.44.1-1ubuntu0.3.deb 9.0.0-1.deb openssh-noble-debs.tar openssh-revisit-rsync.tar)
        opts+=(--include tests/reports/ffmpeg-revisit/noble-runtime.tar.gz)
    fi
    for name in "${packages[@]}"; do
        opts+=(--include "tests/reports/fzf-revisit/$name")
    done
    CLI_HELP_TEST_TIMING=$mode python3 -I -c '
import subprocess, sys, time
with open(sys.argv[1], "wb") as log:
    start = time.monotonic()
    status = subprocess.run(sys.argv[2:], stdout=log, stderr=subprocess.STDOUT).returncode
    print(f"{time.monotonic() - start:.3f} seconds, exit {status}")
sys.exit(status)
' "$logs/$target-$mode.log" python3 -I tests/run_sandbox.py --target "$target" "${opts[@]}" -- \
        bash tests/reports/ffmpeg-revisit/suite-env.sh \
        env YQ_TEST_BINDIR=tests/reports/yq-revisit bash tests/run.sh
}

result=0
for mode in 0 1; do
    pids=()
    for target in host noble310 noble312; do
        run_timing_target "$target" "$mode" > "$logs/$target-$mode.wall" &
        pids+=("$!")
    done
    for pid in "${pids[@]}"; do wait "$pid" || result=1; done
done
printf 'Matrix exit %s. Logs in %s\n' "$result" "$logs"
```

For the controlled cases, run the following on each target. These tests
create disposable suites that cover normal and timed output, an ordinary
skip, fixture skips and errors, failing and skipped subtests, and a
preflight that exits 37 before importing tests. They also check empty-suite
exit behavior and report directory creation failure.
[Controlled cases](../tests/test_timed_unittest.py)

```bash
python3 -I tests/run_sandbox.py --target "${target:-host}" \
    --include tests/timed_unittest.py --include tests/test_timed_unittest.py -- \
    python3 -m unittest discover -s tests -p test_timed_unittest.py -v
```

### Paired baseline results

Timing is complete on all three offline targets. The 2026-11-23 baseline
used two waves of three concurrent targets. Source and package fixture
SHA-256 digests and file modes matched across waves.

| Target | Ubuntu | Python | Normal wall | Timed wall | Timed minus normal | Pass / fail / skip in each mode | Exit in each mode |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 1082.630 s | 1082.960 s | +0.330 s | 1529 / 0 / 1 | 0 |
| `noble310` | 24.04.5 | 3.10.20 | 1281.590 s | 1279.566 s | −2.024 s | 1529 / 0 / 1 | 0 |
| `noble312` | 24.04.5 | 3.12.3 | 1119.544 s | 1118.817 s | −0.727 s | 1529 / 0 / 1 | 0 |

All 1,530 timed discovery IDs matched the normal console test list in
order. The timed console and JSONL records also matched every normal
outcome. The sole skip was the Windows-specific probe limitation, with
the same reason in both modes. The full runs had zero fixture-level skips
or errors. The wall-time deltas include ordinary run-to-run variation.
Their magnitude was below 0.2% on each target.

| Timed target | Snapshot | Backend startup | Extraction | Packaged fixtures and suite launch | Preflight | Discovery | Inside cases | Unittest outside cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `host` | 0.101 s | 0.025 s | 0.057 s | 0.083 s | 6.47 s | 0.63 s | 1061.11 s | 13.70 s |
| `noble310` | 0.199 s | 0.145 s | 0.177 s | 2.292 s | 10.13 s | 0.81 s | 1244.39 s | 20.60 s |
| `noble312` | 0.198 s | 0.159 s | 0.177 s | 2.277 s | 6.75 s | 0.70 s | 1093.07 s | 14.74 s |

The stage table omits the short intervals between checkpoints, including
the sandbox's version checks and launcher cleanup. The full wall times
include these intervals. The three longest modules correspond to the
three longest classes on each target.

| Target | Longest module/class totals | Slowest individual case |
| --- | --- | --- |
| `host` | `SyntaxScreenTests` 122.77 s, `PodmanRunMenuTests` 113.78 s, `ExpansionScreenTests` 95.41 s | rsync all-row summaries and Details, 51.73 s |
| `noble310` | `SyntaxScreenTests` 175.02 s, `PodmanRunMenuTests` 115.26 s, `ExpansionScreenTests` 97.62 s | numerical integration across opted-in profiles, 82.88 s |
| `noble312` | `SyntaxScreenTests` 143.73 s, `PodmanRunMenuTests` 111.27 s, `ExpansionScreenTests` 93.32 s | numerical integration across opted-in profiles, 58.37 s |

The five controlled regressions passed on each target. Separate disposable
probes preserved exit 143 after interrupting a test and identified the
unfinished case. Both modes also preserved exit 1 when the timing stream
was directed to `/dev/full`. The first matrix stopped at the numerical gate
with exit 1 in both modes. The gate flagged the protected source digest
for `tests/run.sh`, which was refreshed after reviewing the timing diff.
The strict numerical gate then passed all 3,123 required contracts.
[Reviewed source digest](numerical-inventory/review.json)

The six logs, exact invocations, input manifests, comparison, and initial
preflight failure logs are local to
`tests/reports/timing/baseline-2026-11-23/`. The timed log for each target
records the location of its associated raw `events.jsonl`.

## 3. Make the complete checks cheaper

Apply these changes independently and retain the ones with measured savings.

1. **Simulated inventory.** In `InventoryRegressionTests.exercise_profile`, construct the default key map once per profile and reuse it. It is currently reconstructed for every draw. Each row draws at 60×16, 100×24, 160×32 and again at 60×16. Keep the first three for every row. Exercise the return to 60×16 once per representative layout, including a wrapped Details case and a change in the visible option window. Assert selected-row visibility and Details after returning to the original size. Compare the FFmpeg route and a small profile before and after, including search, option selection and untouched profile assertions. [Simulated inventory](../tests/test_regression_inventory.py) · [Key loader](../cli_help/ui.py) · [Existing resize tests](../tests/test_terminal_screen.py)
2. **All-profile insertion.** In `InsertionContractTests.test_every_bundled_option_inserts_exactly_midline`, resolve the context once per profile for its identical pending line and cursor. Continue to call insertion and assert the literal, cursor and original context for each option. Keep its distinct whitespace and partial-token case. The simulated inventory already uses one context per profile. Compare exact row counts and retain separate missing-value, attached-value and positional-boundary tests. [Insertion matrix](../tests/test_functional_matrix.py) · [Argument editing tests](../tests/test_invocation_expansion.py)
3. **Numerical diagnostics.** `NumericalDiagnosticTests.setUpClass` builds the inventory directly and `check_coverage` builds it again from the same root and reviews. Split the checker into inventory construction and a private evaluation step, and pass the freshly built report to that step in this class. Keep the public CLI building its own inventory. Leave synthetic, mutating and independent census tests on fresh input. Compare complete reports in both modes, including stale fingerprints, diagnostics and exit codes. [Numerical diagnostics](../tests/test_numerical_diagnostics.py) · [Numerical gate](../scripts/check_numerical_coverage.py)
4. **Real terminal capture.** If the timed FFmpeg or Git walks dominate, instrument tmux subprocess counts. In the all-row helper compare a candidate pane-only capture for fixed-size frames with the existing capture of metadata and history on every poll. Keep exact selected label, summary, and complete Details comparisons. Keep the stronger stable-frame and cursor checks for resize, cancellation and editing. Run the walk repeatedly under all three targets and check that partial frames still time out or retry correctly. [All-row terminal checks](../tests/test_syntax_terminal.py) · [Capture implementation](../tests/test_terminal_screen.py)

Test sharding only after measuring these changes. Pilot two duration-balanced shards on one target, with independent temporary state and tmux sockets. Include duplicate setup and extraction in the wall time. Keep sharding only if it improves total time at the same fixture coverage and does not increase failures under concurrent runs.

## 4. Add explicit selection for local audits

Add an opt-in `--suite impacted --base REF --explain` to `tests/run_sandbox.py` as a report-only pilot. Use `tests/test-impact.json` for explicit group inputs, test IDs, command paths and fixture requirements. Reuse the existing command inventory as the source for generated route cases. Its method names contain a sorted index that can shift when another route is added, so resolve cases by command at discovery time. A missing test ID or unexpectedly empty group triggers full-suite fallback. An explicit `--suite impacted --base REF` can run the printed selection after pilot validation. Keep the existing default and `--` custom command path. [Generated route cases](../tests/test_regression_inventory.py) · [Sandbox runner](../tests/run_sandbox.py)

| Input changed | Required selection |
| --- | --- |
| `profiles/ip-address.json`, `ip-link.json`, `ip-route.json` or `ss.json` | Shared collection and numerical preflight, four route cases, the iproute2 family inventory and menu checks, plus the applicable shared insertion and syntax checks. Add those family-specific tests as the revisit introduces them. |
| `config/drivers.example/ip.json`, `ss.json` or a mapped iproute2 help capture | Include the same family, route resolution, fixed discovery arguments, and keyword and positional boundaries. Include the packaged fixture checks when changes affect evidenced client behavior. |
| A yq profile, capture or route | Include `test_yq_manual_inventory`, the yq menu and editing cases, and `SystemDependencyFollowupTests.test_installed_leaf_help_provenance_and_curated_flags`. Include pinned-client tests when syntax or executable behavior changes. |
| Markdown | Check links, heading fragments and inbound links to renamed targets. If a file supplies test data, run the consuming test. For example, the system dependency test reads option tables from the Podman audit. If a release package includes the Markdown, its archive verification belongs in the affected set as well. |
| Review database, shared fixture manifests or archive inputs | Always run the owning repository-wide gate. Map additional consumers explicitly. For a named group that reads shared data, include those inputs even when its command-specific profile is the only file edited. |
| Parser, profile schema, common presentation, shell binding, sandbox setup, or an unmapped source or test | Run full verification for all affected targets. For a change with unknown reach, use the complete matrix. |

Compute candidates against the supplied base using the files that enter the snapshot. Include staged and unstaged content, both paths of renames, deletions and new files supplied by `--include`. Report unresolved untracked project inputs and require them in the snapshot before claiming verification. Use the same manifest and bytes for selection and execution. Always show each selected ID, the input that triggered it, expected fixture availability and any full-suite fallback. [Snapshot implementation](../tests/run_sandbox.py) · [Cross-family fixture test](../tests/test_system_dependency_followup.py) · [Package tests](../tests/test_release_snapshot.py)

Compare the report against normal full runs with changes confined to a family profile, help capture, audit table, shared harness, added file, deleted file and unavailable fixture. Replay the historical yq failure in a disposable snapshot. The selector must include the failing test. Confirm that an iproute2-only profile edit excludes the FFmpeg all-row walk from the focused loop, while a shared display change includes it. Require the expected test IDs to appear and fail the pilot if a full run finds a failure outside the planned set.

## 5. Reuse green results only after selection works

Start with explicit focused and full commands. Add persistent reuse later if measurements show that affected groups still take enough time to justify it. Pilot one group with bounded inputs, such as a family’s all-row walk on a pinned Noble image. Record a digest of input paths, contents and modes, discovered test IDs, selector version, test invocation, target image ID, runtime versions, relevant environment and fixture hashes. For host reuse, require an equivalent identity for the installed tools and libraries the group exercises. Otherwise execute the host group. Write completed group results atomically. A failed or incomplete attempt or a missing required fixture forces execution. Treat expected platform skips as skips and report their reasons. A cache hit reports the source run and date as reused evidence.

Validate content, path, test, binary, target and environment changes independently. Interrupt a run and check that it creates no new reusable result. A previously completed group may remain eligible only if its current identity still matches and no later attempt invalidated it. Keep reuse opt-in. Compare executed, reused, skipped and failed counts with their full-run counterparts. Retain one-command full runs for final audit verification under the current roadmap, broad changes, releases, and explicit user requests. Evaluate CI changes after the local pilot has measured savings and matched the full suite. [Full audit gate](../ROADMAP.md#how-to-audit-a-batch) · [CI matrix](../.github/workflows/ci.yml)
