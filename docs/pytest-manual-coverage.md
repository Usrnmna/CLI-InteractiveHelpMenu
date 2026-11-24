# pytest core manual coverage

The menu grew from 18 to 121 selectable spellings. It covers built-in plugins shipped with pytest, including capture, cache, logging, doctest, debugging and JUnit reporting. Positional paths, Python package names, node IDs, configuration keys and third-party switches have separate grammars. For example, `pytest tests/test_cli.py::test_args --collect-only` selects tests by node ID and reports collection. A plugin such as pytest-cov can add its own flags to installed help. [Profile](../profiles/pytest.json) · [Versioned core declarations](../tests/fixtures/pytest/pytest-declarations.tsv)

| Release examined | Registered option groups of spellings | Spellings |
| --- | ---: | ---: |
| Noble package 7.4.4-1 | 85 | 112 |
| Upstream 8.3.5, historical value reference | 88 | 115 |
| Resolute package 9.0.2-4 | 91 | 119 |
| Upstream 9.2.0 | 92 | 121 |

## Sources and reconciliation

The Ubuntu guides document invocation and examples. For complete alias and operand coverage the audit read the registered argparse actions from each of the four versions with third-party plugin autoload disabled, outside the project and with conftest loading disabled. Registration retains short aliases and compatibility forms suppressed by the help formatter. Each spelling in the table has an independent release and arity record. [Noble pytest(1)](https://manpages.ubuntu.com/manpages/noble/man1/pytest.1.html) · [Resolute pytest(1)](https://manpages.ubuntu.com/manpages/resolute/man1/pytest.1.html) · [9.2.0 command-line reference](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst#command-line-flags) · [Original package sources and executable evidence](pytest-option-audit.md#sources-and-scope)

- `--strict` is the deprecated marker-checking alias in 7.4.4 and 8.3.5. In the 9.x releases it enables the broader strict setting. The new `--strict-markers` row makes marker-only behavior discoverable. [7.4.4 registrations](https://github.com/pytest-dev/pytest/blob/7.4.4/src/_pytest/main.py) · [9.2.0 registrations](https://github.com/pytest-dev/pytest/blob/9.2.0/src/_pytest/main.py)
- `--lf` uses saved failures and normally runs everything when that cache is empty. `--lfnf none` changes the empty-cache result to a successful exit without running tests. `--ff` changes ordering and still runs the remaining tests. `--setup-plan`, `--setup-only` and `--setup-show` distinguish planning from fixture execution and execution of test bodies.
- `--debug` accepts an optional filename and truncates its destination. `--cache-show` accepts an optional glob and exits before collection. `--pastebin` can send report content to an external service. The menu describes that side effect. The rendering tests use a stub.
- `--disable-plugin-autoload` appears in the two 9.x inventories. An explicit `-p` or `PYTEST_PLUGINS` request still works. `--max-warnings` and the long spelling `--report-chars` appear in 9.2.0. The former can fail an otherwise passing run.

The original captures, node-ID and marker fixtures, and duration-threshold findings remain available in the first-pass audit. The new tests compare membership and operand requirements and check that options can follow a quoted node ID. [Regression coverage](../tests/test_devtools_manual_inventories.py) · [Rendered menu and full suites](devtools-batch-verification.md#compatibility-results)
