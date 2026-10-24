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
| [Option insertion GIF](option-insertion.gif) | An approximately 11-second loop: pending input, Alt-H, `/` and Ctrl-U to replace the initial filter with `archive`, Enter to apply the filter, and Enter to insert |
| [Help browser](help-browser.png) | Categorized browser with the initial `--ar` filter from the pending option |
| [Inserted option](option-inserted.png) | Final pending buffer, also available as a still alternative to the animation |
| [Guided review](guided-review.png) | Option selection and field editing in a temporary `example convert` collection |

The capture starts with `rsync --ar` and uses the bundled rsync profile with
discovery disabled. An isolated
shell function named `rsync` writes an execution marker if invoked. Before saving
the GIF, the recorder verifies that the marker is absent and that Readline contains
`rsync --archive ` with cursor position 16. The shell is terminated without sending
another Enter. This is evidence for the illustrated insertion, not an exhaustive
test of all commands or discovery routes.

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

The generator overwrites the four named media assets in this directory. It records
raw PTY output in asciicast v2 format and insertion assertions under the ignored
`tests/reports/readme-media/` directory. Those recordings contain local interpreter
and temporary paths and are not public documentation assets. GIF timing uses
short presentation holds between actual captured states; it does not measure
application performance. Review raw output and rendered images after regenerating.
`validation.json` records capture time, runtime and optional dependency versions,
terminal dimensions, source and asset SHA-256 hashes, the pending buffer/cursor,
the non-execution result, and unchanged review collection contents. Source hashes
identify the captured working tree independently of the unchanged alpha version.

Mermaid diagrams are maintained directly in the root README and topic guides.
Their labels describe implemented flows; the screenshots and GIF show real UI
output. The workflow badge reports GitHub-hosted state independently of these
local captures.
