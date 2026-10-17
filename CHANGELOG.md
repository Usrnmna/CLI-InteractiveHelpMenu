# Changelog

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
