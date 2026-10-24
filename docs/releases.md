# Release artifacts and build procedure

[Project overview](../README.md) · [Installation](installation.md) · [Documentation index](README.md)

## Version 0.1.2 - Alpha

The [VERSION](../VERSION) value `0.1.2-alpha` identifies the alpha prerelease tag
`v0.1.2-alpha`. Published assets are listed on
[GitHub Releases](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases).
The [versioned changelog](../CHANGELOG.md#version-012---alpha) and
[release notes](release-notes-v0.1.2-alpha.md) describe the included work.
Final distributable files are built from the exact release commit into a new
ignored directory, such as `dist/release-v0.1.2-alpha/`. Local candidates and
historical packages remain separate; building alone does not publish a release.
The [candidate validation guide](release-candidate.md) covers exact-source
checks, isolated lifecycle tests, rendered evidence, and remaining evidence limits.

Equal version strings do not establish equal source contents. Compare the
`BUILD-INFO.json` source hashes with the exact checkout, then verify artifact
checksums. Source hashes identify inputs; checksums do not authenticate a publisher.
The [GitHub updater](github-updates.md) uses version ordering and never treats
different contents at an equal version as an upgrade.

The prerelease targets Linux and Bash;
Python 3.10+ with `curses`, Bash 4.4+, and a UTF-8 terminal remain required.
The native launcher is compiled for Linux x86_64 on Ubuntu 24.04 and requires
glibc 2.34 or newer. Systems with an older glibc or a different C library can use
the source archive through its Bash/Python entry points. The launcher forwards
literal arguments to the adjacent Python or Bash runtime; it does not embed
Python and is not a Windows executable. Other Linux architectures can use the
source archive with a compatible Python/Bash installation.

| Artifact | Purpose |
| --- | --- |
| `cli-interactive-help-v0.1.2-alpha-source.tar.gz` | Maintained source, tests, fixtures, documentation, configuration, optional development tools, and shell installers |
| `cli-interactive-help-v0.1.2-alpha-linux-x86_64.tar.gz` | Complete source/runtime bundle plus compiled `cli-help` launcher |
| `cli-interactive-help-v0.1.2-alpha-linux-x86_64.run` | Self-extracting installer or updater, with embedded archive verification |
| `cli-help-v0.1.2-alpha-linux-x86_64` | Compiled launcher; requires the adjacent runtime from an extracted archive |
| `BUILD-INFO.json` | Version, compiler/platform details, and hashes of all packaged source inputs |
| `*.checksum` | SHA-256 checksums for each artifact, plus the aggregate `SHA256SUMS.checksum` |

## Version 0.1.1 - Alpha

The files under `releases/v0.1.1-alpha/` are preserved historical packages, also
associated with the [GitHub Releases page](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases).
Their artifact names use `v0.1.1-alpha` in place of `v0.1.2-alpha` above.
Those packages predate the current command-context and argument-syntax modules,
passive diagnostics, module-cache freshness guards, terminal-width fixes,
collection recovery, and GitHub updater. Their source archive is complete for
its historical inputs rather than the current checkout. The archives and their
checksums must remain unchanged. They are used as isolated upgrade fixtures.

## Verify and install

Download the eleven named release files into one directory, or use a verified
local build. Verify before installation:

```bash
sha256sum -c SHA256SUMS.checksum
```

For an individual downloaded artifact, use its matching `.checksum` file instead.
For the self-extracting installer:

```bash
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run --verify
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run install --prefix "$HOME/apps/cli-help" --no-rc
```

Installer arguments such as `--prefix "$HOME/apps/cli-help"` and `--no-rc` are
forwarded literally. Existing installations can be upgraded without removal:

```bash
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run update --prefix "$HOME/apps/cli-help"
```

The installer requires `tar`, `tail`, `mktemp`, and `sha256sum`, in addition to the
normal runtime dependencies. It verifies the embedded archive before extraction
and runs the existing installation/update scripts. Temporary source is removed
on ordinary completion. Update status `2` retains that source directory and
prints its location so the printed conflict-review command remains usable.
Remove retained temporary source after review. The permanent update and review
backups follow the [installation recovery rules](installation.md#update-recovery).

The launcher is installed from binary bundles and participates in the same
ownership and edit-preservation checks as other runtime files. Updating later
from a source-only checkout removes an unchanged optional launcher; Bash help
continues through the Python runtime. Custom launcher changes are preserved.

## Extracted runtime and native launcher

```bash
tar -xzf cli-interactive-help-v0.1.2-alpha-linux-x86_64.tar.gz
cd cli-interactive-help-v0.1.2-alpha
./cli-help --version
./cli-help --check
./cli-help install
./cli-help update --prefix "$HOME/apps/cli-help"
./cli-help review-update /absolute/path/to/update-backup/report.json
```

Browser and collection arguments are forwarded to `cli_help/main.py`.
`install`, `update`, `uninstall`, `review-update`, and `update-from-github` select the corresponding
shell wrappers. The launcher resolves its own executable location, so moving a
complete extracted bundle is supported. To use the separate launcher download,
copy it into the root of the extracted source bundle as `cli-help` and mark it
executable. Downloading that file alone is insufficient for browser operation.
`CLI_HELP_PYTHON` selects a Python executable; no shell command string is built.

## Build from source

GCC is required in addition to the runtime dependencies. From Linux x86_64:

```bash
bash tests/run.sh
python3 scripts/build_release.py --output dist/release-v0.1.2-alpha
cd dist/release-v0.1.2-alpha
sha256sum -c SHA256SUMS.checksum
```

The version comes from [VERSION](../VERSION). `CC` may name an alternative C
compiler executable; compiler command strings are not interpreted. The builder
refuses an existing output directory or output beneath a maintained source
directory. It excludes reserved private/generated names, credential/tool homes,
recovery state, reports, Python caches, previous releases, and build outputs.
Unexcluded maintained symlinks and special files are rejected. New source archives include the maintained
documentation, test fixtures, CI configuration, and `tools/` media generator
with its optional requirements. Those tools are absent from the preserved alpha
archives. Media dependencies are not copied into installed runtimes. Builds from
the current tree must use a separate output directory, leaving the preserved
release directory unchanged.

Capture opens each input through pinned directories with no symlink following,
refuses special files before reading, and rechecks file and directory identity.
Concurrent replacements or edits during a read abort the build. Input names with
backslashes or control characters are rejected to match updater extraction rules.

Selection uses the explicit root files and source directories in the builder,
without requiring Git. New maintained modules are included automatically.
Untracked files under those directories can also become inputs; inspect the
manifest before building and keep private notes outside them. Reserved-name
exclusion is not secret-content detection. Installed runtimes contain only the
installation payload, excluding documentation, tests, CI, and optional media tools.

Archives normalize ordering, modes, owner identifiers, and timestamps. Native
compilation enables warnings as errors and omits linker build identifiers.
Identical source and toolchain inputs produce identical archives and launcher
bytes; compiler or platform differences can change native output and build
metadata. `BUILD-INFO.json` maps artifacts to exact source contents without
claiming that an uncommitted build belongs to a particular Git commit.
The compiler consumes a temporary copy of the captured C input used by the
archives and manifest. Capture is not an atomic multi-file snapshot; edits between
different file captures still require
a final manifest-to-checkout comparison; rebuild after any included source or
documentation edit. Keep validation reports outside package inputs to avoid
self-referential hashes.

The release tests compile the launcher, verify checksums, extract the archives,
exercise installer/update/removal paths, reject corrupted embedded payloads, and
confirm literal argument forwarding. Building artifacts does not itself publish
a GitHub release. Publication requires a separate explicit decision after source,
package, and documentation verification; no automatic publication is configured.

## Release provenance and publication

The annotated release tag identifies the verified source commit. A clean checkout
of that commit supplies the packaged inputs; every manifest hash must agree with
the corresponding Git blob. Working-tree line-ending conversion can produce
different bytes despite a clean Git status, so a prior local candidate is reused
only after this comparison succeeds.

Release assets are prepared in a draft with the prerelease flag enabled and
latest-stable selection disabled. Publication follows source/package verification
and successful required hosted checks. Downloaded published assets are compared
byte for byte with the tested local files. The release body records the source
commit and current verification evidence without including private reports.
Checksums establish integrity rather than independent publisher authentication.
