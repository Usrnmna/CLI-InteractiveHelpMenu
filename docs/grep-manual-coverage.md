# GNU grep manual coverage

The menu has **48 selectable options**. Fourteen retain their original insertion spellings and 34 are new. The manuals declare 48 long spellings, including two pairs of aliases. These account for 46 rows. The other two rows are `-I`, a fixed binary-input policy, and `-X MATCHER`, an undocumented matcher selector accepted by both reviewed releases. The 48 rows have 38 literal aliases and one numeric shorthand. [Bundled grep profile](../profiles/grep.json) · [First-pass audit](grep-option-audit.md)

## Sources

| Reference | Version | Material checked |
| --- | --- | --- |
| [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html) | 3.12 | Command-line and matching control, context, file selection, regular expressions, exit status and environment. |
| [Noble grep(1)](https://manpages.ubuntu.com/manpages/noble/man1/grep.1.html) | 3.11-4build1 | Option declarations, file and record handling, platform qualifications. |
| [Resolute grep(1)](https://manpages.ubuntu.com/manpages/resolute/man1/grep.1.html) | 3.12-1 | The same 48 long spellings, with the same required or optional operands. |
| [GNU 3.11 release source](https://ftp.gnu.org/gnu/grep/grep-3.11.tar.xz) · [GNU 3.12 release source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz) | Release-matched | `src/grep.c` short and long option tables, matcher names, numeric parsing, output and exit logic. `src/pcresearch.c` compile flags and pattern restrictions. `doc/grep.texi` option definitions. |
| [Noble fixed help](../tests/fixtures/grep/gnu-grep-3.11-help.txt) · [Noble version](../tests/fixtures/grep/gnu-grep-3.11-version.txt) | grep 3.11, PCRE2 10.42 | Standard output of `LC_ALL=C grep --help` and `LC_ALL=C grep --version` on the Ubuntu 24.04 targets. |
| [Resolute fixed help](../tests/fixtures/grep/gnu-grep-3.12-help.txt) · [Resolute version](../tests/fixtures/grep/gnu-grep-3.12-version.txt) | grep 3.12, PCRE2 10.46 | The same probes on the Ubuntu 26.04 target. |

## Manual inventory

The primary name selects a row. A dash in the operand column marks a switch. A named operand is required except for the optional `[=WHEN]` on `--color`. Long options with a required value accept a separate word or an attached value after `=`. Short options that take a value accept it in the same word or the next. The numeric shorthand `-NUM` consists of a dash followed immediately by decimal digits, such as `-2`. Selecting its row inserts `--context=`. Applicability covers the two reviewed Ubuntu builds. Platform and library differences are described below.

| Canonical | Aliases | Operand | Applicability | Disposition |
| --- | --- | --- | --- | --- |
| `--help` | — | — | both | added |
| `--version` | `-V` | — | both | added |
| `--extended-regexp` | `-E` | — | both | original |
| `--fixed-strings` | `-F`, `--fixed-regexp` | — | both | original |
| `--basic-regexp` | `-G` | — | both | added |
| `--perl-regexp` | `-P` | — | both | added |
| `--regexp` | `-e` | `PATTERN` | both | original |
| `--file` | `-f` | `FILE` | both | added |
| `--ignore-case` | `-i`, `-y` | — | both | original |
| `--no-ignore-case` | — | — | both | added |
| `--invert-match` | `-v` | — | both | original |
| `--word-regexp` | `-w` | — | both | original |
| `--line-regexp` | `-x` | — | both | added |
| `--count` | `-c` | — | both | original |
| `--color` | `--colour` | `[=WHEN]` | both | added |
| `--files-without-match` | `-L` | — | both | added |
| `--files-with-matches` | `-l` | — | both | original |
| `--max-count` | `-m` | `NUM` | both | added |
| `--only-matching` | `-o` | — | both | original |
| `--quiet` | `-q`, `--silent` | — | both | added |
| `--no-messages` | `-s` | — | both | added |
| `--byte-offset` | `-b` | — | both | added |
| `--with-filename` | `-H` | — | both | added |
| `--no-filename` | `-h` | — | both | added |
| `--label` | — | `LABEL` | both | added |
| `--line-number` | `-n` | — | both | original |
| `--initial-tab` | `-T` | — | both | added |
| `--null` | `-Z` | — | both | added |
| `--after-context` | `-A` | `LINES` | both | added |
| `--before-context` | `-B` | `LINES` | both | added |
| `--context` | `-C`, `-NUM` | `LINES` | both | original |
| `--group-separator` | — | `STRING` | both | added |
| `--no-group-separator` | — | — | both | added |
| `--text` | `-a` | — | both | added |
| `--binary-files` | — | `TYPE` | both | added |
| `--devices` | `-D` | `ACTION` | both | added |
| `--directories` | `-d` | `ACTION` | both | added |
| `--exclude` | — | `GLOB` | both | original |
| `--exclude-from` | — | `FILE` | both | added |
| `--exclude-dir` | — | `GLOB` | both | added |
| `-I` | — | — | both | added |
| `--include` | — | `GLOB` | both | original |
| `--recursive` | `-r` | — | both | original |
| `--dereference-recursive` | `-R` | — | both | added |
| `--line-buffered` | — | — | both | added |
| `--binary` | `-U` | — | both | added |
| `--null-data` | `-z` | — | both | added |
| `-X` | — | `MATCHER` | both | added |

## Manual and source findings

- **Pattern and file operands.** Without `-e` or `-f`, the first operand is the pattern. With either switch, the remaining operands name input files. An empty pattern selects every line in ordinary matching, while an empty pattern file contributes zero patterns. A blank line in a pattern file supplies an empty pattern. `--` ends option parsing, so `grep -- '-x' file` and `grep -e '-x' file` can search for a leading dash. A file operand of `-` denotes standard input. The delimiter and standard-input operand belong to the command grammar. The short matcher selectors and their long names are options. [GNU matching control](https://www.gnu.org/software/grep/manual/grep.html#Matching-Control)
- **PCRE library differences.** Both builds accept `-P` and require a single distinct PCRE pattern after duplicate removal. In a UTF-8 locale, grep uses ASCII digits for `\d`. Its PCRE2 compile flags differ by library version. With PCRE2 10.42 the older implementation does not enable Unicode character properties by default. With PCRE2 10.46 it enables them while retaining ASCII `\d`. Thus the current GNU manual’s Unicode description of `[[:digit:]]` in PCRE mode needs a Noble qualification. An explicit Unicode property such as `\p{Nd}` is available on both builds. PCRE2 10.43 or later also supplies the inline `(?aD)` and `(?-aD)` switches. Under `-zP`, a record can span multiple newlines. An input file with no NUL can require buffering the entire file. [GNU grep programs](https://www.gnu.org/software/grep/manual/grep.html#grep-Programs) · [GNU 3.11 source](https://ftp.gnu.org/gnu/grep/grep-3.11.tar.xz) · [GNU 3.12 source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz)
- **Counts and results.** Selection applies to input records. `-c` counts selected records per file, while `-o` prints nonempty matching pieces. An inverted selection can therefore succeed with no pieces to print. `-l` and `-L` change which filenames are printed. Exit status still reflects selection, so `-L` can print a filename and exit 1. A successful `-q` returns 0 even after an earlier input error. `-s` suppresses input-file diagnostics and preserves error status. [General output control](https://www.gnu.org/software/grep/manual/grep.html#General-Output-Control) · [Exit status](https://www.gnu.org/software/grep/manual/grep.html#Exit-Status)
- **Numeric operands.** `-A` and `-B` set individual directions. `-C` and `-NUM` supply the default for directions without an explicit count, regardless of order. The explicit operands accept nonnegative decimal lengths without suffixes. The source accepts a positive integer overflowing `intmax_t` at its saturated maximum. `-m` is a per-file selected-line limit and permits trailing context. The manual documents 0 as an immediate stop and −1 as unlimited. The implementation’s zero-limit shortcut excludes `-L`, and its inverted-selection loop compares the number emitted directly against the stored limit. These details explain the fixture exceptions below. [Context line control](https://www.gnu.org/software/grep/manual/grep.html#Context-Line-Control) · [GNU 3.12 source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz)
- **Output delimiters.** `-Z` replaces the separator immediately after an output filename. `-z` uses NUL for input and selected output records, including pieces printed by `-o`. Counts, filename-only results and context group separators have their own terminators. For example, `-lZ` terminates each filename with NUL. A zero-based `-b` offset with `-o` refers to the match, while `-n` numbers its input record from one. [Output line prefix control](https://www.gnu.org/software/grep/manual/grep.html#Output-Line-Prefix-Control) · [Other options](https://www.gnu.org/software/grep/manual/grep.html#Other-Options)
- **File selection and binary input.** The final matching include/exclude rule wins. An initial include skips unmatched files. Explicit file operands can match a path suffix beginning at a directory boundary. During recursion, the basename is matched. `--exclude-dir` applies directory globs. With `-r`, an explicit directory symlink is followed, while a discovered symlink is skipped. `-R` follows both. The switches `-I` and `--text` choose the fixed `without-match` and `text` values of `--binary-files`. The separate `--binary` requests binary I/O on systems that translate text, such as Windows. On Ubuntu it leaves input and the binary-file heuristic unchanged. [File and directory selection](https://www.gnu.org/software/grep/manual/grep.html#File-and-Directory-Selection) · [Other options](https://www.gnu.org/software/grep/manual/grep.html#Other-Options)
- **Optional color value.** Omitting the option disables coloring by default. Bare `--color` requests `auto`. Only an attached `=WHEN` supplies the option's value, so `grep --color always file` searches for the pattern `always`. Selecting `--color=` puts the cursor after the equals sign for an explicit value. To use the bare form, remove that equals sign. Canonical settings are `always`, `never` and `auto`. The release parsers also accept `yes` and `force`, `no` and `none`, and `tty` and `if-tty` respectively, case-insensitively. [GNU general output control](https://www.gnu.org/software/grep/manual/grep.html#General-Output-Control) · [GNU 3.12 source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz)

## Compatibility forms and exclusions

The GNU manual lists historical `-y` under `--ignore-case`. The Ubuntu man pages and fixed help omit it. Both release parsers also declare the unpublished `--fixed-regexp` spelling for `--fixed-strings`. The intentionally undocumented `-X MATCHER` appears in both parser tables and accepts additional matchers beyond the public switches, including `awk`, `gawk` and `posixawk`. The row identifies its implementation-specific status. The menu inserts `--context=` for the numeric shorthand and `-X ` before a matcher name. [GNU matching control](https://www.gnu.org/software/grep/manual/grep.html#Matching-Control) · [GNU 3.12 source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz)

The historical `-u` and `--unix-byte-offsets` have no selectable row. GNU grep 3.11 accepts them, warns about obsolescence and makes no change. GNU grep 3.12 removes the long declaration and rejects both spellings. Arbitrary unambiguous long-option abbreviations depend on the current parser table. The inventory uses declared spellings. Environment settings, regex syntax and the separately invoked `egrep`, `fgrep` and `rgrep` wrappers belong outside this command's option list. [GNU 3.11 source](https://ftp.gnu.org/gnu/grep/grep-3.11.tar.xz) · [GNU 3.12 source](https://ftp.gnu.org/gnu/grep/grep-3.12.tar.xz) · [Ubuntu command synopsis](https://manpages.ubuntu.com/manpages/resolute/man1/grep.1.html)

## Verification

### Packaged executables

Each offline target ran its own grep against disposable inputs. The comparisons checked raw stdout, stderr and exit status independently. The two Noble interpreters used the same packaged grep and produced byte-identical fixed help and version output. The installed grep / libpcre2-8-0 package revisions were 3.11-4build1 / 10.42-4ubuntu2.2 on Noble and 3.12-1 / 10.46-1ubuntu0.1 on Resolute. The four files under tests/fixtures/grep retain unedited standard output in the C locale. The Unicode fixtures used C.UTF-8. [Executable regressions](../tests/test_grep_packaged.py)

| Disposable fixture | Observed result on both releases unless stated |
| --- | --- |
| A file with both newlines and NULs | `-HozZ` printed a filename, NUL, one matching piece and NUL for each match. With `-lz` the listed name ended in LF. Adding `-Z` changed it to NUL. With `-HzcZ` the count still ended in LF. |
| Two matches on the first selected line | `-om1` printed both pieces. `-c` counted the line once. `-nbo` reported a one-based record number with each zero-based match byte offset, including after a multibyte character. |
| Two nonmatching lines and two matching lines | `grep -vc hit in` wrote `2` and exited 0. Adding `-m-1` wrote `0` and exited 1. With ordinary matching the same explicit limit printed both matching lines. Omitting the limit preserves unlimited inverted selection on both packages. |
| A zero limit and a nonexistent input path | `-m0 -c` exited 1 with empty stdout and stderr. With `-L`, grep still checked the missing path and exited 2. On an existing file, `-m0 -L` printed its name and exited 1, even if it contained the pattern. |
| A missing file followed by a matching file | `-q` produced no stdout, diagnosed the missing file and exited 0. Adding `-s` hid the diagnostic. Using only `-s` printed the selected line and exited 2. |
| Two disjoint groups | `-o -C1` emitted the two matching pieces and a group separator with empty stderr. An empty separator string left a blank line. Disabling the separator removed it. With `-zC0`, the exact bytes between the matching records were NUL, two dashes and LF. |
| Arabic-Indic and ASCII digits | `-P '\d'` selected only ASCII on both. `[[:digit:]]` selected only ASCII on Noble and both on Resolute. `\p{Nd}` selected both on each release. Noble rejected the inline digit-mode switch `(?-aD)` with status 2. Resolute accepted it. |
| Pattern, color and file-selection operands | A dash-leading pattern worked with either `-e` or `--`. An empty pattern file selected nothing, and a blank line in it selected every line. Bare `--color` highlighted a terminal and left piped output plain. A separated `always` became the search pattern. An empty or unknown attached mode printed help and exited 0. Explicit suffix globs, reversed include/exclude rules and both symlink recursion policies agreed with the file-selection Details. |
| NUL and carriage return in a file | Default binary detection and `-U` produced the same binary-match diagnostic. `-a` emitted the matching bytes, including NUL and CR. `-I` produced no matches in this fixture. |

### Rendered menu

With discovery disabled, real Bash/tmux sessions browsed the bundled profile. A shell stub recorded any accidental execution of the pending grep command. At 210×100 the tests traversed all four categories, checked every selected row's label and summary, and compared the complete Details pane with the authored prose and formatted value guidance. At 60×16, searching from an unfiltered menu for `--silent` selected `--quiet`. Scrolling exposed the status-0 qualification after a file error. Escape restored the exact original pending line and cursor. Searching for the numeric context shorthand or the `--colour` alias and pressing Enter inserted `--context=` or `--color=` immediately before the two existing quoted operands. Typing the value left both operands intact. The stub recorded no execution. [Inventory and terminal regressions](../tests/test_grep_manual_coverage.py)

The strict numerical gate reconciled 867 required value contracts across 76 profiles. All 49 changed inventory identities were inspected against the original working tree. Every source observation outside the grep profile was unchanged for those identities. The byte-related prose on `--binary`, `--byte-offset`, `--null-data` and `--text` triggered advisory checks. All four are operand-free switches. Their units describe input or output data. The focused run included the new inventory, menu and executable checks, the original grep terminal regression, the bundled insertion-spelling check and the insertion-contract class. The full run used the project sandbox runner and `bash tests/run.sh`. The new audit, tests and four captures were explicitly included in the snapshots. As in the rsync revisit, the Noble full suites received the verified rsync package fixture in disposable storage. [Sandbox instructions](development.md#isolated-local-debugging) · [Rsync package fixture provenance](rsync-manual-coverage.md#verification)

| Target | Ubuntu | Python | grep package | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 3.12-1 | 24 / 0 / 0 | 1,383 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 3.11-4build1 | 24 / 0 / 0 | 1,383 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 3.11-4build1 | 24 / 0 / 0 | 1,383 / 0 / 1 |

The single skip on each target covers the Windows-specific probe. All grep inventory, executable and terminal checks ran on every target.
