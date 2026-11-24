# uv option audit

The first-pass profiles contained 56 selectable entries. The [full manual revisit](uv-manual-coverage.md) records the expanded inventory, release differences and verification. The comparison covers Astral uv 0.13.9 and the 0.6.14 reference used by the bundled structured value guidance. Option order, operand labels and literal insertions are preserved.

## Sources

| Profile | Entries | Astral command reference |
| --- | ---: | --- |
| [uv add](../profiles/uv-add.json) | 12 | [Add requirements](https://docs.astral.sh/uv/reference/cli/#uv-add) |
| [uv lock](../profiles/uv-lock.json) | 11 | [Lock a project](https://docs.astral.sh/uv/reference/cli/#uv-lock) |
| [uv sync](../profiles/uv-sync.json) | 12 | [Sync a project](https://docs.astral.sh/uv/reference/cli/#uv-sync) |
| [uv tool install](../profiles/uv-tool-install.json) | 10 | [Install a tool](https://docs.astral.sh/uv/reference/cli/#uv-tool-install) |
| [uv venv](../profiles/uv-venv.json) | 11 | [Create an environment](https://docs.astral.sh/uv/reference/cli/#uv-venv) |

All 56 flags appear in the current command reference and in the corresponding 0.13.9 long help. The tagged 0.6.14 command reference covers 55. Its exception is `uv venv --clear`, a hidden compatibility flag in that release. The comparison also used the release-specific CLI declarations, dependency and tool guides. [0.13.9 CLI declarations](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-cli/src/lib.rs) · [0.6.14 generated manual](https://github.com/astral-sh/uv/blob/0.6.14/docs/reference/cli.md) · [Project dependencies](https://github.com/astral-sh/uv/blob/0.13.9/docs/concepts/projects/dependencies.md) · [Tool environments](https://github.com/astral-sh/uv/blob/0.13.9/docs/concepts/tools.md)

Neither Ubuntu suite's amd64 package-contents search returned an executable ending in `bin/uv`. The release-specific `uv(1)` pages returned HTTP 404. Astral’s manuals and the two identified upstream binaries therefore supply the version-specific evidence. The Ubuntu results below establish compatibility of the menu on those operating systems. [Noble package contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fuv&mode=path&suite=noble&arch=amd64) · [Resolute package contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fuv&mode=path&suite=resolute&arch=amd64)

## Disposition of the original entries

Rows shared across commands are counted once per menu. “Sufficient” describes the original summary. Details can still supply an example, interaction or limit.

| Option on all five menus | Original disposition | Menu decision |
| --- | --- | --- |
| `--offline` | Sufficient | Explain the available inputs when network access is disabled. Local files and cached data can still satisfy the request. |
| `--no-cache` | Inaccurate | The command uses a temporary cache. It bypasses the persistent cache and can still download data. |
| `--directory DIRECTORY` | Sufficient | Changing directory also changes the base for relative paths. |
| `--project PROJECT` | Incomplete | This sets the discovery starting point. Relative operands still use the working directory. Tool installations retain their own environment. |

### uv add

| Option | Original disposition | Menu decision |
| --- | --- | --- |
| `--dev` | Incomplete | Name the dev group, its `--group dev` alias and its exclusion from published metadata. |
| `--optional EXTRA` | Incomplete | The extra belongs to the project being edited. Consumers can select this published extra. |
| `--group GROUP` | Incomplete | Identify the dependency-groups table and distinguish dependency groups from published extras. |
| `--editable` | Incomplete | Show a local directory operand and explain how Python source edits reach the environment. |
| `--no-sync` | Incomplete | The project requirements and lockfile can change while installation is skipped. |
| `--locked` | Incomplete | Adding a requirement fails if the lockfile is missing or must change. |
| `--rev REV` | Sufficient | Show its use with a Git source and the separate branch and tag switches. |
| `--python PYTHON` | Redundant | Replace the repeated parser description with the interpreter’s role in resolution and syncing. Retain the structured request grammar. |

### uv lock

| Option | Original disposition | Menu decision |
| --- | --- | --- |
| `--upgrade` | Incomplete | Refresh package data and reconsider all locked versions within constraints. |
| `--upgrade-package PACKAGE` | Incomplete | Refresh the named package and allow a new version. The requirement can carry a constraint. |
| `--check` | Sufficient | State the failure cases and the `--locked` equivalence. |
| `--check-exists` | Incomplete | An existing stale lockfile passes. Freshness requires `--check`. |
| `--resolution STRATEGY` | Incomplete | Explain highest, lowest and lowest-direct, including transitive dependencies. |
| `--prerelease STRATEGY` | Incomplete | Give the distinct defaults and meanings in 0.6.14 and 0.13.9. Both structured variants retain their source scope. |
| `--python PYTHON` | Redundant | Name its use when building for metadata and when inferring the minimum Python version. |

### uv sync

| Option | Original disposition | Menu decision |
| --- | --- | --- |
| `--extra EXTRA` | Incomplete | A repeatable extra selects packages for installation. All extras participate in resolution. Conflicting selections fail. |
| `--all-extras` | Incomplete | Install every extra, subject to declared conflicts. |
| `--no-dev` | Incomplete | Only the dev group is excluded. Other default groups can remain active. |
| `--locked` | Incomplete | A stale or missing lockfile fails the check. Creation of the project environment can precede the error. |
| `--frozen` | Incomplete | Read the existing lockfile without checking freshness. New requirements can be absent and a missing lockfile is an error. |
| `--no-install-project` | Sufficient | Skip the current package and keep its dependencies, allowing a separate build cache layer. |
| `--dry-run` | Incomplete | Preview changes to both the lockfile and the environment. |
| `--python PYTHON` | Redundant | An interpreter path chooses Python for the project environment, even when the path points into another environment. |

### uv tool install

| Option | Original disposition | Menu decision |
| --- | --- | --- |
| `--with PACKAGE` | Incomplete | Install an additional requirement in the same isolated tool environment. |
| `--with-editable PACKAGE` | Incomplete | The operand is a local package directory. Source edits remain visible to the tool. |
| `--force` | Incomplete | Replace colliding executable names. In 0.13.9 the tool environment is recreated. |
| `--reinstall` | Incomplete | Refresh data and reinstall even packages already at the selected version. |
| `--upgrade` | Incomplete | Permit newer compatible versions and refresh cached package data. |
| `--python PYTHON` | Redundant | Select the interpreter used to build the tool’s private environment. The tool guide specifies that discovery ignores a project-local Python pin and the project’s requires-python value. |

### uv venv

| Option | Original disposition | Menu decision |
| --- | --- | --- |
| `--seed` | Incomplete | Name pip and the additional setuptools and wheel seeds for Python versions before 3.12. |
| `--clear` | Incomplete | Identify the version limit and the additional force flag needed to clear a nonempty ordinary directory in 0.13.9. |
| `--system-site-packages` | Incomplete | Distinguish runtime import visibility from the packages managed by uv pip. |
| `--prompt PROMPT` | Inaccurate | Correct the structured default. Without a positional path, the current directory supplies the name. An explicit path uses the environment directory name. A literal dot selects the current directory name. |
| `--relocatable` | Incomplete | Move the environment as a unit. The guarantee covers standard console and GUI entry points. Binaries receive no rewriting. |
| `--allow-existing` | Incomplete | Create in place without clearing prior files. An interpreter change can leave incompatible files behind. |
| `--python PYTHON` | Redundant | Identify the base interpreter and the discovery rule for existing environments. |

## Version differences and manual-only options

The 0.6.14 prerelease default accepts packages that publish only prereleases and first-party requirements with explicit prerelease specifiers. In 0.13.9 the default is `if-necessary`. Stable candidates are tried first and prereleases may be considered when the acceptable stable candidates are exhausted. The older default spelling `if-necessary-or-explicit` is a deprecated alias for the new policy in 0.13.9. [0.6.14 resolver options](https://github.com/astral-sh/uv/blob/0.6.14/docs/reference/cli.md#uv-lock) · [0.13.9 prerelease modes](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-configuration/src/prerelease.rs)

In 0.6.14, creating at an existing virtual environment replaces it by default. It accepts the undocumented `--clear` spelling and warns that the flag has no effect. A nonempty ordinary directory is refused. On 0.13.9, `--clear` can replace a virtual environment, while clearing a nonempty ordinary directory requires the additional `--force` option. Both versions can create in place with `--allow-existing`. [0.6.14 compatibility flag and warning](https://github.com/astral-sh/uv/blob/0.6.14/crates/uv-cli/src/compat.rs#L269-L298) · [0.13.9 venv options](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-cli/src/lib.rs)

The first-pass selection omitted other documented options. Examples include `add --requirements`, `--branch` and `--tag`, `lock --refresh`, `sync --inexact` and `--no-default-groups`, `tool install --with-requirements`, and `venv --no-project`. Package index configuration, build isolation and interpreter download settings also remain in the upstream reference. These bundled-menu checks do not count toward the separate discovery audit.

## Executable checks

Each Ubuntu target ran both uv binaries against generated local wheels and disposable projects. The newer executable reported 0.13.9. The 0.6.14 executable came from the manylinux x86_64 wheel after verification against the release's SHA-256 digest. The offline sandboxes used their own tool directories, caches and base interpreters. [0.6.14 release files and digests](https://pypi.org/pypi/uv/0.6.14/json)

| Fixture | Observed result |
| --- | --- |
| Add a local wheel to an extra | `add --optional docs --no-sync` recorded the extra and wrote the lockfile. It left the project without a virtual environment. |
| Introduce a dependency-group change after locking | `lock --check` failed. `lock --check-exists` passed. A dry run left both the original lockfile bytes and the absent environment unchanged. |
| Sync from the stale lockfile | `sync --locked` failed and left a newly created environment. `sync --frozen --extra docs` succeeded and installed the locked wheel without rewriting the lockfile. |
| Resolve a requirement of at least 1.5 with only 1.0 and 2.0rc1 available | The 0.13.9 default selected 2.0rc1. The 0.6.14 default failed, then succeeded with `--prerelease allow`. |
| Install a tool with an extra requirement | `tool install --with` exposed the main executable and made the added requirement importable in that tool’s own environment. |
| Reuse or replace a directory | Both versions preserved a marker with `--allow-existing` and honored an explicit prompt. In 0.13.9, `--clear` replaced an existing environment and refused a nonempty ordinary directory until paired with `--force`. In 0.6.14, the compatibility flag emitted a no-effect warning and the ordinary directory survived. Default recreation removed the marker from a virtual environment. |
| Supply a relative environment path from outside the project | `venv --project` created the explicit path under the working directory. `venv --directory` created the same relative path under the selected directory. |

## Rendered menus and offline suites

On each target, a Bash/tmux session opened each menu with discovery disabled. At 210×100 every highlighted row, summary and complete Details pane was checked against the profile and formatted value guidance. Cancellation restored the line and cursor. Selecting `--optional`, `--prerelease`, `--extra`, `--with` and `--prompt` inserted the respective literal spelling before an existing `--offline` suffix. A shell stub recorded accidental execution and remained unused.

At 60×16, searches from the five unfiltered menus found `add --no-sync`, `lock --check-exists`, `sync --frozen`, `tool install --force`, and `venv --clear`. The checks scrolled to the qualifications about environment updates, stale lockfiles, missing lockfiles, executable replacement, and 0.6.14 directory handling. A permanent regression verifies the frozen-lock explanation and preserves a pending `--extra docs` suffix through cancellation and insertion. [Terminal regression](../tests/test_expansion_terminal.py) · [Sandbox procedure](development.md#isolated-local-debugging)

The 21 focused checks on each target covered the rendered regression, development profile declarations, literal insertion, Python request guidance and inventory reconciliation. The 71 refreshed review fingerprints correspond to the five profile files, their command descriptions and category descriptions, and the 56 reviewed options. [Numerical inventory review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 21 / 0 / 0 | 1,342 / 0 / 1 | 484.665 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 21 / 0 / 0 | 1,342 / 0 / 1 | 548.797 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 21 / 0 / 0 | 1,342 / 0 / 1 | 485.475 s |

Each full run included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. The single skip on each Linux target was the Windows-specific probe.
