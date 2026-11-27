# Local release candidate validation

[Release formats and build procedure](releases.md) · [Development and tests](development.md) ·
[Installation and recovery](installation.md) · [Documentation index](README.md)

## v0.5.0-alpha local candidate

**Local publication status: blocked pending a corrected source commit.** The two builds of `d13b3e67bae4b8ac00027a4ec7979175bb6a9528` reproduced exactly. All three offline suites then stopped at the numerical preflight. Leave this revision and both output directories out of publication. [Remaining steps](../ROADMAP.md#remaining-work) · [Accepted Ubuntu source verification](audit-history.md#phase-3-combined-verification)

The checkout was clean on `main`. The accepted provider, Bash adapter, renderer, profile, configuration and test files matched their Phase 3 versions. The checkout gallery matched all 224 recorded source hashes and eight asset hashes. Offline Lychee reported zero errors, 31 focused repository-policy and documentation-link tests passed, and the whitespace, attribute and ignore checks passed. The impacted selector proposed full discovery. Actionlint 1.7.12 passed with a local label entry for `ubuntu-26.04`; the stock catalog flagged that label, which GitHub had already assigned to a hosted runner. [Earlier hosted runner](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/45799373693/job/139838263441)

Two independent source copies supplied 1,130 tracked files from Git blobs with their recorded modes. The builder included 1,118 files. On Ubuntu 26.04.1 x86_64, GCC 15.2.0 and Python 3.14.4 produced eleven byte-identical files under `dist/candidate-v0.5.0-alpha/` and `dist/candidate-v0.5.0-alpha-2/`. Both builds passed their checksums, installer self-verification and launcher version check. The package verifier matched the archives, their metadata, the launcher and the embedded payload. The launcher's highest required glibc symbol was 2.34.

| Target | Ubuntu / Python | Fixture manifest SHA-256 | Full-suite result |
| --- | --- | --- | --- |
| host | 26.04.1 / 3.14.4 | `f08addd63144ff211587db461169f9f26302e5a969aea6865ec70ff879e19984` | Numerical preflight exit 1 before discovery |
| noble310 | 24.04.5 / 3.10.20 | `585b29b53ef075b24e12ddad0d32b612f0182e32824f4f300be2800b1babee8c` | Numerical preflight exit 1 before discovery |
| noble312 | 24.04.5 / 3.12.3 | `585b29b53ef075b24e12ddad0d32b612f0182e32824f4f300be2800b1babee8c` | Numerical preflight exit 1 before discovery |

Each target verified the frozen file manifest, first build and historical v0.1.1-alpha package. No unittest case started, so discovery totals, test outcomes, skips and the upgrade result are unavailable. The focused reproduction gave one `review_stale` error for `source||.github/workflows/ci.yml`. The workflow change adds two comments above the existing package step. Updating its single reviewed fingerprint cleared inventory reconciliation and both prospective and strict gates in the working tree. All 4,426 required contracts were complete, with 93 warnings, 11 informational diagnostics and zero errors or debt.

Separate installed-prefix checks on the first build passed on all three targets. All 57 reference shards matched the manifest. With the manual tool unavailable, `/usr/bin/hostname` offered `--alias` from the applicable packaged reference. Bare `echo` used Bash help. External `/usr/bin/echo` used the Resolute reference on the host and gave revision-specific guidance for Noble coreutils 9.4-3ubuntu6.3. The installed APT route exposed `--simulate` for `apt install`. In a 100×24 private Bash terminal, cancelling preserved the pending line and cursor. Selecting `install` completed `apt ins` while preserving the quoted operand. The disposable prefixes were removed. Repeat these checks on the corrected first build.

The ignored evidence directory `tests/reports/v050-d13b3e6/` contains the Git manifest, first-attempt asset sizes and hashes, per-target logs, focused reproduction and corrected gate reports. The final upload directory and tag target can be selected after a new commit containing the correction passes the combined gate. A later documentation-only commit may describe that verified source separately.

## v0.4.1-alpha local candidate

**Verified locally, unpublished — November 25, 2026.** Phase 4 publication is skipped. The first build passed the full offline suite and installed-menu checks on all three targets. [Release verification summary](audit-history.md#local-release-verification)

The November 25, 2026 preparation selects both retained improvements. The runtime inputs match the [measured implementation](menu-cost-measurements.md#combined-offline-verification). SHA-256 for `cli_help/ui.py` is `9852b14abd235b29adfa54f03ab61a545f9e3955a1a6fa640c26ccdee19cc4a5` and for `cli_help/core.py` is `a78b5b7c6e4fe3d2b97ac2105d211685be74339102ed91f962fccb6ba6f3ef93`.

On Ubuntu 26.04.1 with Python 3.14.4, all 44 focused host sandbox tests passed in 39.565 seconds. Coverage included idle timeouts, terminal resize and recovery, menu interaction, profile validation, override precedence and prerelease selection. The checkout version and changelog heading agreed, and the offline Markdown link check passed. The builder selected the same 1,003 paths as the frozen v0.4.0-alpha manifest. The preparation logs and file hashes are under `tests/reports/v0.4.1-alpha-preparation/`.

**Source and reproducibility.** The frozen source is `cced50757a53612860d34bbcd77b0f2e0d99d0f0`. Two separate source directories were populated directly from that commit using `git ls-tree -rz` and `git cat-file --batch`, preserving file modes. Each copy supplied exactly the 1,003 packaged paths and hashes approved at preparation. The other 12 tracked files comprise the Codex environment file and the historical release fixture.

Both builds ran on Ubuntu 26.04.1 x86_64, kernel 7.0.0-43-generic, glibc 2.43, GCC 15.2.0 (Ubuntu 15.2.0-16ubuntu1) and Python 3.14.4. From each source directory, the build command was `LC_ALL=C.UTF-8 CC=/usr/bin/gcc /usr/bin/python3 -B scripts/build_release.py --output "$output"`, using a fresh absolute output path. The first set is in `dist/candidate-v0.4.1-alpha/` and the rebuild in `dist/candidate-v0.4.1-alpha-2/`. All 11 files matched byte for byte. Archive members, contents, modes, ownership and timestamps passed the package verifier. The standalone and bundled launchers matched, the launcher reported `0.4.1-alpha`, and the installer wrapper and payload matched the Linux archive. Both sets passed every checksum and installer `--verify` check.

| First build file | SHA-256 |
| --- | --- |
| `BUILD-INFO.json` | `06365fcb1effd23b2842b097c60f82ffec0793c980f30cb95dd8ed3cd6b068da` |
| `SHA256SUMS.checksum` | `f097624b0f23e3f5a9ffbf9edd393bee65c5f66e4d1ed7804ce0963702041bf1` |
| `cli-help-v0.4.1-alpha-linux-x86_64` | `661970b86f834e129b99759a1bcfa34291ff9620f0808075d4c4a8fdd6a41929` |
| `cli-interactive-help-v0.4.1-alpha-linux-x86_64.run` | `3c4c6c08bc7730882ebfe8191d07b947b6ecd5da4ebc4e78d0a87885cd6ce787` |
| `cli-interactive-help-v0.4.1-alpha-linux-x86_64.tar.gz` | `483fa44880bcf0c117c92fced75863379dc3830514e3c682f8a1cabdac6e70f3` |
| `cli-interactive-help-v0.4.1-alpha-source.tar.gz` | `79f4db4e733b7c9da53b43cb8db4b865ebbce3e2c1492c77dec1302446bdce78` |

**Offline inputs.** Each target checked the same 1,015 tracked files against a manifest with SHA-256 `17c52d27da341f94385b1dc8e382cc15741f5e51dc95cbad1656abb45655f940`. The sandbox received the first build's 11 files and the release-specific client fixtures through `--include`. It checked the artifacts and the preserved v0.1.1-alpha fixture before running `bash tests/run.sh` with `CLI_HELP_TEST_RELEASE_DIR=/tmp/src/dist/candidate-v0.4.1-alpha` and `CLI_HELP_TEST_HISTORICAL_DIR=/tmp/src/releases/v0.1.1-alpha`. The host used Bubblewrap. The Noble targets ran in rootless Podman through the user service manager. [Sandbox procedure](development.md#isolated-local-debugging)

**Matrix results.** Each target completed one full run and exited zero. All 1,891 test IDs matched discovery at the frozen revision. The sole skip was `test_probe_reports_the_windows_limitation` because the POSIX probe completed normally. All 15 exact-candidate package and installed-screen tests passed per target, including historical upgrade, repeated update and removal.

| Target | Ubuntu | Python | Bash / tmux / glibc | Pass | Fail or error | Skip | Unittest (s) | End to end (s) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| host | 26.04.1 | 3.14.4 | 5.3.9 / 3.6 / 2.43 | 1,890 | 0 | 1 | 2,444.338 | 2,476.13 |
| noble310 | 24.04.5 | 3.10.20 | 5.2.21 / 3.4 / 2.39 | 1,890 | 0 | 1 | 2,720.290 | 2,759.92 |
| noble312 | 24.04.5 | 3.12.3 | 5.2.21 / 3.4 / 2.39 | 1,890 | 0 | 1 | 2,456.249 | 2,490.70 |

**Installed Bash menu.** The additional terminal checks ran after unittest discovery and are included in the end-to-end times. On each target the first build installed into a disposable prefix with `--no-rc` and reported `CLI Interactive Help Menu 0.4.1-alpha`. At 80×24 and 60×16 the idle screen stayed stable, responded to a shrink below minimum and restored the original menu when expanded. All six reference frames matched. The second filtered option stayed selected across all three detail levels. Escape restored the original line, cursor and terminal state. Selecting `-b:v` preserved the quoted suffix, insertion point and numbered scrollback. The pending command's execution marker stayed absent and uninstall removed the prefix.

The dated verification record and status updates were written after both builds. Reproduce the packages from the frozen SHA. The ignored evidence directory `tests/reports/v041-cced507/` holds the build script and log, full source and artifact manifests, exact per-target runner arguments, terminal check, elapsed times and reconciled logs.

## Identity and evidence boundaries

The [frozen v0.4.0-alpha candidate](releases.md#version-040---alpha) includes both shared value formatting and the three-level menu. The existing performance-only packages under `dist/candidate-v0.4.0-alpha-recheck/` and its `-2` rebuild predate the redesign. The [combined candidate record](#combined-candidate-verification) identifies its separate source and assets.

The earlier v0.1.2-alpha release review preserved local candidates at
`dist/candidate-v0.1.2-alpha/`, `dist/candidate-v0.1.2-alpha-review/`, and
`dist/candidate-v0.1.2-alpha-config/` as unpublished snapshots. A fresh checkout does not contain these ignored directories.
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

## Combined candidate verification

The **verified upload set** is `dist/candidate-v0.4.0-alpha-combined/`. The independent rebuild is `dist/candidate-v0.4.0-alpha-combined-2/`. This record and the roadmap update were written after the builds in the working tree. Reproduce the assets from the frozen SHA.

On November 25, 2026, the release inputs were frozen at `cc30ade99d1ddf2f593b409f66bd05dc0029f44c`. The working tree was clean at that commit. It records the [Menu review and release decision](audit-history.md#menu-review-and-v040-alpha-selection) and keeps `VERSION` at `0.4.0-alpha`. The browser creates one shared-value formatting cache per open and cycles through Simple, Detailed and Expanded. The presentation and UI modules match the [pre-experiment hashes](serial-prose-reuse-experiment.md#reproduction). The idle loop still redraws after a timeout, and the loader still checks profile text character by character. The prose-reuse patch is a benchmark input under `tools/`.

**Build and provenance.** Two independent local clones checked out the full SHA with detached HEAD and clean status. The build host ran Ubuntu 26.04.1 LTS on x86_64, kernel 7.0.0-43-generic, glibc 2.43, GCC 15.2.0 (Ubuntu 15.2.0-16ubuntu1), Python 3.14.4, Bash 5.3.9 and tmux 3.6 with locale `C.UTF-8`. The highest glibc symbol version required by this launcher is `GLIBC_2.34` (`readelf --version-info`).

From the project root, the two builds used the following inputs and output paths. Both directories are retained locally.

```bash
root=$PWD
sha=cc30ade99d1ddf2f593b409f66bd05dc0029f44c
for copy in first second; do
    checkout="$root/.cache/phase3-cc30ade/$copy"
    git clone --no-local --no-checkout "$root" "$checkout"
    git -C "$checkout" checkout --detach "$sha"
    test "$(git -C "$checkout" rev-parse HEAD)" = "$sha" || exit 1
    test -z "$(git -C "$checkout" status --porcelain)" || exit 1
    output="$root/dist/candidate-v0.4.0-alpha-combined"
    if [ "$copy" = second ]; then output="$output-2"; fi
    (cd "$checkout" && CC=/usr/bin/gcc /usr/bin/python3 -B scripts/build_release.py --output "$output") || exit 1
done
```

The first build contains 1,003 source files. Comparison against `git ls-tree -rz` and `git cat-file --batch` matched every manifest path and SHA-256 to the frozen tree. The only tracked paths outside that inventory were the Codex environment file and the 11 historical release files. The [package verifier](../tests/test_release_snapshot.py) checked all 1,003 source archive members and all 1,004 Linux archive members, including bytes, modes, owner/group and timestamps. The standalone and bundled launchers matched. The installer wrapper and embedded Linux archive matched the builder output before either installer was exercised. Both installers then passed `--verify`.

**Artifact digests.** Each individual checksum and both aggregate lists passed `sha256sum -c`. All 11 filenames and file contents matched across builds with `cmp`. The table gives SHA-256 for each asset and for its individual checksum file.

| Asset | SHA-256 | SHA-256 of matching `.checksum` file |
| --- | --- | --- |
| `cli-interactive-help-v0.4.0-alpha-linux-x86_64.run` | `5f5b1232735dfda2adbae365aea84dcddb2979f7e41364d9e9f2f531a0f72710` | `b480dea7acdbdb1f8b0102bcee51c5e8b31379bd9af8a370df0855e9e7856743` |
| `cli-interactive-help-v0.4.0-alpha-linux-x86_64.tar.gz` | `1e61793f1bad662e4ad5be0c01c4b873a8642c2f64161f3dc721af152cc0042b` | `1da2e3c5f6ec447b077ae9b697ae07eaeb6ec52cf0e52cdf0fcc9ecdf950807c` |
| `cli-help-v0.4.0-alpha-linux-x86_64` | `69865cb32ade928d323106848812c8ced4d7602ac7fa39141d1d8f20016f1817` | `95dee93c9cef8174a962942956a30cefafea367af7a883f49a30aa479faa982c` |
| `cli-interactive-help-v0.4.0-alpha-source.tar.gz` | `d5b0018eb24c6148893e3f02b77fe26e899bfeda53be6c07fa155f26319b68c8` | `40aecb2177d0d185106255090d1d54500b9483eab4945c269f38992bf52ce4a7` |
| `BUILD-INFO.json` | `b21ed7bf5954dedb5fbddbb4a1af9b84810888d6149c7f92bffe23ae20799703` | `f7fef6094326fef685c5387f5d1cb3eef766ad6845ee0c77c765f5406ac9eae9` |
| `SHA256SUMS.checksum` | `485206837655375afdc420a69780231e335907086180632b494adc131a47c4dc` | — |

**Offline test inputs.** Each target received the first build's 11 files through the sandbox runner's `--include` option. The tracked historical fixture came from the detached checkout. Inside the sandbox, the wrapper verified both aggregate identities and all listed hashes and passed the following environment to the full suite.

```bash
export CLI_HELP_TEST_RELEASE_DIR=/tmp/src/dist/candidate-v0.4.0-alpha-combined
export CLI_HELP_TEST_HISTORICAL_DIR=/tmp/src/releases/v0.1.1-alpha
bash tests/run.sh
```

The package and terminal test classes resolve the supplied release path, verify its contents and use its installer. The upgrade test reads the historical installer from the supplied fixture path and checks its digest. The historical installer SHA-256 was `e56049a17804041787915c8b063b180d7fc39a4be7fecb4a8e8b7183c6d8f1ae` and its aggregate checksum file had SHA-256 `e5b64360c518fce838f120db42a95602eca818e4f7d768490dcc01e6269e8fe0`. [Package checks](../tests/test_release_snapshot.py) · [Installed adapter checks](../tests/test_release_terminal.py)

The local evidence directory is `tests/reports/phase3-cc30ade/`. From the project root, `python3 -B tests/reports/phase3-cc30ade/check-artifacts.py` repeats the Git, archive, checksum and rebuild comparisons. In the evidence directory, `run-full.sh TARGET` records the exact per-target sandbox command and pinned fixture selection for ffmpeg, fd, fzf, OpenSSH, rsync and yq. `phase3-suite.sh` verifies the inputs in the sandbox. `run-terminal.sh TARGET` runs the additional installed-menu checks. The targets are `host` (Bubblewrap), `noble310` and `noble312` (rootless Podman). Both Noble commands ran through the local user service manager so Podman could create its UID mapping. All three sandboxes used private writable scratch space with networking disabled. [Sandbox procedure](development.md#isolated-local-debugging)

**Full offline results.** Each unsharded run completed all four preflight checks and full unittest discovery. Each transcript matched all 1,889 discovered test IDs at the frozen SHA. All three commands exited 0.

| Ubuntu | Python | Bash / tmux / glibc | Passed | Failed or errored | Skipped | Unittest seconds |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 26.04.1 | 3.14.4 | 5.3.9 / 3.6 / 2.43 | 1,888 | 0 | 1 | 2,513.497 |
| 24.04.5 | 3.10.20 | 5.2.21 / 3.4 / 2.39 | 1,888 | 0 | 1 | 2,818.753 |
| 24.04.5 | 3.12.3 | 5.2.21 / 3.4 / 2.39 | 1,888 | 0 | 1 | 2,520.852 |

On each target, only `test_probe_reports_the_windows_limitation` skipped because POSIX hosts complete the probe normally. All 15 exact-candidate package and installed-screen tests passed, including isolated install, upgrade from the preserved 0.1.1-alpha installer, backup verification, repeated update, source-only transition and removal. The final logs are `{host,noble310,noble312}-full.log` and `{host,noble310,noble312}-terminal.log` in the evidence directory. Earlier runs without the full executable fixture set were stopped and excluded from these counts. Run `python3 -B tests/reports/phase3-cc30ade/check-results.py` from the project root to reconcile the logs with discovery.

**Installed terminal.** On each Linux target, the first build's installer populated a temporary prefix with `--no-rc`. A private tmux server sourced its installed Bash adapter under `TERM=tmux-256color` and `C.UTF-8`. For the selected FFmpeg `-b:v BITRATE` option, every cell matched the [six reference frames](superpowers/plans/2026-11-24-menu-detail-levels-verification.md#simple-80x24). With the `bps` filter applied, the second result (`-b:a`, Stream codecs, 2/2) stayed selected through a complete view cycle at both sizes. All three levels exposed the full 89-character custom category title through scrolling when necessary.

At both 80×24 and 60×16, cancellation restored the original screen, cursor, Readline buffer, termios settings and numbered history. Insertion added `-b:v` before a quoted suffix and restored the cursor to the insertion point. Typing a further character edited that position. The execution sentinel stayed absent and removal cleared the isolated prefix on each target.

## Final source and package checks

From a clean copy of the maintainer-confirmed revision, build the first set and check its digests:

```bash
python3 scripts/build_release.py --output dist/candidate-v0.5.0-alpha
(cd dist/candidate-v0.5.0-alpha && sha256sum -c SHA256SUMS.checksum)
```

Build again from a second clean copy of the same revision with the same toolchain in a fresh directory, such as `dist/candidate-v0.5.0-alpha-2/`. Verify the manifest against the Git blobs and compare all 11 files byte for byte. Supply the first set and the historical installer to each offline sandbox before running its full suite. The [v0.4.0-alpha record](#combined-candidate-verification) gives the fixture and launch procedure.
The five artifacts, five individual checksum files, and aggregate checksum use
the existing release format. No artifact is uploaded automatically.

The package regression harness can inspect and exercise these exact artifacts
instead of building its own temporary candidate:

```bash
export CLI_HELP_TEST_RELEASE_DIR="$PWD/dist/candidate-v0.5.0-alpha"
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
candidate="$PWD/dist/candidate-v0.5.0-alpha"
scratch=$(mktemp -d)
mkdir -p "$scratch/home" "$scratch/config" "$scratch/cache" "$scratch/data" "$scratch/tmp"
env -i PATH="$PATH" HOME="$scratch/home" XDG_CONFIG_HOME="$scratch/config" \
  XDG_CACHE_HOME="$scratch/cache" XDG_DATA_HOME="$scratch/data" TMPDIR="$scratch/tmp" \
  CLI_HELP_PYTHON="$(command -v python3)" PYTHONDONTWRITEBYTECODE=1 \
  bash "$candidate/cli-interactive-help-v0.5.0-alpha-linux-x86_64.run" \
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
