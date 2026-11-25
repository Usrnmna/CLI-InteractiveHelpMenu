# Git stash and worktree option audit

First recorded 2026-11-22. This first pass covered 85 bundled rows. See the [expanded inventory and verification](git-stash-worktree-manual-coverage.md) for the later manual comparison.

## Reference manuals

| Source | Version reviewed | Manuals |
| --- | --- | --- |
| Git upstream | The stash, worktree, log and diff manuals identify 2.56.0 as their latest revision, with no changes for 2.56.1. | [stash](https://git-scm.com/docs/git-stash/2.56.0), [worktree](https://git-scm.com/docs/git-worktree/2.56.0), [log](https://git-scm.com/docs/git-log/2.56.0), [diff](https://git-scm.com/docs/git-diff/2.56.0) |
| Ubuntu 24.04 LTS | git 1:2.43.0-1ubuntu7.4 | [stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html), [worktree](https://manpages.ubuntu.com/manpages/noble/man1/git-worktree.1.html), [log](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html) |
| Ubuntu 26.04 LTS | git 1:2.53.0-1ubuntu1.1 | [stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html), [worktree](https://manpages.ubuntu.com/manpages/resolute/man1/git-worktree.1.html), [log](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff.1.html) |
| Existing structured guidance | Git 2.48.0 | [stash implementation](https://github.com/git/git/blob/v2.48.0/builtin/stash.c), [revision counts](https://github.com/git/git/blob/v2.48.0/revision.c), [worktree prune](https://github.com/git/git/blob/v2.48.0/builtin/worktree.c), [pruning eligibility](https://github.com/git/git/blob/v2.48.0/worktree.c), [expiry date parsing](https://github.com/git/git/blob/v2.48.0/date.c) |

## Stash findings and dispositions

The 58 rows represented six stash paths, including implicit and explicit push. Apply retains the entry, pop drops it after success and a conflict can leave it available. List and show required separate inherited log and diff inventories.

## Worktree findings and dispositions

The 27 worktree entries included four subcommand keywords, add, list, prune and remove. The audit qualified force on a locked worktree, expiration during pruning and what a porcelain listing reports.

## Coverage boundaries and version differences

The baseline covered only the named operations. Stash had other subcommands, including export/import in newer editions. The later inventory reconciles direct rows and borrowed log/diff options separately.

## Disposable Git fixtures

The following observations come from real Git **2.43.0** on Ubuntu 24.04 and **2.53.0** on Ubuntu 26.04. Each executable ran against a temporary repository in the offline sandbox.

| Fixture | Observed on both Git versions |
| --- | --- |
| Two named stashes | `--oneline` added abbreviated IDs. Patches and stats reflected changes from the base. `--date=short` produced date-based selectors. Zero returned no entries. Both `-n -1` and `--max-count=-2` returned both entries. |
| Reflog message distinct from commit message | Only `--grep-reflog` matched a marker written exclusively into the reflog. |
| Staged, unstaged, untracked and ignored files | Ordinary `--keep-index -u` left the staged change ready to commit, removed the untracked file and retained the ignored file. `--all` also removed the ignored file. `--only-untracked --name-only` showed the saved untracked name. A separate `--staged` save left an independent unstaged edit in place. |
| Apply, clean pop and conflicting pop | `apply --index` restored staging and kept the entry. Successful `pop --index` dropped it. A competing edit produced a conflicted index and left the original stash object referenced after pop failed. |
| NUL-delimited pathspecs on stdin | A wildcard selected two matching files. An embedded newline remained part of a third filename. An unrelated file stayed outside the stash. |
| Locked and missing worktrees | Verbose list showed the lock reason. `--porcelain -z` emitted NUL-terminated attributes and an empty terminator. Bare `-z` failed. One force could not remove the locked worktree. Two succeeded. A dry-run prune reported the missing worktree without removing its registration. Direct prune removed it, and an earlier preview with `--expire never` had excluded it. |

## Rendered-menu verification

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,332 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,332 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,332 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
