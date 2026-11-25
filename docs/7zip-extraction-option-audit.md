# 7-Zip extraction option audit

First recorded 2026-11-22. This first pass covered 8 bundled rows. See the [expanded inventory and verification](7zip-extraction-manual-coverage.md) for the later manual comparison.

## Sources

| Reference | Version | Coverage |
| --- | --- | --- |
| [Upstream release](https://github.com/ip7z/7zip/releases/tag/26.06) and [Linux distribution with HTML manual](https://github.com/ip7z/7zip/releases/download/26.06/7z2606-linux-x64.tar.xz) | 26.06 | In `MANUAL/cmdline`, see `syntax.htm`, `commands/extract_full.htm` and the switch pages `output_dir.htm`, `type.htm`, `yes.htm`, `overwrite.htm` and `bs.htm`. The fixed root help lists `-bd`. |
| Ubuntu 24.04 LTS [7z(1)](https://manpages.ubuntu.com/manpages/noble/man1/7z.1.html) and [7zz(1)](https://manpages.ubuntu.com/manpages/noble/man1/7zz.1.html) | 23.01+dfsg-11 | The 7zz page refers to 7z for switch documentation. Both packages use the same source. |
| Ubuntu 26.04 LTS [7z(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7z.1.html) and [7zz(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7zz.1.html) | 26.00+dfsg-1 | The same division applies. The full 7z executable supports plugins. The standalone 7zz executable uses its built-in handlers. |
| [Upstream command-line parser](https://github.com/ip7z/7zip/blob/24.09/CPP/7zip/UI/Common/ArchiveCommandLine.cpp) | 24.09 | The existing structured guides for `-o` and `-t` use this version. Both switches take an attached, nonempty string. |

## Disposition of the eight entries

The two four-row menus covered overwrite, progress, archive type and destination controls. The type and directory rows insert a prefix and leave the cursor ready for an attached value.

## Version differences and manual-only coverage

The quoted output template `'-o*'` worked across the audited editions. Upstream 26.01 added explicit path modes, including `-spod` for a literal asterisk on Linux. Both Ubuntu packages predated those modes.

## Behavior observed on disposable archives

Real Ubuntu package binaries ran against a generated ZIP containing `sub/file.txt` in a private offline sandbox. The tests exercised both `7z` and `7zz` at **23.01** on Ubuntu 24.04 and **26.00** on Ubuntu 26.04. The [Ubuntu packages](https://archive.ubuntu.com/ubuntu/pool/universe/7/7zip/) were unpacked into scratch space.

| Check | Result on all four executable/version combinations |
| --- | --- |
| Destination | Default extraction preserved `sub/file.txt` under the working directory. An attached path containing a space moved the same tree under that directory. With `sample.zip`, the argument `'-oby-name/*'` produced `by-name/sample/sub/file.txt`. All four rejected `-spod`. |
| Format and argument syntax | `-tzip` read the ZIP and `-t7z` rejected it. Automatic detection read the same bytes renamed to `sample.bin`. The `i` command listed ZIP support. Passing either `-o` or `-t` as a separate word from its value failed. |
| Overwrite | Answering no to the default prompt preserved a pre-existing file. `-y` replaced its contents. Combining `-aos` with `-y` preserved them. |
| Progress | A real pseudoterminal displayed percentage progress during ordinary extraction. Adding `-bd` removed that indicator and retained the completion message. Extraction of a missing archive still reported an error and returned failure. |

## Rendered menus and sandbox verification

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_syntax_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,334 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,334 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,334 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
