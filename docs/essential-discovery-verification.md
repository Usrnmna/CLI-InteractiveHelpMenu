# Essential discovery verification

The [route inventory](essential-discovery-audit.md) lists the 46 paths in matrix order. The [media](essential-media.md), [Git and Docker](essential-git-docker.md), [package manager](essential-packages.md) and [utility](essential-utilities.md) audits identify the source editions, requests, option counts and known exclusions.

## Terminal evidence

Each Bash session has a private tmux socket, home, cache, program stubs and a disposable runtime with an empty bundled-profile directory. The test runs the normal `--discover COMMAND --refresh` entry point and checks every generated spelling and operand count against the independent inventory before opening the menu. It checks the actual terminal title and generated description, visits every row, and compares the highlighted declaration, rendered summary and complete Details against terminal cells. The stubs accept only the exact arguments for the program's recorded documentation and manual requests. A different invocation writes a marker that fails the check. Reopening a successful menu must use the cache. Root npm's empty result must retain the command line and cursor and report its diagnostic. [Terminal harness](../tests/test_essential_terminal.py)

At 60×16, the checks filter from an unfiltered menu, scroll to the last Details line when needed, cancel and inspect both Readline state variables. They reopen the menu and accept the selection before an existing quoted suffix. The child-boundary cases include Docker, npm and uv. At the pip root a completed separator also prevents subcommand discovery. Tests of full captured replies and tests of small historical excerpts use separate expectations. These replays verify the menu on three Ubuntu/Python combinations independently of which clients happen to be installed on each runner.

A separate Resolute sandbox invoked the installed programs through discovery with a fresh private cache and their real manual pages. FFmpeg returned 176 spellings and FFprobe returned 496. Both matched the release-specific arity map, reported both expected sources and returned zero source warnings. This fixed-documentation check opened no media.

## Reproduction

Use the [offline runner](development.md#isolated-local-debugging) from the repository root. Pass one `--include` per untracked runtime module, test, audit and input. Inside each target, run the four family modules and `test_essential_terminal` with `PYTHONPATH=tests python3 -B -m unittest -v`. The same snapshot can run discovery, corpus, parser-association, presentation, editing and cache regressions. Run the strict numerical check with `python3 -B scripts/check_numerical_coverage.py --mode strict --summary`. For the full command, supply the same target-specific [packaged fixtures](remaining-bundled-verification.md#reproduction) used by the bundled audits, then run `bash tests/run.sh`. The CI link check uses Lychee 0.24.2 with the repository configuration.

## Compatibility results

The focused shared run covered 295 tests per target, including discovery routing and caching, historical help, argument ownership, presentation, literal editing and package installation. The terminal module exercised 103 cases per target across 46 command paths. Separate runs revisited the three full utility menus affected by the last alias changes and the fourteen Git menus affected by revised summaries across the two releases.

The numerical review compared source observations with the pre-audit tree. The changes affected captured and synthetic help, and the census picked up five new reader modules. Two former observations came from examples or subordinate prose on the `git show` and `esptool.py write_flash` paths. The review also checked changes in optional argument handling against unrelated fzf and journalctl captures before updating the fingerprints. All three targets passed the strict gate for 4,426 required records.

| Target | Ubuntu / Python | Focused shared pass / fail / skip | Terminal pass / fail / skip | Repeated focused checks after final edits |
| --- | --- | --- | --- | --- |
| `host` | 26.04.1 / 3.14.4 | 295 / 0 / 0 in 33.376 s | 103 / 0 / 0 in 496.397 s | 13 parser checks in 1.852 s, 3 utility menus in 20.760 s, 14 Git menus in 69.003 s |
| `noble310` | 24.04.5 / 3.10.20 | 295 / 0 / 0 in 44.517 s | 103 / 0 / 0 in 520.802 s | 13 parser checks in 3.980 s, 3 utility menus in 24.061 s, 14 Git menus in 78.415 s |
| `noble312` | 24.04.5 / 3.12.3 | 295 / 0 / 0 in 35.770 s | 103 / 0 / 0 in 491.132 s | 13 parser checks in 2.154 s, 3 utility menus in 21.164 s, 14 Git menus in 71.211 s |

All repeated checks passed with zero skips and zero failures. The terminal checks recorded zero unexpected invocations. The large-screen checks included all 3,541 rows in the complete Resolute or vendor set and the additional release-specific and historical cases.

An existing terminal test in the first full matrix caught a regression in the captured `aws s3 cp --exclude` declaration. The new syntax text appeared ahead of the manual definition, which caused both the opening fragment and its complete sentence to appear in Details. The corrected merge keeps the complete definition first and the bracketed syntax alongside it. Reverification included that seven-family terminal regression, the package and merge checks, and the affected complete npm menus. All 64 focused checks passed on each target with zero failures and skips in 35.035 s on `host`, 38.108 s on `noble310` and 34.291 s on `noble312`. This regression in a shared reader gives no additional tier credit to AWS.

## Full offline suite

| Target | Initial pass / fail / skip | Initial duration | Corrected pass / fail / skip | Corrected duration |
| --- | ---: | ---: | ---: | ---: |
| `host` | 1,707 / 1 / 1 | 1891.649 s | 1,708 / 0 / 1 | 1895.805 s |
| `noble310` | 1,707 / 1 / 1 | 2109.077 s | 1,708 / 0 / 1 | 2108.062 s |
| `noble312` | 1,707 / 1 / 1 | 1898.077 s | 1,708 / 0 / 1 | 1901.187 s |

Six full suites ran, one initial and one corrected run per target. Each used the offline packaged fixtures and included the shell syntax checks, numerical coverage, both collection checks and unittest discovery. Times in the table are unittest durations. Each run skipped the Windows probe-limitation case on Linux. The discovery terminal tests made no network requests. A SHA-256 comparison confirmed the 720 version-controlled and new non-Markdown files matched the corrected snapshot inputs after the runs.

Lychee 0.24.2 checked the final maintained Markdown tree with the CI configuration, including local heading fragments and the configured cache of successful external responses. All 2,871 link occurrences passed across 1,572 unique targets, with zero errors and zero timeouts.
