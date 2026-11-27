# Project roadmap

## Remaining work

**No required work remains for the Ubuntu coverage batch.** [Maintainer acceptance](docs/audit-history.md#ubuntu-coverage-handoff-acceptance)

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
| The maintainer authorizes the hosted shard comparison | Run `timed-control`, then `three-shard-pilot` on the same commit using the control run ID. Verify per-target discovery, outcomes and skip reasons. Record queue delays, elapsed time to the last required job, slowest shard and total runner-minutes. Use those results to decide whether to propose changing CI defaults. [Manual CI pilot](docs/development.md#manual-three-shard-pilot) |
| Measurements identify a material menu or discovery cost | Isolate the measured operation, compare matched timings and verify the affected behavior. Obtain explicit approval before introducing selective loading, a persistent index or another process. [Performance plan](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Focused test selection still leaves substantial cost | Pilot opt-in result reuse for one group. Verify invalidation for changed sources, tests, targets, fixtures and environments, including interrupted runs. Compare executed, reused, failed and skipped counts to a full run. Record parity and measured savings before considering CI selection. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) |

## How to audit a batch

For reopened provider rows, group changes that share evidence or fixtures. Run focused host checks for routing, arity, exact insertion and pending-buffer preservation as each group changes. Batch the affected rendering and fixed-source checks across targets, reconcile the changed inventories, validate both collections and run the strict numerical gate. Freeze the combined inputs once and run one full offline suite per target (`host`, `noble310`, `noble312`). Record each target as it finishes. [Command-help audit procedure](docs/development.md#auditing-command-help) · [Offline target setup](docs/test-selection-plan.md#reproduce-the-paired-offline-baseline)

## Recording progress and finishing the audit

Keep the next action and its dependency here. Record completed reviews, source identities and test outcomes in the [audit history](docs/audit-history.md) or the relevant family audit.
