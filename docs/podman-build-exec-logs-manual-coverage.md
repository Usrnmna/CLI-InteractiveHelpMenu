# Podman build, exec and logs manual coverage

The three revisits add 143 rows. Build grew from 10 to 134 (124 added rows, 120 options and 14 aliases), exec from 10 to 23 (13 added rows, 15 options and eight aliases), and logs from eight to 14 (six added rows, nine options and five aliases). The tables reconcile the public manuals with the exact command's packaged help. The original declaration fixtures and the separately captured Noble help remain independent evidence. [First-pass Podman audit](podman-option-audit.md) · [Noble capture provenance](../tests/fixtures/help/followup-systems/manifest.json)

Each release column records the **OPTIONS heading**, including aliases attached to it. A dash means there is no heading in that manual. Operand labels follow the manuals or fixed help where a heading omits the value. A dash in the operand column means a switch, including Boolean switches accepting an explicit attached value. An optional policy uses brackets. Additional aliases identified in tagged source appear beside their primary spelling and are qualified below.

## Build inventory

[Upstream build(1), 6.2.0](https://docs.podman.io/en/v6.2.0/markdown/podman-build.1.html#options) · [Noble build(1), 4.9.3+ds1-1ubuntu0.2](https://manpages.ubuntu.com/manpages/noble/man1/podman-build.1.html) · [Resolute build(1), 5.7.0+ds2-3build1](https://manpages.ubuntu.com/manpages/resolute/man1/podman-build.1.html)

All three manuals describe the inherited parent option `--runtime PATH`. Use it before `build` to choose the OCI runtime. The command-specific `--runtime-flag` takes an argument for that runtime. Buildah’s flag registration explicitly leaves runtime selection to Podman. The 97 Noble, 112 Resolute and 121 upstream headings include that parent option. The remaining 120 upstream headings cover the full three-manual union for this command. [Podman build option translation](https://github.com/podman-container-tools/podman/blob/v6.2.0/cmd/podman/common/build.go) · [Buildah flag registration and alias normalization](https://github.com/podman-container-tools/podman/blob/v6.2.0/vendor/go.podman.io/buildah/pkg/cli/common.go)

The clients omit the documented `--net`, `--help` and `-h` from fixed help. The Buildah normalizer also accepts the unlisted aliases `--override-arch`, `--override-os` and `--purge`. Upstream 6.2 adds `--raw-iidfile` for `--iidfile-raw`. The documented `--compress` and `--disable-content-trust` are compatibility no-ops. The hidden buildx compatibility flags `--load` and `--progress`, and internal/deprecated Buildah flags outside the manuals and public fixed help, have no separate menu rows. The normalizer’s `--tty` maps to a flag that these build commands do not register. Containerfile instructions such as `RUN --mount` and `COPY --from` belong to the file. Only 6.2 offers a build CLI `--mount` to apply a mount to every RUN. [Noble flag registration](https://github.com/podman-container-tools/podman/blob/v4.9.3/vendor/github.com/containers/buildah/pkg/cli/common.go) · [Resolute flag registration](https://github.com/podman-container-tools/podman/blob/v5.7.0/vendor/github.com/containers/buildah/pkg/cli/common.go)

The menu distinguishes the positional context supplying COPY/ADD files from the instruction file supplied with `-f`. A manifest list collects results from multiple platforms. A build argument supplies an ARG value. A secret mount exposes data to a RUN step. The mount itself is temporary, but a command can still copy its contents into a layer. Changing the secret contents alone does not invalidate the cached step. Noble documents the file form. Its tagged Buildah parser already accepts `env=NAME` and `type=file|env`, which also appear in the newer manuals. Cache reuse and registry pull policy have separate controls. The packaged clients send `always` for bare `--pull` and `missing` for `newer`. For `false`, Noble sends `missing` and Resolute sends `never`. Upstream 6.2 implements the newer-image policy. The literal selection remains `--pull=`. [Noble secret parser](https://github.com/podman-container-tools/podman/blob/v4.9.3/vendor/github.com/containers/buildah/pkg/parse/parse.go) · [Original pull-policy recorder results and tagged translations](podman-option-audit.md#version-differences-and-executable-evidence)

The help syntax and flag registration resolve missing metavariables for options such as `--format`, `--from`, `--ignorefile` and `--cache-ttl`. The `--sbom-scanner-command=image` heading takes a scanner **command**. The separate scanner-image option selects its executable environment. Boolean options with a manual heading ending in `=bool-value` work bare. Upstream describes an explicit compression format as enabling forced compression by default, but its CLI translation sets the implicit force flag in the configured-format branch. The menu specifies the explicit switch where that distinction matters. [6.2 compression translation](https://github.com/podman-container-tools/podman/blob/v6.2.0/cmd/podman/common/build.go)

| Spellings | Operand | Noble | Resolute | 6.2 |
| --- | --- | --- | --- | --- |
| `--add-host` | `hostname[;hostname[;…]]:ip` | ✓ | ✓ | ✓ |
| `--all-platforms` | — | ✓ | ✓ | ✓ |
| `--annotation` | `annotation=value` | ✓ | ✓ | ✓ |
| `--arch`, `--override-arch` | `arch` | ✓ | ✓ | ✓ |
| `--authfile` | `path` | ✓ | ✓ | ✓ |
| `--build-arg` | `arg=value` | ✓ | ✓ | ✓ |
| `--build-arg-file` | `path` | ✓ | ✓ | ✓ |
| `--build-context` | `name=value` | ✓ | ✓ | ✓ |
| `--cache-from` | `image` | ✓ | ✓ | ✓ |
| `--cache-to` | `image` | ✓ | ✓ | ✓ |
| `--cache-ttl` | `DURATION` | ✓ | ✓ | ✓ |
| `--cap-add` | `CAP_xxx` | ✓ | ✓ | ✓ |
| `--cap-drop` | `CAP_xxx` | ✓ | ✓ | ✓ |
| `--cert-dir` | `path` | ✓ | ✓ | ✓ |
| `--cgroup-parent` | `path` | ✓ | ✓ | ✓ |
| `--cgroupns` | `how` | ✓ | ✓ | ✓ |
| `--compat-volumes` | — | — | ✓ | ✓ |
| `--compress` | — | ✓ | ✓ | ✓ |
| `--compression-format` | `gzip\|zstd\|zstd:chunked` | — | — | ✓ |
| `--compression-level` | `level` | — | — | ✓ |
| `--cpp-flag` | `flags` | ✓ | ✓ | ✓ |
| `--cpu-period` | `limit` | ✓ | ✓ | ✓ |
| `--cpu-quota` | `limit` | ✓ | ✓ | ✓ |
| `--cpu-shares`, `-c` | `shares` | ✓ | ✓ | ✓ |
| `--cpuset-cpus` | `number` | ✓ | ✓ | ✓ |
| `--cpuset-mems` | `nodes` | ✓ | ✓ | ✓ |
| `--created-annotation` | — | — | ✓ | ✓ |
| `--creds` | `USER[:PASSWORD]` | ✓ | ✓ | ✓ |
| `--cw` | `options` | ✓ | ✓ | ✓ |
| `--decryption-key` | `key[:passphrase]` | ✓ | ✓ | ✓ |
| `--device` | `host-device[:container-device][:permissions]` | ✓ | ✓ | ✓ |
| `--disable-compression`, `-D` | — | ✓ | ✓ | ✓ |
| `--disable-content-trust` | — | ✓ | ✓ | ✓ |
| `--dns` | `ipaddr` | ✓ | ✓ | ✓ |
| `--dns-option` | `option` | ✓ | ✓ | ✓ |
| `--dns-search` | `domain` | ✓ | ✓ | ✓ |
| `--env` | `env[=value]` | ✓ | ✓ | ✓ |
| `--file`, `-f` | `Containerfile` | ✓ | ✓ | ✓ |
| `--force-compression` | — | — | — | ✓ |
| `--force-rm` | — | ✓ | ✓ | ✓ |
| `--format` | `format` | ✓ | ✓ | ✓ |
| `--from` | `IMAGE` | ✓ | ✓ | ✓ |
| `--group-add` | `group\|keep-groups` | ✓ | ✓ | ✓ |
| `--help`, `-h` | — | ✓ | ✓ | ✓ |
| `--hooks-dir` | `path` | ✓ | ✓ | ✓ |
| `--http-proxy` | — | ✓ | ✓ | ✓ |
| `--identity-label` | — | ✓ | ✓ | ✓ |
| `--ignorefile` | `FILE` | ✓ | ✓ | ✓ |
| `--iidfile` | `ImageIDfile` | ✓ | ✓ | ✓ |
| `--iidfile-raw`, `--raw-iidfile` | `ImageIDfile` | — | — | ✓ |
| `--inherit-annotations` | — | — | ✓ | ✓ |
| `--inherit-labels` | — | — | ✓ | ✓ |
| `--ipc` | `how` | ✓ | ✓ | ✓ |
| `--isolation` | `type` | ✓ | ✓ | ✓ |
| `--jobs` | `number` | ✓ | ✓ | ✓ |
| `--label` | `label` | ✓ | ✓ | ✓ |
| `--layer-label` | `label[=value]` | ✓ | ✓ | ✓ |
| `--layers` | — | ✓ | ✓ | ✓ |
| `--logfile` | `filename` | ✓ | ✓ | ✓ |
| `--logsplit` | — | ✓ | ✓ | ✓ |
| `--manifest` | `manifest` | ✓ | ✓ | ✓ |
| `--memory`, `-m` | `number[unit]` | ✓ | ✓ | ✓ |
| `--memory-swap` | `number[unit]` | ✓ | ✓ | ✓ |
| `--metadata-file` | `MetadataFile` | — | — | ✓ |
| `--mount` | `mount-specification` | — | — | ✓ |
| `--network`, `--net` | `mode` | ✓ | ✓ | ✓ |
| `--no-cache` | — | ✓ | ✓ | ✓ |
| `--no-hostname` | — | ✓ | ✓ | ✓ |
| `--no-hosts` | — | ✓ | ✓ | ✓ |
| `--omit-history` | — | ✓ | ✓ | ✓ |
| `--os`, `--override-os` | `string` | ✓ | ✓ | ✓ |
| `--os-feature` | `feature` | ✓ | ✓ | ✓ |
| `--os-version` | `version` | ✓ | ✓ | ✓ |
| `--output`, `-o` | `output-opts` | ✓ | ✓ | ✓ |
| `--pid` | `pid` | ✓ | ✓ | ✓ |
| `--platform` | `os/arch[/variant][,…]` | ✓ | ✓ | ✓ |
| `--pull` | `[=POLICY]` | ✓ | ✓ | ✓ |
| `--quiet`, `-q` | — | ✓ | ✓ | ✓ |
| `--retry` | `attempts` | ✓ | ✓ | ✓ |
| `--retry-delay` | `duration` | ✓ | ✓ | ✓ |
| `--rewrite-timestamp` | — | — | ✓ | ✓ |
| `--rm`, `--purge` | — | ✓ | ✓ | ✓ |
| `--runtime` | `PATH (parent)` | ✓ | ✓ | ✓ |
| `--runtime-flag` | `flag` | ✓ | ✓ | ✓ |
| `--save-stages` | — | — | — | ✓ |
| `--sbom` | `preset` | — | ✓ | ✓ |
| `--sbom-image-output` | `path` | — | ✓ | ✓ |
| `--sbom-image-purl-output` | `path` | — | ✓ | ✓ |
| `--sbom-merge-strategy` | `method` | — | ✓ | ✓ |
| `--sbom-output` | `file` | — | ✓ | ✓ |
| `--sbom-purl-output` | `file` | — | ✓ | ✓ |
| `--sbom-scanner-command` | `COMMAND` | — | ✓ | ✓ |
| `--sbom-scanner-image` | `image` | — | ✓ | ✓ |
| `--secret` | `id=id[,src=envOrFile][,env=ENV][,type=file\|env]` | ✓ | ✓ | ✓ |
| `--security-opt` | `option` | ✓ | ✓ | ✓ |
| `--shm-size` | `number[unit]` | ✓ | ✓ | ✓ |
| `--sign-by` | `fingerprint` | ✓ | ✓ | ✓ |
| `--skip-unused-stages` | — | ✓ | ✓ | ✓ |
| `--source-date-epoch` | `seconds` | — | ✓ | ✓ |
| `--source-policy-file` | `pathname` | — | — | ✓ |
| `--squash` | — | ✓ | ✓ | ✓ |
| `--squash-all` | — | ✓ | ✓ | ✓ |
| `--ssh` | `default\|ID[=SOCKET\|KEY[,KEY…]]` | ✓ | ✓ | ✓ |
| `--stage-labels` | — | — | — | ✓ |
| `--stdin` | — | ✓ | ✓ | ✓ |
| `--tag`, `-t` | `imageName` | ✓ | ✓ | ✓ |
| `--target` | `stageName` | ✓ | ✓ | ✓ |
| `--timestamp` | `seconds` | ✓ | ✓ | ✓ |
| `--tls-verify` | — | ✓ | ✓ | ✓ |
| `--ulimit` | `type=soft-limit[:hard-limit]` | ✓ | ✓ | ✓ |
| `--unsetannotation` | `annotation` | — | ✓ | ✓ |
| `--unsetenv` | `env` | ✓ | ✓ | ✓ |
| `--unsetlabel` | `label` | ✓ | ✓ | ✓ |
| `--userns` | `how` | ✓ | ✓ | ✓ |
| `--userns-gid-map` | `mapping` | ✓ | ✓ | ✓ |
| `--userns-gid-map-group` | `group` | ✓ | ✓ | ✓ |
| `--userns-uid-map` | `mapping` | ✓ | ✓ | ✓ |
| `--userns-uid-map-user` | `user` | ✓ | ✓ | ✓ |
| `--uts` | `how` | ✓ | ✓ | ✓ |
| `--variant` | `VARIANT` | ✓ | ✓ | ✓ |
| `--volume`, `-v` | `HOST-DIR:CONTAINER-DIR[:OPTIONS]` | ✓ | ✓ | ✓ |

## Exec inventory

[Upstream exec(1), 6.2.0](https://docs.podman.io/en/v6.2.0/markdown/podman-exec.1.html#options) · [Noble exec(1), 4.9.3+ds1-1ubuntu0.2](https://manpages.ubuntu.com/manpages/noble/man1/podman-exec.1.html) · [Resolute exec(1), 5.7.0+ds2-3build1](https://manpages.ubuntu.com/manpages/resolute/man1/podman-exec.1.html)

Noble has 11 option headings, Resolute 13 and upstream 14. The packaged clients also accept the unlisted usage switches `--help` and `-h`. The CLI stops flag parsing at the first positional word. For a named container the following word is the child command. With `--latest` or `--cidfile FILE`, omit the positional container and start the child command immediately. A child’s `--help` belongs to the child. The hidden implementation switch `--wait` is outside the manual and public fixed-help inventory. [Upstream exec argument handling](https://github.com/podman-container-tools/podman/blob/v6.2.0/cmd/podman/containers/exec.go) · [Noble exec parser](https://github.com/podman-container-tools/podman/blob/v4.9.3/cmd/podman/containers/exec.go)

Files passed to `--env-file` are read in order. Explicit `--env` settings take precedence even when they occur earlier on the command line. A detached exec prints an exec session ID. A pipe needs stdin via `-i`. Allocating a terminal with `-t` also merges the output streams. Local clients can select the latest container or pass inherited file descriptors. Resolute adds container ID files and the crun-specific descriptor list. Upstream adds local `--no-session`, which conflicts with detach and explicit detach keys. [Resolute exec option handling](https://github.com/podman-container-tools/podman/blob/v5.7.0/cmd/podman/containers/exec.go)

| Spellings | Operand | Noble | Resolute | 6.2 |
| --- | --- | --- | --- | --- |
| `--cidfile` | `file` | — | ✓ | ✓ |
| `--detach`, `-d` | — | ✓ | ✓ | ✓ |
| `--detach-keys` | `sequence` | ✓ | ✓ | ✓ |
| `--env`, `-e` | `env` | ✓ | ✓ | ✓ |
| `--env-file` | `file` | ✓ | ✓ | ✓ |
| `--help`, `-h` | — | — | — | — |
| `--interactive`, `-i` | — | ✓ | ✓ | ✓ |
| `--latest`, `-l` | — | ✓ | ✓ | ✓ |
| `--no-session` | — | — | — | ✓ |
| `--preserve-fd` | `FD1[,FD2,…]` | — | ✓ | ✓ |
| `--preserve-fds` | `N` | ✓ | ✓ | ✓ |
| `--privileged` | — | ✓ | ✓ | ✓ |
| `--tty`, `-t` | — | ✓ | ✓ | ✓ |
| `--user`, `-u` | `user[:group]` | ✓ | ✓ | ✓ |
| `--workdir`, `-w` | `dir` | ✓ | ✓ | ✓ |

## Logs inventory

[Upstream logs(1), 6.2.0](https://docs.podman.io/en/v6.2.0/markdown/podman-logs.1.html#options) · [Noble logs(1), 4.9.3+ds1-1ubuntu0.2](https://manpages.ubuntu.com/manpages/noble/man1/podman-logs.1.html) · [Resolute logs(1), 5.7.0+ds2-3build1](https://manpages.ubuntu.com/manpages/resolute/man1/podman-logs.1.html)

All three manuals have the same eight headings and four documented aliases. Fixed help omits the accepted usage switches `--help` and `-h`. Command validation permits several explicit container names or IDs locally and only one remotely. Local `--latest` selects by creation order and excludes explicit container operands. The log formatter prefixes multi-container output with IDs by default or names with `-n`. The example’s `--rm` belongs to `podman run`. Removing the followed container can discard its final unread lines. The hidden implementation flag `--details` is outside all three public inventories. [Noble argument validation](https://github.com/podman-container-tools/podman/blob/v4.9.3/cmd/podman/containers/logs.go) · [Upstream argument validation](https://github.com/podman-container-tools/podman/blob/v6.2.0/cmd/podman/containers/logs.go) · [Upstream log formatter](https://github.com/podman-container-tools/podman/blob/v6.2.0/libpod/logs/log.go)

`--tail=-1` selects all available lines. Positive durations count backward for `--since` and forward for `--until`. Negative durations reverse those directions. Both use the client clock. Unix seconds may include a fraction. Calendar timestamps without a zone use UTC. [Resolute time parser](https://github.com/podman-container-tools/podman/blob/v5.7.0/pkg/util/utils.go)

| Spellings | Operand | Noble | Resolute | 6.2 |
| --- | --- | --- | --- | --- |
| `--color` | — | ✓ | ✓ | ✓ |
| `--follow`, `-f` | — | ✓ | ✓ | ✓ |
| `--help`, `-h` | — | — | — | — |
| `--latest`, `-l` | — | ✓ | ✓ | ✓ |
| `--names`, `-n` | — | ✓ | ✓ | ✓ |
| `--since` | `TIMESTAMP` | ✓ | ✓ | ✓ |
| `--tail` | `LINES` | ✓ | ✓ | ✓ |
| `--timestamps`, `-t` | — | ✓ | ✓ | ✓ |
| `--until` | `TIMESTAMP` | ✓ | ✓ | ✓ |

## Verification

The packaged clients' fixed help advertised 103 build, 18 exec and 12 logs spellings on Noble, and 118, 20 and 12 on Resolute. Each spelling and its switch, required-value or optional-value form matched the menu on all three offline targets. The Noble package also matched its repository captures. Both clients accepted build’s unlisted `--net`, `--override-arch`, `--override-os` and `--purge`, as well as the inherited runtime option and the hidden usage switches. Both rejected build’s `--tty`, `--source-policy-file` and `--raw-iidfile`, and exec’s `--no-session`. Resolute accepted build’s `--sbom` and exec’s `--cidfile`. Noble rejected both. Only fixed help or a private recorder was used for these client checks.

For the six pull-policy cases, each client sent the expected policy in five requests and rejected the two-context invocation before dispatch. Both positive and negative ten-minute log windows produced the expected opposite offsets for since and until. Remote logs rejected multiple containers and latest selection. For exec, the recorder received the exact child argument vector `["child", "--env", "arg", "--help"]`. A command-line variable overrode the same key in a later environment file, and the file’s other variable reached the request. The recorder returned a deliberate error before creating an exec process, building an image or reading a log. The mount, storage and scanner effects described above come from manuals and source.

At 210×100, real Bash/tmux sessions with discovery disabled compared the selected summary and complete Details for all 134 build, 23 exec and 14 logs rows. The screen checks include formatted value guidance. At 60×16, search and scrolling reached the secret cache rule, environment-file precedence and signed log cutoff. Escape restored the original line and cursor. Enter inserted `--secret` before the build context, `--env-file` before the container and child command, and `--until` before the container list. A separate narrow test inserted `--pull=never`. The exec test requested help at a child argument and verified the boundary diagnostic and intact child command. The Podman shell stub recorded no execution. [Terminal checks](../tests/test_podman_run_menu.py) · [Pull-policy insertion](../tests/test_expansion_terminal.py)

The numerical review reconciled 191 changed source identities across the three profiles. Existing fixture, capture and matrix observations matched the pre-edit inventory. Strict coverage accepted all 751 required contracts across the workspace. [Inventory review](numerical-inventory/review.json) · [Manual and capture regression](../tests/test_system_dependency_followup.py) · [Offline sandbox procedure](development.md#isolated-local-debugging)

| Offline sandbox | Python | Podman | Focused passed / failed / skipped | Full passed / failed / skipped | Full suite time |
| --- | --- | --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 (`host`) | 3.14.4 | 5.7.0 | 28 / 0 / 0 | 1,354 / 0 / 1 | 641.299 s |
| Ubuntu 24.04.5 (`noble310`) | 3.10.20 | 4.9.3 | 28 / 0 / 0 | 1,354 / 0 / 1 | 711.835 s |
| Ubuntu 24.04.5 (`noble312`) | 3.12.3 | 4.9.3 | 28 / 0 / 0 | 1,354 / 0 / 1 | 638.665 s |

All three full runs included the new inventory document in the offline snapshot. Each skipped the Windows-only probe. All three menus meet the manual coverage and rendered Details criteria. The upstream compression-default discrepancy is recorded in the build inventory.
