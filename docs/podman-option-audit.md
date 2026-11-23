# Podman option audit

The manual revisits cover [build](podman-build-exec-logs-manual-coverage.md#build-inventory), [exec](podman-build-exec-logs-manual-coverage.md#exec-inventory) and [logs](podman-build-exec-logs-manual-coverage.md#logs-inventory). Their [verification results](podman-build-exec-logs-manual-coverage.md#verification) cover the expanded menus.

The first pass covered 44 selectable entries across four menus. The [run manual-coverage revisit](podman-run-manual-coverage.md) records the expanded inventory and updated verification. Short and long aliases occupy separate rows. The main syntax correction is in `podman build`. Selecting the pull policy now inserts `--pull=` and places the cursor after the equals sign. Typing a bare `--pull` remains valid. A space before a policy turns that word into a build-context operand.

## Sources and versions

The first-pass comparison used Podman 6.2.0. Its structured value guidance was scoped to upstream 5.4.2. Ubuntu’s four Noble man pages identify package `4.9.3+ds1-1ubuntu0.2`, and its four Resolute pages identify `5.7.0+ds2-3build1`.

| Menu | Upstream 6.2.0 | Pinned 5.4.2 | Ubuntu 24.04 | Ubuntu 26.04 |
| --- | --- | --- | --- | --- |
| [run](../profiles/podman-run.json) | [run manual](https://docs.podman.io/en/v6.2.0/markdown/podman-run.1.html) | [run manual](https://docs.podman.io/en/v5.4.2/markdown/podman-run.1.html) | [Noble run(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-run.1.html) | [Resolute run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-run.1.html) |
| [build](../profiles/podman-build.json) | [build manual](https://docs.podman.io/en/v6.2.0/markdown/podman-build.1.html) | [build manual](https://docs.podman.io/en/v5.4.2/markdown/podman-build.1.html) | [Noble build(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-build.1.html) | [Resolute build(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-build.1.html) |
| [exec](../profiles/podman-exec.json) | [exec manual](https://docs.podman.io/en/v6.2.0/markdown/podman-exec.1.html) | [exec manual](https://docs.podman.io/en/v5.4.2/markdown/podman-exec.1.html) | [Noble exec(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-exec.1.html) | [Resolute exec(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-exec.1.html) |
| [logs](../profiles/podman-logs.json) | [logs manual](https://docs.podman.io/en/v6.2.0/markdown/podman-logs.1.html) | [logs manual](https://docs.podman.io/en/v5.4.2/markdown/podman-logs.1.html) | [Noble logs(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-logs.1.html) | [Resolute logs(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-logs.1.html) |

## Dispositions

Each disposition applies to the original wording and value guidance of every listed spelling.

### Run · 16 original entries

| Spelling | Disposition | Finding |
| --- | --- | --- |
| `--detach`, `-d` | Incomplete | Starting in the background prints the **container ID**. It can be used to reattach. |
| `--interactive`, `-i` | Incomplete | Makes stdin available to the container. Use this flag alone for piped input. |
| `--tty`, `-t` | Incomplete | Allocates a pseudo-terminal, which merges stdout and stderr and can add control characters. |
| `--name` | Sufficient | Retains the summary. The generated name is the default, and either name can identify the container in later commands. |
| `--env`, `-e` | Redundant | Retains assignment and host lookup, removes repeated numerical disclaimers. Quoting a prefix wildcard passes it to Podman for matching. |
| `--publish`, `-p` | Incomplete | Distinguishes the host address, host port and container port. A loopback address restricts the listener. Omitting the address normally binds all host addresses. An omitted host port is assigned automatically. Details retain equal-length ranges and protocol choices. |
| `--volume`, `-v` | Incomplete | A host path, named volume and destination-only anonymous volume have different lifetimes. The destination is absolute. Mounts default to writable, and `:ro` selects read-only access. |
| `--rm` | Incomplete | Exit removes the container and its anonymous volumes. Named volumes and bind-mounted host files persist. |
| `--workdir` | Incomplete | Sets the directory inside the container. The image’s WORKDIR supplies the default, otherwise it is `/`. |
| `--user` | Redundant | Keeps the useful `USER[:GROUP]` and UID/GID mappings. Removes the repeated explanation about numerical units. |

### Build · 10 entries

| Spelling | Disposition | Finding |
| --- | --- | --- |
| `--tag`, `-t` | Sufficient | Retains the summary. Podman qualifies an image name without a registry with `localhost`. |
| `--file`, `-f` | Incomplete | Accepts a local file, an HTTP(S) URL, or `-` for stdin. With one local Containerfile and no explicit context, its parent directory becomes the context. |
| `--build-arg` | Redundant | The value feeds a Containerfile ARG. Setting the argument alone creates no environment entry in the resulting image. |
| `--no-cache` | Incomplete | Rebuilds layers. Refreshing a base image is a separate pull-policy decision. |
| `--pull` | Inaccurate | The old row displayed a space before POLICY and the pinned 5.4.2 metadata assigned the wrong bare-flag policy. The row now displays `--pull=POLICY` and explains the tested Ubuntu behavior. |
| `--target` | Incomplete | Names the stage from `FROM … AS name`. An intermediate stage can become the build result. |
| `--platform` | Incomplete | Selects OS, architecture and optional variant. Multiple platforms use a manifest list. Foreign-architecture RUN steps may need emulation. |
| `--quiet` | Incomplete | Suppresses instruction, pull and write progress. Errors remain visible. |

### Exec · 10 entries

| Spelling | Disposition | Finding |
| --- | --- | --- |
| `--interactive`, `-i` | Incomplete | Makes stdin available to the new command in the existing container. This suffices for piped input. |
| `--tty`, `-t` | Incomplete | Allocates a terminal for the command. Its output streams merge. |
| `--detach` | Incomplete | Prints the **exec session ID**. The session is removed when the command finishes. |
| `--env`, `-e` | Redundant | An assignment or a host-variable lookup sets the environment for this command. Removes repeated generic value guidance. |
| `--workdir` | Incomplete | Changes the working directory for this exec session. |
| `--user` | Redundant | Retains user and optional group names or IDs and explains how a namespace affects host IDs. |
| `--privileged` | Incomplete | On Linux the option requests all available capabilities for the exec process’s bounding set. The launching user still limits a rootless process. [Podman 5.7 exec capability selection](https://github.com/containers/podman/blob/v5.7.0/libpod/oci_conmon_exec_linux.go) |

### Logs · 8 entries

| Spelling | Disposition | Finding |
| --- | --- | --- |
| `--follow`, `-f` | Incomplete | Continues reading new output. Removing the container, including automatic removal with `--rm`, can discard the final unread lines. |
| `--timestamps` | Sufficient | Each log line can display its recorded time. |
| `--tail` | Redundant | Retains the integer line count and the default `-1` for all lines. |
| `--since` | Incomplete | A positive duration counts backward from the client clock. The menu retains Unix seconds and calendar/RFC3339 forms. |
| `--until` | Incomplete | A positive duration counts forward. For a cutoff ten minutes ago, use `--until=-10m`. |
| `--names` | Incomplete | Replaces IDs in multi-container log prefixes with names. [Podman log formatter](https://github.com/containers/podman/blob/v5.7.0/libpod/logs/log.go) |
| `--color` | Incomplete | Uses color to distinguish the containers producing the output. |

## Version differences and executable evidence

Noble’s build manual calls both `always` and `missing` the default and describes `false` as an alias for `never`. Both Ubuntu manuals describe `newer` as a digest comparison. To resolve these discrepancies, each offline sandbox ran its release’s actual Podman client in remote mode against a private Unix-socket recorder. The recorder captured each request and returned an intentional error before any build or log retrieval. The measurements establish CLI parsing and forwarding. [Podman 4.9.3 build translation](https://github.com/containers/podman/blob/v4.9.3/cmd/podman/common/build.go) · [5.7.0 translation](https://github.com/containers/podman/blob/v5.7.0/cmd/podman/common/build.go)

| Build invocation | Ubuntu 24.04 client 4.9.3 | Ubuntu 26.04 client 5.7.0 |
| --- | --- | --- |
| Policy omitted | Sent `missing` | Sent `missing` |
| Bare `--pull` | Sent `always` | Sent `always` |
| `--pull=never` | Sent `never` | Sent `never` |
| `--pull=newer` | Sent `missing` | Sent `missing` |
| `--pull=false` | Sent `missing` | Sent `never` |
| `--pull never .` | Rejected two context operands before sending a request | Same |

The upstream 5.4.2 flag registration assigns `missing` to the bare flag. Its build translation also maps `newer` to `missing`. In 6.2.0 the translation explicitly selects the newer-image policy for `newer`. These two comparisons come from tagged source. [5.4.2 flag registration](https://github.com/containers/podman/blob/v5.4.2/vendor/github.com/containers/buildah/pkg/cli/common.go) · [5.4.2 build translation](https://github.com/containers/podman/blob/v5.4.2/cmd/podman/common/build.go) · [6.2.0 build translation](https://github.com/containers/podman/blob/v6.2.0/cmd/podman/common/build.go)

Each Ubuntu client sent a log window starting ten minutes before its clock and ending ten minutes after it for `--since 10m --until 10m`. The parser also accepts fractional Unix seconds and treats a calendar timestamp without a zone as UTC. [5.4.2 log command](https://github.com/containers/podman/blob/v5.4.2/cmd/podman/containers/logs.go) · [5.4.2 time parser](https://github.com/containers/podman/blob/v5.4.2/pkg/util/utils.go)

The newer upstream run manual allows a configured default host bind address. Supplying the address explicitly keeps port publication predictable across the releases. At the end of the first pass, examples of manual-only coverage included run’s `--network` and `--mount`, build’s `--manifest` and `--secret`, exec’s `--env-file` and `--detach-keys`, and logs’ `--latest`. The first-pass baseline was 44 rows. [6.2.0 port publication](https://github.com/containers/podman/blob/v6.2.0/docs/source/markdown/options/publish.md)

## Rendered menus and offline verification

Each target displayed all 44 highlighted rows and their complete Details in real Bash/tmux sessions at 210×100. The first reviews caught two omissions in the rendered text, a version qualifier and the `10m` example. The final renders include the corrected guidance. At 60×16, search and scrolling reached the port binding, pull policy, exec privilege and log cutoff explanations. Selection inserted `--publish`, `--pull=`, `--env` and `--since` before existing operands. Escape restored the original line and cursor for each menu. The shell stub recorded no Podman execution while browsing. [Minimum-size pull-policy regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The four fixed help routes and their literal-insertion checks passed against the packaged Podman client on each target. The 63 refreshed inventory fingerprints cover 44 options, four categories, four command descriptions, four shared value definitions, four profile files, the build route and two declaration fixture files. [Live compatibility checker](../tests/live_compatibility.py) · [Numerical review](numerical-inventory/review.json)

| Ubuntu | Python | Podman client | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | --- | ---: |
| 24.04.5 | 3.10.20 | 4.9.3 | 17 / 0 / 0 | 1,349 / 0 / 1 | 569.071 s |
| 24.04.5 | 3.12.3 | 4.9.3 | 17 / 0 / 0 | 1,349 / 0 / 1 | 504.360 s |
| 26.04.1 | 3.14.4 | 5.7.0 | 17 / 0 / 0 | 1,349 / 0 / 1 | 504.316 s |

The full runs included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. The single skip on each target was the Windows-only probe.
