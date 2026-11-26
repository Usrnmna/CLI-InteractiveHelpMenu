# Ubuntu command coverage comparison

[Roadmap](../ROADMAP.md#ubuntu-command-coverage-expansion) · [Shipped command inventory](ubuntu-command-coverage/shipped.tsv) · [Kernel companion paths](ubuntu-command-coverage/kernel-companions.tsv) · [Ranked and supplementary optional commands](ubuntu-command-coverage/optional.tsv)

## Implemented batch

The result columns in the linked inventories report the implemented root coverage. All 119 ranked command rows across 100 packages and all eight kernel paths have selectable results in the Resolute reference replay. The shipped union has 2,039 names with selectable coverage and 346 with command-specific usage or documentation guidance. The tables below retain the comparison against the original project snapshot. [Results, evidence, result codes and limitations](ubuntu-coverage-audit.md)

## Reference and project evidence

The reference contains the command names shipped in six Ubuntu 26.04 amd64 filesystem profiles. It includes executable paths and symlinks from the normal command directories, Bash builtins, and launchers exposed by seeded snaps. The Desktop profiles use the ordinary English installer selections. Server Cloud means the published root filesystem archive. The inventory describes the inspected image payloads. Installer-added packages, hardware-specific variations, later image updates, other architectures and other distributions can have different inventories. [Ubuntu release media](https://releases.ubuntu.com/26.04/) · [Ubuntu Base archives](https://cdimage.ubuntu.com/ubuntu-base/releases/26.04/release/) · [Ubuntu Server Cloud archives](https://cloud-images.ubuntu.com/releases/resolute/release/)

| Profile | Shipped names |
| --- | ---: |
| Desktop Default | 2,041 |
| Desktop Extended | 2,087 |
| Server Default | 1,739 |
| Server Minimized | 1,437 |
| Ubuntu Base | 542 |
| Server Cloud | 1,500 |
| Union | 2,385 |

The project snapshot is `6354c05b5af11e57868ccec57bdf4a86aa0151a2`. The comparison matches exact, case-sensitive command names against the bundled profiles, built-in Git and Docker routes, supplied driver collection, and maintained fixture inventory. Fixture documents were replayed through the profile builder without invoking the documented programs. The source of an option, a bundled profile and a driver route each provide different evidence. Example-driver discovery requires `CLI_HELP_DRIVERS`. Static profile availability is recorded independently of that setting. [Bundled profiles](../profiles/) · [Built-in routes](../cli_help/command_paths.py) · [Driver activation](compatibility.md#enable-the-drivers) · [Fixture inventory](../tests/test_regression_inventory.py)

| Status | Evidence counted |
| --- | --- |
| Bundled root menu | A bundled profile for the exact command name. |
| Selectable root fixture | A maintained root fixture produced selectable options on replay. The fixture may be captured output or a format specimen. The routing column identifies applicable driver activation. |
| Selectable subpaths only | Bundled or replayed menu evidence for one or more exact leaves, including the explicitly supported Python module forms. |
| Route or nonselectable fixture only | A route or fixture exists, with no bundled or selectable fixture menu for the name or its leaves. The path columns also record usage-only root fixtures alongside selectable leaves. |
| No maintained evidence | No matching bundled menu, recorded driver path or maintained fixture was found. Generic installed-command discovery can still succeed on individual tools. |

Project status is based on the maintained corpus, including usage-only replies and profile-only leaves in the compatibility matrix. It does not assert live option coverage on all versions or installations. A related executable, package alias, prefix role or fixture for another spelling does not establish help for the exact invocation. [Compatibility matrix](../tests/fixtures/help/matrix.json) · [Discovery implementation](../cli_help/discovery.py)

## Shipped coverage at the original snapshot

| Maintained project evidence | Shipped names |
| --- | ---: |
| Bundled root menu | 9 |
| Selectable root fixture | 15 |
| Selectable subpaths only | 6 |
| No maintained menu, route or fixture evidence | 2,355 |
| Total | 2,385 |

The six names with subpath evidence only are `git`, `ip`, `openssl`, `python3`, `restic` and `systemctl`. The maintained `python3` forms cover `-m pip` and `-m pytest`. The root interpreter remains a gap. Existing Bash integration and prefix parsing do not provide command help for `bash`, `cd`, `command`, `env` or `sudo`. The inventory includes 61 Bash builtin names. It flags special spellings such as `.`, `:`, `[` and `gnu[` for explicit review. Names that overlap with external utilities, such as `test` and `[`, need evidence for the applicable invocation. [Invocation grammar](../cli_help/invocation.py) · [Bash builtins](https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html)

APT and dpkg are the first default family. The shipped `apt`, `apt-get`, `apt-cache`, `apt-mark`, `apt-config`, `dpkg`, `dpkg-deb` and `dpkg-query` names lack maintained menu evidence. Inventory root and documented subcommand help by package edition. Preserve boundaries between package operands and options, between APT and dpkg, and between read-only documentation requests and package actions. [Ubuntu APT manuals](https://manpages.ubuntu.com/manpages/resolute/man8/apt.8.html) · [Ubuntu package management](https://ubuntu.com/server/docs/how-to/software/package-management/)

The eight kernel-versioned companion paths have no maintained evidence. Seven share names with normal command-directory entries. `intel-speed-select` appears only at the kernel companion path in this reference and needs its own documented invocation. Both paths and names are retained so wrappers do not hide edition or applicability differences. [Kernel companion paths](ubuntu-command-coverage/kernel-companions.tsv)

Default coverage applies to the shipped commands on the selected supported profile, including Bash builtins, administrative commands, aliases exposed as executables, seeded snaps and kernel companions. Maintain an evidence-backed disposition for every baseline row. Provide a selectable menu where a documented option or keyword can be inserted. Provide reachable usage or documentation guidance where the command has no selectable interface. Keep a concrete blocker open for any row without a verified source or reachable result. Availability varies by image, so a missing local binary must have an explicit outcome. Existing user driver configuration, the `CLI_HELP_DISCOVERY` modes, and the pending-buffer and argument boundaries remain part of acceptance. [Bulk manual scanner](../cli_help/bulk_scan.py) · [Invocation and argument contract](invocation-and-structured-arguments.md)

## Ranked optional gaps at the original snapshot

The optional queue preserves the November 25, 2026 Debian Popularity Contest snapshot. A ranked package contributes one representative command absent from all six Ubuntu profiles. The comparison also includes the supplied companion commands. Vote counts measure recent Debian package activity, including automated and dependency use. [Debian ranking](https://popcon.debian.org/by_vote) · [Debian vote definition](https://popcon.debian.org/FAQ)

| Ranks | Bundled representative root | Selectable representative root fixture | Representative subpaths only | Representative without maintained evidence |
| --- | ---: | ---: | ---: | ---: |
| 1–25 | 1 | 2 | 3 | 19 |
| 26–50 | 0 | 3 | 3 | 19 |
| 51–100 | 2 | 4 | 2 | 42 |
| Total | 3 | 9 | 8 | 80 |

For 79 of the 100 packages, none of the listed command names has a maintained menu. The additional representative gap is `ansible` at rank 59. The same package's `ansible-playbook` already has a bundled root. Other examples include `ctest` alongside the evidenced `cmake` root and `gofmt` alongside maintained `go` leaves. The optional inventory preserves all 205 reference rows, including the 55 that are shipped on some profiles. Apply shipped coverage wherever a command is shipped, even when it also needs an installation note for another profile.

Start with missing `smartctl` (#1), `sensors` (#2), `apache2ctl` (#3), `make` (#5), `sshfs` (#6), `fail2ban-client` (#7), `socat` (#8), `pigz` and `unpigz` (#9), and `nginx` (#10). Preserve the existing `gcc` (#4), `7z` (#11), and `ffmpeg` and `ffprobe` (#17) evidence. Give special attention to root gaps in the high-ranked Docker, pip and Podman families and to example-driver activation for existing routes. The npm root is an existing usage-only case. Covering it does not require inventing insertable options. [All ranked packages, companion commands and exact project paths](ubuntu-command-coverage/optional.tsv)

The unranked ecosystem shortlist has existing selectable leaves for `aws`, `gcloud`, `helm`, `kubectl`, `terraform`, `tofu` and `uv`. The comparison found no maintained evidence for `deno`. These tools remain outside the ranked APT queue.

## Integrated verification procedure

1. Prepare the source evidence and fixture manifest together for the default inventory and the ranked queue. Group aliases, wrappers and command families by shared help sources and test setup. Start optional groups at their earliest rank. Reuse existing captures and independent assertions for unchanged paths. Run the existing scan against bounded, isolated image or fixture directories where possible. A scan renders manuals and does not invoke the scanned executables. Use version-matched documentation or allowlisted fixed requests for the remaining cases. Treat a failed request, an empty option set and a usage-only result separately.
2. Use focused host checks while editing each group. Include the relevant help parsing, route resolution, numerical declarations, literal insertion, and historical fixture checks. Review the impact report before using the selector. Where it falls back to the whole suite, use the documented explicit family checks for edit feedback and keep the full gate for the integrated snapshot. Do not claim selector coverage for an unmapped path. [Isolated debugging](development.md#isolated-local-debugging) · [Test selection](test-selection-plan.md#4-add-explicit-selection-for-local-audits)
3. Integrate the default and optional queues before full-suite verification. On the prepared `host`, `noble310` and `noble312` targets, batch the affected rendered-terminal and fixed-source checks. Check profile availability, example-driver dependencies, option and operand boundaries, cancellation, and literal midline insertion. Reconcile the inventory and collection, review changed numerical facts and run the strict numerical gate before the full tests. Include required untracked fixtures explicitly. [Command-help audit procedure](development.md#auditing-command-help)
4. Freeze one input snapshot and run the ordinary full offline suite once per target with the corresponding prepared fixtures. Use the same integrated source, profile, driver, documentation and assertion inputs on all three targets. Keep a failure in the affected focused loop until it is resolved. A correction to the frozen inputs needs verification against the corrected snapshot under the existing batch gate. Record the shared identity, target-specific versions and fixtures, passes, failures, skips and unresolved paths. If shared runtime changes become necessary, resolve the architecture decision before implementing them and keep independent evidence preparation moving. [Full offline verification](test-selection-plan.md#full-offline-verification)
