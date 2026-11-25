# Serial prose reuse during menu opening

**Defer production adoption of this cache.** Exact-string reuse saved about 26–28 ms per matched FFmpeg open. All six large-menu cases improved at p95. The median improvement of 4.4–5.4% fell below the project's proposed 30% target. The three-row Git worktree remove menu showed little change. [Comparison criteria](ffmpeg-menu-performance-plan.md#before-and-after-measurement)

## Time to the first complete frame

Each row represents 40 alternating pairs after one discarded warm-up per variant. A private interactive Bash shell launched a fresh helper for each Alt-H. The timer stopped when the decoded terminal cells matched the complete **baseline** screen. The percentage compares the two medians. The last column takes the median of the 40 within-pair differences. These statistics can differ even in sign when the effect is small.

| Terminal | Menu | Baseline median / p95 (ms) | Reuse median / p95 (ms) | Median reduction | Median paired saving (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| 80×24 | FFmpeg | 546.2 / 554.8 | 518.8 / 531.8 | +5.0% | +27.8 |
| 80×24 | FFmpeg `-map` | 547.1 / 562.0 | 521.2 / 534.6 | +4.7% | +26.3 |
| 80×24 | FFmpeg `-rw_timeout` | 568.5 / 591.9 | 537.7 / 557.4 | +5.4% | +27.6 |
| 80×24 | Git worktree remove | 223.6 / 228.5 | 223.5 / 229.4 | +0.0% | -0.5 |
| 60×16 | FFmpeg | 554.5 / 566.4 | 530.1 / 546.0 | +4.4% | +26.2 |
| 60×16 | FFmpeg `-map` | 548.9 / 559.7 | 519.9 / 536.0 | +5.3% | +27.9 |
| 60×16 | FFmpeg `-rw_timeout` | 545.8 / 554.2 | 519.6 / 527.1 | +4.8% | +26.3 |
| 60×16 | Git worktree remove | 227.6 / 235.5 | 225.5 / 233.3 | +0.9% | +1.4 |

Completing the first `bps` filter in an initially unfiltered FFmpeg menu took 48.52 ms before and 48.49 ms with reuse at 80×24. At 60×16 the medians were 25.79 and 25.75 ms. This timed the final `ps` after the first `b`, through receipt of the matching screen. The cache lives only during construction. It cannot reuse the lazy unit-search work that starts with a keystroke.

FFmpeg's median first-frame resident memory rose by about 2.3 MiB. For unfiltered FFmpeg the median process high-water mark through dismissal went from 54.23 to 56.04 MiB at 80×24 and 53.93 to 55.87 MiB at 60×16. Across the primary cases no median RSS or high-water increase crossed the greater of 2 MiB or 5% of the baseline. All measured interaction p95 changes stayed inside the greater of 5 ms or 10%. These are warm local results on Ubuntu 26.04.1, CPython 3.14.4 and Bash 5.3.9 with a Threadripper 3970X. Cold reads and other interpreters were outside this experiment.

The independent 40-pair Git repeat measured 223.34 ms before and 223.28 ms with reuse at 80×24, and 223.83 and 223.36 ms at 60×16. Repeat p95 increased by 1.8 and 2.5 ms respectively, within the control threshold. The small differences changed direction across individual pairs.

## What the cache saved

On FFmpeg's 1,759 rows, 2,296 of 7,919 cleanup calls hit the cache (29.0%). The other 5,623 calls ran the original cleanup. The three-row Git profile had six hits in 12 calls. In a separate 12-pair CPU sweep with profiles already loaded, FFmpeg construction fell from 319.08 to 292.09 ms. Git fell from 0.385 to 0.270 ms. All 76 bundled profiles had lower constructor CPU medians in this sweep. Git's constructor saving was too small to distinguish reliably in full terminal startup. Raw per-command timings and `construction-by-command.csv` are in the local evidence directory.

## Search and detail verification

- The model comparison matched byte for byte across 6,487 bundled rows in 76 profiles plus 14 rows from custom, discovered and reopened preview fixtures. It included ordered view fields, complete searchable text, expanded guidance and 640 ordered query transitions with category and row selection. The model capture SHA-256 was `dfb5fec6c8bb1f612c9673a00dffe767a57fa3b3e2dd0681bf523f110c3eb888`.
- For every FFmpeg and Git option, a cell-recording window compared Simple, Detailed and Expanded through the last available page. All **17,808 page records** matched, including text, coordinates and attributes. The comparison covered 7,363 pages at 80×24 and 10,445 at 60×16. Another 156 records compared the filtered screen and every category's ordered matches across all three levels for 13 queries per menu and size. Cases included `bps`, `bits per second`, case-sensitive unit spellings, a no-match query and clearing the filter. The combined screen capture SHA-256 was `b8f8269fb759864b45a1467994d54f795807e92bd82593bb33ac4c7b2a4d408e`.
- The timed real Bash sessions independently checked decoded screen text against the baseline at each scripted checkpoint, cycled all three levels, and verified the original pending line and cursor after cancellation. All 87 focused candidate tests passed, including the native tmux checks for FFmpeg bitrate guidance at both sizes, long category titles, expanded scrolling and literal option insertion.

### Reproduction

The comparison used working-tree runtime bytes at `1f26c69202cbd2231e51889d273a55e6a24c0479`. Existing documentation and benchmark-tool changes were present. The runtime and profile files matched the commit. Both snapshots used identical bundled profiles, Bash integration, interpreter and isolated configuration. Neither snapshot had project bytecode. Each warm-up and recorded open started a new helper with discovery off. Pair order alternated. Only the candidate routed prose cleanup through a serial 4,096-entry LRU cache created in `Browser.__post_init__`. Its key was the exact input string and its value the existing immutable tuple of cleaned sentences. The cache expired before the first draw. The experiment changed neither the stored profiles nor the search, rendering or unit-conversion algorithms.

From the checkout, set `decoder` to a Python with the [media decoder dependencies](../tools/requirements-media.txt). Use a fresh report directory. The before and after trees need their own copies of the Python test files because the fixtures locate the helper relative to those files.

```bash
export MENU_BENCH_DIR="$(mktemp -d)"
export PYTHONDONTWRITEBYTECODE=1
bench="$PWD/tools/menu_benchmark"
for variant in before after; do
    tree="$MENU_BENCH_DIR/$variant"
    mkdir -p "$tree"/{cli_help,bash,tests,tools}
    cp cli_help/*.py "$tree/cli_help/"
    cp bash/*.bash "$tree/bash/"
    cp tests/*.py "$tree/tests/"
    cp tools/*.py "$tree/tools/"
    for entry in VERSION profiles config tests/fixtures; do ln -s "$PWD/$entry" "$tree/$entry"; done
done
patch -s -d "$MENU_BENCH_DIR/after" -p1 < "$bench/prose/candidate.patch"
"$decoder" "$bench/prose/paired.py" > "$MENU_BENCH_DIR/paired.jsonl"
"$decoder" "$bench/prose/paired.py" --cases small > "$MENU_BENCH_DIR/git-repeat.jsonl"
python3 "$bench/constructor.py" > "$MENU_BENCH_DIR/constructors.jsonl"
for variant in before after; do
    python3 "$bench/parity.py" "$MENU_BENCH_DIR/$variant" > "$MENU_BENCH_DIR/model-$variant.jsonl"
    python3 "$bench/prose/screens.py" "$MENU_BENCH_DIR/$variant" > "$MENU_BENCH_DIR/screens-$variant.jsonl"
done
for check in model screens; do
    cmp "$MENU_BENCH_DIR/$check-before.jsonl" "$MENU_BENCH_DIR/$check-after.jsonl"
done
(cd "$MENU_BENCH_DIR/after" && PYTHONPATH=tests python3 -m unittest test_numerical_presentation test_value_semantics test_ffmpeg_manual_inventory test_menu_levels test_expansion_terminal.ExpansionScreenTests.test_ffmpeg_optional_audio_map_at_minimum_size)
```

Raw samples and byte-comparison inputs from this run are in the ignored local directory `tests/reports/serial-prose-20261124/`. The baseline SHA-256 digests for `presentation.py` and `ui.py` begin with `14276893a184` and `0926328f2eb3`. Applying the [experiment patch](../tools/menu_benchmark/prose/candidate.patch) produces `d70366158e68` and `b98b07a3ede0` respectively. [Paired PTY driver](../tools/menu_benchmark/prose/paired.py) · [Screen and search comparison](../tools/menu_benchmark/prose/screens.py)
