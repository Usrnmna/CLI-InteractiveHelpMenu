# 7-Zip extraction option audit

The bundled menus for [7z x](../profiles/7z-x.json) and [7zz x](../profiles/7zz-x.json) each contain four switches. Both commands extract files with their archived directory structure. The first filename identifies the archive. Subsequent filenames or patterns select archive members.

## Sources

| Reference | Version | Coverage |
| --- | --- | --- |
| [Upstream release](https://github.com/ip7z/7zip/releases/tag/26.06) and [Linux distribution with HTML manual](https://github.com/ip7z/7zip/releases/download/26.06/7z2606-linux-x64.tar.xz) | 26.06 | In `MANUAL/cmdline`, see `syntax.htm`, `commands/extract_full.htm` and the switch pages `output_dir.htm`, `type.htm`, `yes.htm`, `overwrite.htm` and `bs.htm`. The fixed root help lists `-bd`. |
| Ubuntu 24.04 LTS [7z(1)](https://manpages.ubuntu.com/manpages/noble/man1/7z.1.html) and [7zz(1)](https://manpages.ubuntu.com/manpages/noble/man1/7zz.1.html) | 23.01+dfsg-11 | The 7zz page refers to 7z for switch documentation. Both packages use the same source. |
| Ubuntu 26.04 LTS [7z(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7z.1.html) and [7zz(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7zz.1.html) | 26.00+dfsg-1 | The same division applies. The full 7z executable supports plugins. The standalone 7zz executable uses its built-in handlers. |
| [Upstream command-line parser](https://github.com/ip7z/7zip/blob/24.09/CPP/7zip/UI/Common/ArchiveCommandLine.cpp) | 24.09 | The existing structured guides for `-o` and `-t` use this version. Both switches take an attached, nonempty string. |

## Disposition of the eight entries

The disposition applies to the original wording. Each menu keeps its original order and argument forms.

| Menu | Entry | Disposition | Finding |
| --- | --- | --- | --- |
| `7z x` | `-oDirectory` | Incomplete | Show the current-directory default and a usable attached path such as `-o'out dir'`. Quoting `'-o*'` passes the asterisk to 7-Zip for an output directory named after each archive. |
| `7z x` | `-tType` | Incomplete | Select the input format with an attached value such as `-tzip`. Automatic detection uses the archive extension. `7z i` lists the available handlers. |
| `7z x` | `-y` | Incomplete | Explain the effect of answering yes when a destination file exists. The default overwrite policy replaces it without asking. Explicit `-aos` skips the file even with `-y`. |
| `7z x` | `-bd` | Sufficient as written | Retain “Disable the progress indicator.” Normal output and errors have separate controls. |
| `7zz x` | `-oDirectory` | Incomplete | The standalone build also preserves archived subdirectories under the destination. Supply the path in the same shell argument as `-o`. |
| `7zz x` | `-tType` | Incomplete | The same attached syntax applies. The example uses `7zz i` so the reported formats belong to the executable performing extraction. |
| `7zz x` | `-y` | Incomplete | State the default replacement behavior and the skip-existing alternative. Both are available in the standalone build. |
| `7zz x` | `-bd` | Sufficient as written | Retain the progress-only summary. It accurately describes the standalone build. |

The command headers now describe extraction with directory structure. In the menu, selecting `-oDirectory` or `-tType` inserts only `-o` or `-t` and places the cursor immediately after it. The displayed argument names are placeholders. The review covered ten changed inventory fingerprints across the six revised rows, two headers and two profile files. The versioned value guides and attached-argument metadata still match the pinned parser. [Numerical inventory review](numerical-inventory/review.json)

## Version differences and manual-only coverage

- **Output paths.** All audited versions support the quoted `'-o*'` form. Upstream 26.01 introduced the `-spo` modes, including `-spod` for a literal asterisk in a Linux destination. Both Ubuntu versions predate that switch. The menu shows the common form. [Upstream 26.01 release notes](https://github.com/ip7z/7zip/releases/tag/26.01)
- **Archive types.** A forced type selects the handler for reading. Detection can recognize archive contents even under an unfamiliar extension. The manual also describes top-level-only, nested and parser modes. These qualifiers remain in the manual. The separate `t` command tests archive integrity. [Upstream manual distribution](https://www.7-zip.org/download.html) and [Ubuntu command and switch reference](https://manpages.ubuntu.com/manpages/resolute/man1/7z.1.html)
- **Other extraction controls.** The manual also covers overwrite, skip and auto-renaming modes (`-ao`), member and archive filters (`-i`, `-x`, `-ai`, `-ax`), recursion, passwords, standard input and output, fully qualified paths, checksums and type exclusion. The general switches include output verbosity and routing of messages, errors and progress. These have no selectable rows in either profile. The upstream console help lists `-bd` even though the HTML page for `x` omits it from the extraction switch list. [Upstream console help](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Console/Main.cpp#L156) and [Noble switch reference](https://manpages.ubuntu.com/manpages/noble/man1/7z.1.html)

## Behavior observed on disposable archives

Real Ubuntu package binaries ran against a generated ZIP containing `sub/file.txt` in a private offline sandbox. The tests exercised both `7z` and `7zz` at **23.01** on Ubuntu 24.04 and **26.00** on Ubuntu 26.04. The [Ubuntu packages](https://archive.ubuntu.com/ubuntu/pool/universe/7/7zip/) were unpacked into scratch space.

| Check | Result on all four executable/version combinations |
| --- | --- |
| Destination | Default extraction preserved `sub/file.txt` under the working directory. An attached path containing a space moved the same tree under that directory. With `sample.zip`, the argument `'-oby-name/*'` produced `by-name/sample/sub/file.txt`. All four rejected `-spod`. |
| Format and argument syntax | `-tzip` read the ZIP and `-t7z` rejected it. Automatic detection read the same bytes renamed to `sample.bin`. The `i` command listed ZIP support. Passing either `-o` or `-t` as a separate word from its value failed. |
| Overwrite | Answering no to the default prompt preserved a pre-existing file. `-y` replaced its contents. Combining `-aos` with `-y` preserved them. |
| Progress | A real pseudoterminal displayed percentage progress during ordinary extraction. Adding `-bd` removed that indicator and retained the completion message. Extraction of a missing archive still reported an error and returned failure. |

## Rendered menus and sandbox verification

On each target, Bash/tmux sessions opened the bundled menus with discovery disabled. At 180×72 the checks visited every option, verified the command header, label, summary and Details, and confirmed that `-tType` inserted `-t` directly before an existing suffix. At 60×16 a search for “overwrite” found `-y` in both menus. Scrolling exposed the skip-existing guidance. Cancellation restored the original line and cursor. Reopening the menu and scrolling through `-oDirectory` reached the archive-name example. Selecting it and typing a quoted directory produced `-o'out dir' sample.zip` with the archive operand intact. The executable stubs recorded zero runs. [Terminal regression](../tests/test_syntax_terminal.py)

Browser searches also returned the corresponding row for “output directory”, “archive type” and “progress indicator” in both profiles. Three focused checks passed on each target, covering the minimum-size terminal regression, attached arguments and fixed help routes, and numerical-inventory review. To repeat the terminal check, substitute `host`, `noble310` or `noble312` for TARGET. [Offline sandbox instructions](development.md#isolated-local-debugging)

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_syntax_terminal.py -k extraction_overwrite_and_attached_destination -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,334 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,334 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,334 | 0 | 1 |

The full-suite snapshots included the untracked audit documents. The Windows-specific probe accounted for the single skip on each Linux target.
