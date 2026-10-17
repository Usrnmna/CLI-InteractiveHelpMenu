# Release artifacts and build procedure

[Project overview](../README.md) · [Installation](installation.md) · [Documentation index](README.md)

## Version 0.1.1 - Alpha

The source tree additionally provides a [GitHub release updater](github-updates.md)
for automatic package selection, verification, and guided conflict review. This
feature was added after the `v0.1.1-alpha` artifacts; those published files remain
unchanged. The guide describes adding the updater to an existing installation.

The release identifier is `v0.1.1-alpha`. This alpha targets Linux and Bash;
Python 3.10+ with `curses`, Bash 4.4+, and a UTF-8 terminal remain required.
The native launcher is compiled for Linux x86_64 on Ubuntu 24.04 and requires
glibc 2.34 or newer. Systems with an older glibc or a different C library can use
the source archive through its Bash/Python entry points. The launcher forwards
literal arguments to the adjacent Python or Bash runtime; it does not embed
Python and is not a Windows executable. Other Linux architectures can use the
source archive with a compatible Python/Bash installation.

Published files are available under `releases/v0.1.1-alpha/` in the repository and on its
[GitHub Releases page](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases).

| Artifact | Purpose |
| --- | --- |
| `cli-interactive-help-v0.1.1-alpha-source.tar.gz` | Complete maintained source, tests, documentation, and shell installers |
| `cli-interactive-help-v0.1.1-alpha-linux-x86_64.tar.gz` | Complete source/runtime bundle plus compiled `cli-help` launcher |
| `cli-interactive-help-v0.1.1-alpha-linux-x86_64.run` | Self-extracting installer or updater, with embedded archive verification |
| `cli-help-v0.1.1-alpha-linux-x86_64` | Compiled launcher; requires the adjacent runtime from an extracted archive |
| `BUILD-INFO.json` | Version, compiler/platform details, and hashes of all packaged source inputs |
| `*.checksum` | SHA-256 checksums for each artifact, plus the aggregate `SHA256SUMS.checksum` |

## Verify and install

Download all artifacts and checksum files into the same directory, then verify:

```bash
sha256sum -c SHA256SUMS.checksum
```

For an individual downloaded artifact, use its matching `.checksum` file instead.
For the self-extracting installer:

```bash
bash cli-interactive-help-v0.1.1-alpha-linux-x86_64.run --verify
bash cli-interactive-help-v0.1.1-alpha-linux-x86_64.run install
```

Installer arguments such as `--prefix "$HOME/apps/cli-help"` and `--no-rc` are
forwarded literally. Existing installations can be upgraded without removal:

```bash
bash cli-interactive-help-v0.1.1-alpha-linux-x86_64.run update
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
tar -xzf cli-interactive-help-v0.1.1-alpha-linux-x86_64.tar.gz
cd cli-interactive-help-v0.1.1-alpha
./cli-help --version
./cli-help --check
./cli-help install
./cli-help update --prefix "$HOME/apps/cli-help"
./cli-help review-update /absolute/path/to/update-backup/report.json
```

Browser and collection arguments are forwarded to `cli_help/main.py`.
`install`, `update`, `uninstall`, and `review-update` select the corresponding
shell wrappers. The launcher resolves its own executable location, so moving a
complete extracted bundle is supported. To use the separate launcher download,
copy it into the root of the extracted source bundle as `cli-help` and mark it
executable. Downloading that file alone is insufficient for browser operation.
`CLI_HELP_PYTHON` selects a Python executable; no shell command string is built.

## Build from source

GCC is required in addition to the runtime dependencies. From Linux x86_64:

```bash
bash tests/run.sh
python3 scripts/build_release.py --output dist/v0.1.1-alpha
cd dist/v0.1.1-alpha
sha256sum -c SHA256SUMS.checksum
```

The version comes from [VERSION](../VERSION). `CC` may name an alternative C
compiler executable; compiler command strings are not interpreted. The builder
refuses an existing output directory and excludes local reports, Python caches,
previous releases, and build outputs. Source archives include the maintained
documentation, test fixtures, and CI configuration.

Archives normalize ordering, modes, owner identifiers, and timestamps. Native
compilation enables warnings as errors and omits linker build identifiers.
Identical source and toolchain inputs produce identical archives and launcher
bytes; compiler or platform differences can change native output and build
metadata. `BUILD-INFO.json` maps artifacts to exact source contents without
claiming that an uncommitted build belongs to a particular Git commit.

The release tests compile the launcher, verify checksums, extract the archives,
exercise installer/update/removal paths, reject corrupted embedded payloads, and
confirm literal argument forwarding. Building artifacts does not itself publish
a GitHub release. The alpha prerelease is published only after its source commit
passes the Linux and documentation workflow.
