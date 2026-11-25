# pytest option audit

First recorded 2026-11-22. Counts and observations below describe the original bundled selections. See the [expanded inventory and verification](pytest-manual-coverage.md) for the later manual comparison.

The bundled menu contained 18 entries, including separate short and long spellings. The audit covered core pytest on Ubuntu 24.04 and 26.04. Plugins can extend the installed command. The menu preserves the original option order, required operands and literal spellings. [Bundled profile](../profiles/pytest.json)

## Sources and scope

| Source | Version | Evidence |
| --- | --- | --- |
| [Upstream command-line reference](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst#command-line-flags) | pytest 9.2.0 | Reference for all 18 spellings, operands, aliases and defaults. [Upstream release](https://pypi.org/project/pytest/9.2.0/) |
| [Ubuntu 24.04 pytest(1)](https://manpages.ubuntu.com/manpages/noble/man1/pytest.1.html) | python3-pytest 7.4.4-1 | Invocation examples for name and marker selection, plugins, durations and verbosity. |
| [Ubuntu 26.04 pytest(1)](https://manpages.ubuntu.com/manpages/resolute/man1/pytest.1.html) | python3-pytest 9.0.2-4 | Also shows marker keyword arguments and collecting node IDs with quiet output. |
| [pytest 8.3 reference](https://docs.pytest.org/en/8.3.x/reference/reference.html#command-line-flags) and [8.3.5 implementation](https://github.com/pytest-dev/pytest/tree/8.3.5/src/_pytest) | 8.3.5 | Reference release for the structured value guidance. The tagged parsers, session and reporters resolve behavior omitted from the option table. |

The Ubuntu pages are invocation guides. Where they omit a flag or a boundary case, the upstream reference and the implementation for the corresponding package version supply the evidence. Each tested release also listed all 18 spellings in its own help.

## Entry decisions

The 18 core entries distinguished expression matching, test selection, output controls, configuration and temporary files. Third-party plugins can add options to an installed command.

## Material distinctions and version boundaries

`-k` matched names case-insensitively. Marker names under `-m` required exact casing. The 7.4.4 parser rejected a marker keyword-value expression accepted by 8.3.5, 9.0.2 and 9.2.0.

## Executable verification

The offline fixtures ran actual pytest against generated test modules, an explicit config, a private plugin and disposable directories. Automatic third-party plugin loading was disabled. Both Noble targets exercised the extracted Ubuntu 7.4.4 package and the upstream 8.3.5 and 9.2.0 wheels. The Resolute target exercised its system pytest 9.0.2 and the upstream 9.2.0 wheel. [Ubuntu 7.4.4 package](https://archive.ubuntu.com/ubuntu/pool/universe/p/pytest/python3-pytest_7.4.4-1_all.deb) · [8.3.5 release](https://pypi.org/project/pytest/8.3.5/) · [9.2.0 release](https://pypi.org/project/pytest/9.2.0/)

| Fixture | Observed result |
| --- | --- |
| Selection and collection | Collection created an import-time marker file and left the test-body marker absent. Case-insensitive name selection and exact marker selection returned the expected node IDs. The keyword marker expression returned one test on the newer releases and usage error 4 on 7.4.4. |
| Temporary base | An existing file survived a collection-only session. Requesting `tmp_path` removed that file and populated the recreated base. Passing the working directory as the base yielded usage error 4. |
| Failure limits and tracebacks | Both exit-first spellings, a limit of one, and a negative limit stopped at the first failure. Zero reported both failures. A fixture setup error also stopped the session. All six traceback styles preserved the failing outcome. |
| Capture and reports | On a passing test, `fd` hid both direct descriptor and Python writes. With `sys`, the descriptor write appeared live. Both writes appeared live under `tee-sys` and `no`. The generated JUnit XML contained the expected test case. |
| Config, plugins and output | With an explicit config the test observed the config directory as its root. An explicit root overrode it. The private plugin loaded by name, stayed disabled with its blocking spelling, and both quiet and verbose aliases completed the passing test. |
| Phase timing | A single test produced setup, call and teardown records at zero threshold. Counts of one and minus one selected one and two records respectively. An explicit high threshold with `-vv` reproduced the release difference above. |

## Rendered menu and sandbox suites

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Minimum-size regression](../tests/test_expansion_terminal.py) · [Duration evidence](../tests/fixtures/value-semantics/migration-evidence.json) · [Numerical regression](../tests/test_numerical_migration.py)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 22 / 0 / 0 | 1,345 / 0 / 1 | 490.873 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 22 / 0 / 0 | 1,345 / 0 / 1 | 554.297 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 22 / 0 / 0 | 1,345 / 0 / 1 | 490.939 s |

Each Linux suite skipped the Windows-specific probe.
