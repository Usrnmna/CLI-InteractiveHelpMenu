# Regression review: option descriptions and terminal presentation

Verified on 2026-10-26 against the current working tree. The review identified and repaired declaration regressions, then repeated the complete applicable suite. This establishes the recorded offline and terminal behavior; it does not establish all possible command grammars, installed-version compatibility, or absence of every defect.

## Results and evidence

- Linux/WSL Python 3.12.3: **1318 tests run, 1316 passed, 0 failures, 0 errors, 2 skips**.
- Windows Python 3.13: **402 portable tests passed**, zero failures/errors/skips. No native Windows Bash/curses acceptance claim.
- Per-path offline audit: **358 tests passed** (also included in the full Linux total; not additive).
- Preflight: **12 checks passed**, covering six Bash syntax checks, bundled and configured-driver validation, inventory reconciliation, strict numerical preservation and exact command/driver listings.
- [Machine-readable coverage and tested-file hashes](regression-coverage.json).
- Local detailed evidence under `tests/reports/current-regression/`: `linux-suite.json` (Linux test outcomes), `linux-suite.log` (Linux log), `windows-portable.log` (Windows log), `inventory.json` (per-path details), and `preflight.json` (preflight). These logs are local ignored artifacts and are absent from fresh checkouts; the matrix and outcome snapshot above are maintained files.

## Inventory and boundaries

Inventory combines both built-in and configured driver routes, all bundled profiles, the primary compatibility matrix, supplemental capture/workflow manifests, and the twelve Python module forms. Capture labels such as Yarn `(classic)`/`(modern)` and Go help topics are attached to their command paths rather than counted as commands. There are 357 named implementation paths plus the captured generic-root `find` case: **358 rows**, including **317 registry routes**, **76 profiles**, **96 categories**, and **942 option/keyword records**. The primary matrix alone has 162 cases and is not the full inventory.

All 942 bundled records were selected and drawn at 60×16, 100×24 and 160×32, with shrink/grow redraws, search, modal navigation, preview/cancel, exact midline insertion, Unicode suffix and cursor assertions. Separate tests cover below-minimum dimensions, long declarations/descriptions, scrolling, absent/malformed guidance, qualifications, warnings, blank results and stale-cell clearing. These exhaustive checks use the documented cell model; representative tmux checks establish actual cells and terminal restoration.

182 paths have bundled or fixture documentation; 176 have routing-only evidence. The 283 fixture variants include seven empty parses. An empty parse records safe processing, not proof that every upstream option was recognized. Missing documentation/rendering evidence is explicitly marked below. Arbitrary executables and user-defined drivers/profiles form an open-ended extension interface; their grammar and rejection boundaries are tested as functions, rather than represented as a finite list of target programs.

Linux environment: Ubuntu 24.04 under WSL2, Python 3.12.3, Bash 5.2.21, tmux 3.4 and GCC 13.3.0. Static GUI checks disable discovery. Inspected process-contract tests use private executable doubles and fixed help/manual arguments; the test named `kubectl_live_fixed_help` runs an instrumented fixture, not installed kubectl. No supported target is executed merely to claim compatibility. Install/update/release checks use disposable homes/prefixes, fake download clients and isolated terminal sockets.

## Fixes and preservation review

The initial complete run had 955 tests, five failures, two errors and two skips. Failures concerned stale preservation review identities and lost sed aliases. Additional inventory comparison exposed pytest choice-set aliases and psql shared-equals/annotated aliases. Four focused parser regressions were established before correction.

- Complete comma-containing operands now remain intact for brace, angle and square placeholders; their following aliases survive.
- Shared `=` declarations preserve psql aliases and literal insertion syntax. Repeated lowercase operands preserve sed `-e`/`--expression=` and `-f`/`--file=`.
- Quoted alias labels are preserved without inventing a required value, and trailing declaration commas no longer become summaries.
- Cache generation is **16**. Old parsed caches become misses through the existing permitted discovery path; imported/curated files are not overwritten.
- The shared terminal sanitizer is included in the protected-source inventory. **109 fingerprints** were reassessed against a disposable pre-fix snapshot (`d97ac6f`); existing classifications, uncertainties, qualifications, exception lists and gate rules were preserved. One false SSH `-KR` observation embedded in prose was removed from the review index; its original captured source remains intact. One sanitizer-source census entry was added.
- No layout redesign, documentation deletion, commit, push or publication was performed.

Package tests exercised the repaired runtime and verification sources before the
final reporting-only Markdown/JSON files and documentation-index link were added.
Those report files were checked separately for local links and evidence integrity.

| Original fix | Confirmed evidence |
|---|---|
| Description preservation | Captured AWS exclusion opening, ambiguous spaces/tabs, aliases, types, multiline text and option-like prose; new alias regressions; AWS rendered description. |
| OPTIONS rows | Every bundled option at three widths; native rsync/ls/grep/tar resize and insertion; complete-or-absent qualified guidance and visible review markers. |
| Opening duplication | Six real captures in model and tmux checks; exact opening rule, blank lines, near matches, merged sources and legitimate later repetitions. |
| Terminal remnants | ESC/C1 CSI and string forms, charset designators, overstrikes, malformed recovery, large inputs, validation rejection and isolated native rendering. |

## Major function coverage

Each row names assertions that ran successfully; module-level totals are supplemental, not a substitute for these mappings.

