# Rendered terminal verification

Captured from the Bash shortcut in a private tmux session. Each frame shows the same FFmpeg option, `-b:v BITRATE`, in the Stream codecs category. Blank lines are terminal rows. On November 25, 2026, a fresh local `0.4.0-alpha` build reproduced every displayed row in all six frames using its unpacked Bash adapter and runtime.

<a id="simple-80x24"></a>

## 80 × 24 · Simple

```text
Interactive help | ffmpeg                                Simple   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection   │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs         │   -c:v CODEC             Choose the codec for video …
  Help and components   │
  Formats and mapping   │   -c:a CODEC             Choose the codec for audio …
  Seeking and timestamps│
  Rates & limits        │   -c:v:0 CODEC           Choose the codec for the fi…
  Filters and bitstreams│
  Video and frame timing│   -c:a:0 CODEC           Choose the codec for the fi…
  Audio and subtitles   │
  Encoding and hardware │ > -b:v BITRATE           Set video bitrate
  Progress & logs       │
  Alternate spellings   │   -b:a BITRATE           Set audio bitrate
  Inverse switches      │
  Codec parameters      │   -filter:v FILTERGRAPH  Filter video before encoding
  Container I/O         │
  Video scaler          │   -filter:a FILTERGRAPH  Filter audio before encoding
  Audio resampler       │
  Video codecs A–F      │   -vn                    Exclude video from an input…
up/down move  left/right category  tab focus  / search
enter insert  esc cancel
```

<a id="detailed-80x24"></a>

## 80 × 24 · Detailed

```text
Interactive help | ffmpeg                              Detailed   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection   │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs         │   -c:a CODEC             Choose the codec for audio …
  Help and components   │
  Formats and mapping   │   -c:v:0 CODEC           Choose the codec for the fi…
  Seeking and timestamps│
  Rates & limits        │   -c:a:0 CODEC           Choose the codec for the fi…
  Filters and bitstreams│
  Video and frame timing│ > -b:v BITRATE           Set video bitrate
  Audio and subtitles   │
  Encoding and hardware │   -b:a BITRATE           Set audio bitrate
  Progress & logs       │
  Alternate spellings   │   -filter:v FILTERGRAPH  Filter video before encoding
  Inverse switches      │
  Codec parameters      │   -filter:a FILTERGRAPH  Filter audio before encoding
  Container I/O         │
-b:v BITRATE ─────────────────────────────────────────────────────────────────
Use 2M for 2,000,000 bits/s.
Enter the number and suffix without /s.
up/down move  left/right category  tab focus  / search
enter insert  esc cancel
```

<a id="expanded-80x24"></a>

## 80 × 24 · Expanded

```text
Interactive help | ffmpeg                              Expanded   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection   │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs         │   -c:a:0 CODEC           Choose the codec for the fi…
  Help and components   │
  Formats and mapping   │ > -b:v BITRATE           Set video bitrate
  Seeking and timestamps│
  Rates & limits        │   -b:a BITRATE           Set audio bitrate
-b:v BITRATE ──────────────────────────────────────────────────── Lines 1–11/29
Use 2M for 2,000,000 bits/s.
Input             Result (bps)
N                 N
NK or Nk          N × 1,000
NM                N × 1,000,000
NG                N × 1,000,000,000
NKi               N × 1,024
NMi               N × 1,048,576
NGi               N × 1,073,741,824
NB                N × 8
NKB or NkB        N × 8,000
up/down move  left/right category  tab focus  / search
enter insert  esc cancel  [/] scroll details
```

<a id="simple-60x16"></a>

## 60 × 16 · Simple

```text
Interactive help | ffmpeg            Simple   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES        │ OPTIONS *                          5/10
  File selection  │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │   -c:v:0 CODEC     Choose the codec fo…
  Help & parts    │
  Formats & maps  │   -c:a:0 CODEC     Choose the codec fo…
  Seek & time     │
  Rates & limits  │ > -b:v BITRATE     Set video bitrate
  Stream filters  │
  Frame timing    │   -b:a BITRATE     Set audio bitrate
  Audio & subs    │
  Encoding & HW   │   -filter:v FILT…  Filter video before…
up/down move  left/right category  tab focus  / search
enter insert  esc cancel
```

