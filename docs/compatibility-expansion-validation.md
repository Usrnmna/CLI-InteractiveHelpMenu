# Complete compatibility expansion validation

[Project overview](../README.md) · [Complete route matrix](compatibility.md) ·
[Supported invocation grammar](invocation-and-structured-arguments.md)

Recorded on 2026-10-23 in America/Los_Angeles (2026-10-24 UTC). This report
describes that dated snapshot. No commit, push, hosted release, or publication occurred.
The [current compatibility guide](compatibility.md) includes later workflow and
Unix corpus additions; the counts and test results below retain their original
scope and are not evidence of a new run against those additions.

## Completed dependency follow-up

All **30 previously skipped routes passed** after isolated local installation.
The complete maintained inventory was then rerun: **128 passed, zero failed,
zero skipped, and one expected unsupported npm-root case**, across 129 paths and
62 executable names. Current and legacy esptool routes use separate environments.
The original expansion snapshot's 98 passes and 30 dependency skips are superseded
by this completed run; its raw local reports remain available as historical evidence.

| Evidence layer | Result and scope |
| --- | --- |
| Full Linux suite | 524 tests: 523 passed, one Windows-only probe test skipped; zero failures/errors |
| Snapshot integrity | 389 maintained files copied byte-for-byte to an isolated Linux filesystem; checkout fingerprints unchanged during tests |
| Previously missing tools | All 30 routes passed fixed help/version and in-memory insertion checks |
| Full live matrix | 128 passed, one documented unsupported npm-root case; no missing executables |
| Probe audit | 304 requests checked against exact per-route help/manual/version allowlists; no pending operands forwarded |
| Terminal evidence | Real Bash PTY/tmux cells, cursor, cancellation, resizing, Unicode, scrollback, and optional-number argument entry passed |
| GitHub configuration | Local actionlint and Dependabot YAML validation passed; hosted jobs were not run |

The suite ran under Ubuntu 24.04 WSL, Python 3.12.3, Bash 5.2.21, tmux 3.4,
and GCC 13.3.0. It completed in 181.198 seconds on the Linux snapshot.
The previous twelve selected-interpreter pip/pytest live cases and both Yarn
major-version checks remain recorded in the earlier expansion evidence; the
current full suite retains their deterministic regressions.

Live source timeouts were 30 seconds. Successful checks do not establish the
browser's two-second default responsiveness. Curated checks combine actual leaf
help, inherited documentation or exact installed-version source, independent
argument contracts, and literal edits. Root help alone does not establish full
command compatibility or arity. Every curated option in the thirty-route
follow-up was reviewed against these sources.

## Issues identified and corrected

- Go run no longer offers the build-only `-o` option. Its fixed leaf help exposes
  `-exec` and references shared build flags; the live sentinel contract now follows
  that distinction. Supplemental `go help build` and `go help testflag` captures
  support inherited flags without executing a build or test.
- Podman build's `--pull` policy is optional. Bare and equals-attached forms
  permit subsequent options while build-context positionals retain their boundary.
- Both fzf multi-selection aliases carry optional count metadata. Explicit
  `optional_value_kind: "nonnegative_integer"` supports separate ASCII decimal
  counts, joined `-m2`, and `--multi=2`; arbitrary text, signed counts, and `--`
  are not consumed as optional values. Guided edits preserve or clear this field
  consistently when the argument contract changes.
- Ansible playbook help/version probes use fixed `C.UTF-8` values. Ansible-core
  2.21.5 rejected the previous `C` locale. Other tools retain their existing locale;
  pending environment variables remain excluded. Cache version 7 invalidates
  entries predating this probe change.
- Esptool's deprecated `.py` alias prints a warning before its version. Live
  reporting now selects the actual version line. Modern hyphenated and legacy
  underscored spellings remain distinct guarded routes.
- Google storage list's `--format` description now states its `gsutil` restriction.
  Go test verbosity and legacy .NET package-cache descriptions were also clarified.

Installed .NET SDK source confirmed hidden `--verbosity` and `--nologo` aliases,
legacy `--no-cache`, implicit restore flags, and optional `--self-contained`
Boolean arity. These valid options were retained despite abbreviated help output.

## Newly installed versions and route results

