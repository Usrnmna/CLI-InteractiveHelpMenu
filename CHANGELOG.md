# Changelog

## Unreleased

No additional changes are recorded after `v0.1.2-alpha`.

## Version 0.1.2 - Alpha

The `v0.1.2-alpha` prerelease contains the foundational command-context,
diagnostics, compatibility, terminal, collection, and packaging work below.
Preserved `0.1.1-alpha` artifacts remain unchanged. See the
[release notes](docs/release-notes-v0.1.2-alpha.md) and
[package validation procedure](docs/release-candidate.md).

- Release selection excludes nested credential homes, caches, recovery state,
  and generated evidence while retaining source fixtures and public media.
  Maintained symlinks and special files are rejected. Native compilation uses
  the captured source bytes recorded in the package manifest; output beneath
  maintained source directories is refused.
- Release review pins source reads against symlink/replacement races, bounds
  special-file rejection, and refuses names inconsistent with updater extraction.
  Candidate verification checks actual archives and the embedded installer payload
  before execution. Native/Bash missing-interpreter errors omit configured values.
- Repository configuration protects nested tool homes, runtime copies, and build
  sessions while retaining public fixtures. Extensionless launchers receive binary
  handling. CI retains artifact-policy evidence and uses fresh candidate directories.
- Package regressions exercise actual candidate artifacts, historical upgrades,
  source-only transitions, retained conflict-review source, custom-file
  preservation, passive privacy checks, collection recovery, and rendered Bash
  insertion. CI retains scoped package evidence without publishing binaries.
- Repository policy excludes installer scratch directories and retains source
  fixtures and public assets. Passive CI checks exercise invalid collections and
  missing bundle values with target-execution detection and scoped safe reports.
- Review fixes pin passive collection enumeration against symlink swaps, reject
  invalid directory/report layouts and noncanonical backup paths, validate driver
  schemas before recovery pairing, and enforce typed scan-state evidence.
  Bundle value errors distinguish missing payloads from disallowed spellings
  without echoing arguments or changing pending input.
- Explicit profile value styles distinguish separate, equals, joined, and
  attached-only values. Declared OpenSSH bundles retain exact-name precedence
  and child boundaries; static 7-Zip extraction subsets protect joined payloads.
- Browser clipping and wrapping account for wide and combining characters.
  An explicit escape-delay setting supports fragmented terminal keys while
  retaining the existing default; rendered tests cover the confirmed failures.
- Read-only collection consistency reports distinguish corruption, stale
  evidence, and uncertain locks. Explicit snapshot-bound review-backup recovery
  preserves original bytes, pins directories, and rechecks staged replacements.
- Passive diagnostics identify explicit driver activation and exact route-file
  provenance. Manual composition instructions document precedence, conflicts,
  and preservation of custom collections without changing activation defaults.
- Workflow and GNU baseline captures add 31 matrix routes. Compose run retains
  its service boundary; Kubernetes inherited arity protects omitted values.
  Parser corrections preserve required optional-prefix placeholders, exclude
  truncated numeric ranges, and invalidate old metadata with cache schema 10.
- Driver-report review redacts private configured help operands and manual
  aliases, retains valid static-only context explanations, and describes
  effective pytest and version-dependent Yarn help safely. Compression ranges
  remain excluded across alignment whitespace changes.
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
- Module cache identity fingerprints fixed pip/pytest version responses under the
  selected interpreter before auto-mode cache reuse. Failed identity checks
  bypass caching; unchanged-version local edits require expiry or refresh.
- Third-party compatibility coverage includes all essential, next, and extended
  tiers: 162 command paths across 73 executable names, with loadable drivers,
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
