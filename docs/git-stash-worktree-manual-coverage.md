# Git stash and worktree manual coverage

The 11 bundled menus originally contained 85 selectable rows. This revisit covers implicit stash push, the five bundled stash subcommands, the worktree command selector and its four bundled subcommands. A keyword without a dedicated profile has usage guidance on its root row. Completing that keyword ends the parent menu's scope. Git global options precede the command path.

## Sources and inventories

| Manuals | Upstream | Ubuntu 24.04 Noble | Ubuntu 26.04 Resolute |
| --- | --- | --- | --- |
| Stash and worktree | [stash](https://git-scm.com/docs/git-stash/2.56.0) · [worktree](https://git-scm.com/docs/git-worktree/2.56.0) | [stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html) · [worktree](https://manpages.ubuntu.com/manpages/noble/man1/git-worktree.1.html) | [stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html) · [worktree](https://manpages.ubuntu.com/manpages/resolute/man1/git-worktree.1.html) |
| Delegated options | [log](https://git-scm.com/docs/git-log/2.56.0) · [diff](https://git-scm.com/docs/git-diff/2.56.0) · [revisions](https://git-scm.com/docs/gitrevisions) | [log](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) · [diff](https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html) | [log](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) · [diff](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff.1.html) |

The upstream manuals identify 2.56.0 as their last revision through 2.56.1. The Ubuntu git-man packages are 1:2.43.0-1ubuntu7.4 and 1:2.53.0-1ubuntu1.1. The independent inventories record spellings, operand forms, release differences, source decisions and exclusions.

- [Direct stash and worktree options and root keywords](git-stash-worktree-direct-inventory.md)
- [Log and diff options in a stash reflog walk](git-stash-list-inventory.md)
- [Diff options for a stash comparison](git-stash-show-inventory.md)

## Menu inventory

| Menu | Original rows | Added | Final | Distinct effects |
| --- | ---: | ---: | ---: | ---: |
| `git stash` | 17 | 20 | 37 | 29 |
| `git stash push` | 17 | 7 | 24 | 16 |
| `git stash apply` | 3 | 5 | 8 | 7 |
| `git stash pop` | 3 | 2 | 5 | 4 |
| `git stash list` | 9 | 192 | 201 | 174 |
| `git stash show` | 9 | 103 | 112 | 96 |
| `git worktree` | 5 | 4 | 9 | 9 |
| `git worktree add` | 11 | 9 | 20 | 17 |
| `git worktree list` | 4 | 3 | 7 | 6 |
| `git worktree prune` | 5 | 2 | 7 | 5 |
| `git worktree remove` | 2 | 1 | 3 | 2 |
| **Total** | **85** | **348** | **433** | **365** |

Counts are per command path. The 433 rows include 68 alternate selectable spellings. The direct menus also explain 30 reset spellings and 16 built-in help aliases in Details. On stash list, a dash followed by decimal digits is an additional count syntax, such as `-3`. The parser recognizes a complete shorthand token before the next option and keeps the cursor out of its value. The 85 original literal edits and the original Git 2.48.0 value contracts remain covered. [Argument syntax](profiles-and-drivers.md) · [Insertion and terminal checks](../tests/test_git_stash_worktree_menus.py)

## Packaged usage

Each package ran with the C locale, system and global Git configuration disabled, and a private, newly initialized repository in the offline sandbox. The captures preserve both streams, the argument vector and the exit status for each command. They include the subcommands that have no bundled profile. Each of the 11 menu paths printed its short usage to standard output and returned 129. On Noble, the export and import probes returned the root usage. On Resolute, both returned their own usage. On both releases, `stash create -h` took the message path and reported the missing initial commit on standard error. This fixed invocation cannot establish a create help action. [Noble fixed usage](../tests/fixtures/git-stash-worktree/noble-usage.json) · [Resolute fixed usage](../tests/fixtures/git-stash-worktree/resolute-usage.json)

The existing discovery specimens remain separate from those captures. In particular, short usage for `stash list` refers to log options without enumerating them. A parsed flag in the shared diff manual also requires an applicable mode before it belongs in a stash menu. [First-pass audit and fixture provenance](git-stash-worktree-option-audit.md)

## Material changes

- Under `stash list`, `-u` prints tracked changes as a patch. Under `stash show`, the same letter adds saved untracked files to the comparison. Uppercase `-U` requests a patch in both menus. In `stash push`, Git 2.53 requires a count with `-U`, and Git 2.43 rejects that option.
- `stash list --grep-reflog=PATTERN` searches the reflog subject displayed by default. `--grep=PATTERN` searches the stored commit message and can also match enabled notes. An empty stash bypasses the delegated option parser. The release checks used populated reflogs.
- `stash show --stat=30` sets the output width. With a space, `stash show --stat 30` requests stash 30. The menu retains the original bare insertion. Other diff operands on this path need to share the option token, since a separate word can become the stash selector.
- On Resolute, `worktree add --relative-paths` also enables the repository's relative-worktrees extension. That can affect older clients opening the repository. A subsequent `--no-relative-paths` writes absolute links for the new worktree and leaves the extension enabled. Noble rejects the switch.
- `worktree list --expire TIME` annotates eligible missing worktrees. `worktree prune --expire TIME` removes their administrative records. With porcelain output and `-z`, each attribute ends in NUL and an additional NUL separates worktrees.

The inventories separate manual and source findings from packaged observations. In particular, the upstream-only conflict labels are options for apply. Both Ubuntu packages rejected them. Upstream Git 2.56.1 was also built in a disposable sandbox to resolve the output of the new oldest-count limiter. [Direct observations](git-stash-worktree-direct-inventory.md#packaged-git-observations) · [Reflog observations](git-stash-list-inventory.md#executable-observations) · [Comparison observations](git-stash-show-inventory.md#packaged-observations)

## Verification

Bash/tmux sessions with discovery disabled and an execution-recording Git stub opened all 11 profiles on each target. At 240×150 the terminal regression traversed the 433 selectable rows and compared their highlighted labels, summaries and complete Details panes, including the formatted value guidance. At 60×16 the tests searched for the count, lock, expiry and depth qualifications, scrolled to the relevant text, and checked the exact restored or edited Readline buffer and cursor. Selecting `push` opened its child menu. The `--` boundary rejected a subsequent option edit. The recording stubs observed zero pending-command executions. [Terminal checks](../tests/test_git_stash_worktree_menus.py) · [Original count and lock regressions](../tests/test_expansion_terminal.py)

| Target | Ubuntu | Python | Git | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 2.53.0 | 77 / 0 / 0 | 1,437 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 2.43.0 | 77 / 0 / 0 | 1,437 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 2.43.0 | 77 / 0 / 0 | 1,437 / 0 / 1 |

The focused runs included the manual inventories, packaged Git fixtures, terminal tests, argument syntax, expansion and insertion regressions, documentation-link and repository-policy regressions, and the strict numerical gate. All 1,053 required contracts passed across the 76 bundled profiles. The review reconciled 511 changed inventory identities, including declarations, scoped count-parser changes and the Linux CI timeout. Existing discovery observations and their provenance were retained. [Numerical review](numerical-inventory/review.json)

The full offline commands ran `bash tests/run.sh` through the project sandbox, including each new document, fixture and test individually. The full snapshots used the existing OpenSSH package fixtures on all three targets and the rsync fixture on Noble. Only the Windows-specific probe skipped. The inventories and menu Details reconcile for all 11 command paths. [Sandbox guide](development.md#isolated-local-debugging) · [OpenSSH package fixtures](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)
