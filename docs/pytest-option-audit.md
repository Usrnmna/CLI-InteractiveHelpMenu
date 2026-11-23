# pytest option audit

The bundled menu contains 18 entries, including separate short and long spellings. The audit covers core pytest on Ubuntu 24.04 and 26.04. Plugins can extend the installed command. The menu preserves the original option order, required operands and literal spellings. [Bundled profile](../profiles/pytest.json)

## Sources and scope

| Source | Version | Evidence |
| --- | --- | --- |
| [Upstream command-line reference](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst#command-line-flags) | pytest 9.2.0 | Reference for all 18 spellings, operands, aliases and defaults. [Upstream release](https://pypi.org/project/pytest/9.2.0/) |
| [Ubuntu 24.04 pytest(1)](https://manpages.ubuntu.com/manpages/noble/man1/pytest.1.html) | python3-pytest 7.4.4-1 | Invocation examples for name and marker selection, plugins, durations and verbosity. |
| [Ubuntu 26.04 pytest(1)](https://manpages.ubuntu.com/manpages/resolute/man1/pytest.1.html) | python3-pytest 9.0.2-4 | Also shows marker keyword arguments and collecting node IDs with quiet output. |
| [pytest 8.3 reference](https://docs.pytest.org/en/8.3.x/reference/reference.html#command-line-flags) and [8.3.5 implementation](https://github.com/pytest-dev/pytest/tree/8.3.5/src/_pytest) | 8.3.5 | Reference release for the structured value guidance. The tagged parsers, session and reporters resolve behavior omitted from the option table. |

The Ubuntu pages are invocation guides. Where they omit a flag or a boundary case, the upstream reference and the implementation for the corresponding package version supply the evidence. Each tested release also listed all 18 spellings in its own help.

## Entry decisions

The disposition describes the previous menu text and structured guidance.

| Entry | Original disposition | What the menu now explains |
| --- | --- | --- |
| `-k EXPRESSION` | Redundant | Replaces parser boilerplate with case-insensitive substring matching, including parent names, parameter IDs and markers. Gives a quoted boolean example. |
| `-m MARKEXPR` | Incomplete | Uses exact, case-sensitive marker names. Gives a quoted expression and identifies which Ubuntu release supports matching a marker's keyword arguments. |
| `-x` | Incomplete | A failure or an error can end the session. The limit equals `--maxfail=1`. |
| `--exitfirst` | Incomplete | Same limit as `-x`, including collection and fixture errors. |
| `--maxfail NUM` | Inaccurate | Counts failures and errors. Zero disables the limit. Corrects the structured lower bound for the signed parser. |
| `-q` | Incomplete | Reduces terminal output. Repetition reduces it further. With collection alone it lists test node IDs. |
| `--quiet` | Incomplete | The long spelling has the same effect. Details give the compact repeated spelling `-qq`. |
| `-v` | Incomplete | Displays the individual test names and outcomes. Repeating it can expand assertion comparisons. |
| `--verbose` | Incomplete | The long spelling enables the same individual results and Details explain `-vv`. |
| `--collect-only` | Incomplete | Skips test bodies. Test modules and conftest files can still execute code at import, and collection hooks still run. |
| `--tb STYLE` | Sufficient | Keeps the six accepted styles. Gives the default and explains how to suppress a traceback while retaining the failure. |
| `--capture METHOD` | Incomplete | Distinguishes file descriptors, Python streams, live Python output with `tee-sys`, and disabled capture. The default `fd` also captures writes from subprocesses that inherit stdout or stderr. |
| `--rootdir DIR` | Incomplete | Anchors test node IDs and the default cache. Working directory, import path and choice of test operands are separate. |
| `-c FILE` | Incomplete | An explicit file replaces config discovery. Its parent supplies the root unless overridden. |
| `-p NAME` | Sufficient | Keeps both operations and gives the syntax for loading a plugin early, blocking one with `no:NAME`, and naming more than one. |
| `--basetemp DIR` | Incomplete | On first use pytest clears and recreates the supplied directory. The summary makes this visible before selection. |
| `--durations N` | Inaccurate | Counts individual setup, call and teardown records. Zero selects all records before the separate seconds threshold. Corrects the structured integer range. |
| `--junit-xml PATH` | Incomplete | Takes a report filename and writes JUnit XML alongside the terminal results. |

## Material distinctions and version boundaries

- **Name and marker filters.** A substring such as `FAST` can match a lowercase test name with `-k`. With `-m`, the marker name must match exactly. The 7.4.4 marker parser rejects `"slow(phase=1)"`. The 8.3.5, 9.0.2 and 9.2.0 parsers match the named keyword value. [7.4.4 selector](https://github.com/pytest-dev/pytest/blob/7.4.4/src/_pytest/mark/__init__.py) · [8.3.5 selector](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/mark/__init__.py) · [9.0.2 selector](https://github.com/pytest-dev/pytest/blob/9.0.2/src/_pytest/mark/__init__.py)
- **Timing reports.** `--durations=0 --durations-min=0` shows all measured phases. At ordinary verbosity the default threshold is 0.005 seconds. In 7.4.4 and 8.3.5, `-vv` also bypasses an explicit threshold. In 9.0.2 and 9.2.0, `-vv` lowers the default to zero and an explicit threshold still applies. [7.4.4 reporter](https://github.com/pytest-dev/pytest/blob/7.4.4/src/_pytest/runner.py) · [8.3.5 reporter](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/runner.py) · [9.0.2 reporter](https://github.com/pytest-dev/pytest/blob/9.0.2/src/_pytest/runner.py) · [9.2.0 reporter](https://github.com/pytest-dev/pytest/blob/9.2.0/src/_pytest/runner.py)
- **Signed counts.** The manuals document positive counts and zero. The tested implementations also accept negative integers. A negative failure limit stops at the first failure or error. A negative duration count drops that many records from the shortest end of the sorted list before threshold filtering. The basic descriptions use the documented forms. The versioned value guidance records the parser behavior. [8.3.5 session and failure limit](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/main.py) · [8.3.5 duration handling](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/runner.py)
- **Directory operands.** Cleanup occurs when the temporary base is requested. The option validator rejects the current directory and its ancestors. For configuration, `-c` selects a file and `--rootdir` overrides the root used for reporting and cache placement. An explicit test path controls what to collect. [Temporary base implementation](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/tmpdir.py) · [Base path validation](https://github.com/pytest-dev/pytest/blob/8.3.5/src/_pytest/main.py) · [Root and configuration rules](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/customize.rst)
- **Manual-only coverage.** The full CLI also supports running only previous failures (`--lf`) or running those tests first (`--ff`), listing fixtures (`--fixtures`), showing local variables (`--showlocals`), choosing an import mode (`--import-mode`) and setting the reporting threshold (`--durations-min`). Details cross-reference the threshold and the `-s` capture shorthand. The Ubuntu 26.04 guide also shows how to read arguments from a file with `pytest @tests_to_run.txt`, a syntax introduced in pytest 8.2. These remain outside the 18 selectable entries. [Ubuntu 26.04 invocation guide](https://manpages.ubuntu.com/manpages/resolute/man1/pytest.1.html) · [Upstream command-line flags](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst#command-line-flags)

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

On each target a real Bash/tmux session displayed all 18 rows at 210×100. The checks covered each highlighted label, summary, authored explanation and complete generated Details pane. Escape restored the pending line and cursor. Selecting `-m` inserted that literal before an existing test path. At 60×16, searching for “dedicated directory” found `--basetemp DIR`. Scrolling reached the cleanup warning, cancellation restored the original edit, and selection allowed a directory value to be typed before the existing filename. A shell stub recorded no execution during either interaction. [Minimum-size regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

Each target passed 22 focused checks covering profile contracts, literal insertion, the narrow terminal interaction, numerical presentation and inventory reconciliation. The 22 reviewed fingerprints cover the profile file, its description and category, all 18 options, and the independent migration fixture. [Duration evidence](../tests/fixtures/value-semantics/migration-evidence.json) · [Numerical regression](../tests/test_numerical_migration.py) · [Inventory review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 22 / 0 / 0 | 1,345 / 0 / 1 | 490.873 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 22 / 0 / 0 | 1,345 / 0 / 1 | 554.297 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 22 / 0 / 0 | 1,345 / 0 / 1 | 490.939 s |

All three offline runs included the untracked audit documents and passed the shell syntax, numerical coverage, profile validation and unittest checks. Each Linux run skipped the Windows-only probe.
