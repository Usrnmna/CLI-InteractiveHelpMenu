# Plan for shorter local test runs

Start by giving command audits a repeatable focused command and timing the next scheduled full run. Then reduce measured duplicate work and validate test selection against the full suite. Start with iproute2 and use the yq revisit to test whether selection catches dependencies in shared test modules. [Roadmap](../ROADMAP.md#reducing-test-duration) · [Offline runner](../tests/run_sandbox.py) · [Full suite](../tests/run.sh)

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

| File | Proposed change |
| --- | --- |
| [tests/run.sh](../tests/run.sh) | Add opt-in `CLI_HELP_TEST_TIMING=1` to call a standard-library `tests/timed_unittest.py` helper with the existing discovery arguments. Preserve verbose output, fixture behavior, order and exit status. Record shell syntax, numerical gate, both collection checks and unittest separately. |
| `tests/timed_unittest.py` | Use the `TextTestResult` pattern from the review runner with ordinary unittest discovery. Time discovery, each case, and suite overhead outside individual cases. Attach subtest failures to their parent and retain fixture-level skips and errors. Where overhead dominates, time the affected class or module fixtures directly. [Existing review runner](../tests/regression_review.py) |
| [tests/run_sandbox.py](../tests/run_sandbox.py) | Time snapshot creation and sandbox command wall time. Emit in-sandbox extraction and fixture setup durations through explicit report output or marked log lines captured on the host. Keep files and logs under ignored `tests/reports/` or a private temporary directory. Record target, actual runtime versions, fixture identities, first failure and completion state. |

Use a monotonic clock. Run timing on the next required full matrix and retain per-target reports. Compare before and after on the same target, with the same fixture set and the same concurrency. Report median of three focused measurements. For full suites report each observed wall time and aggregate by module and class. The timing path passes when it produces the same test IDs, skip reasons and outcomes as normal discovery, and preserves nonzero exit status on a preflight failure and a failing subtest. [Current fixture setup examples](ffmpeg-manual-coverage.md#reproducing-the-sandbox-checks)

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
