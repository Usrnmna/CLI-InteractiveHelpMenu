# Git stash show option inventory

The comparison uses the stash's base commit and saved working tree. With no stash operand it uses the latest stash. Adding `-u` includes the saved third parent when present. Using `--only-untracked` compares that parent's tree with an empty tree. [Upstream stash manual](https://git-scm.com/docs/git-stash/2.56.0) · [Noble stash manual](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html) · [Resolute stash manual](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html)

## Manual inventory

The table groups 112 selectable spellings into 96 option effects, including short usage, stash content selection and delegated diff controls. The first pass had nine rows. The revisit adds 103. Every literal spelling in the table has a row. Combined modes such as `--patch-with-stat` have their own entries. Brackets enclose an optional operand, and its position shows the required attachment. A separate non-option word always goes to the stash selector. The original `--stat` row still inserts the bare flag.

The references are the upstream Git 2.56.0 diff manual, Ubuntu 24.04 Git 1:2.43.0-1ubuntu7.4 and Ubuntu 26.04 Git 1:2.53.0-1ubuntu1.1. “All” refers to syntax across these three references. Packaged output exceptions appear below. The two usage captures print the stash-specific options on stdout with status 129. Their synopsis delegates the remaining formatting options to the diff manual. [Upstream diff manual](https://git-scm.com/docs/git-diff/2.56.0) · [Noble diff manual](https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html) · [Resolute diff manual](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff.1.html) · [Noble usage](../tests/fixtures/git-stash-worktree/noble-usage.json) · [Resolute usage](../tests/fixtures/git-stash-worktree/resolute-usage.json)

| Spellings and operands | Availability | Effect |
| --- | --- | --- |
| `-p` / `--patch` | All | Show the stashed changes as a patch |
| `--stat[=WIDTH[,NAME-WIDTH[,COUNT]]]` | All | Summarize changes by file |
| `--name-only` | All | List changed paths |
| `--name-status` | All | List changed paths with their status |
| `-u` / `--include-untracked` | All | Show saved untracked files too |
| `--only-untracked` | All | Show only the saved untracked files |
| `--binary` | All | Include applicable binary patches |
| `--no-include-untracked` | All | Exclude the saved untracked files |
| `-h` / `--help` / `--help-all` | All | Display stash show usage |
| `-s` / `--no-patch` | All | Suppress diff output |
| `-U[LINES]` / `--unified[=LINES]` | All | Show a patch with this many context lines |
| `--output=FILE` | All | Write the diff to a file |
| `--output-indicator-new=CHAR` | All | Change the marker for added lines |
| `--output-indicator-old=CHAR` | All | Change the marker for removed lines |
| `--output-indicator-context=CHAR` | All | Change the marker for context lines |
| `--raw` | All | Show file modes, object IDs, status and paths |
| `-t` | All | Include changed directory entries in the diff |
| `--patch-with-raw` | All | Show raw change records and a patch |
| `--indent-heuristic` | All | Shift hunk boundaries for readability |
| `--no-indent-heuristic` | All | Disable indentation-based hunk placement |
| `--minimal` | All | Spend more time finding a smaller diff |
| `--patience` | All | Use the patience diff algorithm |
| `--histogram` | All | Use the histogram diff algorithm |
| `--anchored=TEXT` | All | Anchor the diff at matching lines |
| `--diff-algorithm=ALGORITHM` | All | Choose how Git matches changed lines |
| `--stat-width=WIDTH` | All | Set the maximum width of a diffstat |
| `--stat-name-width=WIDTH` | All | Limit the filename column in a diffstat |
| `--stat-graph-width=WIDTH` | All | Limit the graph width in a diffstat |
| `--stat-count=COUNT` | All | Limit the number of files in a diffstat |
| `--compact-summary` | All | Include file and mode changes in the diffstat |
| `--numstat` | All | Show added and deleted line counts per file |
| `--shortstat` | All | Show only diffstat totals |
| `-X[PARAMETERS]` / `--dirstat[=PARAMETERS]` | All | Report each directory's share of the changes |
| `--cumulative` | All | Include child directories in parent change shares |
| `--dirstat-by-file[=PARAMETERS]` | All | Measure directory shares by changed file count |
| `--summary` | All | Summarize file creation, renames and mode changes |
| `--patch-with-stat` | All | Show a diffstat and a patch |
| `-z` | All | Terminate path fields with NUL |
| `--submodule[=FORMAT]` | All | Choose how changed submodule commits appear |
| `--color[=WHEN]` | All | Control colored diff output |
| `--no-color` | All | Suppress colored output |
| `--color-moved[=MODE]` | All | Highlight lines that moved within the diff |
| `--no-color-moved` | All | Turn off moved-line highlighting |
| `--color-moved-ws=MODES` | All | Choose whitespace rules for moved lines |
| `--no-color-moved-ws` | All | Respect whitespace when detecting moved lines |
| `--word-diff[=MODE]` | All | Show changes within lines word by word |
| `--word-diff-regex=REGEX` | All | Choose what counts as a word |
| `--color-words[=REGEX]` | All | Show changed words in color |
| `--no-renames` | All | Turn off rename and copy detection |
| `--rename-empty` | All | Allow empty blobs as rename sources |
| `--no-rename-empty` | All | Exclude empty blobs as rename sources |
| `--check` | All | Report new whitespace errors and conflict markers |
| `--ws-error-highlight=KINDS` | All | Choose which lines highlight whitespace errors |
| `--full-index` | All | Show complete blob IDs in patch index lines |
| `--abbrev[=DIGITS]` | All | Set the minimum object ID abbreviation length |
| `--no-abbrev` | All | Show complete object IDs in raw records |
| `-B[N[/M]]` / `--break-rewrites[=N[/M]]` | All | Split complete rewrites into deletions and creations |
| `-M[SCORE]` / `--find-renames[=SCORE]` | All | Detect renamed files by content similarity |
| `-C[SCORE]` / `--find-copies[=SCORE]` | All | Detect copied files as well as renames |
| `--find-copies-harder` | All | Consider unchanged files as copy sources |
| `-D` / `--irreversible-delete` | All | Omit the deleted file's patch content |
| `-lLIMIT` | All | Limit exhaustive rename and copy detection |
| `--diff-filter=STATUS` | All | Select paths by change status |
| `-STEXT` | All | Find files where a string's occurrence count changed |
| `-GREGEX` | All | Find files with matching added or removed lines |
| `--find-object=OBJECT` | All | Find changes in the number of references to an object |
| `--pickaxe-all` | All | Show the whole comparison when a pickaxe matches |
| `--pickaxe-regex` | All | Treat the -S string as an extended regular expression |
| `-OORDERFILE` | All | Read file display order from a pattern file |
| `--skip-to=PATH` | All | Start the output at a changed path |
| `--rotate-to=PATH` | All | Show a changed path first |
| `-R` | All | Reverse the direction of the diff |
| `--relative[=PATH]` | All | Limit output to a directory and shorten pathnames |
| `--no-relative` | All | Use repository-wide paths and scope |
| `-a` / `--text` | All | Treat binary files as text for comparison |
| `--ignore-cr-at-eol` | All | Ignore carriage returns at line ends |
| `--ignore-space-at-eol` | All | Ignore changes in trailing whitespace |
| `-b` / `--ignore-space-change` | All | Ignore changes in the amount of whitespace |
| `-w` / `--ignore-all-space` | All | Ignore whitespace when comparing lines |
| `--ignore-blank-lines` | All | Ignore changes made up only of blank lines |
| `-IREGEX` / `--ignore-matching-lines=REGEX` | All | Ignore changes whose lines all match a pattern |
| `--inter-hunk-context=LINES` | All | Join nearby patch hunks |
| `-W` / `--function-context` | All | Include the surrounding function in patch context |
| `--exit-code` | All | Signal differences with the exit status |
| `--quiet` | All | Test for differences without displaying them |
| `--ext-diff` | All | Allow configured external diff helpers |
| `--no-ext-diff` | All | Disable external diff helpers |
| `--textconv` | All | Allow configured text conversion for comparison |
| `--no-textconv` | All | Disable text conversion filters |
| `--ignore-submodules[=WHEN]` | All | Control which submodule changes are hidden |
| `--src-prefix=PREFIX` | All | Set the before-side pathname prefix |
| `--dst-prefix=PREFIX` | All | Set the after-side pathname prefix |
| `--no-prefix` | All | Remove both patch pathname prefixes |
| `--default-prefix` | All | Restore the standard patch pathname prefixes |
| `--line-prefix=PREFIX` | All | Prepend text to each line of diff output |
| `--max-depth=DEPTH` | Resolute and upstream | Limit how far the tree comparison descends |

## Ownership and exclusions

| Spellings or syntax | Disposition |
| --- | --- |
| Diff's lowercase `-u` | The stash parser consumes this spelling to select saved untracked content. Use `-p`, `--patch` or bare `-U` for a patch. |
| `--no-index`, `--cached` / `--staged`, `--merge-base` | These select independent comparison endpoints in standalone diff. Stash show supplies its own endpoints. Both Ubuntu clients rejected `--cached`, `--merge-base` and `--no-index` with status 129. |
| `-1` / `--base`, `-2` / `--ours`, `-3` / `--theirs`, `-0` | These choose unmerged index stages in standalone diff. The stash comparison has no such inputs. Short numerals can parse as revision limits and produce an ordinary diff. Accepted input does not establish stage selection. |
| `--ita-visible-in-index`, `--ita-invisible-in-index` | A stored tree has no intent-to-add bit. An internal index used to combine saved content contains populated entries. These switches cannot reveal a different intent-to-add entry. |
| `--cc`, `-c`, `--combined-all-paths`, log merge modes | A stash may have several parents. Show explicitly selects the base and working tree, or the saved untracked tree. The merge presentation controls in git-log do not turn it into a combined diff. |
| Tree recursion, commit headers and input options | Both clients produced ordinary raw file records with `-r`, `--root`, `-v`, `--no-commit-id`, `--always` and `--pretty`. Recursion is already enabled, and no commit header is generated. `--stdin` with empty input also returned the normal comparison. The standalone diff-tree mode for reading pairs of endpoints does not apply to stash show. |
| `--no-stat`, `--no-only-untracked` | The first belongs to format-patch in the shared diff-options manual source. The stash parser disables negation on the second. Both packaged clients returned 129. |
| `[--] <path>…`, revisions, endpoints, ranges and blob operands from standalone diff | Show accepts at most one stash-like reference, including a numeric stash index. A pathname following `--` is still considered a stash operand. Use standalone diff when selecting other endpoints or pathspecs. |
| `--abbrev-commit`, `--pretty`, traversal, history limiting and reflog filters | Revision parsing is shared internally, but show performs a single diff and prints no commit headers. These switches cannot select or format a history walk here. `--no-abbrev` has a distinct, observed raw-diff effect and is included. |
| Selector-only primitives such as `--no-ext-diff` and `--no-textconv` | Included because they affect the permitted diff machinery. No external helper was executed during verification. |

The diff-tree manual documents `-t` separately from recursion. With `-t`, a changed directory appears alongside its contents in a raw or name-status listing. [Upstream diff-tree manual](https://git-scm.com/docs/git-diff-tree/2.56.0) · [Noble diff-tree manual](https://manpages.ubuntu.com/manpages/noble/man1/git-diff-tree.1.html) · [Resolute diff-tree manual](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff-tree.1.html)

The manual headings, inline diffstat setters, stage selectors and delegated diff-algorithm section were reconciled against the shared diff option declarations. Generic abbreviation of long options and mechanically synthesized, undocumented parser inverses are outside the published spelling count. [Tagged common diff options](https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/diff-options.adoc) · [Diff algorithm choices](https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/diff-algorithm-option.adoc) · [Tagged diff parser](https://raw.githubusercontent.com/git/git/v2.56.0/diff.c) · [Tagged revision parser](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c)

## Packaged observations

The following checks used fresh repositories in the project's offline host and Noble sandboxes with two changed tracked paths at different depths and one saved untracked path. Status zero indicates that Git accepted the invocation. Output and resulting state establish the effects separately.

| Private fixture check | Ubuntu 24.04 Git 2.43.0 | Ubuntu 26.04 Git 2.53.0 |
| --- | --- | --- |
| Lowercase `-u`, uppercase `-U`, attached `-U0` | Lowercase added the saved untracked file to the default stat. Bare uppercase printed a tracked-only patch. The attached zero removed surrounding context. | Same. |
| `--stat=30,10,1`, `--stat 30`, `-U 0` | Attached values showed one file row, an ellipsis and overall totals. The separated 30 selected an unavailable stash (128). The separated zero selected stash zero and retained normal context. | Same. |
| Configured untracked default, explicit inclusion, exclusion and untracked-only listing | Each option selects the corresponding stored paths. | Same. |
| `-t --raw`, `-t --name-status`, `-r --raw` | Both `-t` formats added the changed directory as a separate record. The raw record had mode 040000 on both sides. Explicit recursion alone kept only the changed files. | Same. |
| `--exit-code`, `--quiet` | Both returned 1 for differences. Only the first printed a patch. | Same. |
| `--max-depth=0 --name-only` | Rejected (129). | Printed the directory entry and top-level file. Depth 1 printed the nested filename. With `-u` and a saved untracked tree, Git rejected the implicit index diff (128). With `--only-untracked`, depth zero listed the saved top-level untracked file. |
| Explicit string and regex pickaxes, a relative directory, and before/after prefixes | The selected files and pathnames agreed with their operands. | Accepted syntax did not reliably produce the requested matches or prefixes. Some runs reported a regex error for a valid expression. The specific bytes and diagnostics varied. |
| `--abbrev=4 --raw`, `--no-abbrev --raw` | The first printed four hex digits for the fixture objects. The second printed full SHA-1 IDs. | Same. |

In these Ubuntu releases a negative unified context can be accepted and produce malformed patch ranges. Use a nonnegative line count. Upstream 2.56.0 rejects negative values. The tagged stash implementation explains the option/selector split and the distinct comparisons for tracked and saved untracked content. The tagged revision parsers also differ in their handling of option arguments. A successful parse on Git 2.53.0 does not establish correct output for every string-valued diff option. [Noble stash implementation](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/stash.c) · [Resolute stash implementation](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/stash.c) · [Upstream stash implementation](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/stash.c) · [Resolute revision parser](https://raw.githubusercontent.com/git/git/v2.53.0/revision.c) · [Upstream revision parser](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c) · [Upstream context handling](https://raw.githubusercontent.com/git/git/v2.56.0/diff.c)

The [family verification report](git-stash-worktree-manual-coverage.md) records the rendered-menu and compatibility suite results.

## Output operand regression

In the [hosted Linux run](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/45280846559), Git 2.56.1 returned 128 for `stash show --output nonexistent`. The packaged Ubuntu clients returned 1. All three versions treated the separate word as an invalid stash reference. The [tagged stash dispatcher](https://raw.githubusercontent.com/git/git/v2.56.1/builtin/stash.c) maps negative subcommand results to 128. The [regression](../tests/test_git_stash_show.py) compares the separate form with the same failed stash lookup, checks the diagnostic and absence of an output file, then verifies that `--output=diff.txt -p` writes a patch.
