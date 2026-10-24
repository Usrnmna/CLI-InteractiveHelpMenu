# v0.1.2-alpha

This foundational alpha prerelease improves command-context correctness,
privacy-preserving diagnostics, compatibility evidence, terminal behavior, and
package/update reliability. Selecting an option edits pending Bash input; it does
not execute that command. Separate help/version/manual requests remain fixed,
reviewed, bounded, and independent of pending operands.

## Changes

- Declared parent-option values preserve nested command context, including
  Docker Compose file and profile options before a leaf subcommand.
- Explicit argument forms support selective attached-only values and unambiguous
  declared short bundles. Quoting, Unicode, suffixes, cursor positions, positional
  boundaries, `--` separators, and child-command regions remain protected.
- Passive `--doctor` and `--explain` report configuration, provenance, cache state,
  and reason codes without target discovery, writes, or pending-value disclosure.
  Native and Bash interpreter-startup errors omit the configured value.
- Discovery freshness checks selected-interpreter pip/pytest module identity;
  failed identity checks bypass caching. Fixed-route controls and discovery modes
  retain their existing execution boundaries.
- Driver activation remains explicit. Diagnostics explain selection and metadata
  provenance; manual composition instructions preserve existing precedence.
- Captured help and insertion contracts deepen Git, Compose, Kubernetes, GitHub
  CLI, and GNU utility workflows. Coverage describes bounded routes and syntax,
  rather than exhaustive compatibility with every executable/version.
- Cell-width handling covers wide and combining characters. Configurable key
  timing, resize/reopen checks, Readline restoration, and rendered regressions
  strengthen keyboard and terminal behavior.
- Read-only collection consistency checks distinguish invalid metadata, stale
  evidence, and uncertain locks. Explicit snapshot-bound backup recovery retains
  originals and refuses changed or unsafe evidence; locks are not broken automatically.
- Packaging captures source through guarded descriptors, compiles the captured
  C bytes, excludes reserved private/generated inputs, and verifies actual archive
  and installer agreement before package tests. Installation and update review
  preserve custom files, backups, cancellation, and resumable conflict handling.
- Repository rules protect nested private outputs and extensionless binaries.
  CI checks artifact policy and retains explicitly scoped evidence without
  enabling automatic publication.

## Requirements and limitations

Linux, Bash 4.4+, Python 3.10+ with `curses`, a UTF-8 terminal, and `stty` are
required. The native executable targets Linux x86_64 with glibc 2.34 or newer.
It requires the adjacent Bash/Python runtime; it does not embed Python or provide
a Windows executable. The source archive provides the Bash/Python installation
path where the native launcher is unsuitable.

Supplied compatibility drivers remain opt-in. Ambiguous or unsupported grammar
continues to fail conservatively; arbitrary shell evaluation, plugin enumeration,
and general expression-language parsing are excluded. GNU captures do not establish
BSD/BusyBox equivalence. Rendered keyboard/cell tests do not establish screen-reader
support or compatibility with every terminal, Python, Bash, architecture, or libc.

## Assets and verification

| Asset | Purpose |
| --- | --- |
| `cli-interactive-help-v0.1.2-alpha-source.tar.gz` | Maintained source, tests, fixtures, documentation, configuration, and optional development tools |
| `cli-interactive-help-v0.1.2-alpha-linux-x86_64.tar.gz` | Complete source/runtime bundle with native launcher |
| `cli-interactive-help-v0.1.2-alpha-linux-x86_64.run` | Verified self-extracting installer/updater |
| `cli-help-v0.1.2-alpha-linux-x86_64` | Standalone launcher download; place beside the extracted runtime as `cli-help` |
| `BUILD-INFO.json` | Source hashes and compiler/platform requirements |
| Five individual `.checksum` files and `SHA256SUMS.checksum` | Per-file and aggregate SHA-256 verification |

Download all eleven files into one directory and verify before installation:
Use the named source archive asset when selecting source-only installation;
GitHub's automatically generated source downloads have a different inventory.

```bash
sha256sum -c SHA256SUMS.checksum
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run --verify
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run install \
  --prefix "$HOME/apps/cli-help" --no-rc
source "$HOME/apps/cli-help/bash/interactive-help.bash"
```

The installer also requires `tar`, `tail`, `mktemp`, and `sha256sum`. `--no-rc`
avoids startup-file registration. For an existing installation:

```bash
bash cli-interactive-help-v0.1.2-alpha-linux-x86_64.run update \
  --prefix "$HOME/apps/cli-help"
```

Update status `2` retains verified installer source and prints the conflict-review
command. Keep source and backups until explicit review is complete. Source-only
updates remove an unchanged optional native launcher and preserve an edited one.
Published alpha discovery requires `--prerelease`; equal versions are not remotely
reinstalled, so same-version local snapshots use the local-source update path.

The release tag identifies the tested source commit. Match `BUILD-INFO.json` to
that source and verify checksums; hashes establish integrity rather than an
independent publisher signature. Historical `v0.1.1-alpha` packages remain unchanged.
