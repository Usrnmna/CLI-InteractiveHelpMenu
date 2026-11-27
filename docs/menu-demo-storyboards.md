# Five Bash menu demonstrations

These are scripts for a future recording of the development checkout. In the starting lines below, `▏` marks the Readline cursor. The final Enter in a menu returns to editing. End the recording at the pending Bash prompt before accepting the command.

| Package | User’s task | Capability to make visible | Planned medium |
| --- | --- | --- | --- |
| apt | Preview installing Graphviz | Complete a verb at the cursor, then use verb-specific options | Four PNGs |
| bash | Give a prompt a five-second timeout | Read installed builtin help and supply a required argument | Three PNGs |
| git | Prepare a machine-readable worktree listing | Follow a nested command and discover a prerequisite | Four PNGs |
| rsync | Limit a transfer over a slow connection | Reveal clipped text without shifting the option name | Timed GIF |
| ffmpeg | Find the last entry in a large codec menu | Page through a category and cancel back to an unfinished edit | Four PNGs |

Use the keyboard throughout. Keep the command, selected item, and returned cursor visible in the terminal. Put keystroke captions outside the terminal frame. Retain the terminal’s markers and reverse-video selection so each sequence also reads in monochrome. Record the Ubuntu, Bash and package versions with the captures. Use installed-provider discovery for APT and Bash and the bundled profiles for Git, rsync and FFmpeg.

## 1. APT · preview a package install

Start at 100×24 with `apt ins▏ 'graphviz'`.

1. **Before.** Show the incomplete verb, cursor and quoted operand.
2. **Complete the verb.** Press Alt-H, highlight the literal keyword `install`, and capture its selection. Press Enter in the menu.
3. **Inspect the install options.** At the returned cursor before the quoted name, type `--sim` and a separating space. Move left one character to leave `apt install --sim▏ 'graphviz'`. Reopen with Alt-H and highlight `--simulate`. Keep the `apt install` title in frame.
4. **After.** Accept the option. Show `apt install --simulate ▏'graphviz'`. Frame the same portion of the prompt as in step 1 so the preserved quotes are easy to compare.

## 2. Bash · time out a prompt

Start at 100×24 with `builtin read ▏`. The explicit `builtin` selects Bash’s own help topic.

1. **Find the argument.** Press Alt-H and highlight `-t timeout`. Include the `builtin read` title and the adjacent declarations, such as `-d delim`, so the argument notation is visible.
2. **Understand the timeout.** Open Detailed with Shift+D and show the timeout explanation. If the first page shows another part of the Bash help topic, page to the `-t` entry before choosing the still.
3. **Supply the value.** Accept `-t`. In Bash, type `5 reply`. End on `builtin read -t 5 reply▏` and caption which text the menu inserted and which text was typed.

## 3. Git · list worktrees for a script

Start at 80×24 with `git worktree list ▏`. The goal is stable output even when a worktree path contains a newline.

1. **Scope.** Press Alt-H. Show the `git worktree list` title and `--porcelain`, the first option in this seven-entry menu.
2. **Discover the dependency.** Move down to `-z` and press Shift+D. Capture the detail explaining that NUL termination requires `--porcelain`. Keep both names legible.
3. **Choose the prerequisite.** Move up to `--porcelain` and accept. Show it on the pending line. Reopen the same menu with Alt-H.
4. **Finish.** Select `-z` and accept. Show `git worktree list --porcelain -z ▏`. Use this prompt as the final frame because the resulting NUL characters would be invisible in a terminal listing.

## 4. rsync · read a clipped bandwidth limit

Use 60×16 with `CLI_HELP_NARROW_MENU=1` and default summary scrolling. Start with `rsync ▏`. Keep the terminal size, crop and option row fixed throughout the moving portion.

1. **Locate.** Open with Alt-H, move down six categories to Network, press → for Options, and move down once to `--bwlimit=RATE`. Show the clipped summary and its neighboring rows.
2. **Pause.** Hold the opening frame for the full two seconds after highlighting the option. Keep the entire option row visible.
3. **Reveal.** Record the actual app at normal speed as only the highlighted summary moves and reveals “KiB/s)”. Hold the final text briefly. Keep the declaration, highlight marker and neighboring rows in view as stationary references.
4. **Apply.** Press Enter to insert `--bwlimit=`. Type `5000 'project files/' backup/` at the prompt. End on `rsync --bwlimit=5000 'project files/' backup/▏`. The bare value represents 5000 KiB/s.

## 5. FFmpeg · find a codec setting and return to an edit

Start at 120×30 with `ffmpeg ▏ 'review clip.mp4'`. The cursor is between the two spaces. This scenario ends by cancelling the menu.

1. **Orient.** Press Alt-H and move right 13 categories to Codec parameters. Capture the first selection, `-alpha_mode`, alongside the 1/92 counter.
2. **Page.** Press PageDown once. Show the new highlighted option and counter. Record the actual name shown at this size, since the jump depends on available rows.
3. **Reach the end.** Press End. Capture `-trellis` and 92/92. Keep the complete row and footer visible. If Details is needed to read its meaning, switch views before taking this still.
4. **Restore.** Press Esc. Show the original line and cursor immediately before the existing space and quoted filename. Use the caption “Esc returns to the edit” and retain the quoted name in the crop.
