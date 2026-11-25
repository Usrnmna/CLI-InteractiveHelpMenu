# .NET CLI option audit

First recorded 2026-11-22. Counts and observations below describe the original bundled selections. See the [expanded inventory and verification](dotnet-manual-coverage.md) for the later manual comparison.

The five bundled menus contained 76 selectable entries. Short and long spellings have separate rows and insert their own literal tokens. The test menu describes VSTest. SDK 10 and later also support a Microsoft.Testing.Platform (MTP) command mode with a different option set. [Build](../profiles/dotnet-build.json) · [Publish](../profiles/dotnet-publish.json) · [Restore](../profiles/dotnet-restore.json) · [Run](../profiles/dotnet-run.json) · [Test](../profiles/dotnet-test.json)

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

The five commands required distinct guidance for configuration defaults, runtime selection, implicit restore and output locations. In restore, legacy `--no-cache` bypassed the NuGet HTTP cache while still allowing use of the global packages folder.

## Material differences and coverage boundaries

The published test profile covered VSTest. SDK 10 can select Microsoft.Testing.Platform, whose arguments differ. Both tested SDK parsers also accepted hidden restore spellings. The executable fixtures below record those differences.

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

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Minimum-size restore regression](../tests/test_expansion_terminal.py)

All three targets displayed all 76 entries in real Bash/tmux sessions at 210×100. The checks compared each highlighted spelling and summary, the authored explanation and the entire generated Details pane. The initial pass found that the renderer omitted the sentence about using an existing assembly with `--list-tests`. A direct instruction restored that guidance in the final renders.

| Ubuntu | Python | SDK used for executable fixtures | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | --- | ---: |
| 24.04.5 | 3.10.20 | 9.0.200 | 22 / 0 / 0 | 1,347 / 0 / 1 | 561.141 s |
| 24.04.5 | 3.12.3 | 10.0.100 | 22 / 0 / 0 | 1,347 / 0 / 1 | 496.765 s |
| 26.04.1 | 3.14.4 | 10.0.100 | 22 / 0 / 0 | 1,347 / 0 / 1 | 497.003 s |

Each Linux suite skipped the Windows-specific probe.
