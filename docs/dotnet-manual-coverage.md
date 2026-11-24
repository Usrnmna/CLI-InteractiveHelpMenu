# .NET CLI manual coverage

The five menus contain 242 selectable spellings and insertion forms. The 76 original rows retain their literal spellings. Each menu covers its command reference, the Ubuntu documentation, and the union of four SDK help outputs. The test menu covers VSTest. [First-pass audit and distribution links](dotnet-option-audit.md#sources-and-versions) · [SDK help declarations and manual synopses](../tests/fixtures/dotnet-manual/option-headings.json) · [Original SDK 10.0.402 capture](../tests/fixtures/help/runtime-followup-captured.json)

| Menu | Previous rows | Added | Total | Positional operands |
| --- | ---: | ---: | ---: | --- |
| build | 15 | 44 | 59 | Project or solution. SDK 10+ also accepts a file-based C# app. |
| publish | 16 | 35 | 51 | Project or solution, or a file-based app on SDK 10+. |
| restore | 14 | 27 | 41 | Project or solution, or a file-based app on SDK 10+. |
| run | 13 | 26 | 39 | Project via --project, or file-based app on SDK 10+. A literal -- protects every subsequent application argument. |
| test | 18 | 34 | 52 | Project, solution, directory or built DLL/EXE. Inline RunSettings follow --, for example RunConfiguration.MaxCpuCount=1. |

The Microsoft Learn synopsis and option sections were compared with the Noble and Resolute dotnet-host-10.0 pages (10.0.15-0ubuntu1~24.04.1 and 10.0.15-0ubuntu1~26.04.1). The two distributions provide identical command synopses for build, publish, restore and run. Both test manuals direct the reader to the selected runner. SDK 9.0.200, 10.0.100, 10.0.402 and 11.0.100 supply independent executable evidence. Package version numbers identify the publisher of the manual and do not determine the SDK in a user's working directory. [Build](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build) · [Publish](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-publish) · [Restore](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-restore) · [Run](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run) · [VSTest](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest)

## Selectable inventory

Each row lists literal insertions with the same operand shape for the named commands. A trailing colon leaves the cursor attached to the option. Brackets mark optional operands. The full MSBuild switch language, NuGet configuration properties, project-defined targets, adapters and launch profiles are delegated interfaces. The table includes the MSBuild controls named by these five leaf references and the SDK's implicit-restore controls. [SDK 9 parsers](https://github.com/dotnet/sdk/tree/v9.0.200/src/Cli/dotnet/commands) · [SDK 10 parsers](https://github.com/dotnet/sdk/tree/v10.0.100/src/Cli/dotnet/Commands) · [SDK 10.0.402 command definitions](https://github.com/dotnet/sdk/tree/v10.0.402/src/Cli/Microsoft.DotNet.Cli.Definitions) · [SDK 11 definitions](https://github.com/dotnet/sdk/tree/v11.0.100/src/Cli/Microsoft.DotNet.Cli.Definitions)

| Menus | Selectable spellings | Operand | Effect or qualification |
| --- | --- | --- | --- |
| all | `-h` `--help` | none | Fixed help. Question-mark aliases -? and /? are searchable in Details. Quote them in Bash. |
| all | `-a` `--arch` | ARCH | Architecture portion of the target RID. SDKs before 7 used -a for the VSTest adapter path. |
| all | `--os` | OS | OS portion of the RID. Restore advertises this in SDK 10 and 11. |
| all | `--artifacts-path` | DIR | Common root with separate project outputs. Use the same root across dependent build, restore and run commands. |
| all | `--disable-build-servers` | none | Bypass persistent MSBuild, compiler and Razor build servers. |
| all | `--interactive` | [BOOL] | Allow credential prompts. SDK 10.0.402 and 11.0.100 can also disable prompting explicitly. |
| all | `--tl:` | MODE | Terminal Logger auto, on or off. Run forwards this token to the application in the two earliest captures. |
| all | `-p:` `--p:` `-property:` `--property:` | NAME=VALUE | Set an MSBuild property. /p: and /property: are alternate prefixes. |
| all | `-r` `--runtime` | RID | Select the target runtime. Restore accepts repeated RIDs. |
| all | `-v` `--verbosity` | LEVEL | Named logging level. The original numerical enum contract is pinned to SDK 9.0.200. |
| build publish run test | `--v` `-verbosity` | LEVEL | SDK 10+ MSBuild-compatible aliases. The same parser accepts /v and /verbosity. |
| build publish run test | `-c` `--configuration` | CONFIGURATION | Select a project configuration. Publish defaults depend on target framework and SDK. |
| build publish run test | `-f` `--framework` | FRAMEWORK | Select a target framework moniker declared by the project. |
| build publish test | `-o` `--output` | DIR | Write build output, deployment files or test binaries according to the command. |
| build publish restore test | `--nologo` `--no-logo` `-nologo` | none | Suppress the build or VSTest banner. SDK 10.0.402 and 11.0.100 register the expanded banner aliases including /nologo. |
| build publish run test | `--no-restore` | none | Reuse existing assets matching the configuration and output layout. |
| publish run test | `--no-build` | none | Reuse compiled output and skip implicit restore. |
| build publish restore | `--ucr` `--use-current-runtime` | none | Derive the target RID from the SDK host. |
| build publish run | `--sc` `--self-contained` | [BOOL] | Include the target runtime by default when this option is supplied bare. |
| build publish run | `--no-self-contained` | none | Select framework-dependent output. |
| build publish | `--version-suffix` | SUFFIX | Set the suffix used with VersionPrefix when Version is unset. |
| build publish | `-l:` | LOGGER | MSBuild logger assembly and optional parameters. VSTest uses -l for its own results logger. |
| build publish restore | `--source` | SOURCE | Replace configured NuGet feeds. Repeat to use more than one. |
| build publish restore | `--packages` | DIR | Choose the global packages folder used during restore. |
| build publish restore | `--configfile` | FILE | Read one NuGet settings file. |
| build publish restore | `--disable-parallel` | none | Serialize NuGet project restores. |
| build publish restore | `--ignore-failed-sources` | none | Downgrade eligible feed failures to warnings. |
| build publish restore | `--no-cache` `--no-http-cache` | none | Bypass the HTTP cache. The global packages folder can still satisfy dependencies. |
| build publish restore | `--force` | none | Resolve dependencies again despite the previously successful restore. |
| build publish restore | `--restoreProperty:` `-restoreProperty:` `--rp:` `-rp:` | NAME=VALUE | Assign an MSBuild property for restore. Slash prefixes include /rp: and /restoreProperty:. |
| build | `-bl` `--binaryLogger` | none | Write msbuild.binlog in the working directory. |
| build | `-bl:` `--binaryLogger:` | FILE | Supply the binary log path as an attached value. |
| build | `-t:` `--t:` `-target:` `--target:` | TARGETS | Run one or more MSBuild targets. /t: and /target: are alternate prefixes. |
| build | `--debug` | none | Debugger hook in SDK 9.0.200 and 10.0.100. Release builds accepted it without waiting. SDK 10.0.402 and 11.0.100 rejected it. |
| build | `--no-incremental` | none | Rebuild even when compilation outputs are current. |
| build publish restore test | `--no-dependencies` | none | Build skips building references. Publish and restore skip recursive restore. VSTest on SDK 11 skips building references. |
| publish | `--manifest` | FILE | Exclude packages provided by the target manifest. Repeat for additional manifests. |
| restore | `-s` | SOURCE | Short feed spelling for explicit restore. |
| restore | `-f` | none | Short form of --force. |
| restore | `--force-evaluate` | none | Reevaluate dependencies even with an existing lockfile. |
| restore | `--lock-file-path` | FILE | Choose the dependency lockfile location. |
| restore | `--use-lock-file` | none | Generate and use the project lockfile. |
| restore | `--locked-mode` | none | Fail on changes to an existing locked graph. |
| run | `--project` | PROJECT | Select a project file or directory. |
| run | `-p` | PATH_OR_ASSIGNMENT | Deprecated project path shorthand. An equals sign selects property assignment. All four SDKs still accepted -p Probe.csproj. |
| run | `--file` | FILE | Select a file-based C# app explicitly on SDK 10+. |
| run | `-lp` `--launch-profile` | NAME | Choose a named launch profile. |
| run | `--no-launch-profile` | none | Ignore the launch settings file. |
| run | `--no-cache` | none | Rebuild a file-based app. SDK 9.0.200 instead forwards this token to the app. |
| run | `--device` | DEVICE | Use a device identifier reported for the target workload in SDK 10.0.402 or 11.0.100. |
| run | `--list-devices` | none | Query devices available to the target workload in SDK 10.0.402 or 11.0.100. |
| run test | `-e` `--environment` | NAME=VALUE | Set one application or isolated test-host variable per occurrence. |
| test | `-s` `--settings` | FILE | Read a VSTest .runsettings file. |
| test | `-t` `--list-tests` | none | Discover and list tests without running them. |
| test | `--test-adapter-path` | DIR | Search a directory for adapters. |
| test | `--filter` | EXPRESSION | Select tests by an adapter-supported expression. |
| test | `-d` `--diag` | FILE | Write test platform, host and collector diagnostics. |
| test | `--results-directory` | DIR | Set the results root independently of binary output. |
| test | `-l` `--logger` | LOGGER | Select a test result logger and any quoted parameters. |
| test | `--collect` | COLLECTOR | Enable a named VSTest data collector. |
| test | `--blame` | none | Record test order before a host crash. |
| test | `--blame-crash` | none | Enable crash dump collection for supported processes and platforms. |
| test | `--blame-crash-dump-type` | TYPE | Choose full or mini. |
| test | `--blame-crash-collect-always` | none | Collect after normal and abnormal test host exit. |
| test | `--blame-hang` | none | Dump and terminate a timed-out test host. |
| test | `--blame-hang-dump-type` | TYPE | Choose full, mini or none. None still terminates the hung process. |
| test | `--blame-hang-timeout` | TIMESPAN | Set the per-test hang timeout. Bare values are milliseconds. The default with hang diagnostics enabled is one hour. |

## Reference differences and runner selection

* The publish synopsis advertises -s for a package feed. All four SDKs rejected it with MSB1001. Use --source instead. Build also requires the long feed spelling. The four SDKs passed run's documented --force, --no-dependencies and --source through to the application. Run an explicit restore with the desired flags before dotnet run --no-restore. Unknown application tokens, project paths, inline RunSettings and the -- separator are entered as command operands. The menu preserves the existing child-argument boundary. [SDK run definition](https://github.com/dotnet/sdk/blob/v11.0.100/src/Cli/Microsoft.DotNet.Cli.Definitions/Commands/Run/RunCommandDefinition.cs) · [Implicit restore definitions](https://github.com/dotnet/sdk/blob/v11.0.100/src/Cli/Microsoft.DotNet.Cli.Definitions/Common/ImplicitRestoreOptions.cs)
* The MSBuild Terminal Logger option passed through to the application on run with SDK 9.0.200 and 10.0.100. On 10.0.402 and 11.0.100 it was consumed. The SDK 11 VSTest --no-dependencies switch built the selected test project without building project references. The three earlier SDKs rejected it. The build debugger switch is distinct from the Debug configuration. [SDK 10 debugger helper](https://github.com/dotnet/sdk/blob/v10.0.100/src/Cli/Microsoft.DotNet.Cli.Utils/DebugHelper.cs) · [SDK 11 test definitions](https://github.com/dotnet/sdk/tree/v11.0.100/src/Cli/Microsoft.DotNet.Cli.Definitions/Commands/Test)
* VSTest is the default. SDK 10+ can select Microsoft.Testing.Platform with the global.json test.runner setting. The MTP synopsis includes project, solution and module selectors (--project, --solution, --test-modules, --root-directory), parallelism and result policies (--max-parallel-test-modules, --minimum-expected-tests, --maximum-failed-tests, --timeout, --results-directory-layout), platform settings (--config-file, --diagnostic-output-directory), output and launch controls (--no-banner, --no-ansi, --no-progress, --no-artifact-post-processing, --show-test-results, --no-launch-profile, --no-launch-profile-arguments), device selection (--device, --list-devices), --ucr/--use-current-runtime, --collect-test-map and --affected-tests. In MTP, --output selects console verbosity and --list-tests can select a listing format. Extension options depend on packages registered by the test project. These forms belong to MTP; inserting them into a VSTest command would change its meaning or fail. [MTP reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-mtp) · [Runner selection in Ubuntu](https://manpages.ubuntu.com/manpages/resolute/man1/dotnet-test.1.html)
* The VSTest dump timeout contract covers bare milliseconds and the documented millisecond, second, minute and hour suffixes, including fractional hours. A no-dump hang still terminates the process. Full and mini crash dumps require a supported process, runtime and OS. A runsettings file, shell-quoted logger arguments, data collectors and the distinction between binary and results directories remain searchable. [Blame switches and platform limits](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest#options)

## Executable verification

The offline fixtures used the official linux-x64 SDK on Ubuntu 24.04.5 with Python 3.10.20 (SDK 9.0.200), Ubuntu 24.04.5 with Python 3.12.3 (SDK 10.0.100) and Ubuntu 26.04.1 with Python 3.14.4 (SDK 11.0.100). Each generated a console project and NUnit project with a private NuGet feed. The native checks included custom lockfile generation and reevaluation, a launch-profile environment override, a literal child argument, deployment selection, and an explicit build artifact root, target, property and binary log. Changing the artifacts root after restore initially produced NETSDK1004 because the new intermediate directory had no assets file. Restoring into that layout produced the assembly and binary log. [SDK 9 release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/9.0/releases.json) · [SDK 10 release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json) · [SDK 11 release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/11.0/releases.json)

All three selected and ran one NUnit case with .runsettings, diagnostic logging, a 90-second hang timeout and dump type none. Diagnostics and TRX output were verified on disk. These fixtures exercised option acceptance and the passing-test path. Crash dumps, timeouts that actually terminate a process, credential prompts and physical device launch were verified from documentation and source. [Inventory and insertion regression](../tests/test_dotnet_manual_inventory.py)

The combined batch records real Bash/tmux checks for every selectable row, minimum-size interaction checks and the full three-target suite. [Compatibility results](devtools-batch-verification.md#compatibility-results)
