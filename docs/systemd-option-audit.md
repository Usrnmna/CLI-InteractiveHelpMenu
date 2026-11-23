# systemd option audit

The bundled profiles contain 50 selectable spellings. Eleven options recur in three `systemctl` menus, two more belong to `systemctl show`, and fifteen belong to `journalctl`. The review retains their order, argument contracts and literal insertion. The descriptions now follow the selected command: the same spelling can select units, include empty properties, format a table or affect only a journal excerpt.

## Sources

| Manual | Upstream systemd 262 | Ubuntu 24.04 LTS, 255.4-1ubuntu8.18 | Ubuntu 26.04 LTS, 259.9-0ubuntu0.1 |
| --- | --- | --- | --- |
| systemctl(1) | [Unit commands and options](https://www.freedesktop.org/software/systemd/man/262/systemctl.html) | [Noble systemctl](https://manpages.ubuntu.com/manpages/noble/man1/systemctl.1.html) | [Resolute systemctl](https://manpages.ubuntu.com/manpages/resolute/man1/systemctl.1.html) |
| journalctl(1) | [Journal sources, filtering and output](https://www.freedesktop.org/software/systemd/man/262/journalctl.html) | [Noble journalctl](https://manpages.ubuntu.com/manpages/noble/man1/journalctl.1.html) | [Resolute journalctl](https://manpages.ubuntu.com/manpages/resolute/man1/journalctl.1.html) |

The structured value records retain their systemd 257 scope. The option parsers and output routines resolve gaps between the manuals and the two Ubuntu binaries. [Tagged upstream systemctl manual](https://github.com/systemd/systemd/blob/v262/man/systemctl.xml) · [Tagged upstream journalctl manual](https://github.com/systemd/systemd/blob/v262/man/journalctl.xml) · [257 systemctl](https://github.com/systemd/systemd/blob/v257/man/systemctl.xml) · [257 journalctl](https://github.com/systemd/systemd/blob/v257/man/journalctl.xml)

## Disposition of the original systemctl entries

Each cell is a disposition for one selectable row in the indicated profile. “Sufficient” means the original summary correctly answered what the option does. Some of those rows now carry a default or an invocation detail.

| Option | [list-units](../profiles/systemctl-list-units.json) (11) | [show](../profiles/systemctl-show.json) (13) | [status](../profiles/systemctl-status.json) (11) |
| --- | --- | --- | --- |
| `--user` | Sufficient. Identify the calling user's manager. | Sufficient. Select that manager for properties. | Sufficient. Select that manager for status. |
| `--system` | Sufficient. Mark the system manager as the default. | Sufficient. Same default. | Sufficient. Same default. |
| `--no-pager` | Sufficient. Keep the one-line explanation. | Sufficient. Keep. | Sufficient. Keep. |
| `--no-legend` | Incomplete. Suppress column headers and the footer with counts and hints. | Inaccurate. Properties have no table legend. Use `--value` to omit names. | Inaccurate. A status heading is separate from a table legend. |
| `--full` | Sufficient. Long names and descriptions can exceed terminal width. | Inaccurate. Property output already has its own representation. | Incomplete. Full width also affects the process tree and journal text. |
| `--all` | Incomplete. Include inactive units in memory and units following another unit. Installed templates belong to `list-unit-files`. | Inaccurate. Include empty properties. Without operands or filters, this still inspects the manager. | Incomplete. With no operands or filters, the manager overview is followed by status for all units in memory. |
| `--type=` | Incomplete. Accept a comma-separated list. `help` lists supported types. | Incomplete. Filters enumeration or glob expansion. An explicit name is looked up directly. | Incomplete. Applies to unit selection, with the same explicit-name rule. |
| `--state=` | Incomplete. Alternatives may be load, active or substate names. | Incomplete. Filters enumerated units, including glob matches. | Incomplete. `--state=failed` without an operand selects failed units. A named unit is inspected directly. |
| `--plain` | Incomplete. Hide the status-symbol column in the unit listing. | Inaccurate. Property output has no such column. | Inaccurate. The option preserves the normal status heading and process tree. |
| `--lines=` | Redundant. Retain the status-only scope. The value does not limit unit rows. | Redundant. Retain the status-only scope. Select property fields with `--property=`. | Redundant. Keep the required count, default of 10 and zero to hide the journal. |
| `--output=` | Inaccurate. JSON modes serialize the unit table. Journal text modes produce the ordinary table. | Inaccurate. JSON mode preserves the normal property representation. | Incomplete. Format the journal excerpt, with the rest of the report in its usual form. |
| `--property=` | — | Incomplete. Select by name, comma-separated list or repeated option. An explicitly requested empty property is shown. | — |
| `--value` | — | Sufficient. Pair with `--property=MainPID` to print its value alone. | — |

Both Ubuntu manuals describe `--output=` under `status`. The table serializer also uses it for `list-units`. The pinned guidance now identifies compact, indented, server-sent-event and text-sequence JSON for the table. The `status` and `journalctl` guides also restore `short-delta`, which adds elapsed time since the preceding entry to a monotonic timestamp. [257 table serializer](https://github.com/systemd/systemd/blob/v257/src/systemctl/systemctl-util.c) · [Unit table rendering](https://github.com/systemd/systemd/blob/v257/src/systemctl/systemctl-list-units.c) · [Journal output modes](https://github.com/systemd/systemd/blob/v257/man/journalctl.xml)

All three manuals document the legend switch as `--legend=BOOL`. The bundled `--no-legend` remains an accepted compatibility spelling. Version 262 documents an empty `--type=` or `--state=` for resetting a filter. Both Ubuntu clients reject the empty value. Their `show` and `status` implementations send globs through filtered unit enumeration and look up literal names directly. [255 option parser](https://github.com/systemd/systemd/blob/v255/src/systemctl/systemctl.c) · [259 option parser](https://github.com/systemd/systemd/blob/v259/src/systemctl/systemctl.c) · [Name expansion](https://github.com/systemd/systemd/blob/v259/src/systemctl/systemctl-util.c) · [Operand and manager selection](https://github.com/systemd/systemd/blob/v259/src/systemctl/systemctl-show.c)

## Disposition of the original journalctl entries

| [Journal option](../profiles/journalctl.json) | Disposition | Menu decision |
| --- | --- | --- |
| `--unit=` | Incomplete | Match a unit name or a quoted glob. Repetition adds units. Related manager and coredump records can match. With `--user`, the match is on user units. |
| `-u` | Incomplete | Give the same scope and retain the separate operand. |
| `--follow` | Incomplete | Normally start with ten recent entries, then stream. Use `--lines=0` for new entries only or `--since=` for a start time. |
| `-f` | Incomplete | Retain the same follow behavior and Ctrl-C exit. |
| `--since=` | Redundant | Keep the inclusive lower bound and the calendar, relative, zone and epoch forms. Quote a timestamp containing spaces. |
| `--until=` | Redundant | Keep the inclusive upper bound. A date without a time ends at midnight at the start of that date. |
| `--priority=` | Redundant | Distinguish a threshold from an inclusive range. The structured guidance preserves all eight names and their numerical order. |
| `--output=` | Incomplete | Identify the default, message-only, JSON and verbose formats. Restore `short-delta` in the format list. |
| `--no-pager` | Sufficient | Keep the original explanation. |
| `--system` | Incomplete | Select the system journal, including kernel messages. Access permissions still apply. |
| `--user` | Incomplete | Select the calling user's journal. Per-user journals require persistent logging. |
| `--reverse` | Sufficient | Keep the order and explain incompatibility with follow and oldest-first counts. |
| `--directory=` | Incomplete | Replace the usual journal locations with the supplied directory. |
| `--boot=` | Inaccurate | Distinguish the bare flag from the inserted equals spelling. Document selection in an external directory and the Ubuntu 24.04 ID-relative offset discrepancy. |
| `--lines=` | Inaccurate | Count entries. The clients accept zero, bare `--lines` means ten, and an empty joined value is rejected. `+N` selects the oldest N and conflicts with reverse or follow. |

The journal manuals describe a positive count and an optional boot operand. The parsers accept a zero count and distinguish an omitted operand from an explicitly empty string. The manuals describe offsets relative to a boot ID. In 255 the selection path for a supplied ID finds that ID without applying its parsed offset. The later implementation passes the ID and offset together. The structured record for 257 also now distinguishes the local current boot from the newest recorded boot in a supplied directory. [255 boot selection and count parser](https://github.com/systemd/systemd/blob/v255/src/journal/journalctl.c) · [257 boot selection](https://github.com/systemd/systemd/blob/v257/src/journal/journalctl-util.c) · [259 boot selection](https://github.com/systemd/systemd/blob/v259/src/journal/journalctl-util.c)

## Manual-only coverage

The 50 entries are a curated selection. Other documented systemctl options include dependency expansion, job modes, timestamps, host and container selection, and unit-file operations. Commands such as `list-unit-files` and `list-dependencies` have their own output rules. Journal filtering also supports field matches, identifiers, cursors, kernel records, regular expressions and individual journal files. Rotation, vacuuming and sealing belong to the journal maintenance reference. Resolute and upstream also document invocation selection, introduced in 257 and absent from Noble's journal manual. These reviews count only the four bundled profiles.

## Executable checks

The Ubuntu 26.04 offline sandbox ran the installed 259.9 clients and the extracted Ubuntu 24.04 255.4 clients with their matching private systemd library. A disposable D-Bus service answered queries about three synthetic units. A journal import from generated records provided two boot IDs. These fixtures exercised the clients without connecting to a host manager or reading a host journal. The Bash menu tests below ran separately on each target. [Ubuntu 24.04 client package](https://archive.ubuntu.com/ubuntu/pool/main/s/systemd/systemd_255.4-1ubuntu8.18_amd64.deb)

| Fixture | Observed result |
| --- | --- |
| Unit table | Both clients returned the active service and timer as JSON. `--all` included the inactive service. `--state=inactive` selected it. Both rejected an empty type or state filter. All four JSON modes serialized the table. The `short-delta`, `cat` and `export` modes printed the ordinary unit table. |
| Properties and status | EmptyText disappeared from ordinary `show` output and appeared as `EmptyText=` with `--all`. `--property=Id --value` printed just the unit name. An explicitly named active service still produced properties and status under mismatched filters. `show --output=json --property=Id` printed `Id=alpha.service`. |
| Boot selection | In the fixture directory, bare `--boot` and `--boot=0` both selected the newest boot. Offsets `1` and `-1` selected the first of two boots. Given the first ID followed by `+1`, 255.4 returned the first boot and 259.9 returned the second. Both rejected an empty `--boot=`. |
| Counts and order | With twelve records, bare `--lines` returned ten, `all` returned twelve, and `0` returned none. `2` and `+2` selected opposite ends. Both clients rejected an empty `--lines=`, reverse combined with follow, and reverse combined with `+2`. |
| Other journal filters | A quoted unit pattern selected the matching service. A warning threshold included more severe events. Entries exactly on both requested time bounds appeared. Reverse output began with the newest event. |

## Rendered menus and offline suite

Each target opened all four bundled menus in real Bash/tmux sessions with discovery disabled. At 210×100 the highlighted label, summary and complete Details pane were checked for every row. Cancelling from each menu preserved the original pending line and Readline cursor. Selection inserted the literal `--output=`, `--property=`, `--lines=` and `--boot=` in the list, show, status and journal menus respectively, before an existing ` --no-pager` suffix. Stub functions would have recorded any execution of the pending command. No execution occurred.

At 60×16 each menu opened unfiltered. Searching for “machine-readable rows”, “even when it is empty”, “hide the journal excerpt” and “ignores the offset” found the applicable entry in each. Scrolling reached the qualification in its Details pane. The journal regression also cancelled, reopened the menu, selected `--boot=` and typed `-1`. The buffer contained `journalctl --boot=-1 --no-pager` with the cursor after the offset. [Terminal regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The 13 focused checks on each target covered the new regression, system profile declarations and insertion, numeric severity and boot guidance, and inventory completeness. Review of the 58 changed fingerprints covered the four profile files and headers, category descriptions and affected option records. The review preserved existing classifications and updated the fingerprints after checking the new facts. [Numerical inventory review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 13 / 0 / 0 | 1,340 / 0 / 1 | 476.686 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 13 / 0 / 0 | 1,340 / 0 / 1 | 534.321 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 13 / 0 / 0 | 1,340 / 0 / 1 | 476.927 s |

The full runs included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. The skip on each target was the Windows-only probe limitation. Results are from the local offline matrix.
