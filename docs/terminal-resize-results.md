# Phase 2 terminal resize results

All six cases ran in live, keyboard-driven Bash/tmux sessions on Ubuntu 26.04.1 LTS. The checkout was clean at `b578e05` before capture. The accepted compact header was present throughout. Each pair shows the same operation across a resize. A–E retained their operational state within the checks below. F exposed a visible redraw defect after returning to Bash.

The images show complete terminal panes. Captions sit outside the pane. The replay used Bash 5.3.9, Ubuntu tmux `3.6a-2ubuntu0.2` and `TERM=tmux-256color`. APT used installed discovery. The rsync, Git and FFmpeg sessions used the bundled profiles. Terminal text, event timestamps, cursor coordinates, layout settings and per-case observations are retained in the [capture record](assets/resize-review/phase2/terminal-cells.json). Seven focused clock, resize and Readline regression tests passed on the host. Physical terminal-emulator drag and flicker remain unmeasured.

## A · Editing a search

At 80 columns the split view showed `Search: aste`. At 79 the guided menu kept the partial query, the selected match and the Enter/apply and Esc/restore hints. Finishing `asterisk` and pressing Enter selected `--purge` under the applied filter. In a separate pass Esc restored `--pur`. Both returned to `apt install --pur▏ 'graphviz'`. A split-layout control stayed split at 79 and a monochrome guided replay retained the same text.

| Before | After |
| --- | --- |
| ![Active APT search at 80×24](assets/resize-review/phase2/A-apply-before.png) | ![Same partial search at 79×24](assets/resize-review/phase2/A-apply-narrow.png) |

[Applied filter](assets/resize-review/phase2/A-apply-result.png) · [Restored filter](assets/resize-review/phase2/A-restore-result.png) · [Split control at 79 columns](assets/resize-review/phase2/A-control-narrow.png) · [Monochrome at 79 columns](assets/resize-review/phase2/A-mono-narrow.png)

**Review:** Is the difference between editing a search and browsing its results clear at 79 columns?

## B · Reading a long explanation

In the split layout, shrinking from 160×40 to 60×16 changed the suffix table from three columns to one. The viewport retained row 6. Its first text changed from the end of a qualification (“supported”) to the first input (“Input N · KiB/s”). At 80 columns, reducing height from 24 to 16 retained both row 8 and its text, “Input NB · B/s”. All 13 input/unit pairs were in order. All 63 narrow lines and all 60 lines at 80×16 matched independent fresh opens, including the final explanation.

In the guided layout, shrinking from the wide split view opened **Options**, with `--bwlimit=RATE` still selected at 2/38 in Expanded. Pressing → opened Details at the beginning. All seven pages matched a fresh narrow session.

| Before | After |
| --- | --- |
| ![Expanded rsync description at row 6 in a wide three-column table](assets/resize-review/phase2/B-width-before.png) | ![Row 6 after the table reflows to one column](assets/resize-review/phase2/B-width-after.png) |

[80×24](assets/resize-review/phase2/B-height-before.png) · [80×16](assets/resize-review/phase2/B-height-after.png) · [Final suffix and rounding rule](assets/resize-review/phase2/B-width-suffix.png) · [Bottom of Details](assets/resize-review/phase2/B-width-last.png) · [Guided Options after shrink](assets/resize-review/phase2/B-guided-narrow.png) · [Guided Details after →](assets/resize-review/phase2/B-guided-read.png) · [Restored width](assets/resize-review/phase2/B-width-return.png)

**Review:** Should a reader partway through Details land directly in narrow Details with the same phrase visible?

## C · Resizing a moving summary

One session widened 0.271 seconds after highlighting the clipped bandwidth summary. Another widened after motion had begun. In both, the entire summary fit at 160×24 and the frame stayed still for the 2.25-second observation. After shrinking to 60×16 again, the first movement was observed at 2.016 and 2.005 seconds respectively. Other rows and the option name stayed fixed. With the keyboard motion toggle off, the clipped text stayed still through the 3.55-second return observation.

| Before | After |
| --- | --- |
| ![Only the selected bandwidth summary has begun moving](assets/resize-review/phase2/C-moving-active.png) | ![The full bandwidth summary fits after widening](assets/resize-review/phase2/C-moving-wide.png) |

