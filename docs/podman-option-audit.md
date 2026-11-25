# Podman option audit

First recorded 2026-11-22. This first pass covered 44 bundled rows. See the [run inventory](podman-run-manual-coverage.md) and [build, exec and logs inventory](podman-build-exec-logs-manual-coverage.md) for the later manual comparison.

## Sources and versions

The first-pass comparison used Podman 6.2.0. Its structured value guidance was scoped to upstream 5.4.2. Ubuntu’s four Noble man pages identify package `4.9.3+ds1-1ubuntu0.2`, and its four Resolute pages identify `5.7.0+ds2-3build1`.

| Menu | Upstream 6.2.0 | Pinned 5.4.2 | Ubuntu 24.04 | Ubuntu 26.04 |
| --- | --- | --- | --- | --- |
| [run](../profiles/podman-run.json) | [run manual](https://docs.podman.io/en/v6.2.0/markdown/podman-run.1.html) | [run manual](https://docs.podman.io/en/v5.4.2/markdown/podman-run.1.html) | [Noble run(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-run.1.html) | [Resolute run(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-run.1.html) |
| [build](../profiles/podman-build.json) | [build manual](https://docs.podman.io/en/v6.2.0/markdown/podman-build.1.html) | [build manual](https://docs.podman.io/en/v5.4.2/markdown/podman-build.1.html) | [Noble build(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-build.1.html) | [Resolute build(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-build.1.html) |
| [exec](../profiles/podman-exec.json) | [exec manual](https://docs.podman.io/en/v6.2.0/markdown/podman-exec.1.html) | [exec manual](https://docs.podman.io/en/v5.4.2/markdown/podman-exec.1.html) | [Noble exec(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-exec.1.html) | [Resolute exec(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-exec.1.html) |
| [logs](../profiles/podman-logs.json) | [logs manual](https://docs.podman.io/en/v6.2.0/markdown/podman-logs.1.html) | [logs manual](https://docs.podman.io/en/v5.4.2/markdown/podman-logs.1.html) | [Noble logs(1)](https://manpages.ubuntu.com/manpages/noble/man1/podman-logs.1.html) | [Resolute logs(1)](https://manpages.ubuntu.com/manpages/resolute/man1/podman-logs.1.html) |

## Dispositions

### Run · 16 original entries

The run profile qualified resource limits and container configuration.

### Build · 10 entries

The pull-policy row inserted `--pull=` for an attached value. A separate word after bare `--pull` could become the build context.

### Exec · 10 entries

The audit distinguished execution inside an existing container from its creation-time options.

### Logs · 8 entries

A positive duration for `--since` counted backward from the client clock. The row also accepted calendar timestamps and Unix seconds.

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

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Minimum-size pull-policy regression](../tests/test_expansion_terminal.py) · [Live compatibility checker](../tests/live_compatibility.py)

Each target displayed all 44 highlighted rows and their complete Details in real Bash/tmux sessions at 210×100. The first reviews caught two omissions in the rendered text, a version qualifier and the `10m` example. The final renders include the corrected guidance. At 60×16, search and scrolling reached the port binding, pull policy, exec privilege and log cutoff explanations. Selection inserted `--publish`, `--pull=`, `--env` and `--since` before existing operands. Escape restored the original line and cursor for each menu. The shell stub recorded no Podman execution while browsing. [Minimum-size pull-policy regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

| Ubuntu | Python | Podman client | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | --- | --- | --- | --- | ---: |
| 24.04.5 | 3.10.20 | 4.9.3 | 17 / 0 / 0 | 1,349 / 0 / 1 | 569.071 s |
| 24.04.5 | 3.12.3 | 4.9.3 | 17 / 0 / 0 | 1,349 / 0 / 1 | 504.360 s |
| 26.04.1 | 3.14.4 | 5.7.0 | 17 / 0 / 0 | 1,349 / 0 / 1 | 504.316 s |

Each Linux suite skipped the Windows-specific probe.
