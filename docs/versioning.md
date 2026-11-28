# Version numbering and planned releases

The current checkout version comes from [VERSION](../VERSION). During alpha development, the minor number normally identifies the development plan and the patch number advances as steps of that plan ship. A plan groups related targets around a distinct user-visible goal. A step delivers a verifiable improvement toward a target. A roadmap task can span several releases or consist entirely of maintenance.

| What ships | Version change | Example |
| --- | --- | --- |
| The next ordinary step within the current plan, including a focused fix such as restoring the cursor after cancellation | Increase the patch number by one for the release. | `v0.3.1-alpha` → `v0.3.2-alpha` |
| The first qualifying program change for the next distinct plan | Increase the minor number by one and reset the patch to zero. The first shipped step takes `.0` and the next separately shipped ordinary step takes `.1`. | `v0.3.4-alpha` → `v0.4.0-alpha` → `v0.4.1-alpha` |
| A step or batch within the current plan delivers a substantially larger outcome than its other targets, such as enabling a previously unsupported interactive workflow across command families | Start the next minor series early. Continue the plan’s ordinary steps from the new series. | `v0.3.2-alpha` → `v0.4.0-alpha`, followed by `v0.4.1-alpha` for an ordinary fix |
| Any qualifying program change after patch 9 | Carry into the next minor series with patch zero. | `v0.4.9-alpha` → `v0.5.0-alpha` |

For a plan transition, record the outgoing and incoming goals, what users gain from the first shipped step, and why the new goal goes beyond an ordinary target in the current plan. Drafting, renaming or subdividing a plan carries no increment. For an early minor bump within a plan, describe what users could do before and after and why the shipped difference exceeds a typical target. For a performance milestone, give measurements across the affected workflows. A faster first frame in one large menu fits a patch. Making previously impractical menus usable throughout opening, searching and navigation could justify a minor bump.

The patch-9 carry applies even when the same plan continues. If several rules call for a minor bump in the same release, advance the minor number once.

The navigation candidate uses `0.6.0-alpha` in VERSION and `v0.6.0-alpha` for its artifacts. The preceding 0.5 release expanded Ubuntu command coverage. The 0.6 release adds a distinct way to navigate and read that help across terminal sizes, including a three-screen workflow, a keyboard scrolling preview and preservation of the reading position during resize. The APT guidance and scenario gallery ship with the same batch. [Five recorded workflows](menu-demo-storyboards.md) · [Resize verification](terminal-resize-review.md#phase-4--verify-the-accepted-changes-together)

## Proposed targets

A proposed release must change the working program. Eligible changes include a Bash keybinding fix, an improvement to menu performance, and corrections to the option descriptions or literal spellings that the menu displays or inserts. README edits, audit reports, demonstration media, CI changes and test-runner improvements are maintenance. They can accompany a program change and carry no version increment on their own.

The `0.3` series expanded the command help users can find and insert. The first `0.4` batch improves how users open and read that help. It combines per-open reuse of shared value formatting with selectable levels of explanation. The performance-only candidate remained unpublished, so both changes share the first number in the new series, `v0.4.0-alpha`. Skipping unchanged idle frames and shortening serial validation deliver the next step together under `v0.4.1-alpha`. [Verified 0.4 patch](../CHANGELOG.md#version-041---alpha) · [Menu performance plan](ffmpeg-menu-performance-plan.md)

The maintainer selected v0.5.0-alpha for a distinct goal. The 0.4 series improved menu reading and responsiveness. The new series gives Ubuntu users edition-aware package and builtin help and a reference for commands on minimal images. Future performance targets receive numbers in shipping order if their measurements justify inclusion. [Roadmap tasks and dependencies](../ROADMAP.md#remaining-work)

| Proposed release | Change to the working program | Evidence for inclusion |
| --- | --- | --- |
| v0.6.0-alpha (local candidate) | Navigate help and read option details across terminal sizes. | [Candidate](release-candidate.md#v060-alpha-local-candidate) · [Release notes](release-notes-v0.6.0-alpha.md) |
| v0.5.0-alpha (previous) | Browse Ubuntu package-manager verbs, builtin topics and applicable shipped and optional command help. | [Accepted handoff](audit-history.md#ubuntu-coverage-handoff-acceptance) · [Exact-package verification](release-candidate.md#v050-alpha-local-candidate) |
| Unassigned | Make searches and selection changes redraw faster in large menus. | If repeated matching or text wrapping accounts for the delay, measure time from a keypress to the updated screen before and after the change. Confirm that editing a query refreshes the matches, changing selection shows the correct Details, and resizing rewraps the text. [Redraw experiments](ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Unassigned | Open menus faster for commands whose installed identity must be checked before showing help. | If traces identify redundant discovery work, compare first display time and probe counts on the same fixtures. Verify matching and mismatched executable identities, stale entries and failed probes still produce the expected help or fallback. [Discovery investigation](runtime-architecture.md#optimization-candidates) |

The loading improvement retains serial, full-collection validation. Changes to the loading architecture require a separate decision. Test selection, benchmarks and release checks can proceed in roadmap order independently of the release sequence. [Conditional decisions](../ROADMAP.md#conditional-decisions)

### Assigning the next number

1. **Identify the program change.** Describe what users can do, see or measure in the installed program and how to verify it. Keep maintenance tasks on the roadmap.
2. **Number changes in shipping order.** Identify the plan, target and step delivered. Separately released ordinary steps each advance the patch. Steps shipped together receive one number based on their combined outcome. Apply the plan-transition, substantial-outcome and patch-9 rules above, then renumber later proposals from that release. A deferred experiment leaves the next number available.
3. **Verify the combined candidate.** Run focused checks while changes are in progress. Freeze the source, build twice and compare the outputs. Supply the first package set and historical upgrade fixture to one full offline run per target across Ubuntu 26.04 with Python 3.14 and Ubuntu 24.04 with Python 3.10 and 3.12. Record pass, fail and skip counts for those exact artifacts. [Sandbox procedure](development.md#isolated-local-debugging) · [Candidate validation](release-candidate.md#final-source-and-package-checks)
4. **Record the release.** When preparing the candidate, set `VERSION` and record the changes actually included in the changelog. Mark it published only after the corresponding tag and release artifacts are available. Keep later proposals here. [Changelog](../CHANGELOG.md) · [Release procedure](releases.md)
