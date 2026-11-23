# .NET CLI option audit

The five bundled menus contain 76 selectable entries. Short and long spellings have separate rows and insert their own literal tokens. The test menu describes VSTest. SDK 10 and later also support a Microsoft.Testing.Platform (MTP) command mode with a different option set. [Build](../profiles/dotnet-build.json) · [Publish](../profiles/dotnet-publish.json) · [Restore](../profiles/dotnet-restore.json) · [Run](../profiles/dotnet-run.json) · [Test](../profiles/dotnet-test.json)

## Sources and versions

| Command | Microsoft CLI reference | Ubuntu 24.04 | Ubuntu 26.04 |
| --- | --- | --- | --- |
| build | [Build options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build) | [Noble dotnet-build(1)](https://manpages.ubuntu.com/manpages/noble/man1/dotnet-build.1.html) | [Resolute dotnet-build(1)](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-build.1.html) |
| publish | [Publish options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-publish) | [Noble dotnet-publish(1)](https://manpages.ubuntu.com/manpages/noble/man1/dotnet-publish.1.html) | [Resolute dotnet-publish(1)](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-publish.1.html) |
| restore | [Restore options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-restore) | [Noble dotnet-restore(1)](https://manpages.ubuntu.com/manpages/noble/man1/dotnet-restore.1.html) | [Resolute dotnet-restore(1)](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-restore.1.html) |
| run | [Run options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run) | [Noble dotnet-run(1)](https://manpages.ubuntu.com/manpages/noble/man1/dotnet-run.1.html) | [Resolute dotnet-run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-run.1.html) |
| test | [VSTest options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest) · [MTP options](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-mtp) | [Noble dotnet-test(1)](https://manpages.ubuntu.com/manpages/noble/man1/dotnet-test.1.html) | [Resolute dotnet-test(1)](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-test.1.html) |

The five Noble pages identified their provider as `dotnet-host-10.0 10.0.15-0ubuntu1~24.04.1`. The five Resolute pages identified `10.0.15-0ubuntu1~26.04.1`. The corresponding manual bodies matched across distributions. These versions identify the documentation packages. The executable checks below identify the SDKs actually run.

Microsoft's build, publish, restore, run and VSTest references cover SDK 6 and later and label features introduced later. Both Ubuntu test pages explain runner selection and defer the flag list to runner-specific documentation. The SDK 9.0.200 parsers govern the menu's pinned value metadata. SDK 10.0.100 provided a second parser comparison. [SDK 9.0.200 parsers](https://github.com/dotnet/sdk/tree/v9.0.200/src/Cli/dotnet/commands) · [SDK 10.0.100 parsers](https://github.com/dotnet/sdk/tree/v10.0.100/src/Cli/dotnet/Commands)

## Disposition of all 76 entries

The disposition evaluates the previous description and value guidance. Each row below applies to every spelling and menu it names.

| Shared entry | Menus | Original disposition | What changes for the reader |
| --- | --- | --- | --- |
| `-c`, `--configuration` | build, run, test | Incomplete | Debug is the usual project default. Release and project-defined configuration names are accepted. |
| `-c`, `--configuration` | publish | Incomplete | With SDK 8 or newer, projects targeting net8.0 or newer normally publish Release. Earlier targets normally publish Debug. Projects can override the default. |
| `-f`, `--framework` | build, publish, run, test | Incomplete | Select a target framework moniker declared in the project. Build can compile multiple targets. Publish and run can select one, and multi-target run requires a selection. Test runs all declared targets by default. |
| `-r`, `--runtime` | build, publish, run, test | Incomplete | A RID such as linux-x64 selects a target OS and architecture. Publish distinguishes runtime selection from bundling .NET. Run needs a locally runnable target. VSTest identifies the SDK 7 change to the short spelling. |
| `-r`, `--runtime` | restore | Inaccurate | Restore can resolve multiple runtime targets by repeating the option. Its SDK parser collects them in the plural RuntimeIdentifiers property. |
| `-o`, `--output` | build, publish | Incomplete | Build writes binaries, while publish writes deployment files. Relative paths start at the working directory. A shared output directory can mix project outputs. Web projects can nest publish directories on repeated publishes. |
| `-o`, `--output` | test | Incomplete | Selects the directory containing the compiled test assemblies. The results directory and its logger output are separate. |
| `-v`, `--verbosity` | build, publish, restore, run, test | Sufficient | Retains the five named logging levels and the SDK 9.0.200 enum guidance. Run distinguishes SDK logging from application arguments. Test gives a separate console logger example. |
| `--no-restore` | build, publish, run, test | Incomplete | Skips the usual implicit NuGet restore. Previously restored assets must cover the selected target framework and runtime. |
| `--nologo` | build, publish, test | Sufficient | Names the affected banner, MSBuild for build and publish, Microsoft TestPlatform for test. |
| `--no-build` | publish, run, test | Incomplete | Reuses compatible existing outputs and also skips implicit restore. |
| `--force` | build, restore | Incomplete | Repeats dependency resolution, with the effect of removing the project assets file. It is independent of the incremental compilation switch. |

| Command-specific entry | Menu | Original disposition | What changes for the reader |
| --- | --- | --- | --- |
| `--no-incremental` | build | Incomplete | Rebuilds the dependency graph even when outputs appear current. |
| `--no-dependencies` | build | Incomplete | Skips building project references. Their outputs can still be needed, and NuGet restore remains a separate step. |
| `--self-contained [BOOL]` | publish | Incomplete | The bare option selects true. False selects framework-dependent deployment. A bundled runtime is platform-specific. |
| `--no-self-contained` | publish | Incomplete | The deployment needs a compatible runtime on the destination even when it contains RID-specific assets. |
| `--use-current-runtime` | publish | Sufficient | Identifies the SDK host as the runtime target and gives the explicit RID alternative for cross-publishing. |
| `-s`, `--source` | restore | Incomplete | Command-line sources replace the configured feed list. Repeat the option for multiple URLs or local package directories. |
| `--packages` | restore | Incomplete | Sets the global packages folder for this restore. Gives the usual Ubuntu location and what may override it. |
| `--configfile` | restore | Incomplete | Selects one NuGet configuration file in place of the normal settings hierarchy. |
| `--disable-parallel` | restore | Incomplete | Restores projects one at a time. |
| `--ignore-failed-sources` | restore | Incomplete | An inaccessible feed can be a warning when the required package version is available elsewhere. A missing required version still fails restore. |
| `--no-cache` | restore | Inaccurate | The hidden legacy spelling bypasses NuGet's HTTP cache. Restore can still use the global packages folder. Details give the documented spelling `--no-http-cache`. |
| `--locked-mode` | restore | Incomplete | Fails on a stale existing lock. By itself this option does not enable lockfile generation. |
| `--use-lock-file` | restore | Incomplete | Generates and uses packages.lock.json. Identifies locked mode for enforcing the recorded graph. |
| `--project` | run | Incomplete | Accepts a project file or directory and otherwise searches the working directory. |
| `--launch-profile` | run | Incomplete | Takes a profile name from Properties/launchSettings.json. The profile can supply environment variables. |
| `--no-launch-profile` | run | Sufficient | Skips the launch settings file and its environment settings. |
| `--filter` | test | Redundant | Gives a shell-quoted VSTest expression. Keeps adapter-specific properties, the four comparison operators, boolean combinations and the SDK forwarding property in searchable Details. |
| `--logger` | test | Incomplete | Can be repeated. Quotes the logger's semicolon-separated parameters and shows how to keep separate TRX files for multiple frameworks. |
| `--results-directory` | test | Incomplete | VSTest creates the directory when needed. The usual location is TestResults under the project. A logger determines which report is written. |
| `--collect` | test | Incomplete | Takes a collector name. The quoted XPlat Code Coverage example requires the Coverlet collector in the test project. |
| `--list-tests` | test | Sufficient | Lists discovered tests without executing test cases. Discovery still loads assemblies and adapters, and can reuse a prior build. |

## Material differences and coverage boundaries

- **HTTP cache and dependency locks.** The Microsoft and Ubuntu restore references document `--no-http-cache`. The 9.0.200 and 10.0.100 parsers also accept `--no-cache` and hide it from help. NuGet treats the legacy property as an HTTP-cache switch. The global packages folder can satisfy an entire restore with an empty feed. Locked mode and lock generation are also independent, as the fixtures below demonstrate. [SDK 9 restore parser](https://github.com/dotnet/sdk/blob/v9.0.200/src/Cli/dotnet/commands/dotnet-restore/RestoreCommandParser.cs) · [SDK 10 restore parser](https://github.com/dotnet/sdk/blob/v10.0.100/src/Cli/dotnet/Commands/Restore/RestoreCommandParser.cs) · [NuGet cache behavior](https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders)
- **RID and deployment.** Starting with apps targeting .NET 8, selecting a RID alone no longer makes a deployment self-contained. Other publish settings can still affect deployment. Explicit `--self-contained` and `--no-self-contained` express the intended choice. Restore accepts a list of RIDs through repeated flags. Build and publish use a single RuntimeIdentifier. [Runtime-specific deployment change](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/8.0/runtimespecific-app-default) · [SDK 9 common options](https://github.com/dotnet/sdk/blob/v9.0.200/src/Cli/dotnet/CommonOptions.cs)
- **VSTest binaries and reports.** Build and test forward their output path to MSBuild OutputPath. Publish uses PublishDir. VSTest forwards `--results-directory` separately to VSTestResultsDirectory. Since SDK 7, `-r` selects the runtime. Earlier VSTest CLIs used that short spelling for the results directory. The VSTest reference also documents that a fixed TRX filename can overwrite results from an earlier target framework. [SDK test parser](https://github.com/dotnet/sdk/blob/v9.0.200/src/Cli/dotnet/commands/dotnet-test/TestCommandParser.cs) · [SDK publish parser](https://github.com/dotnet/sdk/blob/v9.0.200/src/Cli/dotnet/commands/dotnet-publish/PublishCommandParser.cs) · [VSTest reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest)
- **Runner selection.** SDK 10 introduced native MTP mode via the test runner setting in global.json. VSTest is the default on the tested SDKs. The MTP command has different switches, and its extensions depend on the test application. This review covers the 18 entries in the VSTest profile. [Microsoft.Testing.Platform command reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-mtp)
- **Manual-only options.** Examples outside the selection include `--artifacts-path` for project-separated output, `--arch` and `--os` for targeting, restore's `--force-evaluate` and `--lock-file-path`, run's `--property`, and VSTest's `--settings`, `--diag` and blame options. The 76 rows preserve the curated spellings, including the legacy cache option. Installed-command discovery remains a separate roadmap item.

## Executable verification

Each offline sandbox used a checksum-verified Microsoft linux-x64 SDK archive and a local NuGet feed. The tests created a console project, launch settings, a disposable package cache and a two-test NUnit project. The fixture used Microsoft.NET.Test.Sdk 17.12.0, NUnit 4.3.2 and NUnit3TestAdapter 4.6.0. Noble's minimal test images needed ICU, which was extracted into private sandbox storage. No SDK or package was installed on the host. [Microsoft SDK 9 release metadata](https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/9.0/releases.json) · [SDK 10 release metadata](https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/10.0/releases.json)

| Fixture | Observed on SDK 9.0.200 and 10.0.100 |
| --- | --- |
| Build, run and publish | Build without restored assets failed. After restore, build wrote the app under Debug. Run reused it with and without the profile's environment variable, and passed a literal `--configuration` through the application argument boundary. Framework-dependent publish wrote the app under Release. |
| Deployment settings | A separate project imported the SDK targets and reported the evaluated SelfContained property during publish. A linux-x64 RID alone evaluated to false, a bare self-contained flag to true, and an explicit false to false. This probe measured property selection. |
| Restore and caches | After populating a private packages folder, forced locked restore succeeded with an empty replacement feed and `--no-cache`. Target help showed only `--no-http-cache` of the two spellings. |
| Lockfile | A fresh console project restored successfully with `--locked-mode` alone and produced no lockfile. After explicit lock generation in the test project, changing a dependency version failed with NU1004 and preserved the lockfile bytes. |
| VSTest | Listing discovered both tests and wrote the assembly to the requested binary directory. A subsequent no-build run selected the passing test and excluded the deliberately failing test. The TRX in the separate results directory contained exactly the selected test. |
| Verbosity | Build accepted numeric value 3 and rejected 42. The detailed numeric alias map in the profile remains scoped to SDK 9.0.200. [Pinned enum evidence](numerical-inventory/debt-resolution.md) |

## Rendered menus and offline suites

All three targets displayed all 76 entries in real Bash/tmux sessions at 210×100. The checks compared each highlighted spelling and summary, the authored explanation and the entire generated Details pane. The initial pass found that the renderer omitted the sentence about using an existing assembly with `--list-tests`. A direct instruction restored that guidance in the final renders.

At 60×16, search and scrolling reached the build reference rule, RID-based publishing, the global packages folder, launch profile settings and the VSTest reports directory. Across the five menus, selecting `--output`, `--runtime`, `--source`, `--launch-profile` or `--results-directory` inserted the literal flag before the existing suffix. Escape restored the original buffer and cursor. The minimum-size regression also selected `--no-cache` before a pending project filename. A shell stub recorded no execution while browsing. [Minimum-size restore regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The focused checks covered literal insertion, development profiles, VSTest filter grammar, numeric verbosity aliases, the minimum-size restore menu and inventory reconciliation. The 91 refreshed review fingerprints cover 76 options, five categories, five command descriptions and five profile files. [Numerical review](numerical-inventory/review.json)

| Ubuntu | Python | SDK used for executable fixtures | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | --- | ---: |
| 24.04.5 | 3.10.20 | 9.0.200 | 22 / 0 / 0 | 1,347 / 0 / 1 | 561.141 s |
| 24.04.5 | 3.12.3 | 10.0.100 | 22 / 0 / 0 | 1,347 / 0 / 1 | 496.765 s |
| 26.04.1 | 3.14.4 | 10.0.100 | 22 / 0 / 0 | 1,347 / 0 / 1 | 497.003 s |

All three offline snapshots included the untracked audit documents and passed shell syntax checks, numerical coverage, profile validation and unittest discovery. Each Linux target skipped the probe specific to Windows.
