# Setup, browser controls, and keybindings

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Requirements and quick start

- Linux with Bash 4.4 or newer.
- Python 3.10 or newer with its standard-library `curses` module.
- A UTF-8 locale and a terminal of at least 60 columns by 16 rows.
- The standard Linux `stty` utility enables automatic recovery after resizing.
- Optional: the Linux `man-db` tools and locally installed manual pages for
  manual-page discovery. Help-output discovery also works without `man`.

For persistent per-user setup, use the [install and uninstall scripts](installation.md).
For a temporary session without installation, run this from the project directory
in Bash:

```bash
source "$PWD/bash/interactive-help.bash"
```

### Run in a terminal pane

For an editor or app with an integrated terminal, set its working directory to
the checkout root. Use the following launch command for a temporary Bash
session with bundled profiles and discovery off.

```bash
env CLI_HELP_DISCOVERY=off bash --noprofile --rcfile ./bash/interactive-help.bash -i
```

Use a UTF-8 terminal pane at least 60×16. At 80×24 more rows fit beside the
selected option. Type `ffmpeg ` (including the trailing space), press Alt-H
and use the arrow keys and uppercase `D` to explore. Escape returns to the
pending line. Press Ctrl-U **at the Bash prompt** to discard that line.
[Compare the two terminal sizes](superpowers/plans/2026-11-24-menu-detail-levels-verification.md)

### First option insertion

Type `rsync --ar` without pressing Enter, then press **Alt-H**. The text at the
cursor supplies the initial filter. With `--archive` selected in the options pane,
press Enter to replace the partial flag and return to `rsync --archive `.
The inserted flag has a trailing space; the command remains pending at the Bash
prompt. This bundled static profile does not require an installed `rsync`.

Press Ctrl-U in the browser to clear the initial filter and browse all categories.
To search descriptions, press `/`, type a term, and press Enter to apply it;
press Enter again to select an option. Escape or Ctrl-C outside search entry
closes the browser and retains the original command and cursor position. During
search entry, Escape restores the previous filter. Alt-H can also be entered as
Escape followed by `h` in terminals that do not transmit Alt combinations directly.

### Other pending input examples