[Opening hold](assets/resize-review/phase2/C-pause-before.png) · [Clipped again](assets/resize-review/phase2/C-moving-again.png) · [Motion disabled](assets/resize-review/phase2/C-pause-before.png)

**Review:** Keep the fresh two-second pause when a resize clips the same selection again?

## D · Navigating a long option list

PageDown selected `-color_primaries` at 13/92 in the 120×30 codec menu. End selected `-trellis` at 92/92. At 79×24, the selected row and its count stayed visible in Options. The second Details page reached “Argument required.” Growing restored the split view. Up selected `-ticks_per_frame` at 91/92 and Down returned to `-trellis`.

| Before | After |
| --- | --- |
| ![FFmpeg selected at the bottom of the wide codec list](assets/resize-review/phase2/D-before.png) | ![The final codec option remains selected in narrow Options](assets/resize-review/phase2/D-after.png) |

[PageDown](assets/resize-review/phase2/D-page.png) · [Open Details](assets/resize-review/phase2/D-details.png) · [Final explanation](assets/resize-review/phase2/D-last.png) · [Return to 120×30](assets/resize-review/phase2/D-return.png)

**Review:** Is the last option easy to relocate when Details moves off the list screen?

## E · Crossing the minimum size

At 59×16 and 60×15 the menu displayed the minimum-size instruction with Escape available. Enter and Down while undersized left the menu open. Growing back to 60×16 restored the original selected `--patch` frame cell for cell. Escape while undersized restored the quoted command and cursor. Queuing widths 80 → 79 → 60 → 80 at height 24 without delays produced the same final cells as the starting 80×24 frame. This checks the settled frame after the burst.

| Before | After |
| --- | --- |
| ![Git selection at the supported minimum](assets/resize-review/phase2/E-before.png) | ![A single-column shrink displays the recovery instruction](assets/resize-review/phase2/E-width.png) |

[Height-only warning](assets/resize-review/phase2/E-height.png) · [Recovered menu](assets/resize-review/phase2/E-width-back.png) · [Escape below minimum](assets/resize-review/phase2/E-cancel.png) · [Before resize burst](assets/resize-review/phase2/E-burst-before.png) · [Settled burst result](assets/resize-review/phase2/E-burst-after.png)

**Review:** Does the warning give enough information to recover the menu or leave it?

## F · Returning to a wrapped Bash edit

After a shrink to 60×16, Esc and Ctrl-C each restored the original Unicode command at character offset 108. Enter inserted `--archive` once before the quoted destination and placed the cursor at 114. Each exit produced one visible prompt and retained all 80 scrollback markers. Reopening worked and the execution marker stayed clear.

**Visible defect.** After Esc or Ctrl-C, growing the Bash prompt from 60 to 80 columns left a duplicate tail of the command above the prompt. The cells still showed it after reopening and cancelling. The extra text was on screen only. The Readline buffer was exact. This reproduced with and without querying the buffer before the resize. The Enter run showed a clean prompt. Plain Bash at its ordinary bottom-of-screen prompt was also clean. Moving plain Bash’s prompt to the top with Ctrl-L before growing reproduced the same stray row.

| Before | After |
| --- | --- |
| ![The pending command wraps cleanly after Esc at 60×16](assets/resize-review/phase2/F-esc-exit.png) | ![A duplicate tail appears above the prompt at 80×24](assets/resize-review/phase2/F-esc-grow.png) |

[Menu before shrink](assets/resize-review/phase2/F-esc-open.png) · [Menu after shrink](assets/resize-review/phase2/F-esc-small.png) · [Ctrl-C result](assets/resize-review/phase2/F-esc-grow.png) · [Inserted option](assets/resize-review/phase2/F-insert-exit.png) · [Plain Bash bottom control](assets/resize-review/phase2/F-plain-grow.png) · [Plain Bash top control](assets/resize-review/phase2/F-plain-top-grow.png) · [After reopening and cancelling](assets/resize-review/phase2/F-esc-grow.png)

**Review:** Should the next development batch investigate recovery from the duplicate tail, given that plain Bash can reproduce it at the top of the screen?

[Phase plan and maintainer decision record](terminal-resize-review.md#phase-3--review-the-frames-and-choose-development-work)
