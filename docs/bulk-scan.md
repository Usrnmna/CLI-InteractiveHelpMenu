# Bulk scanning and scan-report interpretation

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Bulk scanning of installed commands

The scanner inventories executable files in `PATH` and imports their installed
manuals into the same editable profile and driver format:

```bash
python3 cli_help/main.py --scan-installed \
  --output-dir "$HOME/.config/cli-help/scanned"
```

Activate the collection after inspecting its report and generated files. A scan
with no successful imports does not create profile or driver directories.
The scanner invokes only the manual renderer with fixed arguments; it never
invokes an inventoried command, falls back to its `--help`, or reads the pending
Bash buffer. Imported static profiles retain literal option insertion without
executing the pending command. Existing discovery settings continue to govern
commands that have no imported profile.

## First collection walkthrough

A bounded first scan limits manual-rendering attempts while retaining a report
of successful imports and entries requiring adjustment:

```bash
python3 cli_help/main.py --scan-installed --limit 100 \
  --output-dir "$HOME/.config/cli-help/scanned"

python3 cli_help/main.py --review-report \
  "$HOME/.config/cli-help/scanned/scan-report.json"
```

In a review entry, **o** edits options, **c** edits categories, and **d** edits
driver settings. **p** previews the menu and **s** saves validated changes with
backups. Original scan findings remain available. The
[guided review guide](review.md) explains the forms and save behavior.

Per-record generation uses the same structurally checked collection writer as
manual import. Replacing a profile retains prior authored evidence without
inventing numerical meanings or promoting review status. The
[numerical authoring reference](numerical-inventory/step6-authoring.md) explains
reviewing unannotated values and preserving optional metadata through corrections.

Continue with activation only when the collection contains successfully generated
profile and driver directories. A zero-success scan does not create them.

## Activating a collection

After inspecting the [scan report](#report-statuses-and-diagnostics) and correcting
entries through the [interactive reviewer](review.md), enable the generated files:

```bash
export CLI_HELP_PROFILES="$HOME/.config/cli-help/scanned/profiles"
export CLI_HELP_DRIVERS="$HOME/.config/cli-help/scanned/drivers"
python3 cli_help/main.py --check
```

These exports select the collection in the current shell. To load it in future
sessions, place the exports before the adapter's source statement or managed
startup block. A selected driver directory replaces the previously selected
custom driver collection; [manual composition](profiles-and-drivers.md#activation-and-manual-composition)
describes combining collections. Bundled profiles remain available unless replaced
by a matching custom profile.

## Filters and scan limits

Filters and limits support smaller scans:

```bash
python3 cli_help/main.py --scan-installed --scan-path /usr/bin \
  --include 'git*' --include 'ffmpeg' --exclude 'git-upload-*' \
  --limit 100 --scan-subcommands \
  --output-dir "$HOME/.config/cli-help/scanned"
```

| Option | Behavior |
| --- | --- |
| `--scan-path DIR` | Inventory this directory instead of `PATH`; repeat for several directories |
| `--include GLOB` | Select executable basenames; repeated patterns are combined |
| `--exclude GLOB` | Omit matching basenames; exclusions take precedence |
| `--limit N` | Cap manual-rendering attempts, including failed attempts; preserved entries do not consume the limit; zero means unlimited |
| `--scan-subcommands` | Include paths declared by built-in or `CLI_HELP_DRIVERS` drivers; only routes with manual names can be imported |
| `--replace` | Regenerate selected existing profiles/routes; other entries remain unchanged |
| `--strict-scan` | Return a nonzero status for entries requiring manual adjustment |

Directory traversal is nonrecursive. Duplicate basenames follow `PATH` precedence;
shadowed paths are recorded. Executable symlinks retain their invocation names.
Shell aliases, functions, and builtins are not enumerated. Manual lookup searches
sections 1 and 8 using the configured manual route or executable basename.
Hyphenated filenames do not imply subcommands. Newly generated drivers retain
known global-option arity and positional boundaries from loaded drivers.

## Report statuses and diagnostics

Progress goes to standard error. Standard output contains a JSON summary and the
path to `OUTPUT_DIR/scan-report.json`. The report contains inventory warnings,
global errors, settings, timestamps, per-command diagnostics, generated file
paths, option counts, and suggested actions:

| Status | Meaning |
| --- | --- |
| `success` | A valid profile and driver route were written with no detected review issues |
| `needs_adjustment` | A manual is missing or unparseable, a route/name is unsupported, or generated documentation needs review |
| `failed` | Rendering, timeout, output-limit, or file-writing failure |
| `skipped` | Filtered, beyond the limit, already present, interrupted, or prevented by a scan-wide error |

The separate `generated` field distinguishes usable generated output that needs
review from cases that produced no profile. Review heuristics flag unparsed
option-like lines and root-only coverage of known subcommand programs. Wrapped
prose and examples can trigger these heuristics. Absence of a warning does not
prove completeness or correct argument arity; inferred documentation requires
comparison with the applicable command version before relying on its coverage.

Missing manuals can be installed separately or supplied through `--import-man`.
Unsupported forms can be represented by manually edited profiles where the
literal flag schema permits them. The renderer uses the existing
`CLI_HELP_DISCOVERY_TIMEOUT` setting and 512 KiB output limit per manual.
The process limits do not sandbox the manual renderer.

## Repeated scans and interruption recovery

Existing profiles or driver routes are preserved before rendering unless
`--replace` is supplied. Collection validation and indexing occur once per scan.
The JSON report is replaced atomically after each processed entry and at scan
completion. Repeating a scan skips completed entries and retries failures;
failed attempts still consume the limit, so filters may be needed to advance
past repeated failures. A new scan replaces the previous report at the same path.
Graceful Ctrl-C retains completed results and reports remaining jobs as skipped.
An abrupt process termination may leave a checkpoint with `finished: false`.
The `.scan.lock` prevents overlapping report writers, and `.import.lock` excludes
concurrent imports. Inspect stopped processes and partial profile/driver pairs
before removing stale locks or using `--replace` to reconcile incomplete writes.

Exit status is 0 for a completed scan without operational errors, 1 for failed
entries, inventory warnings, global errors, or strict-mode review issues, and 130
for an interrupted active scan. Ordinary argument errors use argparse status 2.
