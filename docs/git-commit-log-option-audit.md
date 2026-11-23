# Git commit and log option audit

The [commit menu](../profiles/git-commit.json) contains nine entries and the [log menu](../profiles/git-log.json) contains ten. The audit covers the bundled profiles, including their structured value guides, search text, argument spelling and rendered Details.

## Reference manuals

| Source | Version | Manuals |
| --- | --- | --- |
| Git upstream | Latest manual revisions: 2.55.0 for commit and 2.56.0 for log | [git commit](https://git-scm.com/docs/git-commit/2.55.0) and [git log](https://git-scm.com/docs/git-log/2.56.0) |
| Ubuntu 24.04 LTS (Noble) | git 1:2.43.0-1ubuntu7.4 | [git-commit(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-commit.1.html) and [git-log(1)](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html) |
| Ubuntu 26.04 LTS (Resolute) | git 1:2.53.0-1ubuntu1.1 | [git-commit(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-commit.1.html) and [git-log(1)](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) |
| Existing structured value guides | Git 2.48.0 | [message options](https://github.com/git/git/blob/v2.48.0/Documentation/git-commit.txt), [revision selection](https://github.com/git/git/blob/v2.48.0/Documentation/rev-list-options.txt), [revision parser and walk](https://github.com/git/git/blob/v2.48.0/revision.c) and [date parser](https://github.com/git/git/blob/v2.48.0/date.c) |

## Disposition of the bundled entries

The disposition describes the original row. The finding records what someone composing the command needs to know. Options appear in menu order.

### git commit

| Entry | Disposition | Finding |
| --- | --- | --- |
| `--message` | Incomplete | Keep the summary and the quoting advice. Repeating `-m` starts a separate paragraph. A message and a message file are mutually exclusive. |
| `--file` | Incomplete | Keep the summary. A file name of `-` reads standard input. Add `--edit` to open that message in the editor. |
| `--edit` | Incomplete | A supplied message normally bypasses the editor. This switch opens it for a message supplied with `-m`, read with `-F` or reused with `-C`. |
| `--all` | Incomplete | Commit already staged changes plus working-tree modifications and deletions of tracked files. A new untracked path requires an explicit add. |
| `--patch` | Incomplete | Interactive hunk selection adds to the staged snapshot. Existing staged changes also enter the commit. |
| `--amend` | Inaccurate | The operation replaces the tip, including on a detached HEAD. Its parents and, by default, its author carry over. The previous message can be kept with `--no-edit`. A published amendment rewrites history. |
| `--dry-run` | Incomplete | Preview the same options and paths as the intended commit. The output also identifies changes left unstaged and untracked files. |
| `--verbose` | Incomplete | The editor shows the proposed diff. A second `-v` adds unstaged tracked changes. The displayed diffs stay out of the saved message. |
| `--short` | Incomplete | The switch implies dry-run even when invoked alone. For ordinary tracked paths the first column describes the index and the second describes the working tree. Conflicts and untracked paths have distinct codes. [Short status format](https://git-scm.com/docs/git-status#_short_format) |

### git log

| Entry | Disposition | Finding |
| --- | --- | --- |
| `--oneline` | Inaccurate | The abbreviated object ID and subject form a compact header. A patch or graph can span additional lines for the same commit. |
| `--graph` | Incomplete | Draw ancestry beside the commits. The default graph order is topological and edges may occupy lines between commits. |
| `--decorate` | Incomplete | Identify the refs pointing to each commit. Explicit bare `--decorate` requests short names. Attached `=full` requests full names and `=auto` limits decorations to terminal output. |
| `--stat` | Incomplete | Show per-file change statistics for displayed diffs. Git accepts optional attached width, name-width and entry-count parameters. The menu inserts the bare flag. |
| `--patch` | Inaccurate | The former description promised a patch for every commit. Merge diffs are normally omitted. An explicit first-parent merge diff compares the merge result with its first parent. |
| `--max-count=` | Inaccurate | Zero selects nothing. A negative count leaves the result uncapped. The previous structured lower bound excluded accepted input. The limit applies before output reversal. |
| `--author=` | Incomplete | The regular expression matches the author header, including name or email. Repeated author patterns accept any match. The committer has a separate filter. |
| `--grep=` | Incomplete | Search message text and enabled notes. Repeated expressions accept any match by default. Use `--all-match` to require each expression. |
| `--since=` | Redundant | The editorial text duplicated the structured date grammar. Details now explain the committer timestamp, early termination and the full-range alternative `--since-as-filter`. The versioned date grammar remains in the value guide. |
| `--all` | Incomplete | Start the walk from HEAD and refs under `refs/`, including local branches, remote-tracking branches and tags. A reflog-only commit requires another starting point. |

## Coverage boundaries and version differences

- **Commit.** Manual-only controls include reuse, re-edit, fixup and squash messages, author and date overrides, signoff, signatures, trailers, cleanup, empty commits, hooks, pathspec input, interactive modes, and the porcelain, branch and NUL-delimited status formats. The menu inserts `--message` and `--file` with a separate operand. The manuals also show attached long forms and the short aliases `-m` and `-F`. Resolute and upstream document patch context controls `--unified` and `--inter-hunk-context` for commit. The Noble commit manual omits them. [Noble commit](https://manpages.ubuntu.com/manpages/noble/man1/git-commit.1.html), [Resolute commit](https://manpages.ubuntu.com/manpages/resolute/man1/git-commit.1.html) and [upstream commit](https://git-scm.com/docs/git-commit/2.55.0)
- **Log.** Revision ranges and paths after `--` are operands. Additional manual controls cover ref selection and reflogs, traversal order and parent selection, date and committer filters, regex modes, pretty formats, notes, decoration filters, merge-diff formats, rename detection, diff algorithms and line or content searches. Options mentioned in Details, including `--all-match`, `--since-as-filter` and `--diff-merges=first-parent`, can be typed directly. The current upstream log manual gives `today` a specific midnight meaning that neither Ubuntu page documents. The profile uses an explicit date or relative expression for portable guidance. [Noble log](https://manpages.ubuntu.com/manpages/noble/man1/git-log.1.html), [Resolute log](https://manpages.ubuntu.com/manpages/resolute/man1/git-log.1.html) and [upstream log](https://git-scm.com/docs/git-log/2.56.0)
- **Structured guidance.** Git 2.48.0 accepts signed output counts, stops at zero and decrements positive counts. The date parser still distinguishes calendar fields, sufficiently large bare epoch values, zoned timestamps and relative expressions. The reviewed inventory fingerprints cover the changed profile files, command descriptions, option entries and the log count definition. [Revision parser](https://github.com/git/git/blob/v2.48.0/revision.c) and [date parser](https://github.com/git/git/blob/v2.48.0/date.c)

## Behavior observed in disposable Git repositories

The offline sandbox used Git 2.43.0 on Ubuntu 24.04 and Git 2.53.0 on Ubuntu 26.04. Both executables produced the following results.

| Fixture | Observation |
| --- | --- |
| Staged, unstaged, deleted and untracked paths | Both `commit --short` and `commit --dry-run --all` preserved HEAD. Short status distinguished staged, unstaged and untracked paths. A subsequent `commit --all` included the three tracked changes and left the untracked file outside the index. |
| Commit messages and editor | Two `--message` arguments produced two paragraphs. Amending with `--file -` used standard input and retained the parent and author. With `-vv --edit`, the editor saw both diffs and the saved message contained only the supplied text. |
| Nonmonotonic committer dates | From a 2011 tip through a 2000 parent to a 2010 ancestor, a 2005 cutoff with `--since` returned only the tip. `--since-as-filter` also found the 2010 ancestor. All three author dates were in 1999. A cutoff equal to the tip timestamp included the tip. |
| Counts, filtering and refs | Zero returned no commits and `-2` returned the unrestricted selection. A limit of one followed by reversal returned the newest commit. Author and repeated message filters matched the expected commits, including the narrower `--all-match` result. `--all` included a separate branch's history and bare `--decorate` printed its name through a pipe. |
| Two-parent merge with different files on each branch | `log -1 --patch` displayed the merge header without a diff. Adding `--diff-merges=first-parent` displayed the change introduced from the other branch. |

## Rendered menus and sandbox checks

On each target, real Bash/tmux sessions at 180×72 traversed both bundled menus and checked each command header and all 19 option labels, summaries and Details. Midline selection inserted `--message`, bare `--decorate` and bare `--stat` ahead of an existing suffix. At 60×16 the regression searched for “short status format” and “committer timestamp”, scrolled to the dry-run and history-walk qualifications, and verified that cancellation restored both the original buffer and cursor. Selection inserted `--short` and `--since=` at the cursor with the suffix intact. The Git stub recorded zero executions. [Terminal regression](../tests/test_expansion_terminal.py)

The three focused checks passed on each target. They covered the minimum-size terminal regression, the Git date heuristics and expiry sentinels, and numerical-inventory review. To repeat the terminal regression, substitute `host`, `noble310` or `noble312` for TARGET. The full-suite snapshots also included the untracked audit documents. [Sandbox instructions](development.md#isolated-local-debugging)

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k commit_preview_and_log_date_filter_at_minimum_size -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,333 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,333 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,333 | 0 | 1 |

The single skip on each target was the Windows-specific probe test.
