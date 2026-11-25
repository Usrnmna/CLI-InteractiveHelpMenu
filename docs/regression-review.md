# Regression review: option descriptions and terminal presentation

Historical verification on 2026-10-26 used the source fingerprints in the accompanying JSON snapshot. The review identified and repaired declaration regressions, then repeated the complete applicable suite. This establishes the recorded offline and terminal behavior; it does not establish all possible command grammars, installed-version compatibility, or absence of every defect.

## Results and evidence

- Linux/WSL Python 3.12.3: **1318 tests run, 1316 passed, 0 failures, 0 errors, 2 skips**.
- Windows Python 3.13: **402 portable tests passed**, zero failures/errors/skips. No native Windows Bash/curses acceptance claim.
- Per-path offline audit: **358 tests passed** (also included in the full Linux total; not additive).
- Preflight: **12 checks passed**, covering six Bash syntax checks, bundled and configured-driver validation, inventory reconciliation, strict numerical preservation and exact command/driver listings.
- [Machine-readable coverage and tested-file hashes](regression-coverage.json).
- Local detailed evidence under `tests/reports/current-regression/`: `linux-suite.json` (Linux test outcomes), `linux-suite.log` (Linux log), `windows-portable.log` (Windows log), `inventory.json` (per-path details), and `preflight.json` (preflight). These logs are local ignored artifacts and are absent from fresh checkouts; the matrix and outcome snapshot above are maintained files.

## Inventory and boundaries

Inventory combines both built-in and configured driver routes, all bundled profiles, the primary compatibility matrix, supplemental capture/workflow manifests, and the twelve Python module forms. Capture labels such as Yarn `(classic)`/`(modern)` and Go help topics are attached to their command paths rather than counted as commands. There are 357 named implementation paths plus the captured generic-root `find` case: **358 rows**, including **317 registry routes**, **76 profiles**, **96 categories**, and **942 option/keyword records**. The primary matrix alone has 162 cases and is not the full inventory.

All 942 bundled records were selected and drawn at 60×16, 100×24 and 160×32, with shrink/grow redraws, search, modal navigation, preview/cancel, exact midline insertion, Unicode suffix and cursor assertions. Separate tests cover below-minimum dimensions, long declarations/descriptions, scrolling, absent/malformed guidance, qualifications, warnings, blank results and stale-cell clearing. These exhaustive checks use the documented cell model; representative tmux checks establish actual cells and terminal restoration.

182 paths have bundled or fixture documentation; 176 have routing-only evidence. The 283 fixture variants include seven empty parses. An empty parse records safe processing, not proof that every upstream option was recognized. Missing documentation/rendering evidence is explicitly marked below. Arbitrary executables and user-defined drivers/profiles form an open-ended extension interface; their grammar and rejection boundaries are tested as functions, rather than represented as a finite list of target programs.

Linux environment: Ubuntu 24.04 under WSL2, Python 3.12.3, Bash 5.2.21, tmux 3.4 and GCC 13.3.0. Static GUI checks disable discovery. Inspected process-contract tests use private executable doubles and fixed help/manual arguments; the test named `kubectl_live_fixed_help` runs an instrumented fixture, not installed kubectl. No supported target is executed merely to claim compatibility. Install/update/release checks use disposable homes/prefixes, fake download clients and isolated terminal sockets.

## Fixes and preservation review

The initial complete run had 955 tests, five failures, two errors and two skips. Failures concerned stale preservation review identities and lost sed aliases. Additional inventory comparison exposed pytest choice-set aliases and psql shared-equals/annotated aliases. Four focused parser regressions were established before correction.

- Complete comma-containing operands now remain intact for brace, angle and square placeholders; their following aliases survive.
- Shared `=` declarations preserve psql aliases and literal insertion syntax. Repeated lowercase operands preserve sed `-e`/`--expression=` and `-f`/`--file=`.
- Quoted alias labels are preserved without inventing a required value, and trailing declaration commas no longer become summaries.
- Cache generation is **16**. Old parsed caches become misses through the existing permitted discovery path; imported/curated files are not overwritten.
- The shared terminal sanitizer is included in the protected-source inventory. **109 fingerprints** were reassessed against a disposable pre-fix snapshot (`d97ac6f`); existing classifications, uncertainties, qualifications, exception lists and gate rules were preserved. One false SSH `-KR` observation embedded in prose was removed from the review index; its original captured source remains intact. One sanitizer-source census entry was added.
- No layout redesign, documentation deletion, commit, push or publication was performed.

Package tests exercised the repaired runtime and verification sources before the
final reporting-only Markdown/JSON files and documentation-index link were added.
Those report files were checked separately for local links and evidence integrity.

