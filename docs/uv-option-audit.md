# uv option audit

First recorded 2026-11-22. This first pass covered 56 bundled rows. See the [expanded inventory and verification](uv-manual-coverage.md) for the later manual comparison.

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

### uv add

`--no-sync` could update requirements and the lockfile while skipping environment installation.

### uv lock

`--check-exists` accepted an existing stale lockfile. Freshness required `--check`.

### uv sync

`--frozen` used an existing lockfile without checking freshness.

### uv tool install

The force selection concerned installation of tool executables.

### uv venv

Replacing an existing environment depended on the release and the target directory.

## Version differences and manual-only options

Prerelease defaults differed between 0.6.14 and 0.13.9. Both accepted `uv venv --clear`, but in 0.6.14 the parser treated it as a compatibility flag and warned that it had no effect.

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

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 21 / 0 / 0 | 1,342 / 0 / 1 | 484.665 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 21 / 0 / 0 | 1,342 / 0 / 1 | 548.797 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 21 / 0 / 0 | 1,342 / 0 / 1 | 485.475 s |

Each Linux suite skipped the Windows-specific probe.