| Tool | Installed version | Previously skipped routes passed |
| --- | --- | --- |
| Podman | 4.9.3 | run, build, exec, logs |
| PostgreSQL client | 16.15 | psql shell invocation |
| Mike Farah yq | 4.54.1 | eval |
| fd / fdfind | 9.0.0 | both executable names |
| fzf | 0.44.1 | fzf |
| Ansible-core | 2.21.5 | ansible-playbook |
| Go | 1.27.3 | build, test, run, mod tidy |
| .NET SDK | 10.0.402 | build, test, run, publish, restore |
| Bun | 1.4.4 | run |
| Azure CLI | 2.91.0 | account show, vm list, storage blob list |
| Google Cloud SDK | 590.0.1 | config list, compute instances list, storage ls |
| Esptool | 5.6.0 and separate 4.12.0 | two modern aliases and legacy write_flash |
| Arduino CLI | 1.5.1 | compile |

## Isolation and installation provenance

Systems and runtime installations reside under ignored `.cache/live-followup/`.
Distribution packages were downloaded and extracted without installing system
packages or starting services. Podman/psql ELF RUNPATHs were adjusted to their
local extracted libraries. Official Go, .NET, Bun, Arduino, Google SDK, and yq
archives were checked against upstream checksums or release asset digests.
Python environments isolate Ansible, Azure, and both esptool major versions;
pip installation reports preserve package download hashes. A download hash
records integrity evidence, not a security audit of third-party software.

Azure/Google extraction on the Windows mount was slow. Their verified working
runtime is retained in an isolated native WSL `/tmp` directory, located through
`.cache/live-followup/cloud/runtime.json`; it is temporary and may be removed by
operating-system cleanup. Downloads remain in the repository cache for rebuilding.
Redundant slow installers were stopped after checking their process identities;
no background installer remained. No personal cloud/device configuration changed.

Every live run used a temporary HOME. Cloud configuration disabled telemetry,
update checks, prompts, and dynamic extension installation. Local Go/.NET/Bun/
Arduino launchers set fixed isolation controls and forward arguments unchanged
to verified binaries; they are test-environment launchers, not executable driver
configuration. Go toolchain downloads, .NET first-use certificate generation,
and tool telemetry were disabled. Only the registered help/version/manual routes
were supplied. No login, init, container daemon, database server, or device session
was required.

## Complete live version inventory

