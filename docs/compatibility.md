# Third-party command compatibility

[Project overview](../README.md) · [Documentation index](README.md) ·
[Driver configuration](profiles-and-drivers.md)

The compatibility matrix covers 162 maintained command paths across 73
executable names. The tiers organize test coverage; they are not measured usage
rankings. A passing case establishes the selected option declarations, argument
counts, and literal insertion behavior for the recorded version. It does not
establish complete option coverage or successful execution of the program's work.

## Programs and command paths

| Tier | Program or package | Tested command paths |
| --- | --- | --- |
| Essential | Git | `git commit`, `git log`, `git diff`, `git status`, `git show`, `git fetch`, `git switch` |
| Essential | curl, Wget, rsync | `curl`, `wget`, `rsync` |
| Essential | Docker and Compose plugin | `docker run`, `docker image ls`, `docker compose up`, `logs`, `exec`, `ps`, `config`, `build`, `pull`, `down`, `run` |
| Essential | GNU file and text utilities | `cp`, `mv`, `rm`, `sort`, `head`, `tail`, `du`, `df`, `sed` |
| Essential | Compression utilities | GNU `gzip`, XZ Utils `xz` |
| Essential | pip | `pip`, `pip install`, `pip download`, `pip3 install` |
| Essential | uv | `uv pip install`, `uv run` |
| Essential | npm and pnpm | `npm`, `npm install`, `npm run`, `pnpm install` |
| Essential | jq and ripgrep | `jq`, `rg` |
| Essential | FFmpeg | `ffmpeg`, `ffprobe` |
| Next | GitHub CLI | `gh pr list/view/create`, `gh repo clone`, `gh issue list/view`, `gh run list/view`, `gh workflow list/view` |
| Next | Kubernetes and Helm | `kubectl get`, `describe`, `logs`, `config view`, `apply`, `delete`, `exec`, `port-forward`; `helm install`, `helm upgrade` |
| Next | AWS CLI | `aws s3 cp`, `aws s3 sync`, `aws ec2 describe-instances` |
| Next | Terraform and OpenTofu | `terraform plan`, `terraform apply`, `tofu plan`, `tofu apply` |
| Next | Rust Cargo | `cargo build`, `cargo test` |
| Next | CMake, Ninja, GCC, Clang | `cmake`, `ninja`, `gcc`, `clang` |
| Extended | rclone, restic, BorgBackup | `rclone`, `rclone copy`, `rclone sync`, `restic backup`, `borg create` |
| Extended | 7-Zip | `7z`, `7zz`; static `7z x`, `7zz x` extraction subsets |
| Extended | ImageMagick | `magick` (version 7), `convert` (version 6) |
| Extended | yt-dlp and VLC | `yt-dlp`, `vlc` |
| Expansion | Linux services and logs | `systemctl status`, `systemctl list-units`, `systemctl show`, `journalctl` |
| Expansion | OpenSSH | `ssh`, `scp`, `sftp` |
| Expansion | Python quality | `pytest`, `ruff check`, `ruff format` |
| Expansion | Additional uv | `uv sync`, `uv add`, `uv lock`, `uv venv`, `uv tool install` |
| Expansion | Go | `go build`, `go test`, `go run`, `go mod tidy` |
| Expansion | .NET | `dotnet build`, `dotnet test`, `dotnet run`, `dotnet publish`, `dotnet restore` |
| Expansion | Linux networking | `ip address`, `ip link`, `ip route`, `ss` |
| Expansion | OpenSSL | `openssl s_client`, `openssl x509`, `openssl dgst` |
| Expansion | JavaScript | `yarn install`, `yarn add`, `yarn run`, `bun run` |
| Expansion | Podman | `podman run`, `podman build`, `podman exec`, `podman logs` |
| Expansion | PostgreSQL shell | `psql` invocation options; SQL and backslash commands excluded |
| Expansion | Terminal and data utilities | Mike Farah `yq eval`, `fd`, `fdfind`, `fzf` |
| Expansion | Automation | `ansible-playbook` |
| Expansion | Cloud | `az account show`, `az vm list`, `az storage blob list`, `gcloud config list`, `gcloud compute instances list`, `gcloud storage ls` |
| Expansion | Git stash | `git stash`, `git stash push`, `git stash pop`, `git stash apply`, `git stash list`, `git stash show` |
| Expansion | Git worktree | `git worktree`, `git worktree add`, `git worktree list`, `git worktree remove`, `git worktree prune` |
| Expansion | Embedded development | `pio run`, `pio device monitor`, equivalent `platformio` routes, `esptool write-flash`, `esptool.py write-flash`, legacy `esptool.py write_flash`, `arduino-cli compile` |

