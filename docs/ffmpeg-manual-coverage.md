# FFmpeg manual coverage

The [FFmpeg inventory](ffmpeg-manual-inventory.md) records the release references and the distinction between native options, directly routed library options and parameters inside filtergraphs. The [original 16-row audit](ffmpeg-option-audit.md) retains the initial dispositions and test results.

## Material corrections

- **Seeking relative to the end.** Supply a negative duration to `-sseof` before the relevant `-i`. The manuals use zero to describe the end of the file. The parsers reject a supplied zero. A negative offset also requires a known input duration. [Upstream options](https://ffmpeg.org/ffmpeg.html#Main-options) · [Noble input handling](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n6.1.1/fftools/ffmpeg_demux.c) · [Resolute input handling](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0.1/fftools/ffmpeg_demux.c)
- **Multiple inputs and outputs.** Enter input options before the corresponding `-i` and output options before the corresponding output filename. Repeat per-file options for later files. `-to` specifies a stop position, `-t` specifies duration and takes priority when both occur in the same group. Global `-copyts` preserves input timestamp values subject to subsequent processing and muxer adjustments. [Upstream CLI manual](https://ffmpeg.org/ffmpeg.html) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/ffmpeg.1.html)
- **Stream order and filtering.** Automatic audio selection normally favors the most channels. A default disposition can give another track in the same file precedence. An explicit map can select multiple streams. Repeated maps set their order in the output, a negative map removes previous matches, and an optional map still requires an existing input number. Unlabeled complex-filter outputs go to the first output file. A labeled output pad must be mapped exactly once. `-vf` and `-af` apply simple graphs to the selected media type. A filtered stream needs an encoder. Other streams in the same file can still use stream copy. [Stream selection](https://ffmpeg.org/ffmpeg.html#Stream-selection) · [Filtering](https://ffmpeg.org/ffmpeg.html#Filtering)
- **Release-specific scope.** Noble applies `-bsf` on output. Resolute and 9.1 also support an input bitstream filter before decoding. Both Ubuntu releases accept `-thread_queue_size` on input and output. The 9.1 declaration limits it to output. [6.1.1 declarations](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n6.1.1/fftools/ffmpeg_opt.c) · [8.0.1 declarations](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0.1/fftools/ffmpeg_opt.c) · [9.1 declarations](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.1/fftools/ffmpeg_opt.c)

## Verification

The packaged-client fixtures and Bash/tmux checks exercise separate paths. The clients process disposable media. The terminal harness disables discovery and places a recording executable on PATH while the pending command is edited. The historical optional-audio check uses a recording shell function. [Rendered-menu tests](../tests/test_syntax_terminal.py) · [Optional-audio insertion](../tests/test_expansion_terminal.py) · [Offline sandbox instructions](development.md#isolated-local-debugging)

### Results from real media

Both Ubuntu packages processed a generated three-second Matroska file containing video and two distinguishable audio tracks. The checks inspected the resulting streams, timestamps and durations with the matching ffprobe. [Executable regressions](../tests/test_ffmpeg_packaged.py) · [Package versions, build configurations and fixture preparation](../tests/fixtures/ffmpeg/help/README.md)

| Command distinction | Observed on the Ubuntu clients |
| --- | --- |
| Map order and codec overrides | Mapping the French audio track first, then video, then English audio yielded stream indices 0, 1 and 2. After `-c copy`, the narrower `-c:a:0 pcm_u8` changed only the first output audio track. A negative map removed the English track. An optional missing subtitle map succeeded. An optional map naming a nonexistent input failed. |
| Automatic audio selection | With an unmarked stereo English track first and a default-marked mono French track second, automatic selection copied the French track. An explicit `-map 0:a:0` copied English. |
| Library options | `-id3v2_version 3` and `4` changed the version byte in the generated MP3 header. Input `-blocksize 32` succeeded and zero failed despite the file protocol’s output-only help flag. Two input images at `-framerate 5/2` produced a rate of 5/2 and a duration of 0.8 seconds. |
| Options reset between outputs | The first output with `-map 0 -an` contained only video. The second with `-map 0:a` contained both audio tracks. |
| Filter outputs | Combining `-vf scale=32:24` with video stream copy failed. An unlabeled complex-filter output produced 32-pixel-wide video even with an explicit audio map and `-vn`. Leaving a labeled output pad unconnected failed. |
| Seek and stop | On 10 fps video with one-second keyframe spacing, seeking to 1.4 seconds before the input retained 20 frames with stream copy and 16 with transcoding. Output-side transcoding retained 16. `-sseof -1` retained 10 frames. Zero was rejected with “must be negative”. On PCM audio, `-ss 0.2 -to 0.8` produced 0.6 seconds on either side. When `-to 0.1` and `-t 0.2` were set together, the result was 0.2 seconds. |
| Timestamps | A fixture with an initial timestamp of five seconds produced output starting at zero by default, five seconds with `-copyts`, and zero with both `-copyts -start_at_zero`. |
| Overwriting | With `-n`, both clients printed an “already exists” diagnostic and returned status **0**. The existing file kept its original bytes, and the later output was absent. With `-y`, the existing file was replaced with valid audio. |
| Version differences | Resolute accepted `-/filter:v graph` and scaled a 64-pixel-wide input to 32 pixels. Noble rejected that option. Selecting the base view with `0:v:vidx:0` failed on Noble and produced 30 frames on Resolute. Both rejected `-sbsf` and accepted the `-bsf:s` spelling in a parser check. |

### Rendered menu and editing

The Bash/tmux harness opens the menu between an existing quoted input and a quoted output. At 220×120, it visits all 1,759 choices in 42 categories and compares the selected label, summary, line wrapping and every line of Details with the terminal cells. At 60×16, a search for **end of file** from the unfiltered menu finds `-sseof`. Scrolling reaches “Place it before the input it should seek.” Escape restores the exact original line and cursor. Reopening and selecting the row allows insertion of `-sseof -2` before the second `-i 'last clip.mkv'`. The original **optional audio** search still supports a quoted `-map '0:a?'` before an existing output. Recording stubs detect any execution of the pending command. [All-row and seek checks](../tests/test_syntax_terminal.py) · [Optional-map check](../tests/test_expansion_terminal.py)

Adding the native `-c` option exposed an editing regression while completing a partial `-c:`. The FFmpeg profile now identifies its argument syntax explicitly. The editor can replace an unfinished option, consume a negative map or pipe operand and locate the next editable slot after `-c:a:1 copy` or `-/filter:v:1 graph.txt`. The latter form requires a client release that supports file-loaded arguments. [Inventory and operand regressions](../tests/test_ffmpeg_manual_inventory.py) · [Original partial-selector regression](../tests/test_invocation_expansion.py)

### Reproducing the sandbox checks

Use a fresh snapshot for each focused and full run. Until the files are tracked, pass one `--include` for each new audit document, inventory, help capture and test module. The [FFmpeg fixture instructions](../tests/fixtures/ffmpeg/help/README.md) reproduce the private Noble runtime. The full suites also used the documented [fzf](fzf-manual-coverage.md#verification), [fd](fd-manual-coverage.md#verification), [OpenSSH](openssh-packaged-checks.md#package-verification-and-reproduction) and [Noble rsync](rsync-manual-coverage.md#verification) packages. Set their fixture variables inside the sandbox. Keep FFmpeg's private library search path local to its two client subprocesses.

Run the following focused selection inside `python3 -I tests/run_sandbox.py --target TARGET` after package setup. The full command inside a fresh sandbox is `bash tests/run.sh`. The independent numerical gate is `python3 -B scripts/check_numerical_coverage.py --mode strict --summary`.

```bash
env PYTHONPATH=tests python3 -m unittest -v \
  test_ffmpeg_manual_inventory test_ffmpeg_packaged \
  test_invocation_expansion.StructuredEditingTests \
  test_module_discovery.VariantAndSelectorTests.test_concrete_joined_selectors_and_placeholder_exclusions \
  test_numerical_migration.NumericalMigrationTests.test_reference_scales_distinguish_rsync_openssh_and_ffmpeg \
  test_numerical_migration.NumericalMigrationTests.test_time_scales_explicit_units_and_literal_zero \
  test_numerical_migration.NumericalMigrationTests.test_composites_delegated_values_and_dates_preserve_distinctions \
  test_numerical_migration.NumericalMigrationTests.test_display_fields_and_formatter_expose_essential_meaning \
  test_numerical_presentation.NumericalPresentationTests.test_reference_time_scales_and_specials_are_searchable \
  test_numerical_inventory.NumericalInventoryTests.test_real_source_counts_are_independent_and_reviews_are_complete \
  test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline \
  test_expansion_terminal.ExpansionScreenTests.test_ffmpeg_optional_audio_map_at_minimum_size \
  test_syntax_terminal.SyntaxScreenTests.test_ffmpeg_seek_before_second_input_at_minimum_size \
  test_syntax_terminal.SyntaxScreenTests.test_ffmpeg_all_rows_and_complete_details \
  test_regression_inventory.InventoryRegressionTests.test_path_164_ffmpeg
```

## Compatibility results

| Target | Ubuntu | Python | FFmpeg and ffprobe | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | `8.0.1-3ubuntu2` | 33 / 0 / 0 | 1,511 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | `6.1.1-3ubuntu5` | 33 / 0 / 0 | 1,511 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | `6.1.1-3ubuntu5` | 33 / 0 / 0 | 1,511 / 0 / 1 |

All nine packaged-media regressions and both minimum-size FFmpeg menu checks ran on each target. The all-row Bash/tmux check covered 5,277 selections across the three targets. The recording stubs recorded zero executions. Each full suite skipped only the Windows-specific probe. The strict numerical gate passed all 3,105 required contracts across 76 profiles. The tests use the installed Resolute package and privately extracted Noble packages. Optional hardware and external-library registrations have source or parser evidence as specified in the inventory.

The configured Lychee check resolved all 234 link occurrences across the seven changed Markdown files, including local heading fragments. A separate check resolved all 31 distinct source URLs in the bundled profile.
