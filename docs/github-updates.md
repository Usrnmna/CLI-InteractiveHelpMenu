# Updating an installation from GitHub releases

[Project overview](../README.md) · [Installation and recovery](installation.md) ·
[Guided conflict review](update-review.md) · [Documentation index](README.md)

The release updater checks published releases in
[`Usrnmna/CLI-InteractiveHelpMenu`](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases),
downloads a compatible archive and its checksum, and upgrades the existing
installation. Custom settings, edited files, and custom collections follow the
same preservation and backup rules as a local-source update. Bash startup files
are not rewritten, sourced, or evaluated during an upgrade.

## Check and upgrade

From a checkout containing the updater:

```bash
# Inspect the stable channel without downloading a package or changing files.
bash update-from-github.sh --check

# Download, verify, and apply the newest stable release.
bash update-from-github.sh

# Include alpha/beta releases.
bash update-from-github.sh --prerelease --check
bash update-from-github.sh --prerelease
```

The updater is included in new installations. It can also run directly from an
installed runtime:

```bash
bash "${XDG_DATA_HOME:-$HOME/.local/share}/cli-interactive-help/update-from-github.sh" --prerelease
```

An installation made from the original `v0.1.1-alpha` package does not contain
this updater. Run `bash update.sh --prefix /path/to/installation` from a checkout
containing the updater once to add it, or run that checkout's
`update-from-github.sh --prefix /path/to/installation`. Published alpha archives
remain unchanged. If no newer eligible release is published, the check reports
no update. A release check does not obtain unreleased checkout changes, even
when their `VERSION` matches the installed alpha.

