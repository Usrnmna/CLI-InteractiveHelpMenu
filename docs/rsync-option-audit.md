# Bundled rsync option audit

The offline menu covers 29 client options. Each entry was checked against the
option definition in all three manuals below. The menu row states the effect.
The Details pane explains conditions that can change the result, such as which
files a filter protects, when a transfer is skipped, or how a rate is interpreted.

| Manual | Documented version | Client summary rows | Selectable | Other client rows | Daemon summary rows |
| --- | --- | ---: | ---: | ---: | ---: |
| [Ubuntu 24.04 LTS](https://manpages.ubuntu.com/manpages/noble/man1/rsync.1.html) | 3.2.7-1ubuntu1.5 | 144 | 29 | 115 | 14 |
| [Ubuntu 26.04 LTS](https://manpages.ubuntu.com/manpages/resolute/man1/rsync.1.html) | 3.4.1+ds1-7ubuntu0.3 | 144 | 29 | 115 | 14 |
| [Upstream rsync](https://download.samba.org/pub/rsync/rsync.1) | 3.5.2 | 157 | 29 | 128 | 16 |

Counts follow the printed **Option Summary**. Aliases on one row count once.
Daemon startup has a separate summary, including some spellings shared with the
client. All daemon startup entries are manual-only.

## Selectable client options

| Menu category | Options | Details that affect use |
| --- | --- | --- |
| Transfer | `--archive`, `--recursive`, `--update`, `--ignore-existing` | Archive's implied flags and recursion exception with `--files-from`. Newer-file checks and the treatment of existing directories. |
| Preview | `--dry-run`, `--itemize-changes` | How to list proposed changes, read an itemized record and interpret transfer statistics during a trial run. |
| Filtering | `--exclude`, `--include`, `--exclude-from` | First-match order, directory traversal, shell quoting and rules read from a file or standard input. |
| Output | `--verbose`, `--progress`, `--human-readable`, `--stats`, `--quiet` | Per-file and overall progress, repeated flags, literal and matched data, and error output. Upstream 3.5.2 adds an `i` to binary units. The two Ubuntu manuals use the same unit letters for both scales. |
| Network | `--compress`, `--bwlimit`, `--timeout`, `--rsh` | Compression negotiation, average socket rate and rounding, I/O inactivity, and quoting a remote-shell command with arguments. |
| Attributes | `--acls`, `--xattrs`, `--hard-links`, `--numeric-ids` | Filesystem and privilege limits, links within the transfer set, and numeric ownership mapping. |
| Deletion | `--delete`, `--delete-after` | Which directories are eligible, exclusions and sender errors, previewing deletions, and when per-directory rules take effect. |
| Comparison | `--checksum`, `--size-only` | How rsync chooses files for transfer, which side reads file data, and why equal sizes alone can miss changed content. |
| Recovery | `--partial`, `--backup`, `--backup-dir` | Reuse of partial data, which destination files become backups, and how the backup path and suffix are resolved. |

## Client options available in the manuals

The following client summary entries are outside the bundled selection in both
Ubuntu releases. Each entry uses its first printed spelling. The linked manuals
include aliases, operands, complete filter syntax and examples. Some of these
options appear in the menu as cross-references.

`--info`, `--debug`, `--stderr`, `--no-motd`, `--no-OPTION`, `--relative`,
`--no-implied-dirs`, `--suffix`, `--inplace`, `--append`, `--append-verify`, `--dirs`,
`--old-dirs`, `--mkpath`, `--links`, `--copy-links`, `--copy-unsafe-links`, `--safe-links`,
`--munge-links`, `--copy-dirlinks`, `--keep-dirlinks`, `--perms`, `--executability`,
`--chmod`, `--owner`, `--group`, `--devices`, `--copy-devices`, `--write-devices`,
`--specials`, `-D`, `--times`, `--atimes`, `--open-noatime`, `--crtimes`,
`--omit-dir-times`, `--omit-link-times`, `--super`, `--fake-super`, `--sparse`,
`--preallocate`, `--whole-file`, `--checksum-choice`, `--one-file-system`, `--block-size`,
`--rsync-path`, `--existing`, `--remove-source-files`, `--del`, `--delete-before`,
`--delete-during`, `--delete-delay`, `--delete-excluded`, `--ignore-missing-args`,
`--delete-missing-args`, `--ignore-errors`, `--force`, `--max-delete`, `--max-size`,
`--min-size`, `--max-alloc`, `--partial-dir`, `--delay-updates`, `--prune-empty-dirs`,
`--usermap`, `--groupmap`, `--chown`, `--contimeout`, `--ignore-times`, `--modify-window`,
`--temp-dir`, `--fuzzy`, `--compare-dest`, `--copy-dest`, `--link-dest`,
`--compress-choice`, `--compress-level`, `--skip-compress`, `--cvs-exclude`, `--filter`,
`-F`, `--include-from`, `--files-from`, `--from0`, `--old-args`, `--secluded-args`,
`--trust-sender`, `--copy-as`, `--address`, `--port`, `--sockopts`, `--blocking-io`,
`--outbuf`, `--8-bit-output`, `-P`, `--remote-option`, `--out-format`, `--log-file`,
`--log-file-format`, `--password-file`, `--early-input`, `--list-only`, `--stop-after`,
`--stop-at`, `--fsync`, `--write-batch`, `--only-write-batch`, `--read-batch`, `--protocol`,
`--iconv`, `--checksum-seed`, `--ipv4`, `--ipv6`, `--version`, `--help`.

The upstream 3.5.2 client summary also gives these spellings their own rows.

`--inc-recursive`, `--no-inc-recursive`, `--no-i-r`, `--old-d`, `--insecure-links`,
`--confine-root`, `--drop-D`, `--no-whole-file`, `--ignore-non-existing`,
`--delay-symlinks`, `--compress-threads`, `--nice`, `--no-nice`.

A separate row can reflect a documentation change. For example, Ubuntu lists
`--old-d` on the same row as `--old-dirs`. The row counts do not establish when
an option was implemented.

## Rendered-menu verification

The terminal regression opens the bundled profile in Bash with discovery off.
It checks the preview and deletion guidance in a 120×40 tmux pane, scrolls to the
last line at 60×16, then verifies that cancellation preserves the pending
command and cursor. A shell stub detects accidental execution.

Run the focused regression from the repository root in the
[local sandbox](development.md#isolated-local-debugging).

```bash
python3 -I tests/run_sandbox.py -- python3 -m unittest discover -s tests \
  -p test_terminal_screen.py -k test_rsync_preview_and_deletion_guidance_is_readable -v
```

All 29 summaries and full descriptions appeared in a 160×80 tmux pane on
Ubuntu 24.04.5 with Python 3.10.20 and 3.12.3 and on Ubuntu 26.04.1 with
Python 3.14.4. Each offline full suite ran 1,328 tests with 1,327 passes and one
Windows-specific skip. These checks exercised menu rendering and shell editing
without starting an rsync transfer.
