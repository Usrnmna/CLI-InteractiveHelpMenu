## Change and purpose

Describe the concrete problem, resulting behavior, and affected components.
Link a related issue when available. Use synthetic command arguments in examples.

## Verification

List commands actually run and their results. Distinguish deterministic fixtures,
live fixed help/version checks, rendered terminal checks, and unverified cases.
For terminal changes, include cells, cursor, alternate-screen, and scrollback
evidence; logical buffer checks alone do not establish visual correctness.
For compatibility changes, identify captured implementations and versions,
fixed documentation requests, argument/child boundaries, and any unverified
variants. For diagnostics, record privacy and no-target-process/no-write checks.
For argument forms, cover exact names, attached payloads, declared bundles, and
unchanged legacy defaults. For display changes, cover mixed-width text and delayed
key sequences. For recovery changes, cover stale evidence, concurrent file changes,
uncertain locks, unsafe paths, interruptions, and preservation of original bytes.
For repository configuration, record ignore-policy checks, workflow lint, local
CI smoke results, and explicit upload paths. Retain strict failure handling;
private captures, staging files, and recovery backups must remain excluded.

## Limits and compatibility

Describe remaining limitations, configuration/schema compatibility, and any
required migration. Unrelated changes and existing execution boundaries should
remain preserved.
Describe affected driver activation/precedence and cache invalidation when relevant.

<!-- Credentials, private paths, complete pending buffers, tool homes, and raw
probe output must be excluded. Diagnostic reports require review and redaction
before sharing; local report/cache directories are not PR attachments by default. -->
