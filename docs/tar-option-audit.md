# Bundled GNU tar option audit

First recorded 2026-11-22. This first pass covered 12 bundled rows. See the [expanded inventory and verification](tar-manual-coverage.md) for the later manual comparison.

## Manuals and versions

| Source | Version reviewed | Scope |
| --- | --- | --- |
| [GNU tar manual](https://www.gnu.org/software/tar/manual/tar.html) | 1.35.90 | Published online edition, including operations, option summary and worked examples. |
| [GNU tar release source](https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz) | 1.35 | The packaged manual in `doc/tar.texi` provides the release reference for the Ubuntu base version. |
| [Ubuntu 24.04 LTS tar(1)](https://manpages.ubuntu.com/manpages/noble/man1/tar.1.html) | 1.35+dfsg-3ubuntu0.4 | Operation modes, option declarations, operands and exit status. |
| [Ubuntu 26.04 LTS tar(1)](https://manpages.ubuntu.com/manpages/resolute/man1/tar.1.html) | 1.35+dfsg-4ubuntu0.4 | Same 12 declarations and definitions as the Noble page. |

The Ubuntu pages describe `-C` as applying to all following options. GNU's
working-directory chapter gives the more precise rule and explicitly documents
the exception for archive paths. The 1.35 release manual also illustrates
successive directory changes. [GNU working-directory examples](https://www.gnu.org/software/tar/manual/tar.html#directory)

## Disposition of the 12 entries

The 12 original rows covered archive operations, member selection and file location. In particular, `-C` changes where tar looks for subsequent member operands. A relative archive path supplied by `-f` is resolved from the starting directory.

## Manual-only coverage

The two Ubuntu pages listed 169 distinct long spellings. The pilot selected 12. The other 157 included aliases and separate operations. The full inventory reconciles that difference.

## Sandbox verification

A real Bash/tmux session displayed all 12 descriptions at 160×56 on each target. The fixtures verified search, cancellation and literal editing. Archive behavior came from the manuals.

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 26.04.1 LTS | 3.14.4 | 1,328 | 0 | 1 |
| 24.04.5 LTS | 3.10.20 | 1,328 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,328 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
