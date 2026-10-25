# Collection consistency and guarded backup restoration

[Documentation index](README.md) · [Review and backed-up saves](review.md) ·
[Passive diagnostics](diagnostics.md)

## Read-only inspection

```bash
python3 cli_help/main.py --check-collection /path/to/collection
```

This mode inspects the selected collection's `profiles/`, `drivers/`, root JSON
reports, existing `.review-backups/`, and `.scan.lock`/`.import.lock` entries.
It does not invoke targets, discover help, write files or bytecode, change locks,
load personal configuration, or alter pending input. It uses neither the command
buffer nor discovery settings. Files are read as bounded regular files with
symlink protection; inspection is limited to 4,096 entries, 2 MiB per file,
64 MiB total, and a bounded directory depth. Driver files retain their 256 KiB
schema limit. Incomplete inspection prevents automatic restoration.
Reserved collection directories must be directories, and JSON metadata/report
entries must be regular files. Directory enumeration uses pinned descriptors so
a concurrent symlink swap cannot introduce names from outside the collection.
Scan versions remain integers; recorded completion/interruption/generated fields
must be booleans when present. Missing optional historical fields retain their
existing incomplete/unreviewed interpretation.

JSON includes `status`, `inspection_complete`, an opaque `snapshot`, file
identities/hashes, stable finding codes and severities, and existing backup IDs.
Locations are reported; file contents, embedded report errors, lock contents,
configured probe operands, and command buffers are omitted. Local paths and
hashes still require review before sharing. Exit status is zero for `ok` or
`attention_required`, and one for `invalid` or `rejected`.

| Finding codes | Meaning and guidance |
| --- | --- |
| `collection_json_invalid`, `duplicate_profile`, `duplicate_driver` | Invalid schema/JSON or duplicate identity; inspect the named file locally |
| `sem_*`, `authoring_semantics_review` | Supplied numerical metadata has structural errors, explicit uncertainty or inactive declarations awaiting review; absent legacy metadata does not trigger completeness findings |
| `collection_layout_invalid` | A reserved collection directory is a file or another unsupported entry; inspect the named location without replacing it automatically |
| `profile_route_missing`, `driver_profile_missing` | Unpaired metadata; static-only and discovery-only collections can intentionally produce warnings |
| `manual_metadata_mismatch`, `import_metadata_invalid` | Imported provenance differs or has an invalid shape; review before regenerating |
| `scan_pair_missing`, `scan_report_invalid` | Recorded generated output is missing, or scan evidence has invalid identities/structure |
| `scan_incomplete`, `review_evidence_stale` | Interrupted scan or hashes differing from reviewed files; re-review current files |
| `lock_ownership_uncertain` | A lock exists; coordinate with writers and inspect ownership before any manual removal |
| `backup_manifest_missing`, `backup_manifest_invalid`, `temporary_write_present` | Retained recovery data needs local inspection; nothing is promoted or deleted |
| `unsafe_collection_path`, `unsafe_collection_file`, `collection_limit`, `collection_changed`, `collection_unreadable` | Symlinks, special files, bounds, concurrent changes, or unreadable entries prevent reliable evidence |

Lock age or absence of a PID does not establish staleness. Host differences,
ownership and PID reuse remain uncertain. Inspection never labels these locks
safe to remove, and restoration never breaks an existing lock.

Numerical findings retain structured source/pointer, command, option/component
and correction guidance without including complete profile contents. Explicit
unresolved or incomplete declarations produce warnings; malformed active metadata
produces errors. Restoration uses the shared structural check for supplied fields
before writes. See [numerical authoring and inspection](numerical-inventory/step6-authoring.md)
for preservation, inactive evidence and platform verification limits.

## Explicit restoration of an existing review backup

First inspect the collection and choose a backup ID locally. Then supply both
that ID and the exact snapshot from a fresh inspection:

```bash
python3 cli_help/main.py --recover-collection /path/to/collection \
  --restore-backup BACKUP_ID --expect-snapshot SNAPSHOT
```

The command is an explicit replacement choice. It reuses manifests created by
the existing review/save workflow; it does not infer a repair from an error.
Only direct JSON children of `profiles/` and `drivers/`, and the canonical root
`scan-report.json`, can be restored. Existing metadata directories are required.
The proposed effective profiles/drivers must validate as paired, unique metadata;
unrelated malformed metadata can therefore require separate local correction.
Malformed current bytes can be replaced when the chosen backup restores validity.
Every proposed driver is schema-validated before pairing, including JSON arrays,
nulls, strings, or numbers that cannot represent a driver. These produce a safe
`invalid_backup` rejection. Manifest target names must use their canonical relative
spelling; redundant separators and `.` components are rejected before writes.

The snapshot binds the choice to inspected contents and identities. Sources,
manifest, targets and owned locks are checked again after staging and immediately
before each replacement. Pinned directory descriptors prevent a parent symlink
swap from redirecting writes. Scanner/importer locks exclude cooperative writers;
new, removed, or changed metadata also invalidates the staged plan. This does
not provide a filesystem transaction against arbitrary concurrent tools.
A changed collection requires another inspection and another explicit choice.

Before replacement, original bytes and a manifest are retained in a new private
`.review-backups/recovery-ID/` directory (mode 0700). Restoration preserves the
selected backup bytes exactly, including hashes referenced by scan evidence.
Existing backups remain untouched. Results report `restored`, `unchanged`, or
`rejected`. Repeating an already applied choice with a fresh snapshot is a no-op
and creates no additional backup. Changed lock ownership is never unlinked.

Replacement is atomic per file. A multi-file interruption can leave some files
restored and others unchanged. `recovery_incomplete` retains the backup location;
inspect again before choosing a valid retained backup. No automatic rollback or
multi-file transaction is claimed. Incomplete staging also remains inspectable.
Deletion, lock removal, restoration of arbitrary files, and automatic startup
repair are excluded. A backup requiring deletion reports `restore_requires_removal`
and is retained for explicit manual handling. Other guidance uses existing
[review drafts and save validation](review.md), or a separately chosen manual
import. A fully atomic multi-file store would require architectural approval.
