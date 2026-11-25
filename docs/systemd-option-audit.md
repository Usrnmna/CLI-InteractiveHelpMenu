# systemd option audit

First recorded 2026-11-22. This first pass covered 50 bundled rows. See the [expanded inventory and verification](systemd-manual-coverage.md) for the later manual comparison.

## Sources

| Manual | Upstream systemd 262 | Ubuntu 24.04 LTS, 255.4-1ubuntu8.18 | Ubuntu 26.04 LTS, 259.9-0ubuntu0.1 |
| --- | --- | --- | --- |
| systemctl(1) | [Unit commands and options](https://www.freedesktop.org/software/systemd/man/262/systemctl.html) | [Noble systemctl](https://manpages.ubuntu.com/manpages/noble/man1/systemctl.1.html) | [Resolute systemctl](https://manpages.ubuntu.com/manpages/resolute/man1/systemctl.1.html) |
| journalctl(1) | [Journal sources, filtering and output](https://www.freedesktop.org/software/systemd/man/262/journalctl.html) | [Noble journalctl](https://manpages.ubuntu.com/manpages/noble/man1/journalctl.1.html) | [Resolute journalctl](https://manpages.ubuntu.com/manpages/resolute/man1/journalctl.1.html) |

The structured value records retain their systemd 257 scope. The option parsers and output routines resolve gaps between the manuals and the two Ubuntu binaries. [Tagged upstream systemctl manual](https://github.com/systemd/systemd/blob/v262/man/systemctl.xml) · [Tagged upstream journalctl manual](https://github.com/systemd/systemd/blob/v262/man/journalctl.xml) · [257 systemctl](https://github.com/systemd/systemd/blob/v257/man/systemctl.xml) · [257 journalctl](https://github.com/systemd/systemd/blob/v257/man/journalctl.xml)

## Disposition of the original systemctl entries

The same flags applied differently to unit tables, properties and status output. The descriptions qualified empty properties and machine-readable table forms per operation.

## Disposition of the original journalctl entries

Journal boot IDs, offsets, an explicitly empty boot operand and a zero line count needed distinct handling. The fixed journal and D-Bus fixtures below record release differences.

## Manual-only coverage

The baseline used 50 rows across three systemctl operations and journalctl. The revisit extends the operation-specific inventories and records release-only switches.

## Executable checks

The Ubuntu 26.04 offline sandbox ran the installed 259.9 clients and the extracted Ubuntu 24.04 255.4 clients with their matching private systemd library. A disposable D-Bus service answered queries about three synthetic units. A journal import from generated records provided two boot IDs. These fixtures exercised the clients without connecting to a host manager or reading a host journal. The Bash menu tests below ran separately on each target. [Ubuntu 24.04 client package](https://archive.ubuntu.com/ubuntu/pool/main/s/systemd/systemd_255.4-1ubuntu8.18_amd64.deb)

| Fixture | Observed result |
| --- | --- |
| Unit table | Both clients returned the active service and timer as JSON. `--all` included the inactive service. `--state=inactive` selected it. Both rejected an empty type or state filter. All four JSON modes serialized the table. The `short-delta`, `cat` and `export` modes printed the ordinary unit table. |
| Properties and status | EmptyText disappeared from ordinary `show` output and appeared as `EmptyText=` with `--all`. `--property=Id --value` printed just the unit name. An explicitly named active service still produced properties and status under mismatched filters. `show --output=json --property=Id` printed `Id=alpha.service`. |
| Boot selection | In the fixture directory, bare `--boot` and `--boot=0` both selected the newest boot. Offsets `1` and `-1` selected the first of two boots. Given the first ID followed by `+1`, 255.4 returned the first boot and 259.9 returned the second. Both rejected an empty `--boot=`. |
| Counts and order | With twelve records, bare `--lines` returned ten, `all` returned twelve, and `0` returned none. `2` and `+2` selected opposite ends. Both clients rejected an empty `--lines=`, reverse combined with follow, and reverse combined with `+2`. |
| Other journal filters | A quoted unit pattern selected the matching service. A warning threshold included more severe events. Entries exactly on both requested time bounds appeared. Reverse output began with the newest event. |

## Rendered menus and offline suite

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 13 / 0 / 0 | 1,340 / 0 / 1 | 476.686 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 13 / 0 / 0 | 1,340 / 0 / 1 | 534.321 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 13 / 0 / 0 | 1,340 / 0 / 1 | 476.927 s |

Each Linux suite skipped the Windows-specific probe.
