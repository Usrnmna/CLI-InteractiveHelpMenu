# FFmpeg option audit

First recorded 2026-11-22. This first pass covered 16 bundled rows. See the [expanded inventory and verification](ffmpeg-manual-coverage.md) for the later manual comparison.

## Sources

| Reference | Version or scope |
| --- | --- |
| [Upstream FFmpeg manual](https://ffmpeg.org/ffmpeg.html) | Rolling manual, compared with the [versioned 7.1 manual source](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/ffmpeg.texi) used by the profile. The relevant sections cover stream selection, transcoding, stream copy, filters and per-file options. |
| [Ubuntu 24.04 ffmpeg(1)](https://manpages.ubuntu.com/manpages/noble/man1/ffmpeg.1.html) | Noble package `7:6.1.1-3ubuntu5`. |
| [Ubuntu 26.04 ffmpeg(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ffmpeg.1.html) | Resolute package `7:8.0.1-3ubuntu2`. |
| [Duration syntax](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/utils.texi), [numeric prefixes and stream specifiers](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/fftools-common-opts.texi), [codec options](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/codecs.texi), [filters](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/filters.texi) and [input protocols](https://github.com/FFmpeg/FFmpeg/blob/n7.1/doc/protocols.texi) | FFmpeg 7.1 references for the structured value guides. Codec, filter and protocol availability depends on the build. |

## Disposition of the 16 entries

The first 16 rows separated file-scoped inputs and outputs from global controls. The `-map` entry explained that a trailing question mark tolerates an absent matching stream in an existing input.

## Compatibility and manual-only coverage

Noble and Resolute manuals differed on multiview selectors. Stream copy retains every view. Transcoding multiview video defaults to the base view. The later inventory separates top-level flags from codec-, format- and build-specific AVOptions.

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

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,337 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,337 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,337 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
