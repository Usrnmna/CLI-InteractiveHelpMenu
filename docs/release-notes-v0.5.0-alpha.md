## v0.5.0-alpha — Ubuntu command coverage for Bash

Press **Alt-H** while editing a Bash command to browse the options and subcommands available at the cursor. For example, with the cursor after `ins` in `apt ins 'package name'`, selecting `install` completes the verb and preserves the quoted package name. Escape restores the original line and cursor.

### Changes since v0.4.1-alpha

| Ubuntu command family | What this release adds |
| --- | --- |
| Shipped commands | Across six Ubuntu 26.04 amd64 images, 2,189 of 2,385 distinct command names have selectable options or keywords on at least one applicable invocation. The other 196 have command-specific usage or documentation guidance. The audit covers Desktop Default and Extended, Server Default and Minimized, Ubuntu Base and Server Cloud. |
| APT and dpkg | The five APT tools cover 112 command-to-verb combinations on Resolute and 104 on Noble. Options follow the selected verb, including `apt list --installed` and `apt install --simulate`. The dpkg family accounts for aliases, archive and directory operands, and all three arguments to `dpkg --compare-versions`. |
| Bash builtins | Help covers 61 builtin names. Bash 5.3 provides 44 selectable topics and 17 usage results. Bash 5.2 provides 42 and 19 respectively. Bare `echo` and `command echo` use builtin help. An explicit `/usr/bin/echo` selects the external provider. The menu preserves argument boundaries with `builtin`, `env` and `sudo`. |
| Kernel companion tools | All eight inventoried paths in the versioned Ubuntu kernel tools package have selectable results, including `rtla` and `intel-speed-select`. |
| Optional packages | The 100 ranked packages cover 119 command entries on Resolute and 117 on Noble, including siblings such as `pigz` and `unpigz`. Install optional packages separately. The reviewed Noble archive supplies ImageMagick 6 and lacks the `magick` and `starship` executables. |

Both Ubuntu reference editions ship with the runtime. Eligible commands load a per-command reference when local help is missing, including on the audited Base and Server Minimized images. For an exact provider revision and reviewed manual, the menu can replace an incorrect or incomplete parse. For example, `xzgrep` omits switches its manual lists as unsupported. The review covers 111 alternate name/revision pairs across 98 names. It added 645 declarations across 75 newly selectable Noble roots. Single-dash Tcl options and numeric printer model keywords retain their documented spellings.

Command-specific guidance explains cases where a choice depends on later operands or another program. Examples include the conflicting manual and script for `ptardiff -h` and the snap-dependent command tables for the `lxc` and `lxd` wrappers.

Expanded Details keeps accepted spellings beside their explanations in one, two or three columns. Read down a column, then across. In the release audit, all 13 rsync bandwidth suffixes remained reachable when shrinking from 160×40 to 60×16. The terminal review covered seven sizes through 200×50.

The README includes live APT and Bash builtin examples. Edition-specific inventories and the provider audit document coverage and limitations. Contributors can compare a manual timed CI control with three test shards per Python version. Routine CI uses full discovery. Documentation checks include bounded retries for transient manual-site failures and revision-specific verification for eligible GitHub links.

Readers upgrading from an earlier 0.4 build also receive the v0.4.1-alpha improvements. The idle menu checks terminal size while skipping unchanged frames. On the recorded Ubuntu host, that removed 66 repeated redraws per ten-second interval, and printable-text validation reduced median loading CPU time for 76 profiles from 118.36 ms to 74.04 ms.

### Download and install

On Linux x86_64, download the `.run` installer and its matching `.run.checksum` into the same directory. The menu requires Bash 4.4+, Python 3.10+ with curses and a UTF-8 terminal. The binary requires glibc. The installer uses tar, tail, mktemp and sha256sum.

```bash
sha256sum -c cli-interactive-help-v0.5.0-alpha-linux-x86_64.run.checksum &&
bash cli-interactive-help-v0.5.0-alpha-linux-x86_64.run --verify &&
bash cli-interactive-help-v0.5.0-alpha-linux-x86_64.run install --prefix "$HOME/apps/cli-help" --no-rc &&
source "$HOME/apps/cli-help/bash/interactive-help.bash"
```

The Linux tarball contains the complete bundle. The standalone launcher needs the adjacent extracted runtime. The source archive supports compatible Linux systems with Bash and Python. Existing installations at this same version use a local installer update to obtain the corrected package. The GitHub updater offers only higher versions.

### Verification

Source commit `9274a1a1bf1fe83ea8428a3c651dd113f09e6d98`. Two independent builds matched across all 11 files. The aggregate checksum file for the corrected set has SHA-256 `f63c07eeac464a1cb55a5d0b56cb3211edbafb80d1f9470aa90b91e3e81a3530`.

The first build passed the full offline suite on Ubuntu 26.04.1 with Python 3.14.4 and on Ubuntu 24.04.5 with Python 3.10.20 and 3.12.3. Each target passed 2,065 tests with one expected Windows-only skip. All 15 package and installed-screen tests passed on each target, including upgrade from the historical v0.1.1-alpha installer. Separate installed-prefix checks verified the 57 bundled reference files, builtin and external command routing, APT help, cancellation, insertion beside a quoted operand and removal.

[Source and coverage audit](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/blob/9274a1a1bf1fe83ea8428a3c651dd113f09e6d98/docs/ubuntu-coverage-audit.md) · [Changes since v0.4.1-alpha](https://github.com/Usrnmna/CLI-InteractiveHelpMenu/compare/v0.4.1-alpha...v0.5.0-alpha)