The `v0.1.2-alpha` version line is a prerelease. Use `--prerelease --check` to
inspect eligible published alpha packages; availability is determined by the
[GitHub Releases listing](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases).
An older same-version local candidate requires a
[verified local-source update](installation.md#updating-an-existing-installation)
to obtain different source contents.
A different source hash with the same version never makes a package eligible
for a GitHub upgrade; equal versions remain excluded. Local validation does not
establish remote asset availability or successful distribution.

Inside a custom installation, the installed wrapper targets its own directory.
From a source checkout, the default is
`${XDG_DATA_HOME:-$HOME/.local/share}/cli-interactive-help`. An explicit `--prefix`
overrides either default. Missing or unmanaged installations are rejected;
initial setup uses [the installer](installation.md).

The updated native launcher also supports `./cli-help update-from-github`.
The original `v0.1.1-alpha` native binary predates this command.

| Option | Behavior |
| --- | --- |
| `--check` | Read release metadata and report the selected package; do not download, install, or open review |
| `--prerelease` | Include semantic prereleases and releases marked as prereleases by GitHub |
| `--version TAG` | Select an exact release tag; prereleases still require `--prerelease` |
| `--source` | Select the source archive even when a compatible native package exists |
| `--prefix PATH` | Select an existing managed installation |
| `--no-review` | Preserve conflicts and print a resume command without opening the reviewer |

Equal and older versions are never reinstalled or downgraded. The installed
`VERSION` must match its ownership checksum; an edited or missing version marker
requires inspection or a local-source update. Semantic version ordering is used
instead of publication order; numeric prerelease identifiers compare numerically.
Build metadata does not change precedence. Drafts and unsupported tag formats
are excluded. Listing is bounded to 1,000 releases; an exact tag is required if
that limit is reached.

## Package selection and verification

Linux, Bash 4.4+, and Python 3.10+ with `curses` remain required. The updater uses
the Python standard library and does not require `curl`, `wget`, Git, or a GitHub
token. It makes unauthenticated requests for the fixed public repository.

On Linux x86_64 with glibc 2.34 or newer, the updater prefers the matching native
runtime archive when available. Other architectures, older glibc versions, and
other C libraries use the source archive. `--source` also forces this route.
The native launcher still requires the adjacent Bash/Python runtime. Source-only
updates remove an unchanged optional native launcher and preserve an edited one,
as described in [release package ownership](releases.md#verify-and-install).

The archive must have a matching `.checksum` asset or an entry in
`SHA256SUMS.checksum`. Asset names and download URLs must match the selected tag
and repository. Downloads must match the API size, the checksum-file SHA-256,
and the API SHA-256 digest when GitHub supplies one. Verification completes
before extraction or execution of any downloaded updater code. The updater does
not execute downloaded `.run` installers or release-description text.

HTTPS certificate verification remains enabled. Redirects are restricted to
GitHub and its release asset hosts; HTTP downgrades and arbitrary hosts are
rejected. Each request has a 15-second network timeout and a 120-second transfer
budget. Limits include 4 MiB per metadata response, 64 MiB per archive, 64 KiB
per checksum file, 128 MiB of expanded tar data, 32 MiB per member, and 10,000
members. Oversized or malformed inputs fail before installation changes.
Archives cannot contain path traversal, links, devices, FIFOs, sparse files, or
duplicate paths. Extracted permissions exclude special permission bits.

Checksums establish agreement with the release assets served by GitHub; they are
not independent publisher signatures. Applying an update trusts this repository's
release publishers and executes the verified package's installation code. Network,
TLS, rate-limit, and metadata failures stop the update rather than bypassing
verification. The implementation follows GitHub's documented
[release listing API](https://docs.github.com/en/rest/releases/releases#list-releases)
and [release asset metadata](https://docs.github.com/en/rest/releases/assets#get-a-release-asset).

## Conflicts, backups, and recovery

```text
Managed installation version -> GitHub release metadata -> compatible package
                                                           |
                                                download + verify SHA-256
                                                           |
                                               validate archive and version
                                                           |
                                        managed update + full previous backup
                                                           |
                             no conflicts <----------------+----> preserved conflicts
                                  |                                      |
                         remove download staging             retain verified review source
                                                                         |
                                                      terminal: open guided-capable reviewer
                                                      no terminal: print resume command
```

The existing installer lock serializes installation mutations. The incoming
updater checks the expected installed version while holding that lock, preventing
a concurrent upgrade from being replaced by an earlier download. Local edits
made during the download are included in staging; concurrent edits during staging
trigger the existing stale-input checks.

When conflicts remain, an interactive terminal opens the update reviewer. Select
an entry and press **g** to accept or reject individual change blocks. Preview and
queue the result, then save from the review menu. Saving creates a separate review
backup. Keeping a local file is a completed review decision and remains protected
from later update/removal. See [the guided editing controls](update-review.md#guided-editing-without-an-external-editor)
for navigation and validation behavior.

Without a terminal, or with `--no-review`, the update preserves local conflicts
and prints a shell-quoted resume command. The verified downloaded source remains
in a private sibling directory named `<prefix>.release-update-*`. It also remains
after a failed or interrupted application attempt, because recovery paths may
already exist. Inspect the printed installation and review backups before retrying.
Failures during download or archive validation remove download staging and do not
modify the installation.

The download directory remains after an interactive conflict review, including
when every decision has been saved, so the printed command can reopen the report.
It can be removed after review and recovery are no longer needed. Installation
backups (`<prefix>.update-backup-*`) and review backups
(`<prefix>.update-review-backup-*`) remain separate; their recovery procedures are
documented in [update recovery](installation.md#update-recovery) and
[review recovery](update-review.md#stale-inputs-and-recovery).

A partial update can advance `VERSION` while customized files remain unresolved.
Resume the printed report rather than expecting a repeated release check to reopen
it. Downloaded source, backups, and report files are not automatically pruned.
No recurring background checks are installed.

| Exit status | Meaning |
| --- | --- |
| `0` | Check completed, no newer eligible release, successful update, or all conflicts explicitly reviewed |
| `1` | Network, verification, validation, or application error; inspect printed recovery paths if application began |
| `2` | Update completed with unresolved/deferred conflicts, or command-line usage error |
| `130` | Interrupted update or cancelled interactive review; saved decisions and backups remain |

## Maintainer interface and validation

The release updater invokes the verified package's `scripts/installation.py`
directly, using literal arguments. Compatible future packages must support
`update --expected-version VERSION --result-file PATH`. The version comparison
runs inside the installation lock. The optional completion record is a new JSON
file outside the installation with `schema_version: 1`, `status: 0|2`, and
`report: null|PATH`. It is written after a completed update or no-op. Failure to
write it can occur after an installation switch, so the release updater retains
source for recovery and reports an error. Existing paths are never overwritten.

```bash
python3 -m unittest discover -s tests -p 'test_release_update.py' -v
bash tests/run.sh
```

Offline tests cover SemVer ordering, channels, pagination, malformed metadata,
package/architecture selection, timeouts, rate limits, redirect restrictions,
truncation, checksum and digest failures, unsafe archives, decompression bounds,
backup and setting preservation, concurrent-version checks, lock failures,
interruption, completion records, custom prefixes, and guided review in a real
Bash terminal. The terminal workflow also verifies option insertion without
execution of the pending command. Network fixtures do not establish availability
of future GitHub releases or compatibility with every Linux distribution.

The release-updater baseline on 2026-10-17 passed all 355 tests on Ubuntu 24.04 under WSL with Python
3.12.3, including 48 release-updater tests and 31 real Bash terminal tests across
the suite. Live GitHub discovery selected `v0.1.1-alpha`; its 569,002-byte native
runtime archive downloaded, matched the published checksum and API digest, and
extracted with the expected version. No downloaded code ran and no installation
changed during that live network check. Upgrade application and guided review
were exercised with isolated installations and offline release fixtures.
Subsequent third-party command coverage and live-program results are documented
in the [compatibility guide](compatibility.md).
