# Git stash list manual inventory

The nine original rows grew to 201. Each of the 201 literal spellings is selectable. The table groups 25 alternative spellings on the same line. Two further spellings have the same effect on this path. Lowercase `-u` is another patch alias, and the packaged `--help-all` prints the same synopsis as `-h`. This gives 174 groups of effects, counting presets such as `--oneline` and explicit resets separately. The additional `-NUMBER` syntax supplies a count directly and has no fixed insertion spelling.

## Sources and delegation

| Reference | Version | Evidence |
| --- | --- | --- |
| Upstream | Git manual 2.56.0, release executable 2.56.1 | [stash](https://git-scm.com/docs/git-stash/2.56.0), [log](https://git-scm.com/docs/git-log/2.56.0), [diff](https://git-scm.com/docs/git-diff/2.56.0), [revision grammar](https://git-scm.com/docs/gitrevisions/2.56.0), [revision traversal](https://git-scm.com/docs/git-rev-list/2.56.0) |
| Ubuntu 24.04 Noble | git-man 1:2.43.0-1ubuntu7.4 | [stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html), [log](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html) |
| Ubuntu 26.04 Resolute | git-man 1:2.53.0-1ubuntu1.1 | [stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html), [log](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff.1.html) |

With an existing stash ref, all three implementations construct the argument vector `log --format=%gd: %gs -g --first-parent <arguments> refs/stash --`. The format is one argument. An empty stash returns before Git parses the delegated options, so an empty-repository acceptance check cannot establish that an option works. The appended ref and separator also explain why supplying a filename directly fails. To limit diffs by pathname, `--stdin` accepts a line containing `--` followed by one path per line. [Noble dispatch](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/stash.c), [Resolute dispatch](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/stash.c), [upstream dispatch](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/stash.c)

The inventory covers options described by the delegated log manual, including its diff formats, documented variants within explanatory paragraphs, and applicable revision flags. Syntax such as `%gs`, a reflog selector, a date expression and a diff algorithm name belongs to its operand. Original rows retain their relative order and the Git 2.48.0 parameter contracts. [Historical audit](git-stash-worktree-option-audit.md), [diff comparison inventory](git-stash-show-inventory.md)

## Selectable inventory

Each literal in a cell has its own row in the menu. A trailing equals sign is part of an insertion. The attachment column describes the Git parser. Bare optional long forms also work. For `--stat` the menu inserts the bare option so following words retain their original place. All means Git 2.43.0, 2.53.0 and 2.56.0, subject to the configuration and mode qualifications in Details.

| Selectable spellings | Operand | Attachment | Applicable releases |
| --- | --- | --- | --- |
| `-h`, `--help` | — | — | All |
| `--help-all` | — | — | All |
| `--oneline` | — | — | All |
| `--format=` | `FORMAT` | = only | All |
| `--date=` | `FORMAT` | = or separate | All |
| `--pretty` | `FORMAT` | optional = | All |
| `--abbrev-commit` | — | — | All |
| `--no-abbrev-commit` | — | — | All |
| `--relative-date` | — | — | All |
| `--decorate` | `STYLE` | optional = | All |
| `--no-decorate` | — | — | All |
| `--decorate-refs=` | `PATTERN` | = or separate | All |
| `--decorate-refs-exclude=` | `PATTERN` | = or separate | All |
| `--clear-decorations` | — | — | All |
| `--mailmap`, `--use-mailmap` | — | — | All |
| `--no-mailmap`, `--no-use-mailmap` | — | — | All |
| `--encoding=` | `ENCODING` | = or separate | All |
| `--expand-tabs` | `COLUMNS` | optional = | All |
| `--no-expand-tabs` | — | — | All |
| `--notes` | `REF` | optional = | All |
| `--show-notes` | `REF` | optional = | All |
| `--no-notes` | — | — | All |
| `--show-notes-by-default` | — | — | All |
| `--standard-notes` | — | — | All |
| `--no-standard-notes` | — | — | All |
| `--show-signature` | — | — | All |
| `--log-size` | — | — | All |
| `--parents` | — | — | All |
| `--show-linear-break` | `TEXT` | optional = | All |
| `-n`, `--max-count=` | `COUNT` | short attached or separate, long = or separate | All |
| `--max-count-oldest=` | `COUNT` | = or separate | 2.56 only |
| `--skip=` | `COUNT` | = or separate | All |
| `--since=`, `--after=` | `DATE` | = or separate | All |
| `--since-as-filter=` | `DATE` | = or separate | All |
| `--until=`, `--before=` | `DATE` | = or separate | All |
| `--max-age=` | `TIMESTAMP` | = or separate | All |
| `--min-age=` | `TIMESTAMP` | = or separate | All |
| `--author=` | `PATTERN` | = or separate | All |
| `--committer=` | `PATTERN` | = or separate | All |
| `--grep-reflog=` | `PATTERN` | = or separate | All |
| `--grep=` | `PATTERN` | = or separate | All |
| `--all-match` | — | — | All |
| `--invert-grep` | — | — | All |
| `-i`, `--regexp-ignore-case` | — | — | All |
| `--basic-regexp` | — | — | All |
| `-E`, `--extended-regexp` | — | — | All |
| `-F`, `--fixed-strings` | — | — | All |
| `-P`, `--perl-regexp` | — | — | All |
| `--merges` | — | — | All |
| `--no-merges` | — | — | All |
| `--min-parents=` | `COUNT` | = only | All |
| `--max-parents=` | `COUNT` | = only | All |
| `--no-min-parents` | — | — | All |
| `--no-max-parents` | — | — | All |
| `--all` | — | — | All |
| `--branches` | `GLOB` | optional = | All |
| `--tags` | `GLOB` | optional = | All |
| `--remotes` | `GLOB` | optional = | All |
| `--glob=` | `GLOB` | = or separate | All |
| `--exclude=` | `GLOB` | = or separate | All |
| `--exclude-hidden=` | `MODE` | = or separate | All |
| `--reflog` | — | — | All |
| `--single-worktree` | — | — | All |
| `--alternate-refs` | — | — | All |
| `--ignore-missing` | — | — | All |
| `--stdin` | — | — | All |
| `--follow` | — | — | All |
| `--full-diff` | — | — | All |
| `--dense` | — | — | All |
| `--sparse` | — | — | All |
| `--first-parent` | — | — | All |
| `-g`, `--walk-reflogs` | — | — | All |
| `--boundary` | — | — | All |
| `--left-right` | — | — | All |
| `--diff-merges=` | `MODE` | = or separate | All |
| `--no-diff-merges` | — | — | All |
| `-m` | — | — | All |
| `-c` | — | — | All |
| `--cc` | — | — | All |
| `--dd` | — | — | All |
| `--remerge-diff` | — | — | All |
| `--combined-all-paths` | — | — | All |
| `-t` | — | — | All |
| `--unpacked` | — | — | All |
| `-p`, `--patch` | — | — | All |
| `--stat` | `WIDTH[,NAME-WIDTH[,COUNT]]` | optional = | All |
| `--name-only` | — | — | All |
| `--name-status` | — | — | All |
| `-u` | — | — | All |
| `--binary` | — | — | All |
| `-s`, `--no-patch` | — | — | All |
| `-U`, `--unified` | `LINES` | short attached, long = | All |
| `--output=` | `FILE` | = or separate | All |
| `--output-indicator-new=` | `CHAR` | = or separate | All |
| `--output-indicator-old=` | `CHAR` | = or separate | All |
| `--output-indicator-context=` | `CHAR` | = or separate | All |
| `--raw` | — | — | All |
| `--patch-with-raw` | — | — | All |
| `--indent-heuristic` | — | — | All |
| `--no-indent-heuristic` | — | — | All |
| `--minimal` | — | — | All |
| `--patience` | — | — | All |
| `--histogram` | — | — | All |
| `--anchored=` | `TEXT` | = or separate | All |
| `--diff-algorithm=` | `ALGORITHM` | = or separate | All |
| `--stat-width=` | `WIDTH` | = or separate | All |
| `--stat-name-width=` | `WIDTH` | = or separate | All |
| `--stat-graph-width=` | `WIDTH` | = or separate | All |
| `--stat-count=` | `COUNT` | = or separate | All |
| `--compact-summary` | — | — | All |
| `--numstat` | — | — | All |
| `--shortstat` | — | — | All |
| `-X`, `--dirstat` | `PARAMETERS` | short attached, long = | All |
| `--cumulative` | — | — | All |
| `--dirstat-by-file` | `PARAMETERS` | optional = | All |
| `--summary` | — | — | All |
| `--patch-with-stat` | — | — | All |
| `-z` | — | — | All |
| `--submodule` | `FORMAT` | optional = | All |
| `--color` | `WHEN` | optional = | All |
| `--no-color` | — | — | All |
| `--color-moved` | `MODE` | optional = | All |
| `--no-color-moved` | — | — | All |
| `--color-moved-ws=` | `MODES` | = or separate | All |
| `--no-color-moved-ws` | — | — | All |
| `--word-diff` | `MODE` | optional = | All |
| `--word-diff-regex=` | `REGEX` | = or separate | All |
| `--color-words` | `REGEX` | optional = | All |
| `--no-renames` | — | — | All |
| `--rename-empty` | — | — | All |
| `--no-rename-empty` | — | — | All |
| `--check` | — | — | All |
| `--ws-error-highlight=` | `KINDS` | = or separate | All |
| `--full-index` | — | — | All |
| `--abbrev` | `DIGITS` | optional = | All |
| `--no-abbrev` | — | — | All |
| `-B`, `--break-rewrites` | `N[/M]` | short attached, long = | All |
| `-M`, `--find-renames` | `SCORE` | short attached, long = | All |
| `-C`, `--find-copies` | `SCORE` | short attached, long = | All |
| `--find-copies-harder` | — | — | All |
| `-D`, `--irreversible-delete` | — | — | All |
| `-l` | `LIMIT` | attached or separate | All |
| `--diff-filter=` | `STATUS` | = or separate | All |
| `-S` | `TEXT` | attached or separate | All |
| `-G` | `REGEX` | attached or separate | All |
| `--find-object=` | `OBJECT` | = or separate | All |
| `--pickaxe-all` | — | — | All |
| `--pickaxe-regex` | — | — | All |
| `-O` | `ORDERFILE` | attached or separate | All |
| `--skip-to=` | `PATH` | = or separate | All |
| `--rotate-to=` | `PATH` | = or separate | All |
| `-R` | — | — | All |
| `--relative` | `PATH` | optional = | All |
| `--no-relative` | — | — | All |
| `-a`, `--text` | — | — | All |
| `--ignore-cr-at-eol` | — | — | All |
| `--ignore-space-at-eol` | — | — | All |
| `-b`, `--ignore-space-change` | — | — | All |
| `-w`, `--ignore-all-space` | — | — | All |
| `--ignore-blank-lines` | — | — | All |
| `-I`, `--ignore-matching-lines=` | `REGEX` | short attached or separate, long = or separate | All |
| `--inter-hunk-context=` | `LINES` | = or separate | All |
| `-W`, `--function-context` | — | — | All |
| `--exit-code` | — | — | All |
| `-q`, `--quiet` | — | — | All |
| `--ext-diff` | — | — | All |
| `--no-ext-diff` | — | — | All |
| `--textconv` | — | — | All |
| `--no-textconv` | — | — | All |
| `--ignore-submodules` | `WHEN` | optional = | All |
| `--src-prefix=` | `PREFIX` | = or separate | All |
| `--dst-prefix=` | `PREFIX` | = or separate | All |
| `--no-prefix` | — | — | All |
| `--default-prefix` | — | — | All |
| `--line-prefix=` | `PREFIX` | = or separate | All |
| `--max-depth=` | `DEPTH` | = or separate | Resolute and upstream |

## Exclusions and release differences

| Manual spelling or family | Disposition for this command path |
| --- | --- |
| `--reverse`, `--graph`, `--topo-order`, `--date-order`, `--author-date-order`, `--children`, `--ancestry-path[=COMMIT]`, `--simplify-by-decoration`, `--simplify-merges`, both `-L` range forms | The required graph, line or history-limiting traversal is incompatible with the reflog walker. |
| `--graph-lane-limit=N`, `--graph-indent`, `--no-graph-indent` | Upstream graph layout requires the incompatible graph mode. Both Ubuntu clients lack these new options. |
| `--cherry`, `--cherry-pick`, `--cherry-mark`, `--left-only`, `--right-only`, `--not`, `--exclude-first-parent-only`, `--merge`, `--bisect` | These operate on excluded commits or a two-sided range. A reflog walk cannot traverse a negative revision. Resolute rejects the left/right filters directly. Noble accepts them but leaves the ordinary stash list intact. With no bisection refs, `--bisect` changes nothing. |
| `--no-walk[=sorted/unsorted]`, `--do-walk`, `--full-history`, `--show-pulls`, `--remove-empty` | The next entry comes from the reflog, independently of parent traversal, so these options cannot stop at a path's creation, visit additional parents or change the order of stashes. The fixed first-parent comparison bypasses later parents when simplifying a path. Path-dependent dense/sparse selection does have an effect. |
| `--maximal-only` | Both Ubuntu clients reject it. Upstream accepted it and still listed a branch base as well as its descendants. Its child-visited pruning belongs to ordinary ancestry traversal. |
| `--source` | Accepted on the three releases. The walk does not populate the source decoration used for normal traversal. A custom `%S` printed literally, even with `--source --branches`. Use `%gD` or `%gd` for the ref and reflog selector. |
| `--ita-invisible-in-index`, `--ita-visible-in-index` | A saved-commit comparison does not consult the working index's intent-to-add entries. |
| `--cached`, `--staged`, `--no-index`, `--merge-base`, `--ours`, `--theirs`, `--base` and standalone diff revision/path forms | These select different comparison inputs for other commands. List compares the stash commits selected by the reflog walk. |
| Object enumeration and plumbing output | `--objects`, `--objects-edge`, `--objects-edge-aggressive`, `--in-commit-order`, `--indexed-objects` and object filtering cannot turn log into a tree/blob enumeration. `--count` leaves stash entries visible. The rev-list-only bitmap, progress, disk-usage, missing-object, object-name, bisection-output, timestamp and header switches belong to the plumbing command. `--unpacked` does apply because it filters the selected commit object itself. |
| Stash push/show controls | `--include-untracked`, `--only-untracked`, `--staged`, `--keep-index` and `--pathspec-from-file` belong to sibling commands. On list, `-u` generates a patch. On show, it requests the saved untracked tree. |

The revision parser identifies incompatible walk modes and selects the next reflog entry. Log has its own options and status handling, including `-q`, while diff options act on comparisons supplied by log. [Git 2.43 revision parser](https://raw.githubusercontent.com/git/git/v2.43.0/revision.c), [Git 2.53 revision parser](https://raw.githubusercontent.com/git/git/v2.53.0/revision.c), [Git 2.56 revision parser](https://raw.githubusercontent.com/git/git/v2.56.0/revision.c), [log implementation](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/log.c), [merge diff modes](https://raw.githubusercontent.com/git/git/v2.56.0/diff-merges.c), [diff implementation](https://raw.githubusercontent.com/git/git/v2.56.0/diff.c)

## Executable observations

Private repositories in the offline sandbox supplied multiple named stashes, changed tracked paths, a stash with an extra untracked parent, a branch reflog and a commit note. The following outcomes were observed on Git 2.43.0 and 2.53.0.

| Check | Result |
| --- | --- |
| `--skip=1 --max-count=1`, negative skip, `-n -1` | One entry at index 1, no skip, and no count cap, respectively. The count is applied after the skip. |
| `--stdin` given a separator and one changed path | The path restricted both the default list and `--name-only`. Adding `--full-diff` reported both changed filenames for the matching stash. Adding `--sparse` restored the entries whose selected path was unchanged. An ordinary filename supplied on the command line exited 1 as a bad revision. |
| `--notes --format=%N`, `--notes --grep=only` | The first printed the note body. The second matched text present only in the note. The default selector-and-subject format contained no note text. |
| `--all`, `--branches`, `--boundary --oneline` | Adding refs also printed branch or HEAD reflogs. Explicit refs/stash remained in the input, so the same stash could appear twice. Boundary output included additional parent commits marked with a minus. Reflog placeholders on boundary lines could repeat the last selector. |
| `-u`, bare `-U`, `-U0`, `-U 0`, `--stat=20,10,1`, `--stat 20` | The first three generated patches. The space-separated 0 was a bad revision. Attached diffstat parameters produced a diffstat, while the separate 20 was a bad revision. |
| `--quiet`, `--quiet -p`, `--exit-code` | Quiet alone left reflog lines visible and returned 0. An explicit patch still appeared with quiet. With changed stashes, exit-code returned 1. |
| `--remerge-diff`, `--combined-all-paths` | Git skipped the three-parent stash with an octopus merge warning. Both clients rejected the combined path switch without a combined diff mode. |
| `--max-depth=0 --name-only` and `--max-count-oldest=1` | Resolute accepted the depth option and Noble rejected it. Both rejected the oldest-count option. |

A checksum-verified Git 2.56.1 source release built in the private host sandbox supplied an additional comparison. Given four named stashes, `--max-count-oldest=2 --format=%gs/%s` returned the two oldest commit subjects in the normal listing order, but printed the oldest **reflog subject** for both. The default layout repeated the oldest selector and reflog message. Use commit fields such as `%H` and `%s` to identify those objects. The older Ubuntu versions have no oldest-count selector. The tarball SHA-256 was `f0b0bf89264b9bd2e1c640363e7529643989da76281600473c50745cd34a607f`. [Release checksum list](https://www.kernel.org/pub/software/scm/git/sha256sums.asc), [oldest-count queue](https://raw.githubusercontent.com/git/git/v2.56.1/revision.c)

The [family report](git-stash-worktree-manual-coverage.md) records rendered-menu and full-suite results separately from these Git executable checks.
