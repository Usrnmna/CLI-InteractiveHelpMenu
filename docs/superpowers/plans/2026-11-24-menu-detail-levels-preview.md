# Option detail levels at two terminal sizes

These are the approved design mockups. [Actual screens from the local build](2026-11-24-menu-detail-levels-verification.md) show what the browser displays.

Six proposed screens use the bundled FFmpeg menu, the **Stream codecs** category, an empty filter, and the fifth of ten options selected, `-b:v BITRATE`. Only the detail level and terminal size change. The neighboring codec and filter entries make the space reclaimed by Simple visible. The bit-rate note applies to the two named options.

[View the six screens side by side](2026-11-24-menu-detail-levels-preview.png) · [Implementation plan](2026-11-24-menu-detail-levels.md)

| Terminal | Simple · options visible | Detailed · options visible | Expanded · options visible |
| --- | ---: | ---: | ---: |
| 80×24 | 9 | 7 | 3 |
| 60×16 | 5 | 3 | 2 |

The counts refer to selectable rows in the right pane. The left pane scrolls independently. At 60×16, Expanded removes the blank row between its two options so that the first conversion rows remain visible. The illustrated `D` binding and colors are proposals. The text version retains selection and focus markers in monochrome.

## Simple

### 80×24

```text
Interactive help · ffmpeg                                Simple   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs      10 │   -c:v CODEC             Choose video codec
  Help and componen… 22 │
  Formats and mappi… 18 │   -c:a CODEC             Choose audio codec
  Seeking and times… 18 │
  Input rate and ou… 18 │   -c:v:0 CODEC           First video stream codec
  Filters and bitst… 13 │
  Video and frame t… 28 │   -c:a:0 CODEC           First audio stream codec
  Audio and subtitl… 11 │
  Encoding and hard… 17 │ > -b:v BITRATE           Set video bitrate
  Progress and diag… 31 │
  Alternate spellin… 22 │   -b:a BITRATE           Set audio bitrate
  Inverse switches   36 │
  Codec parameters   92 │   -filter:v FILTERGRAPH  Filter video
  Container and I/O… 38 │
  Video scaler       15 │   -filter:a FILTERGRAPH  Filter audio
  Audio resampler    54 │
  Video codecs A–F  135 │   -vn                    Exclude video
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel
```

### 60×16

```text
Interactive help · ffmpeg            Simple   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES        │ OPTIONS *                          5/10
  Files and se… 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │   -c:v:0 CODEC   First video stream co…
  Help and co… 22 │
  Formats and… 18 │   -c:a:0 CODEC   First audio stream co…
  Seeking and… 18 │
  Input rate … 18 │ > -b:v BITRATE   Set video bitrate
  Filters and… 13 │
  Video and f… 28 │   -b:a BITRATE   Set audio bitrate
  Audio and s… 11 │
  Encoding an… 17 │   -filter:v FI…  Filter video
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel
```

## Detailed

### 80×24

```text
Interactive help · ffmpeg                              Detailed   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs      10 │   -c:a CODEC             Choose audio codec
  Help and componen… 22 │
  Formats and mappi… 18 │   -c:v:0 CODEC           First video stream codec
  Seeking and times… 18 │
  Input rate and ou… 18 │   -c:a:0 CODEC           First audio stream codec
  Filters and bitst… 13 │
  Video and frame t… 28 │ > -b:v BITRATE           Set video bitrate
  Audio and subtitl… 11 │
  Encoding and hard… 17 │   -b:a BITRATE           Set audio bitrate
  Progress and diag… 31 │
  Alternate spellin… 22 │   -filter:v FILTERGRAPH  Filter video
  Inverse switches   36 │
  Codec parameters   92 │   -filter:a FILTERGRAPH  Filter audio
  Container and I/O… 38 │
-b:v BITRATE ──────────────────────────────────────────────────────────────────
Example: 2M = 2,000,000 bps. Omit /s in the input.
Rate control depends on the encoder.
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel
```

### 60×16

```text
Interactive help · ffmpeg          Detailed   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES        │ OPTIONS *                          5/10
  Files and se… 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │   -c:a:0 CODEC   First audio stream co…
  Help and co… 22 │
  Formats and… 18 │ > -b:v BITRATE   Set video bitrate
  Seeking and… 18 │
  Input rate … 18 │   -b:a BITRATE   Set audio bitrate
  Filters and… 13 │
-b:v BITRATE ──────────────────────────────────────────────
Example: 2M = 2,000,000 bps. Omit /s in the input.
Rate control depends on the encoder.
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel
```

## Expanded

### 80×24

```text
Interactive help · ffmpeg                              Expanded   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES              │ OPTIONS *                                        5/10
  Files and selection 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs      10 │   -c:a:0 CODEC           First audio stream codec
  Help and componen… 22 │
  Formats and mappi… 18 │ > -b:v BITRATE           Set video bitrate
  Seeking and times… 18 │
  Input rate and ou… 18 │   -b:a BITRATE           Set audio bitrate
-b:v BITRATE ───────────────────────────────────────────────────── Lines 1–11/18
Example: 2M = 2,000,000 bps. Omit /s in the input.
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
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel   [ ] scroll details
```

### 60×16

```text
Interactive help · ffmpeg          Expanded   D change view
Put file-specific options before their input or output.
Filter: (none)
CATEGORIES        │ OPTIONS *                          5/10
  Files and se… 6 │ -b:v/-b:a: bare N in bits/second (bps)
> Stream codecs   │ > -b:v BITRATE   Set video bitrate
  Help and co… 22 │   -b:a BITRATE   Set audio bitrate
-b:v BITRATE ────────────────────────────────── Lines 1–6/18
Example: 2M = 2,000,000 bps. Omit /s in the input.
Input             Result (bps)
N                 N
NK or Nk          N × 1,000
NM                N × 1,000,000
NG                N × 1,000,000,000
↑↓ move   ←→ category   Tab focus   / search
Enter insert   Esc cancel   [ ] scroll details
```

Expanded opens at the top of the explanation. The subsequent lines contain the remaining input forms, prefix and suffix rules, encoder behavior, and documented version. The counter includes these scrollable lines. These frames illustrate layout and copy only.
