# Terminal demonstration media

[Project overview](../../README.md) · [Development guide](../development.md) · [Historical visual and configuration review](../media-and-configuration-review.md)

The six public assets show the **v0.4.0-alpha local candidate** on Ubuntu 26.04.1, Bash 5.3.9 and Python 3.14.4. Terminal cells come from the actual application. The title bar identifies the captured checkout and the caption describes the keystrokes. The GIF uses presentation holds. For measured latency see the [Stage 1 benchmark](../ffmpeg-menu-performance-plan.md#stage-1-evaluation). The three-level browser has [updated terminal captures](../superpowers/plans/2026-11-24-menu-detail-levels-verification.md) showing the current category header, option spacing, unit labels and level key.

| Asset | What to look for |
| --- | --- |
| [Browse, insert and cancel](option-insertion.gif) | A 35.7-second loop through 19 checked states. Navigate categories, search for a unit, insert valued flags into pending commands and reopen help. |
| [Help browser](help-browser.png) | The unfiltered rsync Transfer category. The highlighted archive row shows which attributes archive mode preserves. |
| [Numerical guidance](numerical-guidance.png) | The selected bandwidth limit shows 1024 bytes/second per bare unit and the applicability warning. Searching for `bytes/second` finds this option. |
| [Assembled command](option-inserted.png) | The original flags, two inserted options, quoted pattern and both paths remain at the prompt after cancellation. |
| [Scrolled ls browser](ls-browser.png) | Display row 12 of 20. The lower Details viewport explains quoting, explicitly named files and how `-a` or `-A` overrides `--hide`. |
| [Guided review](guided-review.png) | In the [collection review workflow](../review.md#interactive-review-and-correction), select an option and edit individual fields in an illustrative collection. |

## Demonstration sequence

The recorder opens a real 100×24 Bash PTY with a temporary home, an isolated Readline configuration and discovery off. The rsync profile contains 216 options in 13 categories. The ls profile contains 60 options in six categories. Seven rows fit in each list.

1. Open rsync help with Alt-H and clear the partial flag with Ctrl-U. Browse Output and Attributes. Page down to Recovery to scroll the category pane.
2. In Network, select `--bwlimit=`, then search for `bytes/second`. Enter inserts the literal flag. Type `5000` back at the prompt.
3. Reopen the browser and search for `--exclude=`. Enter applies the filter. A second Enter inserts the flag. Add the pattern and paths, reopen help, then cancel.
4. In ls, page down to row 8 and move four rows to `--hide=PATTERN`. Scroll Details to read the override rule, insert the flag and type a quoted pattern. The long listing uses `-l --human-readable`, so the hide pattern takes effect when the directory is listed.

The recorder checks the actual Readline buffer and cursor after insertion and again after rsync cancellation. Both final lines have one additional trailing space at the cursor. The long rsync command wraps on screen.

```text
rsync --archive --compress --human-readable --itemize-changes --partial --bwlimit=5000 --exclude='*.tmp' "/srv/project files/" "/mnt/backup/project files/"
ls -l --human-readable --hide='*.tmp' "/srv/project files/"
```

Both Bash sessions use inert rsync and ls functions that record any execution. The shells close with the lines still pending. In a third session the guided reviewer opens a disposable collection, edits a field and cancels. The recorder compares the collection JSON before and after. The screenshot shows the lower viewport of the real form.

## Regeneration

From the repository root on Linux or WSL, use Bash 4.4+, Python 3.10+ and DejaVu Sans Mono. Install the optional [rendering dependencies](../../tools/requirements-media.txt) in a local environment. The installed program uses the Python standard library.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements-media.txt
.venv/bin/python tools/capture_readme_media.py \
  --output .cache/readme-media-candidate \
  --evidence tests/reports/readme-media-candidate
```

Choose fresh destinations. The [generator](../../tools/capture_readme_media.py) checks the visible selections and scroll positions, fingerprints runtime and profile inputs before and after capture, and writes five PNGs and one GIF. Open each PNG and inspect the entire decoded GIF alongside the recorded states before replacing the public assets. Use a full-size image for reading Details on narrow screens. A different local monospaced TrueType font can be selected with `CLI_HELP_MEDIA_FONT`.

Raw asciicast output, temporary paths and terminal buffers belong in the ignored evidence directory. The three cast files retain the output streams. `scenes.json` records cells and hold durations. `validation.json` records input and asset hashes, application and dependency versions, dimensions, pending line/cursor checks, execution markers and the review result.

The November 24 candidate capture used pyte 0.8.2, Pillow 12.1.1 and wcwidth 0.9.5. The GIF and four browser/command PNGs are 1148×702. The cropped reviewer is 1148×558. The encoder retained all 19 states. The final rsync and ls cursor offsets were 156 and 60. Both execution markers stayed absent and the review collection remained byte-identical. Local evidence resides under `tests/reports/candidate-040/media/`. The [October review](../media-and-configuration-review.md) records the previous capture and its independent tmux replay.
