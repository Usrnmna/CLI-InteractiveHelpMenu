# Changelog

## Unreleased

- Context review corrections validate executable tokens before diagnostics,
  protect attached parent values from replacement, and retain root-global literal
  operands. Passive diagnostics report invalid home expansion and actual shell
  locale requirements. Runtime and passive cache readers reject symlinks/special
  files and enforce actual read limits.
- Declared parent-option arity preserves leaf context for Compose file, project,
  and profile options without forwarding pending values to documentation probes.
- Passive `--doctor` and `--explain` JSON reports inspect configuration, context,
  provenance, and bounded cache state. Reason-coded errors omit rejected input
  values and arbitrary subprocess output.
- Cache version 8 fingerprints fixed pip/pytest version responses under the
  selected interpreter before auto-mode cache reuse. Failed identity checks
  bypass caching; unchanged-version local edits require expiry or refresh.
- Third-party compatibility coverage includes all essential, next, and extended
  tiers: 129 command paths across 62 executable names, with loadable drivers,
  independent sentinel expectations, and captured help excerpts.
- Recognized sudo/env/command prefixes, selected-interpreter pip/pytest module
  help, literal ip keywords, concrete FFmpeg selectors, and repeated esptool
  address/file groups preserve buffer text and cursor offsets. Ambiguous lookup
  forms and incomplete groups fail closed without executing pending commands.
- Version guards distinguish Mike Farah yq, JavaScript Yarn, and current/legacy
  esptool syntax. Cache identity retains interpreter and executable context
  and invalidates entries predating Ansible's fixed UTF-8 probe locale.
- Live dependency checks corrected Go run's build-only output option, Podman's
  optional pull policy, and fzf's optional count aliases. Explicit nonnegative
  integer metadata supports separate fzf counts without consuming arbitrary text.
- Curated profiles and independent route fixtures cover Linux services, SSH,
  Python/Go/.NET tooling, networking, OpenSSL, JavaScript, Podman, PostgreSQL,
  terminal tools, Ansible, cloud CLIs, Git stash/worktree, and embedded tooling.
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
