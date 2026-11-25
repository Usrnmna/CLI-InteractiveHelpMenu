# Command menu performance plan

[Runtime architecture and first baseline](runtime-architecture.md#local-performance-baseline) · [FFmpeg manual coverage](ffmpeg-manual-coverage.md)

Stage 1 retained formatting a shared value definition once per menu open. The [Stage 1 evaluation](#stage-1-evaluation) covers the current 76 bundled profiles, custom overrides, discovered help and authoring previews. The earlier FFmpeg measurements below motivated the experiment.

## FFmpeg benchmark evidence

In the original implementation, `Browser.__post_init__` built an `OptionText` for
every row before the first draw. Each value declaration went through structural validation, shared
definition expansion, formatting and prose cleanup. The browser then built
the complete case-folded search string and the Details lines for that row.
This ran for every row even when the pending option already supplied an
initial filter such as `-map`.

| Profile or sample | Rows | Rows with value metadata | Median constructor CPU |
| --- | ---: | ---: | ---: |
| rsync | 216 | 61 | 36 ms |
| FFmpeg, evenly sampled across categories | 216 | 207 | 68 ms |
| FFmpeg, evenly sampled across categories | 880 | 832 | 265 ms |
| FFmpeg, full profile | 1,759 | 1,665 | 522 ms |

The FFmpeg samples retain the full profile's shared definitions. The timings
are medians of 12 warm constructor runs after one warm-up, with JSON already
loaded, on local Ubuntu 26.04.1 with Python 3.14. Within FFmpeg, CPU cost grew
roughly with row count. At the same row count, FFmpeg took about 1.9 times as
long as rsync. Its rows carry more value metadata and longer detail prose.

The call profile recorded 1,665 calls to `format_value_semantics` and 13,061
calls to `concise_description`. A separately instrumented run attributed
about 299 ms of CPU to the value-text path, including about 153 ms for
validation, expansion and formatting and 103 ms for cleaning up that output.
Row-prose cleanup outside that path took about 226 ms. These measurements
include instrumentation overhead. FFmpeg has **1,477 rows whose value
contract is a single shared reference**, reducing to 43 distinct reference
and arity keys. The constructor repeats value-text preparation for each of
those rows. Option-level source notes accounted for about 2 ms in a separate
probe.
[Browser construction](../cli_help/ui.py#L73) · [Presentation](../cli_help/presentation.py#L175) · [Shared-reference validation](../cli_help/value_semantics.py#L484)

## Earlier prototype results

A temporary probe reused the immutable formatted value text for a single
shared reference in one browser construction, keyed by the reference name,
argument count and optionality. The full `OptionText` for each row was still
assembled before the first draw. Every field matched the baseline for all
**4,603 rows across 76 bundled profiles**, including the complete search
string and ordered Details lines. The experiment ran in a temporary Python
wrapper.

| Metric | Stock | Temporary prototype |
| --- | ---: | ---: |
| FFmpeg constructor CPU | 526.0 ms | 289.3 ms |
| FFmpeg unfiltered first frame | 678.6 ms | 444.1 ms |
| FFmpeg with initial `-map` filter, first frame | 679.5 ms | 443.8 ms |
| FFmpeg helper RSS at first frame | 45.6 MiB | 44.9 MiB |
| rsync with initial `--ar` filter, first frame | 191.7 ms | 190.6 ms |

These are single-host medians from 12 paired runs per case after one warm-up.
The terminal pilot used equal Python wrapper overhead on both sides, a
100 × 24 Bash PTY, and the first frame's footer as the output marker.
Its RSS reading was taken at first display. Memory peaks after interaction,
key-to-redraw latency, cold-filesystem behavior and other systems remain
unmeasured. A separate prose-only memoization probe reached about 412 ms of
constructor CPU with a 4,096-entry scratch cache. That makes prose cleanup
a plausible second experiment after the reference reuse.
[PTY fixture](../tests/test_bash_pty.py#L21)

## Implementation stages

### 1. Reuse shared value text within one browser open

- [x] Add targeted tests in `tests/test_numerical_presentation.py`. Two
  rows using the same single reference and arity should invoke the formatter
  once while retaining their own flag labels, source notes and search text.
  Cases with different argument counts or optionality must take their
  applicable validation paths. Cover a missing or cyclic reference, a ref
  with extra fields, and reuse of the same ref name for different definitions
  in two profiles. Reopen a preview after editing a definition and require the
  fresh text.
- [x] In `cli_help/presentation.py`, let `option_text` pass an optional
  `shared_values` mapping to `value_text`. Admit only the exact schema-v1
  contract containing one `{"ref": "<name>"}` variant. Key successful
  `ValueText` results by `(ref, effective_argument_count, value_optional)`.
  Check that the schema version and count are integers and optionality is
  boolean before using the key.
  The existing formatter checks the first occurrence in each context.
  Preserve the existing path for positional metadata, inline or multi-variant
  contracts, malformed shapes and formatter failures. Command and option
  names currently label diagnostics. Keep option-specific source notes and
  prose assembled per row.
- [x] In `cli_help/ui.py`, create and pass the mapping from
  `Browser.__post_init__`. Let it expire when construction ends.
  Keep the full eager search strings and Details lines available before
  drawing. An ordinary startup and an authoring preview each start with
  the definitions from their current profile.
- [x] Before editing runtime code, capture every ordered `OptionText` field
  for every bundled command path. Compare the candidate with that snapshot
  by command, category and row, including complete search strings, Details
  lines, summaries and notices. Compare displayed option labels as well.
  Repeat with fixtures for a custom override, discovered help and an authoring
  preview. Check result order, category counts and selection,
  casefolded and cross-field matches, formatter-only terms, source evidence
  and every Details line at the minimum size. Keep the existing FFmpeg
  terminal case for searching `optional audio`, scrolling to the input
  requirement, cancelling intact and inserting a literal `-map`.
  [Presentation tests](../tests/test_numerical_presentation.py) · [FFmpeg PTY case](../tests/test_expansion_terminal.py#L324)

### Deferred follow-up on prose and redraws

- [ ] Measure the first candidate on its own. If prose preparation still
  dominates startup, test reusing an already-cleaned summary or memoizing
  exact cleanup inputs during construction. Repeat full string parity,
  including punctuation, whitespace and queries spanning old field
  boundaries. Include transient peak RSS in the comparison.
- [ ] If interactive traces identify significant redraw work, measure
  `Browser.options`, `option_label_width` and `wrap_cells` separately.
  Consider retaining category matches for the active query or the wrapped
  Details for the current option and width. Clear matches when the query
  changes and rewrap when the selection or width changes. Measure idle
  redraw suppression separately and retain geometry polling and resize
  recovery. These follow-ups are independently testable.
- [ ] Keep the first experiment confined to presentation and browser
  construction. Treat selective profile loading, a persistent index, or
  additional processes as separate architecture proposals.

## Before-and-after measurement

**Every bundled menu.** With its profile already loaded, time construction of
a fresh `Browser` using process CPU time. For each command path, report row
count, eligible reference uses, distinct reference-and-arity keys, and
baseline and candidate CPU times with their difference. Include paths with
zero eligible rows so the report exposes the cost of checking eligibility.

**Representative terminal sessions.** Use FFmpeg for the large menu, plus
a small bundled menu, rsync and fzf. Include menus with few or zero repeated
keys, a custom profile and a discovered profile. For discovery, use fixed
help fixtures and measure a cache miss and a valid cache hit independently.
Exercise the same preview fixture before and after a definition edit for
correctness. Apply the terminal measurements below to the selected PTY cases.

Run baseline and candidate with identical profile and fixture bytes. Record
revision and profile hashes, host and interpreter versions, terminal size,
locale, and discovery settings. Use an isolated Bash setup with discovery
off for static cases. Warm the filesystem once for each revision, start a
fresh helper per invocation, alternate revision order, and collect at least
40 measured samples per revision for each primary case. Save raw samples and
report median and p95 by command path, revision and scenario. Repeat the comparison if run-to-run
variation overlaps the observed change.

| Measure | Start and end points |
| --- | --- |
| Startup | From writing Alt-H to observing the complete first menu in decoded PTY cells, including the expected selection and Details footer. Use unfiltered and filtered openings, including FFmpeg with initial `-map` and `-rw_timeout`. Record CPU for profile loading, context resolution, constructor and first draw in a separate instrumented run. |
| RAM | Record the Python helper's `VmRSS` and `VmHWM` from `/proc/<pid>/status` after the first frame, after a full search and navigation script, and immediately before dismissal. Record RSS again after returning to a short query. Report the initial and idle RSS and the highest observed high-water mark. Measure startup and sustained interaction separately from profiler runs. |
| Responsiveness | From sending a key or terminal resize to the first decoded screen that reflects the expected state. Measure first search, repeated search, a no-match query, a formatter-only term such as `'ms'`, category and row movement, Details scrolling, and shrink to 60 × 16 then grow to 100 × 24. Measure keys individually and replay a rapid sequence that must end in the same state. |
| Idle work | Over a matched 10-second interval with the menu open, record helper user and system CPU from `/proc/<pid>/stat`, voluntary context-switch delta and draw count in a separately instrumented run. Use idle measurement to assess redraw follow-ups. |

Reuse the PTY fixture and terminal-cell decoder for timing. Timestamp with a
monotonic clock before each write and after decoding each output chunk. The
tmux tests remain the independent correctness check for resize, cancellation
and scrollback. Their stability wait would dominate a latency measurement.
For cold-start testing, use the same isolated VM or dedicated machine
with a documented cache-reset procedure for both revisions. Keep those
results separate from warm local runs.
[Bash PTY fixture](../tests/test_bash_pty.py#L21) · [Terminal-cell decoder](../tools/capture_readme_media.py#L51) · [tmux screen checks](../tests/test_terminal_screen.py#L40)

Use **30% lower FFmpeg median first-frame time** on the warm PTY cases as a
proposed target for the large-menu benchmark, with improved FFmpeg p95.
Require exact correctness parity for all menus. Review constructor CPU
changes per command, including slowdowns. Investigate a control or interaction p95 regression
larger than the greater of 5 ms or 10%, or a helper RSS or high-water
regression larger than the greater of 2 MiB or 5%, over repeated matched runs.
These are review thresholds based on the pilot and expected measurement
noise. Run the presentation, numerical semantics, FFmpeg inventory and PTY
tests before expanding to the project's normal compatibility matrix.
[Local sandbox and supported test targets](development.md#isolated-local-debugging)

## Stage 1 evaluation

**Retain the per-open reuse for the v0.4.0-alpha candidate.** The three warm FFmpeg opens saved 233–237 ms at the median (31.0–31.5%), with improved p95 and exact parity. The largest primary control p95 increase was 4.37 ms for rsync, with a 2.22 ms increase on the repeat. The largest increase in median checkpoint RSS across the primary and repeated controls was 0.055 MiB after navigation on a discovery miss. Both are below the investigation thresholds. These results support shipping the first performance-plan step. The [release guide](releases.md#version-040---alpha) describes the subsequently prepared local candidate. [Version protocol](versioning.md#proposed-targets)

The baseline was the clean working tree at `2797f1ceb35bca4cfc2cc4a590158720584068fc`. Its 989 tracked files were copied from disk before the runtime edits. The profile set contains 6,487 rows across 76 command paths. SHA-256 of the sorted compact JSON mapping from file path to file-content SHA-256 was `97dda0651ce09e5b0209e2b3ce6842cf5d360bf2f54fd9c5180d50e53269dcb9` for the 76 profiles and `b8b29b115026c5626e19c2d3c501d09350875083d7413fb0e3508bbde1855a7b` for the 533 tracked files under `tests/fixtures/`. The FFmpeg profile itself had digest `b03e892648cfea2ed17d7cdfb7328e7a98a0923ece91092240ff90676d2bb9a4`.

| Runtime source | Baseline SHA-256 | Candidate SHA-256 |
| --- | --- | --- |
| `cli_help/presentation.py` | `f5297e1faf165cfba2b9d9fcda78c323ea1a5e50471f34aa23e0002fd0cc3a6c` | `adb5ddc8fc69af1ea9dd48e161c35718e15cfdcce300e5353ea0c2eced6a4204` |
| `cli_help/ui.py` | `d5ee8645d8f4f8a86690c9184d94dcc7bad84802033d540e738418e4f7b25c0c` | `71b43fbe53f4f3ec7fc3dccc08b9faf4f7dfae1ef91741d9f855314a23047ad6` |

### Correctness

Every bundled row retained its label, compact text, summary, notice, hint, complete case-folded search string and ordered Details. The same comparison covered two custom override rows, eight rows parsed from fixed help and manual text, and both rows of an authoring preview before and after editing its definition. The capture drove the draw code through every Details page at 60 × 16. The 6,501 rows contained 69,501 wrapped Details lines. A separate check reconstructed every expected page from the saved Details paragraphs and compared it to the captured cells. Eight filter transitions per menu (640 observations) recorded all categories’ ordered matches and the active category and row, including uppercase, cross-field, formatter-only, source and no-match queries. Both 14,934,300-byte captures had SHA-256 `4b4ee0123074c442d34046ef2118345cc5fbed1a6dd9e9b579e4031356edf4e6`. These all-row comparisons used a cell-recording window. The independent FFmpeg Bash/tmux check searched for “optional audio”, scrolled to the input requirement, cancelled with the pending line and cursor intact, then checked literal insertion before the output operand.

A browser-local dictionary holds successful immutable `ValueText` objects only while preparing the rows. It accepts one schema-v1 reference and keys it by name, effective argument count and boolean optionality. Each distinct context goes through the original formatter. Row summaries, evidence, warnings and search strings are assembled separately. New regressions count formatter calls, compare invalid and ineligible cases against uncached output, and reopen independently defined and edited previews. The numerical gate initially flagged the two protected runtime source digests. Review confirmed the only source changes were the bounded lookup in presentation and its per-construction owner in the UI. Both source pins were refreshed.

### Time to the first complete frame

Each row uses 40 measured opens per revision with the normal system standard-library bytecode and matched source trees. Times include decoding. p95 is the nearest-rank 38th observation. Positive reduction means a faster median.

| Open | Before median (ms) | After median (ms) | Median reduction | Before p95 (ms) | After p95 (ms) |
| --- | --- | --- | --- | --- | --- |
| FFmpeg unfiltered | 749.5 | 516.1 | +31.1% | 761.4 | 527.3 |
| FFmpeg `-map` | 752.3 | 515.1 | +31.5% | 763.4 | 539.5 |
| FFmpeg `-rw_timeout` | 752.5 | 519.0 | +31.0% | 769.0 | 534.2 |
| rsync `--ar` | 256.4 | 257.5 | -0.4% | 261.8 | 266.1 |
| fzf | 255.6 | 255.6 | 0.0% | 262.1 | 261.6 |
| git worktree remove | 221.1 | 221.5 | -0.2% | 233.8 | 227.9 |
| Custom rsync | 222.3 | 221.2 | +0.5% | 230.0 | 230.4 |
| Discovery miss | 261.6 | 262.8 | -0.5% | 267.1 | 268.8 |
| Discovery hit | 220.6 | 220.2 | +0.2% | 226.0 | 224.6 |

The smaller effects on controls warranted an independent second block of 40 pairs per case. Cells give before / after, in ms.

| Repeated control | Median | p95 |
| --- | --- | --- |
| rsync `--ar` | 256.5 / 256.2 | 260.2 / 262.4 |
| fzf | 254.9 / 255.4 | 264.2 / 262.0 |
| git worktree remove | 218.8 / 219.3 | 226.8 / 223.1 |
| Custom rsync | 220.1 / 220.3 | 226.0 / 224.9 |
| Discovery miss | 260.7 / 261.1 | 269.4 / 268.0 |
| Discovery hit | 220.7 / 219.7 | 224.2 / 223.3 |

A separate 40-pair sensitivity run redirected Python’s bytecode cache to a fresh private prefix. The helper disables bytecode writes before importing most modules. Startup overhead therefore differed from the normal system-library run. This measured setup missed the 30% median target, with improved p95 in all three FFmpeg scenarios. Filesystem reads remained warm.

| Private prefix | Median before / after (ms) | p95 before / after (ms) | Median reduction |
| --- | --- | --- | --- |
| FFmpeg unfiltered | 894.2 / 657.6 | 924.3 / 677.2 | 26.5% |
| FFmpeg `-map` | 776.6 / 544.2 | 798.7 / 563.4 | 29.9% |
| FFmpeg `-rw_timeout` | 771.9 / 541.4 | 794.5 / 551.7 | 29.9% |

### Interaction latency

Each cell gives before median/p95 → after median/p95 in ms over the primary 40 pairs. The rapid sequence typed the formatter-only term `'ms'` without intermediate waits. A dash marks a transition that could not change the visible cells in that scenario.

| Input | FFmpeg unfiltered | FFmpeg `-map` | FFmpeg `-rw_timeout` |
| --- | --- | --- | --- |
| search | 1.6/1.8 → 1.6/1.8 | 2.1/2.3 → 2.1/2.2 | 1.8/2.0 → 1.9/2.1 |
| first key | 1.5/1.8 → 1.5/2.0 | 1.5/1.7 → 1.5/1.7 | 2.0/2.3 → 2.1/2.4 |
| second key | 3.4/3.6 → 3.4/4.0 | 3.4/3.5 → 3.4/3.7 | 3.1/3.6 → 3.1/3.5 |
| no match | 3.7/4.0 → 3.7/4.0 | 3.7/3.9 → 3.7/4.0 | 4.0/4.3 → 4.0/4.4 |
| clear long | 2.9/3.2 → 2.9/3.0 | 2.9/3.0 → 2.9/3.1 | 3.6/3.9 → 3.6/4.2 |
| rapid formatter | 5.5/7.1 → 5.5/7.0 | 5.6/7.1 → 5.5/6.2 | 5.0/6.8 → 5.0/5.8 |
| clear formatter | 2.8/3.1 → 2.8/3.0 | 2.8/3.3 → 2.9/3.1 | 3.5/3.8 → 3.5/3.7 |
| short query | 1.5/1.6 → 1.5/1.6 | 1.5/1.6 → 1.5/1.6 | 2.0/2.3 → 2.0/2.2 |
| clear short | 1.4/1.5 → 1.4/1.6 | 1.4/1.5 → 1.4/1.6 | 1.9/2.1 → 1.9/2.0 |
| apply | 1.4/1.5 → 1.4/1.5 | 1.4/1.5 → 1.4/1.5 | 1.9/2.1 → 1.9/2.1 |
| row in current category | 3.2/3.3 → 3.2/3.4 | 3.2/3.5 → 3.2/3.5 | 3.0/3.1 → 3.0/3.4 |
| next category | 2.9/3.2 → 2.9/3.1 | 3.0/3.2 → 2.9/3.1 | 3.4/3.7 → 3.4/3.6 |
| next row | 2.2/2.4 → 2.3/2.5 | 2.3/2.5 → 2.3/2.4 | 2.9/3.2 → 2.9/3.2 |
| shrink | 1.9/2.0 → 1.9/2.0 | 1.9/2.1 → 1.9/2.1 | 2.1/2.3 → 2.1/2.5 |
| scroll | 1.1/1.1 → 1.1/1.1 | 1.1/1.1 → 1.1/1.1 | 1.3/1.4 → 1.3/1.3 |
| grow | 3.5/3.7 → 3.5/3.7 | 3.5/3.7 → 3.5/3.6 | 3.9/4.3 → 3.9/4.3 |
| clear | — | 2.9/3.1 → 2.9/3.3 | 3.5/3.7 → 3.5/3.7 |

| Input | rsync `--ar` | fzf | git worktree remove |
| --- | --- | --- | --- |
| search | 1.4/1.6 → 1.4/1.6 | 1.8/2.1 → 1.8/2.1 | 1.2/1.5 → 1.2/1.6 |
| first key | 1.4/2.2 → 1.4/2.2 | 1.8/2.4 → 1.7/2.4 | 1.1/1.5 → 1.1/1.2 |
| second key | 2.4/2.5 → 2.4/2.7 | 2.6/2.8 → 2.6/3.1 | 1.8/2.0 → 1.8/2.1 |
| no match | 2.1/2.1 → 2.1/2.3 | 2.2/2.3 → 2.2/2.5 | 1.0/1.2 → 0.9/1.1 |
| clear long | 2.6/2.7 → 2.6/2.8 | 3.1/3.4 → 3.1/3.5 | 2.2/2.5 → 2.2/2.5 |
| rapid formatter | 4.9/5.3 → 4.9/6.3 | 3.7/4.1 → 3.7/4.6 | 1.9/2.4 → 1.9/2.2 |
| clear formatter | 2.8/3.1 → 2.9/3.0 | 3.1/3.2 → 3.1/3.2 | 2.2/2.4 → 2.2/2.4 |
| short query | 1.4/1.6 → 1.5/1.6 | 1.6/2.0 → 1.6/1.8 | 1.1/1.4 → 1.1/1.2 |
| clear short | 1.4/1.5 → 1.4/1.6 | 1.6/1.6 → 1.6/1.7 | 1.1/1.2 → 1.1/1.2 |
| apply | 1.4/1.5 → 1.4/1.5 | 1.6/1.7 → 1.6/1.7 | 1.1/1.3 → 1.1/1.2 |
| row in current category | 2.3/2.5 → 2.3/2.6 | 2.3/2.4 → 2.3/2.4 | 1.9/2.1 → 1.9/2.2 |
| next category | 3.1/3.3 → 3.2/3.6 | 2.7/2.8 → 2.7/3.2 | — |
| next row | 2.4/2.7 → 2.4/2.6 | 2.1/2.3 → 2.1/2.3 | 2.1/2.3 → 2.1/2.4 |
| shrink | 1.7/2.1 → 1.7/1.9 | 1.8/1.9 → 1.8/2.0 | 1.7/1.9 → 1.7/1.8 |
| scroll | 1.0/1.1 → 1.0/1.1 | 1.0/1.1 → 1.1/1.1 | 1.0/1.0 → 1.0/1.0 |
| grow | 3.3/3.4 → 3.3/3.6 | 3.2/3.5 → 3.3/3.5 | 2.6/3.3 → 2.6/2.7 |
| clear | 2.3/2.4 → 2.3/2.4 | — | — |

| Input | Custom rsync | Discovery miss | Discovery hit |
| --- | --- | --- | --- |
| search | 1.3/1.5 → 1.3/1.3 | 1.2/1.3 → 1.2/1.3 | 1.2/1.3 → 1.2/1.3 |
| first key | 1.2/1.3 → 1.2/1.3 | 1.1/1.2 → 1.1/1.3 | 1.1/1.2 → 1.1/1.3 |
| second key | 2.2/2.4 → 2.2/2.5 | 1.9/2.2 → 1.9/1.9 | 1.9/2.0 → 1.9/2.0 |
| no match | 1.1/1.3 → 1.1/1.3 | 1.0/1.0 → 1.0/1.0 | 1.0/1.0 → 1.0/1.0 |
| clear long | 2.3/2.5 → 2.3/2.7 | 2.1/2.2 → 2.1/2.2 | 2.1/2.2 → 2.1/2.2 |
| rapid formatter | 3.0/3.6 → 3.0/3.4 | 2.0/2.6 → 2.0/2.6 | 2.0/2.7 → 2.0/2.7 |
| clear formatter | 2.3/2.4 → 2.3/2.5 | 2.1/2.2 → 2.1/2.2 | 2.1/2.2 → 2.1/2.2 |
| short query | 1.2/1.3 → 1.2/1.4 | 1.1/1.1 → 1.1/1.2 | 1.1/1.2 → 1.1/1.2 |
| clear short | 1.1/1.2 → 1.1/1.2 | 1.1/1.1 → 1.1/1.2 | 1.1/1.1 → 1.1/1.3 |
| apply | 1.1/1.2 → 1.1/1.3 | 1.1/1.1 → 1.1/1.1 | 1.1/1.1 → 1.1/1.1 |
| row in current category | 2.0/2.2 → 2.0/2.3 | 2.0/2.2 → 2.0/2.1 | 2.0/2.3 → 2.0/2.3 |
| next category | — | 2.0/2.3 → 1.9/2.1 | 1.9/2.1 → 1.9/2.1 |
| next row | — | — | — |
| shrink | 1.7/1.9 → 1.6/2.0 | 1.4/1.5 → 1.4/1.5 | 1.4/1.5 → 1.4/1.6 |
| scroll | 1.0/1.1 → 1.0/1.0 | — | — |
| grow | 2.7/2.8 → 2.6/2.7 | 2.3/2.4 → 2.3/2.4 | 2.3/2.5 → 2.3/2.4 |
| clear | — | 2.1/2.3 → 2.1/2.3 | 2.1/2.2 → 2.1/2.2 |

### Helper memory and idle work

Memory is in MiB, before / after. RSS columns use the primary median. The last column gives the maximum kernel high-water mark across all 40 helpers at dismissal, including peaks between samples. The one-character query followed a longer search. The last resize completed the navigation script immediately before dismissal.

| Scenario | First RSS | Short query RSS | Post-navigation RSS | Pre-dismiss RSS | Highest VmHWM |
| --- | --- | --- | --- | --- | --- |
| FFmpeg unfiltered | 52.49 / 51.83 | 52.50 / 51.83 | 52.52 / 51.87 | 52.52 / 51.87 | 52.67 / 52.02 |
| FFmpeg `-map` | 52.49 / 51.83 | 52.49 / 51.83 | 52.51 / 51.84 | 52.51 / 51.84 | 52.65 / 52.02 |
| FFmpeg `-rw_timeout` | 52.50 / 51.87 | 52.50 / 51.87 | 52.50 / 51.87 | 52.50 / 51.87 | 52.65 / 51.96 |
| rsync `--ar` | 47.19 / 47.23 | 47.19 / 47.23 | 47.23 / 47.23 | 47.23 / 47.23 | 47.35 / 47.32 |
| fzf | 47.19 / 47.20 | 47.19 / 47.20 | 47.22 / 47.23 | 47.22 / 47.23 | 47.30 / 47.30 |
| git worktree remove | 47.00 / 46.97 | 47.00 / 46.97 | 47.02 / 47.00 | 47.02 / 47.00 | 47.15 / 47.15 |
| Custom rsync | 46.76 / 46.78 | 46.76 / 46.78 | 46.76 / 46.78 | 46.76 / 46.78 | 46.96 / 46.89 |
| Discovery miss | 47.19 / 47.22 | 47.19 / 47.22 | 47.19 / 47.22 | 47.19 / 47.22 | 47.33 / 47.33 |
| Discovery hit | 47.13 / 47.12 | 47.13 / 47.12 | 47.13 / 47.12 | 47.13 / 47.12 | 47.25 / 47.25 |

Each idle reading spans ten seconds after the first frame. CPU is in 10 ms scheduler ticks. Switches are voluntary. The draw count comes from a separate instrumented ten-second open. The final column counts completed draws during that interval.

| Scenario | User ticks | System ticks | Switches | Idle RSS (MiB) | Draws |
| --- | --- | --- | --- | --- | --- |
| FFmpeg unfiltered | 6 / 6 | 0 / 0 | 66 / 66 | 52.50 / 51.82 | 66 / 66 |
| FFmpeg `-map` | 9 / 8 | 0 / 0 | 66 / 66 | 52.37 / 51.83 | 66 / 66 |
| FFmpeg `-rw_timeout` | 7 / 8 | 0 / 1 | 66 / 66 | 52.56 / 51.74 | 66 / 66 |
| rsync `--ar` | 4 / 5 | 0 / 0 | 66 / 66 | 47.31 / 47.31 | 66 / 66 |
| fzf | 7 / 7 | 0 / 0 | 66 / 66 | 47.16 / 47.24 | 66 / 66 |
| git worktree remove | 3 / 3 | 0 / 0 | 66 / 66 | 46.95 / 46.94 | 66 / 66 |
| Custom rsync | 3 / 3 | 1 / 0 | 66 / 66 | 46.78 / 46.58 | 66 / 66 |
| Discovery miss | 2 / 2 | 0 / 0 | 66 / 66 | 47.14 / 47.20 | 66 / 66 |
| Discovery hit | 2 / 2 | 0 / 0 | 66 / 66 | 47.00 / 47.09 | 66 / 66 |

### Instrumented first-frame phases

Process CPU in ms, before / after, from individual fresh instrumented helpers. Context CPU includes in-process discovery work and excludes CPU used by child probes. These phase timings exclude Bash, interpreter startup and PTY decoding.

| Scenario | Load profiles | Resolve context | Build browser | First draw |
| --- | --- | --- | --- | --- |
| FFmpeg unfiltered | 112.81 / 115.72 | 0.52 / 0.52 | 524.98 / 295.50 | 0.99 / 0.94 |
| FFmpeg `-map` | 112.63 / 116.65 | 0.62 / 0.63 | 525.79 / 296.60 | 1.42 / 1.35 |
| FFmpeg `-rw_timeout` | 114.91 / 115.44 | 0.68 / 0.63 | 532.20 / 292.08 | 1.15 / 1.10 |
| rsync `--ar` | 115.73 / 114.58 | 0.39 / 0.33 | 38.10 / 37.64 | 0.73 / 0.68 |
| fzf | 113.47 / 112.35 | 0.26 / 0.25 | 36.13 / 35.91 | 1.16 / 1.05 |
| git worktree remove | 114.45 / 114.22 | 0.26 / 0.27 | 0.94 / 0.94 | 0.48 / 0.47 |
| Custom rsync | 114.44 / 114.02 | 0.20 / 0.21 | 1.36 / 1.18 | 0.51 / 0.51 |
| Discovery miss | 115.29 / 113.17 | 5.39 / 5.77 | 1.10 / 1.09 | 0.42 / 0.40 |
| Discovery hit | 114.21 / 118.26 | 0.65 / 0.66 | 1.28 / 1.13 | 0.46 / 0.39 |

### Constructor CPU by bundled path

The median of 12 paired sweeps covers fresh browser construction with the validated profile already in memory. Each revision used a separate interpreter per sweep. The timer excluded garbage collection before construction and destruction afterward. Across all 76 paths, 2,044 eligible rows reduced to 306 per-menu keys. The 38 paths with no eligible rows are included. FFmpeg saved 234.01 ms of constructor CPU (44.4%). Go test, OpenSSL x509 and journalctl each saved about 4 ms. Twenty-two paths measured slightly slower, with a maximum increase of 0.14 ms for grep. A positive delta denotes a slowdown.

| Command | Rows | Eligible uses | Distinct keys | Before (ms) | After (ms) | Δ ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `7z x` | 57 | 0 | 0 | 13.21 | 13.16 | -0.05 |
| `7zz x` | 57 | 0 | 0 | 12.19 | 12.17 | -0.02 |
| `ansible-playbook` | 61 | 22 | 14 | 11.63 | 10.48 | -1.15 |
| `arduino-cli compile` | 50 | 10 | 5 | 10.40 | 9.69 | -0.71 |
| `az account show` | 12 | 0 | 0 | 2.50 | 2.51 | +0.01 |
| `az storage blob list` | 24 | 0 | 0 | 5.63 | 5.64 | +0.01 |
| `az vm list` | 14 | 0 | 0 | 2.61 | 2.62 | +0.01 |
| `bun run` | 121 | 4 | 2 | 18.54 | 18.36 | -0.18 |
| `dotnet build` | 59 | 0 | 0 | 12.56 | 12.58 | +0.02 |
| `dotnet publish` | 51 | 0 | 0 | 11.21 | 11.14 | -0.07 |
| `dotnet restore` | 41 | 0 | 0 | 8.58 | 8.54 | -0.04 |
| `dotnet run` | 39 | 0 | 0 | 9.62 | 9.43 | -0.19 |
| `dotnet test` | 52 | 0 | 0 | 12.00 | 11.85 | -0.15 |
| `esptool write-flash` | 27 | 4 | 2 | 11.86 | 11.48 | -0.38 |
| `esptool.py write-flash` | 27 | 4 | 2 | 11.85 | 11.42 | -0.43 |
| `esptool.py write_flash` | 23 | 4 | 2 | 10.92 | 10.36 | -0.56 |
| `fd` | 98 | 24 | 10 | 19.38 | 16.77 | -2.61 |
| `fdfind` | 98 | 24 | 10 | 19.44 | 17.02 | -2.42 |
| `ffmpeg` | 1759 | 1477 | 43 | 526.77 | 292.76 | -234.01 |
| `fzf` | 209 | 2 | 1 | 34.99 | 34.69 | -0.30 |
| `gcloud compute instances list` | 26 | 0 | 0 | 5.68 | 5.74 | +0.06 |
| `gcloud config list` | 22 | 0 | 0 | 4.57 | 4.61 | +0.05 |
| `gcloud storage ls` | 43 | 0 | 0 | 6.71 | 6.78 | +0.07 |
| `git commit` | 98 | 12 | 5 | 13.05 | 11.97 | -1.08 |
| `git log` | 234 | 16 | 8 | 35.41 | 33.98 | -1.43 |
| `git stash` | 37 | 3 | 2 | 4.61 | 4.38 | -0.23 |
| `git stash apply` | 8 | 0 | 0 | 1.31 | 1.32 | +0.01 |
| `git stash list` | 201 | 18 | 9 | 31.71 | 30.07 | -1.64 |
| `git stash pop` | 5 | 0 | 0 | 0.52 | 0.53 | +0.01 |
| `git stash push` | 24 | 3 | 2 | 3.37 | 3.20 | -0.17 |
| `git stash show` | 112 | 12 | 6 | 17.94 | 16.93 | -1.01 |
| `git worktree` | 9 | 0 | 0 | 0.88 | 0.88 | -0.00 |
| `git worktree add` | 20 | 0 | 0 | 2.46 | 2.46 | +0.00 |
| `git worktree list` | 7 | 0 | 0 | 1.14 | 1.15 | +0.01 |
| `git worktree prune` | 7 | 0 | 0 | 1.00 | 1.00 | -0.00 |
| `git worktree remove` | 3 | 0 | 0 | 0.37 | 0.37 | -0.00 |
| `go build` | 33 | 0 | 0 | 6.89 | 6.92 | +0.03 |
| `go mod tidy` | 10 | 0 | 0 | 1.82 | 1.82 | -0.00 |
| `go run` | 33 | 0 | 0 | 6.94 | 6.98 | +0.04 |
| `go test` | 95 | 46 | 23 | 23.27 | 19.03 | -4.24 |
| `grep` | 48 | 0 | 0 | 8.49 | 8.64 | +0.14 |
| `ip address` | 47 | 0 | 0 | 9.16 | 9.23 | +0.07 |
| `ip link` | 13 | 0 | 0 | 2.84 | 2.87 | +0.03 |
| `ip route` | 30 | 0 | 0 | 9.12 | 9.16 | +0.04 |
| `journalctl` | 100 | 44 | 22 | 25.86 | 21.73 | -4.13 |
| `ls` | 60 | 0 | 0 | 17.49 | 17.37 | -0.12 |
| `openssl dgst` | 56 | 23 | 2 | 12.32 | 8.60 | -3.72 |
| `openssl s_client` | 210 | 0 | 0 | 35.59 | 35.57 | -0.02 |
| `openssl x509` | 104 | 25 | 2 | 21.26 | 17.10 | -4.15 |
| `pio device monitor` | 25 | 7 | 5 | 5.40 | 5.05 | -0.36 |
| `pio run` | 24 | 7 | 4 | 4.91 | 4.47 | -0.44 |
| `platformio device monitor` | 25 | 7 | 5 | 5.43 | 5.04 | -0.39 |
| `platformio run` | 24 | 7 | 4 | 4.90 | 4.43 | -0.47 |
| `podman build` | 134 | 16 | 8 | 30.00 | 28.39 | -1.61 |
| `podman exec` | 23 | 6 | 3 | 5.07 | 4.26 | -0.81 |
| `podman logs` | 14 | 0 | 0 | 2.25 | 2.26 | +0.01 |
| `podman run` | 168 | 22 | 11 | 44.79 | 42.06 | -2.73 |
| `psql` | 70 | 22 | 11 | 11.25 | 9.48 | -1.77 |
| `pytest` | 121 | 8 | 4 | 17.48 | 17.00 | -0.48 |
| `rsync` | 216 | 0 | 0 | 36.63 | 36.60 | -0.03 |
| `ruff check` | 60 | 2 | 1 | 9.20 | 9.01 | -0.19 |
| `ruff format` | 32 | 0 | 0 | 5.40 | 5.45 | +0.05 |
| `scp` | 24 | 0 | 0 | 4.78 | 4.78 | -0.00 |
| `sftp` | 26 | 0 | 0 | 5.44 | 5.42 | -0.02 |
| `ss` | 85 | 0 | 0 | 10.96 | 10.99 | +0.03 |
| `ssh` | 46 | 0 | 0 | 11.15 | 11.13 | -0.02 |
| `systemctl list-units` | 38 | 18 | 9 | 8.69 | 7.03 | -1.66 |
| `systemctl show` | 41 | 19 | 9 | 9.37 | 7.53 | -1.84 |
| `systemctl status` | 37 | 16 | 8 | 8.57 | 6.96 | -1.62 |
| `tar` | 157 | 0 | 0 | 23.09 | 23.21 | +0.12 |
| `uv add` | 113 | 27 | 12 | 22.41 | 19.94 | -2.47 |
| `uv lock` | 76 | 19 | 9 | 15.94 | 13.96 | -1.98 |
| `uv sync` | 110 | 19 | 9 | 20.81 | 19.35 | -1.46 |
| `uv tool install` | 98 | 31 | 15 | 21.10 | 18.72 | -2.38 |
| `uv venv` | 57 | 14 | 7 | 11.30 | 10.08 | -1.22 |
| `yq eval` | 69 | 0 | 0 | 11.52 | 11.64 | +0.12 |

### Full offline verification

The focused host run passed all 80 presentation, numerical semantics, FFmpeg inventory and minimum-size terminal checks. The strict numerical gate passed. The three full suites then ran concurrently after the performance measurements, from the same 993 source inputs plus each target’s package fixtures. The source manifest SHA-256 was `522c575bda21eba42212925509124568ed3c978e89a0f60b2a733ff195e49ab5`. All 1,880 discovered IDs matched the start and end events in order on each target. Each run skipped the Windows-only probe check on Linux. Elapsed times include snapshot creation, sandbox startup, fixture setup, preflight and the suite.

| Target | Ubuntu | Python | Passed | Failed | Skipped | Elapsed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| host | 26.04.1 LTS | 3.14.4 | 1,879 | 0 | 1 | 2,509.78 s |
| noble310 | 24.04.5 LTS | 3.10.20 | 1,879 | 0 | 1 | 2,788.76 s |
| noble312 | 24.04.5 LTS | 3.12.3 | 1,879 | 0 | 1 | 2,514.29 s |

For a full local run before the new files are tracked, add one `--include` per file in `tools/menu_benchmark/` to the documented package-fixture command. The local evidence directory retains each target’s exact argv, fixture digests, transcript, wall time and verification result. Performance was measured on the host. The Noble runs establish compatibility.

### Reproduce the comparison

Use two source directories named `before` and `after` inside a fresh local report directory. The commands below assume the current candidate has all of its runtime files in the index or already tracked. Include additional untracked runtime files explicitly for other experiments. For this clean baseline, the commit archive reproduces the tracked input bytes. For a dirty baseline, copy the working tree before editing. Snapshot the candidate from disk too. Keep both trees free of project bytecode caches. Run the examples from the repository root in Bash. The PTY controller uses the optional media decoder dependencies. [Media capture dependencies](../tools/requirements-media.txt) · [Sandbox matrix and package fixtures](test-selection-plan.md#reproduce-the-paired-offline-baseline)

```bash
export MENU_BENCH_DIR
MENU_BENCH_DIR=$(mktemp -d "$PWD/tests/reports/menu-stage1-XXXXXXXX")
mkdir "$MENU_BENCH_DIR"/{before,after}
git archive 2797f1ceb35bca4cfc2cc4a590158720584068fc | tar -x -C "$MENU_BENCH_DIR/before"
git ls-files --cached --deduplicate -z | tar --null -T - -cf - | tar -x -C "$MENU_BENCH_DIR/after"

for rev in before after; do
    python3 -B tools/menu_benchmark/parity.py "$MENU_BENCH_DIR/$rev" > "$MENU_BENCH_DIR/$rev.jsonl"
done
cmp "$MENU_BENCH_DIR"/{before,after}.jsonl
python3 -B tools/menu_benchmark/constructor.py > "$MENU_BENCH_DIR/cpu.jsonl"
python3 -B tools/menu_benchmark/terminal.py 40 > "$MENU_BENCH_DIR/warm.jsonl"
python3 -B tools/menu_benchmark/terminal.py 40 rsync fzf small custom miss hit > "$MENU_BENCH_DIR/controls-repeat.jsonl"
STAGE1_IDLE=1 python3 -B tools/menu_benchmark/terminal.py 1 > "$MENU_BENCH_DIR/idle.jsonl"
STAGE1_IDLE=1 STAGE1_INSTRUMENT=1 python3 -B tools/menu_benchmark/terminal.py 1 > "$MENU_BENCH_DIR/instrumented.jsonl"
```

[All-row parity recorder](../tools/menu_benchmark/parity.py) · [Constructor sweep](../tools/menu_benchmark/constructor.py) · [Terminal benchmark](../tools/menu_benchmark/terminal.py) · [Phase and draw instrumentation](../tools/menu_benchmark/instrument.py)

The local evidence directory is `tests/reports/stage1-2797f1c/`. It contains both source snapshots, the baseline file manifest, raw paired measurements, separate instrumented traces and parity captures. Measurements used Ubuntu 26.04.1 LTS, an AMD Ryzen Threadripper 3970X, Bash 5.3.9, Python 3.14.4, C.UTF-8, xterm-256color and the pyte 0.8.2 decoder. Each pair alternated launch order after a discarded warm-up on both revisions. Each Alt-H started a fresh helper. Static cases disabled discovery. Discovery cases used the same fixed executables and separately verified a probe on each miss and its absence on each valid hit. The terminal benchmark compares the entire decoded screen, including the selected row and footer, against the baseline draw. The pending lines and cursors were checked after dismissal and the execution markers stayed absent. Filesystem reads were warm. Cold-filesystem behavior remains unmeasured.
