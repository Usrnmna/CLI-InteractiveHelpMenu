# fzf manual coverage

The root menu covers **191 distinct effects**. Its 209 selectable spellings comprise the original 17 and 192 additions. Nine additional short inverses beginning with `+` are searchable in the Details for the corresponding dash spelling. The independent inventory accounts for nine excluded spellings, including popup plumbing and build-dependent profiling controls. [Release inventory](fzf-manual-inventory.md) · [First-pass audit](fzf-option-audit.md) · [Bundled profile](../profiles/fzf.json)

## Sources and scope

The Ubuntu releases compared here are Noble **0.44.1-1ubuntu0.3** and Resolute **0.67.0-1**. The upstream reference is **0.75.0**. Searches, field expressions, initial selection, exit status, layout, bindings and placeholders are described in each release's `fzf(1)`. The options parser establishes operand consumption and accepted compatibility spellings. The existing structured guides retain their **0.60.3** provenance. [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/fzf.1.html) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/fzf.1.html) · [Upstream manual](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/man/man1/fzf.1) · [Pinned parser](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/src/options.go)

The example driver uses fixed root `--help` and the `fzf` manual. The editor stops at the first positional argument and at `--`. Native fzf ignores the standalone `--` in its option loop. Action names, key bindings, preview placeholders, query operators and walker settings are documented under the options that consume them. Printed shell integration has a separate entry for each supported shell. [Driver](../config/drivers.example/fzf.json) · [Upstream parser](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/options.go)

