# Podman run manual coverage

The bundled menu grew from 16 to 168 selectable spellings. The three manuals describe 151 distinct implemented options, including the accepted Docker compatibility no-op, plus 17 aliases. Ten of those options and six aliases appeared in the original menu. The revisit adds 141 options and 11 aliases. The original rows retain their order and inserted text. New rows are grouped by purpose. The first positional operand still ends Podman option completion. [Bundled run profile](../profiles/podman-run.json) · [Original Podman audit](podman-option-audit.md)

## References and scope

| Source | Version | Option headings |
| --- | --- | ---: |
| [Upstream run manual](https://docs.podman.io/en/v6.2.0/markdown/podman-run.1.html#options) | Podman 6.2.0 | 151 |
| [Ubuntu 24.04 run(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-run.1.html) | 4.9.3+ds1-1ubuntu0.2 | 141 |
| [Ubuntu 26.04 run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-run.1.html) | 5.7.0+ds2-3build1 | 152 |

The union contains 153 headings. One is a separate heading for an alias, and one documents an unimplemented option. Sixteen further aliases appear beside their primary spelling. The inventory below records the section heading, menu argument, release coverage and any exclusion. Global options before `run`, arguments after the image, and switches belonging to commands in examples have different owners. For example, the examples section’s `--permissive` text refers to SELinux policy configuration.

## Material changes

- **Volume ownership and labels.** Both volume spellings explain that `:U` recursively changes ownership on the host. On a large tree this can delay startup. Lowercase `:z` requests shared SELinux labeling. Uppercase `:Z` requests private labeling, and containers in the same pod share that label. Details distinguish these persistent host changes from a temporary `:O` overlay, whose writes normally disappear. Custom overlay upper and work directories require manual cleanup. [Upstream volume option](https://github.com/containers/podman/blob/v6.2.0/docs/source/markdown/options/volume.md)
- **Mount lifetime and propagation.** A destination alone creates an anonymous volume. A named volume can be created on demand, while a bind source must exist on the machine running Podman. Upstream 6.2 documents `nocreate` for named volumes. Neither Ubuntu page lists it. Details also cover initial copy-up, read-only mounts, submounts, propagation, execution and device permissions, and ID mapping. The separate `--mount` row shows the key/value syntax and identifies which releases document artifact mounts. [Noble run(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-run.1.html) · [Resolute run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-run.1.html)
- **Networking and ports.** Both `--network` and `--net` show the rootful bridge default and the change from rootless slirp4netns on Noble to pasta on Resolute and upstream. Details distinguish sharing the host namespace, joining another namespace and assigning options per named network. Exposing a port, publishing one port and publishing every exposed port have separate rows. [Upstream network modes](https://docs.podman.io/en/v6.2.0/markdown/podman-run.1.html#network-mode-net)
- **Health checks and limits.** Regular and startup health checks have distinct intervals, retry effects and timeouts. Both Ubuntu manuals give a 30s startup interval and document `disable`. Upstream gives 0s and adds `--health-start-interval` as an alias. The menus distinguish CPU microseconds from container lifetime in seconds, combined memory and swap from a memory reservation, and device bandwidth from operation counts. Podman’s size parser uses binary multipliers and accepts case-insensitive suffixes. For a device rate, 1mb means 1,048,576 bytes per second. A rate in IOPS counts operations per second. The bundled review retains the original 4.9.3 help capture as separate evidence. [Upstream run options](https://docs.podman.io/en/v6.2.0/markdown/podman-run.1.html#options) · [4.9.3 resource parsing](https://github.com/containers/podman/blob/v4.9.3/pkg/specgenutil/specgen.go) · [5.7.0 resource parsing](https://github.com/containers/podman/blob/v5.7.0/pkg/specgenutil/specgen.go) · [6.2.0 resource parsing](https://github.com/containers/podman/blob/v6.2.0/pkg/specgenutil/specgen.go) · [Vendored size parser](https://github.com/containers/podman/blob/v6.2.0/vendor/github.com/docker/go-units/size.go)
- **Compatibility spellings.** Both Ubuntu releases document real-time CPU controls for rootful cgroups v1. Upstream 6.2 still parses the two flags as hidden no-ops. All three manuals describe `--disable-content-trust` as an accepted no-op and `--link-local-ip` as unimplemented. Both packaged clients rejected the latter as an unknown flag during argument parsing. Only the accepted compatibility flag has a menu row. Noble also accepts an undocumented `--gpus=all` without exposing a device. Resolute documents NVIDIA devices and upstream 6.2 adds AMD. The two Ubuntu manuals call the default image-volume mode `bind`. Resolute’s packaged help reports `anonymous`, the upstream default name. Both names describe creating an anonymous volume. [Noble GPU compatibility implementation](https://github.com/containers/podman/blob/v4.9.3/cmd/podman/containers/run.go) · [Tagged flag definitions](https://github.com/containers/podman/blob/v6.2.0/cmd/podman/common/create.go) · [Packaged Noble help capture](../tests/fixtures/help/followup-systems/podman-run.txt)

## Option inventory

Each release column records a heading in that manual’s OPTIONS section. A dash records absence from that section. The Noble help capture contributes 155 independent spellings. Its manual also names the alias `--net`, which is absent from that help listing. Resolute adds 11 documented spellings to that set, and upstream adds the health interval alias. The separate health interval alias has its own row here. Short aliases and `--net` appear alongside the primary spelling. Value-taking rows insert only the literal flag.

| Manual option and aliases | Menu operand | Noble | Resolute | Upstream |
| --- | --- | :---: | :---: | :---: |
| `--add-host` | `HOST:IP` | ✓ | ✓ | ✓ |
| `--annotation` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--arch` | `ARCH` | ✓ | ✓ | ✓ |
| `--attach`, `-a` | `STREAM` | ✓ | ✓ | ✓ |
| `--authfile` | `FILE` | ✓ | ✓ | ✓ |
| `--blkio-weight` | `WEIGHT` | ✓ | ✓ | ✓ |
| `--blkio-weight-device` | `DEVICE:WEIGHT` | ✓ | ✓ | ✓ |
| `--cap-add` | `CAPABILITY` | ✓ | ✓ | ✓ |
| `--cap-drop` | `CAPABILITY` | ✓ | ✓ | ✓ |
| `--cert-dir` | `DIR` | — | ✓ | ✓ |
| `--cgroup-conf` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--cgroup-parent` | `PATH` | ✓ | ✓ | ✓ |
| `--cgroupns` | `MODE` | ✓ | ✓ | ✓ |
| `--cgroups` | `MODE` | ✓ | ✓ | ✓ |
| `--chrootdirs` | `PATH` | ✓ | ✓ | ✓ |
| `--cidfile` | `FILE` | ✓ | ✓ | ✓ |
| `--conmon-pidfile` | `FILE` | ✓ | ✓ | ✓ |
| `--cpu-period` | `USEC` | ✓ | ✓ | ✓ |
| `--cpu-quota` | `USEC` | ✓ | ✓ | ✓ |
| `--cpu-rt-period` | `USEC` | ✓ | ✓ | — |
| `--cpu-rt-runtime` | `USEC` | ✓ | ✓ | — |
| `--cpu-shares`, `-c` | `SHARES` | ✓ | ✓ | ✓ |
| `--cpus` | `CPUS` | ✓ | ✓ | ✓ |
| `--cpuset-cpus` | `CPU-LIST` | ✓ | ✓ | ✓ |
| `--cpuset-mems` | `NODE-LIST` | ✓ | ✓ | ✓ |
| `--creds` | `USER[:PASSWORD]` | — | ✓ | ✓ |
| `--decryption-key` | `KEY[:PASSPHRASE]` | ✓ | ✓ | ✓ |
| `--detach`, `-d` | — | ✓ | ✓ | ✓ |
| `--detach-keys` | `SEQUENCE` | ✓ | ✓ | ✓ |
| `--device` | `DEVICE` | ✓ | ✓ | ✓ |
| `--device-cgroup-rule` | `RULE` | ✓ | ✓ | ✓ |
| `--device-read-bps` | `PATH:RATE` | ✓ | ✓ | ✓ |
| `--device-read-iops` | `PATH:RATE` | ✓ | ✓ | ✓ |
| `--device-write-bps` | `PATH:RATE` | ✓ | ✓ | ✓ |
| `--device-write-iops` | `PATH:RATE` | ✓ | ✓ | ✓ |
| `--disable-content-trust` | — | ✓ | ✓ | ✓ |
| `--dns` | `ADDRESS` | ✓ | ✓ | ✓ |
| `--dns-option` | `OPTION` | ✓ | ✓ | ✓ |
| `--dns-search` | `DOMAIN` | ✓ | ✓ | ✓ |
| `--entrypoint` | `COMMAND` | ✓ | ✓ | ✓ |
| `--env`, `-e` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--env-file` | `FILE` | ✓ | ✓ | ✓ |
| `--env-host` | — | ✓ | ✓ | ✓ |
| `--env-merge` | `EXPRESSION` | ✓ | ✓ | ✓ |
| `--expose` | `PORT[/PROTO]` | ✓ | ✓ | ✓ |
| `--gidmap` | `[FLAGS]CONTAINER:FROM[:COUNT]` | ✓ | ✓ | ✓ |
| `--gpus` | `DEVICES` | — | ✓ | ✓ |
| `--group-add` | `GROUP` | ✓ | ✓ | ✓ |
| `--group-entry` | `ENTRY` | ✓ | ✓ | ✓ |
| `--health-cmd` | `COMMAND` | ✓ | ✓ | ✓ |
| `--health-interval` | `DURATION` | ✓ | ✓ | ✓ |
| `--health-log-destination` | `DESTINATION` | — | ✓ | ✓ |
| `--health-max-log-count` | `COUNT` | — | ✓ | ✓ |
| `--health-max-log-size` | `CHARACTERS` | — | ✓ | ✓ |
| `--health-on-failure` | `ACTION` | ✓ | ✓ | ✓ |
| `--health-retries` | `COUNT` | ✓ | ✓ | ✓ |
| `--health-start-interval` | `DURATION` | — | — | ✓ |
| `--health-start-period` | `DURATION` | ✓ | ✓ | ✓ |
| `--health-startup-cmd` | `COMMAND` | ✓ | ✓ | ✓ |
| `--health-startup-interval` | `DURATION` | ✓ | ✓ | ✓ |
| `--health-startup-retries` | `COUNT` | ✓ | ✓ | ✓ |
| `--health-startup-success` | `COUNT` | ✓ | ✓ | ✓ |
| `--health-startup-timeout` | `DURATION` | ✓ | ✓ | ✓ |
| `--health-timeout` | `DURATION` | ✓ | ✓ | ✓ |
| `--help` | — | ✓ | ✓ | ✓ |
| `--hostname`, `-h` | `NAME` | ✓ | ✓ | ✓ |
| `--hosts-file` | `FILE` | — | ✓ | ✓ |
| `--hostuser` | `USER` | ✓ | ✓ | ✓ |
| `--http-proxy` | — | ✓ | ✓ | ✓ |
| `--image-volume` | `MODE` | ✓ | ✓ | ✓ |
| `--init` | — | ✓ | ✓ | ✓ |
| `--init-path` | `PATH` | ✓ | ✓ | ✓ |
| `--interactive`, `-i` | — | ✓ | ✓ | ✓ |
| `--ip` | `ADDRESS` | ✓ | ✓ | ✓ |
| `--ip6` | `ADDRESS` | ✓ | ✓ | ✓ |
| `--ipc` | `MODE` | ✓ | ✓ | ✓ |
| `--label`, `-l` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--label-file` | `FILE` | ✓ | ✓ | ✓ |
| `--link-local-ip` | Unimplemented | ✓ | ✓ | ✓ |
| `--log-driver` | `DRIVER` | ✓ | ✓ | ✓ |
| `--log-opt` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--mac-address` | `MAC` | ✓ | ✓ | ✓ |
| `--memory`, `-m` | `SIZE` | ✓ | ✓ | ✓ |
| `--memory-reservation` | `SIZE` | ✓ | ✓ | ✓ |
| `--memory-swap` | `SIZE` | ✓ | ✓ | ✓ |
| `--memory-swappiness` | `LEVEL` | ✓ | ✓ | ✓ |
| `--mount` | `SPEC` | ✓ | ✓ | ✓ |
| `--name` | `NAME` | ✓ | ✓ | ✓ |
| `--network`, `--net` | `MODE` | ✓ | ✓ | ✓ |
| `--network-alias` | `NAME` | ✓ | ✓ | ✓ |
| `--no-healthcheck` | — | ✓ | ✓ | ✓ |
| `--no-hostname` | — | — | ✓ | ✓ |
| `--no-hosts` | — | ✓ | ✓ | ✓ |
| `--oom-kill-disable` | — | ✓ | ✓ | ✓ |
| `--oom-score-adj` | `SCORE` | ✓ | ✓ | ✓ |
| `--os` | `OS` | ✓ | ✓ | ✓ |
| `--passwd` | — | ✓ | ✓ | ✓ |
| `--passwd-entry` | `ENTRY` | ✓ | ✓ | ✓ |
| `--personality` | `PERSONA` | ✓ | ✓ | ✓ |
| `--pid` | `MODE` | ✓ | ✓ | ✓ |
| `--pidfile` | `FILE` | ✓ | ✓ | ✓ |
| `--pids-limit` | `LIMIT` | ✓ | ✓ | ✓ |
| `--platform` | `OS/ARCH` | ✓ | ✓ | ✓ |
| `--pod` | `NAME` | ✓ | ✓ | ✓ |
| `--pod-id-file` | `FILE` | ✓ | ✓ | ✓ |
| `--preserve-fd` | `FD-LIST` | — | ✓ | ✓ |
| `--preserve-fds` | `COUNT` | ✓ | ✓ | ✓ |
| `--privileged` | — | ✓ | ✓ | ✓ |
| `--publish`, `-p` | `PORT` | ✓ | ✓ | ✓ |
| `--publish-all`, `-P` | — | ✓ | ✓ | ✓ |
| `--pull` | `POLICY` | ✓ | ✓ | ✓ |
| `--quiet`, `-q` | — | ✓ | ✓ | ✓ |
| `--rdt-class` | `CLASS` | ✓ | ✓ | ✓ |
| `--read-only` | — | ✓ | ✓ | ✓ |
| `--read-only-tmpfs` | — | ✓ | ✓ | ✓ |
| `--replace` | — | ✓ | ✓ | ✓ |
| `--requires` | `CONTAINERS` | ✓ | ✓ | ✓ |
| `--restart` | `POLICY` | ✓ | ✓ | ✓ |
| `--retry` | `ATTEMPTS` | — | ✓ | ✓ |
| `--retry-delay` | `DURATION` | — | ✓ | ✓ |
| `--rm` | — | ✓ | ✓ | ✓ |
| `--rmi` | — | ✓ | ✓ | ✓ |
| `--rootfs` | — | ✓ | ✓ | ✓ |
| `--sdnotify` | `MODE` | ✓ | ✓ | ✓ |
| `--seccomp-policy` | `POLICY` | ✓ | ✓ | ✓ |
| `--secret` | `NAME[,OPTIONS]` | ✓ | ✓ | ✓ |
| `--security-opt` | `OPTION` | ✓ | ✓ | ✓ |
| `--shm-size` | `SIZE` | ✓ | ✓ | ✓ |
| `--shm-size-systemd` | `SIZE` | ✓ | ✓ | ✓ |
| `--sig-proxy` | — | ✓ | ✓ | ✓ |
| `--stop-signal` | `SIGNAL` | ✓ | ✓ | ✓ |
| `--stop-timeout` | `SECONDS` | ✓ | ✓ | ✓ |
| `--subgidname` | `NAME` | ✓ | ✓ | ✓ |
| `--subuidname` | `NAME` | ✓ | ✓ | ✓ |
| `--sysctl` | `KEY=VALUE` | ✓ | ✓ | ✓ |
| `--systemd` | `MODE` | ✓ | ✓ | ✓ |
| `--timeout` | `SECONDS` | ✓ | ✓ | ✓ |
| `--tls-verify` | — | ✓ | ✓ | ✓ |
| `--tmpfs` | `PATH[:OPTIONS]` | ✓ | ✓ | ✓ |
| `--tty`, `-t` | — | ✓ | ✓ | ✓ |
| `--tz` | `ZONE` | ✓ | ✓ | ✓ |
| `--uidmap` | `[FLAGS]CONTAINER:FROM[:COUNT]` | ✓ | ✓ | ✓ |
| `--ulimit` | `RESOURCE=SOFT[:HARD]` | ✓ | ✓ | ✓ |
| `--umask` | `MASK` | ✓ | ✓ | ✓ |
| `--unsetenv` | `NAME` | ✓ | ✓ | ✓ |
| `--unsetenv-all` | — | ✓ | ✓ | ✓ |
| `--user`, `-u` | `USER` | ✓ | ✓ | ✓ |
| `--userns` | `MODE` | ✓ | ✓ | ✓ |
| `--uts` | `MODE` | ✓ | ✓ | ✓ |
| `--variant` | `VARIANT` | ✓ | ✓ | ✓ |
| `--volume`, `-v` | `VOLUME` | ✓ | ✓ | ✓ |
| `--volumes-from` | `CONTAINER[:OPTIONS]` | ✓ | ✓ | ✓ |
| `--workdir`, `-w` | `DIR` | ✓ | ✓ | ✓ |

## Verification

The packaged 4.9.3 client advertised 155 spellings in its fixed help on both Noble targets. The packaged 5.7.0 client advertised 166 on Resolute. Every listed spelling matched the menu’s operand requirement. Both clients accepted the unlisted alias `--net=none` and rejected `--link-local-ip` and the upstream-only `--health-start-interval`. Noble accepted the unlisted compatibility spelling `--gpus=all`. These checks used help and argument parsing inside the offline sandbox. The manuals and tagged implementation supply the evidence for mount effects, GPU support and runtime defaults.

The screen regression opens the bundled menu in real Bash and tmux with discovery disabled. At 210×100 it visits each of the nine categories and checks the selected summary, every authored Details sentence and the formatted value guidance on all 168 rows. At 60×16 it searches for “private SELinux label”, checks both volume spellings and scrolls to the host UID/GID effect. Escape restores the original line and cursor. Enter inserts the literal `--volume` before the existing image operand with the cursor ready for a value. A shell function records any attempt to execute the pending command. [Rendered-menu regressions](../tests/test_podman_run_menu.py) · [Cross-release spelling regression](../tests/test_system_dependency_followup.py) · [Isolated sandbox procedure](development.md#isolated-local-debugging)

The numerical review compares promoted help-fixture observations with their new bundled declarations. The original help text and its version provenance are preserved. Strict coverage reconciles all 641 required contracts across the project, including the per-device rates and binary memory units. [Coverage review](numerical-inventory/review.json) · [Capture provenance regression](../tests/test_numerical_diagnostics.py)

An initial full run exposed an assumption in the installed-help regression that every bundled spelling appeared in a single 4.9.3 capture. The revised regression checks all 155 captured spellings plus the exact additions from the three manuals and rejects unexpected or duplicate rows. The fixture retains its original contents.

| Offline target | Python | Focused passed / failed / skipped | Full passed / failed / skipped | Full suite time |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 | 3.10.20 | 24 / 0 / 0 | 1,351 / 0 / 1 | 632.765 s |
| Ubuntu 24.04.5 | 3.12.3 | 24 / 0 / 0 | 1,351 / 0 / 1 | 564.341 s |
| Ubuntu 26.04.1 | 3.14.4 | 24 / 0 / 0 | 1,351 / 0 / 1 | 563.707 s |

The full suite included shell syntax, profile validation with both driver configurations, numerical coverage and unittest discovery. Each target skipped the Windows-only probe. Both new workspace files were included in the offline snapshots.
