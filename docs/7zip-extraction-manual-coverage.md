# 7-Zip extraction manual coverage

The `7z x` and `7zz x` menus now distinguish the archives to open, the members to extract, and the action to take when a destination exists. Each menu grew from 4 to 57 selectable rows. The 53 additions per menu contribute 106 bundled rows. The two executable names share the same 57 choices, with build-specific guidance for handlers. The original `-o`, `-t`, `-y` and `-bd` insertions retain their order. [Full 7z profile](../profiles/7z-x.json) · [Standalone 7zz profile](../profiles/7zz-x.json) · [Original four-row audit](7zip-extraction-option-audit.md)

## Manual inventory

The independent inventory gives each spelling, operand form, release scope, reference section and exclusion. It reconciles the 26.06 Linux distribution’s command syntax, extraction pages, switch index and individual switch pages with the Ubuntu Noble and Resolute manuals. Ubuntu packages ship `7z(1)` and a short `7zz(1)` that points to it. The packaged manual header says 22.01 on both releases. The actual binaries report 23.01 and 26.00. [Versioned inventory and sources](7zip-extraction-manual-inventory.md) · [Upstream release](https://github.com/ip7z/7zip/releases/tag/26.06) · [Ubuntu packages](https://archive.ubuntu.com/ubuntu/pool/universe/7/7zip/)

The 57 choices count complete overwrite and output-directory policies individually. Toggle and numeric suffixes such as `-ssc-`, `-r0` and `-bb2` appear in the owning row's guidance. The manual supplies no additional synonym switches for these extraction effects. Examples of other root-help switches are `-mx` for encoding and `-slt` for listings. The Windows security-descriptor and zone operations have no Linux filesystem effect. The original versioned excerpts remain available alongside new complete switch-table captures from the five executable/release combinations. Each capture records the fixed argument, version banner, package and normalization. [Exclusions and grammar](7zip-extraction-manual-inventory.md#grammar-and-excluded-controls) · [Fixed root help](../tests/fixtures/7zip-extraction/root-help.json) · [Original excerpts](../tests/fixtures/help/syntax-7zip-captured.json)

## Material changes

- **Existing files.** Ordinary extraction prompts on a collision. `-y` accepts replacement when there is no explicit overwrite policy. The four `-ao` choices say which file retains its original name and contents. In particular, `-aou` renames the incoming file and `-aot` renames the existing file.
- **Archive versus member.** The first filename normally identifies the archive. Later names and patterns select its members. `-an` removes the archive operand slot, and `-ai` and `-ax` then select archives on disk. `-i` and `-x` act inside them. The menu distinguishes the inline pattern marker in `'-ir!*.txt'` from the list-file marker in `-i@names.txt`. Shell quoting passes the pattern to 7-Zip. A literal `--` ends switch and positional list-file recognition.
- **Streaming and passwords.** `-si` requires a format that can read sequential input. `-so` writes decoded bytes, and selecting several members can join their contents. Normal messages, errors and progress have separate destinations. The general password page describes a bare `-p` prompt. In the console extraction path, the presence of the switch supplies a password even when its value is empty. For a prompt, omit `-p`. [Tagged extraction and update callbacks](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Console/Main.cpp)
- **Paths and releases.** The profiles preserve the 24.09 attached-value guides for `-o` and `-t`. Quoted `'-o*'` uses the archive basename on both Ubuntu releases. Explicit `-spod`, `-spoc` and `-spor` arrived in 26.01. The Linux effects of trailing-dot replacement and large-page controls also depend on the release. Format, reader-property and memory-limit guidance identifies handler dependencies. [26.01 release notes](https://github.com/ip7z/7zip/releases/tag/26.01) · [Versioned switch inventory](7zip-extraction-manual-inventory.md#selectable-inventory)

## Disposable executable checks

All archive operations used new files inside the offline project sandboxes. Each Ubuntu package pair was unpacked under a private directory with `dpkg-deb -x`. The full executable ran beside its packaged `7z.so`, and the standalone executable ran from the same package tree. The upstream Linux x86-64 `7zz` from release 26.06 ran separately on the Resolute target. Fixtures included ZIP members with known bytes, an encrypted 7z archive with a disposable password, a TAR with ordinary links, and gzip and TAR streams. The following observations apply to all five executable/release combinations except where indicated. [Offline sandbox setup](development.md#isolated-local-debugging)

| Fixture or invocation | Observed result |
| --- | --- |
| `x -aoMODE sample.zip sub/name.txt` with an existing `sub/name.txt` | Status 0 for each complete mode, with and without an additional `-y`. `-aoa` left only the new bytes and `-aos` left only the old bytes. With `-aou`, `name.txt` held the old bytes and `name_1.txt` held the new. With `-aot`, the contents were reversed. Answering no at the ordinary collision prompt preserved the destination. |
| `x -so -an '-ai!*.zip' '-ax!other.zip' '-ir!*.txt' '-xr!*.log'` | Status 0. Stdout contained exactly the selected member from `sample.zip`. A positional `@members` and `-i@members` selected that same file. Putting `--` before `@member` selected the archive entry literally named `@member`. |
| `x -spm -so sample.zip sub` and `sub/` | Both returned 0. The first produced zero bytes and the second emitted the nested file. With `-spm2`, the literal unmarked `sub` also selected the file. |
| `x -o'out dir' -tzip sample.zip` and type detection | The destination retained `sub/name.txt`. Automatic detection read the same ZIP bytes under an unfamiliar extension. Forcing 7z or excluding ZIP gave status 2. Separate `-o out` and `-t zip` operands, bare `-ao` and bare `-bs` gave status 7. The literal token `-o=equals` created a directory named `=equals`. |
| `x '-oby-name/*' sample.zip` and output path modes | The common form produced `by-name/sample/sub/name.txt`. With `'-oout/*'`, upstream `-spod` produced `out/*/sub/name.txt`, `-spoc` produced `out/*/sample/sub/name.txt`, and `-spor` produced `out/sample/sub/name.txt`. Both Ubuntu releases returned 7 for each explicit mode. Bare `-spo` returned 7 on all five. |
| `x -p -odest encrypted.7z` versus omission | Bare `-p` returned 2 even with the correct password on stdin. With the switch omitted, 7-Zip prompted, accepted that same input and restored the expected bytes with status 0. A correct attached password worked and a wrong one returned 2. |
| `x -si -ttar -so`, `x -si -tgzip -so`, and `x -si -tzip -so` | TAR and gzip returned the original bytes with status 0. The streamed ZIP returned 2. With `-sifoo.gz -tgzip`, disk extraction created a file named `foo`. |
| `-bd`, `-bso0`, `-bse1`, `-bsp2` and `-scrcSHA256` | A pseudoterminal showed percentage progress without `-bd` and retained the normal completion message with it. `-bso0` suppressed ordinary messages. A missing archive with `-bso0 -bse1` wrote the error to stdout and returned 2. Explicit `-bsp2` sent progress to stderr. The reported digest for a single selected file matched SHA-256 computed over its decoded bytes. |
| Alternate streams, trailing dots and legacy ZIP names | `-snc -snr` extracted `a:b` as `a_b` and `-snc -sns-` omitted it. Only upstream Linux 26.06 converted `trail.` to `trail_` with `-snt`. On Resolute, `-mcp=437` decoded byte 0x82 as é and `-mcp=1252` decoded it as ‚. Both Noble binaries and upstream Linux preserved the raw byte with both code pages. |
| Directory and link entries in a TAR | `-xtd` omitted an empty directory and extracted the selected file under its parent. `-xtf` restored directory records and omitted the file. `-snl-` suppressed symbolic-link creation. With `-snh-`, an explicit TAR hard-link target still shared the original inode. |
| ZIP and XZ reader properties | `-mcp` and `-mcp=` opened the legacy ZIP using the handler’s default OEM code page. `-mcp437` failed with status 2. An XZ stream decoded to the original bytes with either `-mmemuse=2g` or `-mmemuse2g`. An invalid budget returned 2. |
| `i`, `-sni`, `-snz`, `-snld3`, `-smemx128m` and `-slsl-` | Both Ubuntu full clients and upstream standalone listed a RAR handler. Both Ubuntu standalone clients omitted it. The Linux clients parsed the two Windows metadata switches on an ordinary ZIP. Noble rejected the numbered link policy, RAR memory switch and display separator switch with status 7. Resolute and upstream accepted them. With `-bb1 -slsl-`, those builds logged a backslash for the nested member. In a fixed UTC−05 time zone, ordinary collision prompts displayed 19:00 local time and `-slmu` displayed the same instant as 00:00Z the following day. |

Handler registration and argument parsing establish availability. Decoder memory consumption, large-page allocation, ownership changes requiring privileges and Windows filesystem behavior are source-based qualifications. These checks used unprivileged Linux filesystems.

## Verification

Both extraction paths use static profiles. Discovery retains the fixed root `-h` route. Only these profiles opt into 7-Zip switch matching. The editor recognizes the longest declared switch name without regard to ASCII case and preserves existing attached values, including a path beginning with an equals sign. The switch parser protects the `--` boundary. The menu inserts documented spellings and leaves interpretation of handler-specific values to 7-Zip. The command path selected by the menu is lowercase `x`. [Argument-syntax regression](../tests/test_argument_syntax.py) · [Independent inventory regression](../tests/test_7zip_manual_inventory.py)

The rendered checks use real Bash/tmux sessions with discovery disabled and a private executable stub. They compare each selected label, summary and complete formatted Details against terminal cells at 220×120. At 60×16 the checks search for “overwrite” and “rename the existing file”, scroll to the collision outcome and cancel at the original buffer and cursor. Accepting `-aot` retains the quoted archive and member operands. Accepting `-o` and typing a quoted directory yields `-o'out dir'` before those same operands. [Rendered terminal regressions](../tests/test_syntax_terminal.py)

The strict numerical gate passed all 1,234 required contracts. Review covered 130 new or changed inventory identities, including 106 added option rows, category and profile context, and the parser and preservation changes. The prose heuristic flags both `-so` rows for mentioning bytes. Bytes describe the output stream; the switch has no operand or unit to enter. Unrelated inventory observations retained their prior source facts. [Numerical review](numerical-inventory/review.json)

The focused run used the complete argument-syntax, syntax-terminal and extraction inventory modules plus the repository-wide inventory reconciliation test and the all-profile midline insertion test. The first full run exposed an unfinished `--part` token matching the new `--` row as a prefix. Requiring the complete marker restored replacement of that editable word and preserved the boundary after a completed `--`. Each full run used `bash tests/run.sh` with the release-specific OpenSSH fixture and the private rsync binary on Noble. [OpenSSH fixture setup](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)

After the new files are tracked, the focused checks can be repeated with the following command for each target. While the files are untracked, add a separate `--include` before `--` for each new audit document, the inventory test and the root-help capture.

```bash
python3 -I tests/run_sandbox.py --target host -- env PYTHONPATH=tests \
  python3 -m unittest -v test_7zip_manual_inventory test_argument_syntax test_syntax_terminal \
  test_numerical_inventory.NumericalInventoryTests.test_real_source_counts_are_independent_and_reviews_are_complete \
  test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline
```

## Compatibility results

| Target | Ubuntu | Python | 7z / 7zz | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 26.00 / 26.00 | 30 / 0 / 0 | 1,467 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 23.01 / 23.01 | 30 / 0 / 0 | 1,467 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 23.01 / 23.01 | 30 / 0 / 0 | 1,467 / 0 / 1 |

Upstream standalone `7zz` 26.06 also passed the disposable archive checks on the host target. All three targets displayed the 114 rows and their complete Details, restored the original pending line and cursor on cancellation, and recorded zero executions of the pending commands. Each full suite skipped only the Windows-specific probe. Both Linux extraction inventories and their menu Details are complete.

The configured Lychee check resolved all 156 link occurrences across the seven changed Markdown files, including local heading fragments. A separate check resolved all nine distinct source URLs in the two profiles.
