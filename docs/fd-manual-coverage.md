# fd and fdfind manual coverage

Each menu grew from 19 to 98 selectable spellings. The 79 additions per executable contribute 158 rows to the bundled total. The two menus implement the same 58 option families. The other 40 spellings include aliases, short help and the fixed one-result shortcut. The original spellings retain their order, insertion text and release-specific value guidance. [fd profile](../profiles/fd.json) · [fdfind profile](../profiles/fdfind.json) · [First-pass audit](fd-option-audit.md)

## Manual inventory

The independent inventory maps each spelling to its operand form and release, including aliases from the tagged argument declarations, documented inverse switches and three hidden controls. The fixed long help exposes 45 option headings on Noble, 47 on Resolute and 49 upstream. The union also includes spellings found only in the prose or parser. The literal `--` marker, repeated `-u`, pattern, search roots, child arguments and template placeholders are documented as syntax. The three releases supply no additional distinct Linux option after reconciliation. [Release inventory, sources and exclusions](fd-manual-inventory.md) · [Fixed help declarations](../tests/fixtures/fd-manual/root-help.json)

The example driver for `fd` now uses only the selected executable’s fixed `--help`. Ubuntu’s separately installed `fd(1)` belongs to fdclone. The `fdfind` driver retains both fixed help and the Ubuntu finder’s `fdfind(1)`. Neither driver runs a pending search to discover its options. Where no driver is loaded and generic discovery is used, the default manual candidate still derives from the executable name. The bundled menus work with discovery disabled. [Discovery routes and manual names](fd-manual-inventory.md#sources-and-discovery)

## Material changes

- **Command ownership.** `-x` runs a child for each match. `-X` passes multiple paths as separate arguments in a batch. With neither an explicit placeholder nor a batch limit, the former appends one path and the latter appends as many paths as fit. Only one batch argument may contain placeholders, but that argument can use several, such as `'{/.}~{/}'`. A quoted semicolon ends the child’s arguments and allows more native finder options. Without it, an option such as `--size` following the child name goes to the child. The editor protects the child region and retains its existing stop at the first positional operand. Native fd also accepts options after a pattern, search root or terminated child. [Execution options and grammar](fd-manual-inventory.md#grammar-and-exclusions)
- **Traversal.** One `-u` includes ignored and hidden entries. Repetition adds no third mode. On both Ubuntu releases a subsequent `--ignore` or `--no-hidden` resets the combined shortcut. From upstream 10.5.1 each inverse resets only its own setting. An explicit `--exclude .git` prunes the directory even with unrestricted search. The menus distinguish Git, fd, ancestor and explicit ignore files, symlink traversal and filesystem boundaries. [Tagged release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md)
- **Matching and filtering.** A literal substring can match a longer name. Upstream `--exact` matches the entire literal name, or the entire absolute path with `--full-path`. Neither Ubuntu package accepts it. A quoted glob without metacharacters matches a whole ordinary name on both. For size bounds, `-S+1k -S-1k` selects exactly 1,000 bytes, whereas `-S1KiB` selects 1,024. Modification-time bounds are strict. Noble requires a supported date or duration in place of the newer `@SECONDS` syntax. [Filter spellings and operands](fd-manual-inventory.md#option-and-spelling-inventory)
- **Output and status.** `-0` changes the record delimiter and preserves embedded newlines. `-1` limits the search to one result without promising which match arrives first. `--quiet` reports a match with status 0 and no match with status 1. An ordinary successful search can return 0 with empty output. Noble accepts only bare `--strip-cwd-prefix`. Resolute and upstream also accept an attached policy. Selecting the row inserts `--strip-cwd-prefix=` with the cursor after the equals sign. Delete the equals sign for the bare switch, or type a policy such as `never` on a release that accepts it. [Ubuntu and upstream sources](fd-manual-inventory.md#sources-and-discovery)

## Disposable executable checks

Ubuntu checks ran the public `usr/bin/fdfind` from the matching amd64 package extracted with `dpkg-deb -x` inside each offline sandbox. A separate Resolute run used the upstream Linux x86-64 musl release’s `fd`. Fixtures used a private Git tree, ignore rules, files with known sizes and UTC modification times, a directory symlink, mixed-case extensions, and a filename containing a newline. Child-command probes wrote JSON arrays from a private Python helper. Array comparisons permit traversal-order differences and preserve individual argument boundaries. [Packaged executable regressions](../tests/test_fd_packaged.py) · [Ubuntu packages](https://archive.ubuntu.com/ubuntu/pool/universe/r/rust-fd-find/) · [Upstream binary release](https://github.com/sharkdp/fd/releases/tag/v10.5.2)

| Probe | Result |
| --- | --- |
| `-H`, `-HI`, `-u`, `-uu`, `-uuu` | Noble omitted `.git/HEAD` with `-H`. Resolute and upstream included it. All three unrestricted spellings admitted the same hidden and ignored fixtures on all builds. `--no-ignore-vcs` admitted the Git-ignored file, and `--no-global-ignore-file` admitted the file excluded by the global fd rules. |
| Matching, types and traversal | `-F r.dot` found both `r.dot` and `r.dot.bak`. The glob `r.dot` selected only the former. Noble rejected `-t dir` with status 2. All builds admitted mixed-case files and a directory with `-s -e .TXT`. With `-L`, the nested file appeared under the real directory and the symlink. |
| Size, ownership and time | Both signed size bounds included the endpoint. The unitless `-S1000` returned 2. The fixture UID and GID matched and a negated UID excluded those files. A timestamp exactly at the local-date cutoff matched neither time comparison. The epoch form gave status 1 on Noble and an empty successful result for equality on Resolute and upstream. |
| Status and bytes | `-0` emitted a path containing its original newline followed by a single NUL byte. `--max-results=0` returned both matches, `-1` returned one and `--has-results` returned 1 with no output for an absent name. `--path-separator :` changed the separators within the path. |
| Output templates and newer flags | Noble rejected `--format`, `--hyperlink`, and an attached strip-prefix policy. Resolute and upstream printed a formatted name, emitted hyperlink escapes with `--hyper=always` and preserved the prefix with `--strip-cwd-prefix=never`. Only upstream accepted a separate dash-leading format, `--exact`, `--ignore-contain`, `--ignore-parent` and the short base-directory spelling `-C`. |
| Per-match or batch arguments | With two empty files and a child argument `--size`, `-x` made two calls. Each received that literal argument and one whole path, including the filename containing a space. `-X` made one call with the flag and two separate paths. A parent `-S1b` after the literal semicolon suppressed all calls. Repeating a terminated command of the same kind ran both. Mixing the kinds or putting batch placeholders in two separate arguments returned 2. A batch capped at one made two calls. An empty result ran no batch. A child exit of 42 gave finder status 1 in both modes. |
| NUL and per-match execution | With two child outputs containing `MATCH`, `-0 -x` produced `MATCHMATCH` on Noble and Resolute. Upstream 10.5.2 wrote a NUL after each child result, including the last. |
| Hidden parser switches | All binaries accepted `--max-buffer-time 0`. With Bash specified or supplied via the fixture environment, `--gen-completions` wrote a Bash completion script. Combining it with a search operand returned 2. The flag depends on the build’s completion feature. |

A separate traversal fixture opened a fresh pseudoterminal on the sandbox’s private devpts mount. A symlink from the temporary search tree led to that mount. All four binary/target combinations found the created terminal by name with `-L`. Adding any of `--one-file-system`, `--mount` or `--xdev` excluded it. Naming the mount as its own search root admitted it again.

## Verification

The focused checks compare the independent inventory and versioned fixed-help declarations with both profiles, including required, optional, attached and variadic forms. They also cover driver routes, numerical diagnostics, both finder menus and literal midline insertion across every bundled profile. The complete suite uses the matching OpenSSH packages on all three targets and the private rsync fixture on Noble. [Inventory regression](../tests/test_fd_manual_inventory.py) · [Sandbox instructions](development.md#isolated-local-debugging) · [OpenSSH fixture setup](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)

At 220×120 the Bash/tmux test selects each row, reads its on-screen label and summary, and compares all displayed Details lines with the formatter. At 60×16 it searches for “batch placeholder”, scrolls to the quoted-semicolon guidance, cancels and checks the exact Readline buffer and cursor. Selecting the same row inserts `--exec-batch` before the original quoted pattern and search root. Moving the cursor to the child’s `--hidden` produces a child-boundary diagnostic. The earlier hidden-directory and quoted-exclusion tests run alongside these checks. Both finder executables and the child have recording stubs. [Complete and narrow-terminal checks](../tests/test_syntax_terminal.py) · [Hidden-path and exclusion checks](../tests/test_expansion_terminal.py)

The systems insertion regression originally expected a space after every selected flag whose name lacked a final equals sign. Three optional policies in each menu explicitly insert that sign. The regression now checks that spelling and the cursor before the original suffix. The strict numerical gate passed all 1,332 required contracts. Review covered 224 added or changed identities, including the profiles, option and value definitions, and the two driver routes. Observations from the original captures were preserved. [Numerical review](numerical-inventory/review.json) · [Insertion and argument-boundary regression](../tests/test_expansion_systems.py)

To repeat the executable checks, include the matching package in the sandbox snapshot and unpack it with `dpkg-deb -x PACKAGE /tmp/fd`. Set `FD_TEST_BINARY=/tmp/fd/usr/bin/fdfind` for the test process. The separate upstream run sets this variable to the unpacked x86-64 musl `fd` executable. Run `env PYTHONPATH=tests python3 -m unittest -v test_fd_packaged` inside the sandbox. Before the new files are tracked, pass one `--include` for each new audit document, test module and fixed-help capture, in addition to the private fixture inputs.

Run the complete focused selection inside the selected sandbox with its package fixture variables set.

```bash
env PYTHONPATH=tests python3 -m unittest -v \
  test_fd_manual_inventory test_fd_packaged test_expansion_systems \
  test_system_dependency_followup test_numerical_diagnostics \
  test_numerical_inventory.NumericalInventoryTests.test_real_source_counts_are_independent_and_reviews_are_complete \
  test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline \
  test_syntax_terminal.SyntaxScreenTests.test_fd_all_rows_and_complete_details \
  test_syntax_terminal.SyntaxScreenTests.test_fd_batch_search_insertion_and_child_boundary_at_minimum_size \
  test_expansion_terminal.ExpansionScreenTests.test_fd_hidden_directory_guidance_and_midline_exclusion
```

The full gate runs `bash tests/run.sh` in a fresh snapshot of the same target and fixture configuration.

## Compatibility results

| Target | Ubuntu | Python | Packaged fdfind | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 10.3.0 | 38 / 0 / 0 | 1,479 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 9.0.0 | 38 / 0 / 0 | 1,479 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 9.0.0 | 38 / 0 / 0 | 1,479 / 0 / 1 |

Across the three targets, the terminal checks inspected 588 selections (98 rows × two menus × three targets). The stubs recorded zero pending-command or child executions. The upstream Linux `fd` 10.5.2 comparator separately passed all four executable regressions on the host target. Each full run skipped only the Windows-specific probe.

The configured Lychee check resolved all 129 link occurrences in the four changed Markdown files, including local heading fragments. A separate check resolved all eight distinct source URLs in the profiles.
