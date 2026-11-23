# Bundled GNU grep option audit

The [grep menu](../profiles/grep.json) covers 14 long options for selecting
lines, formatting output and choosing files. Two matches on one line
contribute **one** to `--count`, while `--only-matching` can print both. With `-v`, the count is the number of
lines that match none of the patterns in each input file.

## Manuals reviewed

| Source | Version | Material checked |
| --- | --- | --- |
| [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html) | 3.12 | Option definitions, regular expression syntax, context groups and filename selection. |
| [Ubuntu 24.04 LTS grep(1)](https://manpages.ubuntu.com/manpages/noble/man1/grep.1.html) | 3.11-4build1 | Declarations and descriptions of all 14 entries. |
| [Ubuntu 26.04 LTS grep(1)](https://manpages.ubuntu.com/manpages/resolute/man1/grep.1.html) | 3.12-1 | The 14 definitions agree with the Noble page. |

## Disposition of the bundled entries

| Option | Assessment of previous wording | Detail retained or restored |
| --- | --- | --- |
| `--ignore-case` | Basic effect correct. Default and scope unclear. | Case-sensitive default and locale-dependent handling of some Unicode letters. |
| `--extended-regexp` | Restated the option name. | Unescaped parentheses group expressions and a vertical bar separates alternatives. Shell quoting keeps those characters in the pattern. |
| `--fixed-strings` | Basic effect sufficient. | Punctuation matches literally and a fixed string can match part of a line. |
| `--word-regexp` | “Whole words” left the boundary undefined. | Letters, digits and underscores are word characters. A hyphen and an underscore give different results next to a match. |
| `--invert-match` | Ambiguous for multiple patterns. | A line is selected only if every pattern fails to match it. |
| `--regexp=` | Summary sufficient. Operand handling incomplete. | Repeating patterns provides alternatives. Newlines separate patterns, `-e` accepts a leading dash and `-f` can supply additional patterns. |
| `--line-number` | Numbering origin and scope missing. | Prefix each output line with its one-based position in its input file. |
| `--count` | Per-file scope and inverted selection missing. | Multiple matches on one line contribute one. Inverted selection counts nonmatching lines. |
| `--files-with-matches` | Omitted early termination and inverted selection. | Scanning stops at the first selected line in each file. With `-v`, one nonmatching line qualifies the file. |
| `--only-matching` | Omitted empty matches and output boundaries. | Each nonempty match is printed separately. Null-data mode changes the delimiter and context options have no effect. |
| `--context=` | Prose repeated the structured numerical guidance. | The row states that the count applies on both sides. Details explain the group separator and the interaction with `-o`. The existing value guidance retains units, zero, merged groups and numeric limits. |
| `--recursive` | Omitted link traversal and the default search location. | `-r` follows command-line symbolic links and skips links encountered during traversal. `-R` follows both. Omitting file operands searches the working directory. |
| `--include=` | Omitted glob scope, rule order and the unmatched default. | A quoted glob can match a path suffix for an explicit operand, or a base name during recursion. The last matching rule wins. An initial include skips files matching no rule. |
| `--exclude=` | Omitted differences between explicit files, discovered files and directories. | Explains path suffixes, base names, rule order and when to use `--exclude-dir`. |

## Two qualifications checked on both grep versions

The Ubuntu include entries describe base names. GNU refers to its exclusion
rules, which distinguish explicit operands from files found recursively. In a
disposable fixture, `--include='sub/*.txt'` selected the explicit operand
`sub/a.txt` on both GNU grep 3.11 and 3.12. Searching recursively from `.`
with the same glob skipped the file because its base name was `a.txt`.
[GNU file and directory selection](https://www.gnu.org/software/grep/manual/grep.html#File-and-Directory-Selection)

The manuals say `-o` suppresses context and mention a warning. In the same
fixture, `-o -C1` printed the two matched strings, omitted the surrounding lines
and produced no diagnostic on either version. The menu describes the output
without promising a warning. A separate `-c` check returned one for the same
input. [GNU context line control](https://www.gnu.org/software/grep/manual/grep.html#Context-Line-Control)

## Manual-only coverage

All three sources list the same 48 distinct long spellings in their option
declarations. Of these, 14 have selectable menu rows. The other 34 are listed
below, counting aliases separately. Short aliases and the short-only binary
file selector `-I` do not add menu rows.

`--after-context`, `--basic-regexp`, `--before-context`, `--binary`, `--binary-files`,
`--byte-offset`, `--color`, `--colour`, `--dereference-recursive`, `--devices`,
`--directories`, `--exclude-dir`, `--exclude-from`, `--file`, `--files-without-match`,
`--group-separator`, `--help`, `--initial-tab`, `--label`, `--line-buffered`, `--line-regexp`,
`--max-count`, `--no-filename`, `--no-group-separator`, `--no-ignore-case`, `--no-messages`,
`--null`, `--null-data`, `--perl-regexp`, `--quiet`, `--silent`, `--text`, `--version`,
`--with-filename`.

## Rendered-menu verification

The Bash/tmux tests use the bundled profile with discovery disabled. A shell
stub detects execution of a pending grep command. The focused regression
searches for “group separator”, checks the `-o` qualification at 60×16,
cancels to the original line and cursor, and inserts `--context=` before the
existing pattern and filename. The separate executable checks above use only
temporary fixture data inside the offline sandboxes.

Run the focused regression from the repository root using the
[local sandbox runner](development.md#isolated-local-debugging).

```bash
python3 -I tests/run_sandbox.py -- python3 -m unittest discover -s tests \
  -p test_terminal_screen.py -k test_grep_context_search_scroll_and_midline_edit -v
```

On each target, inspection of a 160×56 tmux pane confirmed that all 14 option
rows displayed their full summaries and that the Details pane displayed all
edited descriptions. The numerical input and zero-value guidance remained
visible for `--context=`. Each full offline suite also passed the 60×16
regression with the pending command unexecuted.

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 24.04.5 LTS | 3.10.20 | 1,329 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,329 | 0 | 1 |
| 26.04.1 LTS | 3.14.4 | 1,329 | 0 | 1 |

The skip in each run was the Windows-specific probe test.
