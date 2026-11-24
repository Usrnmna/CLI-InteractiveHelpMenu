# FFmpeg menu performance plan

[Runtime architecture and first baseline](runtime-architecture.md#local-performance-baseline) · [FFmpeg manual coverage](ffmpeg-manual-coverage.md)

## Why preparation takes about half a second

Before the first draw, `Browser.__post_init__` builds an `OptionText` for
every row. Each value declaration goes through structural validation, shared
definition expansion, formatting and prose cleanup. The browser then builds
the complete case-folded search string and the Details lines for that row.
This runs for every row even when the pending option already supplies an
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

## Temporary reuse experiment

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

- [ ] Add targeted tests in `tests/test_numerical_presentation.py`. Two
  rows using the same single reference and arity should invoke the formatter
  once while retaining their own flag labels, source notes and search text.
  Cases with different argument counts or optionality must take their
  applicable validation paths. Cover a missing or cyclic reference, a ref
  with extra fields, and reuse of the same ref name for different definitions
  in two profiles. Reopen a preview after editing a definition and require the
  fresh text.
- [ ] In `cli_help/presentation.py`, let `option_text` pass an optional
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
- [ ] In `cli_help/ui.py`, create and pass the mapping from
  `Browser.__post_init__`. Let it expire when construction ends.
  Keep the full eager search strings and Details lines available before
  drawing. An ordinary startup and an authoring preview each start with
  the definitions from their current profile.
- [ ] Capture exact ordered `OptionText` parity for the same bundled
  corpus on baseline and candidate, through a temporary comparison harness.
  Exercise custom and discovered profile fixtures using the focused
  presentation tests. Check result order, category counts and selection,
  casefolded and cross-field matches, formatter-only terms, source evidence
  and every Details line at the minimum size. Keep the existing FFmpeg
  terminal case for searching `optional audio`, scrolling to the input
  requirement, cancelling intact and inserting a literal `-map`.
  [Presentation tests](../tests/test_numerical_presentation.py) · [FFmpeg PTY case](../tests/test_expansion_terminal.py#L324)

### 2. Profile the remaining prose and redraw work

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

Run baseline and candidate with identical profile and fixture bytes. Record
revision and profile hashes, host and interpreter versions, terminal size,
locale, and discovery settings. Use an isolated Bash setup with discovery
off for static cases. Warm the filesystem once for each revision, start a
fresh helper per invocation, alternate revision order, and collect at least
40 measured samples per primary case. Save raw samples and report median
and p95 by revision and scenario. Repeat the comparison if run-to-run
variation overlaps the observed change.

| Measure | Start and end points |
| --- | --- |
| Startup | From writing Alt-H to observing the complete first menu in decoded PTY cells, including the expected selection and Details footer. Test unfiltered FFmpeg, initial `-map`, and a narrow match such as `-rw_timeout`, plus rsync and fzf controls. Record CPU for profile loading, context resolution, constructor and first draw in a separate instrumented run. |
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
proposed target for stage 1, with improved FFmpeg p95. Require exact
correctness parity. Investigate a control or interaction p95 regression
larger than the greater of 5 ms or 10%, or a helper RSS or high-water
regression larger than the greater of 2 MiB or 5%, over repeated matched runs.
These are review thresholds based on the pilot and expected measurement
noise. Run the presentation, numerical semantics, FFmpeg inventory and PTY
tests before expanding to the project's normal compatibility matrix.
[Local sandbox and supported test targets](development.md#isolated-local-debugging)
