# Bundled GNU grep option audit

First recorded 2026-11-22. This first pass covered 14 bundled rows. See the [expanded inventory and verification](grep-manual-coverage.md) for the later manual comparison.

## Manuals reviewed

| Source | Version | Material checked |
| --- | --- | --- |
| [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html) | 3.12 | Option definitions, regular expression syntax, context groups and filename selection. |
| [Ubuntu 24.04 LTS grep(1)](https://manpages.ubuntu.com/manpages/noble/man1/grep.1.html) | 3.11-4build1 | Declarations and descriptions of all 14 entries. |
| [Ubuntu 26.04 LTS grep(1)](https://manpages.ubuntu.com/manpages/resolute/man1/grep.1.html) | 3.12-1 | The 14 definitions agree with the Noble page. |

## Disposition of the bundled entries

The 14 original long options needed distinctions between lines and matches, operand and recursive path filtering, and the interaction between context and `-o`.

## Two qualifications checked on both grep versions

Both versions accepted a matching explicitly named path with a slash in the include pattern. In the tested `-o -C1` case, both omitted surrounding lines and produced no warning.

## Manual-only coverage

The three manuals listed 48 distinct long spellings. The baseline selected 14, leaving 34 long spellings, short aliases and the short-only `-I` for the full comparison.

## Rendered-menu verification

The 60×16 terminal regression searched for “group separator”, reached the qualification about `-o`, and checked cancellation and insertion with a shell stub.

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 24.04.5 LTS | 3.10.20 | 1,329 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,329 | 0 | 1 |
| 26.04.1 LTS | 3.14.4 | 1,329 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
