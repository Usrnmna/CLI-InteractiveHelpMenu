# Git stash and worktree option audit

The bundled menus contain 58 stash entries across six profiles and 27 worktree entries across five profiles. The count includes selectable aliases, implicit and explicit stash push, and the four worktree keywords. The scope is the bundled menus with discovery disabled.

## Reference manuals

| Source | Version reviewed | Manuals |
| --- | --- | --- |
| Git upstream | The stash, worktree, log and diff manuals identify 2.56.0 as their latest revision, with no changes for 2.56.1. | [stash](https://git-scm.com/docs/git-stash/2.56.0), [worktree](https://git-scm.com/docs/git-worktree/2.56.0), [log](https://git-scm.com/docs/git-log/2.56.0), [diff](https://git-scm.com/docs/git-diff/2.56.0) |
| Ubuntu 24.04 LTS | git 1:2.43.0-1ubuntu7.4 | [stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html), [worktree](https://manpages.ubuntu.com/manpages/noble/man1/git-worktree.1.html), [log](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/noble/man1/git-diff.1.html) |
| Ubuntu 26.04 LTS | git 1:2.53.0-1ubuntu1.1 | [stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html), [worktree](https://manpages.ubuntu.com/manpages/resolute/man1/git-worktree.1.html), [log](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html), [diff](https://manpages.ubuntu.com/manpages/resolute/man1/git-diff.1.html) |
| Existing structured guidance | Git 2.48.0 | [stash implementation](https://github.com/git/git/blob/v2.48.0/builtin/stash.c), [revision counts](https://github.com/git/git/blob/v2.48.0/revision.c), [worktree prune](https://github.com/git/git/blob/v2.48.0/builtin/worktree.c), [pruning eligibility](https://github.com/git/git/blob/v2.48.0/worktree.c), [expiry date parsing](https://github.com/git/git/blob/v2.48.0/date.c) |

## Stash findings and dispositions

Dispositions describe the previous menu wording. Aliases in the same row have the same disposition. Each row in the first table applies to both [git stash](../profiles/git-stash.json) and [git stash push](../profiles/git-stash-push.json), accounting for 17 entries in each menu. The root menu describes implicit push and places pathspec operands after `--`.

| Original entries | Disposition | What the menu now explains |
| --- | --- | --- |
| `-p`, `--patch` | Incomplete | Choose individual hunks from the difference between HEAD and the working tree. Patch mode implies keep-index and takes precedence over staged-only selection. |
| `-S`, `--staged` | Incomplete | Save only staged changes. Independent unstaged changes remain. Overlapping edits can prevent rollback, and the option is incompatible with `-u` and `-a`. |
| `-k`, `--keep-index` | Incomplete | The stash still records the index. With ordinary push, staged changes also stay in the index and working tree, ready to commit. |
| `--no-keep-index` | Inaccurate | “Revert staged changes” omitted the save and could suggest discarding them. This rolls staged changes back **after** recording the index and can override patch mode's default. |
| `-u`, `--include-untracked` | Incomplete | Save and remove untracked files from the working tree. Ignored files stay. |
| `-a`, `--all` | Incomplete | Save and remove both untracked and ignored files, alongside the tracked changes. |
| `-m`, `--message` | Sufficient | Retain the stash description and separate MESSAGE operand. Quoting keeps a multiword message together. |
| `-q`, `--quiet` | Incomplete | Suppress normal stash feedback, including the result message. |
| `--pathspec-from-file` | Incomplete | FILE can be a path or `-` for stdin. Explain newline and NUL separation and the restrictions on mixing input modes, patch and staged selection. |
| `--pathspec-file-nul` | Incomplete | Requires the file-input option. Newlines and quotes are preserved within a NUL-delimited element. Wildcard pathspec matching still applies. |

[git stash apply](../profiles/git-stash-apply.json) and [git stash pop](../profiles/git-stash-pop.json) share three rows each. The headers distinguish what happens to the saved entry: apply keeps it, and pop drops it only after success. A conflicting pop leaves the entry available.

| Original entries on both paths | Disposition | What the menu now explains |
| --- | --- | --- |
| `--index` | Incomplete | Git tries to reinstate the original staging state as well as the working-tree edits. Conflicts can prevent index restoration. |
| `-q`, `--quiet` | Incomplete | Suppress normal command feedback. |

[git stash list](../profiles/git-stash-list.json) uses the stash reflog and accepts log options. [git stash show](../profiles/git-stash-show.json) compares one saved working tree to its original base and accepts diff options. Each menu contains nine entries.

| Path | Original entries | Disposition | Finding |
| --- | --- | --- | --- |
| list | `--oneline` | Incomplete | The default stash listing is already one line per entry. The compact format adds an abbreviated object ID. |
| list | `--stat` | Incomplete | Show a per-file summary for each listed stash against its first parent. |
| list | `-p`, `--patch` | Incomplete | Show each listed stash's tracked changes relative to its first parent. |
| list | `-n`, `--max-count=` | Inaccurate | Zero returns no entries. Positive counts cap the matches. The old value definition incorrectly excluded signed negative counts, which leave the list uncapped. |
| list | `--format=` | Incomplete | A named pretty format or placeholders control the output. `%gd` is the reflog selector and `%gs` its subject. |
| list | `--date=` | Incomplete | In the default format an explicit date mode replaces the numeric stash index in the reflog selector with a date. |
| list | `--grep=` | Incomplete | Match the stash **commit** message. The message displayed by the default listing belongs to the reflog and can differ. Use `--grep-reflog` for that text. |
| show | `-p`, `--patch` | Incomplete | Compare the selected stash with its original base. Omitting the stash selects the latest. |
| show | `--stat` | Incomplete | Show a diffstat. The default show format can be changed by `stash.showStat` and `stash.showPatch`. |
| show | `--name-only` | Sufficient | Retain the list of changed paths. |
| show | `--name-status` | Sufficient | Keep the existing meaning and explain common status letters. |
| show | `-u`, `--include-untracked` | Incomplete | Include files previously saved with `-u` or `-a`. The `stash.showIncludeUntracked` setting can enable this by default. |
| show | `--only-untracked` | Sufficient | Clarify that the displayed files come from the stash. |
| show | `--binary` | Incomplete | Implies patch output, including binary changes in a form suitable for `git apply`. |

## Worktree findings and dispositions

The [worktree root](../profiles/git-worktree.json) contains a help flag and four selectable command keywords. The leaf menus cover [add](../profiles/git-worktree-add.json), [list](../profiles/git-worktree-list.json), [prune](../profiles/git-worktree-prune.json) and [remove](../profiles/git-worktree-remove.json).

| Path | Original entries | Disposition | Finding |
| --- | --- | --- | --- |
| root | `-h` | Sufficient | Retain command usage. |
| root | `add` | Incomplete | Supply a path and optionally a branch or commit. The linked worktree has its own HEAD and index. |
| root | `list` | Incomplete | Show the main worktree first, followed by linked worktrees and their branch or detached state. |
| root | `remove` | Incomplete | Delete the linked directory and its registration. The main worktree cannot be removed. |
| root | `prune` | Incomplete | Clean stale administration when a directory is gone. A directory moved manually may be reconnected with repair. |
| add | `-f`, `--force` | Incomplete | Override the checks for a branch checked out elsewhere or a missing but registered path. Reusing a missing locked path requires force twice. |
| add | `--detach` | Incomplete | Check out the specified commit, or HEAD, without attaching the new worktree to a branch. |
| add | `-b` | Incomplete | Create and check out a new branch at the supplied start point, defaulting to HEAD. An existing name is refused. |
| add | `-B` | Incomplete | An existing branch is reset to the specified start point, defaulting to HEAD. |
| add | `--checkout` | Sufficient | Populate the new worktree. Clarify that this is the default. |
| add | `--no-checkout` | Sufficient | Skip populating files, allowing initial setup such as sparse checkout. |
| add | `--lock` | Incomplete | Lock at creation and protect the registration from pruning while the directory is unavailable. |
| add | `--reason` | Incomplete | A lock reason requires `--lock` on add. |
| add | `-q`, `--quiet` | Incomplete | Suppress normal creation feedback. |
| list | `--porcelain` | Incomplete | Stable attributes appear on separate lines. Blank lines separate worktrees. Use `-z` to preserve embedded newlines. |
| list | `-z` | Inaccurate | The old “terminate records” wording missed the boundary inside each worktree. With the required `--porcelain`, **each attribute** ends in NUL and an extra NUL separates worktrees. |
| list | `-v`, `--verbose` | Incomplete | Show available lock and prune reasons in the human-readable listing. Porcelain is a separate mode. |
| prune | `-n`, `--dry-run` | Sufficient | Preview eligible administrative records and leave them in place. |
| prune | `-v`, `--verbose` | Sufficient | Report each registration removed. |
| prune | `--expire` | Redundant | Replace duplicated date-parser text in editorial Details with the cutoff's practical effect, quoting and lock protection. The precise version-scoped date grammar remains accessible. |
| remove | `-f`, `--force` | Inaccurate | A single force permits removal of a dirty or submodule-containing linked worktree. A locked worktree requires force twice. Removal can delete uncommitted files. |

## Coverage boundaries and version differences

- **Stash subcommands.** The stash root represents implicit push. The dedicated menus cover push, apply, pop, list and show. Branch, clear, drop, create, store and the deprecated save form are outside the selection. Resolute and current upstream also document export/import and export's `--print` and `--to-ref`. Noble does not list them. The `--` separator, pathspec operands and stash references such as `stash@{1}` are syntax the user types. [Noble stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html), [Resolute stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html) and [upstream stash](https://git-scm.com/docs/git-stash/2.56.0)
- **Stash options.** The untracked negation `--no-include-untracked` has no row. Resolute and current upstream document patch context controls `-U<n>`, `--unified=<n>` and `--inter-hunk-context=<n>`, and the `stash.index` configuration default for apply/pop. The current upstream apply synopsis also has `--label-ours`, `--label-theirs` and `--label-base` for conflict-marker labels. The root and explicit push profiles keep the same 17 spellings. [Upstream stash options](https://git-scm.com/docs/git-stash/2.56.0#_options) and [Resolute stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html)
- **Inherited log and diff controls.** List selects the nine log spellings above from the options applicable to a reflog walk. Further controls include `--skip`, `--since`, `--until`, `--grep-reflog`, regex modes and pretty placeholders. Show selects nine spellings from stash and diff. Further choices include `--numstat`, `--shortstat`, `--raw`, context controls, rename detection and diff algorithms. Both menus insert bare `--stat`. Git also accepts attached diffstat width, filename-width and count parameters. Delegated options retain the applicability rules of their owning manual. [Git log](https://git-scm.com/docs/git-log/2.56.0) and [Git diff](https://git-scm.com/docs/git-diff/2.56.0)
- **Worktrees.** Lock, unlock, move and repair are manual-only subcommands. Add's short detach alias `-d`, `--orphan`, tracking and remote-guessing switches are outside its menu. Relative-path controls appear in Resolute and current upstream. List's `--expire` changes which missing worktrees are annotated as prunable. The selectable expiry row belongs to prune. The help menu inserts only a flag or keyword. The user supplies worktree paths, branch names, commit arguments and lock reasons. [Noble worktree](https://manpages.ubuntu.com/manpages/noble/man1/git-worktree.1.html), [Resolute worktree](https://manpages.ubuntu.com/manpages/resolute/man1/git-worktree.1.html) and [upstream worktree](https://git-scm.com/docs/git-worktree/2.56.0)
- **Pinned numerical semantics.** Git 2.48.0 parses `-n` and `--max-count` as signed integers and only decrements positive counts. The shared stash-list definition now reflects this. For direct worktree prune, the initial cutoff is `TIME_MAX`. The age check for an ordinary missing worktree with an index uses its administrative index timestamp. `never` and `false` set a zero cutoff, while `all` and `now` remove the extra age restriction. A lock protects a valid registration. Broken administrative records can qualify independently of age. The existing relative-date, epoch and time-zone guidance remains scoped to 2.48.0. [Revision parser](https://github.com/git/git/blob/v2.48.0/revision.c#L2303), [expiry parser](https://github.com/git/git/blob/v2.48.0/date.c#L957), [prune command](https://github.com/git/git/blob/v2.48.0/builtin/worktree.c#L252) and [pruning eligibility](https://github.com/git/git/blob/v2.48.0/worktree.c#L859)

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

On each target, real Bash/tmux sessions opened all 11 bundled menus with discovery disabled. At 180×72, inspection traversed every category and compared all 85 visible labels, full summaries and Details with the corresponding profile. Each menu also inserted its last selected flag or keyword ahead of an existing suffix. A Git stub detected any execution of the pending command.

The 60×16 regression searches for “negative count” in stash list and “locked worktree” in worktree remove. It scrolls the selected Details, checks cancellation against the original line and cursor, then verifies literal insertion of `--max-count=` and `--force` with the suffix intact. The stub recorded zero executions. The three focused tests covered this regression, the expiry sentinels and the numerical-inventory review on each target. [Terminal regression](../tests/test_expansion_terminal.py) and [sandbox runner](development.md#isolated-local-debugging)

To repeat the focused terminal test, replace TARGET with `host`, `noble310` or `noble312`.

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k git_stash_count_and_locked_worktree_guidance -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,332 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,332 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,332 | 0 | 1 |

Each snapshot included the untracked audit documents. The coverage gates and bundled-profile checks passed. The sole skip on each target was the Windows-specific probe test.
