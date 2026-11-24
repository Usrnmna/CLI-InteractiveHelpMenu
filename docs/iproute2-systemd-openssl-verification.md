# Combined verification for iproute2, systemd and OpenSSL

This batch covers 11 bundled Bash menus. The family audits record the manual inventories, release differences, exclusions and disposable client probes.

| Family | Command paths | First-pass rows |
| --- | --- | ---: |
| [iproute2](iproute2-manual-coverage.md) | `ip address`, `ip link`, `ip route`, `ss` | 36 |
| [systemd](systemd-manual-coverage.md) | `systemctl list-units`, `systemctl show`, `systemctl status`, `journalctl` | 50 |
| [OpenSSL](openssl-manual-coverage.md) | `openssl s_client`, `openssl x509`, `openssl dgst` | 33 |

## Menu checks

The [terminal tests](../tests/test_syntax_terminal.py) open each menu in an interactive Bash session under tmux. At 220×120 they visit every row in profile order and compare the selected label, summary, all formatted Details lines and the displayed line count against the captured terminal cells. A stub records attempted execution of the pending program. Discovery is disabled. These checks exercise the menu with existing operands or filters after the Readline cursor.

At 60×16 each menu has a search, cancellation and literal edit check. The tests read the relevant qualification, check the original line and cursor after Escape, reopen the menu, select an option and verify the resulting edit before the suffix. The [existing minimum-size cases](../tests/test_expansion_terminal.py) cover route prefix matching, journal boot offsets and TLS verification depth.

## Reproducing the batch

Use the [offline sandbox runner](development.md#isolated-local-debugging) with the same working-tree inputs for `host`, `noble310` and `noble312`. Supply one `--include` per required untracked audit, fixture and test file. Run family inventory and shared regression checks before launching the full matrix. For example, this invocation exercises all three wide menu walks plus their embedded minimum-size checks once the files are tracked.

```sh
python3 -I tests/run_sandbox.py --target host -- env PYTHONPATH=tests python3 -B -m unittest -v \
  test_syntax_terminal.SyntaxScreenTests.test_iproute2_manual_menus \
  test_syntax_terminal.SyntaxScreenTests.test_systemd_manual_menus \
  test_syntax_terminal.SyntaxScreenTests.test_openssl_manual_menus
```

For the full suite, use the packaged fixtures and environment in the [yq reproduction instructions](yq-eval-manual-coverage.md#reproduction) and run `bash tests/run.sh` once per target. The [batching workflow](../ROADMAP.md#how-to-audit-a-batch) applies to subsequent families.

## Compatibility results

| Target | Ubuntu | Python | Focused pass / fail / skip | Full pass / fail / skip | Full unittest time |
| --- | --- | --- | ---: | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 44 / 0 / 0 | 1,541 / 0 / 1 | 19m 09s |
| `noble310` | 24.04.5 | 3.10.20 | 44 / 0 / 0 | 1,541 / 0 / 1 | 21m 42s |
| `noble312` | 24.04.5 | 3.12.3 | 44 / 0 / 0 | 1,541 / 0 / 1 | 19m 18s |

The focused counts combine the first run with a targeted rerun. On each target, 43 of 44 tests passed initially. Five subcases in the remaining shared regression assumed a separate dash-leading text value was accepted for the new `ss -f`, `-A`, `-D`, `-F` and `-N` rows. The corrected regression checks the [explicit attachment rule](argument-syntax.md), the negative-number exception and the literal attached form. It passed on all three targets before the full runs began.

Each target inspected all 761 selectable rows. The focused walks across all three targets verified 2,283 row selections and their complete Details. The stubs recorded zero pending command executions. Each full suite skipped only the Windows-specific probe. Full unittest time excludes snapshot creation and suite preflight.

The strict numerical gate verified 3,599 required records across 76 profiles. The three family inventories added 642 rows to the original 119. The original rows retain their relative order and literal insertions. This batch used three full runs for the 11 menus, saving six full runs compared with testing each family in a separate matrix.
