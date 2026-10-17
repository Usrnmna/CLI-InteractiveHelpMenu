# Setup, browser controls, and keybindings

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Requirements and quick start

- Linux with Bash 4.4 or newer.
- Python 3.10 or newer with its standard-library `curses` module.
- A UTF-8 locale and a terminal of at least 60 columns by 16 rows.
- Optional: the Linux `man-db` tools and locally installed manual pages for
  manual-page discovery. Help-output discovery also works without `man`.

From the project directory in Bash:

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
git -C "project directory" branch --
docker run --
docker --context local container run --
```

The repository contains curated subsets for `rsync`, GNU `grep`, GNU `ls`, GNU
`tar`, `git commit`, and `git log`. Commands do not need to be installed to browse
these static profiles. Custom and bundled profiles take precedence. For other
installed commands, the browser automatically extracts options from `--help`
output and locally installed man pages. For example, type `cp --` or `sed --`
and press Alt-H. Automatically generated profiles are cached.

Automatic discovery may invoke the installed program's fixed help route.
The [discovery and safety guide](discovery-and-safety.md) explains manual-only
mode, static-only mode, and execution boundaries.

To load the plugin in future sessions, add a source statement using the actual
checkout path to `~/.bashrc`. The prototype does not modify startup files.

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
`vi-command`. The default is `emacs-standard`. Rebinding removes the previously
installed plugin binding. Any existing binding on the new sequence is replaced;
previous third-party bindings are not saved or restored. `cli_help_unbind`
removes the plugin's current binding from the session.

Browser shortcuts are configured in JSON. Copy
[keys.example.json](../config/keys.example.json) to an editable location, then
export its path:

```bash
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