| Function | Status | Test evidence |
|---|---|---|
| Profile/key configuration and overrides | pass | `test_core.BrowserTests.test_config_validation`<br>`test_core.BrowserTests.test_custom_keys_merge_with_defaults`<br>`test_core.EditingTests.test_custom_profile_overrides_bundled_definition` |
| Driver loading and safe routes | pass | `test_drivers.DriverValidationTests.test_example_drivers_load_without_installed_programs`<br>`test_drivers.DriverValidationTests.test_routes_reject_templates_shell_text_and_action_first_argv` |
| Help parsing and ambiguous descriptions (step 1) | pass | `test_parser_association.ParserAssociationTests.test_captured_aws_exclusion_description_preserves_its_opening`<br>`test_parser_association.ParserAssociationTests.test_description_spacing_preserves_aliases_values_and_continuations`<br>`test_parser_association.ParserAssociationTests.test_option_mentions_in_prose_are_preserved_without_becoming_aliases` |
| Alias/operand regressions repaired during review | pass | `test_parser_association.ParserAssociationTests.test_comma_choices_keep_complete_operands_and_following_aliases`<br>`test_parser_association.ParserAssociationTests.test_shared_equals_alias_retains_psql_variable_declaration`<br>`test_parser_association.ParserAssociationTests.test_mirrored_lowercase_operands_and_quoted_alias_annotations_survive`<br>`test_parser_association.ParserAssociationTests.test_trailing_declaration_comma_is_not_description_prose` |
| Width-aware rows and qualifications (step 2) | pass | `test_numerical_presentation.NumericalPresentationTests.test_option_descriptions_align_and_keep_the_same_column_when_scrolling`<br>`test_numerical_presentation.NumericalPresentationTests.test_value_hint_is_complete_or_absent_and_summary_remains_visible`<br>`test_numerical_presentation.NumericalPresentationTests.test_review_and_uncertainty_notices_survive_narrow_rows` |
| Conservative opening deduplication (step 3) | pass | `test_presentation_descriptions.DescriptionPresentationTests.test_real_captured_opening_descriptions_appear_once`<br>`test_presentation_descriptions.DescriptionPresentationTests.test_exact_line_boundary_rule_preserves_blank_lines_and_near_matches` |
| Complete terminal-sequence filtering (step 4) | pass | `test_terminal_sanitization.TerminalSanitizationTests.test_known_remnants_are_removed_before_profile_validation_and_rendering`<br>`test_terminal_sanitization.TerminalSanitizationTests.test_incomplete_sequences_recover_without_consuming_following_prose`<br>`test_terminal_sanitization.TerminalSanitizationTests.test_large_and_repeated_unterminated_inputs_remain_bounded`<br>`test_terminal_sanitization.TerminalSanitizationTests.test_display_defense_does_not_weaken_profile_validation` |
| Source association and import round trip | pass | `test_parser_association.ParserAssociationTests.test_actual_captures_round_trip_with_source_scope_and_original_sections`<br>`test_parser_association.ParserAssociationTests.test_separate_alias_pairs_do_not_share_targeted_documentation` |
| Literal insertion, suffix and character cursor | pass | `test_core.EditingTests.test_replace_whole_partial_token_at_middle_cursor`<br>`test_core.EditingTests.test_equal_option_leaves_cursor_at_value`<br>`test_core.EditingTests.test_unicode_character_cursor_and_suffix`<br>`test_core.EditingTests.test_quoted_shell_symbols_are_literal` |
| Navigation, focus, filtering and scrolling | pass | `test_functional_matrix.SearchNavigationTests.test_navigation_is_clamped_and_focus_default`<br>`test_functional_matrix.SearchNavigationTests.test_search_matches_flag_summary_and_detail_case_insensitively`<br>`test_functional_matrix.SearchNavigationTests.test_long_profile_window_scrolling`<br>`test_functional_matrix.SearchNavigationTests.test_vi_keys_drive_the_browser_loop` |
| Search cancellation and reopening | pass | `test_native_numerical_terminal.NativeNumericalTerminalTests.test_unresolved_guidance_and_search_cancellation_remain_nonfatal`<br>`test_native_numerical_terminal.NativeNumericalTerminalTests.test_minimum_width_resize_unicode_and_reopen_restore_terminal_and_buffer` |
| Empty results, Unicode and resize | pass | `test_numerical_presentation.NumericalPresentationTests.test_unicode_declarations_align_in_cells_and_empty_results_clear_rows`<br>`test_numerical_presentation.NumericalPresentationTests.test_resize_shrink_grow_and_reopen_preserve_selection_and_reachable_text` |
| Absent/valid/malformed optional guidance | pass | `test_numerical_presentation.NumericalPresentationTests.test_every_opted_in_bundled_option_retains_formatter_lines`<br>`test_numerical_presentation.NumericalPresentationTests.test_malformed_metadata_is_nonfatal_and_does_not_guess_units`<br>`test_numerical_presentation.NumericalPresentationTests.test_partial_and_absent_contracts_do_not_become_loading_gates` |
| Native captured descriptions and narrow/wide redraw | pass | `test_display_regression_terminal.CapturedDescriptionScreenTests.test_opening_description_and_spacing_survive_real_rendering` |
| Native terminal cells, history and restoration | pass | `test_terminal_screen.OptionsLayoutTests.test_bundled_descriptions_survive_resize_and_literal_insertion`<br>`test_terminal_screen.ScreenTests.test_top_and_bottom_cancellation_restore_cells_cursor_and_history`<br>`test_terminal_screen.ScreenTests.test_insertion_across_bottom_margin_preserves_scrollback` |
| Module grammar and fixed interpreter requests | pass | `test_module_discovery.ModuleCaptureTests.test_both_interpreters_every_module_route_preserve_exact_prefix_and_cursor`<br>`test_module_discovery.ModuleDiscoveryTests.test_both_interpreters_all_supported_pip_paths_have_fixed_help_operands`<br>`test_module_discovery.ModuleDiscoveryTests.test_unsupported_forms_are_rejected_before_any_probe` |
| Cache freshness and interpreter identities | pass | `test_module_freshness.ModuleFreshnessTests.test_changed_module_under_same_interpreter_invalidates_cache`<br>`test_module_freshness.ModuleFreshnessTests.test_expiration_and_refresh_requery_help_but_warm_hits_only_check_version`<br>`test_module_freshness.ModuleFreshnessTests.test_man_and_off_modes_never_probe_module_identity` |
| Cache invalidation after display/parser fixes | pass | `test_terminal_sanitization.TerminalSanitizationTests.test_previous_sanitizer_cache_identity_cannot_reuse_remnants` |
| Manual import: text/roff and overwrite protection | pass | `test_manual_import.ManualImportTests.test_text_import_creates_loadable_profile_and_manual_only_driver`<br>`test_manual_import.ManualImportTests.test_local_roff_path_is_passed_literally_to_man`<br>`test_manual_import.ManualImportTests.test_reimport_requires_replace_and_preserves_existing_files` |
| Bulk collection: filters, limits and interruption | pass | `test_bulk_scan.BulkScanTests.test_glob_filters_and_limit_report_unprocessed_commands`<br>`test_bulk_scan.BulkScanTests.test_interruption_checkpoints_results_and_marks_remaining_jobs`<br>`test_bulk_scan.BulkScanTests.test_cli_summary_report_and_exit_policies` |
| Review: edit, preview, save and cancellation | pass | `test_review.ReviewTests.test_real_terminal_edit_preview_save_and_cancel_never_run_target`<br>`test_review.ReviewTests.test_save_retains_scan_evidence_and_creates_loadable_corrected_pair_and_backups`<br>`test_review.ReviewTests.test_external_changes_to_selected_files_or_report_prevent_overwrite` |
| Collection inspection and explicit recovery | pass | `test_collection.CollectionTests.test_complete_collection_is_read_only_and_snapshot_is_stable`<br>`test_collection.CollectionTests.test_backup_restoration_is_explicit_byte_preserving_and_repeatable`<br>`test_collection.CollectionTests.test_stale_snapshot_and_changed_sources_refuse_writes`<br>`test_collection.CollectionTests.test_cli_inspection_emits_safe_json_and_requires_explicit_recovery_choices` |
| Passive diagnostics and sensitive-input redaction | pass | `test_context_diagnostics.PassiveDiagnosticTests.test_passive_modes_never_launch_probes_or_write_files`<br>`test_context_diagnostics.PassiveDiagnosticTests.test_pending_values_unknown_prefixes_and_operands_are_not_reported`<br>`test_context_diagnostics.PassiveDiagnosticTests.test_cli_diagnostics_do_not_create_bytecode_or_echo_rejected_cursor` |
| Installation/reinstallation/uninstallation | pass | `test_installation.InstallationTests.test_install_reinstall_and_uninstall_restore_original_rc_bytes_and_mode`<br>`test_installation.InstallationTests.test_installer_never_executes_existing_startup_code`<br>`test_installation.InstallationTests.test_installed_adapter_inserts_without_executing_the_pending_command` |
| Update preservation, rollback and edited-code safety | pass | `test_update.UpdateTests.test_edited_installed_code_is_never_executed_by_validation`<br>`test_update.UpdateTests.test_edited_files_settings_extras_and_deletions_are_preserved`<br>`test_update.UpdateTests.test_failed_switch_restores_previous_runtime`<br>`test_update.UpdateTests.test_updated_adapter_inserts_without_execution` |
| Update review and guided merge | pass | `test_update_review.UpdateReviewTests.test_edited_merge_remains_custom_and_cannot_execute_itself`<br>`test_update_review.UpdateReviewTests.test_real_terminal_diff_replace_save_and_insertion`<br>`test_update_review.UpdateReviewTests.test_stale_local_report_incoming_and_state_stop_save` |
| Guided line-level decisions and preview | pass | `test_guided_merge.GuidedMergeTests.test_all_decisions_preserve_exact_selected_input`<br>`test_guided_merge.GuidedMergeTests.test_preview_does_not_decide_undecided_blocks`<br>`test_guided_merge.GuidedReviewTests.test_real_terminal_guided_changes_save_and_pending_command_is_unexecuted` |
| Release build, checksums and source packaging | pass | `test_release.ReleaseTests.test_all_checksums_and_source_provenance_match`<br>`test_release.ReleaseTests.test_normalized_archives_and_native_build_are_repeatable`<br>`test_release.ReleaseTests.test_source_archive_excludes_reports_caches_and_prior_releases`<br>`test_release.ReleaseTests.test_self_extracting_install_update_and_uninstall` |
| Packaged runtime, historical upgrade and fake GitHub update | pass | `test_release_snapshot.CandidatePackageTests.test_archives_manifest_modes_and_current_source_agree`<br>`test_release_snapshot.CandidatePackageTests.test_historical_install_upgrade_and_source_only_lifecycle`<br>`test_release_snapshot.CandidatePackageTests.test_built_archive_github_update_uses_fixtures_and_rejects_tampering` |
| External evidence, uncertainty and numerical gate | pass | `test_numerical_diagnostics.NumericalDiagnosticTests.test_current_strict_readiness_has_no_debt_or_exceptions`<br>`test_numerical_diagnostics.NumericalDiagnosticTests.test_nested_manual_context_does_not_become_verified_root_compatibility`<br>`test_numerical_diagnostics.NumericalDiagnosticTests.test_synthetic_vlc_and_unversioned_pip_do_not_inherit_versioned_evidence` |
| CLI command and driver listings | pass | `preflight.json: --list-commands (76 exact profile paths)`<br>`preflight.json: --list-drivers (317 exact registry routes)` |

