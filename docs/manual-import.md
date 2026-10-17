# Importing manual pages into a help collection

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Import manual pages into profiles and drivers

`--import-man` converts a manual into a reusable JSON option profile and a
manual-only driver route. The command path following `--import-man` identifies
the documented command; no target program is invoked or required to be installed.

Import an installed page into a local collection:

```bash
python3 cli_help/main.py --import-man git commit --man-page git-commit \
  --output-dir "$HOME/.config/cli-help/imported"
```

## File input formats

Alternatively, input rendered UTF-8 text, a local roff manual, or a compressed
manual file:

```bash
python3 cli_help/main.py --import-man example convert \
  --man-text /path/to/rendered-manual.txt \
  --output-dir "$HOME/.config/cli-help/imported"

python3 cli_help/main.py --import-man example convert \
  --man-file /path/to/example-convert.1.gz \
  --output-dir "$HOME/.config/cli-help/imported"
```

`--man-text` reads text directly. `--man-file` invokes the installed man renderer
with a literal local filename; it accepts plain roff and formats supported by
that renderer, including gzip on man-db. With neither file option, the importer
looks up the installed page in sections 1 and 8. `--man-page` overrides the
default hyphenated page name, including the fallback page recorded for file
imports. Input files and rendered output are limited to 512 KiB. Normal discovery
timeout settings apply to rendering. Manual content must be trusted for local
rendering; the process limits do not sandbox the renderer.

## Generated files and activation

The command prints the created paths and option count. Enable the collection:

```bash
export CLI_HELP_PROFILES="$HOME/.config/cli-help/imported/profiles"
export CLI_HELP_DRIVERS="$HOME/.config/cli-help/imported/drivers"
python3 cli_help/main.py --check
```

Selection then uses the imported static profile without probing the target.
The generated driver records a manual-only fallback for the imported path.
Categories, descriptions, aliases, and recognized argument requirements are
inferred from the manual using the same parser as discovery. No flags are
invented when a page lacks recognizable option declarations; the import fails
without creating a configuration collection. Generated JSON remains editable.

## Updates and interrupted writes

Importing another subcommand merges its route into the same program driver.
Unrelated routes and global-option declarations are preserved. To update an
existing matching profile/route, repeat the command with `--replace`; this resets
that route to manual-only discovery while preserving its positional boundary.
Each file is written atomically, and an exclusive `.import.lock` prevents
concurrent importer updates. A process or system interruption between the profile
and driver writes may leave a complete profile without its route update. Inspect
the stopped importer and lock, then rerun with `--replace` to reconcile the pair.
The importer does not modify `.bashrc` or automatically change active directories.

For multiple installed commands, use [bulk scanning](bulk-scan.md). Collections
with scan reports can be corrected through the [interactive reviewer](review.md).
The [profile and driver reference](profiles-and-drivers.md) describes the generated
file formats.
