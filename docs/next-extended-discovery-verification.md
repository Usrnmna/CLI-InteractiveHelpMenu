# Next and Extended discovery verification

The [Next inventory](next-discovery-audit.md) covers 65 paths and the [Extended inventory](extended-discovery-audit.md) covers 51. The [fixture matrix](../tests/fixtures/help/matrix.json) preserves route order. The fixed inputs produce 3,399 Next and 3,711 Extended spellings or keywords, counted once per route. Two extraction lines reopen their root menus and add 52 visits. Walking the primary inventory therefore visits 7,162 rows per target.

## What the checks establish

Each route test starts with an empty cache, isolated Bash/tmux session, empty bundled and custom profile directories and a private home. Recording stubs supply only the fixed documentation and identity vectors in the family fixture manifests. The normal discovery refresh must produce exactly the expected spelling-to-operand-count map before the shell menu opens. Every selected row, summary and complete Details is compared with the terminal cells. At 60×16 the test searches from an unfiltered view, scrolls to the end of the selected Details where needed and cancels. The shell must recover the original pending line and cursor. A second selection checks the literal insertion and cursor before an existing quoted operand. Warm openings must issue only any prescribed identity probes. The harness fails on execution of the pending command or any unexpected probe. [Terminal tests](../tests/test_discovery_tier_terminal.py) · [Bash and tmux checks](../tests/test_essential_terminal.py)

The two iproute2 usage-only paths must display the diagnostic and preserve Readline state. Direct discovery of either 7-Zip extraction path must fail before a probe. With both profile sources empty their pending extraction lines can use their audited root menus. The checks also cover child-command and end-of-options boundaries, including CMake mode dispatch, Ninja tools and Go test arguments. [Source and routing limits](discovery-and-safety.md)

The source editions differ from the systems running the menu. The manifests identify the fixed replies and independently expected declarations. The family reports record separately what the manuals say, what client or source checks established, where a fixed response ends and which prior samples are excerpts or synthetic. A separate 23-route replay covers the Resolute/vendor system-tool editions on all three targets. [Developer tools](discovery-next-tools.md) · [Cloud and embedded tools](discovery-cloud-tools.md) · [System tools](discovery-extended-tools.md) · [Media and utilities](discovery-media-utilities.md)

## Reproduction

From the repository root, run the [offline sandbox runner](development.md#isolated-local-debugging) with `--target host`, `--target noble310` or `--target noble312`. Include each required untracked file using its own `--include` argument. The primary terminal command is `env PYTHONPATH=tests python3 -B -m unittest -v test_discovery_tier_terminal`. The second system edition uses `verify_system_source_editions` with the same unittest invocation. The strict gate uses `python3 -B scripts/check_numerical_coverage.py --mode strict --summary`. The full run uses `bash tests/run.sh` with the target's [packaged fixtures](remaining-bundled-verification.md#reproduction) and the existing suite environment used for Essential. [Essential reproduction](essential-discovery-verification.md#reproduction)

## Results

Counts below are passed, failed and skipped for each invocation. Times are unittest elapsed seconds. The selections overlap and should not be summed as unique tests. The shared selection's one skip checks the Windows-specific probe limitation on a POSIX host.

| Focused check | Ubuntu 26.04.1 / Python 3.14.4 | Ubuntu 24.04.5 / Python 3.10.20 | Ubuntu 24.04.5 / Python 3.12.3 |
| --- | --- | --- | --- |
| Historical AWS S3 copy Details in Bash/tmux | 1 / 0 / 0 · 23.728 s | 1 / 0 / 0 · 24.384 s | 1 / 0 / 0 · 22.919 s |
| Early integration, before fixes | 80 / 4 / 0 · 13.236 s | 80 / 4 / 0 · 13.882 s | 80 / 4 / 0 · 13.146 s |
| Shared discovery, cache, presentation, editing and association | 237 / 0 / 1 · 39.535 s | 237 / 0 / 1 · 50.021 s | 237 / 0 / 1 · 40.213 s |
| Historical sources, regression inventory and family readers | 460 / 0 / 0 · 55.393 s | 460 / 0 / 0 · 104.164 s | 460 / 0 / 0 · 57.030 s |
| All primary routes, real terminals | 116 / 0 / 0 · 595.149 s | 116 / 0 / 0 · 646.663 s | 116 / 0 / 0 · 586.479 s |
| Four utility reader regressions and four affected terminal menus | 8 / 0 / 0 · 26.483 s | 8 / 0 / 0 · 33.622 s | 8 / 0 / 0 · 26.670 s |
| Numerical, association and preservation regressions after strict gate | 115 / 0 / 0 · 24.657 s | 115 / 0 / 0 · 39.984 s | 115 / 0 / 0 · 26.747 s |

The early failures exposed three Git manual-association regressions and a missing `go run` menu. The fixes preserve borrowed manual paragraphs with their qualifications, scope selectable Git rows to the operation, and let a recognized Go synopsis supply declarations during refresh. The repaired historical and terminal checks passed. A host system-tool pilot passed 19/0/0 in 89.536 s. The [system-tool runs](discovery-extended-tools.md) record the alternate editions, intermediate failures and final rechecks. The [developer-tool runs](discovery-next-tools.md) cover compiler manuals and mode boundaries. An initial host sandbox setup attempt could not create its private namespace. The offline runner subsequently ran with the required namespace permission.

The independent numerical census compared the changed observations with a clean 10,131-entry baseline. It added five reader sources and removed 266 observations that belonged to other Git operations or systemctl verbs (198 flag and 68 value observations). The review checked the remaining 666 changed fingerprints, including the Git stash-list driver scope, before refreshing the existing dispositions. The resulting 9,870-entry inventory had zero diagnostics. All three strict gates passed, with 4,426 complete records out of 4,426 required. The 6,487 bundled rows in 76 profiles retain their prior reviews.

## Full-suite matrix

Three full suites passed against the same frozen non-Markdown project inputs. The SHA-256 digest of the sorted path and content-hash pairs is `c253e5077b6960a47cda39ba9be1f0d225426b7b2f26fe3199e6396444201bc6`. Source edition and sandbox release are independent. The host used Bash 5.3.9 and both Noble targets used Bash 5.2.21.

| Target | Passed | Failed | Skipped | Suite duration | Exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 1,870 | 0 | 1 | 2,506.826 s | 0 |
| Ubuntu 24.04.5 / Python 3.10.20 | 1,870 | 0 | 1 | 2,779.087 s | 0 |
| Ubuntu 24.04.5 / Python 3.12.3 | 1,870 | 0 | 1 | 2,505.752 s | 0 |

Each target ran the full suite once. All three repeated all 116 primary terminal cases on the frozen source, with zero unexpected documentation requests or pending-command executions. The only skip on each target was `test_probe_reports_the_windows_limitation`, because POSIX hosts complete the probe normally. The non-Markdown source digest matched after all three runs. The combined audit closes 65/65 Next and 51/51 Extended dispositions. Including the earlier 46 Essential dispositions brings discovery coverage to 162/162 paths.

Lychee 0.24.2 checked the maintained Markdown tree with the CI configuration, local heading fragments and the configured cache of successful external responses. All 3,209 link occurrences passed across 1,706 unique targets, with zero errors and zero timeouts.