On supported Ubuntu editions, type `apt install ` and press Alt-H to browse
that verb’s options. Type `builtin read ` to browse the installed Bash topic.
For names shared with an executable, `echo ` selects the Bash builtin and
`/usr/bin/echo ` selects the external utility. Keep the trailing space after
the command or verb. Escape returns to the pending line. [Ubuntu terminal snapshots](assets/README.md#ubuntu-command-menus)

Examples of supported pending input:

```text
rsync --ar
grep --
ls 
tar --
git commit --m
git log --
sudo -n env LABEL='café' rsync --ar
python3 -m pip install --
ip address show de
ffmpeg -i 'movie.mp4' -c:v
git -C "project directory" branch --
docker run --
docker --context local container run --
```

The bundled profiles cover specific paths in Linux, development, cloud, and embedded command families. The [family inventories](audit-history.md#bundled-menu-progress) list their manual coverage and release-specific limits. Ordinary static profiles do not require installed
commands. Vendor/version-guarded profiles require identity verification. Custom
profiles replace bundled definitions for matching paths. See
[prefix/module forms and structured entry](invocation-and-structured-arguments.md)
for the supported grammar and mode-specific exceptions. For other
installed commands, the browser automatically extracts options from `--help`
output and locally installed man pages. For example, type `cp --` or `sed --`
and press Alt-H. Automatically generated profiles are cached.
The [supplied-driver activation and composition guide](profiles-and-drivers.md#activation-and-manual-composition)
describes explicit setup for Compose, Kubernetes, and GitHub CLI routes.
`--doctor` reports the selected collection; `--explain` identifies route and
profile provenance without running discovery. See the
[passive diagnostic interfaces](diagnostics.md) for buffer/cursor inputs.

Automatic discovery may invoke the installed program's fixed help route.
The [discovery and safety guide](discovery-and-safety.md) explains manual-only
mode, static-only mode, and execution boundaries.

The installer manages persistent loading through a marked startup block.
Alternatively, add a source statement using the actual checkout path to
`~/.bashrc` manually. Sourcing the adapter itself does not modify startup files:

```bash
source /absolute/path/to/CLI-InteractiveHelpMenu/bash/interactive-help.bash
```

## Browser controls

| Default keys | Action |
| --- | --- |
| Up/Down or `k`/`j` | Move within the focused pane |
| PageUp/PageDown | Scroll the focused category or option list by one page |
| Home/End | Move to the first or last item |
| Left/Right or `h`/`l` | Change category in the split view, or go back/forward one screen in the narrow menu |
| Tab | Switch focus between categories and options |
| Shift+D | Cycle Simple → Detailed → Expanded → Simple |
| `m` | Toggle horizontal scrolling of the highlighted option summary for this menu |
| Space | Next page of Details when text overflows. At the end, return to the top |
| `[` / `]` | Scroll the selected explanation one line, including a clipped category title |
| `/` | Edit the search filter |
| Ctrl-U | Clear the filter |
| Enter | Insert the selected option; in the category pane, focus its options |
| Escape, Ctrl-C, or `q` | Cancel without changing the pending input |

During search entry, Enter applies the filter, Escape restores the previous
filter, Backspace removes a character, and Ctrl-U clears it. A second Enter is
required to select an option after applying a search. Filtering matches option
names, original summaries and descriptions, argument placeholders, and numerical
explanations, including units, scales, accepted forms and source qualifications.
Source evidence remains searchable even when omitted from the concise display.
While a filter is active, each category displays its matching count.
When a new search has no matches in the current category, the first matching
category is selected automatically.

Simple opens with a one-line purpose for each option and gives spare rows to the
option list. Detailed adds a short explanation of the selection. Expanded includes
the available forms, conversions, constraints, examples and version qualifications.
The level key shown at the top preserves selection and filtering. Use `[` and `]`
when a line counter is visible. Long lists in Details use up to three columns
when the entries fit. Read down each column, then move to the top of the next.
Underlined text identifies literal values. Explanations wrap in the same column
as the value, and rules that apply to several values span the pane.

Category names use short sidebar labels. The header shows the original category
title. A title wider than the header can be read in full in the scrollable pane.
Both lists start on the same row, with a blank row between choices. A rule
separates the controls from content. The footer uses arrow symbols and shows
only shortcuts that fit in full. Press **Space** for the next page of Details
when the footer shows `Space next`. At the end, `Space top` returns to the first
page. The `[` and `]` keys still move by one line.

The `>` marker identifies the selection and `*` marks the focused split pane.
Color terminals use separate accents for option names, headings and shortcuts
when their palette supports enough contrasting pairs. `NO_COLOR=1` preserves
the layout, markers and emphasis in monochrome.

### Narrow menu preview

In the development checkout, run `export CLI_HELP_NARROW_MENU=1` in the Bash
session with the adapter loaded. Open a menu with **Alt-H** in a 60–79-column
terminal. At 80 columns and above the split view resumes.

**Shift+D** cycles Simple → Detailed → Expanded → Simple on any of the three screens.
The header shows the active level. Categories and Options keep their lists visible.
Use **→** to read the selected option at that level on the Details screen, where
**Shift+D** changes the explanation in place. **←** returns to the same option and filter.

| Screen | Actions |
| --- | --- |
| Categories | Select a category with ↑↓ and open it with → or Enter. A single category or an initial filter opens directly in Options. |
| Options | Read short summaries. Press → for Details, Enter to insert, or ← for Categories. Use / to search. |
| Details | Read the selected option at full width. Space pages through overflow, ← returns to the same option, and Esc cancels the entire menu. |

Run `unset CLI_HELP_NARROW_MENU` to return to the split view at every size.

### Scrolling option summaries

Scrolling starts enabled in both layouts. Press **m** to toggle it for the open
menu. This shortcut is omitted from the on-screen hints. To open menus with
static summaries, set `export CLI_HELP_SCROLL_SUMMARIES=0` in Bash.

A highlighted summary that exceeds its column stays still for two seconds, then
slides horizontally once, one character at a time. The option name stays fixed.
The final words remain visible until the selection changes. Returning to an option
starts a fresh pause. During search entry, `m` types into the filter. The action
can be rebound as `toggle_summary_scroll` if another action already uses `m`.

A shared unit note names the options it covers. Search accepts forms such as
`bps`, `KiB/s`, `µs`, and `MHz` wherever the corresponding meaning is documented.
Option spelling and original descriptions also remain searchable. Source citations
are omitted from terminal explanations. `[review]`, `[unverified]`, and `[varies]`
flag conflicting, unverified, and target-dependent guidance respectively.

For example, with FFmpeg’s `-b:v BITRATE` selected, an 80×24 terminal shows
nine options in Simple, seven in Detailed and three in Expanded. At 60×16 it
shows five, three and two. Other selections can wrap differently.
[Compare the six captured screens](superpowers/plans/2026-11-24-menu-detail-levels-verification.md)

Labels and descriptions are clipped or wrapped in
terminal cells for ordinary wide and combining text. Ambiguous-width characters,
emoji sequences, terminal fonts, and screen-reader behavior remain environment
dependent. Keyboard/rendered tests establish only their recorded interactions,
not compatibility with assistive technology.

If fragmented terminal keys are mistaken for Escape, an explicit
`export CLI_HELP_ESCAPE_DELAY=250` permits more time for curses to receive the
sequence. Values are integer milliseconds from 20 through 1000; the default
remains 40. A larger setting also delays standalone Escape cancellation. It does
not change Readline's Alt-H binding or guarantee arbitrary delayed Alt sequences.
`--doctor` reports the selected value and `--check` validates it.

Attached-only selections leave the cursor directly against the inserted flag.
Type the value immediately, for example a quoted directory after 7-Zip `-o`.
See [supported value spellings and bundles](argument-syntax.md).

## Passive troubleshooting

Run `python3 cli_help/main.py --doctor` to inspect runtime availability and selected
configuration without launching target programs. `--explain` uses the Bash
helper's buffer/cursor environment inputs to report command recognition, profile
provenance, cache state, and rejection codes while omitting pending operand values.
See [passive diagnostics and troubleshooting](diagnostics.md) for invocation
examples, statuses, privacy boundaries, and explicit active lookup instructions.
For imported collections, `--check-collection DIRECTORY` provides a separate
read-only consistency report. [Collection inspection and recovery](collection-recovery.md)
describes warning severity and explicit guarded backup restoration.

## Terminal resizing and display recovery

The browser uses the terminal's alternate screen. Opening it from the bottom
row preserves earlier output and scrollback at unchanged terminal dimensions.
Resizing below 60 columns or 16 rows displays a minimum-size notice; Escape or
Ctrl-C can still close the browser.

When terminal dimensions change while the browser is open, the Bash adapter
uses Readline's `clear-screen` function after the widget returns. This redraws
the pending command at the top of the viewport and prevents duplicate wrapped
prompt rows in the tested Bash 5.2.21/tmux 3.4 environment. It retains the pending
buffer, cursor, and terminal scrollback. Unchanged dimensions retain the previous
viewport. Dimension detection uses the standard Linux `stty` utility.

If stale rows remain, close the browser and press **Ctrl-L at the Bash prompt**.
This redraws the pending command at the top of the viewport without executing
it. In the tested tmux environment, earlier output remains available in
scrollback. Ctrl-L changes the visible viewport rather than restoring its
previous arrangement. Custom Readline bindings can assign Ctrl-L differently.

The [rendered-screen validation notes](development.md#rendered-screen-regressions)
describe the reproduction, test dependencies, and validation limits.

## Configurable keybindings

The launch shortcut is a Bash Readline sequence. Set it before sourcing the
plugin, or call `cli_help_bind` after changing it:

```bash
CLI_HELP_KEY='\C-x\C-h'
source /absolute/path/to/CLI-InteractiveHelpMenu/bash/interactive-help.bash
```

This example uses Ctrl-X followed by Ctrl-H. The default is `\eh` (Alt-H).
For Vi insertion mode:

```bash
CLI_HELP_KEYMAP=vi-insertion
cli_help_bind
```

Supported maps are `emacs-standard`, `emacs-meta`, `vi-insertion`, and
`vi-command`. The `vi-insertion` setting maps to Bash's `vi-insert` keymap.
The default is `emacs-standard`. `emacs-meta` is normalized to that root map
with an Escape prefix so Readline can replay the dispatch macro. The internal
sequences `\e[988~` and `\e[989~` are reserved. In vi insertion mode, bare
Escape continues to switch to command mode. Readline can list this fallback
alongside longer Escape sequences. Other bindings that overlap either reserved
sequence prevent installation and retain their original behavior.
Rebinding removes the previously
installed plugin binding. Any existing binding on the new sequence is replaced;
previous third-party bindings are not saved or restored. `cli_help_unbind`
removes the plugin's current binding from the session.

Browser shortcuts are configured in JSON. Copy
[keys.example.json](../config/keys.example.json) to an editable location, then
export its path:

```bash
mkdir -p "$HOME/.config/cli-help"
cp -i config/keys.example.json "$HOME/.config/cli-help/keys.json"
export CLI_HELP_CONFIG="$HOME/.config/cli-help/keys.json"
```

Only overridden actions need to be included. For example:

```json
{
  "keys": {
    "next_category": ["n"],
    "previous_category": ["p"],
    "accept": ["a"]
  }
}
```

Action names and named keys are listed in the example file. A key may also be
one printable character. Duplicate assignments, unknown actions, and empty
binding lists are rejected. If an older configuration assigns `D` to another
action, the browser tries `V` and then `f6` for `cycle_detail`. If all three
are occupied, assign a free key to `cycle_detail`. The menu header shows the
effective key. The page action uses `space`. Older configurations that already
assign Space use `P` or `f6` if free, then fall back to their line-scroll keys.
Escape and Ctrl-C remain emergency cancellation
keys and cannot be assigned to another action. Search-entry editing keys remain
fixed. Configuration is read each time the browser opens.
