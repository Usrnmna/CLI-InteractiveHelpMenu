# ls manual coverage

The bundled Bash menu covers 60 distinct options. The 19 pilot insertions remain selectable and 41 options have been added. GNU declares 84 short and long spellings. The Resolute page adds two documented aliases, bringing the documented union to 86. The uutils parser declares one further alias, giving 87 spellings represented by 60 rows and 27 aliases. Selector values and the option terminator are counted separately from option names. [Bundled ls profile](../profiles/ls.json) · [Historical 19-entry audit](ls-option-audit.md)

## Sources and executable versions

- The GNU Coreutils 9.12 manual, section 10.1, covers file selection, information, sorting, layout, timestamps and quoting. The common-option and block-size sections supply the option terminator, program information and display-unit rules. The published manual is newer than either packaged GNU binary. [GNU ls invocation](https://www.gnu.org/software/coreutils/manual/coreutils.html#ls-invocation) · [Common options](https://www.gnu.org/software/coreutils/manual/coreutils.html#Common-options) · [Block size](https://www.gnu.org/software/coreutils/manual/coreutils.html#Block-size)
- Ubuntu 24.04 Noble documents GNU Coreutils `9.4-3ubuntu6.3`. The installed package in both Ubuntu 24.04.5 images has that revision and supplies `/usr/bin/ls`. Both images returned byte-identical help and version output. The GNU 9.4 parser declares the long names, their arities and the separate short-option string. [Noble ls(1)](https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html) · [GNU 9.4 ls source](https://github.com/coreutils/coreutils/blob/v9.4/src/ls.c) · [Noble help](../tests/fixtures/ls/gnu-ls-9.4-help.txt) · [Noble version](../tests/fixtures/ls/gnu-ls-9.4-version.txt)
- Ubuntu 26.04 Resolute documents `rust-coreutils 0.10.0-1ubuntu2~26.04.1`. On the Ubuntu 26.04.1 host that package supplies the default `/usr/bin/ls` through `/usr/lib/cargo/bin/coreutils/ls`. Its parser declares the long-format alias, fixed-value shortcuts and policy words. [Resolute ls(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html) · [uutils 0.10.0 ls source](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/ls/src/ls.rs) · [Resolute default help](../tests/fixtures/ls/uutils-ls-0.10.0-help.txt) · [Resolute default version](../tests/fixtures/ls/uutils-ls-0.10.0-version.txt)
- The same host also supplies `/usr/bin/gnuls` in `gnu-coreutils 9.7-3ubuntu2.1`. Its declarations agree with the Noble GNU option names, but argument values and interactions differ. Host package revisions were read from the host package database, which the offline host sandbox does not mount. All six fixed captures are the unedited standard output of the absolute executable path with `--help` or `--version` and `LC_ALL=C` inside the project sandboxes. [GNU 9.7 ls source](https://github.com/coreutils/coreutils/blob/v9.7/src/ls.c) · [GNU comparator help](../tests/fixtures/ls/gnu-ls-9.7-help.txt) · [GNU comparator version](../tests/fixtures/ls/gnu-ls-9.7-version.txt)
- The six pilot structured guides cite GNU Coreutils 9.6. The versioned source defines the option declarations and the nine case-sensitive policy spellings for color. [GNU 9.6 release manual source](https://raw.githubusercontent.com/coreutils/coreutils/v9.6/doc/coreutils.texi) · [GNU 9.6 ls parser](https://github.com/coreutils/coreutils/blob/v9.6/src/ls.c)

## Manual inventory

Each canonical spelling has one row. All canonical spellings apply to both GNU versions and to uutils. The applicability column flags exceptions for aliases. An em dash under Operand marks a switch. A required long value accepts either `--option=VALUE` or `--option VALUE`. A required short value accepts `-xVALUE` or `-x VALUE`, where `x` represents `I`, `T` or `w`. GNU retains a literal equals sign in an attached short value, whereas uutils strips it. For instance, `-I=name` excludes a file called `=name` on GNU and a file called `name` on uutils. The explicit long spelling `--ignore==name` selects the former pattern on all three.

The three optional long policies take an explicit value only after an equals sign. A separated word is a path operand and an explicitly empty policy is rejected. Bare `-F` applies classification on all three. Only uutils accepts `-F=WHEN`. The spelling `-Fauto` is a short-option cluster on all three. The menu inserts bare `--classify` and the editable prefixes `--color=` and `--hyperlink=`. [Noble option declarations](https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html) · [Resolute option declarations](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)

| Canonical | Aliases | Operand | Applicability | Disposition | Effect |
| --- | --- | --- | --- | --- | --- |
| `--all` | `-a` | — | all | original | Include dot-prefixed names and the implied current and parent entries. |
| `--almost-all` | `-A` | — | all | original | Include dot-prefixed names except the implied current and parent entries. |
| `--author` | — | — | all | added | Add the author to a long listing. On Linux this is the owner. |
| `--escape` | `-b` | — | all | original | Use escape-style quoting for names. |
| `--block-size` | — | `SIZE` | all | added | Set display units for sizes and directory totals. |
| `--ignore-backups` | `-B` | — | all | added | Skip discovered backup names ending in a tilde. |
| `-c` | — | — | all | added | Select inode status-change time for display or ordering. |
| `-C` | — | — | all | added | Fill columns vertically. |
| `--color` | — | `[=WHEN]` | all | original | Color names according to file type and output policy. |
| `--directory` | `-d` | — | all | original | List directory operands themselves. |
| `--dired` | `-D` | — | all | added | Emit filename offsets for Emacs Dired. Noble requires long format to be selected separately. |
| `-f` | — | — | all | added | Include hidden entries and omit sorting. |
| `--classify` | `-F` | `[=WHEN]` | all, GNU short form is a switch | original | Append type indicators, including a star on executable regular files. |
| `--file-type` | — | — | all | added | Identify file types with suffixes while leaving regular files unmarked. |
| `--format` | — | `WORD` | all | added | Choose the layout of a listing. |
| `--full-time` | — | — | all | added | Select long format with full ISO timestamps. |
| `-g` | — | — | all | added | Select long format and omit the owner. |
| `--group-directories-first` | — | — | all | original | Group directories before other entries when sorting. |
| `--no-group` | `-G` | — | all | added | Suppress the group column in a long listing. |
| `--human-readable` | `-h` | — | all | original | Scale sizes into units based on powers of 1024. |
| `--si` | — | — | all | added | Scale sizes into units based on powers of 1000. |
| `--dereference-command-line` | `-H` | — | all | added | Follow symbolic links named as operands. |
| `--dereference-command-line-symlink-to-dir` | — | — | all | added | Follow command-line symlinks that point to directories. |
| `--hide` | — | `PATTERN` | all | original | Suppress matching discovered names in ordinary listings. |
| `--hyperlink` | — | `[=WHEN]` | all | added | Emit terminal hyperlinks for listed names. |
| `--indicator-style` | — | `WORD` | all | added | Choose which file-type suffixes appear after names. |
| `--inode` | `-i` | — | all | original | Show the inode number for each entry. |
| `--ignore` | `-I` | `PATTERN` | all | added | Omit discovered names matching the specified glob. |
| `--kibibytes` | `-k` | — | all | added | Request units of 1024 bytes for filesystem usage. |
| `-l` | `--long` | — | all, alias uutils only | original | Show the long listing with metadata for each name. |
| `--dereference` | `-L` | — | all | original | Use target attributes for symbolic links. |
| `-m` | — | — | all | added | Separate entries with commas and wrap to the output width. |
| `--numeric-uid-gid` | `-n` | — | all | original | Select long format and print numeric user and group IDs. |
| `--literal` | `-N`, `--l` | — | all, --l declared by uutils | added | Use literal names without quoting. |
| `-o` | — | — | all | added | Select long format and omit the group. |
| `-p` | — | — | all | added | Append a slash to directory names. |
| `--hide-control-chars` | `-q` | — | all | added | Replace otherwise unescaped nongraphic characters with question marks. |
| `--show-control-chars` | — | — | all | added | Preserve nongraphic characters that the quoting style leaves raw. |
| `--quote-name` | `-Q` | — | all | original | Enclose names in double quotes and use C escapes. |
| `--quoting-style` | — | `WORD` | all | added | Choose how names are quoted and escaped. |
| `--reverse` | `-r` | — | all | original | Reverse the active sort order. |
| `--recursive` | `-R` | — | all | original | Descend into subdirectories while listing. |
| `--size` | `-s` | — | all | original | Print allocated space for each entry. |
| `-S` | — | — | all | original | Sort by file length with the largest first. |
| `--sort` | — | `WORD` | all | added | Choose the ordering criterion. |
| `--time` | — | `WORD` | all | added | Choose the timestamp used for display or time ordering. |
| `--time-style` | — | `TIME_STYLE` | all | added | Choose the timestamp format in long listings. |
| `-t` | — | — | all | original | Sort newest first by the selected timestamp. |
| `--tabsize` | `-T` | `COLS` | all | added | Set the spacing between tab stops for column layout. |
| `-u` | — | — | all | added | Select the last access timestamp for display or ordering. |
| `-U` | — | — | all | added | Keep the directory's enumeration order. |
| `-v` | — | — | all | added | Use version ordering for numbers embedded in names. |
| `--width` | `-w` | `COLS` | all | added | Set the output width for layouts that wrap. |
| `-x` | — | — | all | added | Fill columns across each row. |
| `-X` | — | — | all | added | Sort by filename extension. |
| `--context` | `-Z` | — | all | added | Display the file security context. |
| `--zero` | — | — | all | added | Terminate output records with a NUL byte. |
| `-1` | — | — | all | added | Display one entry per line. |
| `--help` | — | — | all | added | Display the executable's usage reference. |
| `--version` | `-V` | — | all, alias uutils only | added | Display the executable's version. |

## Fixed-value forms and exclusions

The GNU help heading for `-p` also names `--indicator-style=slash`. This is a value of a separate selector. The `-p` row inserts the switch, while `--indicator-style=` accepts all four styles. The same distinction applies to layout switches such as `-C` and `-1`, sort switches such as `-S` and `-v`, and quoting switches such as `-Q`. Compound options such as `-f`, `-o` and `--full-time` have their own rows. [GNU sorting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-the-output) · [GNU layout and indicators](https://www.gnu.org/software/coreutils/manual/coreutils.html#General-output-formatting) · [GNU quoting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Formatting-the-file-names)

The Resolute manual and fixed help declare `--long` and `-V`. Both GNU binaries reject these spellings with status 2. The uutils source separately declares the unpublished `--l` alias for `--literal`. Both GNU versions also accept it as an unambiguous abbreviation. A disposable file named `a b` confirmed that `-Q --l` outputs its bare name on all three, while `-Ql` produces long-format metadata and a double-quoted name. The inventory counts declared names, excluding arbitrary abbreviated prefixes. [uutils 0.10.0 declarations](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/ls/src/ls.rs) · [GNU 9.4 declarations](https://github.com/coreutils/coreutils/blob/v9.4/src/ls.c)

The shared `--` delimiter ends option parsing. For example, `ls -- -a` listed a file literally named `-a` on all three executables. Paths, wildcard expansion performed by the shell, environment variables, and the separately invoked `dir`, `vdir` and `gnuls` programs are outside the option count. The backup and target-directory options in the Coreutils common chapter apply to other utilities. [GNU common options](https://www.gnu.org/software/coreutils/manual/coreutils.html#Common-options) · [GNU directory listing commands](https://www.gnu.org/software/coreutils/manual/coreutils.html#Directory-listing)

## Material corrections

- **What zero blocks means.** A long listing normally shows a regular file's logical length in bytes. The leading field from `-s` and the directory total report filesystem allocation. GNU rounds a partial display block up and scales the total after adding the underlying allocations. Resolute's default uutils truncates each fixed-unit allocation and sums the displayed counts. A nonempty file that occupies disk space can therefore show zero in `ls -s --block-size=16K`. Length still rounds up on both implementations. `-S` sorts by logical length regardless of the selected display unit. [GNU block-size rules](https://www.gnu.org/software/coreutils/manual/coreutils.html#Block-size) · [uutils display implementation](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/ls/src/display.rs)
- **Which paths recursion follows.** `-H` follows links named on the command line. `-L` also follows links discovered inside a directory. Under a *single* recursive root, GNU visited a directory and its sibling symlink, while uutils diagnosed the second visit. Naming the two paths as separate operands succeeded on all three binaries. A hide pattern yields to either `-a` or `-A`. An ignore pattern stays active. When `-a` and `-A` are combined, the last one controls the implied dot entries on the tested packages despite the GNU manual's blanket precedence statement. [GNU file selection](https://www.gnu.org/software/coreutils/manual/coreutils.html#Which-files-are-listed) · [Ubuntu Resolute ls(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)
- **Which timestamp is displayed or sorted.** The explicit `-lu` displays access time in name order. Adding `-t` orders by access time, newest first. Noble's GNU 9.4 lacks an explicit `--sort=name` and retains name order for `--time=mtime` alone. Both Resolute binaries accept the name key and sort by modification time for that latter invocation. `--time-style` controls how the displayed timestamp is printed. For a custom pair of formats separated by a literal newline, GNU uses the first for old files and the second for recent files. uutils 0.10.0 uses them in the opposite order. [GNU sorting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-the-output) · [GNU time formatting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Formatting-file-timestamps) · [uutils option handling](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/ls/src/config.rs)
- **Output for another program.** With no conflicting formatting options or active hyperlinks, `--zero` emits literal names separated by NUL, including embedded newlines. Later options can restore quoting, colors, commas or columns. A later `-C` even produces an LF-terminated column layout on uutils. A forced hyperlink can survive `--zero` in either order. For Emacs, use `-lD` on Noble to get the filename byte offsets. Resolute's two implementations select long format with `-D` alone. [GNU layout rules](https://www.gnu.org/software/coreutils/manual/coreutils.html#General-output-formatting) · [GNU filename formatting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Formatting-the-file-names)

## Verification

### Packaged executable behavior

The binary checks used a separate temporary directory per fixture, no shell aliases, the C locale, UTC and a fixed terminal type. The byte comparisons captured stdout, stderr and exit status. A raw pseudo-terminal exposed terminal-specific behavior without translating line endings. The host ran both the default uutils binary and the GNU comparator. Each Noble image ran its own GNU binary. [Packaged executable regressions](../tests/test_ls_packaged.py)

| Disposable fixture | Observed output or status |
| --- | --- |
| A 1,048,576-byte sparse file and a 4,608-byte written file | The sparse file sorted first under `-S`, even though `-ls` showed zero allocation for it and eight 1 KiB blocks for the shorter file. `-h` displayed the sparse length as `1.0M`, and `--si` displayed `1.1M`. |
| Unit overrides on the written file | Allocation and length were `4 4608` with `BLOCKSIZE=2K`, `8 5` with `LS_BLOCK_SIZE=1K BLOCK_SIZE=2K`, and `16 4608` with only `POSIXLY_CORRECT=1`. The pair became `8 3` with `-k` and `BLOCK_SIZE=2K`. An explicit one-byte block overrode the environment and yielded `8192 4608`. |
| Directory containing files with 8,192 and 4,096 allocated bytes | With `--block-size=1000 -s`, GNU printed 9 and 5 with total 13. uutils printed 8 and 4 with total 12. With 5,000-byte blocks, GNU printed 2 and 1 with total 3. uutils printed 1 and 0 with total 1. A suffix alone, as in `--block-size=K`, printed a K suffix on GNU; uutils showed numbers without the suffix. |
| A hidden name, backup name and directory symlink | `-aA` omitted the implied dot entries and `-Aa` included them. `-AB` still hid the backup name. An explicit matching operand survived `--ignore`. With `-a --ignore='.*'`, GNU removed the implied entries, while uutils retained them. The sibling-link traversal returned status 2 and an already-listed-directory diagnostic only on uutils. Two explicit operands produced both listings and status 0 everywhere. |
| Independently set access and modification times | `-t` selected the newest modification. `-tr` reversed the order. `-lut --time-style=+%s` selected and printed the fixture's access timestamps. `-l --time=ctime` printed inode-change times matching the filesystem. A separate old/recent pair confirmed the opposite custom format order described above. |
| Unsorted mode, Dired and layout selectors | Noble `-lsf file` printed just the name; `-fls file` restored long format and allocation. On both Resolute binaries the long allocation listing survived either order. Only Noble required `-lD` to emit Dired offsets. `--format=columns` worked on uutils and was rejected by both GNU releases. `-l1` retained long format on all three; `-l --format=single-column` printed just the name. |
| Directory named `auto`, a space in a name and an embedded newline | Bare classify, color and hyperlink each affected piped output. Attached `=auto` affected the PTY and left the pipe plain. A separated `auto` listed the directory as an operand. All three policies accepted the nine lowercase policy words and rejected an empty or uppercase policy. `-Q --zero` wrote literal names ending in NUL; `--zero -Q` double-quoted them and escaped the embedded newline. |
| Anonymous pipe without a creation timestamp | The GNU manual describes an mtime fallback for birth time. The sandbox's `stat -Lc '%W %Y'` returned zero for birth and a nonzero mtime. With `-ldL --time=birth --time-style=+%s` on the inherited pipe descriptor, both GNU packages printed `?` and uutils printed `???`. All returned status 0 with empty stderr. GNU's Linux `do_statx` and `print_long_format` paths account for the marker. [GNU sorting manual](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-the-output) · [GNU 9.4 ls source](https://github.com/coreutils/coreutils/blob/v9.4/src/ls.c) · [GNU 9.7 ls source](https://github.com/coreutils/coreutils/blob/v9.7/src/ls.c) |

The six pilot value guides retain their GNU 9.6 references. Separate release evidence extends the GNU scope to 9.4 and 9.7 and identifies uutils 0.10.0. New value guidance covers the block-size grammar, tab stops, output width, time and layout selectors. For instance, `-T08` works on uutils and is an invalid octal tab size on GNU. A zero tab size requests space padding. Released parser declarations and isolated probes establish these distinctions. [GNU 9.4 parser](https://github.com/coreutils/coreutils/blob/v9.4/src/ls.c) · [uutils option handling](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/ls/src/config.rs)

### Rendered menu and suite coverage

In a real Bash/tmux session with discovery disabled, the wide-menu regression walks the six categories at 220×150. For every selectable row it checks the highlighted label and summary, the full heading in Details, all authored sentences and the complete formatted value guidance. The narrow view at 60×16 starts unfiltered. Searching for “allocated” selects `--size`, and scrolling exposes the sparse-file distinction. Searching for `--long` finds the `-l` row. Escape restores the exact original line and cursor. Selecting either `--hide=` or the new `--tabsize=` before a quoted pathname leaves the pathname intact and the cursor immediately after the equals sign. A shell stub records any attempt to execute the pending command. [Inventory and terminal regressions](../tests/test_ls_manual_coverage.py) · [Allocated-space and hide regression](../tests/test_terminal_screen.py)

The focused command checks the independent manual inventory against each fixed help capture, the terminal and package regressions, the original spelling/order and the general insertion contract. The strict numerical gate reconciles 879 required contracts across 76 profiles. Review covered 65 changed inventory identities and verified that all source observations outside the ls profile for those identities were unchanged. The full suite uses `bash tests/run.sh` in a fresh offline snapshot. Each new audit, test module and fixed capture is included individually. The Noble snapshots also receive the previously verified rsync fixture to exercise those existing tests. [Numerical review](numerical-inventory/review.json) · [Sandbox runner](development.md#isolated-local-debugging) · [Rsync fixture provenance](rsync-manual-coverage.md#verification)

| Target | Ubuntu | Python | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 23 / 0 / 0 | 1,397 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 23 / 0 / 0 | 1,397 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 23 / 0 / 0 | 1,397 / 0 / 1 |

All 60 menu rows and their complete Details passed on each target, with zero stub executions. The sole full-suite skip per target covers the Windows-specific probe. All declared ls options are accounted for and both ls roadmap columns are complete.
