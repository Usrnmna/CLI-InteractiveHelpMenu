# Verification of the remaining bundled menus

These seven families account for the last 224 rows in the original 942-row inventory. Each audit links the release references and independent option declarations for its exact command paths. The combined batch adds 273 rows.

| Family | Command menus | Original rows | Audited rows |
| --- | ---: | ---: | ---: |
| [PostgreSQL](psql-manual-coverage.md) | 1 | 21 | 70 |
| [Ansible](ansible-playbook-manual-coverage.md) | 1 | 21 | 61 |
| [Azure CLI](azure-cli-manual-coverage.md) | 3 | 35 | 50 |
| [Google Cloud CLI](gcloud-manual-coverage.md) | 3 | 34 | 91 |
| [Espressif](esptool-manual-coverage.md) | 3 | 30 | 77 |
| [PlatformIO](platformio-manual-coverage.md) | 4 | 68 | 98 |
| [Arduino CLI](arduino-cli-manual-coverage.md) | 1 | 15 | 50 |
| **Total** | **16** | **224** | **497** |

## What the checks exercise

The [Bash/tmux tests](../tests/test_syntax_terminal.py) compare every highlighted label, summary, Details line and line count with the formatter. At 60×16 each menu is searched from its unfiltered state. Escape must restore both the pending command and cursor, and accepting an option must perform the exact literal edit before the existing suffix. Each executable has a recording stub. Only the three guarded Espressif routes require discovery, where the stubs accept fixed root and leaf help. An unexpected invocation leaves a marker and fails the test.

The [boundary regressions](../tests/test_invocation_expansion.py) cover encrypted address/file pairs, diff-file lists and switching back to normal option parsing. Version-aware terminal checks exercise ordinary pairs at all three cursor positions and a mismatched client identity. Native evidence in the linked family audits comes from fixed help, version requests or isolated parser calls. These checks require no database, managed hosts, cloud accounts, serial devices or boards.

## Reproduction

Use the [offline runner](development.md#isolated-local-debugging). Include each required untracked profile, audit, inventory and test file with a separate `--include`. Use the same target-specific [packaged fixtures](yq-eval-manual-coverage.md#reproduction) as the [preceding matrix](devtools-batch-verification.md#reproduction) to supply historical external-client checks. Run the family inventories, affected historical capture, route, parser, insertion and numerical regressions and the four new terminal tests first. Then run `bash tests/run.sh` in one snapshot per target with the packaged fixture environment.

## Compatibility results

| Target | Ubuntu | Python | Focused pass / fail / skip | Full pass / fail / skip | Full unittest duration |
| --- | --- | --- | ---: | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 276 / 0 / 0 | 1,581 / 0 / 1 | 1385.412 s |
| `noble310` | 24.04.5 | 3.10.20 | 276 / 0 / 0 | 1,581 / 0 / 1 | 1569.845 s |
| `noble312` | 24.04.5 | 3.12.3 | 276 / 0 / 0 | 1,581 / 0 / 1 | 1395.456 s |

Each target verified the 497 final menu rows across the 16 routes. The focused count is the number of distinct passing unittest methods. It includes the affected shared regressions and all four terminal walks. Repeated checks of the final Ubuntu launcher option and esptool frequency qualifications count once. The 60×16 checks exercised each menu's search, Details, cancellation and literal insertion. The stubs recorded zero executions of pending commands.

During focused testing, the wide terminal initially showed only part of the longest per-chip frequency and size tables. The flash walk now provides enough rows to compare every line, and the minimum-size checks still run at 60×16. Other focused repairs covered the historical clipped esptool help spelling, a release-only flag and repeated option operands.

The batch required **three full runs**, one per target. Each passed shell syntax, numerical coverage, both profile/driver validations and unittest discovery. Each skipped the Windows-specific probe on Linux. A separately reported CI failure was traced to the Go 1.26 testing-section anchor. Its one-line documentation correction was checked with Lychee separately. A working-tree digest confirmed the executable, profile and test inputs matched the full-suite snapshots. Durations in the table cover unittest execution and discovery. The strict numerical gate passed all **4,426 required records**. All local audit links resolved, and all 94 distinct external targets in the linked batch documents responded successfully, including retries. Discovery-description coverage remains separately tracked in the [roadmap](../ROADMAP.md#discovered-command-help).
