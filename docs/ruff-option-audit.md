# Ruff option audit

The two bundled menus contain 30 entries, including the short and long spellings of the logging flags. The audit compares Ruff 0.17.6 with 0.11.13, the release used in the original value guidance. The 16 lint entries and 14 formatting entries retain their original order, operands and insertion spellings. [Lint profile](../profiles/ruff-check.json) · [Format profile](../profiles/ruff-format.json)

## Sources

| Reference | Ruff 0.11.13 | Ruff 0.17.6 |
| --- | --- | --- |
| Generated command help, configuration precedence, Python inference and file discovery | [Configuration and CLI](https://github.com/astral-sh/ruff/blob/0.11.13/docs/configuration.md) | [Configuration and CLI](https://github.com/astral-sh/ruff/blob/0.17.6/docs/configuration.md) |
| Rule selection, fix safety and lint exit codes | [Linter](https://github.com/astral-sh/ruff/blob/0.11.13/docs/linter.md) | [Linter](https://github.com/astral-sh/ruff/blob/0.17.6/docs/linter.md) |
| Formatter behavior, line wrapping and exit codes | [Formatter](https://github.com/astral-sh/ruff/blob/0.11.13/docs/formatter.md) | [Formatter](https://github.com/astral-sh/ruff/blob/0.17.6/docs/formatter.md) |
| Setting defaults and accepted values | [Settings declarations](https://github.com/astral-sh/ruff/blob/0.11.13/crates/ruff_workspace/src/options.rs) | [Settings declarations](https://github.com/astral-sh/ruff/blob/0.17.6/crates/ruff_workspace/src/options.rs) |

Ubuntu’s Noble and Resolute amd64 contents searches found no package shipping an executable ending in `bin/ruff`. Both release-specific requests for the `ruff(1)` man page returned HTTP 404. The tagged Astral references and upstream binaries supply the option evidence. The Ubuntu results below apply to the project’s sandbox targets. [Noble contents search](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fruff&mode=path&suite=noble&arch=amd64) · [Resolute contents search](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fruff&mode=path&suite=resolute&arch=amd64)

## Disposition of all 30 entries

Each row below assesses the *original* description. The shared table covers nine entries per command. Each alias remains independently selectable.

| Entry on both menus | Original disposition | Menu decision |
| --- | --- | --- |
| `--target-version VERSION` | Inaccurate | Select the oldest supported Python language version. Correct the accepted tokens and distinguish the built-in fallback from configuration and project inference. |
| `--exclude PATTERNS` | Incomplete | Quote comma-separated globs. Explicit paths bypass exclusions unless `--force-exclude` is set. Use `--extend-exclude` to add patterns. |
| `--no-cache` | Incomplete | Explain that Ruff skips cached results and reprocesses the files. This flag does not clean an existing cache. |
| `--config CONFIG` | Redundant | Replace the repeated parser explanation with a quoted TOML assignment. A setting override takes precedence over a config file, and a dedicated CLI flag takes precedence over both. |
| `--isolated` | Sufficient | Retain the file-isolation meaning. Explicit options, including inline TOML assignments, still apply. |
| `-q` | Incomplete | Suppress summary output. Lint diagnostics, formatting-check results and requested diffs stay visible. |
| `--quiet` | Incomplete | Give the long spelling the same command-specific explanation as `-q`. |
| `-v` | Incomplete | Enable debug logging, including configuration and file-discovery messages. |
| `--verbose` | Incomplete | Give the long spelling the same debug-logging explanation as `-v`. |

### ruff check

| Entry | Original disposition | Menu decision |
| --- | --- | --- |
| `--fix` | Incomplete | Apply eligible fixes to files. Safe fixes are the default. Remaining violations normally produce exit status 1. |
| `--unsafe-fixes` | Incomplete | Permit fixes that can change behavior. Writing them requires a fix mode, and `--diff` previews them. |
| `--diff` | Incomplete | Show a patch without writing. The implied `--fix-only` makes the exit status reflect proposed edits. An unfixable violation alone can exit 0. |
| `--select RULES` | Incomplete | Replace the base selection using codes, prefixes or ALL. Extending the existing selection uses `--extend-select`. Named selectors in 0.17.6 require preview mode. |
| `--ignore RULES` | Incomplete | Disable matching rules. The more specific selector wins. Ignore wins a tie. |
| `--output-format FORMAT` | Sufficient | Keep the report-format meaning and identify the full default, the concise listing and machine-readable JSON. |
| `--exit-zero` | Sufficient | Lint diagnostics still print. Operational and configuration errors still exit 2. |

### ruff format

| Entry | Original disposition | Menu decision |
| --- | --- | --- |
| `--check` | Sufficient | Keep the read-only operation. Distinguish already formatted input (0), changes needed (1) and errors (2). |
| `--diff` | Incomplete | Print a unified formatting patch without changing the file. Required edits normally give exit status 1. |
| `--line-length LENGTH` | Incomplete | Preserve the Unicode width and default of 88. The formatter can exceed the preferred width. Supply the actual integer bounds for both releases. |
| `--extension EXTENSION` | Incomplete | Give a colon-separated mapping, identify the Python language token and qualify the additional Markdown token by release. |
| `--stdin-filename PATH` | Incomplete | Show how to format piped input as a named stub. The supplied filename provides context and output is written to stdout. |

## Version differences and manual-only coverage

- **Python targets.** The 0.11.13 settings declaration lists tokens through `py313`, but that release’s CLI help and both commands accept `py314`. Its lint command warns that Python 3.14 support is under development. In 0.17.6 both commands also accept `py315`. The setting fallback changed from `py39` to `py311`. A discovered project can supply a different minimum through `requires-python`. [0.11.13 CLI](https://github.com/astral-sh/ruff/blob/0.11.13/docs/configuration.md#full-command-line-interface) · [0.17.6 CLI](https://github.com/astral-sh/ruff/blob/0.17.6/docs/configuration.md#full-command-line-interface)
- **Line width.** The accepted ranges are 1–320 in 0.11.13 and 1–65,535 in 0.17.6. The parser and boundary fixtures establish both ceilings. Width uses Unicode character widths and the formatter treats the preference as a wrapping target. [0.11.13 width parser](https://github.com/astral-sh/ruff/blob/0.11.13/crates/ruff_linter/src/line_width.rs) · [0.17.6 width parser](https://github.com/astral-sh/ruff/blob/0.17.6/crates/ruff_linter/src/line_width.rs)
- **Extension languages.** CLI help lists `python`, `pyi` and `ipynb` in both releases. The 0.17.6 parser also accepts `md` and the formatter rewrites Python code blocks in files mapped to it. The 0.11.13 parser rejects that token. Both reject `py` as a mapping language. [0.11.13 extension parser](https://github.com/astral-sh/ruff/blob/0.11.13/crates/ruff_linter/src/settings/types.rs) · [0.17.6 extension parser](https://github.com/astral-sh/ruff/blob/0.17.6/crates/ruff_linter/src/settings/types.rs)
- **Lint selection.** Codes and code prefixes work in both releases. Ruff 0.17.6 also documents names and categories in preview mode. For example, `--preview --select unused-import` worked in 0.17.6. The code `F401` worked in both releases. [0.17.6 rule selection](https://github.com/astral-sh/ruff/blob/0.17.6/docs/linter.md#rule-selection)

Documented options outside the curated selection include lint watch mode, per-file ignores, fixability filters, and `--exit-non-zero-on-fix`. The formatter also supports a source range. Both commands expose force-exclude, additional exclusion patterns and cache-directory selection. Some are mentioned in Details to explain how a bundled flag behaves. Discovered help remains a separate roadmap item.

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

Each Ubuntu target opened both menus in real Bash/tmux sessions with discovery disabled. At 210×100 every highlighted option, summary and complete Details pane was checked. The first rendering pass showed that the formatter’s stdin example had been dropped from Details. Rewording it as a direct instruction restored the filename and the literal stdin operand. The final pass verified all 30 entries. Cancelling restored the original pending line and cursor. Selecting `--select` or `--line-length` inserted the literal option before an existing filename. A shell stub recorded unexpected Ruff execution and remained unused.

At 60×16 a search for “unfixable violation” found the lint diff exit rule. A search for “through 65535” found the formatter’s version-specific width. In each case the qualification was reachable by scrolling. The permanent lint regression checks cancellation and insertion at that size. [Rendered terminal regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The 33 focused checks per target covered profile declarations, midline insertion, rendered terminal behavior, version-specific target and width expectations, extension mappings and numerical-inventory reconciliation. The 37 refreshed fingerprints cover the two profile files, their command and category descriptions, the 30 entries and the corrected independent numerical fixture. [Numerical regression](../tests/test_numerical_migration.py) · [Source-derived expectations](../tests/fixtures/value-semantics/migration-evidence.json) · [Inventory review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 33 / 0 / 0 | 1,344 / 0 / 1 | 486.144 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 33 / 0 / 0 | 1,344 / 0 / 1 | 549.045 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 33 / 0 / 0 | 1,344 / 0 / 1 | 487.288 s |

Each full run included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. Each Linux target skipped the Windows-only probe.
