# Bun run option audit

First recorded 2026-11-22. Counts and observations below describe the original bundled selections. See the [expanded inventory and verification](bun-run-manual-coverage.md) for the later manual comparison.

The [bundled menu](../profiles/bun-run.json) contained eight flags for `bun run`. Place Bun flags before the script or executable name. Later arguments belong to the target, so `bun run --silent task` and `bun run task --silent` have different effects. The menu retains this positional boundary and all eight literal spellings.

## Sources and versions

The upstream runtime reference displayed Bun 1.4.5 at review. The Bun 1.2.5 parser is the pinned source for the profile’s three value-taking flags. Its run-command implementation also shows where Bun handles an unsuccessful target lookup. Both versions were exercised separately from the menu. [Runtime reference](https://bun.sh/docs/runtime) · [Watch and hot reload](https://bun.sh/docs/runtime/watch-mode) · [Environment files](https://bun.com/docs/runtime/environment-variables) · [Bun 1.2.5 CLI parser](https://github.com/oven-sh/bun/blob/bun-v1.2.5/src/cli.zig) · [Bun 1.2.5 run-command implementation](https://github.com/oven-sh/bun/blob/bun-v1.2.5/src/cli/run_command.zig)

Ubuntu’s Noble and Resolute amd64 package contents indexes returned no path ending in `bin/bun`. Requests for `bun(1)` and `bun-run(1)` returned HTTP 404 on both release-specific manpage sites. The upstream references supply the flag semantics for both Ubuntu targets. [Ubuntu 24.04 contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fbun&mode=path&suite=noble&arch=amd64) · [Ubuntu 26.04 contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fbun&mode=path&suite=resolute&arch=amd64) · [Ubuntu manpage index](https://manpages.ubuntu.com/)

## Disposition of the eight entries

Bun flags end at the target name. `--silent` hides the echoed script command while preserving its output. With `--if-present`, a missing script name can still resolve to a file or executable and propagate its failure. The two tested binaries required special care with relative working directories on watch restart.

## Executable checks

Each offline target ran both upstream Linux x64 binaries on disposable files. The package archives were checked against their published SHA-512 integrity values and extracted into private sandbox storage. The package-script fixtures used shell builtins, local files and a local Node interpreter stub. [Bun 1.2.5 package metadata](https://registry.npmjs.org/@oven/bun-linux-x64/1.2.5) · [Bun 1.4.5 package metadata](https://registry.npmjs.org/@oven/bun-linux-x64/1.4.5)

| Fixture | Observed on Bun 1.2.5 and 1.4.5 |
| --- | --- |
| Watch versus hot reload | Editing an imported file reran the entry point. With an absolute working directory a counter on `globalThis` restarted at 1 under `--watch` and advanced to 2 under `--hot`. |
| Working directory on restart | The manual describes an absolute path. Both versions accepted `--cwd app` on the initial run. With no nested `app/app`, the first watch restart failed with a directory lookup error and exit status 1. Repeating the same edit with an absolute directory succeeded. |
| Package script and runtime | A package script took precedence over a same-named file. Silent mode suppressed the echoed command while preserving script output on both streams. A package executable with an env-node shebang selected the Node stub normally and reported the Bun version with `--bun`. |
| Missing and failing targets | A missing name exited 1 normally and 0 with `--if-present`. An existing script that exited 7 still returned 7 with the flag. On Ubuntu 26.04 both binaries also returned 0 for missing explicitly named relative and absolute files. |
| Startup files and arguments | A plain run loaded the project’s `.env`. With two explicit env files, the automatic file’s variable was absent, unique keys from both files were present and the later value won for a shared key. Two preload modules ran in order before the entry point. A trailing `--watch` reached the program as a literal argument. |

## Rendered menu and sandbox suites

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Minimum-size terminal regression](../tests/test_expansion_terminal.py)

| Ubuntu | Python | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | ---: |
| 24.04.5 | 3.10.20 | 20 / 0 / 0 | 1,348 / 0 / 1 | 566.002 s |
| 24.04.5 | 3.12.3 | 20 / 0 / 0 | 1,348 / 0 / 1 | 500.620 s |
| 26.04.1 | 3.14.4 | 20 / 0 / 0 | 1,348 / 0 / 1 | 500.362 s |

Each Linux suite skipped the Windows-specific probe.
