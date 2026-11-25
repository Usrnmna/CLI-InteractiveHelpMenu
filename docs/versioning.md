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

The prepared first performance candidate uses `0.4.0-alpha` in the version file, `v0.4.0-alpha` for the tag, and **Version 0.4.0 - Alpha** for the corresponding changelog heading.

## Proposed targets

A proposed release must change the working program. Eligible changes include a Bash keybinding fix, an improvement to menu performance, and corrections to the option descriptions or literal spellings that the menu displays or inserts. README edits, audit reports, demonstration media, CI changes and test-runner improvements are maintenance. They can accompany a program change and carry no version increment on their own.

The `0.3.0-alpha` checkout expanded the command help users can find and insert. The performance plan addresses how quickly those menus open and respond. Its first implemented step reuses shared value formatting per open and starts the `0.4` series with the prepared `0.4.0-alpha` candidate. [Current checkout and release history](../CHANGELOG.md#version-040---alpha) · [Menu performance plan](ffmpeg-menu-performance-plan.md)

The remaining targets assume each improvement meets its evidence criteria and ships separately in the order shown. [Roadmap tasks and dependencies](../ROADMAP.md#remaining-work)

| Proposed release | Change to the working program | Evidence for inclusion |
| --- | --- | --- |
| v0.4.1-alpha | Make searches and selection changes redraw faster in large menus. | If repeated matching or text wrapping accounts for the delay, measure time from a keypress to the updated screen before and after the change. Confirm that editing a query refreshes the matches, changing selection shows the correct Details, and resizing rewraps the text. [Redraw experiments](ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| v0.4.2-alpha | Reduce CPU use while an open menu waits for input. | If idle redraws have measurable cost, compare idle CPU over the same interval and terminal geometry. Resize the terminal while idle, confirm the menu recovers, then check navigation, insertion and cancellation. [Runtime measurements](runtime-architecture.md#optimization-candidates) |
| v0.4.3-alpha | Open menus faster for commands whose installed identity must be checked before showing help. | If traces identify redundant discovery work, compare first display time and probe counts on the same fixtures. Verify matching and mismatched executable identities, stale entries and failed probes still produce the expected help or fallback. [Discovery investigation](runtime-architecture.md#optimization-candidates) |

The roadmap also calls for measuring startup profile loading. A change to the loading architecture would require a separate decision before becoming a target. Test selection, benchmarks and release checks can proceed in roadmap order independently of the release sequence. [Conditional decisions](../ROADMAP.md#conditional-decisions)

### Assigning the next number

1. **Identify the program change.** Describe what users can do, see or measure in the installed program and how to verify it. Keep maintenance tasks on the roadmap.
2. **Number changes in shipping order.** Identify the plan, target and step delivered. Separately released ordinary steps each advance the patch. Steps shipped together receive one number based on their combined outcome. Apply the plan-transition, substantial-outcome and patch-9 rules above, then renumber later proposals from that release. A deferred experiment leaves the next number available.
3. **Verify the combined candidate.** Run focused checks while changes are in progress. For a release, run one full offline matrix on the finished batch across Ubuntu 26.04 with Python 3.14 and Ubuntu 24.04 with Python 3.10 and 3.12. Record pass, fail and skip counts per target, then apply the package checks to the exact release source. [Sandbox procedure](development.md#isolated-local-debugging) · [Candidate validation](release-candidate.md#final-source-and-package-checks)
4. **Record the release.** When preparing the candidate, set `VERSION` and record the changes actually included in the changelog. Mark it published only after the corresponding tag and release artifacts are available. Keep later proposals here. [Changelog](../CHANGELOG.md) · [Release procedure](releases.md)
