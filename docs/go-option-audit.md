# Go option audit

The audit covers the 10 entries in `go build`, 18 in `go test`, 10 in `go run` and six in `go mod tidy`. A flag shared by three commands counts as three selectable rows. The profiles retain their original option order, argument forms and insertion boundaries. [Build profile](../profiles/go-build.json) · [Test profile](../profiles/go-test.json) · [Run profile](../profiles/go-run.json) · [Tidy profile](../profiles/go-mod-tidy.json)

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

The disposition evaluates the previous wording and value guidance. Shared rows list each applicable menu. A sufficient description is retained when additional prose would only repeat it.

### Build flags shared across menus

| Entry | Menus | Original disposition | Decision |
| --- | --- | --- | --- |
| `-v` | build, run | Sufficient | Reports package names during compilation. Test verbosity is covered separately below. |
| `-n` | build, test, run | Sufficient | Shows planned commands without running them. |
| `-x` | build, test, run | Sufficient | Prints commands as Go executes them. |
| `-race` | build, test, run | Incomplete | Instruments the binary. Detection depends on which paths execute, target support, cgo and a C compiler on Ubuntu. [Race detector requirements](https://go.dev/doc/articles/race_detector#Requirements) |
| `-tags LIST` | build, test, run | Redundant | Replaces numerical boilerplate with an invocation showing comma-separated additional build tags and their effect on file selection. |
| `-ldflags FLAGS` | build, test, run | Redundant | Gives a shell-quoted linker argument list. The structured grammar preserves optional package patterns and the last-match rule. |
| `-gcflags FLAGS` | build, test, run | Redundant | Shows how to disable optimization and inlining across dependencies. Without a pattern, the compiler arguments apply to the packages named on the command line. |
| `-mod MODE` | build, test, run | Incomplete | Distinguishes module downloads in readonly mode, use of vendored packages and permission to update module files. Explains automatic vendoring for eligible modules. [Module build commands](https://go.dev/ref/mod#build-commands) |
| `-trimpath` | build, test, run | Incomplete | Clarifies which filenames change in the executable and how they appear in a stack trace. |

These rows account for nine build entries, eight test entries and nine run entries.

### Command-specific entries

| Menu | Entry | Original disposition | Decision |
| --- | --- | --- | --- |
| build | `-o FILE` | Incomplete | Can write an executable or object. Distinguishes one output file from a destination directory for executables. |
| test | `-run REGEXP` | Incomplete | Selects tests, examples and fuzz seed execution with an unanchored expression. A slash separates subtest levels and a possible parent runs to find its children. |
| test | `-bench REGEXP` | Incomplete | Benchmarks are disabled by default. Gives the all-benchmarks spelling and shows how to skip ordinary tests during a benchmark run. |
| test | `-count N` | Incomplete | Adds the explicit `-count=1` cache bypass. Retains the default, per-CPU counts, exceptions for examples and fuzzing, zero repetitions and unsigned base-prefixed forms. |
| test | `-timeout DURATION` | Redundant | States the per-binary panic deadline, 10-minute default and disabling zero. Keeps case-sensitive units, compound durations, signed zero and the implementation-specific negative-duration behavior. |
| test | `-cover` | Incomplete | Reports statement coverage, with the package under test as the default scope. |
| test | `-coverprofile FILE` | Incomplete | Enables coverage and writes a profile. Gives the command for reading the file by function. [Go coverage guide](https://go.dev/blog/cover) |
| test | `-json` | Incomplete | Produces verbose test events. Whether build diagnostics also arrive as structured events depends on the Go version. |
| test | `-failfast` | Sufficient | Retains the effect on new tests and clarifies that parallel tests already running can finish. |
| test | `-o FILE` | Incomplete | Saves the test executable and runs the tests. Adding `-c` requests compilation alone. A directory receives package-named binaries. |
| test | `-v` | Incomplete | Shows each test and includes Log and Logf output from passing tests. |
| run | `-exec COMMAND` | Redundant | Describes the wrapper's arguments in order. Flags after the package belong to the program. |
| mod tidy | `-e` | Sufficient | Retains the attempt to proceed through package-loading errors. Module files may still change. |
| mod tidy | `-v` | Incomplete | Reports the removed modules on standard error. |
| mod tidy | `-x` | Sufficient | Traces the download commands that execute. |
| mod tidy | `-diff` | Incomplete | Gives the file scope, unified diff, exit status and Go 1.23 minimum. |
| mod tidy | `-go VERSION` | Redundant | Replaces numerical comparisons with the effect of the go directive on indirect requirements and graph pruning. |
| mod tidy | `-compat VERSION` | Inaccurate | Checks for changed module selection and retains needed checksums. Corrects the omitted value in both Details and the structured default. |

## Release differences and manual-only coverage

- **Tidy preview.** Go 1.23 introduced `go mod tidy -diff`. A nonempty diff gives a nonzero status and leaves go.mod and go.sum untouched. Ubuntu 24.04's default series predates the flag. On that system, an unknown-flag error also returns nonzero. [Go 1.23 release notes](https://go.dev/doc/go1.23) · [Go 1.26 tidy help](https://github.com/golang/go/blob/go1.26.0/src/cmd/go/internal/modcmd/tidy.go)
- **Tidy compatibility.** The command help describes the previous Go release as the default for every module. The loader applies that rule only below a go directive of 1.21. From 1.21 onward it uses the declared version. An explicit older `-compat` can retain checksums and report changes in the version supplying an imported package. It does not change the project's go directive. This default was checked directly in the loader for Go 1.22.0, 1.24.0, 1.26.0 and 1.27.4. [Go 1.22 loader](https://github.com/golang/go/blob/go1.22.0/src/cmd/go/internal/modload/load.go) · [Go 1.24 loader](https://github.com/golang/go/blob/go1.24.0/src/cmd/go/internal/modload/load.go) · [Go 1.21 threshold](https://github.com/golang/go/blob/go1.24.0/src/cmd/go/internal/gover/version.go) · [Go 1.26 loader](https://github.com/golang/go/blob/go1.26.0/src/cmd/go/internal/modload/load.go) · [Go 1.27 loader](https://github.com/golang/go/blob/go1.27.4/src/cmd/go/internal/modload/load.go)
- **Test JSON.** Go 1.24 added build output and build failures to the default JSON stream. A consumer written for Noble can therefore see additional event types under Resolute. [Go 1.24 release notes](https://go.dev/doc/go1.24) · [Go 1.22 test help](https://github.com/golang/go/blob/go1.22.0/src/cmd/go/internal/test/test.go)
- **Time and counts.** The test timeout applies independently to each package's test binary. The documented disabling value is zero. The Go 1.24.0 implementation also suppresses the alarm for negative durations. The separate repetition count uses an unsigned integer and applies once per selected CPU setting. [Testing implementation](https://github.com/golang/go/blob/go1.24.0/src/testing/testing.go) · [Duration parser](https://github.com/golang/go/blob/go1.24.0/src/time/format.go) · [Unsigned flag parser](https://github.com/golang/go/blob/go1.24.0/src/flag/flag.go)
- **Outside the menus.** Build flags also include parallelism (`-p`), build modes, overlay files and work-directory retention. Test help additionally covers fuzzing, benchmark duration, CPU settings, coverage packages, profiling, compilation alone and forwarding binary arguments. Run accepts a versioned main package and can select a cross-execution helper. Module help also documents alternate module files and the other module-maintenance commands. A spelling mentioned in Details does not add a menu row. [Upstream command reference](https://pkg.go.dev/cmd/go@go1.27.4)

## Executable checks

Separate from browsing the menus, all three offline targets ran real Go toolchains on a disposable module with a tagged source file, a main program, a subtest, a benchmark and a local module replacement. The binaries came from the official linux/amd64 archives, checked against the published SHA-256 digests. Noble used upstream Go 1.22.12 and Resolute used upstream Go 1.26.0. Module proxy access, external checksum lookup and automatic toolchain downloads were disabled. [Go release archives and checksums](https://go.dev/dl/)

| Fixture | Observed result |
| --- | --- |
| Build and run | Dry-run build printed a compiler command and left the output absent. A tagged build with a linker-supplied string wrote an executable into the requested directory. A wrapper received its own argument, the executable and the program's trailing `-v` in the expected order. |
| Test selection | An anchored subtest expression, a count of `0x2` and a timeout of `1m30s` produced two child log messages. Zero repetitions suppressed the child. A benchmark-only invocation ran the named benchmark. Both toolchains accepted `-timeout=-1s` and ran the subtest. A bare nonzero timeout was rejected. |
| Test outputs | Combining `-o` and `-coverprofile` produced the test executable, a coverage file and the log from the passing test. Adding `-c` produced a test binary without the subtest log. A separately introduced compile error produced a structured build-output event on Go 1.26.0. That event was absent on Go 1.22.12. |
| Tidy preview and update | With an unused requirement and checksum, Go 1.26.0 returned nonzero and printed the proposed deletions from both go.mod and go.sum. Go 1.22.12 rejected the flag. Both invocations preserved the original bytes of both files. A normal tidy removed the unused requirement, reported it on stderr, and set the requested go directive while accepting an explicit compatibility version. A second Go 1.26.0 preview exited successfully with empty output. |

## Rendered menus and offline suites

Each target opened all four bundled menus in real Bash/tmux sessions. At 210×100 every highlighted entry, summary, authored explanation and generated Details pane was checked. Selecting `-tags`, `-count`, `-exec` and `-compat` inserted the literal flag before an existing suffix. Escape restored the pending buffer and cursor. A shell stub recorded no Go executions while browsing.

At 60×16, searching and scrolling reached linker pattern guidance in build, the compile-only distinction in test, wrapper argument placement in run, and the Go 1.22 restriction in tidy. The permanent tidy regression checks the “unified diff” search, the version warning, cancellation and insertion ahead of an existing `-v`. [Rendered terminal regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The focused checks cover profile and insertion contracts, Go time units and zero, rendered search, and inventory reconciliation. The 56 refreshed fingerprints cover 44 option entries, four categories, four command descriptions and four profile files. [Numerical review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 22 / 0 / 0 | 1,346 / 0 / 1 | 494.287 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 22 / 0 / 0 | 1,346 / 0 / 1 | 559.143 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 22 / 0 / 0 | 1,346 / 0 / 1 | 495.491 s |

The full runs included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. Each Linux target skipped the Windows-only probe.
