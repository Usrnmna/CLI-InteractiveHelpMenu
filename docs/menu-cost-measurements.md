# Three-level menu performance measurements

On November 24, 2026, the matched warm FFmpeg opening measured 518 ms before the redesign and 548 ms with the three-level menu. Eager prose preparation accounted for most of the constructor CPU. Four processes improved opening latency in a separate controlled experiment but more than doubled peak proportional memory. The first follow-up tested serial prose reuse. [Experiment results](serial-prose-reuse-experiment.md) [Five decisions and acceptance checks](#decisions)

## Measurement plan

Use the working tree as the serial reference. Run timing blocks sequentially with warm files, a fresh helper per open, isolated Bash, C.UTF-8 and discovery off for static menus. Keep CPU instrumentation, memory sampling and correctness checks separate from latency comparisons.

| Step | Cases and controls | Measurements and checks |
| --- | --- | --- |
| 1. Open and interact | FFmpeg, filtered FFmpeg and git worktree remove. Alternate the saved pre-redesign renderer and current renderer, with identical profiles. | Decode complete PTY frames. Record median and nearest-rank p95 for opening, filtering, navigation and level changes. Attribute constructor, prose, match, width and wrapping costs separately. |
| 2. Idle and resize | Both menus at 80×24 and 60×16, over repeated 10-second windows. | Count draws and measure helper CPU and context switches. Check resize, navigation, insertion, cancellation and restored terminal state. |
| 3. Load collections | Fresh processes with just the selected profile, subsets, the bundled collection and a larger collection. | Time load and validation, CPU and peak RSS. Check longest match, custom precedence, malformed files, changed files and full collection validation. |
| 4. Resolve discovery | Fixed help and manual fixtures with empty and fresh caches, an identity-guarded executable, stale cache, wrong identity and failed probe. | Separate identity, subprocess, parsing and cache times. Count actual requests, check cache reuse and rejection or fallback. |
| 5. Compare worker counts | Profile the eager row preparation first. Compare serial, fixed threads, fixed processes and workload-bounded automatic counts with affinity restricted to one CPU, two CPUs and the normal set. | Include pool setup, ordered results and shutdown before drawing. Compare complete first frames, subsequent key latency, total CPU and simultaneous process-tree memory. Check all-row and search parity, both terminal sizes and worker cleanup. Verify supported interpreter builds. |

Use 40 measured launches per primary comparison after warm-up and report smaller diagnostic samples separately. Apply the existing 30% large-menu median improvement target, improved p95, interaction/control p95 tolerance of max(5 ms, 10%) and memory tolerance of max(2 MiB, 5%). Record one decision per investigation and an acceptance test for each proposed follow-up. [Comparison protocol](ffmpeg-menu-performance-plan.md#before-and-after-measurement)

## Opening and interaction

The original three-pair check reported 508 ms before the redesign and 528 ms after, with other suites running. The repeat used 40 alternating pairs per pending line at the historical harness's 100×24 geometry. Neither snapshot contained project bytecode. Each invocation ended only when the decoder matched the complete menu, including selection and footer.

| Pending line | Pre-redesign median / p95 (ms) | Current median / p95 (ms) |
| --- | --- | --- |
| ffmpeg | 518.2 / 533.0 | 548.1 / 564.3 |
| `ffmpeg -map` | 516.8 / 532.6 | 547.2 / 561.5 |
| `ffmpeg -rw_timeout` | 519.1 / 529.2 | 551.6 / 577.7 |
| `git worktree remove` | 219.4 / 225.3 | 223.8 / 227.4 |

The current renderer was slower in all 120 FFmpeg pairs. Median paired differences were +30.8, +29.9 and +32.3 ms respectively. The small Git control's paired median was +3.7 ms. This confirms the direction of the earlier observation for the combined redesign on this host. It cannot assign the delay to any single detail level, unit alias or category label. A preliminary run that pointed at the checkout and an older saved tree had unequal project bytecode caches and was excluded. The worker matrix below uses a common entry wrapper and the current checkout's ordinary bytecode state. Compare results **within** each experiment.

Median / p95 key-to-complete-frame times below are in milliseconds. “First key” enters `b`. “Unit search” sends the remaining `ps` together and ends on the complete `bps` results frame. “Resize” changes to the other listed geometry. There are 40 observations per 80×24 cell and six per 60×16 cell.

| Serial input | FFmpeg 80×24 | Git 80×24 | FFmpeg 60×16 | Git 60×16 |
| --- | --- | --- | --- | --- |
| Detailed | 2.2 / 2.3 | 1.9 / 2.0 | 1.3 / 1.4 | 1.3 / 1.5 |
| Expanded | 2.8 / 3.2 | 1.8 / 1.9 | 1.9 / 1.9 | 1.2 / 1.2 |
| Simple | 2.3 / 2.4 | 1.5 / 1.6 | 1.4 / 1.5 | 1.1 / 1.1 |
| Move row | 2.0 / 2.2 | 1.6 / 1.6 | 1.2 / 1.2 | 1.0 / 1.1 |
| First key | 2.5 / 2.6 | 1.6 / 1.7 | 1.7 / 1.7 | 1.1 / 1.1 |
| Unit search | 48.8 / 50.0 | 1.7 / 2.1 | 25.0 / 25.4 | 1.3 / 1.3 |
| Resize | 1.9 / 2.0 | 1.6 / 1.7 | 3.2 / 3.3 | 2.0 / 2.1 |

The first unit search stood out from navigation. The serial FFmpeg menu took 48.8 ms at 80×24 and 25.0 ms at 60×16. The draw path requests filtered counts for visible sidebar categories, and the first unit query builds lazy prose aliases for rows it scans. Repeating a query after that work is cached measures a different operation. All timing comparisons matched the expected full cells, including the shorter labels, selection, summaries and full category header. Independent real-terminal assertions verified the `-b:v` guidance, a searchable `bps`, the 9/7/3 and 5/3/2 visible-row counts and the full custom title at both sizes.

### CPU attribution

Eight separately instrumented real FFmpeg opens attributed 295.0 ms of constructor CPU to the historical browser and 320.8 ms to the current one. Median loader CPU stayed at 114.0 / 113.7 ms, context resolution at 0.53 / 0.53 ms and first draw at 0.99 / 0.93 ms. Most of the extra opening cost occurred before drawing.

A separate, more heavily instrumented replay of the current 1,759-row constructor measured 350.7 ms CPU versus 0.42 ms for Git's three rows. Across 7,919 cleanup calls, `concise_description` consumed 244.4 ms inclusive. Of this, 202.6 ms came from preparing the description blocks, 24.4 ms from the direct row-summary call and 17.1 ms from value prose. The complete value-text path took 54.2 ms inclusive. These nested figures must not be added together.

| Current FFmpeg operation, 80×24 | Median CPU (ms), eight replays |
| --- | ---: |
| Simple / Detailed / Expanded draw with no filter | 0.74 / 0.84 / 1.18 |
| Declaration width, initial category, all three views | 0.02 |
| Detail wrapping, Detailed / Expanded | 0.03 / 0.29 |
| First Simple `bps` query and draw / repeat draw | 46.44 / 1.25 |
| Option matching within those two operations | 45.75 / 0.61 |

The first-frame and interaction results favor testing exact-input reuse in the serial prose path. Width and wrapping were small for these selections. Any later cache for unit searches must preserve both legacy substring matches and semantic aliases, their order and current category selection.

## Idle redraws

At a fixed geometry the menu completed 66 redraws in each 10-second window. Each row below gives the observed range across three windows. Linux CPU accounting used 10 ms ticks. Redraws were counted at return from the actual draw function and only timestamps inside the measured window were included.

| Columns | Menu | Draws | User CPU (ms) | System CPU (ms) | Voluntary switches | Involuntary switches | Resize median (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 80 | ffmpeg | 66 | 40 | 0–10 | 66 | 2–5 | 2.0 |
| 80 | small | 66 | 20 | 0–10 | 66 | 0–10 | 1.7 |
| 60 | ffmpeg | 66 | 30–40 | 0 | 66 | 2–7 | 3.3 |
| 60 | small | 66 | 20–30 | 0 | 66 | 5–8 | 2.2 |

After each window the harness changed geometry, checked the decoded frame, cycled all views, moved the row, searched and resized back. It alternated literal insertion and cancellation and verified Readline's exact buffer, cursor and terminal mode flags. Independent tmux tests covered alternate-screen exit, scrollback and the minimum-size recovery path. The resize timings above are observed recoveries after these particular idle windows. The unsignalled fallback can wait for the existing 150 ms poll.

## Startup profile loading

The requested command and its 1,613-byte Git profile stayed fixed while unrelated files were added. Each size used 20 fresh interpreters after warm-up, alternating ascending and descending order. Load wall time starts inside the fresh interpreter and includes JSON reading, decoding and runtime validation. Context lookup is separate. Peak RSS is the whole measurement process's image high-water mark, including imported fixture code. The 152-file case adds 76 synthetic distinct command paths, adjusted for schema restrictions, to the shipped set.

| Files | MiB on disk | Load wall median / p95 (ms) | Load CPU (ms) | Context CPU (ms) | Image peak RSS (MiB) |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.0015 | 0.40 / 0.42 | 0.40 | 0.35 | 28.0 |
| 19 | 1.56 | 19.9 / 20.4 | 19.9 | 0.38 | 31.6 |
| 76 | 8.66 | 118.1 / 122.2 | 118.1 | 0.47 | 48.6 |
| 152 | 17.1 | 226.1 / 230.5 | 226.0 | 0.55 | 67.8 |

In 12 separate instrumented loads, reading and JSON-decoding the 75 unrelated files took 47.2 ms of CPU and validating them took 99.8 ms. The selected file took 0.03 and 0.07 ms respectively. Across the collection, 20,144 calls to the text validator accounted for 64.3 ms inside validation. Instrumentation adds overhead, especially around these small calls. The 75 unrelated bundled files added roughly 118 ms and 20.6 MiB to the Git control. Longest-path resolution remained below 1 ms. All static, discovered and guarded requests pay the collection cost. A loading experiment must keep resolution based on the command tuple inside each file, exact-path custom precedence, same-directory duplicate errors and the current behavior when an unrelated file is malformed. Each open must see edited, added and deleted files. An edited override was reloaded, removing it restored bundled data, and an unrelated malformed custom file made the real `--check` exit 1. Full `--check` must still enumerate and validate the complete collection. A persistent index or a change in when invalid profiles become visible requires a separate architecture decision.

## Guarded discovery

Twelve measured repetitions used real fixture executables in a private PATH and cache, with the example yq driver enabled. The ordinary miss ran the fixed help and manual commands. The guarded `yq eval` miss ran the fixed version and eval-help commands and displayed the curated profile. The “Variant” column includes the version subprocess. “Stat identity” is the separate cache-key metadata work. Cache time includes validation and serialization. Times are milliseconds and exclude the initial bundled profile load.

| Route | Cache / identity | Probes | Context wall median / p95 | Variant | Help + man | Parse + merge | Cache read + write | Stat identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| discover-tool | miss | 2 | 39.4 / 40.5 | 0.00 | 37.4 | 1.4 | 0.31 | 0.05 |
| discover-tool | hit | 0 | 0.40 / 0.42 | 0.00 | 0.00 | 0.00 | 0.17 | 0.05 |
| discover-tool | expired | 2 | 39.1 / 40.1 | 0.00 | 37.1 | 1.4 | 0.36 | 0.04 |
| yq eval | miss | 2 | 23.5 / 24.6 | 10.9 | 10.6 | 0.82 | 0.29 | 0.05 |
| yq eval | hit | 1 | 11.3 / 11.9 | 10.8 | 0.00 | 0.00 | 0.18 | 0.05 |
| yq eval | expired | 2 | 23.6 / 24.4 | 11.0 | 10.8 | 0.83 | 0.36 | 0.05 |
| yq eval | bad-identity | 1 | 10.9 / 11.9 | 10.7 | 0.00 | 0.00 | 0.00 | 0.00 |

Expiring an entry repeated the appropriate probes. The wrong yq variant and a timed-out version request both failed before the cache could authorize a menu. The module freshness fixtures also verified the different policy for an unverified Python module fingerprint. It fetches fresh help while bypassing cache reads and writes. Ordinary fallback, executable replacement, corrupt cache and pending-argument isolation passed their existing tests. A cache hit already removes ordinary subprocess cost. Reusing a previous guard or skipping help on a guarded miss would change which requests succeed. The fixture evidence does not justify that change.

## Worker pools and CPU limits

The hottest independent work was formatting a profile's rows before the first frame. It walks Python objects, builds strings and invokes many short regular-expression operations. On these GIL-enabled CPython builds, threads added scheduling and batch-cache overhead. There was no demonstrated long GIL-releasing native kernel in this path. File reads and subprocess waits can release the GIL, but warm profile loading consumed nearly its elapsed time in CPU, and guarded discovery has ordering and identity requirements. Neither was a reason to parallelize terminal access or probes.

The cells below give first-frame median / p95 in milliseconds. “Small” is the three-row Git worktree remove profile. The 80×24 normal allocation has 40 measured opens per policy. Restricted allocations have eight each and the 60×16 sensitivity check has six each, so their nearest-rank p95 is the largest observation. The automatic policies selected 1, 2 and 4 for FFmpeg as the allocation grew, and 1 for Git in all cases. The fixed two-worker policies deliberately oversubscribed the one-CPU allocation.

| Allocation and menu | Serial | 2 threads | 2 processes | Auto threads | Auto processes |
| --- | --- | --- | --- | --- | --- |
| 1 CPU · ffmpeg | 499.4 / 530.7 | 518.0 / 537.9 | 579.3 / 586.8 | 500.0 / 542.6 | 498.9 / 554.9 |
| 1 CPU · small | 176.6 / 177.6 | 191.2 / 195.3 | 202.5 / 213.1 | 177.2 / 179.2 | 176.8 / 178.3 |
| 2 CPUs · ffmpeg | 493.7 / 496.6 | 512.1 / 515.4 | 398.2 / 459.7 | 511.8 / 530.0 | 395.0 / 404.8 |
| 2 CPUs · small | 173.0 / 176.5 | 187.4 / 189.5 | 196.4 / 198.8 | 173.8 / 181.6 | 174.0 / 175.4 |
| 64 CPUs · ffmpeg | 498.4 / 507.7 | 521.5 / 539.7 | 404.2 / 408.6 | 531.0 / 538.6 | 322.9 / 337.6 |
| 64 CPUs · small | 176.4 / 179.9 | 191.8 / 195.7 | 199.9 / 204.5 | 177.0 / 179.5 | 176.9 / 180.6 |
| 64 CPUs, 60×16 · ffmpeg | 495.2 / 497.4 | 519.8 / 521.5 | 403.9 / 433.2 | 528.1 / 538.0 | 321.1 / 330.7 |
| 64 CPUs, 60×16 · small | 176.6 / 179.1 | 190.9 / 194.6 | 199.4 / 204.9 | 175.9 / 177.0 | 176.5 / 177.6 |

With the normal allocation, four processes reduced the unfiltered FFmpeg median by 35.2% and improved p95. For an initial `-map` filter, serial median/p95 was 502.0/512.1 ms and four processes measured 323.0/336.1 ms. For `-rw_timeout` the corresponding figures were 500.9/509.4 and 325.8/336.7 ms (40 opens each). Both filtered cases also exceeded the 30% median target. The largest subsequent interaction p95 increase for automatic processes across these cases and the two unfiltered controls was under 1 ms. Two processes on a two-CPU allocation reduced the median by 20.0%. Two fixed processes on one CPU increased the median by 16.0%. Serial execution avoided a 23.5 ms median penalty on Git compared with a fixed two-process pool. The first FFmpeg unit search still took about 49 ms at 80×24 with four processes because the pool had already closed.

### Total cost through dismissal

Each row gives medians from five separately instrumented opens with the same search, navigation, view changes, resize and cancellation. CPU includes the helper and its waited children. Worker IDs identify threads or processes that actually executed a batch. A serial open counts the main thread as one. Short-lived children between RSS samples can make the Git process peak particularly low.

| Menu | Policy | Executing workers | Total CPU (ms) | Peak summed RSS (MiB) | Peak summed PSS (MiB) |
| --- | --- | --- | --- | --- | --- |
| ffmpeg | serial | 1 | 560.0 | 54.2 | 42.2 |
| ffmpeg | thread-2 | 2 | 580.0 | 56.6 | 44.5 |
| ffmpeg | process-2 | 2 | 649.9 | 158.5 | 81.7 |
| ffmpeg | thread-auto | 4 | 590.8 | 57.0 | 45.0 |
| ffmpeg | process-auto | 4 | 671.4 | 235.9 | 89.9 |
| small | serial | 1 | 191.3 | 45.2 | 33.6 |
| small | thread-2 | 1–2 | 198.5 | 46.2 | 34.2 |
| small | process-2 | 2 | 221.6 | 46.3 | 34.3 |
| small | thread-auto | 1 | 190.0 | 45.3 | 33.4 |
| small | process-auto | 1 | 191.9 | 45.3 | 33.6 |

Four processes raised FFmpeg's peak PSS by 47.7 MiB and total CPU by 19.9%. Even after apportioning shared pages, the memory increase exceeded the project's max(2 MiB, 5%) review threshold. On the stock read-only Ubuntu 24.04 test targets, both CPython 3.10.20 and 3.12.3 raised `EROFS` when the process pool attempted to create a POSIX semaphore. Threads worked there. With a private writable `/dev/shm` and a two-CPU quota, the same images passed FFmpeg and Git view equality, search ordering, interruption and failure cleanup (1,762 rows each), and the automatic rule detected two CPUs. All three interpreters were ordinary GIL-enabled builds. No free-threaded interpreter or alternate start method was benchmarked.

### Workload size

Eight runs per cell used evenly spaced rows from the real FFmpeg profile in a custom override. Both serial and pool runs loaded the same override. Values give median / p95 first-frame time in milliseconds.

| FFmpeg rows | Auto workers | Serial | 2 processes | Auto processes |
| --- | --- | --- | --- | --- |
| 64 | 1 | 196.9 / 202.1 | 216.0 / 227.9 | 197.9 / 207.3 |
| 160 | 1 | 215.7 / 223.4 | 247.2 / 251.3 | 216.8 / 218.7 |
| 320 | 1 | 245.5 / 247.1 | 250.2 / 260.0 | 247.0 / 251.8 |
| 640 | 2 | 311.9 / 317.8 | 291.1 / 297.0 | 293.2 / 294.8 |
| 960 | 3 | 372.2 / 375.4 | 331.5 / 334.3 | 302.5 / 304.2 |

The first sampled two-process win was at 640 rows. At 320 rows the fixed pool still lost. The crossover lies between those sampled sizes for this input and host. A row count alone cannot describe the cost of every custom profile.

A second automatic policy also required 65,536 summary-plus-detail characters per worker. With 640 authentic rows it chose two workers and measured 292.3/297.9 ms median/p95 versus 311.6/316.0 serial. With the same 640 flags, minimal summaries and no row value metadata, the row-only policy still chose two and measured 222.7/226.0 ms, slower than serial at 203.9/213.7 ms. The size-aware policy chose one and measured 204.5/207.9 ms. Each cell has eight samples. The full 1,759-row profile has 457,021 prose characters. These cutoffs are experimental and depend on content, hardware and launch costs.

The host comparison checked full option fields, lazy Detailed and Expanded content, unit aliases and ordered search results for all 6,487 rows in all 76 menus. The supported container checks covered the same properties on FFmpeg and Git. A malformed task and a parent interruption during construction left one main thread and zero worker processes. In a separate real Bash check, `q` was queued 70 ms after curses initialization, while all four FFmpeg workers were active. Median time to restored Readline was 284.7 ms serial, 315.3 ms with threads and 117.2 ms with processes (six opens each, including the buffer-snapshot wait). The edit and terminal flags matched, and worker PIDs disappeared in all runs. Input remains queued until synchronous construction finishes. [Queued cancellation check](../tools/menu_benchmark/phase1/queued_cancel.py)

## Verification and limits

All 138 focused host tests passed, including independent Bash/tmux checks at both sizes. All worker policies in the PTY matrix matched the complete serial cells at every scripted checkpoint. Host full-collection parity and the two supported container checks cover different scopes as reported above. The timing distributions describe one warm Linux host. Cold filesystem reads, WSL, free-threaded Python, alternate process start methods, sub-5-ms memory spikes and real installed discovery tools were outside the measurements.

## Reproducing the measurements

The serial runtime is commit `1f26c69202cbd2231e51889d273a55e6a24c0479`. The tracked tree was clean at the start. All timing helpers are developer tools. The experiment used the existing Bash widget, Python runtime, profiles and release inputs. An unrelated untracked Codex environment file appeared during the run and was excluded from the benchmark inputs. The host ran Ubuntu 26.04.1, Bash 5.3.9 and standard CPython 3.14.4 on a Threadripper 3970X (32 physical cores, 64 logical CPUs). Static helpers used xterm-256color and C.UTF-8. System-library bytecode and filesystem reads were warm. Each Alt-H launched a new helper. No machine-wide cache flush or exclusive host reservation was used.

The pre-redesign inputs are the saved Stage 1 versions of `ui.py`, `presentation.py` and `value_semantics.py`. Their SHA-256 digests begin with `71b43fbe53f4`, `adb5ddc8fc69` and `9c40bf505b41`. The corresponding working versions begin with `0926328f2eb3`, `14276893a184` and `0874e08fad5f`. The SHA-256 of the sorted compact JSON path-to-digest map for all 76 profile files is `97dda0651ce09e5b0209e2b3ce6842cf5d360bf2f54fd9c5180d50e53269dcb9`. The two trees read identical current profile bytes, including FFmpeg (`b03e892648cf`) and Git worktree remove (`3e59b87eca74`). For the historical comparison, copy current `bash/` and `cli_help/` **without** project bytecode to both snapshot roots, replace just the three files under `before/cli_help/`, and link `VERSION`, `config/`, `profiles/`, `tests/` and `tools/` from both roots to the checkout. Set `PYTHONDONTWRITEBYTECODE=1` for the controller and children. The old renderer predicts its own expected cells. For pool comparisons the unmodified serial renderer predicts every variant's cells.

Run from the checkout in Bash. Set `decoder` to a Python with the project's [media decoder dependencies](../tools/requirements-media.txt). Raw JSON Lines stay under the ignored local directory `tests/reports/menu-costs/`. The saved pre-redesign files are also reproducible from commit `2797f1c` and the [small Stage 1 reconstruction patch](../tools/menu_benchmark/phase1/pre-redesign.patch). The setup below assumes a fresh report directory.

```bash
report="$PWD/tests/reports/menu-costs"
bench=tools/menu_benchmark/phase1
export PYTHONDONTWRITEBYTECODE=1
for variant in before after; do
    tree="$report/matched/$variant"
    mkdir -p "$tree/cli_help"
    cp -r bash "$tree/"
    cp cli_help/*.py "$tree/cli_help/"
    for entry in VERSION config profiles tests tools; do ln -s "$PWD/$entry" "$tree/$entry"; done
done
for module in presentation ui value_semantics; do
    git show "2797f1c:cli_help/$module.py" > "$report/matched/before/cli_help/$module.py"
done
patch -s -d "$report/matched/before" -p1 < "$bench/pre-redesign.patch"
MENU_BENCH_DIR="$report/matched" "$decoder" tools/menu_benchmark/terminal.py 40 ffmpeg small map timeout > "$report/matched.jsonl"

# The existing terminal harness imports its serial oracle from this root.
mkdir -p "$report/current"
ln -snf "$PWD" "$report/current/before"
export MENU_BENCH_DIR="$report/current"
"$decoder" "$bench/terminal_matrix.py" --repeats 40 ffmpeg small > "$report/normal.jsonl"
for limit in 1 2; do
    "$decoder" "$bench/terminal_matrix.py" --cpus "$limit" --repeats 8 ffmpeg small > "$report/cpu-$limit.jsonl"
done
"$decoder" "$bench/terminal_matrix.py" --width 60 --repeats 6 ffmpeg small > "$report/narrow.jsonl"
"$decoder" "$bench/terminal_matrix.py" --resources --repeats 5 ffmpeg small > "$report/resources.jsonl"
for width in 80 60; do
    "$decoder" "$bench/terminal_matrix.py" --idle --width "$width" --repeats 3 --modes serial ffmpeg small > "$report/idle-$width.jsonl"
done
for check in load load-stages discovery presentation; do
    python3 "$bench/components.py" "$check" > "$report/$check.jsonl"
done
for rows in 64 160 320 640 960; do
    "$decoder" "$bench/terminal_matrix.py" --rows "$rows" --repeats 8 --modes serial,process-2,process-auto ffmpeg > "$report/subset-$rows.jsonl"
done
"$decoder" "$bench/terminal_matrix.py" --repeats 40 --modes serial,process-auto map timeout > "$report/filtered.jsonl"
for control in full compact; do
    extra=()
    if [ "$control" = compact ]; then extra+=(--compact); fi
    "$decoder" "$bench/terminal_matrix.py" --rows 640 "${extra[@]}" --repeats 8 --modes serial,process-auto,process-sized ffmpeg > "$report/size-$control.jsonl"
done
STAGE1_INSTRUMENT=1 MENU_BENCH_DIR="$report/matched" "$decoder" tools/menu_benchmark/terminal.py 8 ffmpeg small > "$report/phases-pty.jsonl"
python3 "$bench/queued_cancel.py" > "$report/queued-cancel.jsonl"
python3 "$bench/check_workers.py" --all
PYTHONPATH=tests python3 -m unittest test_menu_levels test_numerical_presentation test_discovery test_module_freshness test_module_discovery test_core test_terminal_screen
```

The stock compatibility command was run for `noble310` and `noble312`. The second run used the same archive, offline image and unprivileged user. The following reproduces the two-CPU container override without changing the sandbox runner.

```bash
target=noble310  # Repeat for noble312.
python3 -I tests/run_sandbox.py --target "$target" --include "$bench/check_workers.py" --include "$bench/workers.py" -- python3 -I "$bench/check_workers.py"
python3 - "$target" <<'PYTHON'
import subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path("tests").resolve()))
import run_sandbox as sandbox
target = sys.argv[1]
files = {Path("tools/menu_benchmark/phase1") / n for n in ("workers.py", "check_workers.py")}
with tempfile.TemporaryFile() as archive:
    sandbox.snapshot(archive, files)
    cmd = sandbox.sandbox_command(target)
    pos = cmd.index(sandbox.image_name(target))
    cmd[pos:pos] = ["--tmpfs=/dev/shm:rw,nosuid,nodev,noexec,size=16m,mode=1777", "--cpus=2"]
    subprocess.run([*cmd, "python3", "-I", "tools/menu_benchmark/phase1/check_workers.py"],
                   stdin=archive, check=True)
PYTHON
```

In the worker comparison, the serial control and candidates use the same Python entry wrapper. The non-serial path cuts the ordered option list into contiguous batches. Each batch formats its own shared value references. The parent collects results in submission order, associates them with the original objects and closes the pool before the first draw. Pool imports, task dispatch, pickling in both directions, teardown and terminal decoding all fall inside the opening measurement. Workers never handle input, curses or discovery. The process experiment explicitly uses Linux `fork` in a single-threaded helper. Other process start methods would need their own measurements. [Temporary adapter](../tools/menu_benchmark/phase1/workers.py) · [PTY matrix](../tools/menu_benchmark/phase1/terminal_matrix.py)

Automatic selection uses the smallest of four workers, detected CPU capacity, and one worker per 320 rows rounded down, with a minimum of one. A count of one calls the existing serial constructor directly. Capacity is the minimum of the interpreter-reported count, available affinity and any visible cgroup v2 CPU quota up the process's hierarchy. Fractional quotas round down, with a floor of one. Older interpreters fall back to `os.cpu_count()` plus available limit information, then one if no count is reported. The benchmark does not detect cgroup v1 quotas or hidden ancestor limits. The host had affinity 0–63 and no visible finite quota. Restricted host runs used CPUs 0 and 0–1. A separate container check imposed a two-CPU quota.

The resource pass uses helper and waited-child user plus system CPU through dismissal. External sampling reads simultaneous RSS and PSS from the helper tree's `smaps_rollup` at approximately 5 ms intervals, excluding the Bash controller. The observed peak can miss shorter allocations. Summed RSS counts shared pages once per process. Proportional set size (PSS) apportions those pages. The ordinary timing pass reads the main helper's RSS checkpoints outside key timers. Constructor instrumentation reports inclusive CPU, so nested function times overlap. Discovery instrumentation reports wall time, including subprocess waits. [Component fixtures](../tools/menu_benchmark/phase1/components.py) · [Worker correctness checks](../tools/menu_benchmark/phase1/check_workers.py)

## Decisions

| Investigation | Affected menus and measured cost | Decision and smallest next experiment | Acceptance checks |
| --- | --- | --- | --- |
| Opening and interaction | FFmpeg added 30–32 ms per matched pair at the median. Eager prose handling dominates. View changes typically take 1–3 ms, while the first `bps` query costs 49 ms at 80 columns. [Opening evidence](#opening-and-interaction) | **Experiment completed. Defer production adoption.** The tested cache reduced FFmpeg opening by 4.4–5.4%. The first unit search showed little change. [Follow-up evidence](serial-prose-reuse-experiment.md) | Compare every view field, ordered matches, original evidence and rendered guidance, including custom, discovered and preview menus. Re-run 40 paired opens for all three FFmpeg cases and the small controls. Target 30% lower FFmpeg median and improved p95. Apply the existing control, interaction and memory limits. |
| Idle redraws | Both baseline menus performed 66 full draws per 10 seconds with no input. [Idle evidence](#idle-redraws) | **Retain unchanged-timeout suppression.** All twelve idle windows had zero redundant draws. [Follow-up measurements](#idle-redraw-experiment) | Zero redundant draws during each stable 10-second window, lower CPU, and resize detected within the existing poll interval plus one draw. Verify insertion, cancellation, scrollback, all levels and terminal restoration at both sizes. |
| Startup profile loading | All menus load 76 files. The unrelated 75 cost about 118 ms on the Git control. [Collection evidence](#startup-profile-loading) | **Retain the serial printable-text check.** Full enumeration and diagnostics matched. [Follow-up measurements](#serial-profile-validation-experiment) | Match all current acceptances, errors and diagnostics, including mixed controls, Unicode, duplicates and invalid unrelated files. Retain longest match, override freshness and full `--check`. Require lower loader CPU and improved small-menu first-frame median and p95 without a threshold regression. Selective loading or a persistent index requires separate approval. |
| Guarded discovery | Ordinary fixture hit 0.4 ms, guarded hit 11.3 ms and guarded miss 23.5 ms. [Discovery evidence](#guarded-discovery) | **Defer** a discovery change. The remaining guarded-hit probe establishes present executable identity. | Preserve fixed arguments, fresh identity checks, cache validation and route-specific failure behavior. Revisit if representative installed-tool traces show a material spend beyond required probes. |
| Multi-core processing | On FFmpeg four processes brought first frame from 498 to 323 ms, peak PSS from 42 to 90 MiB and total CPU from 560 to 671 ms. Threads slowed opening. [Worker evidence](#worker-pools-and-cpu-limits) | **Defer pools and retain serial execution** across production menus. In an experimental selector use one worker on a single CPU or below the measured workload cutoff. | Reconsider after serial improvements only if a bounded process prototype still meets first-frame, control and memory criteria, handles unavailable semaphores, preserves all content and ordering, and cleans up on cancellation and failure. Adding production processes requires architecture approval. |

## Idle redraw experiment

The November 25, 2026 baseline was the working tree at `cc30ade99d1ddf2f593b409f66bd05dc0029f44c`. Only ROADMAP.md and the release and release-candidate guides had uncommitted edits at the start. The host was Ubuntu 26.04.1, CPython 3.14.4, Bash 5.3.9 and xterm-256color. Benchmarks used warm files, fresh helpers, isolated Bash and discovery off. The timing blocks ran sequentially, separately from the test suites.

Previously, a 150 ms input timeout returned to the top of the loop and redrew the complete frame. The experiment keeps the last drawn geometry and page capacity across timeouts. Each poll still reads the controlling terminal size. A key (including KEY_RESIZE) invalidates the frame, and a changed geometry triggers a redraw even without a key.

| Starting size | Menu | Idle draws before → after | Helper CPU before → after (ms) | Time to resized frame after change (ms) |
| --- | --- | --- | --- | --- |
| 80×24 | FFmpeg | 66 → 0 | 40–50 → 0 | 2.0–2.1 |
| 60×16 | FFmpeg | 66 → 0 | 30 → 0 | 3.3–3.4 |
| 80×24 | git worktree remove | 66 → 0 | 20–30 → 0 | 1.9–2.0 |
| 60×16 | git worktree remove | 66 → 0 | 20–30 → 0–10 | 2.3–2.5 |

Each cell covers three 10-second windows after warm-up for each revision. CPU is the sum of helper user and system ticks at 10 ms resolution. A zero reading means no tick accrued in that interval. All windows retained 66 voluntary context switches. In four additional candidate opens, the first key after ten idle seconds changed Simple to Detailed in 1.6–2.5 ms. Resize without a signal can take the remainder of the existing polling interval plus the draw.

To reproduce the idle rows, use the [phase 1 PTY controller](../tools/menu_benchmark/phase1/terminal_matrix.py) with `--idle --modes serial --repeats 3 --width 80 ffmpeg small`, then repeat at width 60. Run once per checkout with its Bash adapter, helper and identical profiles. Use the baseline renderer as the cell oracle. The local experiment directory `tests/reports/idle-validation-cc30ade/` contains the source hashes, snapshot-specific runner, raw JSON Lines and post-idle key replay. Inert executables in the private PATH detected target execution. The controller compared complete frames at both sizes, cycled all three views, moved selection, searched, resized back and alternated exact literal insertion and cancellation. Readline buffers and cursor offsets matched, terminal mode flags were restored and the execution marker stayed absent.

**Decision: retain idle redraw suppression.** All twelve stable candidate windows had zero redundant draws and lower measured CPU. All 13 focused host checks passed, including an unsignalled resize between timeouts, a shrink below minimum and recovery, scrollback preservation, all three detail levels and alternate-screen restoration. The frozen v0.4.0-alpha candidate predates this change.

## Serial profile validation experiment

Both comparison trees contain the retained idle loop. Only `cli_help/core.py` differed between their runtime inputs. Each load still reads every file and validates every field, in the same order. Most display fields contain only printable characters. A single `str.isprintable()` call now recognizes plain built-in strings of that kind. String subclasses retain the original character-by-character check. For a string containing a nonprintable character the original scan still distinguishes permitted tabs and newlines from rejected controls. Type, empty-string and field-specific diagnostics use the original checks.

| Warm workload | Loading wall time, median / p95 (ms), before → after | Loader CPU, median / p95 (ms), before → after |
| --- | --- | --- |
| All 76 bundled files | 118.52 / 120.99 → 74.12 / 76.69 | 118.36 / 120.91 → 74.04 / 76.33 |
| Bundled + two custom files | 119.30 / 122.81 → 74.98 / 81.03 | 119.25 / 122.71 → 74.97 / 80.94 |

Forty alternating pairs per workload followed one discarded warm-up pair. Each sample used a fresh system Python process with warm filesystem reads. The custom collection replaced both the Git worktree parent and its remove leaf. Seventy-eight files produced 76 effective commands. The 118.52 ms bundled baseline reproduced the earlier 118.1 ms observation.

| Instrumented loader stage | Bundled median CPU (ms), before → after | With overrides, before → after |
| --- | --- | --- |
| Read file and decode UTF-8 | 8.41 → 8.54 | 8.54 → 8.44 |
| Parse JSON | 47.52 → 47.50 | 47.76 → 47.37 |
| Validate profiles, inclusive | 100.83 → 55.71 | 100.80 → 55.35 |
| Validate text, within profile validation | 65.12 → 21.18 | 64.99 → 21.06 |

These are 12 separate pairs with CPU timing wrappers. Instrumentation increases times, especially across the 20,144 text checks per bundled load. The last row is already included in the preceding row. The comparison uses the same files on both sides. The historical single-file measurement represents a different workload.

| Menu | Terminal | First frame median (ms), before → after | First frame p95 (ms), before → after |
| --- | --- | --- | --- |
| Bundled Git worktree remove | 80×24 | 223.8 → 179.8 | 231.6 → 185.1 |
| Bundled Git worktree remove | 60×16 | 223.8 → 181.1 | 228.6 → 187.6 |
| Git with parent and leaf overrides | 80×24 | 223.2 → 179.1 | 228.3 → 184.1 |
| Git with parent and leaf overrides | 60×16 | 222.8 → 179.2 | 225.5 → 183.8 |
| FFmpeg | 80×24 | 550.3 → 503.7 | 572.6 → 522.5 |
| FFmpeg | 60×16 | 550.7 → 508.5 | 572.5 → 529.2 |

Each of the six rows covers 40 alternating pairs after warm-up. The controller timed the first fully matched terminal frame, then checked navigation, search, detail levels, resize and dismissal. The largest increase in interaction p95 was 0.36 ms on the FFmpeg unit search. The largest increase in median checkpoint RSS or high-water memory was 0.012 MiB. Both were below the review limits of the greater of 5 ms or 10% for latency, and 2 MiB or 5% for memory. The raw logs and percentile calculations are in the local experiment directory.

To repeat the validation comparison, place two copies of the same source tree in `$MENU_BENCH_DIR/before` and `$MENU_BENCH_DIR/after`. Use the retained idle loop in both. Restore only `cli_help/core.py` from `cc30ade` in the before copy. Remove project bytecode from the disposable copies. In a separate custom directory, copy the bundled Git worktree remove profile to `leaf.json` and change its first option to `--fixture`, its summary to `Read café 日本`, and its detail to `First line\nSecond\tfield.` in JSON. Copy it to `parent.json` with the command path `["git", "worktree"]`.

From each comparison root, use the same [component controller](../tools/menu_benchmark/phase1/components.py) with `load-one profiles` and `load-stages`, appending the absolute custom directory to each command for the override workload. For the first-frame comparison, use an absolute `MENU_BENCH_DIR`, the [paired Bash/PTY controller](../tools/menu_benchmark/prose/paired.py) and the [media decoder dependencies](../tools/requirements-media.txt). Supply private inert Git and FFmpeg stubs in the test PATH. The controller launches both helpers with the system interpreter.

```bash
"$decoder" tools/menu_benchmark/prose/paired.py --cases small ffmpeg
"$decoder" tools/menu_benchmark/prose/paired.py --cases small --git-override "$custom/leaf.json"
```

The Unicode comparison evaluated each of the 1,114,112 code points alone and embedded between a printable prefix, newline, tab and combining-text suffix. Both revisions returned identical verdicts and error text. They also agreed on empty strings, other input types and the serialized effective profiles. An invalid unrelated JSON file, a control in an unrelated description and a duplicate custom command each produced identical exit status, stdout and stderr in both real `--bash` and `--check` invocations. In a single Bash session per revision, reopening after editing and deleting the leaf inserted `--fixture`, then `--changed`, then the bundled `-f`. Each insertion preserved the suffix, the cursor and the unexecuted command.

**Decision: retain the serial printable-text check.** Bundled loader CPU fell by 44.32 ms at the median. Both the bundled and overridden Git controls reached a usable first frame sooner at the median and p95 at both sizes. The complete collection still participates in every open. Both improvements postdate the frozen v0.4.0-alpha candidate and are included in the v0.4.1-alpha source.

## Combined offline verification

All 13 focused idle tests and all 20 focused loader tests passed on the host. The strict numerical gate initially flagged the two edited runtime source fingerprints. Review confirmed that the changed sources contain the timeout and printable-field checks and that no numerical declarations changed. Updating those fingerprints restored a clean strict check.

All three sandboxes verified the same 1,015 tracked files before starting the suite. The SHA-256 of that manifest was `ff1fd7523b6866aa4511171e630bed4d307182e44b763cb39edd16c8c3ac1664`. Each run included the two pinned yq binaries, fixture setup scripts and its Ubuntu-specific client packages. The package tests built from the tested source. After verification, only the documentation was edited to record the outcomes.

| Target | Ubuntu | Python | Pass | Fail | Skip | Suite (s) | End to end (s) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| host | 26.04.1 | 3.14.4 | 1,890 | 0 | 1 | 2,452.3 | 2,463.4 |
| noble310 | 24.04.5 | 3.10.20 | 1,890 | 0 | 1 | 2,720.8 | 2,739.5 |
| noble312 | 24.04.5 | 3.12.3 | 1,890 | 0 | 1 | 2,455.0 | 2,469.2 |

All three runs exited zero. The only skip on each target was the Windows-specific probe limitation, because POSIX completed the probe normally. The direct Noble launches initially stopped at `newuidmap` before any test ran. The documented transient user-service launch allowed rootless Podman to start each offline suite. End-to-end times include snapshot creation, fixture setup and preflight. The target logs, `source.sha256` and exact per-target argument lists are under `tests/reports/idle-validation-cc30ade/`. The candidate artifact checksum file and all five entries it covers still matched the original release record. [Sandbox procedure](development.md#isolated-local-debugging) · [Candidate verification and Noble launch method](release-candidate.md#combined-candidate-verification)