<a id="detailed-60x16"></a>

## 60 × 16 · Detailed

```text
Interactive help | ffmpeg          Detailed   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES        │ OPTIONS *                          5/10
  File selection  │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │   -c:a:0 CODEC     Choose the codec fo…
  Help & parts    │
  Formats & maps  │ > -b:v BITRATE     Set video bitrate
  Seek & time     │
  Rates & limits  │   -b:a BITRATE     Set audio bitrate
  Stream filters  │
-b:v BITRATE ─────────────────────────────────────────────
Use 2M for 2,000,000 bits/s.
Enter the number and suffix without /s.
up/down move  left/right category  tab focus  / search
enter insert  esc cancel
```

<a id="expanded-60x16"></a>

## 60 × 16 · Expanded

```text
Interactive help | ffmpeg          Expanded   D change view
Category 2/42 | Stream codecs
Filter:
CATEGORIES        │ OPTIONS *                          5/10
  File selection  │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │ > -b:v BITRATE     Set video bitrate
  Help & parts    │   -b:a BITRATE     Set audio bitrate
-b:v BITRATE ───────────────────────────────── Lines 1–6/34
Use 2M for 2,000,000 bits/s.
Input             Result (bps)
N                 N
NK or Nk          N × 1,000
NM                N × 1,000,000
NG                N × 1,000,000,000
up/down move  left/right category  tab focus  / search
enter insert  esc cancel  [/] scroll details
```

## Category titles and controls

At 60 columns the unfiltered sidebar has 16 cells for each name. All 302 category
names in 76 bundled profiles fit, and their labels are unique within each profile.
The category header retains the original name. A custom 89-character category
was navigated in a real Bash session at both sizes. Its entire title was readable
in each level by scrolling when needed. The FFmpeg test also applied a `bps` filter,
cycled the level, cancelled, and checked the original command and cursor.

| Terminal | Simple options | Detailed options | Expanded options |
| --- | ---: | ---: | ---: |
| 80 × 24 | 9 | 7 | 3 |
| 60 × 16 | 5 | 3 | 2 |

Counts describe the captured FFmpeg selection. They change with selected content,
wrapping, and the space required by shared guidance.

## Color and performance checks

In tmux, the same unselected ls flag produced ANSI cyan with a reported black
background and ANSI blue with a reported light background. The captured screens
above use the default monochrome fallback. Selection, focus, the category divider
and option gaps remain visible in monochrome. With representative xterm RGB
values, cyan on black had a 10.61:1 luminance contrast and blue on white had
9.40:1. Linear-RGB simulations of protanopia, deuteranopia and tritanopia kept
both pairs above 5.9:1. Actual terminal palettes can differ.

Three paired host runs used the pre-change working tree and the implemented
browser, with each renderer predicting its own PTY frames. Median FFmpeg opening
time was 508 ms before and 528 ms after. The small git menu measured 205 ms and
204 ms. The first FFmpeg search keystroke measured 1.6 ms and 2.9 ms.
Other test suites were running during these local measurements.

## Regression results

| Isolated target | Passed | Skipped |
| --- | ---: | ---: |
| Ubuntu 26.04.1, Python 3.14 | 1,887 | 1 |
| Ubuntu 24.04.5, Python 3.12 | 1,887 | 1 |
| Ubuntu 24.04.5, Python 3.10 | 1,887 | 1 |

Each target covered the same 1,888 distinct tests across four groups. The skip
covers Windows-only behavior on Linux. The previous release candidate failed the
source-inventory check, so the 15 package tests were rerun successfully with
fresh temporary builds on each target. The final spelled-out-unit search change
also passed 34 focused tests per target, including the native viewport checks.
