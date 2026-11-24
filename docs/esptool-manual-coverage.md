# Esptool flash-writing menus

| Profile | Guard | Original rows | Added | Final |
| --- | --- | ---: | ---: | ---: |
| [esptool.py write_flash](../profiles/esptool.py-write_flash.json) | v4 | 10 | 13 | 23 |
| [esptool.py write-flash](../profiles/esptool.py-write-flash.json) | v5 family | 10 | 17 | 27 |
| [esptool write-flash](../profiles/esptool-write-flash.json) | v5 family | 10 | 17 | 27 |

The [declaration inventory](../tests/fixtures/embedded-manual/esptool-options.tsv) groups literal aliases by effect and records public or hidden visibility, operand slots and release. A trailing plus in the slots column denotes repeated groups. The v4 menu has 14 public effects with nine additional spellings. Each v5 menu has 16 public effects in 5.6.0, ten additional spellings and one earlier selectable spelling, `--no-diff-verify`. The two v5 executable names share the same leaf syntax. Version guards identify the command family. Availability of individual newer flags still depends on the installed release.

## References and release differences

Espressif documents repeated byte-offset/file pairs, chip-dependent header settings, erase boundaries, encryption safeguards and compressed serial transfers. The declarations in `esptool/__init__.py` give the short options and operands, including `-ff`, `-fm`, `-fs` and `-sc`. The numeric tables retain their separately verified chip and release scopes. The 5.6.0 parser also lists `32m` and `64m`. No registered chip in that release can encode either setting in a bootloader header. [v4 manual](https://docs.espressif.com/projects/esptool/en/release-v4/esp32/esptool/basic-commands.html) · [v5 manual](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html) · [flash header parameters](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/flash-modes.html) · [migration guide](https://docs.espressif.com/projects/esptool/en/latest/esp32/migration-guide.html)

| Version | Consequence for the menu |
| --- | --- |
| 4.7.0, 4.8.1 | The legacy parser accepts `--verify`. The writer requests a further check of unencrypted data. [4.7.0 declarations](https://github.com/espressif/esptool/blob/v4.7.0/esptool/__init__.py) · [4.8.1 writer](https://github.com/espressif/esptool/blob/v4.8.1/esptool/cmds.py) |
| 4.12.0, 4.14.0 | Help still lists `--verify`. These writers do not use that flag to run an additional pass. [4.12.0 writer](https://github.com/espressif/esptool/blob/v4.12.0/esptool/cmds.py) · [4.14.0 parser](https://github.com/espressif/esptool/blob/v4.14.0/esptool/__init__.py) · [4.14.0 writer](https://github.com/espressif/esptool/blob/v4.14.0/esptool/cmds.py) |
| 5.0.2, 5.1.0 | The write command drops the v4 verification flag. The fast-reflash options are absent. [5.0.2 parser](https://github.com/espressif/esptool/blob/v5.0.2/esptool/__init__.py) · [5.1.0 parser](https://github.com/espressif/esptool/blob/v5.1.0/esptool/__init__.py) |
| 5.2.0 | Adds `--diff-with`, `--skip-flashed` / `-s` and `--no-diff-verify`. The latter suppresses MD5 checks during differential flashing. [parser](https://github.com/espressif/esptool/blob/v5.2.0/esptool/__init__.py) · [writer](https://github.com/espressif/esptool/blob/v5.2.0/esptool/cmds.py) |
| 5.3.0 through 5.6.0 | `--trust-flash-content` supersedes `--no-diff-verify`, which remains a deprecated accepted spelling. The current option skips verification of unchanged files only. Data written after a difference is still checked and a failed partial write is retried in full. `--skip-flashed` now excludes `--diff-with`. [5.3.0 parser](https://github.com/espressif/esptool/blob/v5.3.0/esptool/__init__.py) · [5.4.0 parser](https://github.com/espressif/esptool/blob/v5.4.0/esptool/__init__.py) · [5.5.0 parser](https://github.com/espressif/esptool/blob/v5.5.0/esptool/__init__.py) · [5.6.0 parser](https://github.com/espressif/esptool/blob/v5.6.0/esptool/__init__.py) · [5.6.0 writer](https://github.com/espressif/esptool/blob/v5.6.0/esptool/cmds.py) |

Ubuntu Noble distributes `4.7.0+dfsg-0.1`. Its manual describes `esptool write_flash` and examples but omits many leaf switches. Resolute's `4.7.0+dfsg-0.2` manual page has no command text (the installed compressed man file expands to zero bytes). Both packages provide the executable `esptool`. Their `esptool write_flash` is outside the three bundled routes, which preserve the explicit vendor executable and command guards. The Ubuntu v4 evidence still applies to the underscore parser. [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/esptool.1.html) · [Noble file list](https://packages.ubuntu.com/noble/all/esptool/filelist) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/esptool.1.html) · [Resolute package](https://packages.ubuntu.com/resolute/esptool)

## Original rows, restored Details and exclusions

| Original entries in each route | Disposition and change |
| --- | --- |
| Flash mode, size and frequency | Incomplete. Identify the bootable image header, retained settings, exact chip-dependent tokens, binary size units and clock units. Expose all three short aliases. |
| `--erase-all` | Incomplete. The normal write erases affected sectors, including partially covered ones. This flag also erases data outside the requested images. |
| `--encrypt` | Incomplete. Distinguish encryption of all supplied images from a separate encrypted list. The latter consumes address/file pairs. Chip configuration and alignment matter. |
| `--force` | Incomplete. Identify the bootability implications of overriding protection and compatibility checks. |
| `-z`, `--compress`, `-u`, `--no-compress` | The core transfer descriptions were accurate. Restore the mutually exclusive forms, ROM/stub defaults and distinction between serial transfer and stored bytes. |

New rows cover local help, aliases, SPI wiring, progress, encryption prechecks and version-specific verification. The v5 menus also cover the ordered list of previously flashed files and its literal `skip` marker. V5 accepts deprecated underscore header spellings and `--ignore_flash_encryption_efuse_setting` through a compatibility translation. Those terms appear in Details on the v5 rows, which insert the canonical hyphenated names. The parser also accepts the old command spelling, but the three guarded routes retain their explicit version/command contract. [5.6.0 translation table](https://github.com/espressif/esptool/blob/v5.6.0/esptool/cli_util.py)

Chip, serial port, baud, boot/reset settings, connection attempts, stub selection, tracing and other global selectors belong before the subcommand. The local `-p` suppresses progress. The global `-p PORT` selects the serial port. In newer v5 clients `-s` means silent before the command and skip matching images after it. Hidden experimental NAND parser options `--flash-type` / `-ft` and `--nand-end-address` are recorded in the inventory and excluded from the public manual menus. Separate commands such as `verify-flash` and `erase-flash` have independent grammars. [5.6.0 declarations](https://github.com/espressif/esptool/blob/v5.6.0/esptool/__init__.py)

## Fixture and terminal evidence

The [original synthetic v4 example](../tests/fixtures/help/expansion-esptool.py-write_flash.txt) and [historical capture manifest](../tests/fixtures/help/followup-systems/manifest.json) keep their original provenance. The latter supplies real v4.12.0 and v5.6.0 leaf help. The parser inventory resolves option names truncated by the width of the v5 help capture.

New argument-only checks used temporary binary files and a private home. Resolute's installed 4.7.0 command was stopped immediately after `ArgumentParser.parse_args`. It accepted flash options before or after the contiguous positional pairs, and rejected an ordinary option between two pairs or inside one. An isolated 5.6.0 Click command was exercised through `make_context` without dispatch. It accepted interspersed options and retained both pairs. It also accepted a complete option inside a pair, although the editor deliberately protects incomplete pairs. Both parsers accepted an ordinary pair followed by `--encrypt-files` and two encrypted pairs. The 5.6.0 parser mapped `--diff-with sample.bin skip` to a baseline file and an empty comparison slot. A device-free call to `parse_flash_freq_arg` on all 15 classes in the 5.6.0 `CHIP_DEFS` registry rejected both `32m` and `64m`. As a control, the same call accepted `40m` on 11 classes and `60m` on ESP32-C2. No serial port was accessed or image written. [Chip registration](https://github.com/espressif/esptool/blob/v5.6.0/esptool/targets/__init__.py) · [Header frequency lookup](https://github.com/espressif/esptool/blob/v5.6.0/esptool/loader.py)

The [independent tests](../tests/test_embedded_manual_inventory.py) check both guards, the public spelling/arity union and versioned verification behavior. The [shared verification report](remaining-bundled-verification.md) records the real Bash/tmux walks, edits, refusal checks and full-suite results.

The legacy menu requires major version 4 in fixed root help. A 3.x banner cannot select this profile. The dash-command routes retain the v5-or-newer identity check.