## Lower-priority findings

1. **Search cancellation can retain a changed category.** Open the bundled rsync profile on its first category, type `/zz`, then Escape. Intermediate substring matches can move the category; Escape restores the filter but not the earlier category/selection. This behavior exists before steps 1–4 (`d97ac6f` uses the same search-state handling). Impact: navigation surprise. Recommended follow-up: decide whether cancellation should restore query only or the full selection/focus/scroll state, then add a focused state-snapshot test. No behavior change was made during this review.
2. **Full AWS captures retain later repetitions and example fragments.** Parse `captured.json["aws s3 cp"]["text"]`, select `--exclude`, and inspect its complete details. A generic “Documented option” block and later example/output fragments precede or follow the useful description. This is source-association/merging behavior present in the pre-fix snapshot; it is not an exactly duplicated opening summary. Impact: noisy details and potentially ambiguous inferred argument metadata. Recommended follow-up: separately scope usage/example exclusion and repeated declaration precedence against unchanged captures. Do not broaden deduplication to delete arbitrary repeated text.
3. **Malformed terminal string payloads may remain literal.** Unterminated OSC/DCS-style input retains ambiguous payload through conservative recovery. This is an intentional preservation limit, not an unhandled terminal control. A stricter policy requires evidence that the residual payload is safe to discard.

## Skips and remaining gaps

