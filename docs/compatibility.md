# Third-party command compatibility

[Project overview](../README.md) · [Documentation index](README.md) ·
[Driver configuration](profiles-and-drivers.md)

The compatibility matrix covers 59 representative command paths across 34
executable names. The tiers organize test coverage; they are not measured usage
rankings. A passing case establishes the selected option declarations, argument
counts, and literal insertion behavior for the recorded version. It does not
establish complete option coverage or successful execution of the program's work.

## Programs and command paths

| Tier | Program or package | Tested command paths |
| --- | --- | --- |
| Essential | Git | `git commit`, `git log`, `git diff` |
| Essential | curl, Wget, rsync | `curl`, `wget`, `rsync` |
| Essential | Docker and Compose plugin | `docker run`, `docker image ls`, `docker compose up`, `docker compose logs`, `docker compose exec` |
| Essential | pip | `pip`, `pip install`, `pip download`, `pip3 install` |
| Essential | uv | `uv pip install`, `uv run` |
| Essential | npm and pnpm | `npm`, `npm install`, `npm run`, `pnpm install` |
| Essential | jq and ripgrep | `jq`, `rg` |
| Essential | FFmpeg | `ffmpeg`, `ffprobe` |
| Next | GitHub CLI | `gh pr list`, `gh pr view`, `gh pr create`, `gh repo clone` |
| Next | Kubernetes and Helm | `kubectl get`, `kubectl describe`, `kubectl logs`, `kubectl config view`, `helm install`, `helm upgrade` |
| Next | AWS CLI | `aws s3 cp`, `aws s3 sync`, `aws ec2 describe-instances` |
| Next | Terraform and OpenTofu | `terraform plan`, `terraform apply`, `tofu plan`, `tofu apply` |
| Next | Rust Cargo | `cargo build`, `cargo test` |
| Next | CMake, Ninja, GCC, Clang | `cmake`, `ninja`, `gcc`, `clang` |
| Extended | rclone, restic, BorgBackup | `rclone`, `rclone copy`, `rclone sync`, `restic backup`, `borg create` |
| Extended | 7-Zip | `7z`, `7zz` |
| Extended | ImageMagick | `magick` (version 7), `convert` (version 6) |
| Extended | yt-dlp and VLC | `yt-dlp`, `vlc` |

The maintained expectations, executable/package names, version requests, and
tiers are in [matrix.json](../tests/fixtures/help/matrix.json). Root help and
subcommand help are separate cases. Successful `pip` root discovery, for example,
does not establish `pip install` compatibility.

## Enable the drivers

The included collection extends the built-in Git and Docker routes. Enable it
from the source checkout:

```bash
export CLI_HELP_DRIVERS="$PWD/config/drivers.example"
python3 cli_help/main.py --check
python3 cli_help/main.py --list-drivers
```

For a default per-user installation, use:

```bash
export CLI_HELP_DRIVERS="${XDG_DATA_HOME:-$HOME/.local/share}/cli-interactive-help/config/drivers.example"
```

Add the appropriate export to the Bash startup configuration for persistence.
An independently maintained collection can instead be copied to a configuration
directory. A single `CLI_HELP_DRIVERS` directory is loaded; combine any existing
custom drivers with the desired supplied drivers before changing that setting.
The installer includes the supplied JSON files, and the updater preserves local
edits through its normal conflict workflow.

Drivers specify fixed documentation requests and known global option arity.
Only the listed command paths are adapted. Unknown nested paths fail with a
diagnostic. Tools with conventional root help use generic discovery and need no
additional driver. Curl uses `--help all`, 7-Zip uses `-h`, and ImageMagick uses
`-help`. Rclone root discovery uses `help flags`; `rclone copy --help` exposes
the copy-specific options separately. `rclone sync --help` likewise exposes only
its sync-specific options on the tested version; global flags remain available
from root discovery or a reviewed custom profile.

Compose `exec` stops option insertion at the first positional service name;
its child command's flags are not Compose flags. Cargo `test` permits a test-name
filter but stops at `--`, before arguments for the test binary. Compose options
between `compose` and its subcommand are not resolved; the existing root global
options, such as `docker --context local compose logs`, remain supported.

## Run the checks

The regular Linux suite validates the driver collection and runs all deterministic
format, insertion, process-isolation, and reporting tests:

```bash
bash tests/run.sh
```

Third-party programs are not needed for the offline compatibility corpus. The
full repository suite still requires the normal Linux build and terminal test
dependencies, including GCC for the native launcher. See
[development requirements](development.md).

The live harness uses the supplied driver collection by default; `--drivers` or
`CLI_HELP_DRIVERS` selects another collection. It performs no package installation:

