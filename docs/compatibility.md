# Third-party command compatibility

[Project overview](../README.md) · [Documentation index](README.md) ·
[Driver configuration](profiles-and-drivers.md)

The compatibility matrix covers 162 maintained command paths across 73
executable names. The tiers organize test coverage; they are not measured usage
rankings. A passing case establishes the selected option declarations, argument
counts, and literal insertion behavior for the recorded version. It does not
establish complete option coverage or successful execution of the program's work.

## Ubuntu default coverage

On Ubuntu 24.04 and 26.04, root discovery can use a packaged reference when installed help yields no selectable declarations. It requires an installed executable, checks known provider paths and package revisions, and opens only the matching reference shard. Optional executables can be installed independently. Ubuntu 26.04 image results and the supported package-manager and Bash editions are recorded in the [Ubuntu coverage audit](ubuntu-coverage-audit.md).

## Programs and command paths

Each tier inventory lists every command in matrix order, the source edition, and the outcome for that path.

| Tier | Paths | What the captured documentation supplied |
| --- | ---: | --- |
| [Essential](essential-discovery-audit.md) | 46 | 45 selectable menus. The npm root supplied usage and command names. |
| [Next](next-discovery-audit.md) | 65 | 65 selectable menus, including cloud, compiler and development commands. |
| [Extended](extended-discovery-audit.md) | 51 | 47 selectable menus. The audited ip link and ip route sources yielded usage-only diagnostics. The 7z x and 7zz x extraction paths use static profiles with root documentation available separately. |

The [machine-readable matrix](../tests/fixtures/help/matrix.json) owns the test tiers, executable/package names, version requests and historical expectations. Root and subcommand requests are separate cases. Python interpreter/module invocations add coverage of existing commands. See the [module forms and their boundaries](invocation-and-structured-arguments.md#python-module-documentation).

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
brace declarations. The static extraction profiles distinguish overlapping switches such
as `-m` and `-mmt` and preserve attached values such as a quoted `-o` path.
The [7-Zip extraction inventory](7zip-extraction-manual-coverage.md) gives the release limits. These paths retain root `-h` documentation
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

### Ubuntu and Python test results

The full Linux suite (`bash tests/run.sh`) passed locally and on GitHub Actions
for all three combinations below. The local runs tested the working tree with
the vi keybinding regression test fix. On November 21, 2026 (Pacific time),
GitHub Actions ran the same suite after that fix reached `main` in commit
[`b0c88c8`](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/commit/b0c88c8f0c2275c6eb0bcc57f973844467c743be).

| Ubuntu | Python | Local sandbox and versions | GitHub Actions full-suite step |
| --- | --- | --- | --- |
| 24.04 | 3.10 | Rootless Podman · Ubuntu 24.04.5 · Python 3.10.20 | [Passed on ubuntu-24.04](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/44994019434/job/137121060893) |
| 24.04 | 3.12 | Rootless Podman · Ubuntu 24.04.5 · Python 3.12.3 | [Passed on ubuntu-24.04](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/44994019434/job/137121061094) |
| 26.04 | 3.14 | Bubblewrap · Ubuntu 26.04.1 · Python 3.14.4 | [Passed on ubuntu-26.04](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/44994019434/job/137121061037) |

Each local run passed 1,326 tests and skipped one Windows-only probe test.
The hosted results link to the individual jobs in [workflow run 71](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/actions/runs/44994019434).
For local reproduction, see [isolated local debugging](development.md#isolated-local-debugging).

### Third-party command validation

For bundled help, the [family inventories](audit-history.md#bundled-menu-progress) map the selectable rows to their manuals. For discovery, see the [Essential](essential-discovery-audit.md), [Next](next-discovery-audit.md) and [Extended](extended-discovery-audit.md) route dispositions. Their tests use fixed documentation and inert targets in real terminals. The [combined offline matrix](next-extended-discovery-verification.md#full-suite-matrix) records 1,870 passes and one Windows-only skip per target on that later snapshot. Hosted results above apply to the linked commit.

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
