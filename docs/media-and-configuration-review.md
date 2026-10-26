# Documentation visuals and repository configuration review

Reviewed on 2026-10-26 against the working tree based on `8eb3f87`, including
the existing parser and presentation work. Four terminal assets were refreshed,
two workflow diagrams were corrected, and temporary terminal-evidence exclusions
were aligned across Git, documentation scanning, and release source selection.
Application behavior was not changed by this documentation/configuration review.

[Documentation index](README.md) · [Capture and regeneration guide](assets/README.md)

## Inventory and evidence boundaries

The inventory combined tracked-file enumeration with Markdown/HTML media and
diagram-reference searches, asset-directory inspection, generation-script review,
and source tracing. It found six local media assets, seven Mermaid diagrams, and
one remote workflow badge. No additional tracked chart datasets, SVGs, videos,
PDF illustrations, Graphviz/PlantUML sources, or nested Git policy files were
found. Asset links, alternative text, captions, terminal annotations, labels,
dimensions, durations, and source qualifications were included in the review.

Captures used Ubuntu 24.04 under WSL, Python 3.12.3, Bash 5.2.21, tmux 3.4,
and the existing optional media environment: Pillow 11.3.0, pyte 0.8.2, and
wcwidth 0.9.2. Actual Bash/curses sessions used isolated homes, static profiles,
disabled discovery, inert command buffers, and an offline network namespace.
No dependency was installed. The recorder verified buffers and character cursors,
absence of target-execution markers, cancellation preservation, and unchanged
guided-review collection bytes. The review edit was cancelled without saving.

Public PNGs and the GIF render actual PTY output with the existing capture tool;
title bars and captions are annotations. Source and asset SHA-256 hashes are
recorded in local capture evidence. Full PNGs, all 19 decoded GIF states, and
browser playback were inspected. Independent tmux replay matched all 19 recorded
rsync/ls screens. Offline Edge rendered the nine original documents containing visual
references and all seven Mermaid diagrams. README checks used 1200-pixel and
390-pixel viewports: local embeds loaded, diagrams had no parse errors, and the
page had no horizontal overflow. Six browser playback samples over 37 seconds
showed distinct frames, including progression into the next loop.

The 100×24 terminal images are 1148×702 pixels; the guided-review viewport is
1148×558. The GIF has 19 frames, a 35.7-second loop, and a size of 757,609 bytes.
Holds are presentation timing, not performance measurements. Desktop text is
readable; at phone width, terminal text requires opening the full-size asset or
zooming. Static alternatives and surrounding text retain the workflow and its
qualifications. A full-size numerical-view link was added for this purpose.

Detailed local evidence is retained under `tests/reports/docs-media-2026-10-26/`:
`capture/validation.json`, `capture/scenes.json`, `capture/tmux-replay.json`,
`gif-check.json`, `render/rendered.json`, `render/playback.json`, screenshots,
`tests.json`, `tests.log`, `capture-assertions.log`, `config.json`, `links.log`,
and `actionlint.log`. These ignored files are local evidence, not public assets.
Raw recordings may contain interpreter or temporary paths and remain private.

## Visual coverage

Every discovered visual has a disposition below. “Verified unchanged” means the
listed local checks supported retaining it; it does not establish remote service
status or compatibility with every installed target version.

