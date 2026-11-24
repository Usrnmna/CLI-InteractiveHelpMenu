# Verification of the six development-tool families

The batch covers 18 command menus. Each family inventory records its own manuals, release-specific parser declarations and native observations. The compatibility matrix exercises the Interactive Help Menu with those profiles bundled together.

| Family | Original rows | Revisited rows |
| --- | ---: | ---: |
| [uv](uv-manual-coverage.md) | 56 | 454 |
| [Ruff](ruff-manual-coverage.md) | 30 | 92 |
| [pytest](pytest-manual-coverage.md) | 18 | 121 |
| [Go](go-manual-coverage.md) | 44 | 171 |
| [.NET](dotnet-manual-coverage.md) | 76 | 242 |
| [Bun](bun-run-manual-coverage.md) | 8 | 121 |

## Menu checks

The [terminal tests](../tests/test_syntax_terminal.py) start real Bash sessions inside tmux. With discovery disabled, executable stubs detect attempts to run the pending command. The wide walks compare the highlighted label, summary, formatted Details and line count on every row. At 60×16 each command has a search, a consequential Details check, an Escape round trip with the original cursor and a literal insertion before an existing suffix. The Bun test also opens help from inside the pending script arguments and checks the refusal to edit that region.

## Reproduction

Use the [offline runner](development.md#isolated-local-debugging) with one separate `--include` for each required untracked file. The [preceding batch](iproute2-systemd-openssl-verification.md#reproducing-the-batch) and the [packaged fixture setup](yq-eval-manual-coverage.md#reproduction) specify the isolated environment for the full suite. Run the six menu tests in `test_syntax_terminal.SyntaxScreenTests`, the family declaration tests, generated routes, historical captures, literal insertion and strict numerical checks before starting the three full runs against the integrated profiles.

## Compatibility results

| Target | Ubuntu | Python | Focused pass / fail / skip | Full pass / fail / skip | Full unittest time |
| --- | --- | --- | ---: | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 96 / 0 / 0 | 1,563 / 0 / 1 | 1275.003 s |
| `noble310` | 24.04.5 | 3.10.20 | 96 / 0 / 0 | 1,563 / 0 / 1 | 1448.783 s |
| `noble312` | 24.04.5 | 3.12.3 | 96 / 0 / 0 | 1,563 / 0 / 1 | 1289.515 s |

The focused column counts distinct unittest methods per target. It includes 84 family, shared and route tests, six new terminal walks and six original minimum-size regressions. An initial terminal run exposed three assertions that expected long option names to fit in a 60-column screen. The corrected assertions compare the displayed label at the available cell width and still check the full inserted spelling. All six terminal walks passed on each target. Seven already-counted focused tests then passed again after correcting the release scope shown for two Bun preload aliases and Ruff’s optional suppression reason.

Each target inspected 1,201 rows across 18 menus, with zero pending command executions. The full runs passed shell syntax, numerical checks, both profile/driver checks and unittest discovery. The only skip on each target was the Windows-specific probe. The strict numerical gate independently verified 4,233 required records. The three full runs used the same integrated source and target-specific packaged fixtures. Times in the table cover unittest discovery and execution, excluding snapshot preparation and preflight.