| Original fix | Confirmed evidence |
|---|---|
| Description preservation | Captured AWS exclusion opening, ambiguous spaces/tabs, aliases, types, multiline text and option-like prose; new alias regressions; AWS rendered description. |
| OPTIONS rows | Every bundled option at three widths; native rsync/ls/grep/tar resize and insertion; complete-or-absent qualified guidance and visible review markers. |
| Opening duplication | Six real captures in model and tmux checks; exact opening rule, blank lines, near matches, merged sources and legitimate later repetitions. |
| Terminal remnants | ESC/C1 CSI and string forms, charset designators, overstrikes, malformed recovery, large inputs, validation rejection and isolated native rendering. |

## Major function coverage

The review mapped configuration, routing, parser associations, presentation, literal editing, cache handling, import, collection review, recovery, update and package tests to their individual assertions. The `functions` list retains each test ID and disposition. [Function and path evidence](regression-coverage.json)

## Lower-priority findings

1. **Search cancellation can retain a changed category.** Open the bundled rsync profile on its first category, type `/zz`, then Escape. Intermediate substring matches can move the category; Escape restores the filter but not the earlier category/selection. This behavior exists before steps 1–4 (`d97ac6f` uses the same search-state handling). Impact: navigation surprise. Recommended follow-up: decide whether cancellation should restore query only or the full selection/focus/scroll state, then add a focused state-snapshot test. No behavior change was made during this review.
2. **Full AWS captures retain later repetitions and example fragments.** Parse `captured.json["aws s3 cp"]["text"]`, select `--exclude`, and inspect its complete details. A generic “Documented option” block and later example/output fragments precede or follow the useful description. This is source-association/merging behavior present in the pre-fix snapshot; it is not an exactly duplicated opening summary. Impact: noisy details and potentially ambiguous inferred argument metadata. Recommended follow-up: separately scope usage/example exclusion and repeated declaration precedence against unchanged captures. Do not broaden deduplication to delete arbitrary repeated text.
3. **Malformed terminal string payloads may remain literal.** Unterminated OSC/DCS-style input retains ambiguous payload through conservative recovery. This is an intentional preservation limit, not an unhandled terminal control. A stricter policy requires evidence that the residual payload is safe to discard.

## Skips and remaining gaps

- `test_bash_pty.BashIntegrationTests.test_select_inserts_without_executing_then_normal_enter_executes`: **skip** — Task safety: this test explicitly executes its pending sentinel command; passive insertion is covered separately.
- `test_functional_matrix.EdgeCaseTests.test_probe_reports_the_windows_limitation`: **skip** — POSIX hosts complete the probe normally
- The Windows-only process-limitation assertion was run successfully in the separate Windows checks. The deliberately executing sentinel test remains skipped; passive insertion and pending-state assertions passed elsewhere. No pending command was submitted to close this gap.
- **176 routing-only paths:** provide reviewed help/manual fixtures with independent flag/arity sentinels, then run the per-path audit to add documentation and rendering evidence.
- **Live upstream versions:** not tested. Controlled fixtures cannot establish installed-version compatibility. Closing this gap requires a separately authorized, isolated fixed-help/manual campaign, never pending command execution.
- **Platforms:** Python 3.10, standalone non-WSL Linux, macOS, other architectures/terminal emulators and native Windows Bash/curses were not verified in this run. Repeat the offline gate on those supported environments; use representative native terminal checks where available. Historical hosted results are not substituted for current results.
- **Display limits:** ambiguous-width emoji/grapheme behavior, accessibility and every terminal/Readline release remain unverified. Add representative captures and target-terminal acceptance checks for those requirements.
- **Release delivery:** local candidate compilation, checksums, extraction, install/update/uninstall, historical upgrade and mocked GitHub retrieval were tested. Actual network downloads, hosted CI and publication were not performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/regression_review.py
PYTHONPATH=tests python3 -B -m unittest test_regression_inventory test_display_regression_terminal -v
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
```

The review runner applies the explicit pending-execution skip and static-GUI harness settings. It otherwise discovers the complete `test_*.py` suite. The raw first-run failures, focused red/green logs and fingerprint reconciliation remain in `tests/reports/current-regression/`.

## Command-path matrix

The `commands` list holds 358 per-path records with routing results, bundled category and option counts, fixture provenance, native terminal mappings and test identifiers. Of these, 182 paths had bundled or fixture documentation. The other 176 had routing evidence alone. The October review used controlled inputs. Installed upstream versions were outside that run. [Per-path matrix](regression-coverage.json)

## Suite module totals

The `module_results` object gives outcomes for all 65 Linux test modules. The `skips` list identifies the two skipped tests. The Linux, Windows and preflight summaries identify which checks ran on each platform. [Recorded outcomes](regression-coverage.json)
