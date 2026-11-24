# Arduino CLI compile option coverage

The [compile profile](../profiles/arduino-cli-compile.json) grows from 15 to 50 selectable rows. The command has 29 local effects with 12 short aliases, plus nine inherited settings. The [independent inventory](../tests/fixtures/embedded-manual/arduino-compile-options.tsv) gives the scope, spellings and operand type of each effect. The inherited settings are also valid on the root side of the command.

## Sources and releases

The Ubuntu Noble package index has no `arduino-cli` package. The official package search lists the Ubuntu releases that do provide it. Resolute supplies `arduino-cli 1.2.2-1`, including a dedicated compile manual. The upstream 1.5 and 1.6 manuals agree with that command's public options, aliases and operand types. The generated manual shows the absent default of `--show-properties` as disabled. Fixed help and the tagged parser establish that specifying the flag without a value requests expanded properties. [Ubuntu package search](https://packages.ubuntu.com/search?keywords=arduino-cli&searchon=names&exact=1) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/arduino-cli-compile.1.html) · [1.5 command reference](https://arduino.github.io/arduino-cli/1.5/commands/arduino-cli_compile/) · [1.6 command reference](https://arduino.github.io/arduino-cli/1.6/commands/arduino-cli_compile/) · [property display parser](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/arguments/show_properties.go)

## Corrections to the original rows

| Original spellings | Disposition and change |
| --- | --- |
| `-b`, `--fqbn`, `--board-options` | Incomplete. A fully qualified board name selects the installed platform and board. Menu assignments use that board’s keys and values. The option accepts commas and repeated occurrences. |
| `--build-path`, `--output-dir` | Incomplete, with an inaccurate structured default for `--build-path`. The default build service uses `sketches/<hash>` under the configured build cache. Setting an export directory enables export. Paths containing spaces need one quoted shell argument. |
| `--build-property`, `--libraries` | Incomplete. Each build property is one whole assignment. A library collection directory differs from a single library root. An explicitly selected sketch profile excludes either library override. |
| `--warnings`, `--clean` | The summaries were sufficient. Retain warning levels, their platform recipe dependence and the clean-build cache consequence. |
| `--export-binaries` | Incomplete. Add `-e`, the configuration default and the default destination beneath the sketch's `build` directory. |
| `-j`, `--jobs` | Retain the verified signed integer and zero/CPU-core interpretation. Negative values can stall compilation. |
| `-v`, `--verbose` | Incomplete. Distinguish compiler output from CLI logs and document the conflict with quiet mode. |
| `--only-compilation-database` | Incomplete. The compilation database can be produced without compiling, but platform pre-build hooks can still run. |

The generated help describes a temporary build directory. Both tagged service implementations choose the configured build cache when the caller omits a build path. The default export directory uses the FQBN without its board options and changes the colons to dots. A compilation-database-only build suppresses binary export even when an output directory is given. [1.2.2 compile service](https://github.com/arduino/arduino-cli/blob/v1.2.2/commands/service_compile.go) · [1.6.0 compile service](https://github.com/arduino/arduino-cli/blob/v1.6.0/commands/service_compile.go)

## Added coverage and exclusions

- `--upload` / `-u` requests an upload **after a successful compilation**. Port, protocol, programmer and verification options configure that step. `--verify` alone never initiates an upload. The port may also identify the board during target selection. [Compile and upload flow](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/compile/compile.go) · [port selection](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/arguments/port.go)
- Sketch profiles, preprocessing, debugging, quiet output, property display, discovering ports, signing and encryption each have their own rows. A custom key selection requires the keychain directory and both key names, and the platform must support the recipes. Port discovery accepts a Go duration and defaults to one second. [Compile declarations](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/compile/compile.go) · [discovery timeout](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/arguments/discovery_timeout.go) · [duration grammar](https://pkg.go.dev/time#ParseDuration)
- The inherited rows cover package indexes, configuration file and directory, result format, logging, and color. `--log-file` appends to a file. `--json` formats command results, while `--log-format` controls log messages. [Root declarations and logger](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/cli.go)
- Hidden or deprecated parser controls include `--build-cache-path`, `--build-properties`, `--source-override`, `--skip-libraries-discovery` and the hidden global `--format`. They are absent from the public compile reference and excluded. A sketch path, board-definition properties, platform recipes and standalone upload subcommand options are separate from the compile flag inventory. [1.2.2 parser](https://github.com/arduino/arduino-cli/blob/v1.2.2/internal/cli/compile/compile.go) · [1.6.0 parser](https://github.com/arduino/arduino-cli/blob/v1.6.0/internal/cli/compile/compile.go)

## Fixture and terminal evidence

The [original 15-row specimen](../tests/fixtures/help/expansion-arduino-cli-compile.txt) is synthetic. The [existing 1.5.1 fixed-help capture](../tests/fixtures/help/runtime-followup-captured.json) came from the checksum-verified Linux release. During this audit the Resolute 1.2.2-1 amd64 package was extracted into a temporary directory. Its SHA-256 matched the Ubuntu package index (`bf3e7e26103dfe0c212231c7dc235c200167b9ad70ea4774cfced2c0dc6e3492`). With a private home, `arduino-cli compile --help` produced the same 38 public declarations as the 1.6 manual. No board, port, toolchain, build or upload was used.

The [inventory tests](../tests/test_embedded_manual_inventory.py) compare independent declarations, option arity, readable aliases, structured value checks and literal edits before a quoted sketch operand. The [shared verification report](remaining-bundled-verification.md) records terminal and full-suite outcomes.
