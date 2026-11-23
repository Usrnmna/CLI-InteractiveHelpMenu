# fd and fdfind option audit

The [fd](../profiles/fd.json) and [fdfind](../profiles/fdfind.json) menus each contain 19 selectable spellings. They describe the same file finder. On both Ubuntu releases, the fd-find package installs the public executable as `fdfind` and the manual as `fdfind(1)`. Ubuntu's separate `fd(1)` page belongs to fdclone.

## Sources

| Reference | Version | Scope |
| --- | --- | --- |
| [Upstream fd manual](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1) and [release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md) | 10.5.2 | Search syntax, option interactions and the changes introduced in 10.0. |
| [Ubuntu 24.04 fdfind(1)](https://manpages.ubuntu.com/manpages/noble/man1/fdfind.1.html) | fd-find 9.0.0-1 | Noble package manual. |
| [Ubuntu 26.04 fdfind(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fdfind.1.html) | fd-find 10.3.0-2ubuntu1 | Resolute package manual. |
| [Pinned manual](https://github.com/sharkdp/fd/blob/v10.2.0/doc/fd.1), [argument declarations](https://github.com/sharkdp/fd/blob/v10.2.0/src/cli.rs), [filter construction](https://github.com/sharkdp/fd/blob/v10.2.0/src/main.rs) and [directory walk](https://github.com/sharkdp/fd/blob/v10.2.0/src/walk.rs) | 10.2.0 | Type aliases, extension comparison, exclusions, depth and absolute-path matching in the version used by the structured guides. |

## Disposition of all 38 entries

Each row covers one selectable spelling in each profile. The original wording and disposition agree across both profiles. The two terminal menus were checked independently.

| `fd` entry | `fdfind` entry | Original wording | Finding and change |
| --- | --- | --- | --- |
| `--hidden` | `--hidden` | Incomplete | Retain the short summary. Hidden paths still obey ignore rules. With this switch alone, 9.0 skips `.git/` by default. From 10.0, an explicit exclusion can keep it out. |
| `-H` | `-H` | Incomplete | Give the short spelling the same version-specific `.git/` guidance. |
| `--no-ignore` | `--no-ignore` | Incomplete | Disable standard ignore files, including Git and fd rules. Hidden paths need `--hidden` as well, and explicit exclusions still apply. |
| `-I` | `-I` | Incomplete | Record the same distinction between ignored paths, hidden paths and explicit exclusions. |
| `--type TYPE` | `--type TYPE` | Incomplete | Repeated ordinary types admit either kind. Executable selects executable files. Empty selects empty files or directories and can be narrowed to one kind. |
| `-t TYPE` | `-t TYPE` | Incomplete | Include actionable combinations such as `-tf -tl` and `-te -td`. Both type guides now identify `dir` as an alias introduced in 10.0. |
| `--extension EXT` | `--extension EXT` | Incomplete | A case-insensitive extension match can return directories. Add `-tf` for regular files only. |
| `-e EXT` | `-e EXT` | Incomplete | Repeated extensions admit any listed extension. The value guide retains the optional leading dot. |
| `--max-depth DEPTH` | `--max-depth DEPTH` | Redundant | Replace the repeated units and version preamble with observable boundaries. Depth one searches immediate children, zero returns no entries and omission leaves the depth unlimited. |
| `-d DEPTH` | `-d DEPTH` | Redundant | Give the short spelling the same boundaries. Depth is relative to each search root. |
| `--exclude PATTERN` | `--exclude PATTERN` | Inaccurate | The old summary said the pattern itself was excluded. The glob selects paths to skip, including the contents of matching directories. |
| `-E PATTERN` | `-E PATTERN` | Inaccurate | Quote the glob so Bash passes it intact, as in `-E '*.log'`. Exclusions can be repeated and still take effect with `--no-ignore`. |
| `--full-path` | `--full-path` | Incomplete | Match against the absolute path, including parent directory names. The default search matches the entry name alone. |
| `--absolute-path` | `--absolute-path` | Sufficient as written | Keep the summary. Details point to the separate option that changes what the pattern matches. |
| `--glob` | `--glob` | Incomplete | Match the whole name with a quoted glob. With full-path matching, `**` can span directory levels. |
| `--fixed-strings` | `--fixed-strings` | Incomplete | Literal punctuation loses its regex meaning, but a substring can still match a longer name. |
| `--case-sensitive` | `--case-sensitive` | Sufficient as written | Keep the summary. Details explain why the flag matters for lowercase patterns under smart case. |
| `--ignore-case` | `--ignore-case` | Sufficient as written | Keep the summary. Details explain why the flag matters for patterns containing uppercase letters. |
| `--print0` | `--print0` | Sufficient as written | Keep the NUL-byte summary. Pair with `xargs -0` to pass filenames containing spaces or newlines intact. |

## Versions, syntax and manual-only coverage

- **Hidden Git directories.** Upstream 9.0 introduced a default exclusion for `.git/` under `--hidden`. Version 10.0 removed it. A separate ignore rule can still exclude that directory. Both menus give `--exclude .git` as an explicit choice. For a hidden path excluded by an ignore file, combine `--hidden` and `--no-ignore`. [Release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md#v1000), [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/fdfind.1.html) and [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/fdfind.1.html)
- **Entry types and extensions.** `d` and `directory` work on both Ubuntu releases. Noble rejects `dir`, which Resolute and the pinned 10.2.0 parser accept. The 10.5.2 manual explicitly includes directories in extension searches. The older Ubuntu manuals omit that detail. The 10.2.0 implementation matches the entry name against a case-insensitive extension filter independently of the search pattern. [Type declarations](https://github.com/sharkdp/fd/blob/v10.2.0/src/cli.rs#L774), [extension filter](https://github.com/sharkdp/fd/blob/v10.2.0/src/main.rs#L297) and [upstream manual](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1)
- **Insertion and operands.** The menu inserts the selected flag and leaves its value for the shell user. The existing short forms also accept attached input such as `-d1` and `-tf`. At the command line the first positional argument supplies the pattern and subsequent paths supply search roots. An empty pattern such as `''` selects all names when specifying a root. The profiles stop offering parent options after a positional operand. The program itself accepts options elsewhere on the command line. [Upstream syntax](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1) and [argument-boundary tests](../tests/test_expansion_systems.py)
- **Other options.** Manual-only coverage includes alternate spellings such as `-g`, `-F`, `-i`, `-s`, `-a`, `-p` and `-0`. Additional controls cover ignore sources and unrestricted search, symlink traversal, mount boundaries, minimum and exact depth, size, time and ownership filters, result limits, formatting and command execution. Upstream 10.5 added `--exact` for a whole literal name. For both Ubuntu packages, a glob with no wildcard characters supplies the whole-name example. These controls have no additional selectable rows. [Upstream manual](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1) and [10.5 release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md#1050)

The audit refreshed 42 reviewed fingerprints covering 38 options, two command descriptions and two profile files. The type alias was checked against the pinned parser before refreshing. The structured maximum-depth definition, option order and insertion forms were preserved. [Numerical inventory review](numerical-inventory/review.json)

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

On each target, real Bash/tmux sessions opened both profiles with discovery disabled. At 200×78 each session visited all 19 rows and compared the command header, visible label, summary and complete Details with the profile and formatter. Selecting `--max-depth` inserted the literal flag before an existing pattern. At 60×16 the regression searched for “fd 9.0”, scrolled to the `.git` exclusion guidance, cancelled and checked the original Readline buffer and cursor. It then found `--exclude` by searching for “quote wildcards” and inserted a quoted glob ahead of the existing pattern. The two executable stubs recorded zero runs. [Terminal regression](../tests/test_expansion_terminal.py)

Four focused tests passed on each target. They covered the minimum-size regression, option and alias declarations, the numerical inventory and the NUL-output diagnostic. To repeat the terminal check, substitute `host`, `noble310` or `noble312` for TARGET. [Offline sandbox instructions](development.md#isolated-local-debugging)

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k fd_hidden_directory_guidance_and_midline_exclusion -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,335 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,335 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,335 | 0 | 1 |

The full-suite snapshots included the untracked audit documents. The single skip on each target was the Windows-specific probe.
