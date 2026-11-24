# uv manual coverage

The five bundled menus cover 454 selectable spellings across Astral uv 0.6.14 and 0.13.9. The 56 first-pass rows retain their order, operand labels and literal insertions. The revisit adds 398 rows. Each row describes the releases on which a spelling or its behavior differs. [First-pass audit](uv-option-audit.md)

## Manual inventory

The manual columns count distinct spellings on each command path, including short forms, long aliases and inherited options. Each menu includes both manuals' spellings, options described in the surrounding prose, and the parser-confirmed compatibility forms recorded below. A spelling shared across paths counts once on each path.

| Menu | First pass | 0.6.14 manual | 0.13.9 manual | Added | Selectable | Value-taking |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [uv add](../profiles/uv-add.json) | 12 | 79 | 100 | 101 | 113 | 59 |
| [uv lock](../profiles/uv-lock.json) | 11 | 59 | 67 | 65 | 76 | 40 |
| [uv sync](../profiles/uv-sync.json) | 12 | 81 | 96 | 98 | 110 | 52 |
| [uv tool install](../profiles/uv-tool-install.json) | 10 | 67 | 89 | 88 | 98 | 57 |
| [uv venv](../profiles/uv-venv.json) | 11 | 45 | 50 | 46 | 57 | 25 |
| **Total** | **56** | **331** | **402** | **398** | **454** | **233** |

Grouping short forms, parser aliases and cross-release renames gives 350 path-specific option families and 104 alternate spellings. This count groups the five occurrences of `--native-tls` with `--system-certs`, and `add --raw-sources` with `--raw`. Their release-specific behavior remains explicit. All documented spellings and operand arities for the five paths reconcile.

The old and new manuals respectively contain 274 and 318 long-option headings. All headings and their argument arities match the corresponding release executable's expanded help. The newer web manual lists additional long aliases on the same heading. For example, all five menus accept the inherited `--no-cache-dir` alias for `--no-cache`. Both releases declare it in the cache crate. The newer manual also repeats `--config-settings-package` as its own alias on four paths. Each spelling appears once per menu. [0.6.14 generated reference](https://github.com/astral-sh/uv/blob/0.6.14/docs/reference/cli.md) · [Astral command reference](https://docs.astral.sh/uv/reference/cli/) · [0.6.14 cache arguments](https://github.com/astral-sh/uv/blob/0.6.14/crates/uv-cache/src/cli.rs) · [0.13.9 cache arguments](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-cache/src/cli.rs)

The ten [native declaration fixtures](../tests/fixtures/uv-manual) retain usage, section order, short flags, long flags, repeated switches and required operand labels from `uv help COMMAND`. The [manual alias table](../tests/fixtures/uv-manual/manual-aliases.tsv) supplies the web manual's additional long spellings. The [compatibility table](../tests/fixtures/uv-manual/compatibility.tsv) records additional accepted spellings, their equivalents and operand arity on each release. For example, `lock --locked` checks freshness and `lock --frozen` checks existence. They are documented in the descriptions of `--check` and `--check-exists`. Fixed-argument forms such as `sync --no-group dev` are explained on the corresponding `--no-dev` row. [0.6.14 CLI declarations](https://github.com/astral-sh/uv/blob/0.6.14/crates/uv-cli/src/lib.rs) · [0.13.9 CLI declarations](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-cli/src/lib.rs)

Ubuntu's amd64 package-contents searches for paths ending in `bin/uv` returned no results in Noble and Resolute, and both suite-specific `uv(1)` pages returned HTTP 404. The reviewed executables are upstream releases. The three-target compatibility matrix measures the menu on Ubuntu. [Noble package contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fuv&mode=path&suite=noble&arch=amd64) · [Resolute package contents](https://packages.ubuntu.com/search?searchon=contents&keywords=bin%2Fuv&mode=path&suite=resolute&arch=amd64)

## Changes that affect commands

