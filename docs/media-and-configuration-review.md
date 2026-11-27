# Documentation visuals and repository configuration review

## November 26, 2026 candidate checkout

The current source gallery includes the APT install and Bash read menus alongside the refreshed rsync, ls and guided-review views. The recorder used the working checkout with `VERSION` set to `0.5.0-alpha`. The local candidate package checks are pending. [Checkout capture evidence](assets/README.md#capture-evidence) · [Release checklist](../ROADMAP.md#remaining-work)

## November 25, 2026 local build

The gallery at that revision showed the three-level browser from the November 25 local v0.4.0-alpha build. The capture ran the unpacked runtime on Ubuntu 26.04.1 with Bash 5.3.9 and Python 3.14.4. All 160 fingerprinted runtime inputs matched the archive manifest and the working tree. The archive predates the resulting documentation edits. [November 25 archive and capture evidence](assets/README.md#november-25-historical-capture)

The refreshed animation follows the same rsync option through Simple, Detailed and Expanded before insertion. All 21 frames and their durations matched the recorded states across the 40.5-second loop. An independent tmux 3.6 replay matched all 21 screens at 100×24. The final rsync and ls cursor offsets were 156 and 60. The execution guards stayed silent, Escape preserved the pending rsync command, and cancelling the guided edit preserved the collection bytes. [Demonstration sequence](assets/README.md#demonstration-sequence)

The repository refresh aligned Git, EditorConfig and source-package handling for captured text, compressed fixtures, benchmark patches and temporary test directories. The primary link check and bounded retry now include both Markdown files under `.github/`. Issue forms and contribution guidance ask for the affected menu interaction, detail level and verification scope. On the host, the repository-configuration, documentation-link and release-snapshot modules passed 46 tests in 16.171 seconds. [Refresh record](local-build-refresh.md) · [Repository configuration](development.md#repository-configuration)

## v0.4.0-alpha candidate

The earlier performance candidate bundled six public media assets from its own source inputs. Its review checked binary image attributes, fixture padding, exclusions for generated reports, three local Ubuntu/Python targets, CI report uploads and weekly dependency groups. Release artifacts and the later three-level menu have distinct provenance. [Candidate verification](release-candidate.md) · [Building from source](releases.md#build-from-source)

## Historical review of October 2026

On October 26 the working tree based on `8eb3f87` gained four refreshed terminal assets, two corrected diagrams and aligned exclusions for three private terminal-session directory prefixes. The following sections describe that review and its evidence. The [current asset guide](assets/README.md) describes the November replacements.

## Inventory and evidence boundaries

The October inventory found six local media assets, seven Mermaid diagrams and one remote workflow badge. Capture used Ubuntu 24.04 WSL, Python 3.12.3, Bash 5.2.21, tmux 3.4, Pillow 11.3.0, pyte 0.8.2 and wcwidth 0.9.2. Disposable homes, offline networking, discovery disabled and inert command buffers bounded the sessions.

The 100×24 terminal images measured 1148×702 pixels and the guided-review image measured 1148×558. The GIF contained 19 frames, lasted 35.7 seconds and occupied 757,609 bytes. Its holds were chosen for readability. Capture logs, screen cells, replay results, frames, hashes and browser inspection were recorded under the ignored directory `tests/reports/docs-media-2026-10-26/`.

## Visual coverage

| October visual | Outcome |
| --- | --- |
| Animation, browser, scrolled ls and numerical-guidance images | Regenerated from PTY output. Each of the 19 decoded GIF states matched its independent tmux replay. |
| Pending command and guided review | Regeneration reproduced both images byte for byte. The recorder checked Readline state, cancellation and unchanged collection JSON. |
| Seven Mermaid diagrams | Corrected discovery to show sanitization and cache reuse, and linked collection recovery back to restored profiles and routes. The remaining five covered interaction, architecture, installation, update review and historical Step 8 verification. |
| Browser preview and badge | Offline Edge rendered nine documents and all seven diagrams. Desktop and mobile viewports measured 1200 and 390 pixels. Six samples across 37 seconds confirmed playback into the next loop. The hosted badge could not load in the offline preview. |

## Git and GitHub configuration coverage

October's review covered 12 tracked inputs. Git attributes and EditorConfig described text and binary handling. Git ignores and Lychee exclusions tracked private evidence directories. The review checked CI and Dependabot YAML, both issue forms, issue routing, the PR template, contribution guidance and the optional media requirements. The CI review at that time covered Python 3.10 and 3.12 on Ubuntu 24.04 and 14-day retention for scoped logs.

Git ignore, link scanning and source packaging gained matching exclusions for `cli-help-description-screen-*`, `cli-help-sanitized-screen-*` and `cli-help-replay-*`. Tests verified that similarly named public guides remained eligible for inclusion. Supporting checks covered the release builder, repository configuration, release snapshot, bounded link retry and shell test entry point. [Source selector](../scripts/build_release.py) · [Repository policy tests](../tests/test_repository_config.py) · [Link retry](../scripts/retry_documentation_links.py)

## Verification results

The October review recorded 123 focused Linux/WSL passes with zero failures, errors or skips. Four additional capture-assertion checks passed, bringing the two selections to 127.

| October selection | Passed |
| --- | ---: |
| Repository configuration, link retry and release source boundaries | 9 + 13 + 10 |
| Parser association, opening-description presentation and numerical presentation | 31 + 6 + 37 |
| Terminal sanitization, real Bash/tmux behavior and captured descriptions across seven families | 9 + 7 + 1 |
| Capture assertions | 4 |

All 11 recorded configuration checks passed. Offline Lychee inspected 44 Markdown files and counted 666 references (261 unique), with 574 accepted, 92 excluded and zero errors. The review also checked five YAML files, actionlint, shell syntax, whitespace and strict numerical coverage. The October application regression run has its own test selection and results. [Regression review](regression-review.md)

## Findings and remaining gaps

At a 390-pixel document width, reading terminal text required zoom or a full-size view. Local Edge rendering did not establish GitHub-hosted rendering, badge status, live issue-form behavior or a hosted CI outcome. The captures established local Bash interaction on the reported versions. Other terminals, external URL reachability, live discovery, target workload execution and publication require separate evidence. [Current local verification scope](local-build-refresh.md)
