# PlatformIO run and device monitor manual coverage

| Menu | Original rows | Added | Final rows | Distinct effects | Additional aliases |
| --- | ---: | ---: | ---: | ---: | ---: |
| [pio run](../profiles/pio-run.json) | 17 | 7 | 24 | 14 | 10 |
| [platformio run](../profiles/platformio-run.json) | 17 | 7 | 24 | 14 | 10 |
| [pio device monitor](../profiles/pio-device-monitor.json) | 17 | 8 | 25 | 19 | 6 |
| [platformio device monitor](../profiles/platformio-device-monitor.json) | 17 | 8 | 25 | 19 | 6 |

Both executable names use the same CLI entry point. Each menu preserves its original order, literal spellings and operand metadata. The union contains 98 selectable rows across four menus, up from 68.

## Sources and release differences

| Source | Options and release scope |
| --- | --- |
| [Ubuntu 24.04 platformio(1)](https://manpages.ubuntu.com/manpages/noble/man1/platformio.1.html), [package file list](https://packages.ubuntu.com/noble/all/platformio/filelist) and [package](https://packages.ubuntu.com/noble/platformio) | Noble ships 4.3.4-3. Both `pio(1)` and `platformio(1)` lead to the combined reference. The packaged Click declarations for the two leaves match their upstream 4.3.4 counterparts. [Run inventory](../tests/fixtures/operations-manual/platformio-4.3.4-run.txt) and [monitor inventory](../tests/fixtures/operations-manual/platformio-4.3.4-device-monitor.txt) |
| [Ubuntu package index](https://packages.ubuntu.com/platformio) | The distribution index has no PlatformIO package for 26.04 Resolute. Both release-specific manpage lookups (pio(1) and platformio(1)) returned HTTP 404. Vendor-installed Core has its own release and option set. |
| [Core 6.1.18 run parser](https://github.com/platformio/platformio-core/blob/v6.1.18/platformio/run/cli.py), [monitor parser](https://github.com/platformio/platformio-core/blob/v6.1.18/platformio/device/monitor/command.py) and [retained native captures](../tests/fixtures/help/expansion-development-captured.json) | Fixed help for both executable names, recorded on Ubuntu 24.04 under WSL. [Run inventory](../tests/fixtures/operations-manual/platformio-6.1.18-run.txt) and [monitor inventory](../tests/fixtures/operations-manual/platformio-6.1.18-device-monitor.txt) |
| [Upstream run reference](https://docs.platformio.org/en/stable/core/userguide/cmd_run.html), [monitor reference](https://docs.platformio.org/en/stable/core/userguide/device/cmd_monitor.html), [6.2.0 run parser](https://github.com/platformio/platformio-core/blob/v6.2.0/platformio/run/cli.py) and [monitor parser](https://github.com/platformio/platformio-core/blob/v6.2.0/platformio/device/monitor/command.py) | Core 6.2.0. [Run inventory](../tests/fixtures/operations-manual/platformio-6.2.0-run.txt) and [monitor inventory](../tests/fixtures/operations-manual/platformio-6.2.0-device-monitor.txt) |

The inventories were extracted from each leaf's Click declarations plus the inherited `-h` and `--help` names. An inventory line groups aliases for a single effect and gives its operand count. The archived handwritten `expansion-*.txt` excerpts retain their original role as small discovery fixtures.

- Noble 4.3.4 has 18 run spellings. Core 6.1.18 adds `--monitor-port`, `--list-targets`, `-a` and `--program-arg`. Core 6.2.0 adds `-p` and `--port` to set a shared endpoint. Explicit `--upload-port` or `--monitor-port` takes precedence for its operation. These options select endpoints. The target determines whether upload or monitoring takes place.
- Noble has 24 monitor spellings. Both reviewed 6.x releases add `--no-reconnect` for an established connection that fails. The Noble wrapper builds filter arguments from project settings and the command line. The newer monitor selects CLI filters when present and otherwise uses the project setting. [Noble monitor helper](https://github.com/platformio/platformio-core/blob/v4.3.4/platformio/commands/device/helpers.py)
- Both manuals contain a three-dash `---quiet` heading and an old sample showing 29 as the default exit character. The parsers declare `--quiet` and a default exit code of 3 (Ctrl+C). Code 29 (Ctrl+]) can be requested explicitly. The menu prefix defaults to 20 (Ctrl+T) and must differ from the exit key. Both operands are documented as decimal ASCII codes. Core 6.2.0 parses integers and converts them with Python’s chr() when constructing the terminal. [Noble monitor parser](https://github.com/platformio/platformio-core/blob/v4.3.4/platformio/commands/device/command.py) and [6.2.0 terminal](https://github.com/platformio/platformio-core/blob/v6.2.0/platformio/device/monitor/terminal.py)

## Disposition of original rows

| Original run spellings, on both executables | Disposition and resulting guidance |
| --- | --- |
| `-e`, `--environment`, `-t`, `--target` | Incomplete. Environments select project configurations. Repeat the switch for multiple selections. Targets select work within an environment, including build, upload and monitor. The project can supply default environments and targets. |
| `-d`, `--project-dir`, `-c`, `--project-conf` | Summaries sufficient. Details distinguish the project location and alternate configuration file, including quoted paths. |
| `-j`, `--jobs` | Incomplete across releases. The integer counts parallel build jobs. The newer parsers accept a default from `PLATFORMIO_RUN_JOBS`. Noble uses the CPU count directly. |
| `--upload-port`, `--list-targets` | Incomplete. An endpoint alone does not request an upload. Available targets are environment-specific and the listing flag is absent in Noble. |
| `-v`, `--verbose`, `-s`, `--silent` | Summaries sufficient. Details distinguish build diagnostics from suppression of progress messages. |
| `--disable-auto-clean` | Incomplete. Preserves existing build artifacts through automatic invalidation after configuration or layout changes. Explicit clean requests remain available. |

| Original monitor spellings, on both executables | Disposition and resulting guidance |
| --- | --- |
| `-p`, `--port`, `-b`, `--baud` | Detail was over-specific for the introductory paragraph. The menu explains quoted device patterns, project selection, serial signalling rate and the 9600 baud default. The structured entries retain backend and hardware qualifications. |
| `--parity`, `--rtscts`, `--xonxoff`, `--rts`, `--dtr` | Value contracts were sufficient. Details distinguish hardware and software flow control, parity modes, and the initial logical line state from voltage at the board. |
| `--echo`, `-f`, `--filter`, `--encoding` | Incomplete. Local echo can duplicate a device echo. Filters form a chain, and raw receive mode bypasses decoding and transformations on incoming device data. |
| `-e`, `--environment`, `-d`, `--project-dir` | Incomplete. The monitor loads serial settings from one environment in the chosen project, compared with repeatable build-environment selection. |

New run rows cover the dedicated monitor port, the shared port shortcut, repeatable Native program arguments and help. New monitor rows cover Enter line endings, raw receive mode, the two control keys, diagnostic suppression, reconnect behavior and help. Before the selected command, `-c` or `--caller` takes a caller ID and `-f` is the deprecated force switch. Inside `run`, `-c` selects the project configuration. Inside `device monitor`, `-f` selects a filter. [Root parser](https://github.com/platformio/platformio-core/blob/v6.2.0/platformio/__main__.py) Other project options, remote commands, monitor filter names and in-session keys are parameters or separate interfaces outside these four leaf menus.

## Verification

Core 6.2.0 fixed help ran under both executable names for both commands in a temporary environment with networking disabled and no host serial devices. The option names and operand counts matched the release declarations. Separate parsing accepted independent shared and dedicated port arguments, two Native program arguments including one containing a space, and a selected LF line ending. Click rejected `---quiet`. The probes stopped before the command callbacks, so they did not build, upload or open a port.

The [focused tests](../tests/test_operations_manual_inventories.py) compare both executable aliases with the independent release inventories and the four native 6.1.18 captures. The [combined verification report](remaining-bundled-verification.md) records real rendered-menu checks and full suite results on the three sandbox targets.
