# yq eval option audit

The [bundled menu](../profiles/yq-eval.json) covers 15 spellings for Mike Farah’s yq v4. `eval` runs the expression on each document in input-file order. Use `-` as a filename for standard input. The Ubuntu archive packages named `yq` on both target releases provide Kislyuk’s Python wrapper for jq, which takes a jq filter as its first positional argument. The [eval driver](../config/drivers.example/yq.json) and the menu’s existing executable identity check distinguish the two tools.

## Sources and versions

| Reference | Scope |
| --- | --- |
| [Upstream Evaluate manual](https://mikefarah.gitbook.io/yq/commands/evaluate), [v4.54.3 CLI declarations](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/root.go) and [sequential evaluator](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/evaluate_sequence_command.go) | The manual describes the v4 command. The tagged source and release help establish the flags and behavior for 4.54.3. |
| [v4.44.3 flags](https://github.com/mikefarah/yq/blob/v4.44.3/cmd/root.go), [argument handling](https://github.com/mikefarah/yq/blob/v4.44.3/cmd/utils.go) and [format registry](https://github.com/mikefarah/yq/blob/v4.44.3/pkg/yqlib/format.go) | Pinned release for the structured argument guides. Its defaults and numerical behavior were checked separately. |
| [Ubuntu 24.04 package](https://packages.ubuntu.com/noble/yq), [file list](https://packages.ubuntu.com/noble/all/yq/filelist) and [package archive](https://archive.ubuntu.com/ubuntu/pool/universe/y/yq/yq_3.1.0-3_all.deb) | Noble’s `3.1.0-3` package has no section 1 man page. Its shipped `/usr/share/doc/yq/cli-doc.txt` documents the jq wrapper and the spelling `--in-place`. |
| [Ubuntu 26.04 yq(1)](https://manpages.ubuntu.com/manpages/resolute/man1/yq.1.html) | Resolute’s `3.4.3-2` man page documents the jq wrapper. Neither Ubuntu reference supplies the semantics of Mike Farah’s `eval` options. |

## Disposition of the 15 entries

Each disposition describes the original entry and its value guidance. Rows follow menu order.

| Entry | Disposition | Finding and change |
| --- | --- | --- |
| `--inplace` | Inaccurate | The plural “update input files” suggested one edit per file. The combined result stream replaces the first named file. Later inputs remain intact. Standard input cannot be the destination. |
| `-i` | Inaccurate | The short spelling has the same first-file destination and multi-file behavior. |
| `--null-input` | Incomplete | Run the expression once against null. This can construct a new document. Filenames and an explicit stdin marker are rejected. |
| `-n` | Incomplete | The short spelling also ignores piped data and takes no input filenames. |
| `--exit-status` | Incomplete | An otherwise successful evaluation fails if there are no results or every result is null or the lowercase boolean false. One qualifying result suffices across documents. |
| `-e` | Incomplete | A final false can follow a successful match. Numeric zero, the empty string and the YAML boolean spelled `False` also qualify. |
| `--output-format` | Incomplete | Retain the encoding summary. Automatic output normally follows the first input filename. With an explicit input format, request the desired output format or yq uses YAML. |
| `-o` | Incomplete | Add the same conversion rule. Distinguish the 4.44.3 output encoders from its input decoders and qualify TOML output. |
| `--input-format` | Incomplete | Retain the encoding summary. Automatic selection uses the first filename’s extension and falls back to YAML for stdin and unknown extensions. Specify a decoder for formats such as CSV on stdin. |
| `-p` | Incomplete | Add the same stdin and output interaction. The pinned decoder list excludes the shell output format. |
| `--indent` | Inaccurate | The previous claim that every positive integer produces that many YAML spaces was too broad. State the default and show the release differences for zero, out-of-range widths and negative values. |
| `--prettyPrint` | Incomplete | Describe the effect of clearing styles on the expression result. A flow-style YAML list or map can become a multiline block. |
| `--unwrapScalar` | Incomplete | Describe raw scalar output, the YAML default and the explicit `--unwrapScalar=false` form for retaining quotes and inline comments. |
| `--no-colors` | Sufficient as written | Keep the summary. Details explain terminal versus redirected output and precedence when `--colors` is also set. |
| `--expression` | Redundant | Replace generic menu and grammar commentary with the reason for forcing an expression. A query that also names an existing file needs disambiguation. Quote the expression as one shell argument. |

## Material differences and manual-only coverage

- **In-place writes.** For `yq eval -i '.n += 1' first.yml second.yml`, the first file receives the results for both inputs, in order. A separately updated copy of the second file is never written. The fixed file destination matters even when the expression only selects values. [Sequential evaluation and write destination](https://github.com/mikefarah/yq/blob/v4.44.3/cmd/evaluate_sequence_command.go)
- **Exit status.** The printer remembers whether any printed node qualified. A later null or false does not clear an earlier match. Both versions compare the boolean’s stored text with lowercase `false`. An identity query on the YAML spellings `False` and `FALSE` succeeds. The result test applies after successful evaluation, so parse or file errors can still fail the command. [Result printer](https://github.com/mikefarah/yq/blob/v4.54.3/pkg/yqlib/printer.go) · [Evaluator](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/evaluate_sequence_command.go)
- **Formats and formatting.** Explicit `-p json` with automatic output selects YAML in both versions. Use `-p json -o json` to request JSON explicitly. The 4.44.3 TOML encoder accepts scalar results only. The 4.54.3 registry adds formats such as INI, HCL and KYAML. The upstream pretty-print implementation retains styles on certain ambiguous strings such as `"yes"`. [4.44.3 TOML encoder](https://github.com/mikefarah/yq/blob/v4.44.3/pkg/yqlib/encoder_toml.go) · [4.54.3 format handling](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/utils.go) · [4.54.3 format registry](https://github.com/mikefarah/yq/blob/v4.54.3/pkg/yqlib/format.go) · [Pretty-print expression](https://github.com/mikefarah/yq/blob/v4.54.3/pkg/yqlib/lib.go)
- **Indentation.** In 4.44.3, the YAML encoder uses four spaces at zero and two for positive widths outside 2–9. Its JSON and XML encoders accept nonpositive widths with no indentation spaces. In 4.54.3 the CLI rejects negative widths before encoding and the YAML encoder limits accepted widths to 2–9 for rendering. Zero still produces compact JSON. The pinned value guide remains scoped to 4.44.3. [Pinned YAML emitter](https://github.com/go-yaml/yaml/blob/v3.0.1/emitterc.go) · [4.54.3 argument validation](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/utils.go) · [4.54.3 YAML encoder](https://github.com/mikefarah/yq/blob/v4.54.3/pkg/yqlib/encoder_yaml.go)
- **Outside the menu.** The manuals also cover `eval-all` for evaluating documents together, `--from-file` for an expression stored in a file, `--split-exp` for separate output files, `--no-doc` for suppressing separators and additional short spellings such as `-I`, `-P`, `-r` and `-M`. The menu retains its 15 literal spellings and argument forms. [Upstream Evaluate All manual](https://mikefarah.gitbook.io/yq/commands/evaluate-all) · [Upstream flags](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/root.go)

The numerical inventory review covered the 15 entries, category description, command header and profile file. The expression guide now cites the argument parser. Input and output guides describe their respective format registries and the pinned indentation guide cites the emitter’s width rule. [Inventory review](numerical-inventory/review.json)

## Observed yq behavior

Both upstream Linux amd64 release binaries ran in each of the three offline sandboxes. Their SHA-256 hashes matched the respective upstream release checksums. The fixtures used generated files and standard input in disposable directories. [Release 4.44.3](https://github.com/mikefarah/yq/releases/tag/v4.44.3) · [Release 4.54.3](https://github.com/mikefarah/yq/releases/tag/v4.54.3)

| Fixture | Observed result |
| --- | --- |
| In-place update | Starting with `n: 1` and `n: 2` in two YAML files, `-i '.n += 1'` wrote documents containing 2 and 3 into the first file. The second kept its original bytes. An in-place operation with `-` as the destination failed. An in-place edit with `-e` that selected nothing preserved the original file. |
| Null input and exit status | `-n '.n = 3'` ignored supplied stdin and emitted one mapping. A named input with `-n` failed. For `-e '.'`, true followed by false returned 0. Null followed by false returned 1. No matches returned 1. Zero, an empty string, `False` and `FALSE` each returned 0. |
| Encodings and expression detection | A JSON filename gave JSON output automatically. Explicit `-p json` produced YAML, and adding `-o json` restored JSON. Shell output produced a variable assignment. Mapping-to-TOML conversion failed on 4.44.3 and succeeded on 4.54.3. An expression with the same spelling as an existing filename selected the intended field when passed via `--expression`. |
| Styles and colors | Pretty-printing an inline mapping and list produced block YAML. Explicitly unwrapping a JSON string removed its quotes. Disabling YAML unwrapping preserved the selected string’s quotes and inline comment. Captured output had no ANSI escapes with `--no-colors`. Explicit `--colors` produced escapes even when both flags were supplied. |

For a nested YAML mapping, the following values give the observed leading spaces on the child key. JSON and XML fixtures at zero had no indentation spaces in either release. With negative indentation those two formats still emitted output on 4.44.3 and failed on 4.54.3.

| YAML indentation requested | 4.44.3 | 4.54.3 |
| --- | ---: | ---: |
| `0` | 4 | 2 |
| `1` | 2 | 2 |
| `2` | 2 | 2 |
| `4` | 4 | 4 |
| `10` | 2 | 9 |
| `-1` | Rejected | Rejected |

## Rendered menu and sandbox verification

Each target opened the menu in real Bash/tmux with the example yq driver and automatic discovery enabled. At 200×90 all 15 option labels, summaries and complete Details panes matched the profile and formatter. A wrapper passed only the fixed `--version` and `eval --help` requests to upstream 4.54.3 and recorded any unexpected invocation. The pending command was never executed.

At 60×16 a regression searched for “combined results”, scrolled to the first-file rule and confirmed that cancellation restored the original command line and cursor. A second search selected the literal `--expression`. Typing the quoted expression preserved both filenames to its right. Five focused checks passed on each target, covering this interaction, the executable identity guard, numerical units and indentation, and the inventory review. [Terminal regression](../tests/test_expansion_terminal.py) · [Sandbox instructions](development.md#isolated-local-debugging)

To repeat the terminal regression, substitute `host`, `noble310` or `noble312` for TARGET.

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_expansion_terminal.py -k yq_first_file_warning_and_explicit_expression -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,338 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,338 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,338 | 0 | 1 |

Each full-suite snapshot included the untracked audit documents. The only skip on each target was the Windows-specific probe.
