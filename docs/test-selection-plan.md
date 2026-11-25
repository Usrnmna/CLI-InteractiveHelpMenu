# Plan for shorter local test runs

Use repeatable focused commands and the timed full-suite baseline to identify expensive checks. Then reduce measured duplicate work and validate test selection against the full suite. Start with iproute2 and use the yq revisit to test whether selection catches dependencies in shared test modules. [Roadmap](../ROADMAP.md#reducing-test-duration) · [Offline runner](../tests/run_sandbox.py) · [Full suite](../tests/run.sh)

## Phase status and gates

| Phase | Local workflow | Completion criterion |
| --- | --- | --- |
| 1 · Focused edit loop | Available now | Run the named family and shared checks during editing. Full offline verification remains the batch gate. |
| 2 · Timing | Complete | Paired timed and ordinary runs match in discovery order, outcomes, fixture results and exit status on all three targets. |
| 3 · Reduce duplicate work | Complete | Measure candidates independently, compare sharded and unsharded coverage, then verify retained changes against Phase 2 on the complete offline matrix. |
| 4 · Selection | Next · report-only pilot | Start with an explain-only iproute2 and yq pilot. Require agreement with full-run evidence, including the historical yq failure, before enabling selected execution. |
| 5 · Result reuse | Conditional on validated selection and remaining cost | Demonstrate complete invalidation and equivalent outcomes for one bounded group before offering opt-in reuse. |

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

This command exercises the existing iproute2 editor regressions and its four route-inventory tests. Set `target` to a prepared sandbox. For the complete family checks, include the inventory, executable fixtures and four rendered menus listed in the [completed iproute2 verification](iproute2-systemd-openssl-verification.md).

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
tags fixed between waves. The timing runner and its tests are now tracked. Include the local package inputs and environment loaders needed to reproduce this historical comparison.
[Ubuntu package and loaders](ffmpeg-manual-coverage.md#reproducing-the-sandbox-checks) · [Pinned yq executables](yq-eval-manual-coverage.md#reproduction) · [Sandbox setup](development.md#isolated-local-debugging)

```bash
mkdir -p tests/reports/timing
logs=$(mktemp -d tests/reports/timing/reproduce-XXXXXXXX)
run_timing_target() {
    local target=$1 mode=$2 name path
    local -a opts=() packages
    for path in tests/reports/ffmpeg-revisit/suite-env.sh \
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

### Coverage retained by the four candidates

| Check | Work removed | Evidence required from the optimized check |
| --- | --- | --- |
| Simulated route inventory | Construct the default key map once per profile. Repeat the narrow draw once for each encountered combination of wrapped Details and a shifted option window. | Every row still renders at 60×16, 100×24 and 160×32 with the selected row visible. Compare the restored 60×16 frame cell for cell and page through every wrapped Details line for the representative layouts. Exercise search, literal insertion, cursor, modal controls and profile immutability. [Inventory](../tests/test_regression_inventory.py) |
| All-profile insertion | Resolve the identical mid-token line and cursor once per profile. | Each of 4,603 option insertions still checks the literal, Unicode suffix, resulting cursor and original line and cursor. The independent inventory uses different whitespace and a different partial token. Dedicated editing cases exercise missing, attached and positional values and the child-command boundary. [Insertion](../tests/test_functional_matrix.py) · [Argument boundaries](../tests/test_invocation_expansion.py) |
| Numerical diagnostics | Evaluate the inventory already built in the diagnostic class fixture. | All 13 diagnostic cases retain the same inputs and offline tripwires. Public CLI calls, independent census and mutation tests each build a fresh inventory. [Diagnostic tests](../tests/test_numerical_diagnostics.py) · [Coverage gate](../scripts/check_numerical_coverage.py) |
| Fixed-size tmux walks | Read visible pane cells in one tmux call per poll and retry an incomplete redraw after 5 ms. | Require a matching selected label, summary, complete wrapped Details in order and exact progress in one frame. The retained syntax walks use a 220-column pane. Git keeps its original full capture after the 240-column trial regressed on Python 3.10. Stable-frame polling still checks cursor, alternate screen and history during open, resize, cancellation and editing. [Git walks](../tests/test_git_stash_worktree_menus.py) · [Syntax walks](../tests/test_syntax_terminal.py) · [Capture and partial-frame controls](../tests/test_terminal_screen.py) |

### Measurements and reproduction

The pre-change checkout was `6574ffa`. The Phase 2 manifest matched every original test, runtime and packaged input by mode and SHA-256. Only this plan had changed. Each focused wave started the three prepared targets together using the Phase 2 package commands. Three successive fresh Python processes per target ran the following groups in order. Each measurement spans unittest setup through cleanup, including class fixtures. It excludes interpreter startup, snapshot creation and package extraction. The full and shard comparisons below use external wall time including setup.

Use the Phase 2 command for the chosen target, keep its fixture wrapper and `YQ_TEST_BINDIR`, and replace the final `bash tests/run.sh` with the following command for an individual focused check. The local evidence driver also counted calls to the private shell's tmux method and retained the route inventory records and bundled row counts.

```bash
env PYTHONPATH=tests python3 -m unittest -v "$case"
```

| Group | Value of `case` |
| --- | --- |
| Inventory · large | `test_regression_inventory.InventoryRegressionTests.test_path_164_ffmpeg` |
| Inventory · small | `test_regression_inventory.InventoryRegressionTests.test_path_020_bun_run` |
| Insertion | `test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline` |
| Numerical diagnostics | `test_numerical_diagnostics.NumericalDiagnosticTests` |
| tmux · FFmpeg | `test_syntax_terminal.SyntaxScreenTests.test_ffmpeg_all_rows_and_complete_details` |
| tmux · Git | `test_git_stash_worktree_menus.GitMenuTests.test_log_rows_and_details` |

The FFmpeg route inventories covered 1,759 bundled rows plus 4 and 10 captured rows. The bun run inventories covered 8 bundled rows plus 8 and 103 captured rows. Coverage comparisons use the full per-source records. Before/after CLI output was byte-identical in strict and prospective modes. Each clean report had 70 diagnostics and exit 0. Changing one review fingerprint in a disposable copy produced 71 diagnostics, including the expected `review_stale`, and exit 1. Evaluating the already-built inventory returned the same complete JSON in all four comparisons. The sole refreshed review pin covers the source digest of the checker whose evaluation body was extracted. [Review database](numerical-inventory/review.json)

### Focused results and decisions

Times are seconds in chronological sample order. Spread is maximum minus minimum. Each group exercises one candidate. The fixed-pane candidate includes both the pane-only read and the shorter retry interval, so its measurements cover those two changes together.

| Check | Target | Before samples (s) | After samples (s) | Median before → after (s) | Spread before / after (s) | Saved (s) |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Inventory · FFmpeg | `host` | 12.321, 12.433, 11.972 | 10.657, 10.215, 10.659 | 12.321 → 10.657 | 0.461 / 0.444 | 1.664 |
| Inventory · FFmpeg | `noble310` | 22.709, 22.377, 22.585 | 19.713, 19.397, 19.282 | 22.585 → 19.397 | 0.333 / 0.431 | 3.188 |
| Inventory · FFmpeg | `noble312` | 12.657, 12.340, 12.381 | 10.798, 10.604, 10.893 | 12.381 → 10.798 | 0.317 / 0.289 | 1.584 |
| Inventory · bun run | `host` | 0.547, 0.567, 0.540 | 0.478, 0.447, 0.462 | 0.547 → 0.462 | 0.027 / 0.031 | 0.086 |
| Inventory · bun run | `noble310` | 1.043, 1.097, 1.048 | 0.901, 0.903, 0.896 | 1.048 → 0.901 | 0.053 / 0.006 | 0.147 |
| Inventory · bun run | `noble312` | 0.557, 0.556, 0.573 | 0.479, 0.453, 0.456 | 0.557 → 0.456 | 0.017 / 0.026 | 0.102 |
| Insertion · all rows | `host` | 0.954, 0.938, 0.970 | 0.119, 0.115, 0.117 | 0.954 → 0.117 | 0.032 / 0.004 | 0.837 |
| Insertion · all rows | `noble310` | 1.449, 1.509, 1.425 | 0.217, 0.214, 0.212 | 1.449 → 0.214 | 0.084 / 0.005 | 1.235 |
| Insertion · all rows | `noble312` | 0.977, 0.944, 0.940 | 0.123, 0.120, 0.127 | 0.944 → 0.123 | 0.037 / 0.007 | 0.822 |
| Numerical diagnostics | `host` | 9.291, 8.954, 9.114 | 5.820, 5.742, 5.821 | 9.114 → 5.820 | 0.337 / 0.078 | 3.294 |
| Numerical diagnostics | `noble310` | 14.472, 14.527, 14.221 | 9.204, 9.311, 9.159 | 14.472 → 9.204 | 0.306 / 0.151 | 5.269 |
| Numerical diagnostics | `noble312` | 9.857, 9.606, 9.616 | 6.184, 6.126, 6.128 | 9.616 → 6.128 | 0.251 / 0.059 | 3.488 |
| tmux · FFmpeg | `host` | 34.969, 31.743, 28.079 | 24.818, 24.590, 25.175 | 31.743 → 24.818 | 6.890 / 0.585 | 6.925 |
| tmux · FFmpeg | `noble310` | 70.764, 68.207, 69.228 | 30.230, 30.744, 30.216 | 69.228 → 30.230 | 2.557 / 0.528 | 38.998 |
| tmux · FFmpeg | `noble312` | 48.937, 49.242, 49.242 | 23.537, 23.496, 24.128 | 49.242 → 23.537 | 0.305 / 0.632 | 25.704 |
| tmux · Git log | `host` | 3.747, 3.734, 3.732 | 3.166, 3.163, 3.084 | 3.734 → 3.163 | 0.015 / 0.082 | 0.570 |
| tmux · Git log | `noble310` | 3.528, 3.719, 3.563 | 4.406, 4.512, 4.372 | 3.563 → 4.406 | 0.191 / 0.140 | -0.843 |
| tmux · Git log | `noble312` | 3.322, 3.391, 3.332 | 3.145, 2.976, 2.929 | 3.332 → 2.976 | 0.069 / 0.216 | 0.356 |

Retain the simulated inventory, insertion and numerical changes on all three targets. Retain pane-only polling for the syntax-family walks. Median total tmux invocations for FFmpeg fell from 6,146 to 5,037 on `host`, 8,414 to 5,957 on `noble310` and 7,290 to 5,174 on `noble312`. These totals include navigation, session setup and teardown. The fixed-pane loop may take more pane samples while waiting for a redraw.

Defer changing Git's capture path. Git log used fewer calls (777 → 544, 785 → 724 and 775 → 558 respectively), but on Python 3.10 the median grew by 0.843 s, outside the observed ranges. The Git column above measures the trial, which was removed before full verification. The separate timeout control rejects six kinds of incomplete frames, accepts the corrected retry and terminates when the deadline expires.

### Full offline verification

All three timed runs used the Phase 2 commands and packaged fixtures with the same three-target concurrency. The 659 inputs common to all three snapshots matched by SHA-256 and mode. Per-target input manifests also matched the original fixture bytes. The runs include the retained changes and the restored Git walker.

| Target | Ubuntu / Python | Phase 2 timed wall | Phase 3 timed wall | Observed reduction | Pass / fail / skip | Exit |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `host` | 26.04.1 / 3.14.4 | 1082.960 s | 1073.079 s | 9.881 s | 1530 / 0 / 1 | 0 |
| `noble310` | 24.04.5 / 3.10.20 | 1279.566 s | 1218.491 s | 61.075 s | 1530 / 0 / 1 | 0 |
| `noble312` | 24.04.5 / 3.12.3 | 1118.817 s | 1084.046 s | 34.771 s | 1530 / 0 / 1 | 0 |

Ordered discovery IDs matched execution and verbose console results. Removing only the new passing `test_terminal_screen.FixedFrameTests.test_partial_row_retries_and_times_out` yielded all 1,530 Phase 2 IDs in their original order with identical outcomes. The Windows probe test still skipped with reason “POSIX hosts complete the probe normally”. There were no fixture-level skips or errors. The focused checks also visited all four representative narrow layouts on each target. The 76 profiles still exercised 4,603 bundled insertion rows.

For context, individual test durations within the full waves were as follows (Phase 2 → Phase 3, seconds). The single full-wave difference includes machine variation. In particular, the historical host FFmpeg walk was already close to the new time. Numerical class setup is outside individual case timings and is measured in the focused table.

| Target | Simulated FFmpeg | Simulated bun run | All-profile insertion | FFmpeg terminal | Git log terminal (original) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `host` | 12.26 → 10.17 | 0.56 → 0.45 | 0.94 → 0.11 | 24.50 → 24.24 | 3.71 → 3.79 |
| `noble310` | 22.85 → 19.81 | 1.07 → 0.92 | 1.43 → 0.18 | 69.98 → 29.14 | 3.59 → 3.53 |
| `noble312` | 12.38 → 10.51 | 0.56 → 0.45 | 0.96 → 0.12 | 48.57 → 23.24 | 3.40 → 3.43 |

The ignored local evidence directory is `tests/reports/timing/phase3/`. The exact benchmark commands are in `before-*.command` and `after-*.command`. The fixture wrapper runs `bench.py` three times with the same case order and tmux instrumentation. Set `CLI_HELP_TEST_TIMING=1` when replaying recorded commands. Each corresponding log points to its raw JSONL file. The per-sample counters, per-source inventories and aggregate results are in the logs and `focus.json`. The full invocations, manifests and ordered comparison are in `full-*.command`, `full-inputs-*.json` and `full-parity.json`. The original Phase 2 evidence remains under `baseline-2026-11-23/`.

### Two-shard host pilot

Keep two-way module sharding as a measured local option for this prepared host. The standard three-target full run remains the audit gate. The single pilot establishes the observed wall time and outcome parity for this machine. Reliability across repeated runs, other targets and higher shard counts remains unmeasured.

The pilot used the 91 module totals from the retained `host` full run. Assigning the next longest module to the lighter shard kept class and module fixtures together and predicted 527.084 s and 527.085 s of in-case time. Both shards ran full discovery and retained discovery order within their assigned modules. Each sandbox had its own scratch filesystem, temporary home, packaged fixtures and private tmux sockets. Each ran shell syntax, numerical coverage and both collection checks before unittest.

| Ubuntu 26.04.1 / Python 3.14.4 | Wall (s) | IDs | Pass / fail / skip | Exit |
| --- | ---: | ---: | ---: | ---: |
| Unsharded control | 1045.234 | 1531 | 1530 / 0 / 1 | 0 |
| Shard 1 | 527.026 | 550 | 549 / 0 / 1 | 0 |
| Shard 2 | 536.472 | 981 | 981 / 0 / 0 | 0 |
| Parallel pair, first launch to last exit | 536.473 | 1531 | 1530 / 0 / 1 | 0 |

The pair finished 508.761 s sooner (48.7%). Both sides started together on disjoint four-core sets in the same NUMA node. The control used CPUs 8–11 and both shards shared CPUs 12–15. Separate last-level caches and equal physical-core budgets limited contention, although all processes shared memory and host load. The timings include snapshot creation, startup, extraction, fixture setup, repeated preflight and cleanup. Archive extraction took 0.058 s in each instance. Preflight took 6.265 s for the control and 6.410 / 6.409 s for the shards.

The shard ID sets were disjoint, their union equalled full discovery, and every ID retained its original outcome and skip reason. Each shard matched the control order restricted to its IDs. All three transcripts agreed with the timing events, with zero fixture-level outcomes. The control also matched the unsharded host run from the full matrix.

For a local replay, use the retained `balance.py` on the timed `full-host.log`, then `wave.py solo shard0 shard1`. The exact sandbox invocations are recorded in `solo-host.command`, `shard0-host.command` and `shard1-host.command`. All include the same pilot files with `--include`. The temporary shard entry point changes only the final unittest invocation in a snapshot-local copy of the preflight script. `shards.json` records module membership and `pilot-parity.json` records the combined comparison. Preserve the earlier results when replaying.

## 4. Add explicit selection for local audits

The next runnable task is the report-only selector and its full-run comparisons for iproute2 and yq. Add an opt-in `--suite impacted --base REF --explain` to `tests/run_sandbox.py` as a report-only pilot. Use `tests/test-impact.json` for explicit group inputs, test IDs, command paths and fixture requirements. Reuse the existing command inventory as the source for generated route cases. Its method names contain a sorted index that can shift when another route is added, so resolve cases by command at discovery time. A missing test ID or unexpectedly empty group triggers full-suite fallback. An explicit `--suite impacted --base REF` can run the printed selection after pilot validation. Keep the existing default and `--` custom command path. [Generated route cases](../tests/test_regression_inventory.py) · [Sandbox runner](../tests/run_sandbox.py)

| Input changed | Required selection |
| --- | --- |
| `profiles/ip-address.json`, `ip-link.json`, `ip-route.json` or `ss.json` | Shared collection and numerical preflight, four route cases, the iproute2 family inventory and menu checks, plus the applicable shared insertion and syntax checks. Resolve the family-specific checks from the completed iproute2 audit. |
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
