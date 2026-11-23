# Git log manual inventory

The original ten rows expand to 234 selectable spellings. The 209 groups below include 25 additional literal aliases. Presets, resets and options with different default behavior have separate groups. The variable shorthand `-NUMBER` also sets a positive count without consuming the next word. The ten original literals retain their relative order.

## Sources and scope

| Release | Primary references |
| --- | --- |
| Upstream Git, log manual revision 2.56.0 | [Log options, revision walk, pretty formats and diff formatting](https://git-scm.com/docs/git-log/2.56.0), [revision arguments](https://git-scm.com/docs/gitrevisions/2.56.0), [revision enumeration](https://git-scm.com/docs/git-rev-list/2.56.0), [diff comparisons](https://git-scm.com/docs/git-diff/2.56.0) |
| Ubuntu 24.04 Noble, git-man 1:2.43.0-1ubuntu7.4 | [git-log(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) and [fixed client usage](../tests/fixtures/git-commit-log/noble-usage.json) |
| Ubuntu 26.04 Resolute, git-man 1:2.53.0-1ubuntu1.1 | [git-log(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) and [fixed client usage](../tests/fixtures/git-commit-log/resolute-usage.json) |

The inventory covers the option declarations in all three rendered log manuals, including single-file line history, commit limiting, history simplification, ordering, formatting, merge diffs and the shared diff controls. Supplemental entries cover applicable operands and resets in the surrounding manual text, the delegated revision and diff references, and fixed usage. The packaged clients print the built-in options with `-h` and return 129. Their short usage omits most of the shared revision and diff grammar. The existing Git 2.43.0 man excerpt covers the numeric shorthand, `-n`, `--max-count`, `--all` and `--oneline`. The three-option representative specimen remains separate. [Captured man excerpts](../tests/fixtures/help/captured.json) · [Representative log specimen](../tests/fixtures/help/git-log.txt)

The [stash list inventory](git-stash-list-inventory.md) and [stash show inventory](git-stash-show-inventory.md) provide cross-checks for shared operands. Normal log starts with HEAD and follows parent links. It accepts symmetric differences, walks backward through parents, and can follow the history of one file across renames. A reflog walk requires an explicit `-g`. The history mode changes the meaning of date limits and determines which traversal options work. [Revision parser for Noble](https://raw.githubusercontent.com/git/git/v2.43.0/revision.c) · [Resolute](https://raw.githubusercontent.com/git/git/v2.53.0/revision.c) · [upstream](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c)

## Selectable inventory

Each backticked spelling in the first column has its own row. A trailing equals sign is part of the insertion. Required long operands generally accept either `=VALUE` or a separate word. “Optional =” means Git accepts the bare switch and only accepts a value attached with an equals sign. The original `--decorate` and `--stat` rows insert bare flags. Other optional long-value rows insert the option followed by `=`, with the cursor ready for the value. For optional short operands, the cursor remains immediately after the flag. “All” denotes Git 2.43.0, 2.53.0 and 2.56.0, subject to the mode and configuration qualifications in Details.

| Selectable spellings | Operand | Accepted form | Releases | Effect |
| --- | --- | --- | --- | --- |
| `-h` | — | — | All | Print the short log usage |
| `--help` | — | — | All | Open the git-log manual |
| `--help-all` | — | — | All | Print extended built-in usage |
| `--oneline` | — | — | All | Show an abbreviated ID and commit subject |
| `--format=` | `FORMAT` | = only | All | Choose the commit output format |
| `--date=` | `FORMAT` | = or separate | All | Choose how commit dates are displayed |
| `--pretty` | `FORMAT` | optional = | All | Choose a built-in or custom commit layout |
| `--abbrev-commit` | — | — | All | Shorten displayed commit IDs |
| `--no-abbrev-commit` | — | — | All | Show full commit IDs |
| `--relative-date` | — | — | All | Display dates as ages |
| `--decorate` | `STYLE` | optional = | All | Show ref names beside the commits they identify |
| `--no-decorate` | — | — | All | Hide ref-name decorations |
| `--decorate-refs=` | `PATTERN` | = or separate | All | Limit decorations to matching refs |
| `--decorate-refs-exclude=` | `PATTERN` | = or separate | All | Hide decorations matching a ref pattern |
| `--clear-decorations` | — | — | All | Clear filters on ref-name decorations |
| `--mailmap`, `--use-mailmap` | — | — | All | Display canonical author and committer identities |
| `--no-mailmap`, `--no-use-mailmap` | — | — | All | Display recorded author and committer identities |
| `--encoding=` | `ENCODING` | = or separate | All | Convert commit messages to an output encoding |
| `--expand-tabs` | `COLUMNS` | optional = | All | Expand message tabs to tab stops |
| `--no-expand-tabs` | — | — | All | Preserve tabs in log messages |
| `--notes` | `REF` | optional = | All | Show notes attached to commits |
| `--show-notes` | `REF` | optional = | All | Show commit notes using the older selection rules |
| `--no-notes` | — | — | All | Clear the selected notes refs |
| `--show-notes-by-default` | — | — | All | Include default notes unless other notes were selected |
| `--standard-notes` | — | — | All | Add the default notes refs to the selected notes |
| `--no-standard-notes` | — | — | All | Exclude the default refs from a notes selection |
| `--show-signature` | — | — | All | Verify and display commit signatures |
| `--log-size` | — | — | All | Print the formatted message length in bytes |
| `--parents` | — | — | All | Show parent IDs in commit headers |
| `--show-linear-break` | `TEXT` | optional = | All | Mark breaks between nonlinear commits |
| `-n`, `--max-count=` | `COUNT` | short attached or separate, long = or separate | All | Limit the number of matching commits |
| `--max-count-oldest=` | `COUNT` | = only | 2.56 only | Select the oldest matching commits |
| `--skip=` | `COUNT` | = or separate | All | Skip matching commits before applying the count limit |
| `--since=`, `--after=` | `DATE` | = or separate | All | Show commits from a date onward |
| `--since-as-filter=` | `DATE` | = or separate | All | Filter by date after visiting the entire range |
| `--until=`, `--before=` | `DATE` | = or separate | All | Show commits through a date |
| `--max-age=` | `TIMESTAMP` | = or separate | All | Set the earliest commit time in epoch seconds |
| `--min-age=` | `TIMESTAMP` | = or separate | All | Set the latest commit time in epoch seconds |
| `--author=` | `PATTERN` | = or separate | All | Match the author name or email |
| `--committer=` | `PATTERN` | = or separate | All | Match the committer name or email |
| `--grep-reflog=` | `PATTERN` | = or separate | All | Match reflog messages |
| `--grep=` | `PATTERN` | = or separate | All | Match commit messages by regular expression |
| `--all-match` | — | — | All | Require every commit-message pattern to match |
| `--invert-grep` | — | — | All | Keep commits whose message misses the patterns |
| `-i`, `--regexp-ignore-case` | — | — | All | Ignore case when matching patterns |
| `--basic-regexp` | — | — | All | Use basic regular expressions for log patterns |
| `-E`, `--extended-regexp` | — | — | All | Use extended regular expressions for log patterns |
| `-F`, `--fixed-strings` | — | — | All | Treat log search patterns as literal strings |
| `-P`, `--perl-regexp` | — | — | All | Use Perl-compatible log patterns |
| `--merges` | — | — | All | Show commits with at least two parents |
| `--no-merges` | — | — | All | Show commits with at most one parent |
| `--min-parents=` | `COUNT` | = only | All | Require a minimum number of parents |
| `--max-parents=` | `COUNT` | = only | All | Limit the number of parents |
| `--no-min-parents` | — | — | All | Clear the minimum parent count |
| `--no-max-parents` | — | — | All | Clear the maximum parent count |
| `--all` | — | — | All | Walk history from all refs and HEAD |
| `--branches` | `GLOB` | optional = | All | Start from local branches |
| `--tags` | `GLOB` | optional = | All | Start from tag refs |
| `--remotes` | `GLOB` | optional = | All | Start from remote-tracking refs |
| `--glob=` | `GLOB` | = or separate | All | Start from refs matching a shell-style pattern |
| `--exclude=` | `GLOB` | = or separate | All | Exclude matching refs from the next ref selector |
| `--exclude-hidden=` | `MODE` | = or separate | All | Apply hidden-ref configuration to the next ref selector |
| `--reflog` | — | — | All | Start from objects mentioned in reflogs |
| `--single-worktree` | — | — | All | Restrict ref enumeration to the current worktree |
| `--alternate-refs` | — | — | All | Start from ref tips in alternate object stores |
| `--ignore-missing` | — | — | All | Ignore invalid object names in revision arguments |
| `--stdin` | — | — | All | Read additional revision arguments from standard input |
| `--follow` | — | — | All | Follow one file's history across renames |
| `--full-diff` | — | — | All | Show the complete diff for each matching commit |
| `--dense` | — | — | All | Show commits needed to explain the selected paths |
| `--sparse` | — | — | All | Show every commit visited by the path-limited walk |
| `--first-parent` | — | — | All | Follow only the first parent of included merges |
| `-g`, `--walk-reflogs` | — | — | All | Walk ref updates in reflog order |
| `--boundary` | — | — | All | Show excluded commits at the edge of the walk |
| `--left-right` | — | — | All | Mark commits by side of a symmetric difference |
| `--diff-merges=` | `MODE` | = or separate | All | Choose how merge commits are compared |
| `--no-diff-merges` | — | — | All | Suppress comparisons for merge commits |
| `-m` | — | — | All | Use the configured default merge diff |
| `-c` | — | — | All | Show a combined patch against all parents |
| `--cc` | — | — | All | Show a dense combined patch |
| `--dd` | — | — | All | Show a patch against the first parent of each merge |
| `--remerge-diff` | — | — | All | Compare two-parent merges against an automatic remerge |
| `--combined-all-paths` | — | — | All | Show parent pathnames in combined raw output |
| `-t` | — | — | All | Include tree entries in raw diff output |
| `--unpacked` | — | — | All | Select commits stored as loose objects |
| `-p`, `--patch`, `-u` | — | — | All | Show changes as a patch |
| `--stat` | `WIDTH[,NAME-WIDTH[,COUNT]]` | optional = | All | Summarize changes per file |
| `--name-only` | — | — | All | List changed paths |
| `--name-status` | — | — | All | List changed paths with their status |
| `--binary` | — | — | All | Include applicable binary patches |
| `-s`, `--no-patch` | — | — | All | Suppress diff output |
| `-U`, `--unified` | `LINES` | short attached, long = | All | Show a patch with this many context lines |
| `--output=` | `FILE` | = or separate | All | Write the diff to a file |
| `--output-indicator-new=` | `CHAR` | = or separate | All | Change the marker for added lines |
| `--output-indicator-old=` | `CHAR` | = or separate | All | Change the marker for removed lines |
| `--output-indicator-context=` | `CHAR` | = or separate | All | Change the marker for context lines |
| `--raw` | — | — | All | Show file modes, object IDs, status and paths |
| `--patch-with-raw` | — | — | All | Show raw change records and a patch |
| `--indent-heuristic` | — | — | All | Shift hunk boundaries for readability |
| `--no-indent-heuristic` | — | — | All | Disable indentation-based hunk placement |
| `--minimal` | — | — | All | Spend more time finding a smaller diff |
| `--patience` | — | — | All | Use the patience diff algorithm |
| `--histogram` | — | — | All | Use the histogram diff algorithm |
| `--anchored=` | `TEXT` | = or separate | All | Anchor the diff at matching lines |
| `--diff-algorithm=` | `ALGORITHM` | = or separate | All | Choose how Git matches changed lines |
| `--stat-width=` | `WIDTH` | = or separate | All | Set the maximum width of a diffstat |
| `--stat-name-width=` | `WIDTH` | = or separate | All | Limit the filename column in a diffstat |
| `--stat-graph-width=` | `WIDTH` | = or separate | All | Limit the graph width in a diffstat |
| `--stat-count=` | `COUNT` | = or separate | All | Limit the number of files in a diffstat |
| `--compact-summary` | — | — | All | Include file and mode changes in the diffstat |
| `--numstat` | — | — | All | Show added and deleted line counts per file |
| `--shortstat` | — | — | All | Show only diffstat totals |
| `-X`, `--dirstat` | `PARAMETERS` | short attached, long = | All | Report each directory's share of the changes |
| `--cumulative` | — | — | All | Include child directories in parent change shares |
| `--dirstat-by-file` | `PARAMETERS` | optional = | All | Measure directory shares by changed file count |
| `--summary` | — | — | All | Summarize file creation, renames and mode changes |
| `--patch-with-stat` | — | — | All | Show a diffstat and a patch |
| `-z` | — | — | All | Terminate path fields with NUL |
| `--submodule` | `FORMAT` | optional = | All | Choose how changed submodule commits appear |
| `--color` | `WHEN` | optional = | All | Control colored diff output |
| `--no-color` | — | — | All | Suppress colored output |
| `--color-moved` | `MODE` | optional = | All | Highlight lines that moved within the diff |
| `--no-color-moved` | — | — | All | Turn off moved-line highlighting |
| `--color-moved-ws=` | `MODES` | = or separate | All | Choose whitespace rules for moved lines |
| `--no-color-moved-ws` | — | — | All | Respect whitespace when detecting moved lines |
| `--word-diff` | `MODE` | optional = | All | Show changes within lines word by word |
| `--word-diff-regex=` | `REGEX` | = or separate | All | Choose what counts as a word |
| `--color-words` | `REGEX` | optional = | All | Show changed words in color |
| `--no-renames` | — | — | All | Turn off rename and copy detection |
| `--rename-empty` | — | — | All | Allow empty blobs as rename sources |
| `--no-rename-empty` | — | — | All | Exclude empty blobs as rename sources |
| `--check` | — | — | All | Report new whitespace errors and conflict markers |
| `--ws-error-highlight=` | `KINDS` | = or separate | All | Choose which lines highlight whitespace errors |
| `--full-index` | — | — | All | Show complete blob IDs in patch index lines |
| `--abbrev` | `DIGITS` | optional = | All | Set the minimum object ID abbreviation length |
| `--no-abbrev` | — | — | All | Show complete object IDs in raw records |
| `-B`, `--break-rewrites` | `N[/M]` | short attached, long = | All | Split complete rewrites into deletions and creations |
| `-M`, `--find-renames` | `SCORE` | short attached, long = | All | Detect renamed files by content similarity |
| `-C`, `--find-copies` | `SCORE` | short attached, long = | All | Detect copied files as well as renames |
| `--find-copies-harder` | — | — | All | Consider unchanged files as copy sources |
| `-D`, `--irreversible-delete` | — | — | All | Omit the deleted file's patch content |
| `-l` | `LIMIT` | attached or separate | All | Limit exhaustive rename and copy detection |
| `--diff-filter=` | `STATUS` | = or separate | All | Select paths by change status |
| `-S` | `TEXT` | attached or separate | All | Find commits that change the occurrence count of text |
| `-G` | `REGEX` | attached or separate | All | Find commits with matching added or deleted lines |
| `--find-object=` | `OBJECT` | = or separate | All | Find changes in the number of references to an object |
| `--pickaxe-all` | — | — | All | Show the whole comparison when a pickaxe matches |
| `--pickaxe-regex` | — | — | All | Treat the -S string as an extended regular expression |
| `-O` | `ORDERFILE` | attached or separate | All | Read file display order from a pattern file |
| `--skip-to=` | `PATH` | = or separate | All | Start the output at a changed path |
| `--rotate-to=` | `PATH` | = or separate | All | Show a changed path first |
| `-R` | — | — | All | Reverse the direction of the diff |
| `--relative` | `PATH` | optional = | All | Limit output to a directory and shorten pathnames |
| `--no-relative` | — | — | All | Use repository-wide paths and scope |
| `-a`, `--text` | — | — | All | Treat binary files as text for comparison |
| `--ignore-cr-at-eol` | — | — | All | Ignore carriage returns at line ends |
| `--ignore-space-at-eol` | — | — | All | Ignore changes in trailing whitespace |
| `-b`, `--ignore-space-change` | — | — | All | Ignore changes in the amount of whitespace |
| `-w`, `--ignore-all-space` | — | — | All | Ignore whitespace when comparing lines |
| `--ignore-blank-lines` | — | — | All | Ignore changes made up only of blank lines |
| `-I`, `--ignore-matching-lines=` | `REGEX` | short attached or separate, long = or separate | All | Ignore changes whose lines all match a pattern |
| `--inter-hunk-context=` | `LINES` | = or separate | All | Join nearby patch hunks |
| `-W`, `--function-context` | — | — | All | Include the surrounding function in patch context |
| `--exit-code` | — | — | All | Signal differences with the exit status |
| `-q`, `--quiet` | — | — | All | Request quiet diff output |
| `--ext-diff` | — | — | All | Allow configured external diff helpers |
| `--no-ext-diff` | — | — | All | Disable external diff helpers |
| `--textconv` | — | — | All | Allow configured text conversion for comparison |
| `--no-textconv` | — | — | All | Disable text conversion filters |
| `--ignore-submodules` | `WHEN` | optional = | All | Control which submodule changes are hidden |
| `--src-prefix=` | `PREFIX` | = or separate | All | Set the before-side pathname prefix |
| `--dst-prefix=` | `PREFIX` | = or separate | All | Set the after-side pathname prefix |
| `--no-prefix` | — | — | All | Remove both patch pathname prefixes |
| `--default-prefix` | — | — | All | Restore the standard patch pathname prefixes |
| `--line-prefix=` | `PREFIX` | = or separate | All | Prepend text to each line of diff output |
| `--max-depth=` | `DEPTH` | = or separate | Resolute and upstream | Limit how far the tree comparison descends |
| `--ancestry-path` | `COMMIT` | optional = | All | Keep commits related by ancestry to a range anchor |
| `--author-date-order` | — | — | All | Order by author date while keeping children first |
| `--bisect` | — | — | All | Use the current bisection refs to bound the walk |
| `--cherry` | — | — | All | Mark equivalent patches on the right side |
| `--cherry-mark` | — | — | All | Mark patch-equivalent commits on opposite sides |
| `--cherry-pick` | — | — | All | Omit patch-equivalent commits on opposite sides |
| `--children` | — | — | All | Show child commit IDs in commit headers |
| `--date-order` | — | — | All | Order by commit date while keeping children first |
| `--do-walk` | — | — | All | Resume walking ancestors of the specified commits |
| `--exclude-first-parent-only` | — | — | All | Follow only first parents when excluding ancestry |
| `--full-history` | — | — | All | Follow every parent during history simplification |
| `--graph` | — | — | All | Draw the history graph beside commits |
| `--graph-indent` | — | — | 2.56 only | Indent disconnected roots in the graph |
| `--graph-lane-limit=` | `COUNT` | = only | 2.56 only | Limit visible lanes in the history graph |
| `--left-only` | — | — | All | Select the left side of a symmetric difference |
| `--maximal-only` | — | — | 2.56 only | Keep commits unreachable from any other selected commit |
| `--merge` | — | — | All | Show history relevant to unresolved conflicts |
| `--no-decorate-refs` | — | — | All | Clear explicit decoration inclusion patterns |
| `--no-decorate-refs-exclude` | — | — | All | Clear explicit decoration exclusion patterns |
| `--no-graph-indent` | — | — | 2.56 only | Align disconnected roots with other graph entries |
| `--no-quiet` | — | — | All | Cancel quiet diff mode |
| `--no-source` | — | — | All | Turn off source-ref labels |
| `--no-walk` | `ORDER` | optional = | All | Show named commits without visiting ancestors |
| `--not` | — | — | All | Reverse inclusion for subsequent revisions |
| `--remove-empty` | — | — | All | Stop when a selected path disappears from history |
| `--reverse` | — | — | All | Reverse the selected commits' output order |
| `--right-only` | — | — | All | Select the right side of a symmetric difference |
| `--show-pulls` | — | — | All | Include merges that first introduced a change |
| `--simplify-by-decoration` | — | — | All | Simplify history around selected paths and decorations |
| `--simplify-merges` | — | — | All | Remove redundant merges from simplified history |
| `--source` | — | — | All | Show the starting ref through which a commit was reached |
| `--topo-order` | — | — | All | Keep branch histories together in topological order |
| `-L` | `RANGE:FILE` | attached or separate | All | Trace line history for a range or function |

## Release and mode differences

- Git 2.56 adds `--max-count-oldest`, `--maximal-only`, `--graph-lane-limit`, `--graph-indent` and `--no-graph-indent`. The layout controls require `--graph`. `--max-count-oldest=N` selects the last N commits of the walk before display. The tagged parser reads a separate count but returns a consumed-token count of one on that branch, leaving the number in the revision inputs. The row uses the attached spelling. [Upstream revision parser](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c)
- For `-L`, both Ubuntu manuals document the patch and its suppression. The upstream revision also supports raw, name-only, name-status and summary output. Diffstat-family output remains unavailable for line history. Each range must exist at the single starting revision. A path after `--` is incompatible with line history. [Noble](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) · [Resolute](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) · [Upstream](https://git-scm.com/docs/git-log/2.56.0)
- Resolute and upstream support `--max-depth=N` for tree comparisons. It measures descent from each selected path, rejects wildcards in pathspecs and accepts -1 for unlimited descent. Noble lacks this option. [Depth and path examples](https://git-scm.com/docs/git-diff/2.56.0)
- With unresolved index entries, Noble takes the second side of `git log --merge` from MERGE_HEAD. Newer Git tries MERGE_HEAD, CHERRY_PICK_HEAD, REVERT_HEAD and REBASE_HEAD in order. [Noble preparation](https://raw.githubusercontent.com/git/git/v2.43.0/revision.c) · [Resolute preparation](https://raw.githubusercontent.com/git/git/v2.53.0/revision.c)
- `--format=FORMAT` requires the equals form, while bare `--pretty` selects medium. `--decorate` requests short ref names even through a pipe. `--stat` uses diffstat defaults. Both accept optional attached parameters. A separate token can become a revision or path. The inherited Git 2.48.0 guidance for the original date, count and pattern options remains version-qualified. [Pretty options](https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/pretty-options.adoc) · [Log parser](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/log.c)
- `--grep` searches the stored commit message and enabled notes. `--grep-reflog` requires `-g` and searches the ref update message. In ordinary history date limits compare committer time. With `-g` they use the timestamp of the ref update. [Revision and timestamp selection](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c)
- With an ordinary merge, a requested patch or pickaxe filter normally has no merge diff to inspect. `--first-parent` changes traversal and selects the first-parent merge comparison by default. `--dd` selects that merge patch and leaves traversal of other parents available. [Merge diff implementation](https://raw.githubusercontent.com/git/git/v2.56.0/diff-merges.c)

## Exclusions

| Spelling or syntax | Owner and disposition |
| --- | --- |
| `--`, `^A`, `A..B`, `A...B`, `ref@{N}`, pathspecs | Revision and path operands. A standalone double dash ends revision and option parsing. A range can name multiple starts and exclusions. |
| `%H`, `%s`, `%gd`, `%gs`, `%(trailers:...)`, and other pretty-format placeholders | Format operand grammar. The format rows expose built-in layouts, placeholders and format versus tformat record boundaries. |
| `--ita-invisible-in-index`, `--ita-visible-in-index` | The shared diff text describes the working index's intent-to-add entries. Commit-to-commit comparisons have no working index operand. |
| `--cached`, `--staged`, `--no-index`, `--ours`, `--theirs`, `--base`, `--merge-base` | Select inputs for other diff commands. Log takes revisions and paths. |
| `--count`, `--objects`, `--objects-edge`, `--objects-edge-aggressive`, `--in-commit-order`, `--indexed-objects`, `--filter`, `--object-names`, `--missing`, `--disk-usage`, `--use-bitmap-index`, `--progress`, `--bisect-vars`, `--bisect-all`, `--timestamp`, `--header` | Plumbing enumeration, counting, bisection reporting or object output in git-rev-list. Shared parsing alone does not give git-log the corresponding output mode. The log form of `--bisect` selects the bisection range. |
| `-C` as a directory, `-c` as a configuration setting, `--git-dir`, `--work-tree`, pager selection | Git global options precede `log`. Within its menu `-C` means copy detection and `-c` means a combined merge patch. |
| `--i-still-use-this` and its negation | Hidden in extended usage on Resolute. The shared log parser sets a field consumed by git-whatchanged. It has no log effect. |
| `--commit-list-format`, `--unfold`, `--verify`, `--strategy`, `--combined`, `--git` and `--cc` as an output prefix | References to format-patch, trailer rendering, signature verification, merging or literal diff headers. The actual selectable log switch `--cc` chooses a dense combined diff. |

## Additional packaged observations

Private one-commit repositories in the host and Noble 3.12 sandboxes contained one tracked line. Both Git 2.53.0 and 2.43.0 returned 0 with empty stdout for `log -1 --format=` and `log -1 --format=format:`. Bare `log -1 --format` returned 128. The menu inserts `--format=` with the cursor at the required value. Use `format:` as the value for an explicitly empty layout when continuing to browse other options. Both clients returned 128 for `log -L1,1:tracked --raw` and `log -L1,1:tracked --name-only`, reporting support for patch or suppressed patch output. Extended built-in usage (`log --help-all`) went to stdout with status 129.

### Short-option bundles

Both Ubuntu packages accepted `-pu`, `-pR`, `-Rp`, and `-pGexample` in the same fixture. The menu recognizes bundles within the shared diff parser for `-p -s -u -W -z -D -l -w -b -I -a -R -S -G -O`. A member requiring a value consumes the rest of the token or the following word. [Diff option declarations](https://raw.githubusercontent.com/git/git/v2.53.0/diff.c)

Git passes some leftover short options from its log parser to its diff parser. Both packages accepted `-qp` and `-qL1,1:tracked`, but rejected `-pq`, `-pL1,1:tracked`, `-gp` and `-pg` with status 128. Both also accepted `-pU0`, whose last member has an optional attached value. The menu's existing bundle declarations accept unordered members with unambiguous arity. To continue browsing after a mixed-stage or optional-value bundle, use separate switches such as `-q -p`, `-q -L1,1:tracked` or `-p -U0`. Each component retains its own selectable row. [Log parser](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/log.c) · [Menu argument forms](profiles-and-drivers.md)

The [family verification report](git-commit-log-manual-coverage.md) records the independent packaged-client observations, terminal checks and full suite results.
