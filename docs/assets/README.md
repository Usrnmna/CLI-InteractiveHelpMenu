# Terminal demonstration media

[Project overview](../../README.md) · [Development guide](../development.md)

These images render captured output from actual Linux Bash and Python terminal
sessions. Terminal cells, colors, search results, and form prompts come from the
application. The title bars and numbered captions are presentation annotations.
The guided-review image shows the lower viewport containing the form, omitting
earlier report output.
The assets were regenerated from the `0.1.2-alpha` working tree on 2026-10-25
(America/Los_Angeles). They illustrate the captured checkout, rather than proving
the contents or behavior of a downloaded release package. Source hashes and
runtime details are recorded in local capture evidence.

| Asset | Content |
| --- | --- |
| [Option insertion GIF](option-insertion.gif) | A 35.7-second loop with 19 checked states: browse categories, search numerical meaning, insert rsync options, then scroll ls options and complete details |
| [Help browser](help-browser.png) | Unfiltered rsync browser showing the first seven of nine categories |
| [Assembled rsync command](option-inserted.png) | Completed command with valued options and quoted paths, preserved after reopening help and cancelling |
| [Scrolled ls browser](ls-browser.png) | The twelfth Display option, `--hide=`, with its required argument and the preceding scrolled options |
| [Numerical guidance](numerical-guidance.png) | Actual bandwidth details: bare values use 1024 bytes/second, qualified to rsync 3.4.1; special values and source scope remain visible |
| [Guided review](guided-review.png) | Option selection and field editing in a temporary `example convert` collection |

## Demonstration sequence

Capture uses a 100-column, 24-row terminal, bundled profiles, and disabled
discovery. The rsync profile contains 29 options in nine categories; ls has
19 options in three categories, with twelve options in Display. Seven list rows
fit in this viewport, making both category and option scrolling visible.

| Chapter | Actual terminal interaction |
| --- | --- |
| rsync: open and navigate | Start with existing archive, compression, output, and recovery flags. Alt-H opens help; Ctrl-U clears the initial filter. Tab focuses categories; Right visits Output and Attributes; PageDown reaches Recovery and scrolls earlier categories away. |
| rsync: numerical search and insertion | Return to Network and select `--bwlimit=`. Inspect bare-number scale and rsync 3.4.1 applicability, search `bytes/second`, insert the matching flag, then type `5000` (KiB/s under that documented interpretation). |
| rsync: search and preservation | Reopen help, search for `exclude`, apply the filter with Enter, and select `--exclude=` with a second Enter. Type the quoted pattern and paths. Reopen and cancel with Escape, retaining the complete line and cursor. |
| ls: lists and complete details | PageDown reaches Display option 8/12; End reaches 12/12. Inspect its pattern meaning, use `]` to reach the literal argument declaration, then insert `--hide=` and type its pattern and directory. |

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

The generator writes the six named media assets in this directory. It records
raw PTY output in asciicast v2 format and insertion assertions under the ignored
`tests/reports/readme-media/` directory. Those recordings contain local interpreter
and temporary paths and are not public documentation assets. GIF timing uses
short presentation holds between actual captured states; it does not measure
application performance. Review raw output and rendered images after regenerating.
Use `--output` and `--evidence` to select separate candidate-image and private
evidence directories before replacing public assets. For example, with existing
dependencies:

```bash
.venv/bin/python tools/capture_readme_media.py \
  --output .cache/readme-media-candidate \
  --evidence tests/reports/readme-media-candidate
```

Select fresh destinations to preserve earlier captures. Candidate images should
replace public assets only after inspection; retain byte-identical assets. The
2026-10-25 run used the existing environment without installing dependencies and
ran inside an unprivileged, offline WSL network namespace.
The root ignore rules also exclude `cli-help-media-*` temporary session folders
when `TMPDIR` points at the checkout root. Public GIFs and PNGs remain trackable.
`validation.json` uses schema version 2 and records capture time, runtime and
optional dependency versions, terminal dimensions, source and asset SHA-256
hashes, frame count and total duration, per-command pending buffers/cursors,
non-execution results, and unchanged review collection contents. `scenes.json`
records each caption, hold duration, output-event checkpoint, visible cells,
and required/absent text. `absent_options` checks only the option pane: a flag
mentioned legitimately in explanatory prose does not imply an unscrolled row.
`browser.cast`, `ls.cast`, and `review.cast` retain the actual output streams.
Source hashes identify the captured working tree independently of the alpha
version string. A source change during recording rejects the capture.

The capture renderer supplements pyte 0.8.2 with xterm scroll-up/down handling
for the sequences used by curses. The handling follows the
[xterm control-sequence reference](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html).
Application output and list ordering are retained; captions and title bars are
the only presentation annotations.

Validation on 2026-10-25 independently replayed the refreshed rsync and ls output
through tmux 3.4: all 19 captured screens matched its visible cells. The capture
checks also confirmed exact pending buffers and cursors, cancellation preservation,
absence of target-execution markers, and unchanged review collection contents.
This evidence covers the recorded 100×24 xterm interactions on Bash 5.2.21 and
Python 3.12.3 under Ubuntu 24.04/WSL; other terminal environments remain unverified.
Fresh evidence is retained in `tests/reports/docs-media-current/capture-final/`.
Earlier raw recordings and verification reports remain separate historical
evidence. The assembled-command PNG is byte-identical and was retained.

The capture harness now asserts the displayed numerical lead and scrolls to
later argument text. Its earlier assumption that the literal argument label
appears immediately was obsolete after numerical guidance was added. The
option-pane absence check also excludes legitimate mentions in details. These
are capture assertions; application rendering and insertion are unchanged.

Regenerated captures require fresh checks. Inspect every encoded GIF frame, its
dimensions, and the complete hold sequence alongside the current raw output and
source hashes; previous checks do not establish replacement-asset correctness.

Mermaid diagrams are maintained directly in the root README and topic guides.
Their labels describe implemented flows; the screenshots and GIF show real UI
output. The workflow badge reports GitHub-hosted state independently of these
local captures.
