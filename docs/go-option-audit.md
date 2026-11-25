# Go option audit

First recorded 2026-11-22. Counts and observations below describe the original bundled selections. See the [expanded inventory and verification](go-manual-coverage.md) for the later manual comparison.

The audit covered the 10 entries in `go build`, 18 in `go test`, 10 in `go run` and six in `go mod tidy`. A flag shared by three commands counts as three selectable rows. The profiles retained their original option order, argument forms and insertion boundaries. [Build profile](../profiles/go-build.json) · [Test profile](../profiles/go-test.json) · [Run profile](../profiles/go-run.json) · [Tidy profile](../profiles/go-mod-tidy.json)

## Sources

| Reference | Ubuntu 24.04 LTS | Ubuntu 26.04 LTS |
| --- | --- | --- |
| Default Go toolchain series | Go 1.22. [golang-go 2:1.22~2build1](https://packages.ubuntu.com/noble/golang-go) | Go 1.26. [golang-go 2:1.26~1](https://packages.ubuntu.com/resolute/golang-go) |
| Build flags, build output and program arguments | [go-build(1)](https://manpages.ubuntu.com/manpages/noble/man1/go-build.1.html) · [go-run(1)](https://manpages.ubuntu.com/manpages/noble/man1/go-run.1.html) | [go-build(1)](https://manpages.ubuntu.com/manpages/resolute/man1/go-build.1.html) · [go-run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/go-run.1.html) |
| Test driver and test-binary flags | [go-test(1)](https://manpages.ubuntu.com/manpages/noble/man1/go-test.1.html) · [go-testflag(7)](https://manpages.ubuntu.com/manpages/noble/man7/go-testflag.7.html) | [go-test(1)](https://manpages.ubuntu.com/manpages/resolute/man1/go-test.1.html) · [go-testflag(7)](https://manpages.ubuntu.com/manpages/resolute/man7/go-testflag.7.html) |
| Module maintenance | [go-mod(1)](https://manpages.ubuntu.com/manpages/noble/man1/go-mod.1.html) · [Go 1.22 tidy command](https://github.com/golang/go/blob/go1.22.0/src/cmd/go/internal/modcmd/tidy.go) | [go-mod(1)](https://manpages.ubuntu.com/manpages/resolute/man1/go-mod.1.html) · [Go 1.26 tidy command](https://github.com/golang/go/blob/go1.26.0/src/cmd/go/internal/modcmd/tidy.go) |

The Ubuntu man pages identify their provider as `gccgo-go` from `golang-defaults`, with the respective metadata versions above. Each distribution's `go-mod(1)` describes tidy's purpose and directs readers to `go help mod tidy`. Neither standalone `go-mod-tidy(1)` URL returned a page. The versioned upstream command help supplies the individual tidy flags.

For command editing, the run menu stops at its first positional operand. The test menu can remain active after package paths and closes off parent options after `-args` or `--`. The Go driver documents `-args` as the spelling that forwards the remaining words to the test binary.

The upstream comparison uses the Go 1.27.4 command reference. Existing structured value metadata is pinned to Go 1.24.0. The tagged command references and loader sources distinguish those scopes from the Ubuntu default toolchains. [Go 1.27.4 command reference](https://pkg.go.dev/cmd/go@go1.27.4) · [Go 1.24.0 command reference](https://github.com/golang/go/blob/go1.24.0/src/cmd/go/alldocs.go) · [Go Modules Reference](https://go.dev/ref/mod)

## Disposition of the 44 entries

### Build flags shared across menus

Build, run and test repeated common compiler controls. The shared flags still needed per-menu placement and arity.

### Command-specific entries

The four profiles distinguished a run wrapper, test arguments forwarded after `-args`, and the checks performed by `go mod tidy`.

## Release differences and manual-only coverage

Go 1.23 introduced `go mod tidy -diff`. A nonempty diff changes the exit status and leaves both module files intact. An older Go also returns nonzero when it rejects the unknown flag.

## Executable checks

Separate from browsing the menus, all three offline targets ran real Go toolchains on a disposable module with a tagged source file, a main program, a subtest, a benchmark and a local module replacement. The binaries came from the official linux/amd64 archives, checked against the published SHA-256 digests. Noble used upstream Go 1.22.12 and Resolute used upstream Go 1.26.0. Module proxy access, external checksum lookup and automatic toolchain downloads were disabled. [Go release archives and checksums](https://go.dev/dl/)

| Fixture | Observed result |
| --- | --- |
| Build and run | Dry-run build printed a compiler command and left the output absent. A tagged build with a linker-supplied string wrote an executable into the requested directory. A wrapper received its own argument, the executable and the program's trailing `-v` in the expected order. |
| Test selection | An anchored subtest expression, a count of `0x2` and a timeout of `1m30s` produced two child log messages. Zero repetitions suppressed the child. A benchmark-only invocation ran the named benchmark. Both toolchains accepted `-timeout=-1s` and ran the subtest. A bare nonzero timeout was rejected. |
| Test outputs | Combining `-o` and `-coverprofile` produced the test executable, a coverage file and the log from the passing test. Adding `-c` produced a test binary without the subtest log. A separately introduced compile error produced a structured build-output event on Go 1.26.0. That event was absent on Go 1.22.12. |
| Tidy preview and update | With an unused requirement and checksum, Go 1.26.0 returned nonzero and printed the proposed deletions from both go.mod and go.sum. Go 1.22.12 rejected the flag. Both invocations preserved the original bytes of both files. A normal tidy removed the unused requirement, reported it on stderr, and set the requested go directive while accepting an explicit compatibility version. A second Go 1.26.0 preview exited successfully with empty output. |

## Rendered menus and offline suites

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Rendered terminal regression](../tests/test_expansion_terminal.py)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 22 / 0 / 0 | 1,346 / 0 / 1 | 494.287 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 22 / 0 / 0 | 1,346 / 0 / 1 | 559.143 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 22 / 0 / 0 | 1,346 / 0 / 1 | 495.491 s |

Each Linux suite skipped the Windows-specific probe.
