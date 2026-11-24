# Mike Farah yq eval manual coverage

The [inventory](yq-eval-manual-inventory.md) reconciles 51 option effects and 18 aliases. The 15 original rows retain their order. The 54 additions bring the selectable total to 69 in six categories. The [bundled profile](../profiles/yq-eval.json) keeps the first-positional editing boundary and the existing Mike Farah v4 identity requirement.

## Material changes

- **Split output.** The query produces results. A separate expression passed to `--split-exp` names each result, with `$index` starting at zero. Repeated names replace earlier results. An explicit alphanumeric suffix is kept. Otherwise JSON gets `.json`, properties gets `.properties` and other encodings get `.yml`. In 4.44.3 the parent directory must exist. In 4.54.3 the writer creates directories and normally confines output to the current directory and its descendants. The `--split-exp-file` operand supplies the naming expression from a file and takes precedence over an inline naming expression. [4.44.3 split writer](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/pkg/yqlib/printer_writer.go) · [4.54.3 split writer](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/printer_writer.go)
- **Queries and inputs.** An existing filename is normally treated as data. `--expression` forces a literal query. An existing first positional file with the suffix `.yq` supplies the query automatically. Use `--from-file 'query file.yq'` to select a query file explicitly. A nonempty file expression wins over `--expression`. Input filenames then supply the documents, in sequence. A positional `-` reads stdin at that point. [Argument parser](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/utils.go) · [Sequential evaluator](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/evaluate_sequence_command.go)
- **In-place editing.** Results for all inputs replace the first file after successful evaluation. Errors such as a missing later input or an unsuccessful `-e` retain the original. The evaluator rejects in-place editing with split output. The 4.54.3 release also rejects direct updates to read-only files and replaces a destination symlink itself. [4.54.3 release notes](https://github.com/mikefarah/yq/releases/tag/v4.54.3) · [In-place writer](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/write_in_place_handler.go)
- **Framing and formatting.** `-N` suppresses YAML document markers. `-0` terminates each result with NUL. `-r` controls scalar unwrapping. `-P` resets styles. These operations can be selected separately. Output-format, indentation and component-specific Details qualify behavior by release. [Result printer](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/printer.go) · [Format inventory](yq-eval-manual-inventory.md#formats-and-release-differences)

## Verification

The [release tests](../tests/test_yq_packaged.py) check the SHA-256 of each Linux amd64 executable against the upstream release checksum before running it in the offline sandbox. Without `YQ_TEST_BINDIR`, the six executable tests skip and the rendered-menu tests use fixed release help. Supplying the variable requires both matching binaries. The [inventory tests](../tests/test_yq_manual_inventory.py) compare literal spellings, aliases and required operands with independent fixed help, cover the hidden compatibility flag, and retain the provenance of the earlier captures.

| Release | Asset | SHA-256 |
| --- | --- | --- |
| [4.44.3](https://github.com/mikefarah/yq/releases/tag/v4.44.3) | `yq_linux_amd64` | `a2c097180dd884a8d50c956ee16a9cec070f30a7947cf4ebf87d5f36213e9ed7` |
| [4.54.3](https://github.com/mikefarah/yq/releases/tag/v4.54.3) | `yq_linux_amd64` | `129534601871538efe0ba4c5e62a34fb1d5f469bcb975c4fddeb467d82974973` |

### Observed executable behavior

The fixture assertions check status, stdout and stderr independently of the resulting files. Each process has a disposable working directory. The following byte strings use escaped newlines and NUL bytes.

| Case | Result |
| --- | --- |
| Split a two-document YAML stream | With `-N` and names derived from `$index`, status 0, empty stdout/stderr. The only split files were `item-0.yml` containing `n: one\n` and `item-1.yml` containing `n: two\n`. A file-based naming expression took precedence over an inline name. |
| Split both results into an existing `fixed.txt` | Status 0, empty stdout/stderr. The original bytes and the first result were replaced. Final bytes were `n: two\n`. Version 4.44.3 rejected a missing parent directory with status 1 and a diagnostic. Version 4.54.3 created the directory and wrote `ok\n`. |
| Update two inputs with `-i '.n += 1'` | Status 0, empty stdout/stderr. First file became `n: 2\n---\nn: 3\n`. Second file stayed `n: 2\n`. Selecting nothing with `-e`, naming a missing later input, or combining `-i` with split output returned 1, printed a diagnostic on stderr, emitted no stdout and left both inputs intact. |
| File permissions and links | On a writable directory with an owned mode-0444 input, 4.44.3 returned 0, emitted no stdout/stderr and changed the file from `n: 1\n` to `n: 3\n`. Version 4.54.3 returned 1 with a read-only diagnostic on stderr and preserved the original bytes. With a symlink to a writable input, both pinned clients returned 0 with empty stdout/stderr, replaced the link with a regular file containing `n: 2\n`, and left the target at `n: 1\n`. |
| Split path outside the working directory | A disposable sibling destination received `n: 1\n` on 4.44.3. Version 4.54.3 returned 1 with empty stdout and a path-rejection diagnostic. The destination remained absent. Explicitly enabling `--security-allow-write-any-path` on 4.54.3 wrote the expected bytes with status 0 and empty stdout/stderr. |
| Load a CRLF query, read two named files and stdin | Separate and equals forms of `--from-file`, a positional `.yq` file, and a query file combined with `--expression` all emitted `first\nsecond\npiped\nlast\n` with `-N`. The query file retained its bytes. |
| Null input, exit status and framing | `-n` ignored piped data and rejected an explicit stdin operand. A sequence with any qualifying result succeeded even if it ended in false. Zero, an empty string and `False` each succeeded. Only null and lowercase false, or no output, failed. `-N -0` produced `one\0two\0`. Explicit `-r=false` preserved a quoted YAML scalar and inline comment. |
| Format selection and indentation | A JSON filename selected JSON. Explicit `-pjson` on stdin selected YAML output until `-ojson` was supplied. Nested YAML at widths 0 and 10 produced 4 and 2 spaces on 4.44.3, and 2 and 9 on 4.54.3. A 4.54.3 INI fixture decoded a colon-delimited key. The older client rejected INI. |
| CLI forms | All captured value-taking spellings required an operand. Both releases accepted explicit false on the captured boolean spellings, separate and attached indentation values, and the deprecated JSON shortcuts with a warning. Both rejected `eval --version` and Kislyuk’s `--in-place`. |

### Rendered menu

The [Bash/tmux tests](../tests/test_syntax_terminal.py) inspect the selected label, summary and every wrapped line of Details for each row at 220×120. The example driver is enabled. A PATH wrapper records requests and permits only `--version` and `eval --help`. With the release fixtures present, those probes go to the checksum-matched binary. A separate session supplies Kislyuk’s identity and checks rejection before the leaf-help probe. The input buffer and cursor are inspected through Readline. [Recording fixture](../tests/test_terminal_screen.py)

At 60×16 the expression-file test searches for “read the query”, scrolls to the role of the following filenames, cancels, reopens and inserts `--from-file` before both original filenames. Typing `'query file.yq'` leaves the cursor immediately before the first filename. The [earlier regression](../tests/test_expansion_terminal.py) still searches “combined results”, reaches the first-file rule and inserts a quoted `--expression`. Separate editor checks cover an option-looking string inside the quoted query and the positional boundary.

### Reproduction

Place the two release assets in the ignored directory `tests/reports/yq-revisit/` as executable files named `yq-4.44.3` and `yq-4.54.3`. For independent checksum verification, each release publishes `checksums` with the asset name followed by digests in the order listed in `checksums_hashes_order`. Select the SHA-256 column for `yq_linux_amd64`. Set `TARGET` to `host`, `noble310` or `noble312`. Include each new project file until tracked. [Sandbox runner](development.md#isolated-local-debugging)

```bash
files=(--include tests/reports/yq-revisit/yq-4.44.3
       --include tests/reports/yq-revisit/yq-4.54.3)
while IFS= read -r path; do files+=(--include "$path"); done < <(
  git ls-files --others --exclude-standard -- 'tests/fixtures/yq/*' \
    'tests/test_yq_*.py' 'docs/yq-eval-manual-*.md'
)
python3 -I tests/run_sandbox.py --target "$TARGET" "${files[@]}" -- \
  env YQ_TEST_BINDIR=tests/reports/yq-revisit PYTHONPATH=tests python3 -m unittest -v \
  test_yq_manual_inventory test_yq_packaged \
  test_system_dependency_followup.SystemDependencyFollowupTests.test_installed_leaf_help_provenance_and_curated_flags \
  test_module_discovery.VariantAndSelectorTests.test_yq_requires_mike_farah_major_four \
  test_expansion_systems.SystemsExpansionTests.test_child_commands_expressions_and_end_markers_are_not_parent_options \
  test_numerical_diagnostics.NumericalDiagnosticTests.test_yq_nul_switch_retains_both_sources \
  test_numerical_debt_resolution.NumericalDebtResolutionTests.test_yq_zero_negative_and_ignored_encoder_cases_remain_qualified \
  test_numerical_migration.NumericalMigrationTests.test_display_fields_and_formatter_expose_essential_meaning \
  test_numerical_inventory.NumericalInventoryTests.test_real_source_counts_are_independent_and_reviews_are_complete \
  test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline \
  test_expansion_terminal.ExpansionScreenTests.test_yq_first_file_warning_and_explicit_expression \
  test_syntax_terminal.SyntaxScreenTests.test_yq_all_rows_and_complete_details \
  test_syntax_terminal.SyntaxScreenTests.test_yq_rejects_kislyuk_in_bash \
  test_syntax_terminal.SyntaxScreenTests.test_yq_expression_file_before_two_inputs
```

For the full suite, supply the same yq files and environment plus the private Ubuntu package fixtures described in the [FFmpeg full-suite setup](ffmpeg-manual-coverage.md#reproducing-the-sandbox-checks), then execute `bash tests/run.sh` inside that sandbox. Run the independent inventory gate with `python3 -B scripts/check_numerical_coverage.py --mode strict --summary`.

The first full run exposed a historical test that required every current spelling to appear in the captured 4.54.1 help. Its revised assertion checks all 64 captured spellings and the exact five additions needed to obtain the 69-row profile. The versioned fixtures and their original matrix provenance are preserved. [Historical capture regression](../tests/test_system_dependency_followup.py)

## Compatibility results

| Target | Ubuntu | Python | Mike Farah yq | Focused pass / fail / skip | Full pass / fail / skip | Full duration |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 4.44.3 and 4.54.3 | 21 / 0 / 0 | 1,524 / 0 / 1 | 17m 59s |
| `noble310` | 24.04.5 | 3.10.20 | 4.44.3 and 4.54.3 | 21 / 0 / 0 | 1,524 / 0 / 1 | 20m 58s |
| `noble312` | 24.04.5 | 3.12.3 | 4.44.3 and 4.54.3 | 21 / 0 / 0 | 1,524 / 0 / 1 | 18m 26s |

Each full run skipped only the Windows-specific probe. All 207 row inspections across the three targets matched the menu and its formatted Details. The recording wrappers detected zero executions of the pending command. The strict numerical gate passed all 3,123 required contracts across 76 profiles. The configured Lychee check passed all 269 link occurrences in the six changed Markdown documents, including heading fragments. The inventory reconciles every applicable spelling in the two pinned releases. The next manual-coverage revisit is iproute2.
