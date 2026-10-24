# Local release candidate validation

[Release formats and build procedure](releases.md) · [Development and tests](development.md) ·
[Installation and recovery](installation.md) · [Documentation index](README.md)

## Identity and evidence boundaries

`VERSION` contains `0.1.2-alpha`. Local candidates at
`dist/candidate-v0.1.2-alpha/`, `dist/candidate-v0.1.2-alpha-review/`, and
`dist/candidate-v0.1.2-alpha-config/` remain preserved as unpublished snapshots.
Their inputs can predate the release even when the versions agree. The
[release guide](releases.md#release-provenance-and-publication) describes the
tagged source and separately published prerelease assets. Historical packages in
`releases/v0.1.1-alpha/` remain separate. A version identifies ordering; the
manifest's source hashes identify the inputs. GitHub update checks only consider
published versions newer than the installed version, regardless of source hashes.

Local preparation does not establish hosted CI, remote distribution, another
architecture or libc, every supported Python/Bash version, or assistive-technology
compatibility. Record the compiler, architecture, libc, Python, Bash, tmux, locale,
and terminal alongside each validation. Preserve dated evidence from earlier runs
without treating it as evidence for the current candidate.

## Final source and package checks

Run the documented full suite after the last included edit:

```bash
bash tests/run.sh
python3 scripts/build_release.py --output dist/candidate-v0.1.2-alpha-recheck
(cd dist/candidate-v0.1.2-alpha-recheck && sha256sum -c SHA256SUMS.checksum)
```

The builder refuses an existing output directory. If further edits require
another candidate, select a new ignored directory, such as
`dist/candidate-v0.1.2-alpha-recheck-2/`; retain the earlier candidate for comparison.
The five artifacts, five individual checksum files, and aggregate checksum use
the existing release format. No artifact is uploaded automatically.

The package regression harness can inspect and exercise these exact artifacts
instead of building its own temporary candidate:

```bash
export CLI_HELP_TEST_RELEASE_DIR="$PWD/dist/candidate-v0.1.2-alpha-recheck"
export CLI_HELP_TEST_HISTORICAL_DIR="$PWD/releases/v0.1.1-alpha"
python3 -B -m unittest discover -s tests -p test_release_snapshot.py -v
python3 -B -m unittest discover -s tests -p test_release_terminal.py -v
unset CLI_HELP_TEST_RELEASE_DIR CLI_HELP_TEST_HISTORICAL_DIR
```

These two variables are test-harness inputs, not runtime configuration. The
harness checks source inventory/hashes, all artifact checksums, archive members,
contents and metadata, standalone/runtime launcher agreement, version identity,
and exact installer-wrapper/embedded-archive agreement before executing installers.
Rechecksummed stale, duplicate, or unrelated payloads are rejected. These checks
establish consistency with the reviewed local builder rather than publisher
authentication. Run the harness only against trusted local builds. Historical
upgrades explicitly skip when their preserved fixture is absent; a skipped upgrade
does not establish historical compatibility. Retain the historical directory when
testing from a source snapshot, or provide its absolute path through the test input.

| Evidence | Required contract |
| --- | --- |
| Source selection | Maintained inputs retained; reserved private/generated inputs excluded; changed files/directories, symlink swaps, special files, and updater-incompatible names refused during capture |
| Provenance | Each archived input agrees with `BUILD-INFO.json` and the final checkout; the launcher compiles the same captured C bytes; no output becomes a source input |
| Artifact integrity | Independent archive layout, permissions, source hashes, per-file and aggregate checksums, embedded payload verification, extraction, relocation, and literal native argument forwarding |
| Lifecycle | Actual historical installer upgraded by the candidate; source-only/native transitions; isolated installation, repeated updates, conflicts, backups, explicit review choices, cancellation, and removal |
| Privacy and collections | Packaged passive modes start no target and change no files; secret sentinels omitted; collection inspection and explicitly selected backup recovery preserve originals |
| Rendered terminal | Actual installed Bash adapter, curses cells, cursor coordinates, alternate-screen restoration, resize/reopen, numbered scrollback, quoting, Unicode, suffixes, cancellation, and nonexecution |
| Failure handling | Existing suite covers unsafe archive members, corrupt checksums/payloads, missing requirements, stale evidence, interruptions, concurrent changes, and failed-update preservation |

The rendered package checks use a private Linux tmux server with
`TERM=tmux-256color`, `C.UTF-8`, and isolated Bash configuration. Synthetic target
stubs detect accidental execution. Compose's discovery-backed leaf uses an explicit
small test profile with discovery disabled; this does not imply a bundled static
Compose profile. The 7-Zip case uses installed bundled metadata. Other maintained
terminal tests cover editing modes, fragmented keys, and collection/review screens.
Rendered cells and keyboard behavior do not establish screen-reader support.

## Isolated manual package inspection

Installers normally support startup registration. Validation must use `--no-rc`
and isolated locations rather than personal shell files. For example, from the
repository root:

```bash
candidate="$PWD/dist/candidate-v0.1.2-alpha-recheck"
scratch=$(mktemp -d)
mkdir -p "$scratch/home" "$scratch/config" "$scratch/cache" "$scratch/data" "$scratch/tmp"
env -i PATH="$PATH" HOME="$scratch/home" XDG_CONFIG_HOME="$scratch/config" \
  XDG_CACHE_HOME="$scratch/cache" XDG_DATA_HOME="$scratch/data" TMPDIR="$scratch/tmp" \
  CLI_HELP_PYTHON="$(command -v python3)" PYTHONDONTWRITEBYTECODE=1 \
  bash "$candidate/cli-interactive-help-v0.1.2-alpha-linux-x86_64.run" \
  install --prefix "$scratch/runtime" --no-rc
env -i PATH="$PATH" HOME="$scratch/home" XDG_CONFIG_HOME="$scratch/config" \
  XDG_CACHE_HOME="$scratch/cache" XDG_DATA_HOME="$scratch/data" \
  CLI_HELP_PYTHON="$(command -v python3)" CLI_HELP_DISCOVERY=off \
  "$scratch/runtime/cli-help" --doctor
```

The native launcher requires its adjacent runtime and an available Python with
`curses`; the standalone executable is insufficient. Runtime installation excludes
tests, documentation, and optional media dependencies. Installation and local
updates preserve existing activation and discovery defaults. Selecting an option
edits pending input; separate help/version/manual invocations remain bounded.

Keep failed-update backups and retained installer source until conflict review is
complete. Update status `2` prints a usable review command and retained source
location. Follow [conflict review](update-review.md) and
[installation recovery](installation.md#update-recovery), including stale-input
checks and explicit choices. Do not remove or replace backups automatically.

## Reproducibility and reporting

Build twice from the same stable input bytes with the same compiler and platform,
using different new output directories. Compare every artifact, checksum, and
manifest byte. A different toolchain or build-platform string can legitimately
change output; normalized tar metadata alone does not establish cross-platform
reproducibility. Recheck the manifest against the final included files after tests.

Keep local verification records under `.cache/` or `tests/reports/`, outside
packaged inputs. Such records can contain local paths and synthetic terminal
buffers and require review before sharing. Include candidate location, manifest
identity, checksum results, exact commands, pass/fail/skip counts, rendered
observations, historical-artifact preservation, and remaining limitations.
Separate product failures from missing environments and pending decisions.
Changing a package-included verification document requires another build; avoid
embedding a final artifact's hash into its own hashed source inputs.

CI repeats the existing source suite and builds a fresh temporary candidate,
then tests its actual lifecycle and rendered adapter. Only the named synthetic
diagnostic reports, test/package logs, checksum summary, and build manifest are
retained. Package binaries, raw captures, tool homes, and recovery backups are
excluded. Local smoke execution is distinct from a hosted workflow run.
