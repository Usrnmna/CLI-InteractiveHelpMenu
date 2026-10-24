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

Type `rsync --` without pressing Enter, then press **Alt-H**. Select an option
and press Enter to insert it. Escape or Ctrl-C closes the browser and retains
the original command and cursor position. Alt-H can also be entered as Escape
followed by `h` in terminals that do not transmit Alt combinations directly.

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

The repository contains curated subsets for common Linux, development, cloud,
and embedded command families. Ordinary static profiles do not require installed
commands. Vendor/version-guarded profiles require identity verification. Custom
profiles replace bundled definitions for matching paths. See
[prefix/module forms and structured entry](invocation-and-structured-arguments.md)
for the supported grammar and mode-specific exceptions. For other
installed commands, the browser automatically extracts options from `--help`
output and locally installed man pages. For example, type `cp --` or `sed --`
and press Alt-H. Automatically generated profiles are cached.

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
| Left/Right or `h`/`l` | Change category |
| Tab | Switch focus between categories and options |
| `[` / `]` | Scroll the description upward/downward |
| `/` | Edit the search filter |
| Ctrl-U | Clear the filter |
| Enter | Insert the selected option; in the category pane, focus its options |
| Escape, Ctrl-C, or `q` | Cancel without changing the pending input |

During search entry, Enter applies the filter, Escape restores the previous
filter, Backspace removes a character, and Ctrl-U clears it. A second Enter is
required to select an option after applying a search. Filtering matches option
names, summaries, and descriptions. Each category displays its matching count.
When a new search has no matches in the current category, the first matching
category is selected automatically.

Both list panes scroll to keep the selected item visible. The `rsync` profile
contains nine categories, and the `ls` Display category contains twelve options,
so scrolling can be exercised in an ordinary 24-row terminal.

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
sequences `\e[988~` and `\e[989~` are reserved. An existing binding overlapping
either sequence prevents binding before changes are made; select a compatible
Readline configuration rather than overwriting the conflicting internal key.
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
binding lists are rejected. Escape and Ctrl-C remain emergency cancellation
keys and cannot be assigned to another action. Search-entry editing keys remain
fixed. Configuration is read each time the browser opens.