For a separate optional integer, the editor recognizes digits after switches such as `-m`. For optional text, use a joined form such as `--border=sharp` to keep browsing after that option. Native fzf also accepts `--border sharp`, but the editor treats the separate word as a positional boundary. Type a plus alias directly to use that spelling. The menu inserts its selectable dash equivalent. On Noble, use `+i` directly for case-sensitive matching because that release rejects `--no-ignore-case`. [Operand forms and release inventory](fzf-manual-inventory.md#native-operand-forms) · [Editor context rules](../cli_help/core.py)

For the upstream-only `--threads`, the 0.75.0 manual gives a default of `min(8 × CPU count, 32)`. The tagged parser accepts zero and passes it to the matcher. On that path `NewMatcher` uses Go’s available CPU count, and the scan starts at most one worker per input chunk. The Details follow this implementation. The executable probe confirmed acceptance of zero. Worker counts come from source inspection. [Upstream manual](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/man/man1/fzf.1) · [Matcher construction and scan](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/matcher.go)

## Release behavior on disposable input

The following observations come from real binaries under private homes in offline project sandboxes. The test sets fzf defaults explicitly, supplies every input record and uses separate tmux sockets for interaction. The upstream Linux amd64 release was run separately from the Ubuntu packages. [Executable regressions](../tests/test_fzf_packaged.py) · [Ubuntu package archive](https://archive.ubuntu.com/ubuntu/pool/universe/f/fzf/) · [Upstream release](https://github.com/junegunn/fzf/releases/tag/v0.75.0)

| Probe | Observed result |
| --- | --- |
| Display, match, accept | Input contained `ID7:apple:red` and `ID8:pear:apple`. With `-d: --with-nth 2.. --nth 1 --query apple`, all three releases displayed only `apple:red` as a match. Enter emitted `b'ID7:apple:red\n'`. Resolute and upstream emitted `b'ID7\n'` with `--accept-nth=1` and `b'0=red/ID7\n'` with `--accept-nth '{n}={3}/{1}'`. Noble rejected the output projection with status 2. |
| Filter output after display transformation | Replacing the interactive query with `--filter apple` emitted `b'ID7:apple:red\n'` with default sorting. Adding `--no-sort` emitted `b'apple:red\n'` on both Ubuntu builds and `b'ID7:apple:red\n'` on upstream. Resolute accepted `--accept-nth=1` in both filter paths and left those bytes unchanged. Upstream emitted `b'ID7\n'` in both. |
| Filter and record delimiters | From `cat`, `scatter`, `cXaXt` and `dog`, fuzzy `cat` matched three items, exact `cat` matched two, and `^cat$` matched one. A missing filter returned 1 with empty stdout. Given `b'cat\nname\0dog\0'`, filtering for `cat` with `--read0` produced `b'cat\nname\n'`. Adding `--print0` produced `b'cat\nname\0'`. |
| Automatic selection and exit | With zero initial matches, `-0` exited automatically with empty stdout and status 1. With one initial match, `-1` emitted it with a newline and exited 0. Each switch opened the finder for the other match counts, including multiple matches. Escape from the empty finder returned 130. The long spellings behaved identically. |
| Multiple selection | Two Tab presses and Enter emitted both marked lines with bare `-m` or `--multi`, and with a limit of two. Zero or one, supplied separately or joined, yielded one line. Joined `--multi=-1` and `-m-1` also yielded one. A separate `-1` is itself the select-one switch, and a separate `+1` cancels that switch. Both left multiple marking enabled. |
| Case and ranking | All three binaries matched `LOWER` against `lowercase` with `-i` and returned status 1 with `+i`. Noble returned 2 for the named case policies. In a ranking fixture, Noble kept sorting with `--sort=0` but preserved input order with `--sort 0`. Resolute and upstream preserved input order with both long forms. All three kept sorting with `-s0`. |
| Delimiter and height | With `a.ok`, a dot delimiter and a filter on field two, Noble found no match. The later binaries matched. `-d'[.]'` matched on all three. All accepted `10`, `45.5%` and `~40%` for height. Resolute and upstream accepted `-2`. Only upstream accepted `~-2`. Rejected heights returned 2. |
| Preview, headers and actions | A fixed header and the first input record used as a header appeared beside two selectable records. A recording preview ran for the initially highlighted row and again when the highlight moved. A bound reload called the helper and replaced the records. A separate bound key ran the helper for the new row and then accepted it, emitting `b'new:red\n'`. |

The Ubuntu filter implementations print the displayed text on their streaming path. Disabling sorting enables that path when reversal and synchronous input are also off. Their sorted path retrieves the original record. Upstream 0.75.0 uses the same output transformation in both paths. [Noble filter implementation, lines 146–179](https://raw.githubusercontent.com/junegunn/fzf/0.44.1/src/core.go) · [Resolute filter implementation, lines 238–275](https://raw.githubusercontent.com/junegunn/fzf/v0.67.0/src/core.go) · [Upstream filter implementation, lines 261–284](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/core.go)

## Verification

At 220×120 a real Bash/tmux session with discovery disabled selected every row in all ten categories. The test compared the selected label, summary and complete formatted Details with the terminal cells. At 60×16 it opened the unfiltered menu, searched for “output fields”, scrolled to the original-input numbering rule and pressed Escape. The exact Readline buffer and cursor were restored. Selecting the same row and typing `3` produced `fzf --accept-nth 3 --query 'some text'`, with the cursor before `--query`. The literal-dot test retained its separate quoted delimiter check. The recording fzf stub received zero calls. [Every-row and output-field terminal checks](../tests/test_syntax_terminal.py) · [Literal-dot regression](../tests/test_expansion_terminal.py)

The numerical review examined 211 new or changed identities. It retained the external capture observations for `-0` and `-1` and recorded each as a verified fixed match count. The strict gate passed all 1,409 required contracts. The focused run also checked midline insertion for every bundled option across all 76 profiles. A separate run on the host target passed all eight executable regressions against upstream fzf 0.75.0 (`c7bf2b8e`). [Review fingerprints](numerical-inventory/review.json) · [Fixed-digit regression](../tests/test_numerical_diagnostics.py) · [All-profile insertion test](../tests/test_functional_matrix.py)

An initial full run exposed a regression assertion that searched for every current option in the single Noble help capture. The historical assertion now checks the original 17 curated spellings against both the current menu and the unchanged capture. The release-inventory test checks the expanded menu against all three sources, including spellings absent from Noble help. [Historical capture regression](../tests/test_system_dependency_followup.py) · [Cross-release inventory regression](../tests/test_fzf_manual_inventory.py)

The executable tests use `FZF_TEST_BINARY` to identify the release. For an Ubuntu client, include the matching amd64 package with the sandbox runner and unpack it inside the sandbox with `dpkg-deb -x PACKAGE /tmp/fzf-package`. Set `FZF_TEST_BINARY=/tmp/fzf-package/usr/bin/fzf`. The upstream comparison uses the executable unpacked from the release archive. The full offline suite also requires the documented fd, OpenSSH and Noble rsync fixtures to exercise their packaged tests. [Sandbox instructions](development.md#isolated-local-debugging) · [fd fixture](fd-manual-coverage.md#verification) · [OpenSSH fixtures](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)

Use `python3 -I tests/run_sandbox.py --target TARGET` with one `--include FILE` per untracked audit, Python test, fixed-help fixture and target-specific package input. After `--`, run the fixture setup and the following focused selection inside that sandbox. Run `bash tests/run.sh` in a fresh snapshot with the same fixtures for the full suite.

```bash
env PYTHONPATH=tests python3 -m unittest -v \
  test_fzf_manual_inventory \
  test_fzf_packaged \
  test_expansion_systems \
  test_system_dependency_followup \
  test_numerical_diagnostics \
  test_numerical_inventory.NumericalInventoryTests.test_real_source_counts_are_independent_and_reviews_are_complete \
  test_numerical_migration.NumericalMigrationTests.test_counts_indices_levels_percentages_and_defaults \
  test_numerical_presentation.NumericalPresentationTests.test_reference_counts_indices_levels_percentages_and_identifiers \
  test_functional_matrix.InsertionContractTests.test_every_bundled_option_inserts_exactly_midline \
  test_syntax_terminal.SyntaxScreenTests.test_fzf_output_fields_before_quoted_query_at_minimum_size \
  test_expansion_terminal.ExpansionScreenTests.test_fzf_literal_dot_delimiter_at_minimum_size \
  test_syntax_terminal.SyntaxScreenTests.test_fzf_all_rows_and_complete_details
```

## Compatibility results

| Target | Ubuntu | Python | Packaged fzf | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 0.67.0 | 44 / 0 / 0 | 1,493 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 0.44.1 | 44 / 0 / 0 | 1,493 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 0.44.1 | 44 / 0 / 0 | 1,493 / 0 / 1 |

Each full suite skipped only the Windows-specific probe. The three rendered-menu runs inspected 627 selections in total. The release inventory accounts for every applicable root effect across the three reviewed parsers.

The configured Lychee checker resolved all 145 link occurrences across the four changed Markdown files, including local heading fragments. A separate pass resolved all six distinct source URLs in the profile.
