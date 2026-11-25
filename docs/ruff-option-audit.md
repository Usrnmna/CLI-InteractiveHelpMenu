# Ruff option audit

First recorded 2026-11-22. Counts and observations below describe the original bundled selections. See the [expanded inventory and verification](ruff-manual-coverage.md) for the later manual comparison.

The two bundled menus contained 30 entries, including the short and long spellings of the logging flags. The audit compares Ruff 0.17.6 with 0.11.13, the release used in the original value guidance. The 16 lint entries and 14 formatting entries retained their original order, operands and insertion spellings. [Lint profile](../profiles/ruff-check.json) · [Format profile](../profiles/ruff-format.json)

## Sources

| Reference | Ruff 0.11.13 | Ruff 0.17.6 |
| --- | --- | --- |
| Generated command help, configuration precedence, Python inference and file discovery | [Configuration and CLI](https://github.com/astral-sh/ruff/blob/0.11.13/docs/configuration.md) | [Configuration and CLI](https://github.com/astral-sh/ruff/blob/0.17.6/docs/configuration.md) |
| Rule selection, fix safety and lint exit codes | [Linter](https://github.com/astral-sh/ruff/blob/0.11.13/docs/linter.md) | [Linter](https://github.com/astral-sh/ruff/blob/0.17.6/docs/linter.md) |
| Formatter behavior, line wrapping and exit codes | [Formatter](https://github.com/astral-sh/ruff/blob/0.11.13/docs/formatter.md) | [Formatter](https://github.com/astral-sh/ruff/blob/0.17.6/docs/formatter.md) |
| Setting defaults and accepted values | [Settings declarations](https://github.com/astral-sh/ruff/blob/0.11.13/crates/ruff_workspace/src/options.rs) | [Settings declarations](https://github.com/astral-sh/ruff/blob/0.17.6/crates/ruff_workspace/src/options.rs) |

Ubuntu’s Noble and Resolute amd64 contents searches found no package shipping an executable ending in `bin/ruff`. Both release-specific requests for the `ruff(1)` man page returned HTTP 404. The tagged Astral references and upstream binaries supply the option evidence. The Ubuntu results below apply to the project’s sandbox targets. [Noble contents search](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fruff&mode=path&suite=noble&arch=amd64) · [Resolute contents search](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fruff&mode=path&suite=resolute&arch=amd64)

## Disposition of all 30 entries

### ruff check

Lint `--diff` previews proposed edits and can return success for an unfixable violation alone.

### ruff format

Format `--check` distinguishes clean files, files needing changes and errors. Format `--diff` previews formatting without writing.

## Version differences and manual-only coverage

The 0.11.13 settings declaration stopped at `py313`, but both commands accepted `py314` and lint labeled it experimental. Both 0.17.6 commands also accepted `py315`.

## Executable verification

Each target ran both upstream Linux x86-64 binaries extracted from the published wheels into disposable sandbox storage. Each wheel's SHA-256 digest was checked against its release metadata. The fixtures used generated Python and Markdown input, a temporary Ruff configuration and private cache paths. No project files were passed to either binary. [0.11.13 wheel metadata](https://pypi.org/pypi/ruff/0.11.13/json) · [0.17.6 wheel metadata](https://pypi.org/pypi/ruff/0.17.6/json)

| Fixture | Result |
| --- | --- |
| Fixable unused import and unfixable undefined name | Lint diff previewed removal of the import and preserved the file. Selecting only the undefined name yielded no diff and exit 0. Applying the safe fix removed the import and exited 1 for the remaining violation. |
| Unused local assignment | Enabling unsafe fixes alone left the file intact. Safe fixing also left the assignment. Combining fix and unsafe fixes removed it. |
| Reporting and selection | JSON contained the two expected codes. The specific selector beat a broader ignore, and an equal ignore disabled the rule. The named selector worked in preview only on 0.17.6. Exit-zero suppressed the lint failure while invalid TOML still exited 2. |
| Formatting and configuration | Check and diff exited 1 on unformatted input and preserved its bytes. After formatting, both exited 0. Piped input honored file-based quote style, isolated defaults and inline TOML overrides. The file supplied as stdin context stayed intact. |
| File selection and logging | Both commands skipped an excluded file in a directory traversal, processed the explicitly named path, and honored forced exclusion. Both quiet spellings preserved the relevant result. Both verbose spellings emitted debug messages. |
| Python targets, widths and extension mapping | Both commands accepted every advertised Python target through the version-specific maximum and rejected the next token. Width tests checked zero, one, 88, 320, 321, 65,535 and 65,536. Only 0.17.6 formatted a Python fence through the Markdown extension mapping. |

## Rendered menus and offline suites

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Rendered terminal regression](../tests/test_expansion_terminal.py) · [Numerical regression](../tests/test_numerical_migration.py) · [Source-derived expectations](../tests/fixtures/value-semantics/migration-evidence.json)

Each Ubuntu target opened both menus in real Bash/tmux sessions with discovery disabled. At 210×100 every highlighted option, summary and complete Details pane was checked. The first rendering pass showed that the formatter’s stdin example had been dropped from Details. Rewording it as a direct instruction restored the filename and the literal stdin operand. The final pass verified all 30 entries. Cancelling restored the original pending line and cursor. Selecting `--select` or `--line-length` inserted the literal option before an existing filename. A shell stub recorded unexpected Ruff execution and remained unused.

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 33 / 0 / 0 | 1,344 / 0 / 1 | 486.144 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 33 / 0 / 0 | 1,344 / 0 / 1 | 549.045 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 33 / 0 / 0 | 1,344 / 0 / 1 | 487.288 s |

Each Linux suite skipped the Windows-specific probe.
