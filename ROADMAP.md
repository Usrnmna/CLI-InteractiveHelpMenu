# Project roadmap

## Remaining work

**Current release handoff · v0.6.0-alpha.** Use the first build in `dist/candidate-v0.6.0-alpha/` and the matching source manifest for this release. The maintainer owns commit, push, tag, GitHub asset uploads and publication. Before tagging, match the packaged files in the intended commit to BUILD-INFO.json. After uploading, verify all eleven public asset sizes and digests. The earlier v0.5.0-alpha package and its verification remain separately identified. [Local verification record](docs/release-candidate.md#v060-alpha-local-candidate) · [GitHub release body](docs/release-notes-v0.6.0-alpha.md)

### Narrow terminal navigation preview

The maintainer selected Categories → Options → Details for the narrow prototype, the split view for wide terminals, and accepted resize cases A–F. Phase 4 verification is complete at `266e756`. B preserves the reading phrase and F closes with Ctrl-L at the Bash prompt. The separate product decision is whether the three-screen flow should become the default at 60–79 columns in a future release. The v0.6.0-alpha candidate requires `CLI_HELP_NARROW_MENU=1`. At 80 columns the split view resumes. Compare the same search at 79 columns with the [opt-in layout](docs/assets/resize-review/phase2/A-apply-narrow.png) and the [default layout](docs/assets/resize-review/phase2/A-control-narrow.png). [Five demos](docs/menu-demo-storyboards.md) · [Completed resize verification](docs/terminal-resize-review.md#phase-4--verify-the-accepted-changes-together)

### Unresolved provider findings

Reviewed usage guidance is a completed inventory outcome. Reopen only the affected invocation when its condition below is met. The ledger identifies each path, applicable image, package revision, source and disposition. [Invocation ledger](docs/ubuntu-command-coverage/phase1-review.tsv) · [Evidence and reopening conditions](docs/ubuntu-coverage-audit.md#phase-2-follow-up-on-retained-guidance)

| Finding | Evidence or decision needed | Action when available |
| --- | --- | --- |
| `/usr/bin/ptardiff -h` | A matching Perl revision resolves the conflict between the manual and the packaged script. | Compare the manual with the script and check both bare `-h` and the value-taking form. Declare help only if its arity and behavior agree. |
| `/usr/sbin/lxc` and `/usr/sbin/lxd` | A Server Default, Server Minimized or Server Cloud image or matching fixture identifies the installed LXD snap revision and supplies its command tables. | Verify the client and daemon tables separately, then record each wrapper’s result for that image. |
| Choices after required operands | A matching provider documents a root form, or an explicitly approved change can represent the later argument position. | Check the FUSE helpers, `fprintd-delete`, `xsetmode` and `wpa_action` at their documented positions. Preserve preceding operands during selection and insertion. |
| Plus-prefixed and punctuation spellings | An explicitly approved representation supports the exact literal or alias. | Check `+w`, `+c`, shell toggles, `-?` and `-#` against their respective providers. Verify literal insertion and shell quoting with a pending operand. |
| Delegated and compound arguments | Fixed evidence establishes which program owns the spelling, its revision and its argument form. A grammar change requires explicit approval. | Declare only choices the identified provider owns and the menu can insert faithfully. Keep positional guidance for the other cases. |

## Conditional decisions

These decisions have their own triggers and can be taken up after the Ubuntu handoff.

| Trigger | Action and completion criterion |
| --- | --- |
| Noble package availability changes | Check rank 62 (`magick`) and rank 95 (`starship`) against the matching archive. Update the affected optional row and installation guidance when the package supplies that executable. [Ranked inventory](docs/ubuntu-command-coverage/optional.tsv) |
| A future hosted comparison has matching runner images per target and the maintainer requests another pair | The completed tagged pilot matched all 2,066 IDs and outcomes per target. Its required comparison failed on image revisions. Keep the ordinary unsharded CI default. A future default change requires a successful matched comparison and separate approval. [Run links, image differences and measurements](docs/audit-history.md#hosted-sharding-comparison-at-v050-alpha) |
| Measurements identify a material menu or discovery cost | Isolate the measured operation, compare matched timings and verify the affected behavior. Obtain explicit approval before introducing selective loading, a persistent index or another process. [Performance plan](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Focused test selection still leaves substantial cost | Pilot opt-in result reuse for one group. Verify invalidation for changed sources, tests, targets, fixtures and environments, including interrupted runs. Compare executed, reused, failed and skipped counts to a full run. Record parity and measured savings before considering CI selection. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) |

## How to audit a batch

For reopened provider rows, group changes that share evidence or fixtures. Run focused host checks for routing, arity, exact insertion and pending-buffer preservation as each group changes. Batch the affected rendering and fixed-source checks across targets, reconcile the changed inventories, validate both collections and run the strict numerical gate. Freeze the combined inputs once and run one full offline suite per target (`host`, `noble310`, `noble312`). Record each target as it finishes. [Command-help audit procedure](docs/development.md#auditing-command-help) · [Offline target setup](docs/test-selection-plan.md#reproduce-the-paired-offline-baseline)

## Recording progress and finishing the audit

Keep the next action and its dependency here. Record completed reviews, source identities and test outcomes in the [audit history](docs/audit-history.md) or the relevant family audit.
