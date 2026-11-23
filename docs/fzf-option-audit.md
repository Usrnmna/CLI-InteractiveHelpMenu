# fzf option audit

The [bundled fzf menu](../profiles/fzf.json) contains 17 selectable spellings. The audit covers matching, selection, field handling, display, key bindings, preview and record separators.

## Sources

| Reference | Version | Scope |
| --- | --- | --- |
| [Upstream fzf manual](https://github.com/junegunn/fzf/blob/v0.75.0/man/man1/fzf.1) | 0.75.0 | Options, extended search, field expressions, preview placeholders, bindings and exit status. |
| [Ubuntu 24.04 fzf(1)](https://manpages.ubuntu.com/manpages/noble/man1/fzf.1.html) | 0.44.1-1ubuntu0.3 | Noble manual and distribution package. |
| [Ubuntu 26.04 fzf(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fzf.1.html) | 0.67.0-1 | Resolute manual and distribution package. |
| [Pinned manual](https://github.com/junegunn/fzf/blob/v0.60.3/man/man1/fzf.1), [argument parser](https://github.com/junegunn/fzf/blob/v0.60.3/src/options.go) and [selection actions](https://github.com/junegunn/fzf/blob/v0.60.3/src/terminal.go) | 0.60.3 | Version used by the structured value guides, including selection count, height modifiers and delimiter parsing. |

## Disposition of the 17 entries

The disposition applies to the original wording, including its structured value guide. Rows follow menu order.

| Entry | Disposition | Finding and change |
| --- | --- | --- |
| `--multi` | Redundant | Put the selection action in the summary. Tab and Shift-Tab mark items. A positive maximum caps the marked items, omission enables multiple selection without a user cap and zero disables it. |
| `-m` | Redundant | Give the short spelling the same effect and limits. It accepts an attached count such as `-m2`. |
| `--exact` | Incomplete | A plain term must occur as a contiguous substring. A longer item can still match. In extended search, `^cat$` anchors both ends and a leading single quote switches an individual term back to fuzzy matching. |
| `--query` | Sufficient as written | Keep the summary. The supplied text starts in the editable prompt. Quote multiword text to pass one argument. |
| `-q` | Sufficient as written | Retain the initial-query summary and the same distinction from filter mode. |
| `--filter` | Incomplete | Print matching items and exit directly. A match returns status 0 and no matches returns 1. |
| `-f` | Incomplete | Give the short spelling the same output, exit-status and quoting guidance. |
| `--height` | Incomplete | Keep rows, percentages and adaptive sizing. Explain the Ubuntu version boundary for inverse heights and the restriction on percentage-based vertical margins and padding with adaptive height. |
| `--layout` | Incomplete | Distinguish the prompt from the best match. The default places them at the bottom. Both reverse layouts start the list at the top, and `reverse-list` keeps the prompt at the bottom. |
| `--bind` | Redundant | Replace repeated grammar and version text with a working comma-separated binding example. A colon assigns an action and a plus sign chains actions. |
| `--preview` | Incomplete | Highlighting an item can already run the preview command. The command is one shell argument. fzf substitutes the shell-quoted current item for `{}` and shows the command output. |
| `--prompt` | Sufficient as written | Keep the summary and show a quoted prompt with a trailing space. The prompt labels the editable query. |
| `--header` | Incomplete | The fixed header can contain multiple lines. Their order stays top-to-bottom across layouts. |
| `--delimiter` | Inaccurate | The old value guide attributed AWK-style matching to the supplied delimiter. AWK-style whitespace splitting is the default. An explicit delimiter follows fzf's version-specific parser. Use `--delimiter '[.]'` for a literal dot on both Ubuntu releases. |
| `--nth` | Redundant | Replace the repeated index grammar with a short example and its consequence. Field selection restricts matching. After `--with-nth`, count the displayed fields. Acceptance ordinarily emits the original item. Detailed signed indices and inclusive, open-ended ranges remain in the value guide. |
| `--read0` | Sufficient as written | Keep the input-specific summary. Use it for incoming NUL-delimited items containing newlines. Output has its own switch. |
| `--print0` | Sufficient as written | Keep the output-specific summary. Each printed item receives a NUL terminator. Input has its own switch. |

## Compatibility and manual-only coverage

- **Custom delimiters.** Noble compiles a single dot as a regular expression. The pinned 0.60.3 parser, Resolute and upstream 0.75.0 treat a single character literally. All four parsers recognize the multi-character expression `[.]` as a literal dot. The pinned parser treats an invalid regex as literal text. [Noble-era parser](https://github.com/junegunn/fzf/blob/0.44.1/src/options.go#L502), [pinned parser](https://github.com/junegunn/fzf/blob/v0.60.3/src/options.go#L836), [Resolute-era parser](https://github.com/junegunn/fzf/blob/v0.67.0/src/options.go#L874) and [upstream parser](https://github.com/junegunn/fzf/blob/v0.75.0/src/options.go#L921)
- **Height.** Positive rows, percentages and adaptive caps such as `~40%` are available on both Ubuntu releases. Noble rejects negative height. Resolute accepts inverse height such as `-2`. Both reject the combined form `~-2`, which upstream 0.75.0 documents. The 0.60.3 numerical guide retains its original version scope, six layout forms and percentage bounds. [Noble height parser](https://github.com/junegunn/fzf/blob/0.44.1/src/options.go#L1381), [pinned height parser](https://github.com/junegunn/fzf/blob/v0.60.3/src/options.go#L1900) and [upstream manual](https://github.com/junegunn/fzf/blob/v0.75.0/man/man1/fzf.1)
- **Selection count and insertion.** The menu inserts the literal option. `--multi=2`, `--multi 2`, `-m2` and `-m 2` are accepted program forms. A separate optional count must begin with a digit in the pinned parser. An attached signed integer can also reach the parser, and the selection actions require a positive limit. The guide now records the behavior of attached negative values. The editor retains its existing recognition of nonnegative optional operands. [Argument parser](https://github.com/junegunn/fzf/blob/v0.60.3/src/options.go#L2270), [selection actions](https://github.com/junegunn/fzf/blob/v0.60.3/src/terminal.go#L5216) and [argument regression](../tests/test_system_dependency_followup.py)
- **Other controls.** The curated menu omits additional aliases such as `-e`, `-d` and `-n`. Manual-only options also cover smart case and sorting, display transformations with `--with-nth`, prompt placement, headers taken from input, preview-window positioning, color, history, automatic selection and exit. Resolute and current upstream also document `--accept-nth` for changing output fields. The full binding action list, search operators and placeholder syntax remain in the manuals. [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/fzf.1.html), [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/fzf.1.html) and [upstream manual](https://github.com/junegunn/fzf/blob/v0.75.0/man/man1/fzf.1)

The 20 changed review fingerprints cover the 17 rows, the command header, the profile file and the shared selection-limit definition. The preview and binding guides now cite their owning manual sections. The option order, insertion spellings and optional-argument metadata were preserved. [Numerical inventory review](numerical-inventory/review.json)

## Observed fzf behavior

The packaged fzf 0.44.1 and 0.67.0 executables ran in offline sandboxes against fixed, disposable input. Interactive fixtures used private tmux sockets and a preview that only printed a field. [Ubuntu package archive](https://archive.ubuntu.com/ubuntu/pool/universe/f/fzf/)

| Fixture | Observed result |
| --- | --- |
| Fuzzy, exact and anchored search | From `cat`, `scatter`, `cXaXt` and `dog`, both builds matched the first three for `cat`, the first two for `--exact` and only `cat` for the anchored query `^cat$`. Filter mode returned 1 for a missing term. |
| Delimiters and transformed fields | Splitting `a.ok` on `.` and searching field 2 for `ok` failed to match on Noble and matched on Resolute. The expression `[.]` matched on both. Both also accepted a multi-character regex delimiter. With `id:two:red`, `--with-nth 2.. --nth 1` matched `two` and Enter returned the original three-field item. |
| Record separators | Both builds preserved an embedded newline in a matching input item with `--read0`. Combining it with `--print0` emitted a NUL terminator. Each switch also worked independently. |
| Height parsing | Both accepted row, fractional percentage and adaptive percentage values. Only Resolute accepted `--height=-2`. Both rejected `--height=~-2` with status 2. |
| Marking items | In both finders two Tab presses followed by Enter returned two items with bare `--multi`. The same keys returned one item with `-m1`, `--multi=0`, `--multi=-1` or `-m-1`. |
| Layout, bindings and preview | In each of the three layouts, the observed prompt and first-match positions agreed with the menu. The finder displayed the initial query and both header lines in order. Moving between matches with bound keys changed a field-based preview before Enter. Accepting returned the highlighted original item. |

This filter prints `a.ok` and exits with status 0 on both Ubuntu builds. Changing `'[.]'` to `'.'` gives no output and status 1 on Noble.

```bash
printf '%s\n' a.ok a.no | fzf --delimiter '[.]' --nth 2 --filter ok
```

## Rendered menu and sandbox checks

On each target a real Bash/tmux session with discovery disabled visited all 17 rows at 200×78. Each visible label, summary, command header and complete Details pane agreed with the profile and formatter. At 60×16 the regression searched for “literal dot”, scrolled to the version-specific interpretation, and checked that cancellation restored the original pending line and cursor. Selecting `--delimiter` and entering `'[.]'` preserved the existing `--nth 2` suffix. The fzf stub recorded zero executions. [Terminal regression](../tests/test_expansion_terminal.py)

The first full-suite run caught a missing unit in the `--height` summary. The revised summary names terminal rows and percentages directly. Five focused tests then passed on each target, covering the minimum-size terminal interaction, optional selection counts, numerical semantics, visible units and the inventory review. To repeat the terminal check, substitute `host`, `noble310` or `noble312` for TARGET. [Sandbox instructions](development.md#isolated-local-debugging)

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k fzf_literal_dot_delimiter_at_minimum_size -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,336 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,336 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,336 | 0 | 1 |

Each full-suite snapshot included the untracked audit documents. The single skip on every target was the Windows-specific probe.
