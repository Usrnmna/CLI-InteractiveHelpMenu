# fd and fdfind option audit

First recorded 2026-11-22. This first pass covered 38 bundled rows. See the [expanded inventory and verification](fd-manual-coverage.md) for the later manual comparison.

## Sources

| Reference | Version | Scope |
| --- | --- | --- |
| [Upstream fd manual](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1) and [release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md) | 10.5.2 | Search syntax, option interactions and the changes introduced in 10.0. |
| [Ubuntu 24.04 fdfind(1)](https://manpages.ubuntu.com/manpages/noble/man1/fdfind.1.html) | fd-find 9.0.0-1 | Noble package manual. |
| [Ubuntu 26.04 fdfind(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fdfind.1.html) | fd-find 10.3.0-2ubuntu1 | Resolute package manual. |
| [Pinned manual](https://github.com/sharkdp/fd/blob/v10.2.0/doc/fd.1), [argument declarations](https://github.com/sharkdp/fd/blob/v10.2.0/src/cli.rs), [filter construction](https://github.com/sharkdp/fd/blob/v10.2.0/src/main.rs) and [directory walk](https://github.com/sharkdp/fd/blob/v10.2.0/src/walk.rs) | 10.2.0 | Type aliases, extension comparison, exclusions, depth and absolute-path matching in the version used by the structured guides. |

## Disposition of all 38 entries

Both names needed the same guidance on hidden files, ignore rules, depth, case and type selection. The selectable spellings retained their individual insertions in both menus.

## Versions, syntax and manual-only coverage

The `fd-find` package supplied `fdfind(1)` on Ubuntu. The separate `fd(1)` page belonged to fdclone. Version 9 excluded `.git/` by default under `--hidden`, while version 10 removed that default. Independent ignore rules could still hide it.

## Behavior observed on disposable trees

Tests unpacked the corresponding Ubuntu amd64 package into offline scratch space and ran its `fdfind` executable. Fixtures included an initialized Git repository, separate Git and fd ignore files, hidden paths, mixed-case extensions, a directory ending in `.TXT`, a symlink, an executable and a filename containing a newline. [Ubuntu package archive](https://archive.ubuntu.com/ubuntu/pool/universe/r/rust-fd-find/)

| Fixture | Ubuntu 24.04 · fdfind 9.0.0 | Ubuntu 26.04 · fdfind 10.3.0 |
| --- | --- | --- |
| Hidden Git directory | `-H` omitted `.git/HEAD`. `-HI` included it. | `-H` included `.git/HEAD`. Adding `--exclude .git` omitted it. |
| Directory type | `-t dir` exited with status 2. `-td` selected directories. | Both spellings selected directories. |

| Common fixture | Observed on both Ubuntu builds |
| --- | --- |
| Visibility and pruning | `-H` found hidden children while respecting ignore files. `-I` admitted ignored visible names. Explicit name and glob exclusions still pruned matching paths. |
| Extensions and types | `-e .txt` found `folder.TXT/` and mixed-case regular files, even with `-s`. Repeating `-e` admitted either suffix. Adding `-tf` confined results to regular files. File-plus-symlink, executable and empty-directory filters selected their respective fixtures. |
| Traversal and paths | Zero depth returned nothing, one returned direct children and the unrestricted search found a grandchild. A parent-directory pattern matched with `-p`. Using `-a` alone changed the printed path while preserving name-only matching. |
| Patterns, case and output | A literal substring matched both `r.dot` and `r.dot.bak`, while the glob `r.dot` selected only the former. A full-path glob with `**` reached a nested file. Smart case, forced case and the NUL terminator after a filename with an embedded newline matched the documented behavior. |

## Rendered menus and sandbox verification

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,335 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,335 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,335 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