| Visual and documentation references | Represented behavior and source | Disposition and generation | Verification evidence |
| --- | --- | --- | --- |
| [Option insertion GIF](assets/option-insertion.gif); root README and asset guide | Category/focus navigation, scroll, scoped value search, literal insertion, reopen/cancel; [Bash adapter](../bash/interactive-help.bash), [UI](../cli_help/ui.py), [presentation](../cli_help/presentation.py), bundled rsync/ls profiles | **Updated** using [capture_readme_media.py](../tools/capture_readme_media.py); refreshed aligned option rows | 19 decoded states inspected; complete playback progression; all 19 states match tmux; exact unexecuted buffers/cursors |
| [Help browser](assets/help-browser.png); README static alternative and asset guide | Unfiltered rsync categories, aligned declarations/descriptions, selected details; `draw`, `option_row`, `option_text` | **Updated** from actual PTY output | Full-size inspection; matches GIF browser state and independent replay; readable explicit pane boundaries |
| [Scrolled ls browser](assets/ls-browser.png); README static alternative and asset guide | Option 12/12, scrolled option list and complete required-argument details; `Browser`, `draw`, `option_text` | **Updated** from actual PTY output | Full-size inspection; required declaration and source remain accessible; scrolled details intentionally start mid-paragraph |
| [Numerical guidance](assets/numerical-guidance.png); README and asset guide | `--bwlimit=`, bare 1024 bytes/second, rsync 3.4.1 applicability, evidence and special values; `value_text`, `option_text`, rsync profile | **Updated** from actual PTY output | Desktop/mobile context inspected; required scale/scope assertions pass; details retain qualifications while rows truncate explicitly |
| [Assembled command](assets/option-inserted.png); README static alternative and asset guide | Valued flags, quoted paths, cancellation preserving the pending line | **Verified unchanged**; fresh regeneration was byte-identical | Full-size inspection; exact Readline buffer and cursor, reopen/cancel preservation, no execution marker; visual wrapping is not a buffer newline |
| [Guided review](assets/guided-review.png); [review guide](review.md) and asset guide | Option selection and field editing in an illustrative collection; [review](../cli_help/review.py), [forms](../cli_help/review_forms.py) | **Verified unchanged**; fresh regeneration was byte-identical | Full-size and rendered-guide inspection; partial edit cancelled; original collection JSON unchanged |
| [README interaction diagram](../README.md#using-the-browser) | Pending command → browse → insert/cancel → editing → separate shell Enter; Bash adapter and `main.choose_option` | **Verified unchanged**; inline Mermaid | Source trace, terminal buffer tests, rendered diagram inspection; execution is a separate shell action and was not demonstrated |
| [Development architecture diagram](development.md) | Context validation, static profiles/drivers, bounded discovery, shared metadata display/search, buffer edit/return | **Verified unchanged**; inline Mermaid | Current module responsibilities checked; rendering inspected; optional discovery is separate from offline capture evidence |
| [Discovery diagram](discovery-and-safety.md) | Static precedence, fresh matching cache, man/auto/off, sanitization, association, usable root options | **Updated**; inline Mermaid | `discover`, `read_cache`, `clean_output`, `parse_help_document`, `associate_document` traced; diagram adds complete-sequence stripping and clarifies cache reuse; parser/sanitizer tests pass |
| [Installation/update diagram](installation.md) | Validate, stage, recheck, back up, switch, inspect conflicts | **Verified unchanged**; inline Mermaid | [installation.py](../scripts/installation.py) ownership and transaction flow inspected; diagram renders; no active installation changed |
| [Collection workflow diagram](README.md#help-collection-workflows) | Manual import/scan, profiles/drivers, review/preview, inspection and explicit recovery | **Updated**; inline Mermaid | `main` recovery dispatch and `collection.restore_review_backup` inspected; recovery arrow now returns to restored profiles/routes instead of launching review |
| [Update-review diagram](update-review.md) | Compare, queue choices, confirm/recheck, back up, switch, record fingerprints | **Verified unchanged**; inline Mermaid | `update_review.ReviewSession.save` flow inspected; rendering inspected; no update or publication performed |
| [Step 8 verification diagram](numerical-inventory/step8-verification.md) | Dated integration-test pipeline including fake-window preview and literal insertion calculation | **Historical**; retained inline Mermaid | Historical evidence labels retained; diagram renders; model preview is not relabeled as native terminal evidence |
| [README workflow badge](../README.md) | Hosted Linux/documentation workflow state | **Blocked for live status verification**; reference retained unchanged | Badge and destination match the existing workflow; remote requests intentionally blocked in preview. The resulting missing remote image is expected in offline evidence. A current GitHub response is needed to verify live badge/status rendering. |

The [capture generator](../tools/capture_readme_media.py) is **verified unchanged**:
its PTY capture, alternate-screen/scroll handling, pane-scoped assertions,
source fingerprints, and separate evidence destinations remain appropriate.
Four synthetic capture-assertion tests passed. No fabricated screenshot,
image-generation output, new dependency, or application redesign was introduced.

Historical release archives and dated verification documents were retained.
The current alpha version string does not imply that downloaded release packages
contain these refreshed media or the current working-tree behavior.

## Git and GitHub configuration coverage

All 12 tracked configuration/policy inputs identified in the requested inventory
are listed below. No nested ignore/attribute files, SECURITY, CODEOWNERS,
CODE_OF_CONDUCT, or LICENSE file was found; no policy was invented to fill those
absences. Runtime profile/driver JSON files are application data, not GitHub
configuration; their relevant media behavior is covered above.

| File | Disposition and rationale | Validation |
| --- | --- | --- |
| [.gitignore](../.gitignore) | **Updated**: exclude `cli-help-description-screen-*`, `cli-help-sanitized-screen-*`, and `cli-help-replay-*` directories at any depth | Actual `git check-ignore --no-index` tests for private sessions and maintained media/fixtures; no tracked file matches current ignore rules |
| [.gitattributes](../.gitattributes) | **Verified unchanged**: UTF-8 source/recording text remains LF; PNG/GIF/native/compressed artifacts remain binary | `git check-attr` verifies binary/text/diff/merge and text/eol behavior; no renormalization |
| [.editorconfig](../.editorconfig) | **Verified unchanged**: LF and indentation rules preserve meaningful fixture/Markdown spaces and exclude binary/generated bytes | Syntax and effective policy inspection; no blanket formatting |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | **Verified unchanged**: Python 3.10/3.12 on Ubuntu 24.04, existing policy/test/package/link gates, scoped evidence uploads | actionlint passes; YAML unique-key check; SHA-pinned actions, read-only permissions, disabled checkout credentials, triggers/concurrency, 14-day retention and named upload paths checked |
| [.github/dependabot.yml](../.github/dependabot.yml) | **Verified unchanged**: weekly action and optional media-dependency updates retain minor/patch grouping | YAML validation; `/` action scope and `/tools` pip requirements location checked |
| [Bug report form](../.github/ISSUE_TEMPLATE/bug_report.yml) | **Verified unchanged**: already includes documentation/media/configuration, environment, observed behavior and privacy fields | YAML/unique field IDs/type checks; field wording reviewed |
| [Feature request form](../.github/ISSUE_TEMPLATE/feature_request.yml) | **Verified unchanged**: intended workflow, compatibility and uncertainty remain explicit | YAML/unique field IDs/type checks; field wording reviewed |
| [Issue configuration](../.github/ISSUE_TEMPLATE/config.yml) | **Verified unchanged**: free-form reports and documentation destination remain appropriate | YAML validation and destination-path review; hosted form not exercised |
| [Pull-request template](../.github/pull_request_template.md) | **Verified unchanged**: already requires media provenance, rendered/encoded inspection, non-execution evidence and local/hosted distinction | Content and local references reviewed |
| [Contribution guide](../.github/CONTRIBUTING.md) | **Updated**: document complete playback/narrow-viewport review, visual inventory, and synchronization of temporary-folder policies | Local links; stated commands match maintained checks |
| [lychee.toml](../lychee.toml) | **Updated**: add the same three private session prefixes; preserve strict links, GNU throttling and existing cache policy | TOML parsing; positive/negative exclusion probes; offline links and retry-controller tests |
| [tools/requirements-media.txt](../tools/requirements-media.txt) | **Verified unchanged**: optional pinned capture dependencies match the successful capture environment | Recorded installed versions and successful regeneration; no version upgrades |

Supporting verification and packaging owners were also reviewed:

| File | Disposition and rationale | Validation |
| --- | --- | --- |
| [scripts/build_release.py](../scripts/build_release.py) | **Updated**: align the three private session-prefix exclusions with Git/link scanning | Actual source enumeration on disposable specimens; source-boundary tests; maintained media retained |
| [tests/test_repository_config.py](../tests/test_repository_config.py) | **Updated**: cover new private prefixes, all maintained media names, public similarly named guides, and PNG binary attributes | Nine tests pass using disposable Git repositories |
| [tests/test_release_snapshot.py](../tests/test_release_snapshot.py) | **Updated**: add the three private directory forms to existing enumeration regression specimens | Ten release-inventory tests pass; no active install/update involved |
| [scripts/retry_documentation_links.py](../scripts/retry_documentation_links.py) | **Verified unchanged**: bounded retry and strict final failure gate remain appropriate | Thirteen offline tests with controlled responses/processes |
| [tests/run.sh](../tests/run.sh) | **Verified unchanged**: remains the complete Linux suite entry point referenced by CI/contribution guidance | Shell syntax checked; this documentation task uses the focused selection below rather than claiming a new complete-suite run |

The exclusion changes are directory-specific. A maintained guide named
`docs/cli-help-description-screen.md` remains eligible for tracking. Ignore rules
do not remove already-tracked files; the tracked-ignore audit found none. No file
was untracked, no historical artifact was removed, and no global Git settings or
remote settings were changed.

## Verification results

Fresh focused Linux/WSL run: **123 tests passed, zero failures, zero errors,
zero skips**. Four independent synthetic capture-assertion tests also passed:
**127 tests total** across these two selections.

| Suite | Passed |
| --- | ---: |
| Repository configuration | 9 |
| Documentation retry/failure gate | 13 |
| Release source inventory and unsafe-source boundaries | 10 |
| Parser association and description preservation | 31 |
| Opening-description presentation | 6 |
| Numerical presentation, layout, search and preview | 37 |
| Terminal sanitization, cache and rendered controls | 9 |
| Actual Bash/tmux layout, insertion, cancellation, scrolling and resize | 7 |
| Captured-description real-terminal test across seven command families | 1 |
| Capture assertion checks | 4 |

The terminal selection covers bundled rsync, ls, grep and tar, plus captured Git,
Docker, curl, Terraform, kubectl, FFmpeg and AWS descriptions. It checks narrow,
standard, wide and below-minimum sizes, shrink/grow, Unicode and midline cursor
behavior. Pure presentation checks cover warning/scope preservation, optional
guidance, empty results and preview behavior. Captured help is parsed as data;
the corresponding target executables are not run.

Additional gates cover actionlint, five YAML files, TOML, EditorConfig, workflow
policy, effective ignore/attribute behavior, source selection, shell syntax,
local documentation links/fragments, and whitespace. External links and the
remote badge are excluded from the offline link run. No hosted GitHub Actions
execution is claimed. The earlier [comprehensive regression review](regression-review.md)
remains dated evidence and is not counted again in this task's totals.

Final configuration validation passed all 11 recorded checks. Offline Lychee
checked 44 Markdown documents: 666 references (261 unique), 574 accepted,
92 excluded, and zero errors. actionlint, `bash -n tests/run.sh`,
`git diff --check`, numerical inventory reconciliation, and strict numerical
coverage all exited successfully. No unresolved check failure or test skip
remains in this focused selection. Excluded external references are unverified,
not passing external-link results.

Files changed by this task are the root README, documentation index, asset guide,
discovery diagram guide, this coverage report, four media assets, `.gitignore`,
`lychee.toml`, the contribution guide, the release source selector, and the two
repository/release policy test files listed above. The media-generation script
and dependency pins were retained unchanged. Earlier parser, regression-report,
inventory and test changes in the working tree were preserved.

## Findings and remaining gaps

- No new application defect was established by the captures or focused checks.
  The stale media, two diagram inaccuracies, and inconsistent temporary-folder
  policies were corrected within this task. Existing unrelated work was retained.
- At 390-pixel document width, terminal text is too small for detailed reading.
  Full-size links/static alternatives and adjacent explanations are retained;
  a separate mobile documentation design was not introduced.
- External URL reachability, live badge rendering, exact GitHub-hosted Markdown
  appearance, hosted issue forms and CI jobs were not verified. Close these gaps
  with read-only GitHub rendering/link checks and a separately authorized hosted
  workflow run. Local Edge/Mermaid rendering is an approximation of GitHub.
- Native macOS/Windows terminals, other terminal emulators, every installed
  target version, live help discovery, and real operational command execution
  remain outside this capture's evidence. Use isolated native sessions and
  explicit target-version documentation checks if those claims are required.
- Installation/update diagrams were checked against source; no new installation
  demonstration was necessary. Existing release artifacts were not rebuilt or
  relabeled. Future release preparation must build and verify a fresh candidate
  after all intended inputs are finalized.
- Raw evidence and local preview helpers remain ignored. The maintained capture
  script and regeneration guide provide the repeatable public capture workflow.

No commit, push, publication, deployment, history rewrite, release-tag change,
authentication change, secret update, or remote repository-setting change was
performed.
