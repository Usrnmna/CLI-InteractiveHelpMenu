# Git commit and log option audit

First recorded 2026-11-22. This first pass covered 19 bundled rows. See the [expanded inventory and verification](git-commit-log-manual-coverage.md) for the later manual comparison.

## Reference manuals

| Source | Version | Manuals |
| --- | --- | --- |
| Git upstream | Latest manual revisions: 2.55.0 for commit and 2.56.0 for log | [git commit](https://git-scm.com/docs/git-commit/2.55.0) and [git log](https://git-scm.com/docs/git-log/2.56.0) |
| Ubuntu 24.04 LTS (Noble) | git 1:2.43.0-1ubuntu7.4 | [git-commit(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-commit.1.html) and [git-log(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) |
| Ubuntu 26.04 LTS (Resolute) | git 1:2.53.0-1ubuntu1.1 | [git-commit(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-commit.1.html) and [git-log(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) |
| Existing structured value guides | Git 2.48.0 | [message options](https://github.com/git/git/blob/v2.48.0/Documentation/git-commit.txt), [revision selection](https://github.com/git/git/blob/v2.48.0/Documentation/rev-list-options.txt), [revision parser and walk](https://github.com/git/git/blob/v2.48.0/revision.c) and [date parser](https://github.com/git/git/blob/v2.48.0/date.c) |

## Disposition of the bundled entries

### git commit

The nine entries distinguished staged content, tracked changes included by `-a`, explicit path selection and commit message input.

### git log

The ten entries distinguished limiting history from formatting it. A `--since=` traversal could stop early. The commit date, count and optional display arguments required separate explanations.

## Coverage boundaries and version differences

The original profiles covered a small subset of the commit and log manuals. The revisit reconciled message and status options, revision limiting, history traversal, pretty formats and shared diff controls by operation.

## Behavior observed in disposable Git repositories

The offline sandbox used Git 2.43.0 on Ubuntu 24.04 and Git 2.53.0 on Ubuntu 26.04. Both executables produced the following results.

| Fixture | Observation |
| --- | --- |
| Staged, unstaged, deleted and untracked paths | Both `commit --short` and `commit --dry-run --all` preserved HEAD. Short status distinguished staged, unstaged and untracked paths. A subsequent `commit --all` included the three tracked changes and left the untracked file outside the index. |
| Commit messages and editor | Two `--message` arguments produced two paragraphs. Amending with `--file -` used standard input and retained the parent and author. With `-vv --edit`, the editor saw both diffs and the saved message contained only the supplied text. |
| Nonmonotonic committer dates | From a 2011 tip through a 2000 parent to a 2010 ancestor, a 2005 cutoff with `--since` returned only the tip. `--since-as-filter` also found the 2010 ancestor. All three author dates were in 1999. A cutoff equal to the tip timestamp included the tip. |
| Counts, filtering and refs | Zero returned no commits and `--max-count=-2` returned the unrestricted selection. The separate shorthand `-2` requests two commits. A limit of one followed by reversal returned the newest commit. Author and repeated message filters matched the expected commits, including the narrower `--all-match` result. `--all` included a separate branch's history and bare `--decorate` printed its name through a pipe. |
| Two-parent merge with different files on each branch | `log -1 --patch` displayed the merge header without a diff. Adding `--diff-merges=first-parent` displayed the change introduced from the other branch. |

## Rendered menus and sandbox checks

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,333 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,333 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,333 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
