# FFmpeg option audit

The first pass covered 16 entries in two categories. The [full manual inventory](ffmpeg-manual-inventory.md) and [revisit results](ffmpeg-manual-coverage.md) cover the expanded [bundled FFmpeg menu](../profiles/ffmpeg.json). File order determines the meaning of several options. Input options precede `-i`. Output options precede the output filename. Global options such as the overwrite policy apply throughout the invocation.

## Sources

| Reference | Version or scope |
| --- | --- |
| [Upstream FFmpeg manual](https://ffmpeg.org/ffmpeg.html) | Rolling manual, compared with the [versioned 7.1 manual source](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/ffmpeg.texi) used by the profile. The relevant sections cover stream selection, transcoding, stream copy, filters and per-file options. |
| [Ubuntu 24.04 ffmpeg(1)](https://manpages.ubuntu.com/manpages/noble/man1/ffmpeg.1.html) | Noble package `7:6.1.1-3ubuntu5`. |
| [Ubuntu 26.04 ffmpeg(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ffmpeg.1.html) | Resolute package `7:8.0.1-3ubuntu2`. |
| [Duration syntax](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/utils.texi), [numeric prefixes and stream specifiers](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/fftools-common-opts.texi), [codec options](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/codecs.texi), [filters](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/filters.texi) and [input protocols](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/protocols.texi) | FFmpeg 7.1 references for the structured value guides. Codec, filter and protocol availability depends on the build. |

## Disposition of the 16 entries

Each disposition describes the previous entry. The rows follow menu order.

| Entry | Disposition | Finding and change |
| --- | --- | --- |
| `-i` | Redundant | Keep the file-or-URL summary. Replace repeated protocol grammar with the placement of input options, repeated inputs, standard input and the separate output filename. |
| `-map` | Incomplete | A map can select several streams or a labeled filter output. Explicit maps replace automatic selection for that output. Repetition sets stream order. A negative map removes earlier matches. Quoting `'0:a?'` protects the wildcard from the shell. It allows missing audio in input 0 and still requires that input to exist. |
| `-y` | Sufficient as written | Keep the overwrite-without-prompting summary. Its scope is global across output files. |
| `-n` | Incomplete | An existing output ends the invocation. FFmpeg does not skip the collision and continue with later files. |
| `-ss` | Incomplete | An input seek can land at an earlier seek point. Accurate seeking discards the lead-in during transcoding by default, while stream copy may preserve it. Output-side transcoding discards input until the requested timestamp. |
| `-t` | Incomplete | Before an input this limits data read. Before an output it limits duration written. A bare value is in seconds. The structured guide retains clock notation and the `s`, `ms` and `us` suffixes. A simultaneous `-to` yields to `-t`. |
| `-c:v` | Inaccurate | The value guide previously allowed only encoder names or `copy`. On input this selects a video decoder. On output it selects an encoder or packet copying. The last matching codec option wins. |
| `-c:a` | Inaccurate | Apply the same placement rule to audio. A decoder name is valid before `-i`, and `copy` is valid only for output. |
| `-c:v:0` | Incomplete | The embedded zero selects the first video stream of the relevant input or output. After a broad codec setting, this spelling can override it for just that stream. |
| `-c:a:0` | Incomplete | The zero counts audio streams. The first audio stream can have a different absolute stream index. The option value names the codec or requests output stream copy. |
| `-b:v` | Redundant | Keep bits/s in the summary and use `2M` as a video example. Keep binary prefixes and byte scaling in Details. The selected encoder determines rate control. |
| `-b:a` | Redundant | Use `128k` for 128,000 bits/s. Keep the distinction between the lowercase `k`, binary `i` modifier and final uppercase `B`. The target bitrate applies when encoding. |
| `-filter:v` | Incomplete | Show a quoted scaling example. A simple graph has one video input and one video output. Its result must be encoded. Refer multiple inputs or outputs to `-filter_complex`. |
| `-filter:a` | Incomplete | Show a quoted volume example. A simple audio graph has one audio input and one audio output. Stream copy cannot apply it. |
| `-vn` | Incomplete | Before `-i`, block that input’s video for every output. Before an output, suppress selected or mapped video for that file. Complex filtergraph outputs are an exception. |
| `-an` | Incomplete | Apply the same distinction to audio. Its position determines which input or output it affects. |

## Compatibility and manual-only coverage

For a file with video and optional audio, the following invocation copies the video streams first and any audio streams second. Input 0 must exist and contain video. The output container must accept the copied codecs.

```bash
ffmpeg -i input.mkv -map 0:v -map '0:a?' -c copy output.mkv
```

The Noble manual gives the input/stream and filter-label forms of `-map`. Resolute and the versioned 7.1 guide also describe a multiview selector. When transcoding multiview video, the default is the base view. Stream copy retains every view. Unlabeled complex filter outputs go to the first output even with explicit maps. A labeled filter output must be mapped exactly once. [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/ffmpeg.1.html) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/ffmpeg.1.html) · [Upstream stream selection](https://ffmpeg.org/ffmpeg.html#Stream-selection)

Manual-only options include `-to` for a stop position, `-sseof` for seeking relative to the end, `-copyts` for timestamps, `-filter_complex` for complex graphs, `-vf` and `-af` as filter aliases, and `-sn` and `-dn` for subtitle and data streams. The manuals also cover additional codec selectors, muxers, devices, filters and protocol-specific options. The menu keeps its 16 literal spellings and argument forms. [Upstream options](https://ffmpeg.org/ffmpeg.html#Options)

The inventory review covered the 16 option rows, the stream category description, the command header and the profile file. The corrected structured fields cover decoder names, output-only stream copy, default codec selection and the mapping grammar. The existing unit scales, duration forms and zero-based indices were retained. [Numerical inventory review](numerical-inventory/review.json)

## Observed FFmpeg behavior

The Ubuntu 26.04 sandbox ran packaged FFmpeg and ffprobe 8.0.1-3ubuntu2 on generated video and audio in a disposable directory. The Ubuntu 24.04 comparison used its manual. The offline Noble test image inspected for these fixtures did not contain FFmpeg.

| Fixture | Result on Ubuntu 26.04 |
| --- | --- |
| Input and mapping | FFmpeg read a WAV from standard input with `-i -`. Mapping audio before video, then removing the second audio stream, produced one audio stream followed by video. An optional missing subtitle in input 0 succeeded. An optional stream in nonexistent input 1 produced an error. |
| Codecs and selectors | With a video stream followed by two audio streams, `-c copy -c:a:0 pcm_u8` changed only the first audio stream. The input accepted `-c:v:0 mpeg4` before `-i` and rejected the decoder name `copy`. |
| Stream suppression and filters | Input-side `-an` blocked the first input’s audio while audio from the second input remained available. Output-side `-map 0 -vn` kept both audio streams. An unlabeled video output from a complex graph still reached an output with `-vn`. Simple scaling and volume filters worked with encoding. Combining the audio filter with audio stream copy failed. |
| Seeking | The three-second, 10 fps MPEG-4 fixture had seek points one second apart. With `-ss 1.4` before `-i`, stream copy retained 20 frames and transcoding retained 16. With output-side `-ss 1.4`, transcoding also retained 16. |
| Duration and bitrate | Input-side `-t 200ms` produced 0.2 seconds of PCM audio. Output-side `-to 0.1 -t 0.2` also produced 0.2 seconds. ffprobe reported 128,000 bits/s for MP2 audio encoded with `-b:a 128k`. |
| Overwrite policy | With `-n`, an existing first output kept its original bytes and a later output was never created. This build printed a collision diagnostic and returned status 0. With `-y`, it replaced the disposable file with valid audio. The manuals specify the stop behavior without promising an exit code. |

## Rendered menu and sandbox verification

On each target a real Bash/tmux session with discovery disabled visited all 16 rows across both categories at 200×90. The command header, every selected label and summary, and the entire rendered Details pane matched the profile and formatter. A shell stub confirmed that browsing and cancelling left the pending FFmpeg command unexecuted.

At 60×16 the regression searched for “optional audio” and scrolled to the requirement that the input number exist. Cancelling restored the original buffer and cursor. Selecting the row inserted the literal `-map`, and typing `'0:a?'` left the following output filename intact. The regression uses the displayed Details line count to reach the final page. [Terminal regression](../tests/test_expansion_terminal.py)

Seven focused checks passed on each target. They cover the minimum-size interaction, bitrate and time scales, mapping components, visible units, searchable duration guidance and inventory review. To repeat the terminal check, use `host`, `noble310` or `noble312` for TARGET. [Offline sandbox instructions](development.md#isolated-local-debugging)

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k ffmpeg_optional_audio_map_at_minimum_size -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,337 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,337 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,337 | 0 | 1 |

All three full-suite snapshots included the untracked audit documents. The only skip on each target was the Windows-specific probe.
