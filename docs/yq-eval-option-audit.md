# yq eval option audit

First recorded 2026-11-22. This first pass covered 15 bundled rows. See the [expanded inventory and verification](yq-eval-manual-coverage.md) for the later manual comparison.

## Sources and versions

| Reference | Scope |
| --- | --- |
| [Upstream Evaluate manual](https://mikefarah.gitbook.io/yq/commands/evaluate), [v4.54.3 CLI declarations](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/root.go) and [sequential evaluator](https://github.com/mikefarah/yq/blob/v4.54.3/cmd/evaluate_sequence_command.go) | The manual describes the v4 command. The tagged source and release help establish the flags and behavior for 4.54.3. |
| [v4.44.3 flags](https://github.com/mikefarah/yq/blob/v4.44.3/cmd/root.go), [argument handling](https://github.com/mikefarah/yq/blob/v4.44.3/cmd/utils.go) and [format registry](https://github.com/mikefarah/yq/blob/v4.44.3/pkg/yqlib/format.go) | Pinned release for the structured argument guides. Its defaults and numerical behavior were checked separately. |
| [Ubuntu 24.04 package](https://packages.ubuntu.com/noble/yq), [file list](https://packages.ubuntu.com/noble/all/yq/filelist) and [package archive](https://archive.ubuntu.com/ubuntu/pool/universe/y/yq/yq_3.1.0-3_all.deb) | Noble’s `3.1.0-3` package has no section 1 man page. Its shipped `/usr/share/doc/yq/cli-doc.txt` documents the jq wrapper and the spelling `--in-place`. |
| [Ubuntu 26.04 yq(1)](https://manpages.ubuntu.com/manpages/resolute/man1/yq.1.html) | Resolute’s `3.4.3-2` man page documents the jq wrapper. Neither Ubuntu reference supplies the semantics of Mike Farah’s `eval` options. |

## Disposition of the 15 entries

The 15 rows covered Mike Farah’s v4 evaluator. The identity check distinguished it from Ubuntu’s jq wrapper. The first-file destination, auto-format selection and indentation behavior required release-specific explanations.

## Material differences and manual-only coverage

In-place mode wrote results for multiple inputs to the first named file. The indentation fixtures below distinguish YAML, XML and JSON behavior in 4.44.3 and 4.54.3.

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

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,338 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,338 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,338 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
