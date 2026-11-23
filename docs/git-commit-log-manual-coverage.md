# Git commit and log manual coverage

The [first-pass audit](git-commit-log-option-audit.md) reviewed nine commit rows and ten log rows. The expanded inventories cover each command’s options, aliases, operand forms and release differences.

## Manual inventory

- [Commit inventory](git-commit-manual-inventory.md) covers content selection, authorship, messages, signatures, hooks and status previews.
- [Log inventory](git-log-manual-inventory.md) covers revision selection, history traversal, presentation, line history, and diff formatting and filtering.

| Reference | Commit | Log |
| --- | --- | --- |
| Versioned upstream manuals | [Git 2.55.0](https://git-scm.com/docs/git-commit/2.55.0) | [Git 2.56.0](https://git-scm.com/docs/git-log/2.56.0) |
| Ubuntu 24.04, git-man 1:2.43.0-1ubuntu7.4 | [Noble git-commit(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-commit.1.html) | [Noble git-log(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) |
| Ubuntu 26.04, git-man 1:2.53.0-1ubuntu1.1 | [Resolute git-commit(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-commit.1.html) | [Resolute git-log(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) |

| Menu | Original rows | Added rows | Final rows | Distinct effects | Alternate selectable spellings |
| --- | ---: | ---: | ---: | ---: | ---: |
| `git commit` | 9 | 89 | 98 | 78 | 20 |
| `git log` | 10 | 224 | 234 | 209 | 25 |

Effects are counted per command. The log count shorthand accepts a variable decimal number, so it has no additional fixed row. Both original insertion sequences and the original Git 2.48.0 value guides remain available.

Git’s global options precede the command name. For log, revision expressions select starting points and exclusions. Paths after `--` restrict history, and placeholders such as `%s` belong inside a format argument. The [stash list](git-stash-list-inventory.md) and [stash show](git-stash-show-inventory.md) inventories cover different command paths with different traversal and operand rules.

## Packaged Git results

Both Ubuntu clients ran against private temporary repositories in the offline sandboxes, with isolated configuration, local fixture identities and no remotes. The fixed `-h` requests returned 129. Noble wrote commit usage to stderr. Resolute wrote it to stdout. Both versions wrote log usage to stdout and listed only a subset of the accepted options. Upstream Git 2.56.1 returned 0 for both built-in help forms, `-h` and `--help-all`. The original discovery specimens and bounded Git 2.43.0 man excerpts retain their provenance. [Noble fixed usage](../tests/fixtures/git-commit-log/noble-usage.json) · [Resolute fixed usage](../tests/fixtures/git-commit-log/resolute-usage.json) · [Discovery fixture sources](../tests/fixtures/help/README.md)

| Invocation or fixture | Observed result |
| --- | --- |
| Commit with a staged change and a separate modified path | With no paths, the ordinary commit recorded the staged blob. With `-- chosen` or `--only -- chosen`, it recorded the working-tree copy of the named file and left the unrelated change staged. With `--include -- chosen` or an accepted hunk under `--patch -- chosen`, it recorded both. Each commit exited 0. |
| `commit --all`, `--only --amend`, and pathspec files | The all-tracked commit recorded a tracked deletion and excluded the new untracked file. A message-only amendment with `--only` preserved the prior tree and the pending index change. A NUL-delimited pathspec on stdin selected a filename containing a newline. All three succeeded. |
| A missing path with `commit --include` and unrelated staging | Noble committed the staged change despite the unmatched path. Resolute returned 128, retained the previous HEAD and kept the change staged. The two `--include` spellings document this difference. [Commit coverage and ownership](git-commit-manual-inventory.md#coverage-and-ownership) |
| Status and hooks | With staged changes, `commit -z` and `commit --porcelain` each returned 0 and preserved HEAD. `--porcelain=v2` returned 129. With a rejecting pre-commit hook, a later `--verify` restored the veto after `-n`. Reversing the flags bypassed that hook. |
| Commit patch context | Noble rejected the context options with status 129. Resolute required an integer after `-U`. An explicit nonnegative context required patch or interactive selection. The sentinel `-1` restored the default. A value of `-2` returned 128. |
| Count and date limits on three commits | `log -2` printed the two newest commits. `log --max-count=-2` printed all three. From a 2011 tip through a 2000 parent to a 2010 ancestor, `--since=2005-01-01T00:00:00Z` found the tip and `--since-as-filter=2005-01-01T00:00:00Z` also found the ancestor. All returned 0. |
| Log operand boundaries | `log -- -2` treated the token as a path. Attached decoration and stat operands succeeded. With no matching revisions or filenames, `--decorate full` and `--stat 20` each returned 128. |
| Message correction | With a staged change, `--fixup=reword:COMMIT` created an `amend!` message and kept the change staged. A plain `--fixup=COMMIT` then committed the change under a `fixup!` subject. |
| Pickaxe and line history | Rewriting a line while retaining one occurrence of `needle` appeared with `-Gneedle` and disappeared with `-Sneedle`. A one-line history with `-L1,1:tracked HEAD` succeeded. Adding `-- tracked` to that line-history command returned 128. |
| Reflog restrictions | Ordinary log reversed a two-commit range. The reflog walker rejected both `-g --reverse` and `-g HEAD~2..HEAD` with status 128. |
| Merge traversal and diff selection | `log --first-parent` followed the mainline. At the merge, `log -1 -p` showed the header alone. Adding `--diff-merges=first-parent` showed the change introduced from the topic branch. |

The [packaged Git regressions](../tests/test_git_commit_log_packaged.py) check output, status, committed blobs and index contents. The terminal tests below use a separate recording stub.

## Hosted failure reproduced locally

The three Linux jobs on the preceding stash/worktree revision used Git 2.56.1. Their stash output test expected the Ubuntu packages’ status 1 for an invalid selector. A checksum-verified upstream 2.56.1 source build in the offline host sandbox reproduced the hosted status 128 and the invalid-reference diagnostic. The revised regression checks the failed lookup, the untouched destination and the successful attached output form. The Python 3.10 job also captured a partially drawn Details pane. The terminal regression now waits for all the expected text before inspecting the selected row. The hosted documentation job succeeded. [Hosted run](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/45280846559) · [Stash output regression](git-stash-show-inventory.md#output-operand-regression)

## Verification

At 240×150 the real Bash/tmux regression opens each menu with discovery disabled. It traverses the selectable rows and compares each highlighted label, summary, complete Details pane and formatted value guide with the loaded profile. At 60×16 it searches for “short status format”, “committer timestamp”, “pathspec input file” and “line history”. Each search reaches its qualification, restores the original buffer and cursor on Escape, and inserts the selected spelling before the existing suffix on Enter. Separate cases check bare `--decorate` and `--stat`, attached values, numeric shorthand and the boundary after `--`. A recording Git stub detects pending-command execution. [Terminal and insertion regressions](../tests/test_git_stash_worktree_menus.py) · [Minimum-size status and date regression](../tests/test_expansion_terminal.py)

The editor supports the documented option spellings on these paths. Some additional combinations accepted by Git need separate switches when browsing, including `git commit -a -uall` and `git log -q -p`. For empty log headers, `--format=format:` supplies an explicit format and lets editing continue. The inventories identify these editing limits alongside the corresponding Git spellings.


| Target | Ubuntu | Python | Git | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 2.53.0 | 79 / 0 / 1 | 1,461 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 2.43.0 | 79 / 0 / 1 | 1,461 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 2.43.0 | 79 / 0 / 1 | 1,461 / 0 / 1 |

The recording stub observed zero executions. The focused runs included the inventory and packaged behavior regressions, original literal edits, argument syntax, functional matrix and terminal checks. The strict numerical gate passed all 1,170 required contracts. Reconciliation checked 362 changed identities against the two profiles and retained source observations outside them. [Commit regressions](../tests/test_git_commit_inventory.py) · [Log regressions](../tests/test_git_log_manual_inventory.py) · [Numerical review](numerical-inventory/review.json)

A separate Git 2.56.1 source build on the host sandbox ran the stash-show and commit/log packaged regressions. Eleven passed, zero failed and three skipped because they require one of the two Ubuntu release captures. The failing hosted stash assertion was among the eleven that passed. The archive SHA-256 matched the [previously verified upstream source](git-stash-list-inventory.md#executable-observations).

Each full run invoked `bash tests/run.sh` through the offline project sandbox. Each new document, regression and capture was included individually. All three targets exercised the OpenSSH package fixture and both Noble targets used the separate rsync fixture. Each suite’s single skip was the Windows-specific probe. The manual option inventory and menu Details checks are complete for both commands. [Sandbox guide](development.md#isolated-local-debugging) · [OpenSSH fixtures](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)