| Menu | Behavior documented in Details |
| --- | --- |
| add | Supply one or more positional requirements or repeat `-r FILE`. `--extra` enables an extra of the dependency, while `--optional` places the dependency in a published project extra. The 0.13.9 preview `--bounds minor` writes a compatible minor range. `--raw` omits inferred bounds. Its older spelling `--raw-sources` originally documented the placement of source metadata. |
| lock | The command operates on the discovered project or a named inline-metadata script. `--check-exists` accepts a stale lockfile. The upload cutoff applies to distribution files, and a bare calendar date includes the full day in the system time zone. Both releases accept absolute cutoffs. Version 0.13.9 also accepts unit-bearing durations and the lowercase disabling value `false`. |
| sync | `--only-group NAME` omits the project and its ordinary dependencies. The 0.13.9 manual describes the inverse installation filters in prose. For example, `--only-install-package NAME` can leave a package's dependencies uninstalled. `--inexact` preserves unrelated packages and `--no-exact` is its alias. |
| tool install | Supply the main package as a positional requirement. `--with` adds requirements inside its private environment. On 0.13.9, `--with-executables-from` also exposes their commands. `--python-platform` changes wheel selection while source builds run on the host. The preview `--torch-backend` selects an index specifically for the PyTorch ecosystem. |
| venv | The optional positional path selects the new environment. Index and link settings affect installation of seeds. In 0.6.14, the hidden long `--clear` is a compatibility no-op and the short `-c` is unavailable. Version 0.13.9 accepts both spellings, and requires `--force` as well to clear a nonempty ordinary directory. |
| Shared options | The native certificate store switch changed from `--native-tls` to `--system-certs`. The old spelling still works in 0.13.9. Version 0.6.14 accepts `-V` and `--version` after each command path. Version 0.13.9 takes the version request at the root as `uv --version`. On Linux, package linking defaults to hard links in 0.6.14 and copy-on-write cloning in 0.13.9. |

Time and version numbers retain their distinct meanings. The date-only cutoff selects the beginning of the next local calendar day. A relative day in 0.13.9 is exactly 24 hours, and calendar months and years are rejected. A package-specific cutoff accepts `PACKAGE=false` to exempt one package even when a global cutoff applies. The separate prerelease contracts preserve each release's default and meanings. Platform and PyTorch backend identifiers retain the release's accepted tokens. [0.6.14 cutoff parser](https://github.com/astral-sh/uv/blob/0.6.14/crates/uv-resolver/src/exclude_newer.rs) · [0.13.9 cutoff parser](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-distribution-types/src/exclude_newer.rs) · [Per-package override parser](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-configuration/src/exclude_newer.rs) · [Prerelease policy](https://github.com/astral-sh/uv/blob/0.13.9/crates/uv-configuration/src/prerelease.rs)

## Verification

The [offline inventory tests](../tests/test_uv_manual_inventory.py) compare every spelling, arity and alias to release evidence. They check all 454 literal insertions with a pending quoted Unicode suffix, the first-pass order, fixed output levels, structured value scopes and release-specific grammar. Short value forms accept both `-p3.12` and `-p 3.12`. Long value forms accept a following token or `=VALUE`. A literal `--` ends option selection.

Fresh offline host runs used both upstream binaries, a disposable project, two generated wheels and isolated cache, tool and executable directories. The following effects were observed.

| Run | Observed effect |
| --- | --- |
| Add from a local requirements file | `--requirement` recorded the local package with a lower bound on 0.6.14. On 0.13.9, `--bounds minor` added the upper boundary. |
| Lock and check cutoffs | Both versions accepted a calendar date and an explicit UTC timestamp. Only 0.13.9 accepted `7 days`, `P7D` and `false`. Both rejected `1 month`. The new version also accepted a package-specific `false` override. Both check aliases succeeded against a current lockfile. |
| Sync selected local wheels | The 0.6.14 exclusion filter skipped the named distribution. The 0.13.9 inclusion filter installed only the named distribution. The resulting environment contained the expected executable in each case. |
| Install a tool and a second package | `--with` exposed only the main command on 0.6.14. `--with-executables-from` exposed both commands on 0.13.9. |
| Create an environment in a populated ordinary directory | Both releases refused `--clear` alone and preserved the marker file. On 0.13.9, `-c --force` removed the marker and created the environment. Version 0.6.14 rejected `-c`. |

The native probes exercised local package and filesystem behavior. Remote indexes, TLS trust stores, external build backends, accelerator detection and foreign-platform wheels were reviewed against release documentation. The combined report records rendered menu checks and complete suite results for the supported Linux/Python combinations. [Terminal and suite results](devtools-batch-verification.md#compatibility-results)
