# Bundled GNU tar option audit

The first-pass [tar menu](../profiles/tar.json) had 12 selectable entries. The [full manual-coverage revisit](tar-manual-coverage.md) records the expanded inventory and subsequent verification. The most
consequential edit concerns `--directory` (`-C`). For example, in
`tar -c -C src -f backup.tar main.c`, tar looks for `main.c` in `src`
and writes `backup.tar` in the directory where tar started.

## Manuals and versions

| Source | Version reviewed | Scope |
| --- | --- | --- |
| [GNU tar manual](https://www.gnu.org/software/tar/manual/tar.html) | 1.35.90 | Published online edition, including operations, option summary and worked examples. |
| [GNU tar release source](https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz) | 1.35 | The packaged manual in `doc/tar.texi` provides the release reference for the Ubuntu base version. |
| [Ubuntu 24.04 LTS tar(1)](https://manpages.ubuntu.com/manpages/noble/man1/tar.1.html) | 1.35+dfsg-3ubuntu0.4 | Operation modes, option declarations, operands and exit status. |
| [Ubuntu 26.04 LTS tar(1)](https://manpages.ubuntu.com/manpages/resolute/man1/tar.1.html) | 1.35+dfsg-4ubuntu0.4 | Same 12 declarations and definitions as the Noble page. |

The Ubuntu pages describe `-C` as applying to all following options. GNU's
working-directory chapter gives the more precise rule and explicitly documents
the exception for archive paths. The 1.35 release manual also illustrates
successive directory changes. [GNU working-directory examples](https://www.gnu.org/software/tar/manual/tar.html#directory)

## Disposition of the 12 entries

| Entry | Assessment of previous wording | Result in the menu |
| --- | --- | --- |
| `--create` | Summary sufficient. Replacement behavior missing. | Retains the summary. Explains that creation replaces an existing output archive and normally descends into named directories. |
| `--extract` | Summary sufficient. Selection and destination unclear. | Explains extraction of all or named members, stored names, the default working directory and possible replacement of existing files. |
| `--list` | Summary sufficient. Optional member selection missing. | Explains how to list a subset and use a verbose listing for file metadata. |
| `--diff` | Summary sufficient. Direction and result missing. | Explains content and metadata comparison, treatment of disk-only files and exit status 1 for differences. |
| `--file=` | Incomplete. The original row left the archive and member roles implicit. | Identifies the archive to read or write. Details distinguish member operands and explain local names containing a colon. Existing value guidance covers standard streams. |
| `--directory=` | Incomplete. The row omitted argument order. | Identifies following file names, successive relative directory changes and the exception for the archive path. |
| `--exclude=` | Incomplete. “Matching” left the pattern type and shell behavior implicit. | Identifies wildcards, shell quoting and where to put an exclusion when creating an archive. |
| `--gzip` | Incomplete. The row described compression only. | Covers writing and reading gzip, automatic detection for regular files and explicit selection for streams. |
| `--xz` | Incomplete. Reading xz archives was implicit. | Gives the same distinction for xz files, pipes and non-seekable tapes. |
| `--bzip2` | Incomplete. Reading bzip2 archives was implicit. | Gives the same distinction for bzip2 files, pipes and non-seekable tapes. |
| `--verbose` | Summary sufficient. The effect during listing was unclear. | Retains the summary and distinguishes listing metadata from the member names shown during creation or extraction. |
| `--totals` | Incomplete. Timing and signal form omitted. | The bare option reports bytes at completion. Details explain the documented attached `=SIGNAL` form. Selection still inserts the bare flag. |

GNU describes member selection under [listing](https://www.gnu.org/software/tar/manual/tar.html#list),
[extraction](https://www.gnu.org/software/tar/manual/tar.html#extract) and
[comparison](https://www.gnu.org/software/tar/manual/tar.html#compare). The
[exclusion](https://www.gnu.org/software/tar/manual/tar.html#exclude) and
[compressed archive](https://www.gnu.org/software/tar/manual/tar.html#gzip)
chapters explain shell expansion and stream handling.

## Manual-only coverage

Each Ubuntu page declares the same 169 distinct long spellings. Twelve have
selectable rows. The other 157 include aliases such as `--get`, `--compare`
and `--gunzip`, as well as separate operations such as `--append` and
`--delete`. Short aliases and optional operands do not add selectable rows.
The compatibility meaning of the short-only `-o` is also manual-only.

<details>
<summary>157 Ubuntu long spellings outside the curated selection</summary>

`--absolute-names`, `--acls`, `--add-file`, `--after-date`, `--anchored`, `--append`,
`--atime-preserve`, `--auto-compress`, `--backup`, `--block-number`, `--blocking-factor`,
`--catenate`, `--check-device`, `--check-links`, `--checkpoint`, `--checkpoint-action`,
`--clamp-mtime`, `--compare`, `--compress`, `--concatenate`, `--confirmation`,
`--delay-directory-restore`, `--delete`, `--dereference`, `--exclude-backups`,
`--exclude-caches`, `--exclude-caches-all`, `--exclude-caches-under`, `--exclude-from`,
`--exclude-ignore`, `--exclude-ignore-recursive`, `--exclude-tag`, `--exclude-tag-all`,
`--exclude-tag-under`, `--exclude-vcs`, `--exclude-vcs-ignores`, `--files-from`,
`--force-local`, `--format`, `--full-time`, `--get`, `--group`, `--group-map`, `--gunzip`,
`--hard-dereference`, `--help`, `--hole-detection`, `--ignore-case`,
`--ignore-command-error`, `--ignore-failed-read`, `--ignore-zeros`, `--incremental`,
`--index-file`, `--info-script`, `--interactive`, `--keep-directory-symlink`,
`--keep-newer-files`, `--keep-old-files`, `--label`, `--level`, `--listed-incremental`,
`--lzip`, `--lzma`, `--lzop`, `--mode`, `--mtime`, `--multi-volume`,
`--new-volume-script`, `--newer`, `--newer-mtime`, `--no-acls`, `--no-anchored`,
`--no-auto-compress`, `--no-check-device`, `--no-delay-directory-restore`,
`--no-ignore-case`, `--no-ignore-command-error`, `--no-null`, `--no-overwrite-dir`,
`--no-quote-chars`, `--no-recursion`, `--no-same-owner`, `--no-same-permissions`,
`--no-seek`, `--no-selinux`, `--no-unquote`, `--no-verbatim-files-from`, `--no-wildcards`,
`--no-wildcards-match-slash`, `--no-xattrs`, `--null`, `--numeric-owner`, `--occurrence`,
`--old-archive`, `--one-file-system`, `--one-top-level`, `--overwrite`, `--overwrite-dir`,
`--owner`, `--owner-map`, `--pax-option`, `--portability`, `--posix`, `--preserve-order`,
`--preserve-permissions`, `--quote-chars`, `--quoting-style`, `--read-full-records`,
`--record-size`, `--recursion`, `--recursive-unlink`, `--remove-files`, `--restrict`,
`--rmt-command`, `--rsh-command`, `--same-order`, `--same-owner`, `--same-permissions`,
`--seek`, `--selinux`, `--show-defaults`, `--show-omitted-dirs`, `--show-stored-names`,
`--show-transformed-names`, `--skip-old-files`, `--sort`, `--sparse`, `--sparse-version`,
`--starting-file`, `--strip-components`, `--suffix`, `--tape-length`, `--test-label`,
`--to-command`, `--to-stdout`, `--touch`, `--transform`, `--uncompress`, `--ungzip`,
`--unlink-first`, `--unquote`, `--update`, `--usage`, `--use-compress-program`, `--utc`,
`--verbatim-files-from`, `--verify`, `--version`, `--volno-file`, `--warning`,
`--wildcards`, `--wildcards-match-slash`, `--xattrs`, `--xattrs-exclude`,
`--xattrs-include`, `--xform`, `--zstd`.

</details>

The online GNU [operation and option summaries](https://www.gnu.org/software/tar/manual/tar.html#All-Options)
also have 169 distinct long spellings. Their headings include
`--show-snapshot-field-ranges` and describe `--usage` elsewhere. These counts
compare documentation headings and include aliases. They do not date the
introduction of either option.

## Sandbox verification

A real Bash/tmux session with discovery disabled displayed all 12 summaries
and their full edited descriptions at 160×56 on each target. The tar command
in the test shell was a stub that records accidental execution. The focused
regression searches for “original working directory”, scrolls to the archive
path exception at 60×16, cancels to the original midline cursor, then inserts
`--directory=` before the existing member operand. The stub remained unused.

Run the regression from the checkout with the [offline sandbox runner](development.md#isolated-local-debugging).

```bash
python3 -I tests/run_sandbox.py -- python3 -m unittest discover -s tests \
  -p test_terminal_screen.py -k test_tar_directory_scope_search_cancel_and_insertion -v
```

The three focused host tests passed. A separate search from the unfiltered
host menu moved the selection from `--create` to `--directory=`. Each full
offline run included the new audit and the terminal regression.

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 26.04.1 LTS | 3.14.4 | 1,328 | 0 | 1 |
| 24.04.5 LTS | 3.10.20 | 1,328 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,328 | 0 | 1 |

The skip on each target was the Windows-specific probe test. The manuals
establish the documented archive behavior. The sandbox results establish
menu rendering, search and shell editing for the bundled profile.
