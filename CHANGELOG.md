# Changelog

## Unreleased

- Third-party compatibility coverage includes all essential, next, and extended
  tiers: 59 command paths across 34 executable names, with loadable drivers,
  independent sentinel expectations, and captured help excerpts.
- Discovery recognizes aligned aliases, boolean negation shorthand, kubectl
  defaults, AWS typed values, jq two-value options, and partially optional
  placeholders. Fixed suffix-help routes support additional CLI conventions.
- Live compatibility reports record versions, tiers, argument-count checks, and
  exact insertion checks for every discovered flag. Known case selections retain
  their assertions; missing and unsupported commands remain explicit.
- GitHub release updater selects compatible archives, verifies sizes and SHA-256
  checksums, and preserves settings through the managed update workflow.
- Stable and prerelease channels, exact version selection, check-only operation,
  source-package selection, and deferred review are available through the CLI.
- Conflicts open the guided reviewer in a terminal, with retained verified source
  and resumable commands for deferred or interrupted work.
- Release selection, download failures, archive validation, concurrent updates,
  backups, and real-terminal review have dedicated offline tests.
- Additional routes cover GitHub PR viewing/creation, Cargo tests, Compose
  logs/exec, kubectl describe/logs, Helm upgrade, AWS S3 sync, and rclone sync.
- Discovery retains required values with optional suffixes and negative defaults;
  changed parser metadata invalidates older discovery caches.
- Terminal-size changes trigger a Readline redraw after browsing. Vi insertion
  maps to Bash's `vi-insert` map; reserved dispatch-key conflicts are rejected.
- Documentation and terminal demonstrations reflect the development tree.
  Source packages include the media generator and its optional requirements.
  Dependency updates cover pinned GitHub Actions and optional media tools.
- The README demonstration builds a multi-option rsync command and scrolls
  the twelve-option ls Display category. Capture checks verify visible states,
  valued insertions, cancellation, and pending commands without execution.

## Version 0.1.1 - Alpha

- Guided update-conflict merging accepts or rejects individual changed blocks
  directly in the terminal, with navigation, preview, and validation before queuing.
- Accepted merges use the existing backup, stale-input, ownership, and rollback
  safeguards. External-editor merging remains available.
- Linux release packages include a compiled convenience launcher, a self-extracting
  installer, complete runtime and source archives, build provenance, and SHA-256
  checksum files. Bash and Python remain runtime dependencies.

This alpha includes the Bash help browser, documentation discovery, command
drivers, manual import, bulk scanning, guided collection review, installation,
updates, and update-conflict review. Compatibility limits remain documented in
the [usage guide](docs/usage.md) and [release guide](docs/releases.md).