Expansion rows group the new families; each entry retains its filtering tier in
the machine-readable matrix. Priority affects implementation order, not inclusion.
The two Python interpreter/module forms are additional invocation coverage of
these command paths and are not counted as separate executable routes.

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
The [activation and manual composition instructions](profiles-and-drivers.md#activation-and-manual-composition)
describe same-executable merges and conflict rules. `--doctor` identifies the
selected directory and whether it is the supplied collection; `--explain`
identifies each selected route's provenance separately from the static profile.

Drivers specify fixed documentation requests and known global option arity.
Only the listed command paths are adapted. Unknown nested paths fail with a
diagnostic. Tools with conventional root help use generic discovery and need no
additional driver. Curl uses `--help all`, 7-Zip uses `-h`, and ImageMagick uses
`-help`. Rclone root discovery uses `help flags`; `rclone copy --help` exposes
the copy-specific options separately. `rclone sync --help` likewise exposes only
its sync-specific options on the tested version; global flags remain available
from root discovery or a reviewed custom profile.

Compose `exec` and `run` stop option insertion at the first positional service name;
its child command's flags are not Compose flags. Cargo `test` permits a test-name
filter but stops at `--`, before arguments for the test binary. The supplied
Compose parent route declares value and boolean arity for options between
`compose` and its subcommand. For example,
`docker compose -f local.yml --profile debug up --` selects `up` help. Repeated
files/profiles, long equals-attached values, and declared short attached values
are recognized. Root globals such as `docker --context local compose logs`
remain supported. Unknown parent options and incomplete values fail before
discovery; pending values never enter the fixed help request.

The additional Git routes already existed in the built-in registry; their new
matrix entries establish independent captured-manual and insertion contracts.
Compose leaf routes use fixed `compose LEAF --help` requests. Kubernetes leaves
use `help LEAF`; inherited namespace/context arity is explicitly recorded where
leaf help omits it. `kubectl exec` permits pod operands before `--` and rejects
editing the child-command region after it. GitHub issue/run/workflow parents
accept declared `-R`/`--repo` values before their list/view leaf. Filter repetition
and JSON field lists remain ordinary literal operands.

The baseline Unix corpus uses generic discovery, without additional profiles or
drivers. It records GNU Coreutils 9.4, GNU sed 4.9, GNU gzip 1.12, and XZ Utils
5.4.5 help. Required placeholders with optional prefixes such as
`[HOST/]OWNER/REPO` retain their required suffix. Numeric ranges such as XZ's
`-0 ... -9` are excluded instead of becoming a partial option. Individual literal
numeric flags, such as gzip's `-1`, remain supported.
These checks do not establish BSD or BusyBox compatibility. Sed expression
languages, arbitrary attached-only forms, and general short bundles remain
outside the grammar; pending expressions and filenames are never probed.
Explicit profile declarations support the bounded
[attached-only and bundle subsets](argument-syntax.md); generic parsing does not
infer these contracts from arbitrary help syntax.

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
| `passed` | Parsed declarations and selected arity assertions passed, or fixed-route sentinels and curated insertion passed; the report labels the evidence type |
| `failed` | Discovery, required flags, argument counts, excluded syntax, or insertion checks failed |
| `skipped` | The executable was absent from `PATH` |
| `unsupported` | A designated empty-help case or an explicitly incompatible/unverified executable variant |

Probe timeouts, output-limit failures, and process-start failures remain failures,
even for a designated empty-help case. Any failure returns a nonzero status. `--require-all` also rejects skipped and
unsupported cases. Root npm is intentionally an unsupported case for versions
whose help lists commands without option declarations; `npm install` and `npm run`
are tested separately. Consequently, a complete run can contain that documented
unsupported result while its ordinary exit status is zero.

Curated cases check independent sentinel tokens in fixed help/manual output and
every curated literal insertion. Their `arity_evidence` field explicitly labels
arity as deterministic fixture evidence rather than inferred live confirmation.
For systemctl, upstream common help is paired with route-specific curated metadata;
root help alone does not establish leaf compatibility. Git family manuals likewise
do not imply that every documented family flag applies to every leaf.

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
Local dependency installations and provenance for the completed follow-up are
described in the [expansion validation report](compatibility-expansion-validation.md).
Keep current and legacy esptool installations on separate PATHs for their respective
spellings; a single installed major version cannot validate both route contracts.
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

Concrete FFmpeg stream selectors such as `-c:v` are supported. GCC pass-through
switches such as `-Wl,<options>` remain excluded. Generic parsing excludes 7-Zip
brace declarations; curated `7z x`/`7zz x` profiles provide `-o` and `-t` with
attached-only payloads. These static-only paths retain root `-h` documentation
probes and do not add automatic leaf discovery. Matrix `profile_only` and
`documentation_path` fields distinguish that evidence. The OpenSSH profile
enables only its selected declared bundle members. Placeholder selectors and incomplete literal prefixes
must not be offered as substitutes. Supported prefix/module forms, ip keywords,
repeated address/file groups, child boundaries, and executable-name/version
constraints are detailed in [invocation and structured arguments](invocation-and-structured-arguments.md). Git's numeric shorthand `-<number>`
is skipped while its explicit `-n` and `--max-count` aliases remain available.

Discovery can start arbitrary installed programs through their fixed help routes;
the process limits are not a sandbox. See
[discovery and execution boundaries](discovery-and-safety.md).

## Recorded validation

The [complete expansion validation](compatibility-expansion-validation.md) records
the earlier 129-route inventory, deterministic evidence, live versions, skips, and
limits. The following reports describe older snapshots.

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
