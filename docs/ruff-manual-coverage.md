# Ruff check and format manual coverage

The lint menu grew from 16 to 60 spellings and the formatter from 14 to 32. Each option and short alias has an insertion, including the documented negative forms. The versioned declaration tables separately record required, optional and absent operands. [Lint profile](../profiles/ruff-check.json) · [Lint declarations](../tests/fixtures/ruff/ruff-check-declarations.tsv) · [Format profile](../profiles/ruff-format.json) · [Format declarations](../tests/fixtures/ruff/ruff-format-declarations.tsv)

| Version | Lint declarations / selectable spellings | Format declarations / selectable spellings |
| --- | ---: | ---: |
| 0.11.13 | 50 / 58 | 24 / 29 |
| 0.17.6 | 52 / 60 | 27 / 32 |

Declarations in this table count independently registered or supplementary forms. For example, the formatter’s hidden alias for its exit-on-edit option has its own declaration. Both releases accept it as an alias.

## Sources and release differences

The inventory combines each wheel’s fixed `check --help` and `format --help` with the generated manual and tagged Clap declarations. The parser exposes hidden inverse flags, the deprecated lint spellings `--extend-ignore` and `--extend-unfixable`, lint width and dummy-variable settings, and the formatter alias `--exit-non-zero-on-fix`. Ubuntu’s Noble and Resolute package contents checks found no distribution Ruff executable or release man page. The two versions are upstream clients. [0.11.13 CLI](https://github.com/astral-sh/ruff/blob/0.11.13/docs/configuration.md) · [0.17.6 CLI](https://github.com/astral-sh/ruff/blob/0.17.6/docs/configuration.md) · [Older parser](https://github.com/astral-sh/ruff/blob/0.11.13/crates/ruff/src/args.rs) · [Newer parser](https://github.com/astral-sh/ruff/blob/0.17.6/crates/ruff/src/args.rs) · [Ubuntu checks and original wheel probes](ruff-option-audit.md#sources)

- `check --add-noqa` can rewrite source even without `--fix`. It takes no argument in 0.11.13. In 0.17.6 it accepts an optional attached reason, and `--add-ignore[=REASON]` adds Ruff-specific comments. The menu inserts the newer equals form. Its Details tell 0.11.13 users to remove the equals sign for the bare switch.
- `format --exit-non-zero-on-format` can write a file and then return failure because it changed. `format --check` reports needed edits without writing. `--range` takes one file and an exclusive end position. Notebook ranges are unsupported.
- The 0.17.6 formatter accepts `--extend-exclude` and `--output-format` for check reports. Both commands in that release accept `--color`. An inline `--config` setting overrides config files, and a dedicated flag overrides the inline setting. `--preview` affects unstable lint rules and fixes on one command and unstable formatting on the other.

A disposable host fixture started each run with a single unused `import os`. Both binaries inserted `# noqa: F401` for the bare switch. With `--add-noqa=reviewed`, 0.11.13 exited 2 and preserved the file. Version 0.17.6 exited 0 and wrote `# noqa: F401 reviewed`. The real clients ran in the offline host sandbox, separately from the menu stubs.

The global configuration and logging options accepted by each leaf are included. Commands such as `ruff rule`, the language server, settings keys, rule codes and positional files remain outside these flag inventories. The original captures retain their original versions. The expanded tests compare each profile to its independent declaration table. [Declaration tests](../tests/test_devtools_manual_inventories.py) · [Rendered menus and full suites](devtools-batch-verification.md#compatibility-results)
