# Terminal demonstration media

[Project overview](../../README.md) · [Development guide](../development.md)

These images render captured output from actual Linux Bash and Python terminal
sessions. Terminal cells, colors, search results, and form prompts come from the
application. The title bars and numbered captions are presentation annotations.
The guided-review image shows the lower viewport containing the form, omitting
earlier report output.
The assets are regenerated from the development tree on 2026-10-23; they
illustrate checkout behavior rather than the preserved alpha release packages.

| Asset | Content |
| --- | --- |
| [Option insertion GIF](option-insertion.gif) | A 30.8-second loop with 17 checked states: build an rsync command through category navigation and search, then scroll ls Display options and insert a filename filter |
| [Help browser](help-browser.png) | Unfiltered rsync browser showing the first seven of nine categories |
| [Assembled rsync command](option-inserted.png) | Completed command with valued options and quoted paths, preserved after reopening help and cancelling |
| [Scrolled ls browser](ls-browser.png) | The twelfth Display option, `--hide=`, with its required argument and the preceding scrolled options |
| [Guided review](guided-review.png) | Option selection and field editing in a temporary `example convert` collection |

## Demonstration sequence

Capture uses a 100-column, 24-row terminal, bundled profiles, and disabled
discovery. The rsync profile contains 29 options in nine categories; ls has
19 options in three categories, with twelve options in Display. Seven list rows
fit in this viewport, making both category and option scrolling visible.

| Chapter | Actual terminal interaction |
| --- | --- |
| rsync: open and navigate | Start with existing archive, compression, output, and recovery flags. Alt-H opens help; Ctrl-U clears the initial filter. Tab focuses categories; Right visits Output and Attributes; PageDown reaches Recovery and scrolls earlier categories away. |
| rsync: valued insertion | Return to Network, use Tab and Down to select `--bwlimit=`, inspect the required RATE, insert it, and type `5000`. |
| rsync: search and preservation | Reopen help, search for `exclude`, apply the filter with Enter, and select `--exclude=` with a second Enter. Type the quoted pattern and paths. Reopen and cancel with Escape, retaining the complete line and cursor. |
| ls: longer option list | Open help for existing listing flags and clear the filter. PageDown reaches Display option 8/12; End reaches 12/12. Inspect and insert `--hide=`, then type its pattern and directory. |

The final pending lines are:

```text
rsync --archive --compress --human-readable --itemize-changes --partial --bwlimit=5000 --exclude='*.tmp' "/srv/project files/" "/mnt/backup/project files/"
ls --all --human-readable --hide='*.tmp' "/srv/project files/"
```

Each line has one trailing space at the final cursor. The long rsync line wraps
naturally on screen; no newline is present in its Readline buffer. No filesystem
contents or installed target programs are required for these static profiles.

Separate temporary Bash sessions define harmless `rsync` and `ls` functions
that write an execution marker if called. The recorder checks the exact pending
buffer and character cursor after each insertion, confirms marker absence, and
verifies that rsync cancellation preserves both values. Visible-cell checks
confirm category/option counts, pane focus, required arguments, and disappearance
of earlier rows during scrolling. Shells are terminated without submitting the
pending lines. These checks establish the recorded interactions rather than
exhaustive command or terminal compatibility.

The review screenshot uses illustrative profile/report data in a temporary
collection. It runs the actual review CLI and guided forms, cancels the partial
edit, and verifies that the original collection JSON remains unchanged. No command
discovery, manual rendering, or external editor is used.

## Regeneration

Run from the repository root under Linux or WSL with Python 3.10+, Bash 4.4+,
and the DejaVu Sans Mono font installed:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements-media.txt
.venv/bin/python tools/capture_readme_media.py
```

The optional dependencies belong only to the media generator. The application
retains its standard-library-only Python runtime. `CLI_HELP_MEDIA_FONT` can select
another local monospaced TrueType font. The default font path is
`/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf`.

The generator overwrites the five named media assets in this directory. It records
raw PTY output in asciicast v2 format and insertion assertions under the ignored
`tests/reports/readme-media/` directory. Those recordings contain local interpreter
and temporary paths and are not public documentation assets. GIF timing uses
short presentation holds between actual captured states; it does not measure
application performance. Review raw output and rendered images after regenerating.
The root ignore rules also exclude `cli-help-media-*` temporary session folders
when `TMPDIR` points at the checkout root. Public GIFs and PNGs remain trackable.
`validation.json` uses schema version 2 and records capture time, runtime and
optional dependency versions, terminal dimensions, source and asset SHA-256
hashes, frame count and total duration, per-command pending buffers/cursors,
non-execution results, and unchanged review collection contents. `scenes.json`
records each caption, hold duration, output-event checkpoint, visible cells,
and required/absent text.
`browser.cast`, `ls.cast`, and `review.cast` retain the actual output streams.
Source hashes identify the captured working tree independently of the unchanged
alpha version. A source change during recording rejects the capture.

The capture renderer supplements pyte 0.8.2 with xterm scroll-up/down handling
for the sequences used by curses. The handling follows the
[xterm control-sequence reference](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html).
Application output and list ordering are retained; captions and title bars are
the only presentation annotations.

Validation on 2026-10-23 independently replayed the recorded rsync and ls output
through tmux 3.4: all 17 captured screens matched its visible cells. GIF inspection
also checks every encoded frame, its dimensions, and the complete hold sequence.
This evidence covers the recorded 100×24 xterm interactions on Bash 5.2.21 and
Python 3.12.3 under Ubuntu 24.04/WSL; other terminal environments remain unverified.

Mermaid diagrams are maintained directly in the root README and topic guides.
Their labels describe implemented flows; the screenshots and GIF show real UI
output. The workflow badge reports GitHub-hosted state independently of these
local captures.
