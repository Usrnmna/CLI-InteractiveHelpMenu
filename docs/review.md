# Reviewing and correcting generated help

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Interactive review and correction

Open a collection's scan report from a UTF-8 Linux terminal:

```bash
python3 cli_help/main.py --review-report \
  "$HOME/.config/cli-help/scanned/scan-report.json"
```

The initial queue lists unresolved entries with scan status `needs_adjustment`
or `failed`. Enter a displayed number to open an entry. The queue supports
next/previous pages, a case-insensitive command-name filter, and an all/issues
toggle for inspecting successful or skipped entries. Original diagnostics and
suggested actions are displayed when an entry opens.

## Entry actions

| Entry action | Behavior |
| --- | --- |
| `o` — Options | Select an existing option, then edit its fields, move/reorder it, or delete it |
| `c` — Categories | Rename categories, edit descriptions, reorder/delete categories, or edit the profile description |
| `d` — Driver | Correct global-option arity, manual names, fixed help arguments, and positional boundaries |
| `e` — Edit JSON | Open a temporary draft containing the profile and complete program driver in a text editor |
| `a` — Add option | Collect a category, literal flag, argument placeholder, argument optionality, and summary |
| `m` — Manual import | Replace the draft profile from an installed page, rendered UTF-8 text, or local roff/compressed file |
| `p` — Preview | Open the actual categorized help browser using the current draft |
| `v` — Validate | Check profile and driver schemas, command identity, and built-in global-option compatibility |
| `s` — Save | Confirm replacement of the profile and driver, create backups, and record the review result |
| `b` — Back | Return to the queue; modified drafts require explicit discard |

## Guided corrections

Guided editing requires no external editor. Option, category, and driver-route
selection lists support next/previous pages and a case-insensitive text filter.
Each field shows its current value. Enter retains that value, `/clear` empties
an optional field, and `/cancel` discards the entire current operation.
Description and detail fields also accept `/lines` for multiline text: enter a
single `.` to finish or `..` to insert a literal dot line. Ctrl-C cancels the
operation and returns to the entry without applying its partial changes.

An existing option's flag, summary, detail, argument placeholder, and argument
optionality can be corrected through **Options → Edit**. Clearing the argument
placeholder removes both its value requirement and optionality metadata.
**Options → Move/reorder** selects a destination category and position, with
an additional choice to create a new category for the moved option. Moving or
deleting the final option in a category removes that empty category.

**Categories → Edit** changes the name and description. Move/reorder changes its
display position. The top-level description action updates the profile's introductory
text. Deletion requires confirmation and removes all options in that category.
Deleting all categories leaves an incomplete draft; add an option or import a
manual before previewing or saving it. Duplicate names and duplicate flags are
rejected.

**Driver → Global options** accepts space-separated flags in two lists: options
requiring values and boolean flags. **Driver → Route settings** selects an
existing path and edits its manual page, fixed help arguments, and stop-at-first-
positional-argument behavior. Help arguments omit the executable name; for
example, `help run` represents two fixed arguments. Clearing help arguments
disables executable help for that route; a manual source must then remain.
Built-in global-option arity remains enforced, and built-in globals remain active
through the existing overlay rules. Command and subcommand path identities remain
unchanged. Other routes retain their settings unless separately selected.

Each guided operation validates its complete result before updating draft text.
Invalid flags, conflicting arity, missing documentation sources, and cancelled
operations leave the previous draft intact. Guided edits do not run editors,
manual renderers, executable help, or target commands. Preview and Save retain
their existing behavior; the collection changes only after explicit saving.

## Optional JSON editing

JSON editing uses `VISUAL`, then `EDITOR`, then `vi`. Editor arguments are
split into an argument list without shell evaluation. For example:

```bash
export EDITOR='nano'
python3 cli_help/main.py --review-report ./generated-help/scan-report.json
```

The draft has two top-level objects, `profile` and `driver`, using the schemas
documented in the [profile and driver reference](profiles-and-drivers.md).
Correct category names, option flags, descriptions, required or
optional arguments, global-option arity, manual names, and positional boundaries
in these objects. The complete existing driver is included so unrelated routes
remain present unless explicitly edited. The selected command path cannot be
renamed during review. Missing profiles start with an empty category list; add
options or import documentation before previewing or saving. Invalid editor text
remains available for correction through Edit JSON and cannot be saved.

## Preview behavior

Preview supports the same scrolling, searching, category navigation, and
`CLI_HELP_CONFIG` keybindings as the Bash browser. Its title reads **Help preview**.
Enter inspects the selected flag and returns to review. Preview does not emit a
Readline edit response, run discovery, or execute a target command. Manual import
reads text or invokes only the bounded manual renderer. Edited executable help
routes are schema-validated but never exercised during review; normal discovery
rules apply when those drivers are later activated.

## Saving and review evidence

Saving validates both documents, then writes the collection's profile and driver.
The report retains its original scan status, diagnostics, and summary. A separate
`review` result records the saved paths, option count, timestamp, content hashes,
and backup location. `review_summary` summarizes review state at the last save.
Resolved entries leave the default queue. File hashes are checked when the queue
is reopened; changes to either the profile or shared program driver make the
review stale. Resolving an entry records a documentation review, not verified
command behavior or exhaustive option coverage.

## Collection scope and recovery

The collection is the report's parent directory; embedded report paths do not
redirect writes. Keep the report beside its `profiles/` and `drivers/` directories.
The scanner and importer locks are held throughout the review session. External
changes to selected files, the report, or collection filenames prevent saving
until the session is reopened. Malformed existing collection files must be
corrected before opening the reviewer. Unsupported executable names and option
forms outside the existing literal schemas cannot be enabled through review.

Before every save, existing profile, driver, and report bytes are copied into
`.review-backups/<unique-id>/`. Its `manifest.json` maps each backup to a
collection-relative filename and records files that did not previously exist.
Writes are atomic per file, not transactional across all three files. After an
incomplete save, inspect the backup and current files, restore individual files
as needed, and reopen the reviewer. A report write occurs only after both
configuration writes succeed. A subsequent bulk scan replaces the report,
including its review annotations, while preserving corrected files by default.

## Exit and cancellation

Quit returns status 0. Ctrl-C at the queue or terminal EOF returns 130 and
discards unsaved drafts; Ctrl-C within an entry cancels the action and retains
the draft. Saved changes remain. The reviewer does not alter active environment
variables or shell startup files; the [collection activation procedure](bulk-scan.md#activating-a-collection)
continues to apply.