```bash
python3 tests/live_compatibility.py --report tests/reports/live-programs.json
python3 tests/live_compatibility.py --tier essential --tier next \
  --report tests/reports/live-essential-next.json
python3 tests/live_compatibility.py --case 'aws s3 cp' --case 'jq' \
  --require-all --report tests/reports/live-selected.json
```

Known `--case` selections retain their matrix assertions. New custom cases check
discovery and insertion but have no predefined sentinel or version assertions.
Reports include executable paths, versions, sources, warnings, platform, Python
version, tier, and totals. Every discovered flag is checked for exact insertion;
selected sentinel flags additionally check argument counts. Pending commands
are never run. Fixed version requests supplement the fixed help/manual requests.

| Status | Meaning |
| --- | --- |
| `passed` | Expected declarations and argument counts were found, and insertion checks passed |
| `failed` | Discovery, required flags, argument counts, excluded syntax, or insertion checks failed |
| `skipped` | The executable was absent from `PATH` |
| `unsupported` | A designated empty-help case produced no recognizable options |

Probe timeouts, output-limit failures, and process-start failures remain failures,
even for a designated empty-help case. Any failure returns a nonzero status. `--require-all` also rejects skipped and
unsupported cases. Root npm is intentionally an unsupported case for versions
whose help lists commands without option declarations; `npm install` and `npm run`
are tested separately. Consequently, a complete run can contain that documented
unsupported result while its ordinary exit status is zero.

The live harness defaults to four seconds per help/manual source. Slow executable
startup can be investigated with `--timeout 15`; the accepted range is 0.05–30
seconds, and the selected limit is recorded as `source_timeout_seconds`. A pass
with a longer limit does not establish responsiveness at the default limit or at
the browser's default two-second discovery limit. Version requests retain their
separate ten-second limit.

## Preparing a Linux test environment

Package and executable names can differ: `ripgrep` supplies `rg`, `ninja-build`
supplies `ninja`, and `borgbackup` supplies `borg`. Ubuntu's `7zip` supplies `7z`,
while `7zip-standalone` supplies `7zz`. ImageMagick 6 and 7 use different executable
names and are separate cases. The Compose CLI plugin must be discoverable by
the selected Docker CLI; a working `docker` executable alone is insufficient.

Install distribution packages or official upstream binaries as appropriate for
the test machine. Place optional local binaries on `PATH` before starting the
harness. Use a temporary test home when account configuration should be isolated.
The help and version checks do not require cloud credentials, a Kubernetes
cluster, a Docker daemon, backup repositories, or media input files. Git's
subcommand cases require local Git manual pages and `man-db`; AWS CLI help can
require a local roff renderer.

Ignored `.cache/` storage can hold downloaded binaries and isolated environments.
Reports belong in `tests/reports/`; neither location is included in source release
archives. Maintained synthetic fixtures and bounded captured excerpts remain
tracked and are included in source releases.

## Coverage and remaining limits

The corpus covers nested command resolution, global option values, alias spacing,
boolean negation shorthand, defaults printed by kubectl, AWS typed declarations,
jq's two-value options, optional Cargo arguments, and yt-dlp's required template
with an optional type prefix. It also checks Unicode edits, end-of-options markers,
and runner boundaries for `uv run`, `npm run`, and Docker execution commands.

Specialized joined syntax remains outside the insertion grammar: FFmpeg stream
selectors such as `-c:v`, GCC pass-through switches such as `-Wl,<options>`, and
7-Zip switches such as `-o{Directory}` and `-t{Type}` are excluded. Their literal
prefixes must not be offered as substitutes. Git's numeric shorthand `-<number>`
is skipped while its explicit `-n` and `--max-count` aliases remain available.

Discovery can start arbitrary installed programs through their fixed help routes;
the process limits are not a sandbox. See
[discovery and execution boundaries](discovery-and-safety.md).

## Recorded validation

The [review fixes and compatibility validation](review-fixes-2026-10-23.md)
record regression and live results dated 2026-10-23 for the 59-path matrix. The original
[functional review](functional-review-2026-10-23.md) is retained as a pre-fix record.

On 2026-10-17, the expanded matrix on Ubuntu 24.04 under WSL with an isolated test
home reported **48 passed, 0 failed, 0 skipped, and 1 expected unsupported case**
(npm root help). All 34 executable names were installed. Exact versions and results
are recorded in the local live report and in the provenance of the maintained
captured excerpts. The complete Linux suite passed **372 tests**, including
the added parser, reporting, driver, packaging, and Bash terminal regressions.
All 156 local documentation link targets resolved. Other distributions,
terminal emulators, and unrecorded program versions require their own live run.
AWS CLI major versions and plugin versions must be evaluated independently.