| Executable | Observed version |
| --- | --- |
| `ffmpeg` | ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers |
| `vlc` | VLC version 3.0.20 Vetinari (3.0.20-0-g6f0d0ab126b) |
| `gcc` | gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| `pip` | pip 24.0 from [isolated path] (python 3.12) |
| `git` | git version 2.43.0 |
| `curl` | curl 8.5.0 (x86_64-pc-linux-gnu) libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.3 brotli/1.1.0 zstd/1.5.5 libidn2/2.3.7 libpsl/0.21.2 (+libidn2/2.3.7) libssh/0.10.6/openssl/zlib nghttp2/1.59.0 librtmp/2.3 OpenLDAP/2.6.10 |
| `wget` | GNU Wget 1.21.4 built on linux-gnu. |
| `rsync` | rsync  version 3.2.7  protocol version 31 |
| `docker` | Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2 |
| `pip3` | pip 24.0 from [isolated path] (python 3.12) |
| `uv` | uv 0.13.1 (x86_64-unknown-linux-gnu) |
| `npm` | 9.2.0 |
| `pnpm` | 9.15.9 |
| `jq` | jq-1.7 |
| `rg` | ripgrep 14.1.0 |
| `ffprobe` | ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the FFmpeg developers |
| `gh` | gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3) |
| `kubectl` | Client Version: v1.37.1 |
| `helm` | v4.3.1+gc0d08d0 |
| `aws` | aws-cli/1.46.1 Python/3.12.3 Linux/5.15.153.1-microsoft-standard-WSL2 botocore/1.43.62 |
| `terraform` | Terraform v1.16.6 |
| `tofu` | OpenTofu v1.13.1 |
| `cargo` | cargo 1.75.0 |
| `cmake` | cmake version 3.28.3 |
| `ninja` | 1.11.1 |
| `clang` | Ubuntu clang version 18.1.3 (1ubuntu1) |
| `rclone` | rclone v1.60.1-DEV |
| `restic` | restic 0.16.4 compiled with go1.22.2 on linux/amd64 |
| `borg` | borg 1.2.8 |
| `7z` | 7-Zip 23.01 (x64) : Copyright (c) 1999-2023 Igor Pavlov : 2023-06-20 |
| `7zz` | 7-Zip (z) 23.01 (x64) : Copyright (c) 1999-2023 Igor Pavlov : 2023-06-20 |
| `magick` | Version: ImageMagick 7.1.2-34 Q16-HDRI x86_64 c5d4ca8a0:20261014 https://imagemagick.org |
| `convert` | Version: ImageMagick 6.9.12-98 Q16 x86_64 18038 https://legacy.imagemagick.org |
| `yt-dlp` | 2024.04.09 |
| `systemctl` | systemd 255 (255.4-1ubuntu8.18) |
| `journalctl` | systemd 255 (255.4-1ubuntu8.18) |
| `ssh` | OpenSSH_9.6p1 Ubuntu-3ubuntu13.20, OpenSSL 3.0.13 30 Jan 2024 |
| `scp` | Shared OpenSSH 9.6p1 installation/manual; no standalone version switch. |
| `sftp` | Shared OpenSSH 9.6p1 installation/manual; no standalone version switch. |
| `ip` | ip utility, iproute2-6.1.0, libbpf 1.3.0 |
| `ss` | ss utility, iproute2-6.1.0 |
| `openssl` | OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024) |
| `podman` | podman version 4.9.3 |
| `psql` | psql (PostgreSQL) 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1) |
| `yq` | yq (https://github.com/mikefarah/yq/) version v4.54.1 |
| `fd` | fdfind 9.0.0 |
| `fdfind` | fdfind 9.0.0 |
| `fzf` | 0.44.1 (debian) |
| `ansible-playbook` | ansible-playbook [core 2.21.5] |
| `pytest` | pytest 8.4.2 |
| `ruff` | ruff 0.14.1 |
| `go` | go version go1.27.3 linux/amd64 |
| `dotnet` | 10.0.402 |
| `yarn` | 4.9.4 |
| `bun` | 1.4.4 |
| `az` | azure-cli                         2.91.0 |
| `gcloud` | Google Cloud SDK 590.0.1 |
| `pio` | PlatformIO Core, version 6.1.18 |
| `platformio` | PlatformIO Core, version 6.1.18 |
| `esptool` | esptool v5.6.0 |
| `esptool.py` | esptool.py v4.12.0 |
| `arduino-cli` | arduino-cli  Version: 1.5.1 Commit: 01f3d4f2b Date: 2026-06-05T10:22:17Z |
| `esptool.py` | esptool v5.6.0 |

## Verification limits and retained evidence

No pending workloads ran: no target builds or target-project tests, restores,
remote SSH commands, deployments, cloud operations, database queries, playbooks,
firmware uploads, or serial sessions. Repository tests and its local package build
are separate verification activities. Software help and edit checks do not establish
real-world execution, connectivity, service operation, or physical device behavior.

psql covers shell invocation; SQL and backslash commands remain outside scope.
ip profiles cover listing/filter keywords, not arbitrary mutating subgrammars.
Unlisted flags, plugins, Microsoft.Testing.Platform-specific projects, unsupported
prefix forms, and different tool versions require separate validation. Manual-only
and discovery-off behavior retain their existing explicit variant limitations.
There are no remaining missing-dependency skips in the recorded matrix.

Maintained evidence:

- [Systems leaf captures](../tests/fixtures/help/followup-systems/manifest.json)
- [Runtime help, archive provenance, and installed-source excerpts](../tests/fixtures/help/runtime-followup-captured.json)
- [Cloud help and independent argument contracts](../tests/fixtures/help/followup-cloud-captured.json)
- [Complete fixture provenance guide](../tests/fixtures/help/README.md)

Ignored reports under `tests/reports/compatibility-followup/` contain
`final-full-suite.log`, `final-suite-evidence.json`, `live-complete.json`,
`previously-skipped.json`, `probe-audit.json`, and per-group installation/audit
details. The systems report retains the initial Ansible locale failure. Local
package/link evidence is recorded beside these reports after the final included
documentation edit; packages remain local under
`dist/compatibility-followup-verification/`.

Gitignore excludes downloaded dependencies, reports, and accidental checkout-local
tool homes while retaining profiles and fixtures. GitHub Actions retains only its
test/link logs for 14 days through a pinned artifact action; Dependabot groups
minor/patch CI and documentation-media updates. These are locally validated
configuration changes, not evidence of a hosted workflow run.
