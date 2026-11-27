# Terminal demonstration media

[Project overview](../../README.md) · [Controls and usage](../usage.md) · [Development guide](../development.md)

The seven screenshots and animation show the v0.5.0-alpha source checkout running in Bash on Ubuntu 26.04.1. The images contain the terminal’s actual text, highlights and cursor. Each caption describes the action at that point. The animation pauses on each step for readability. See the [menu measurements](../menu-cost-measurements.md) for timings.

| Asset | What it shows |
| --- | --- |
| [Browse, insert and cancel](option-insertion.gif) | A 40.5-second loop through 21 states in rsync and ls. Follow one bandwidth option through Simple, Detailed and Expanded, then search by unit and insert the flag. |
| [Help browser](help-browser.png) | Simple view opens on Transfer, category 1 of 13. The selected `--archive` row reads “Copy a tree with its metadata.” |
| [Numerical guidance](numerical-guidance.png) | Expanded view shows the bare rate for `--bwlimit=RATE` (1024 bytes/second) and the units for explicit suffixes, including `B/s`, `kB/s` and `KiB/s`. |
| [Assembled command](option-inserted.png) | After Escape, the two-line rsync command still contains its original flags, the bandwidth limit, the quoted exclusion and both paths. |
| [Scrolled ls browser](ls-browser.png) | Expanded view shows lines 17–27 of 28 for `--hide=PATTERN`, option 12 of 20 in Display. Explicitly named files still appear, and `-a` or `-A` overrides the pattern. |
| [Guided review](guided-review.png) | The [guided reviewer](../review.md#interactive-review-and-correction) shows an edited summary and the prompt for the option’s argument placeholder in a disposable example collection. |

## Ubuntu command menus

| Pending input | Checkout snapshot at 100×24 |
| --- | --- |
| `apt install ` | [APT install options](ubuntu-apt.png). The Resolute menu opens in Simple with 75 choices. Escape returns to the pending verb. |
| `builtin read ` | [Bash read options](bash-read.png). The installed Bash topic opens with 12 choices, including `-a array`, `-d delim` and `-t timeout`. |

Both captures use automatic discovery. Each session entered the pending line, pressed Alt-H, and cancelled with Escape. The cursor returned to the trailing space. The [provider audit](../ubuntu-coverage-audit.md#runtime-and-sources) explains why menu contents can differ on Noble.

## Demonstration sequence

1. With an rsync command pending, press Alt-H and clear the partial flag filter with Ctrl-U. Tab focuses categories. Move through Output and Attributes, then press PageDown to reach Recovery.
2. In Network, focus the options and select `--bwlimit=RATE`. Simple shows the bare unit beside the option. Press uppercase `D` for Detailed to read how the rate rounds. Press `D` again for Expanded to inspect the suffixes. Search for `bytes/second` with `/`. Enter applies the filter, and a second Enter inserts `--bwlimit=` at the prompt. Type `5000` and a space.
3. Reopen help, search for `--exclude=`, apply the filter and insert the flag. Add the quoted pattern and paths. Reopen help once more and press Escape.
4. In ls, press PageDown to reach option 10 of 20 in Display, then move down twice to `--hide=PATTERN`. Press `D` to read the quoting advice, then `D` again and `]` to scroll to the override rule. Insert the flag and type a quoted pattern and path.

The final Readline buffers each have a trailing space after the last quote. Their cursor offsets are 156 and 60, respectively.

```bash
rsync --archive --compress --human-readable --itemize-changes --partial --bwlimit=5000 --exclude='*.tmp' "/srv/project files/" "/mnt/backup/project files/"
ls -l --human-readable --hide='*.tmp' "/srv/project files/"
```

The rsync, ls and guided-review sessions use isolated homes and Readline configurations, discovery off, and 100×24 Bash terminals. Execution guards for both commands stayed silent. The rsync buffer and cursor matched before and after Escape. In a third session, the reviewer cancelled the partial edit and the collection JSON remained byte-identical.

## Regeneration

The [capture program](../../tools/capture_readme_media.py) runs on Linux or WSL with Bash 4.4+, Python 3.10+ and DejaVu Sans Mono. Install its optional [rendering dependencies](../../tools/requirements-media.txt) in a virtual environment. To reproduce the source-checkout gallery on Ubuntu with APT and Bash available:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements-media.txt
.venv/bin/python tools/capture_readme_media.py --ubuntu \
  --output .cache/readme-media-images \
  --evidence tests/reports/readme-media
```

For an unpacked candidate, pass its runtime root with `--runtime-root`. Omit `--ubuntu` for the rsync, ls and reviewer demonstration alone. `CLI_HELP_MEDIA_FONT` selects a different monospaced TrueType font. Inspect every PNG and decoded animation frame before replacing the public files.

## Capture evidence

The November 26 checkout recording used Bash 5.3.9, APT 3.2.1ubuntu0.1, Python 3.14.4, Pillow 13.0.0, pyte 0.8.2 and wcwidth 0.9.2. The recorder identified 224 source files, including the two Ubuntu reference editions. The seven PNGs and 21 animation frames were inspected. Raw recordings, displayed cells, input positions, and source and image digests are retained locally under `tests/reports/v050-checkout-media/`. Installed-package checks are listed in the [candidate roadmap](../../ROADMAP.md#remaining-work).

### November 25 historical capture

The November 25 session used Ubuntu 26.04.1, Bash 5.3.9, Python 3.14.4, Pillow 13.0.0, pyte 0.8.2 and wcwidth 0.9.2. The local runtime archive had SHA-256 `6c889a9c73ce6bd7f4b6a11884f6adc9c8684d129b6798034f8c30c697f9d69b`. All 160 fingerprinted application, configuration, profile and version files matched the package manifest and the working tree. The build supplied the runtime for these captures and predates the resulting documentation edits.

The animation and three browser screenshots are 1148×702. The pending-command screenshot is cropped to its two terminal rows (1148×174), and the reviewer to its form (1148×558). All 21 decoded frames and durations matched the recorded states. Independent replay in tmux 3.6 reproduced the same 100×24 text cells in every scene. The three raw asciicasts, per-scene cells and holds, source and media hashes, buffer assertions and decoded-frame and tmux checks reside in the ignored local directory `tests/reports/local-docs-20261125/media/`. The [historical media review](../media-and-configuration-review.md) describes the earlier capture and its tmux replay.
