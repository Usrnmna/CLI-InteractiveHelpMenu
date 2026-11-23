# GNU tar manual coverage

The menu groups **157 distinct options** by purpose. The 12 original options retain their insertion spelling. The other 145 have new rows. All 59 aliases appear in their primary row’s searchable Details and select that row’s literal spelling. The 216 spellings comprise 170 long names and 46 short ones. The 157 additional long spellings from the first pass consist of 143 distinct options and 14 long aliases. The other two new rows cover a GNU diagnostic absent from the Ubuntu man pages and the short-only compatibility option. The mode-dependent short option `-o` has its own row. [Bundled menu](../profiles/tar.json) · [First-pass audit](tar-option-audit.md)

## Sources and scope

| Source | Version | Evidence |
| --- | --- | --- |
| [GNU online manual](https://www.gnu.org/software/tar/manual/tar.html#All-Options) | 1.35.90 | Operation and option summaries, short-option cross-reference and chapters covering file lists, archive updates and tape drives. |
| [GNU release archive](https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz) | 1.35 | `doc/tar.texi`, option definitions and parsing in `src/tar.c` and `src/names.c`, checkpoint actions in `src/checkpoint.c`, size suffixes in `gnu/xstrtol.c`. Release archive SHA-256 is `4d62ff37342ec7aed748535323930c7cf94acf71c3591882b26a7ea50f3edc16`. |
| [Noble tar(1)](https://manpages.ubuntu.com/manpages/noble/man1/tar.1.html) | 1.35+dfsg-3ubuntu0.4 | Operation, option and compatibility declarations and operands. |
| [Resolute tar(1)](https://manpages.ubuntu.com/manpages/resolute/man1/tar.1.html) | 1.35+dfsg-4ubuntu0.4 | Same option headings, aliases and operand requirements as Noble. |
| [Packaged fixed help](../tests/fixtures/tar/gnu-tar-1.35-help.txt) | GNU tar 1.35, both Ubuntu builds above | Byte-identical standard output of `LC_ALL=C tar --help` on the three offline targets. SHA-256 is `8f059f7ebc89167f0c36732831081e6b67fed7dd4218ac55ad046f281049cb60`. |

## Manual inventory

Each primary spelling below selects one row. A dash in the operand column means the option consumes no value. Member, archive and label operands belong to the operation. Required long values accept `--name=value` or a separate word. The menu inserts `--name=` for these rows. For an optional value it inserts the bare switch and documents the attached `=value` spelling. A following word remains an operand. Short aliases can take a required argument in the same or next word. In a dashed cluster an option taking a value ends the option letters. In traditional syntax only the first word is the undashed option cluster, followed by option values in letter order. The menu inserts complete option tokens. [GNU option styles](https://www.gnu.org/software/tar/manual/tar.html#Styles)

The table follows the Ubuntu declarations independently of profile category order. All entries apply to both reviewed Ubuntu clients. Both man pages omit the final row, which both clients and the GNU manual document. The release manual explains `--add-file` in the file-list chapter and `--usage` in the documentation chapter. The online edition includes `--add-file` in its summary. The Ubuntu `-g` example in the syntax discussion appears under optional values, but the operation declaration, release parser and packaged clients require a snapshot argument.

| Primary spelling | Searchable aliases | Option operand |
| --- | --- | --- |
| `--catenate` | `-A`, `--concatenate` | — |
| `--create` | `-c` | — |
| `--diff` | `-d`, `--compare` | — |
| `--delete` | — | — |
| `--append` | `-r` | — |
| `--list` | `-t` | — |
| `--test-label` | — | — |
| `--update` | `-u` | — |
| `--extract` | `-x`, `--get` | — |
| `--show-defaults` | — | — |
| `--help` | `-?` | — |
| `--usage` | — | — |
| `--version` | — | — |
| `--check-device` | — | — |
| `--listed-incremental` | `-g` | `=FILE` |
| `--hole-detection` | — | `=METHOD` |
| `--incremental` | `-G` | — |
| `--ignore-failed-read` | — | — |
| `--level` | — | `=NUMBER` |
| `--seek` | `-n` | — |
| `--no-check-device` | — | — |
| `--no-seek` | — | — |
| `--occurrence` | — | `[=N]` |
| `--restrict` | — | — |
| `--sparse-version` | — | `=MAJOR[.MINOR]` |
| `--sparse` | `-S` | — |
| `--keep-old-files` | `-k` | — |
| `--keep-newer-files` | — | — |
| `--keep-directory-symlink` | — | — |
| `--no-overwrite-dir` | — | — |
| `--one-top-level` | — | `[=DIR]` |
| `--overwrite` | — | — |
| `--overwrite-dir` | — | — |
| `--recursive-unlink` | — | — |
| `--remove-files` | — | — |
| `--skip-old-files` | — | — |
| `--unlink-first` | `-U` | — |
| `--verify` | `-W` | — |
| `--ignore-command-error` | — | — |
| `--no-ignore-command-error` | — | — |
| `--to-stdout` | `-O` | — |
| `--to-command` | — | `=COMMAND` |
| `--atime-preserve` | — | `[=METHOD]` |
| `--delay-directory-restore` | — | — |
| `--group` | — | `=NAME[:GID]` |
| `--group-map` | — | `=FILE` |
| `--mode` | — | `=CHANGES` |
| `--mtime` | — | `=DATE-OR-FILE` |
| `--touch` | `-m` | — |
| `--no-delay-directory-restore` | — | — |
| `--no-same-owner` | — | — |
| `--no-same-permissions` | — | — |
| `--numeric-owner` | — | — |
| `--owner` | — | `=NAME[:UID]` |
| `--owner-map` | — | `=FILE` |
| `--preserve-permissions` | `-p`, `--same-permissions` | — |
| `--same-owner` | — | — |
| `--preserve-order` | `-s`, `--same-order` | — |
| `--sort` | — | `=ORDER` |
| `--acls` | — | — |
| `--no-acls` | — | — |
| `--selinux` | — | — |
| `--no-selinux` | — | — |
| `--xattrs` | — | — |
| `--no-xattrs` | — | — |
| `--xattrs-exclude` | — | `=PATTERN` |
| `--xattrs-include` | — | `=PATTERN` |
| `--file` | `-f` | `=ARCHIVE` |
| `--force-local` | — | — |
| `--info-script` | `-F`, `--new-volume-script` | `=COMMAND` |
| `--tape-length` | `-L` | `=N` |
| `--multi-volume` | `-M` | — |
| `--rmt-command` | — | `=COMMAND` |
| `--rsh-command` | — | `=COMMAND` |
| `--volno-file` | — | `=FILE` |
| `--blocking-factor` | `-b` | `=BLOCKS` |
| `--read-full-records` | `-B` | — |
| `--ignore-zeros` | `-i` | — |
| `--record-size` | — | `=NUMBER` |
| `--format` | `-H` | `=FORMAT` |
| `--old-archive` | `--portability` | — |
| `--pax-option` | — | `=keyword[[:]=value][,keyword[[:]=value]]...` |
| `--posix` | — | — |
| `--label` | `-V` | `=TEXT` |
| `--auto-compress` | `-a` | — |
| `--use-compress-program` | `-I` | `=COMMAND` |
| `--bzip2` | `-j` | — |
| `--xz` | `-J` | — |
| `--lzip` | — | — |
| `--lzma` | — | — |
| `--lzop` | — | — |
| `--no-auto-compress` | — | — |
| `--gzip` | `-z`, `--gunzip`, `--ungzip` | — |
| `--compress` | `-Z`, `--uncompress` | — |
| `--zstd` | — | — |
| `--add-file` | — | `=FILE` |
| `--backup` | — | `[=CONTROL]` |
| `--directory` | `-C` | `=DIR` |
| `--exclude` | — | `=PATTERN` |
| `--exclude-backups` | — | — |
| `--exclude-caches` | — | — |
| `--exclude-caches-all` | — | — |
| `--exclude-caches-under` | — | — |
| `--exclude-ignore` | — | `=FILE` |
| `--exclude-ignore-recursive` | — | `=FILE` |
| `--exclude-tag` | — | `=FILE` |
| `--exclude-tag-all` | — | `=FILE` |
| `--exclude-tag-under` | — | `=FILE` |
| `--exclude-vcs` | — | — |
| `--exclude-vcs-ignores` | — | — |
| `--dereference` | `-h` | — |
| `--hard-dereference` | — | — |
| `--starting-file` | `-K` | `=MEMBER` |
| `--newer-mtime` | — | `=DATE` |
| `--no-null` | — | — |
| `--no-recursion` | — | — |
| `--no-unquote` | — | — |
| `--no-verbatim-files-from` | — | — |
| `--null` | — | — |
| `--newer` | `-N`, `--after-date` | `=DATE` |
| `--one-file-system` | — | — |
| `--absolute-names` | `-P` | — |
| `--recursion` | — | — |
| `--suffix` | — | `=STRING` |
| `--files-from` | `-T` | `=FILE` |
| `--unquote` | — | — |
| `--verbatim-files-from` | — | — |
| `--exclude-from` | `-X` | `=FILE` |
| `--strip-components` | — | `=NUMBER` |
| `--transform` | `--xform` | `=EXPRESSION` |
| `--anchored` | — | — |
| `--ignore-case` | — | — |
| `--no-anchored` | — | — |
| `--no-ignore-case` | — | — |
| `--no-wildcards` | — | — |
| `--no-wildcards-match-slash` | — | — |
| `--wildcards` | — | — |
| `--wildcards-match-slash` | — | — |
| `--checkpoint` | — | `[=N]` |
| `--checkpoint-action` | — | `=ACTION` |
| `--clamp-mtime` | — | — |
| `--full-time` | — | — |
| `--index-file` | — | `=FILE` |
| `--check-links` | `-l` | — |
| `--no-quote-chars` | — | `=STRING` |
| `--quote-chars` | — | `=STRING` |
| `--quoting-style` | — | `=STYLE` |
| `--block-number` | `-R` | — |
| `--show-omitted-dirs` | — | — |
| `--show-transformed-names` | `--show-stored-names` | — |
| `--totals` | — | `[=SIGNAL]` |
| `--utc` | — | — |
| `--verbose` | `-v` | — |
| `--warning` | — | `=KEYWORD` |
| `--interactive` | `-w`, `--confirmation` | — |
| `-o` | — | — |
| `--show-snapshot-field-ranges` | — | — |

## Material findings

- File-list settings are positional. A default `-T` list may contain options, including a directory change that persists into later command-line operands. Putting `--null` before `-T` enables NUL termination and literal handling together. Putting `--no-null` before the next list restores newline and option parsing together. `--verbatim-files-from` changes interpretation independently of the delimiter. A relative archive path still starts in the original working directory. [GNU file lists](https://www.gnu.org/software/tar/manual/tar.html#files) · [Working directory](https://www.gnu.org/software/tar/manual/tar.html#directory)
- Append adds files, update adds missing or newer copies, and catenate adds archives. Duplicate member names can coexist. Extraction normally leaves the last copy. An attached occurrence number selects a particular copy. With `-o`, creation uses V7 and extraction uses the extracting user’s ownership. Incremental extraction can remove files absent from an archived directory. [GNU operations](https://www.gnu.org/software/tar/manual/tar.html#Operations) · [Incremental dumps](https://www.gnu.org/software/tar/manual/tar.html#Incremental-Dumps)
- The three cache and three marker-file options differ in whether the directory, its marker and its contents are recorded. The menu also distinguishes collision errors from silent skips, recursive removal from replacing a single entry, and the effect of following an existing directory symlink. The Ubuntu example for `--xattrs-exclude='user.*'` describes inclusion in its prose. The release manual applies exclusion after inclusion, so the matching keys are omitted. [GNU exclusions](https://www.gnu.org/software/tar/manual/tar.html#exclude) · [Extended attributes](https://www.gnu.org/software/tar/manual/tar.html#Extended-File-Attributes)
- The blocking factor counts 512-byte blocks. Unsuffixed record size is in bytes and must resolve to a multiple of 512. Unsuffixed tape length is in 1024-byte units. A suffix replaces that multiplier. The source additionally accepts lowercase `m`, `g` and `t`. Checkpoints count records, so changing the record size also changes the byte interval. [GNU blocking](https://www.gnu.org/software/tar/manual/tar.html#Blocking-Factor) · [GNU checkpoints](https://www.gnu.org/software/tar/manual/tar.html#checkpoints)
- Regular members sent to `--to-command` each get a separate child and stdin stream. Compression filters process the archive stream. Checkpoint and volume-change programs receive archive state through environment variables. Archive members, date expressions, pax keywords, warning classes, checkpoint action names and child program switches are values or operands. They do not add option rows.
- The GNU manual describes the historical `-[0-7][lmh]` tape drive/density syntax. GNU 1.35 conditionally enables it with `DEVICE_PREFIX`. Both packaged builds reject it. Abbreviations, arbitrary option clusters, the `--` end marker and platform-specific tape shorthands have no separate menu rows. The `-?` help alias is searchable on the `--help` row. Typing the alias directly may require shell quoting.

The prose outside the option tables also mentions spellings outside the current option tables. Both packaged parsers rejected `--sparse-format` and `--no-recursive`. The implemented names are `--sparse-version` and `--no-recursion`. They rejected the historical `--volume` and proposed `--number-blocks`. They diagnosed `--block` as ambiguous and accepted `--strip`, `--cre` and `--use-compress-prog` as unambiguous prefixes. The options of the separate backup, restore and genfile programs, compression helpers and GNU configure belong to those programs.

## Verification

The old functional-matrix pin now checks the original 12 literal insertions. The exhaustive comparison uses the manual inventory and versioned fixed help. In four separate in-memory mutations on the host sandbox, it detected a removed option, a missing alias, a wrong operand requirement and a duplicate row.

**Packaged clients.** Separate disposable fixtures in each offline target archived a leading dash and an embedded newline with `--null -T`, then used `--no-null -T` for ordinary names containing spaces. A `-Csrc` option inside a list also affected the next command-line operand. The archive was written relative to the starting directory. An ordinary list line containing spaces named one file, including leading or trailing spaces. With a directory operand, a normal listing selected its child and `--no-recursion` selected only the directory entry. The packaged parsers required the argument to `-g`, printed snapshot field ranges and rejected `-0l`. Traditional `tar cf` accepted the archive filename after the option letters. Dashed `tar -cof` produced a V7 header and `tar -xof` restored a file owned by the extracting account. The extraction check ran unprivileged.

Appending a duplicate preserved both members. Bare `--occurrence` listed one copy and `--occurrence=0` listed both. Both clients accepted `--get` with `--occurrence=2` and an attached signal in `--totals=USR1`. A 10K record yielded a 10,240-byte archive on the small fixture. A 513-byte record was rejected with status 2. Three one-member archives combined in one `tar -Af a.tar b.tar c.tar` call listed only the first two members by default. `tar -itf a.tar` listed all three. This qualifies the upstream explanation about removing end markers and agrees with the Ubuntu warning for multiple inputs. [GNU concatenation](https://www.gnu.org/software/tar/manual/tar.html#concatenate)

The manuals name the `lzma` program for `--lzma`. Both Ubuntu help outputs name `xz`. A private filter recorder saw both clients invoke `xz` on creation and add `-d` on reading. On Resolute the actual helper produced XZ magic bytes, and `-I 'xz --format=lzma'` produced a stream accepted by the legacy LZMA decoder. The minimal Noble images lack the external `xz` executable. Their evidence covers program selection and arguments, with native compressed bytes verified on Resolute. Remote tape services, physical tape changes, privileged ownership restoration and filesystem security labels are documented behaviors. [GNU compression](https://www.gnu.org/software/tar/manual/tar.html#gzip)

**Rendered menu.** The terminal regression uses private Bash/tmux sessions with discovery disabled and a tar execution recorder. It compares every selected row and all visible Details, including formatted value guidance, at 210×100. At 60×16 it starts from the unfiltered menu, finds the archive-path exception and the NUL-list leading-dash rule, scrolls to each, and checks Escape against the original buffer and cursor. Selection inserts `--directory=` before the existing member. Searching `--get` selects `--extract`. Selecting bare `--totals` preserves the suffix and accepts a subsequent attached `=USR1` edit. [Terminal and inventory regression](../tests/test_tar_manual_coverage.py)

The 166 numerical-inventory changes comprise 145 new options, five new categories and 16 changed fingerprints. The review compared all non-tar observations with the pre-edit inventory. The strict checker accepted all 802 required workspace contracts. Byte totals describe output, while the optional input to `--totals` names a signal. [Numerical review](numerical-inventory/review.json)

For a full run, substitute `host`, `noble310` or `noble312` for `TARGET`. The three include paths make the raw help, inventory and regression available before staging. The focused run uses the same snapshot and selects the tar and numerical regression modules. [Sandbox guide](development.md#isolated-local-debugging)

```bash
snapshot=(--include docs/tar-manual-coverage.md
          --include tests/fixtures/tar/gnu-tar-1.35-help.txt
          --include tests/test_tar_manual_coverage.py)
python3 -I tests/run_sandbox.py --target TARGET "${snapshot[@]}" -- sh -c 'cd tests && python3 -m unittest -v test_tar_manual_coverage test_terminal_screen.OptionsLayoutTests.test_tar_directory_scope_search_cancel_and_insertion test_functional_matrix.PrioritizedInventoryTests.test_bundled_surfaces_are_pinned test_numerical_diagnostics'
python3 -I tests/run_sandbox.py --target TARGET "${snapshot[@]}"
```


### Offline suite results

| Target | Ubuntu | Python | GNU tar package | Focused passed / failed / skipped | Full passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `host` | 26.04.1 LTS | 3.14.4 | 1.35+dfsg-4ubuntu0.4 | 15 / 0 / 0 | 1,358 / 0 / 1 | 699.965 s |
| `noble310` | 24.04.5 LTS | 3.10.20 | 1.35+dfsg-3ubuntu0.4 | 15 / 0 / 0 | 1,358 / 0 / 1 | 772.466 s |
| `noble312` | 24.04.5 LTS | 3.12.3 | 1.35+dfsg-3ubuntu0.4 | 15 / 0 / 0 | 1,358 / 0 / 1 | 696.038 s |

All three full suites passed. Each skipped the Windows-specific probe. The tar recorder remained unused during menu inspection. All applicable manual options and their Details meet the revisit criteria on the three targets.
