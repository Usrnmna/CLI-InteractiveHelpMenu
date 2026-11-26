# Project roadmap

## Remaining work

### Ubuntu command coverage expansion

The remaining shipped work is keyed by exact invocation and image in the [shipped inventory](docs/ubuntu-command-coverage/shipped.tsv). The [batch audit](docs/ubuntu-coverage-audit.md) defines the result codes and records the ranked and kernel results.

1. Review the **346 shipped names** with usage or manual guidance as their strongest result. Start with the 57 invocation records that identify a possible option or an option-bearing synopsis. Confirm ownership and argument boundaries against the listed provider before adding selectable declarations. Preserve usage for positional-only commands, GUI launchers and internal helpers. [Shipped results](docs/ubuntu-command-coverage/shipped.tsv) · [Per-invocation findings](docs/ubuntu-command-coverage/usage-review.tsv)
2. Revisit `magick` and `starship` if the Noble package selection changes. Noble's reference archive provides ImageMagick 6 and has no ranked `starship` package. Resolute has both roots. Retain the distinction when reviewing optional installation instructions.
3. Combine new sources, provider variants and their focused regressions before the next full offline matrix. Run the inventory reconciliation and strict numerical gate against that combined snapshot. [Batch procedure](docs/development.md#auditing-command-help)

## Conditional decisions

| Trigger | Follow-up |
| --- | --- |
| New measurements identify a material runtime cost | Isolate the proposed change, repeat matched timings and confirm behavior. Selective loading, a persistent index or an additional process requires a separate architecture decision. [Performance plan](docs/ffmpeg-menu-performance-plan.md#deferred-follow-up-on-prose-and-redraws) |
| Focused test selection still leaves substantial cost | Pilot result reuse for one bounded group. Check invalidation for changed inputs, environments, targets, fixtures and interrupted runs. Record executed, reused, failed and skipped results. Consider CI selection or sharding after local parity and measured savings. [Result reuse](docs/test-selection-plan.md#5-reuse-green-results-only-after-selection-works) · [Sharding pilot](docs/test-selection-plan.md#two-shard-host-pilot) |

## How to audit a batch

Follow the [command-help audit procedure](docs/development.md#auditing-command-help) for evidence, reconciliation and verification.

## Recording progress and finishing the audit

Record the next action and any unresolved paths or blockers here. Link family results and their evidence from the [audit history](docs/audit-history.md), which also records completed performance work, edit reviews and release verification.