- `test_bash_pty.BashIntegrationTests.test_select_inserts_without_executing_then_normal_enter_executes`: **skip** — Task safety: this test explicitly executes its pending sentinel command; passive insertion is covered separately.
- `test_functional_matrix.EdgeCaseTests.test_probe_reports_the_windows_limitation`: **skip** — POSIX hosts complete the probe normally
- The Windows-only process-limitation assertion was run successfully in the separate Windows checks. The deliberately executing sentinel test remains skipped; passive insertion and pending-state assertions passed elsewhere. No pending command was submitted to close this gap.
- **176 routing-only paths:** provide reviewed help/manual fixtures with independent flag/arity sentinels, then run the per-path audit to add documentation and rendering evidence.
- **Live upstream versions:** not tested. Controlled fixtures cannot establish installed-version compatibility. Closing this gap requires a separately authorized, isolated fixed-help/manual campaign, never pending command execution.
- **Platforms:** Python 3.10, standalone non-WSL Linux, macOS, other architectures/terminal emulators and native Windows Bash/curses were not verified in this run. Repeat the offline gate on those supported environments; use representative native terminal checks where available. Historical hosted results are not substituted for current results.
- **Display limits:** ambiguous-width emoji/grapheme behavior, accessibility and every terminal/Readline release remain unverified. Add representative captures and target-terminal acceptance checks for those requirements.
- **Release delivery:** local candidate compilation, checksums, extraction, install/update/uninstall, historical upgrade and mocked GitHub retrieval were tested. Actual network downloads, hosted CI and publication were not performed.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/regression_review.py
PYTHONPATH=tests python3 -B -m unittest test_regression_inventory test_display_regression_terminal -v
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
```

The review runner applies the explicit pending-execution skip and static-GUI harness settings. It otherwise discovers the complete `test_*.py` suite. The raw first-run failures, focused red/green logs and fingerprint reconciliation remain in `tests/reports/current-regression/`.

## Command-path matrix

**R** = routing/path recognition; **B** = bundled rendering/insertion (category/option counts); **F** = parsed fixture variants (nonempty/total); **T** = explicitly mapped real-terminal evidence. `not tested` is not a pass. Each row’s exact test ID, source provenance and fixture-level counts are in [the JSON matrix](regression-coverage.json). All live-target cells are **not tested**.

| Command path | R | B categories/options | F nonempty/total | T | Test suffix |
|---|---|---|---|---|---|
| `7z` | pass | not tested | pass 3/3 | not tested | `test_path_000_7z` |
| `7z x` | pass | pass 1/4 | pass 1/1 | not tested | `test_path_001_7z_x` |
| `7zz` | pass | not tested | pass 3/3 | not tested | `test_path_002_7zz` |
| `7zz x` | pass | pass 1/4 | pass 1/1 | not tested | `test_path_003_7zz_x` |
| `ansible-playbook` | pass | pass 1/21 | pass 1/1 | not tested | `test_path_004_ansible_playbook` |
| `arduino-cli` | pass | not tested | not tested | not tested | `test_path_005_arduino_cli` |
| `arduino-cli compile` | pass | pass 1/15 | pass 2/2 | not tested | `test_path_006_arduino_cli_compile` |
| `aws` | pass | not tested | not tested | not tested | `test_path_007_aws` |
| `aws ec2` | pass | not tested | not tested | not tested | `test_path_008_aws_ec2` |
| `aws ec2 describe-instances` | pass | not tested | pass 2/2 | not tested | `test_path_009_aws_ec2_describe_instances` |
| `aws s3` | pass | not tested | not tested | not tested | `test_path_010_aws_s3` |
| `aws s3 cp` | pass | not tested | pass 2/2 | pass | `test_path_011_aws_s3_cp` |
| `aws s3 sync` | pass | not tested | pass 1/1 | not tested | `test_path_012_aws_s3_sync` |
| `az` | pass | not tested | not tested | not tested | `test_path_013_az` |
| `az account show` | pass | pass 1/8 | pass 2/2 | not tested | `test_path_014_az_account_show` |
| `az storage blob list` | pass | pass 1/16 | pass 2/2 | not tested | `test_path_015_az_storage_blob_list` |
| `az vm list` | pass | pass 1/11 | pass 2/2 | not tested | `test_path_016_az_vm_list` |
| `borg` | pass | not tested | not tested | not tested | `test_path_017_borg` |
| `borg create` | pass | not tested | pass 2/2 | not tested | `test_path_018_borg_create` |
| `bun` | pass | not tested | not tested | not tested | `test_path_019_bun` |
| `bun run` | pass | pass 1/8 | pass 2/2 | not tested | `test_path_020_bun_run` |
| `cargo` | pass | not tested | not tested | not tested | `test_path_021_cargo` |
| `cargo build` | pass | not tested | pass 2/2 | not tested | `test_path_022_cargo_build` |
| `cargo test` | pass | not tested | pass 1/1 | not tested | `test_path_023_cargo_test` |
| `clang` | pass | not tested | pass 2/2 | not tested | `test_path_024_clang` |
| `cmake` | pass | not tested | pass 2/2 | not tested | `test_path_025_cmake` |
| `convert` | pass | not tested | pass 2/2 | not tested | `test_path_026_convert` |
| `cp` | pass | not tested | pass 1/1 | not tested | `test_path_027_cp` |
| `curl` | pass | not tested | pass 2/2 | pass | `test_path_028_curl` |
| `df` | pass | not tested | pass 1/1 | not tested | `test_path_029_df` |
| `docker` | pass | not tested | not tested | not tested | `test_path_030_docker` |
| `docker attach` | pass | not tested | not tested | not tested | `test_path_031_docker_attach` |
| `docker build` | pass | not tested | pass 1/1 | not tested | `test_path_032_docker_build` |
| `docker commit` | pass | not tested | not tested | not tested | `test_path_033_docker_commit` |
| `docker compose` | pass | not tested | not tested | not tested | `test_path_034_docker_compose` |
| `docker compose build` | pass | not tested | pass 1/1 | not tested | `test_path_035_docker_compose_build` |
| `docker compose config` | pass | not tested | pass 1/1 | not tested | `test_path_036_docker_compose_config` |
| `docker compose down` | pass | not tested | pass 1/1 | not tested | `test_path_037_docker_compose_down` |
| `docker compose exec` | pass | not tested | pass 1/1 | not tested | `test_path_038_docker_compose_exec` |
| `docker compose logs` | pass | not tested | pass 1/1 | not tested | `test_path_039_docker_compose_logs` |
| `docker compose ps` | pass | not tested | pass 1/1 | not tested | `test_path_040_docker_compose_ps` |
| `docker compose pull` | pass | not tested | pass 1/1 | not tested | `test_path_041_docker_compose_pull` |
| `docker compose run` | pass | not tested | pass 1/1 | pass | `test_path_042_docker_compose_run` |
| `docker compose up` | pass | not tested | pass 2/2 | not tested | `test_path_043_docker_compose_up` |
| `docker container` | pass | not tested | not tested | not tested | `test_path_044_docker_container` |
| `docker container attach` | pass | not tested | not tested | not tested | `test_path_045_docker_container_attach` |
| `docker container commit` | pass | not tested | not tested | not tested | `test_path_046_docker_container_commit` |
| `docker container cp` | pass | not tested | not tested | not tested | `test_path_047_docker_container_cp` |
| `docker container create` | pass | not tested | not tested | not tested | `test_path_048_docker_container_create` |
| `docker container diff` | pass | not tested | not tested | not tested | `test_path_049_docker_container_diff` |
| `docker container exec` | pass | not tested | not tested | not tested | `test_path_050_docker_container_exec` |
| `docker container export` | pass | not tested | not tested | not tested | `test_path_051_docker_container_export` |
| `docker container inspect` | pass | not tested | not tested | not tested | `test_path_052_docker_container_inspect` |
| `docker container kill` | pass | not tested | not tested | not tested | `test_path_053_docker_container_kill` |
| `docker container logs` | pass | not tested | not tested | not tested | `test_path_054_docker_container_logs` |
| `docker container ls` | pass | not tested | not tested | not tested | `test_path_055_docker_container_ls` |
| `docker container pause` | pass | not tested | not tested | not tested | `test_path_056_docker_container_pause` |
| `docker container port` | pass | not tested | not tested | not tested | `test_path_057_docker_container_port` |
| `docker container prune` | pass | not tested | not tested | not tested | `test_path_058_docker_container_prune` |
| `docker container rename` | pass | not tested | not tested | not tested | `test_path_059_docker_container_rename` |
| `docker container restart` | pass | not tested | not tested | not tested | `test_path_060_docker_container_restart` |
| `docker container rm` | pass | not tested | not tested | not tested | `test_path_061_docker_container_rm` |
| `docker container run` | pass | not tested | not tested | not tested | `test_path_062_docker_container_run` |
| `docker container start` | pass | not tested | not tested | not tested | `test_path_063_docker_container_start` |
| `docker container stats` | pass | not tested | not tested | not tested | `test_path_064_docker_container_stats` |
| `docker container stop` | pass | not tested | not tested | not tested | `test_path_065_docker_container_stop` |
| `docker container top` | pass | not tested | not tested | not tested | `test_path_066_docker_container_top` |
| `docker container unpause` | pass | not tested | not tested | not tested | `test_path_067_docker_container_unpause` |
| `docker container update` | pass | not tested | not tested | not tested | `test_path_068_docker_container_update` |
| `docker container wait` | pass | not tested | not tested | not tested | `test_path_069_docker_container_wait` |
| `docker context` | pass | not tested | not tested | not tested | `test_path_070_docker_context` |
| `docker context create` | pass | not tested | not tested | not tested | `test_path_071_docker_context_create` |
| `docker context export` | pass | not tested | not tested | not tested | `test_path_072_docker_context_export` |
| `docker context import` | pass | not tested | not tested | not tested | `test_path_073_docker_context_import` |
| `docker context inspect` | pass | not tested | not tested | not tested | `test_path_074_docker_context_inspect` |
| `docker context ls` | pass | not tested | not tested | not tested | `test_path_075_docker_context_ls` |
| `docker context rm` | pass | not tested | not tested | not tested | `test_path_076_docker_context_rm` |
| `docker context show` | pass | not tested | not tested | not tested | `test_path_077_docker_context_show` |
| `docker context update` | pass | not tested | not tested | not tested | `test_path_078_docker_context_update` |
| `docker context use` | pass | not tested | not tested | not tested | `test_path_079_docker_context_use` |
| `docker cp` | pass | not tested | not tested | not tested | `test_path_080_docker_cp` |
| `docker create` | pass | not tested | not tested | not tested | `test_path_081_docker_create` |
| `docker diff` | pass | not tested | not tested | not tested | `test_path_082_docker_diff` |
| `docker events` | pass | not tested | not tested | not tested | `test_path_083_docker_events` |
| `docker exec` | pass | not tested | not tested | not tested | `test_path_084_docker_exec` |
| `docker export` | pass | not tested | not tested | not tested | `test_path_085_docker_export` |
| `docker history` | pass | not tested | not tested | not tested | `test_path_086_docker_history` |
| `docker image` | pass | not tested | not tested | not tested | `test_path_087_docker_image` |
| `docker image build` | pass | not tested | not tested | not tested | `test_path_088_docker_image_build` |
| `docker image history` | pass | not tested | not tested | not tested | `test_path_089_docker_image_history` |
| `docker image import` | pass | not tested | not tested | not tested | `test_path_090_docker_image_import` |
| `docker image inspect` | pass | not tested | not tested | not tested | `test_path_091_docker_image_inspect` |
| `docker image load` | pass | not tested | not tested | not tested | `test_path_092_docker_image_load` |
| `docker image ls` | pass | not tested | pass 2/2 | not tested | `test_path_093_docker_image_ls` |
| `docker image prune` | pass | not tested | not tested | not tested | `test_path_094_docker_image_prune` |
| `docker image pull` | pass | not tested | not tested | not tested | `test_path_095_docker_image_pull` |
| `docker image push` | pass | not tested | not tested | not tested | `test_path_096_docker_image_push` |
| `docker image rm` | pass | not tested | not tested | not tested | `test_path_097_docker_image_rm` |
| `docker image save` | pass | not tested | not tested | not tested | `test_path_098_docker_image_save` |
| `docker image tag` | pass | not tested | not tested | not tested | `test_path_099_docker_image_tag` |
| `docker images` | pass | not tested | not tested | not tested | `test_path_100_docker_images` |
| `docker import` | pass | not tested | not tested | not tested | `test_path_101_docker_import` |
| `docker info` | pass | not tested | not tested | not tested | `test_path_102_docker_info` |
| `docker inspect` | pass | not tested | not tested | not tested | `test_path_103_docker_inspect` |
| `docker kill` | pass | not tested | not tested | not tested | `test_path_104_docker_kill` |
| `docker load` | pass | not tested | not tested | not tested | `test_path_105_docker_load` |
| `docker login` | pass | not tested | not tested | not tested | `test_path_106_docker_login` |
| `docker logout` | pass | not tested | not tested | not tested | `test_path_107_docker_logout` |
| `docker logs` | pass | not tested | not tested | not tested | `test_path_108_docker_logs` |
| `docker network` | pass | not tested | not tested | not tested | `test_path_109_docker_network` |
| `docker network connect` | pass | not tested | not tested | not tested | `test_path_110_docker_network_connect` |
| `docker network create` | pass | not tested | not tested | not tested | `test_path_111_docker_network_create` |
| `docker network disconnect` | pass | not tested | not tested | not tested | `test_path_112_docker_network_disconnect` |
| `docker network inspect` | pass | not tested | not tested | not tested | `test_path_113_docker_network_inspect` |
| `docker network ls` | pass | not tested | not tested | not tested | `test_path_114_docker_network_ls` |
| `docker network prune` | pass | not tested | not tested | not tested | `test_path_115_docker_network_prune` |
| `docker network rm` | pass | not tested | not tested | not tested | `test_path_116_docker_network_rm` |
| `docker pause` | pass | not tested | not tested | not tested | `test_path_117_docker_pause` |
| `docker port` | pass | not tested | not tested | not tested | `test_path_118_docker_port` |
| `docker ps` | pass | not tested | not tested | not tested | `test_path_119_docker_ps` |
| `docker pull` | pass | not tested | not tested | not tested | `test_path_120_docker_pull` |
| `docker push` | pass | not tested | not tested | not tested | `test_path_121_docker_push` |
| `docker rename` | pass | not tested | not tested | not tested | `test_path_122_docker_rename` |
| `docker restart` | pass | not tested | not tested | not tested | `test_path_123_docker_restart` |
| `docker rm` | pass | not tested | not tested | not tested | `test_path_124_docker_rm` |
| `docker rmi` | pass | not tested | not tested | not tested | `test_path_125_docker_rmi` |
| `docker run` | pass | not tested | pass 2/2 | pass | `test_path_126_docker_run` |
| `docker save` | pass | not tested | not tested | not tested | `test_path_127_docker_save` |
| `docker search` | pass | not tested | not tested | not tested | `test_path_128_docker_search` |
| `docker start` | pass | not tested | not tested | not tested | `test_path_129_docker_start` |
| `docker stats` | pass | not tested | not tested | not tested | `test_path_130_docker_stats` |
| `docker stop` | pass | not tested | not tested | not tested | `test_path_131_docker_stop` |
| `docker system` | pass | not tested | not tested | not tested | `test_path_132_docker_system` |
| `docker system df` | pass | not tested | not tested | not tested | `test_path_133_docker_system_df` |
| `docker system events` | pass | not tested | not tested | not tested | `test_path_134_docker_system_events` |
| `docker system info` | pass | not tested | not tested | not tested | `test_path_135_docker_system_info` |
| `docker system prune` | pass | not tested | not tested | not tested | `test_path_136_docker_system_prune` |
| `docker tag` | pass | not tested | not tested | not tested | `test_path_137_docker_tag` |
| `docker top` | pass | not tested | not tested | not tested | `test_path_138_docker_top` |
| `docker unpause` | pass | not tested | not tested | not tested | `test_path_139_docker_unpause` |
| `docker update` | pass | not tested | not tested | not tested | `test_path_140_docker_update` |
| `docker version` | pass | not tested | not tested | not tested | `test_path_141_docker_version` |
| `docker volume` | pass | not tested | not tested | not tested | `test_path_142_docker_volume` |
| `docker volume create` | pass | not tested | not tested | not tested | `test_path_143_docker_volume_create` |
| `docker volume inspect` | pass | not tested | not tested | not tested | `test_path_144_docker_volume_inspect` |
| `docker volume ls` | pass | not tested | not tested | not tested | `test_path_145_docker_volume_ls` |
| `docker volume prune` | pass | not tested | not tested | not tested | `test_path_146_docker_volume_prune` |
| `docker volume rm` | pass | not tested | not tested | not tested | `test_path_147_docker_volume_rm` |
| `docker volume update` | pass | not tested | not tested | not tested | `test_path_148_docker_volume_update` |
| `docker wait` | pass | not tested | not tested | not tested | `test_path_149_docker_wait` |
| `dotnet` | pass | not tested | not tested | not tested | `test_path_150_dotnet` |
| `dotnet build` | pass | pass 1/15 | pass 2/2 | not tested | `test_path_151_dotnet_build` |
| `dotnet publish` | pass | pass 1/16 | pass 2/2 | not tested | `test_path_152_dotnet_publish` |
| `dotnet restore` | pass | pass 1/14 | pass 2/2 | not tested | `test_path_153_dotnet_restore` |
| `dotnet run` | pass | pass 1/13 | pass 2/2 | not tested | `test_path_154_dotnet_run` |
| `dotnet test` | pass | pass 1/18 | pass 2/2 | not tested | `test_path_155_dotnet_test` |
| `du` | pass | not tested | pass 1/1 | not tested | `test_path_156_du` |
| `esptool` | pass | not tested | not tested | not tested | `test_path_157_esptool` |
| `esptool write-flash` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_158_esptool_write_flash` |
| `esptool.py` | pass | not tested | not tested | not tested | `test_path_159_esptool_py` |
| `esptool.py write-flash` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_160_esptool_py_write_flash` |
| `esptool.py write_flash` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_161_esptool_py_write_flash` |
| `fd` | pass | pass 1/19 | pass 1/1 | not tested | `test_path_162_fd` |
| `fdfind` | pass | pass 1/19 | pass 1/1 | not tested | `test_path_163_fdfind` |
| `ffmpeg` | pass | pass 2/16 | pass 2/2 | pass | `test_path_164_ffmpeg` |
| `ffprobe` | pass | not tested | pass 2/2 | not tested | `test_path_165_ffprobe` |
| `find` | pass | not tested | pass 1/1 | not tested | `test_path_166_find` |
| `fzf` | pass | pass 1/17 | pass 1/1 | not tested | `test_path_167_fzf` |
| `gcc` | pass | not tested | pass 2/2 | not tested | `test_path_168_gcc` |
| `gcloud` | pass | not tested | not tested | not tested | `test_path_169_gcloud` |
| `gcloud compute instances list` | pass | pass 1/12 | pass 2/2 | not tested | `test_path_170_gcloud_compute_instances_list` |
| `gcloud config list` | pass | pass 1/7 | pass 2/2 | not tested | `test_path_171_gcloud_config_list` |
| `gcloud storage ls` | pass | pass 1/15 | pass 2/2 | not tested | `test_path_172_gcloud_storage_ls` |
| `gh` | pass | not tested | not tested | not tested | `test_path_173_gh` |
| `gh issue` | pass | not tested | not tested | not tested | `test_path_174_gh_issue` |
| `gh issue list` | pass | not tested | pass 1/1 | pass | `test_path_175_gh_issue_list` |
| `gh issue view` | pass | not tested | pass 1/1 | not tested | `test_path_176_gh_issue_view` |
| `gh pr` | pass | not tested | not tested | not tested | `test_path_177_gh_pr` |
| `gh pr create` | pass | not tested | pass 1/1 | not tested | `test_path_178_gh_pr_create` |
| `gh pr list` | pass | not tested | pass 2/2 | not tested | `test_path_179_gh_pr_list` |
| `gh pr view` | pass | not tested | pass 1/1 | not tested | `test_path_180_gh_pr_view` |
| `gh repo` | pass | not tested | not tested | not tested | `test_path_181_gh_repo` |
| `gh repo clone` | pass | not tested | pass 2/2 | not tested | `test_path_182_gh_repo_clone` |
| `gh run` | pass | not tested | not tested | not tested | `test_path_183_gh_run` |
| `gh run list` | pass | not tested | pass 1/1 | not tested | `test_path_184_gh_run_list` |
| `gh run view` | pass | not tested | pass 1/1 | not tested | `test_path_185_gh_run_view` |
| `gh workflow` | pass | not tested | not tested | not tested | `test_path_186_gh_workflow` |
| `gh workflow list` | pass | not tested | pass 1/1 | not tested | `test_path_187_gh_workflow_list` |
| `gh workflow view` | pass | not tested | pass 1/1 | not tested | `test_path_188_gh_workflow_view` |
| `git` | pass | not tested | not tested | not tested | `test_path_189_git` |
| `git add` | pass | not tested | not tested | not tested | `test_path_190_git_add` |
| `git am` | pass | not tested | not tested | not tested | `test_path_191_git_am` |
| `git apply` | pass | not tested | not tested | not tested | `test_path_192_git_apply` |
| `git archive` | pass | not tested | not tested | not tested | `test_path_193_git_archive` |
| `git blame` | pass | not tested | not tested | not tested | `test_path_194_git_blame` |
| `git branch` | pass | not tested | not tested | not tested | `test_path_195_git_branch` |
| `git checkout` | pass | not tested | not tested | not tested | `test_path_196_git_checkout` |
| `git cherry` | pass | not tested | not tested | not tested | `test_path_197_git_cherry` |
| `git cherry-pick` | pass | not tested | not tested | not tested | `test_path_198_git_cherry_pick` |
| `git clean` | pass | not tested | not tested | not tested | `test_path_199_git_clean` |
| `git clone` | pass | not tested | not tested | not tested | `test_path_200_git_clone` |
| `git commit` | pass | pass 3/9 | pass 2/2 | pass | `test_path_201_git_commit` |
| `git describe` | pass | not tested | not tested | not tested | `test_path_202_git_describe` |
| `git diff` | pass | not tested | pass 2/2 | not tested | `test_path_203_git_diff` |
| `git fetch` | pass | not tested | pass 1/1 | not tested | `test_path_204_git_fetch` |
| `git format-patch` | pass | not tested | not tested | not tested | `test_path_205_git_format_patch` |
| `git grep` | pass | not tested | not tested | not tested | `test_path_206_git_grep` |
| `git init` | pass | not tested | not tested | not tested | `test_path_207_git_init` |
| `git log` | pass | pass 2/10 | pass 2/2 | not tested | `test_path_208_git_log` |
| `git merge` | pass | not tested | not tested | not tested | `test_path_209_git_merge` |
| `git mv` | pass | not tested | not tested | not tested | `test_path_210_git_mv` |
| `git pull` | pass | not tested | not tested | not tested | `test_path_211_git_pull` |
| `git push` | pass | not tested | not tested | not tested | `test_path_212_git_push` |
| `git rebase` | pass | not tested | pass 1/1 | not tested | `test_path_213_git_rebase` |
| `git reflog` | pass | not tested | not tested | not tested | `test_path_214_git_reflog` |
| `git reset` | pass | not tested | not tested | not tested | `test_path_215_git_reset` |
| `git restore` | pass | not tested | not tested | not tested | `test_path_216_git_restore` |
| `git revert` | pass | not tested | not tested | not tested | `test_path_217_git_revert` |
| `git rm` | pass | not tested | not tested | not tested | `test_path_218_git_rm` |
| `git show` | pass | not tested | pass 2/2 | not tested | `test_path_219_git_show` |
| `git stash` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_220_git_stash` |
| `git stash apply` | pass | pass 1/3 | pass 2/2 | not tested | `test_path_221_git_stash_apply` |
| `git stash list` | pass | pass 1/9 | pass 2/2 | not tested | `test_path_222_git_stash_list` |
| `git stash pop` | pass | pass 1/3 | pass 2/2 | not tested | `test_path_223_git_stash_pop` |
| `git stash push` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_224_git_stash_push` |
| `git stash show` | pass | pass 1/9 | pass 2/2 | not tested | `test_path_225_git_stash_show` |
| `git status` | pass | not tested | pass 1/1 | not tested | `test_path_226_git_status` |
| `git switch` | pass | not tested | pass 1/1 | not tested | `test_path_227_git_switch` |
| `git tag` | pass | not tested | not tested | not tested | `test_path_228_git_tag` |
| `git worktree` | pass | pass 2/5 | pass 2/2 | not tested | `test_path_229_git_worktree` |
| `git worktree add` | pass | pass 1/11 | pass 2/2 | not tested | `test_path_230_git_worktree_add` |
| `git worktree list` | pass | pass 1/4 | pass 2/2 | not tested | `test_path_231_git_worktree_list` |
| `git worktree prune` | pass | pass 1/5 | pass 2/2 | not tested | `test_path_232_git_worktree_prune` |
| `git worktree remove` | pass | pass 1/2 | pass 2/2 | not tested | `test_path_233_git_worktree_remove` |
| `go` | pass | not tested | not tested | not tested | `test_path_234_go` |
| `go build` | pass | pass 1/10 | pass 2/2 | not tested | `test_path_235_go_build` |
| `go mod tidy` | pass | pass 1/6 | pass 1/2 | not tested | `test_path_236_go_mod_tidy` |
| `go run` | pass | pass 1/10 | pass 1/2 | not tested | `test_path_237_go_run` |
| `go test` | pass | pass 1/18 | pass 3/3 | not tested | `test_path_238_go_test` |
| `grep` | pass | pass 3/14 | not tested | pass | `test_path_239_grep` |
| `gzip` | pass | not tested | pass 1/1 | not tested | `test_path_240_gzip` |
| `head` | pass | not tested | pass 1/1 | not tested | `test_path_241_head` |
| `helm` | pass | not tested | not tested | not tested | `test_path_242_helm` |
| `helm install` | pass | not tested | pass 2/2 | not tested | `test_path_243_helm_install` |
| `helm upgrade` | pass | not tested | pass 1/1 | not tested | `test_path_244_helm_upgrade` |
| `ip` | pass | not tested | not tested | not tested | `test_path_245_ip` |
| `ip address` | pass | pass 1/8 | pass 0/1 | not tested | `test_path_246_ip_address` |
| `ip link` | pass | pass 1/7 | pass 0/1 | not tested | `test_path_247_ip_link` |
| `ip route` | pass | pass 1/9 | pass 0/1 | not tested | `test_path_248_ip_route` |
| `journalctl` | pass | pass 1/15 | pass 1/1 | not tested | `test_path_249_journalctl` |
| `jq` | pass | not tested | pass 2/2 | not tested | `test_path_250_jq` |
| `kubectl` | pass | not tested | not tested | not tested | `test_path_251_kubectl` |
| `kubectl apply` | pass | not tested | pass 1/1 | not tested | `test_path_252_kubectl_apply` |
| `kubectl config` | pass | not tested | not tested | not tested | `test_path_253_kubectl_config` |
| `kubectl config view` | pass | not tested | pass 2/2 | not tested | `test_path_254_kubectl_config_view` |
| `kubectl delete` | pass | not tested | pass 1/1 | not tested | `test_path_255_kubectl_delete` |
| `kubectl describe` | pass | not tested | pass 1/1 | not tested | `test_path_256_kubectl_describe` |
| `kubectl exec` | pass | not tested | pass 1/1 | pass | `test_path_257_kubectl_exec` |
| `kubectl get` | pass | not tested | pass 2/2 | not tested | `test_path_258_kubectl_get` |
| `kubectl logs` | pass | not tested | pass 1/1 | pass | `test_path_259_kubectl_logs` |
| `kubectl port-forward` | pass | not tested | pass 1/1 | not tested | `test_path_260_kubectl_port_forward` |
| `ls` | pass | pass 3/19 | not tested | pass | `test_path_261_ls` |
| `magick` | pass | not tested | pass 2/2 | not tested | `test_path_262_magick` |
| `mv` | pass | not tested | pass 1/1 | not tested | `test_path_263_mv` |
| `ninja` | pass | not tested | pass 2/2 | not tested | `test_path_264_ninja` |
| `npm` | pass | not tested | pass 0/2 | not tested | `test_path_265_npm` |
| `npm install` | pass | not tested | pass 2/2 | not tested | `test_path_266_npm_install` |
| `npm publish` | pass | not tested | not tested | not tested | `test_path_267_npm_publish` |
| `npm run` | pass | not tested | pass 2/2 | not tested | `test_path_268_npm_run` |
| `openssl` | pass | not tested | not tested | not tested | `test_path_269_openssl` |
| `openssl dgst` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_270_openssl_dgst` |
| `openssl s_client` | pass | pass 1/12 | pass 1/1 | not tested | `test_path_271_openssl_s_client` |
| `openssl x509` | pass | pass 1/11 | pass 1/1 | not tested | `test_path_272_openssl_x509` |
| `pio` | pass | not tested | not tested | not tested | `test_path_273_pio` |
| `pio device monitor` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_274_pio_device_monitor` |
| `pio run` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_275_pio_run` |
| `pip` | pass | not tested | pass 3/3 | not tested | `test_path_276_pip` |
| `pip download` | pass | not tested | pass 3/3 | not tested | `test_path_277_pip_download` |
| `pip install` | pass | not tested | pass 3/3 | not tested | `test_path_278_pip_install` |
| `pip list` | pass | not tested | pass 1/1 | not tested | `test_path_279_pip_list` |
| `pip uninstall` | pass | not tested | pass 1/1 | not tested | `test_path_280_pip_uninstall` |
| `pip3` | pass | not tested | not tested | not tested | `test_path_281_pip3` |
| `pip3 download` | pass | not tested | not tested | not tested | `test_path_282_pip3_download` |
| `pip3 install` | pass | not tested | pass 2/2 | not tested | `test_path_283_pip3_install` |
| `pip3 list` | pass | not tested | not tested | not tested | `test_path_284_pip3_list` |
| `pip3 uninstall` | pass | not tested | not tested | not tested | `test_path_285_pip3_uninstall` |
| `platformio` | pass | not tested | not tested | not tested | `test_path_286_platformio` |
| `platformio device monitor` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_287_platformio_device_monitor` |
| `platformio run` | pass | pass 1/17 | pass 2/2 | not tested | `test_path_288_platformio_run` |
| `pnpm` | pass | not tested | not tested | not tested | `test_path_289_pnpm` |
| `pnpm install` | pass | not tested | pass 2/2 | not tested | `test_path_290_pnpm_install` |
| `podman` | pass | not tested | not tested | not tested | `test_path_291_podman` |
| `podman build` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_292_podman_build` |
| `podman exec` | pass | pass 1/10 | pass 1/1 | not tested | `test_path_293_podman_exec` |
| `podman logs` | pass | pass 1/8 | pass 1/1 | not tested | `test_path_294_podman_logs` |
| `podman run` | pass | pass 1/16 | pass 1/1 | not tested | `test_path_295_podman_run` |
| `psql` | pass | pass 1/21 | pass 1/1 | not tested | `test_path_296_psql` |
| `pytest` | pass | pass 1/18 | pass 3/3 | not tested | `test_path_297_pytest` |
| `python -m pip` | pass | not tested | pass 1/1 | not tested | `test_path_298_python_m_pip` |
| `python -m pip download` | pass | not tested | pass 1/1 | not tested | `test_path_299_python_m_pip_download` |
| `python -m pip install` | pass | not tested | pass 1/1 | not tested | `test_path_300_python_m_pip_install` |
| `python -m pip list` | pass | not tested | pass 1/1 | not tested | `test_path_301_python_m_pip_list` |
| `python -m pip uninstall` | pass | not tested | pass 1/1 | not tested | `test_path_302_python_m_pip_uninstall` |
| `python -m pytest` | pass | not tested | pass 1/1 | not tested | `test_path_303_python_m_pytest` |
| `python3 -m pip` | pass | not tested | pass 1/1 | not tested | `test_path_304_python3_m_pip` |
| `python3 -m pip download` | pass | not tested | pass 1/1 | not tested | `test_path_305_python3_m_pip_download` |
| `python3 -m pip install` | pass | not tested | pass 1/1 | not tested | `test_path_306_python3_m_pip_install` |
| `python3 -m pip list` | pass | not tested | pass 1/1 | not tested | `test_path_307_python3_m_pip_list` |
| `python3 -m pip uninstall` | pass | not tested | pass 1/1 | not tested | `test_path_308_python3_m_pip_uninstall` |
| `python3 -m pytest` | pass | not tested | pass 1/1 | not tested | `test_path_309_python3_m_pytest` |
| `rclone` | pass | not tested | pass 2/2 | not tested | `test_path_310_rclone` |
| `rclone copy` | pass | not tested | pass 2/2 | not tested | `test_path_311_rclone_copy` |
| `rclone sync` | pass | not tested | pass 1/1 | not tested | `test_path_312_rclone_sync` |
| `restic` | pass | not tested | not tested | not tested | `test_path_313_restic` |
| `restic backup` | pass | not tested | pass 2/2 | not tested | `test_path_314_restic_backup` |
| `rg` | pass | not tested | pass 2/2 | not tested | `test_path_315_rg` |
| `rm` | pass | not tested | pass 1/1 | not tested | `test_path_316_rm` |
| `rsync` | pass | pass 9/29 | pass 2/2 | pass | `test_path_317_rsync` |
| `ruff` | pass | not tested | not tested | not tested | `test_path_318_ruff` |
| `ruff check` | pass | pass 1/16 | pass 2/2 | not tested | `test_path_319_ruff_check` |
| `ruff format` | pass | pass 1/14 | pass 2/2 | not tested | `test_path_320_ruff_format` |
| `scp` | pass | pass 1/15 | pass 1/1 | not tested | `test_path_321_scp` |
| `sed` | pass | not tested | pass 1/1 | pass | `test_path_322_sed` |
| `sftp` | pass | pass 1/17 | pass 1/1 | not tested | `test_path_323_sftp` |
| `sort` | pass | not tested | pass 1/1 | not tested | `test_path_324_sort` |
| `ss` | pass | pass 1/12 | pass 1/1 | not tested | `test_path_325_ss` |
| `ssh` | pass | pass 1/19 | pass 1/1 | not tested | `test_path_326_ssh` |
| `systemctl` | pass | not tested | not tested | not tested | `test_path_327_systemctl` |
| `systemctl list-units` | pass | pass 1/11 | pass 1/1 | not tested | `test_path_328_systemctl_list_units` |
| `systemctl show` | pass | pass 1/13 | pass 1/1 | not tested | `test_path_329_systemctl_show` |
| `systemctl status` | pass | pass 1/11 | pass 1/1 | not tested | `test_path_330_systemctl_status` |
| `tail` | pass | not tested | pass 1/1 | not tested | `test_path_331_tail` |
| `tar` | pass | pass 4/12 | not tested | pass | `test_path_332_tar` |
| `terraform` | pass | not tested | not tested | not tested | `test_path_333_terraform` |
| `terraform apply` | pass | not tested | pass 2/2 | not tested | `test_path_334_terraform_apply` |
| `terraform plan` | pass | not tested | pass 2/2 | pass | `test_path_335_terraform_plan` |
| `tofu` | pass | not tested | not tested | not tested | `test_path_336_tofu` |
| `tofu apply` | pass | not tested | pass 2/2 | not tested | `test_path_337_tofu_apply` |
| `tofu plan` | pass | not tested | pass 2/2 | not tested | `test_path_338_tofu_plan` |
| `uv` | pass | not tested | not tested | not tested | `test_path_339_uv` |
| `uv add` | pass | pass 1/12 | pass 2/2 | not tested | `test_path_340_uv_add` |
| `uv lock` | pass | pass 1/11 | pass 2/2 | not tested | `test_path_341_uv_lock` |
| `uv pip` | pass | not tested | not tested | not tested | `test_path_342_uv_pip` |
| `uv pip install` | pass | not tested | pass 2/2 | not tested | `test_path_343_uv_pip_install` |
| `uv run` | pass | not tested | pass 2/2 | not tested | `test_path_344_uv_run` |
| `uv sync` | pass | pass 1/12 | pass 2/2 | not tested | `test_path_345_uv_sync` |
| `uv tool install` | pass | pass 1/10 | pass 2/2 | not tested | `test_path_346_uv_tool_install` |
| `uv venv` | pass | pass 1/11 | pass 2/2 | not tested | `test_path_347_uv_venv` |
| `vlc` | pass | not tested | pass 2/2 | not tested | `test_path_348_vlc` |
| `wget` | pass | not tested | pass 2/2 | not tested | `test_path_349_wget` |
| `xz` | pass | not tested | pass 2/2 | not tested | `test_path_350_xz` |
| `yarn` | pass | not tested | not tested | not tested | `test_path_351_yarn` |
| `yarn add` | pass | not tested | pass 3/3 | not tested | `test_path_352_yarn_add` |
| `yarn install` | pass | not tested | pass 3/3 | not tested | `test_path_353_yarn_install` |
| `yarn run` | pass | not tested | pass 3/3 | not tested | `test_path_354_yarn_run` |
| `yq` | pass | not tested | not tested | not tested | `test_path_355_yq` |
| `yq eval` | pass | pass 1/15 | pass 1/1 | not tested | `test_path_356_yq_eval` |
| `yt-dlp` | pass | not tested | pass 2/2 | not tested | `test_path_357_yt_dlp` |

## Suite module totals

| Module | Pass | Fail | Skip |
|---|---:|---:|---:|
| `test_adversarial` | 25 | 0 | 0 |
| `test_ansible_probe_locale` | 1 | 0 | 0 |
| `test_argument_syntax` | 13 | 0 | 0 |
| `test_bash_pty` | 28 | 0 | 1 |
| `test_bulk_scan` | 18 | 0 | 0 |
| `test_cloud_captured` | 2 | 0 | 0 |
| `test_collection` | 17 | 0 | 0 |
| `test_context_diagnostics` | 13 | 0 | 0 |
| `test_core` | 19 | 0 | 0 |
| `test_discovery` | 25 | 0 | 0 |
| `test_display_regression_terminal` | 1 | 0 | 0 |
| `test_documentation_links` | 13 | 0 | 0 |
| `test_documentation_preservation` | 24 | 0 | 0 |
| `test_drivers` | 18 | 0 | 0 |
| `test_expansion_development` | 17 | 0 | 0 |
| `test_expansion_systems` | 10 | 0 | 0 |
| `test_expansion_terminal` | 8 | 0 | 0 |
| `test_functional_matrix` | 35 | 0 | 1 |
| `test_guided_merge` | 12 | 0 | 0 |
| `test_installation` | 21 | 0 | 0 |
| `test_invocation_expansion` | 14 | 0 | 0 |
| `test_live_harness` | 13 | 0 | 0 |
| `test_manual_import` | 14 | 0 | 0 |
| `test_module_discovery` | 23 | 0 | 0 |
| `test_module_freshness` | 10 | 0 | 0 |
| `test_native_numerical_terminal` | 8 | 0 | 0 |
| `test_native_posix` | 6 | 0 | 0 |
| `test_numerical_authoring` | 35 | 0 | 0 |
| `test_numerical_coverage` | 23 | 0 | 0 |
| `test_numerical_debt_resolution` | 13 | 0 | 0 |
| `test_numerical_diagnostics` | 9 | 0 | 0 |
| `test_numerical_integration` | 12 | 0 | 0 |
| `test_numerical_inventory` | 16 | 0 | 0 |
| `test_numerical_migration` | 11 | 0 | 0 |
| `test_numerical_presentation` | 37 | 0 | 0 |
| `test_optional_integer_values` | 5 | 0 | 0 |
| `test_parser_association` | 31 | 0 | 0 |
| `test_presentation_descriptions` | 6 | 0 | 0 |
| `test_program_corpus` | 16 | 0 | 0 |
| `test_recommendation_review` | 13 | 0 | 0 |
| `test_regression_inventory` | 358 | 0 | 0 |
| `test_release` | 10 | 0 | 0 |
| `test_release_snapshot` | 22 | 0 | 0 |
| `test_release_terminal` | 3 | 0 | 0 |
| `test_release_update` | 48 | 0 | 0 |
| `test_repository_config` | 9 | 0 | 0 |
| `test_review` | 20 | 0 | 0 |
| `test_review_fixes` | 6 | 0 | 0 |
| `test_review_forms` | 20 | 0 | 0 |
| `test_review_terminal` | 3 | 0 | 0 |
| `test_review_workflows` | 8 | 0 | 0 |
| `test_runtime_followup` | 6 | 0 | 0 |
| `test_subcommands` | 17 | 0 | 0 |
| `test_syntax_collection_review` | 7 | 0 | 0 |
| `test_syntax_terminal` | 7 | 0 | 0 |
| `test_system_dependency_followup` | 3 | 0 | 0 |
| `test_terminal_sanitization` | 9 | 0 | 0 |
| `test_terminal_screen` | 7 | 0 | 0 |
| `test_update` | 26 | 0 | 0 |
| `test_update_review` | 33 | 0 | 0 |
| `test_value_semantics` | 32 | 0 | 0 |
| `test_workflow_baseline` | 13 | 0 | 0 |
| `test_workflow_review` | 8 | 0 | 0 |
| `test_workflow_review_terminal` | 2 | 0 | 0 |
| `test_workflow_terminal` | 4 | 0 | 0 |
