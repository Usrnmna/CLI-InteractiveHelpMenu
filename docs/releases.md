# Release artifacts and build procedure

[Project overview](../README.md) · [Installation](installation.md) · [Documentation index](README.md)

See [version numbering and planned releases](versioning.md) when choosing the next release number.

## Version 0.5.0 - Alpha

The selected candidate adds Ubuntu command coverage to the Bash menu, including package-manager routes, builtin help and edition-specific reference files. Those files install with the runtime. Optional tools are installed separately by the user. The corrected local builds correspond to the existing prerelease tag at `9274a1a`. Use the candidate audit for exact-package results, the eleven asset hashes and the manual publication handoff. [Candidate audit](release-candidate.md#v050-alpha-local-candidate) · [GitHub release body](release-notes-v0.5.0-alpha.md)

## Version 0.4.1 - Alpha

The local candidate skips unchanged idle frames and reduces the cost of validating profile text on menu open. The two changes form one patch in the 0.4 series. Performance measurements and regression results are available for both. The first build was verified locally on all three offline targets and reproduced byte for byte. The earlier local audit preceded the [GitHub prerelease](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases/tag/v0.4.1-alpha). [Changelog](../CHANGELOG.md#version-041---alpha) · [Local candidate status](release-candidate.md#v041-alpha-local-candidate)

## Version 0.4.0 - Alpha

The locally verified, unpublished candidate combines per-open reuse of shared value formatting with the three-level browser. Simple leaves more room for options. The default `D` key cycles through Detailed and Expanded without losing the selection or filter. Compact category labels retain access to full titles, and applicable options can be found by unit. [Changelog and timing evidence](../CHANGELOG.md#version-040---alpha) · [Six terminal captures](superpowers/plans/2026-11-24-menu-detail-levels.md#review-record)

The earlier unpublished performance candidate uses the same `0.4.0-alpha` version string and artifact filenames as the combined candidate. Its packages and verification results predate the three-level menu. The November 25 screenshots and animation came from a separate local build with the redesigned menu. The combined candidate comes from `cc30ade99d1ddf2f593b409f66bd05dc0029f44c`. Its [local verification record](release-candidate.md#combined-candidate-verification) identifies the combined packages by SHA-256. [Capture provenance](assets/README.md#november-25-historical-capture) · [Release decision](audit-history.md#menu-review-and-v040-alpha-selection)

## Local package formats

The [candidate validation guide](release-candidate.md) covers exact-source
checks, isolated lifecycle tests, rendered evidence, and remaining evidence limits.

Equal version strings do not establish equal source contents. Compare the
`BUILD-INFO.json` source hashes with the exact checkout, then verify artifact
checksums. Source hashes identify inputs; checksums do not authenticate a publisher.
The [GitHub updater](github-updates.md) uses version ordering and never treats
different contents at an equal version as an upgrade.

The prerelease targets Linux and Bash;
Python 3.10+ with `curses`, Bash 4.4+, and a UTF-8 terminal remain required.
The native launcher targets Linux x86_64. Its libc requirement depends on the build environment. The launcher forwards
literal arguments to the adjacent Python or Bash runtime; it does not embed
Python and is not a Windows executable. Other Linux architectures can use the
source archive with a compatible Python/Bash installation.

| Artifact | Purpose |
| --- | --- |
| `cli-interactive-help-v0.5.0-alpha-source.tar.gz` | Maintained source, tests, fixtures, documentation, configuration, optional development tools, and shell installers |
| `cli-interactive-help-v0.5.0-alpha-linux-x86_64.tar.gz` | Complete source/runtime bundle plus compiled `cli-help` launcher |
| `cli-interactive-help-v0.5.0-alpha-linux-x86_64.run` | Self-extracting installer or updater, with embedded archive verification |
| `cli-help-v0.5.0-alpha-linux-x86_64` | Compiled launcher; requires the adjacent runtime from an extracted archive |
| `BUILD-INFO.json` | Version, compiler/platform details, and hashes of all packaged source inputs |
| `*.checksum` | SHA-256 checksums for each artifact, plus the aggregate `SHA256SUMS.checksum` |

## Version 0.3.1 - Alpha

The [0.3.1 changelog entry](../CHANGELOG.md#version-031---alpha) records the local test-selector checkpoint.

## Version 0.3.0 - Alpha

The [0.3.0 changelog entry](../CHANGELOG.md#version-030---alpha) identifies its source commit and the command-help changes included in that checkout.

## Version 0.1.2 - Alpha

The earlier [published v0.1.2-alpha prerelease](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases/tag/v0.1.2-alpha) includes source and Linux x86_64 packages. Its launcher was built on Ubuntu 24.04 and requires glibc 2.34 or newer. Use the filenames and installation examples in the [v0.1.2-alpha release notes](release-notes-v0.1.2-alpha.md).

## Version 0.1.1 - Alpha

The files under `releases/v0.1.1-alpha/` are preserved historical packages, also
associated with the [GitHub Releases page](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/releases).
Their artifact names use `v0.1.1-alpha` in place of `v0.5.0-alpha` above.
Those packages predate the current command-context and argument-syntax modules,
passive diagnostics, module-cache freshness guards, terminal-width fixes,
collection recovery, and GitHub updater. Their source archive is complete for
its historical inputs rather than the current checkout. The archives and their
checksums must remain unchanged. They are used as isolated upgrade fixtures.

## Verify and install

Run these commands in the v0.5.0-alpha build output directory. For a published package, use the matching filenames and checksums from that release.

```bash
sha256sum -c SHA256SUMS.checksum
```

For an individual downloaded artifact, use its matching `.checksum` file instead.
For the self-extracting installer:

```bash
bash cli-interactive-help-v0.5.0-alpha-linux-x86_64.run --verify
bash cli-interactive-help-v0.5.0-alpha-linux-x86_64.run install --prefix "$HOME/apps/cli-help" --no-rc
```

Installer arguments such as `--prefix "$HOME/apps/cli-help"` and `--no-rc` are
forwarded literally. Existing installations can be upgraded without removal:

```bash
bash cli-interactive-help-v0.5.0-alpha-linux-x86_64.run update --prefix "$HOME/apps/cli-help"
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
tar -xzf cli-interactive-help-v0.5.0-alpha-linux-x86_64.tar.gz
cd cli-interactive-help-v0.5.0-alpha
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

GCC is required in addition to the runtime dependencies. For a local build on Linux x86_64:

```bash
python3 scripts/build_release.py --output dist/release-v0.5.0-alpha
cd dist/release-v0.5.0-alpha
sha256sum -c SHA256SUMS.checksum
```

For candidate verification, build from the frozen source and run the three offline suites with the exact artifacts. [Candidate validation](release-candidate.md#final-source-and-package-checks)

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

The [builder](../scripts/build_release.py) reads working-tree bytes from its explicit root files and source directories. It operates independently of the Git index and archive attributes. It includes `docs/`, `.github/` and the root README, roadmap, changelog and repository configuration. The roadmap and its linked audit summaries can be read together in an extracted archive. New maintained modules are included automatically.
Untracked files under those directories can also become inputs; inspect the
input list before building, check the resulting manifest, and keep private notes outside those directories. Reserved-name
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
