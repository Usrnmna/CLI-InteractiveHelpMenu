# Mike Farah yq eval option inventory

The menu grew from 15 to **69 selectable spellings** in six categories. There are 51 distinct effects and 18 short aliases. Release 4.44.3 accepts 40 effects with 17 aliases. Release 4.54.3 retains those and adds 11 effects with one further alias. The 54 new rows follow the original 15. Every spelling in the inventory has a row. The first-pass audit supplies the original order and dispositions. [Profile](../profiles/yq-eval.json) · [First-pass audit](yq-eval-option-audit.md) · [Verification](yq-eval-manual-coverage.md)

## Scope and evidence

The upstream Evaluate page describes sequential evaluation, the command alias `e`, and default-command invocation since 4.18.1. The release endpoint identified 4.54.3 as the named comparison for the rolling documentation. The page’s short flag list includes deprecated `-j` and omits many inherited flags. On both releases, only `--help` and its alias are local to the leaf. The remaining rows come from persistent root flags, including the hidden deprecated JSON flag. Root-only `--version` and `-V` belong to the root invocation, such as `yq --version`. `eval-all` evaluates inputs together and has its own command path. Expression operators and encoding names are operands. [Evaluate](https://mikefarah.gitbook.io/yq/commands/evaluate) · [Evaluate All](https://mikefarah.gitbook.io/yq/commands/evaluate-all) · [4.54.3 release](https://github.com/mikefarah/yq/releases/tag/v4.54.3)

| Evidence | What it establishes |
| --- | --- |
| [4.44.3 root flags](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/cmd/root.go), [argument handling](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/cmd/utils.go), [eval](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/cmd/evaluate_sequence_command.go), [format registry](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/pkg/yqlib/format.go), [release help](../tests/fixtures/yq/4.44.3-eval-help.txt) | Registration, operand type, scope, defaults and accepted formats for the release that owns the original structured guides. |
| [4.54.3 root flags](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/root.go), [argument handling](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/utils.go), [eval](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/evaluate_sequence_command.go), [format registry](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/format.go), [release help](../tests/fixtures/yq/4.54.3-eval-help.txt) | Independent comparison against the same declarations, including registrations absent from the earlier release. |
| [Original 15-row fixture](../tests/fixtures/help/yq-eval.txt), [provenance](../tests/fixtures/help/expansion-systems-captured.json), [primary matrix](../tests/fixtures/help/matrix.json) and [expansion matrix](../tests/fixtures/help/expansion-systems.json) | Reduced, independently authored declarations from the manual. These provide representative discovery and editing expectations. |
| [Historical fixed help](../tests/fixtures/help/followup-systems/yq-eval.txt) and [capture manifest](../tests/fixtures/help/followup-systems/manifest.json) | Exit-zero `eval --help` from Mike Farah 4.54.1 on Noble under WSL. It lists 64 spellings. The 4.54.3 capture adds the INI delimiter selector and two security switches for split paths and shell escaping. Both captures omit the two deprecated JSON spellings. |
| [Noble package](https://packages.ubuntu.com/noble/yq), [Noble installed files](https://packages.ubuntu.com/noble/all/yq/filelist), [Resolute yq(1)](https://manpages.ubuntu.com/manpages/resolute/man1/yq.1.html) | Ubuntu ships Kislyuk’s jq wrapper, 3.1.0-3 and 3.4.3-2 respectively. Noble ships `/usr/share/doc/yq/cli-doc.txt` and has no section 1 manual. The wrapper accepts a jq filter and spells in-place editing `--in-place`. Mike Farah uses `--inplace`. The example driver verifies executable identity before requesting help. |

## Effects and spellings

The operand column gives the mandatory value, or **switch** for a boolean. A bare switch enables it. To turn it off, attach `=false` to either spelling, for example `-r=false`. A separate word remains available to the positional parser. A required value accepts a separate word or an equals form. Short options with values also accept an immediately attached operand, as in `-I4`. The menu inserts the selected literal. The operand label describes what the user supplies next. The editor stops offering parent options after the first positional expression or filename, even though the executable also accepts interspersed flags.

“Both” means 4.44.3 and 4.54.3. A dash in the alias column means there is no short alias. Defaults describe the absence of that flag, subject to the format or mode stated. The table reconciles the two tagged CLI declarations with the fixed captures above. A format preference only applies to the relevant decoder or encoder.

| Option | Alias | Operand | Default | Releases | Effect |
| --- | --- | --- | --- | --- | --- |
| `--colors` | `-C` | switch | false | Both | Force colored output |
| `--csv-auto-parse` | — | switch | true | Both | Interpret structured values inside CSV cells |
| `--csv-separator` | — | CHAR | comma | Both | Choose the CSV field delimiter |
| `--debug-node-info` | — | switch | false | 4.54.3 | Print metadata for each selected node |
| `--exit-status` | `-e` | switch | false | Both | Fail on no matches or only null and lowercase false |
| `--expression` | — | EXPRESSION | empty | Both | Set the expression explicitly |
| `--from-file` | — | FILE | empty | Both | Read the query from an expression file |
| `--front-matter` | `-f` | MODE | empty | Both | Evaluate the first input’s YAML front matter |
| `--header-preprocess` | — | switch | true | Both | Collect leading YAML comments and separators |
| `--help` | `-h` | switch | false | Both | Show help for sequential evaluation |
| `--indent` | `-I` | NUMBER | 2 | Both | Set output indentation in spaces |
| `--ini-key-value-delimiters` | — | CHARACTERS | =: | 4.54.3 | Choose the INI input delimiters |
| `--ini-preserve-quotes` | — | switch | false | 4.54.3 | Keep surrounding quotes on INI input values |
| `--inplace` | `-i` | switch | false | Both | Write results back to the first input file |
| `--input-format` | `-p` | FORMAT | auto | Both | Select the input encoding |
| `--lua-globals` | — | switch | false | Both | Write a Lua mapping as global assignments |
| `--lua-prefix` | — | TEXT | `"return "` | Both | Set the prefix for each Lua output document |
| `--lua-suffix` | — | TEXT | `";\n"` | Both | Set the suffix for each Lua output document |
| `--lua-unquoted` | — | switch | false | Both | Write eligible Lua table keys without quotes |
| `--no-colors` | `-M` | switch | false (also honors NO_COLOR in 4.54.3) | Both | Disable colored output |
| `--no-doc` | `-N` | switch | false | Both | Suppress YAML document separators |
| `--nul-output` | `-0` | switch | false | Both | End each result with a NUL byte |
| `--null-input` | `-n` | switch | false | Both | Evaluate once with null as the input |
| `--output-format` | `-o` | FORMAT | auto | Both | Select the output encoding |
| `--prettyPrint` | `-P` | switch | false | Both | Reset YAML styles for block output |
| `--properties-array-brackets` | — | switch | false | Both | Use brackets for properties array indices |
| `--properties-separator` | — | TEXT | `" = "` | Both | Set the properties output separator |
| `--security-allow-write-any-path` | — | switch | false | 4.54.3 | Allow split output outside the working directory |
| `--security-disable-env-ops` | — | switch | false | 4.54.3 | Block environment access from yq expressions |
| `--security-disable-file-ops` | — | switch | false | 4.54.3 | Block file operations in yq expressions |
| `--security-enable-system-operator` | — | switch | false | 4.54.3 | Allow expressions to run external commands |
| `--security-force-never-escape-shell-output` | — | switch | false | 4.54.3 | Disable quoting of unwrapped shell output |
| `--shell-key-separator` | — | TEXT | `"_"` | 4.54.3 | Join nested shell variable names with a separator |
| `--split-exp` | `-s` | EXPRESSION | empty | Both | Write each result to a computed filename |
| `--split-exp-file` | — | FILE | empty | Both | Read the output naming expression from a file |
| `--string-interpolation` | — | switch | true | Both | Expand expressions inside quoted yq strings |
| `--tojson` | `-j` | switch | false | Both | Encode results as JSON |
| `--tsv-auto-parse` | — | switch | true | Both | Interpret structured values inside TSV cells |
| `--unwrapScalar` | `-r` | switch | true for YAML and properties | Both | Print a scalar as its raw value |
| `--verbose` | `-v` | switch | false | Both | Write debug diagnostics to standard error |
| `--xml-attribute-prefix` | — | TEXT | `"+@"` | Both | Choose the key prefix for XML attributes |
| `--xml-content-name` | — | KEY | `"+content"` | Both | Name the key holding XML element text |
| `--xml-directive-name` | — | KEY | `"+directive"` | Both | Name the key for XML directives |
| `--xml-keep-namespace` | — | switch | true | Both | Keep namespaces in decoded XML names |
| `--xml-proc-inst-prefix` | — | TEXT | `"+p_"` | Both | Choose the key prefix for XML processing instructions |
| `--xml-raw-token` | — | switch | true | Both | Read XML tokens without namespace translation |
| `--xml-skip-directives` | — | switch | false | Both | Discard XML directives on input |
| `--xml-skip-proc-inst` | — | switch | false | Both | Discard XML processing instructions on input |
| `--xml-strict-mode` | — | switch | false | Both | Enable strict XML decoding |
| `--yaml-compact-seq-indent` | `-c` | switch | false | 4.54.3 | Count the list marker toward YAML indentation |
| `--yaml-fix-merge-anchor-to-spec` | — | switch | false | 4.54.3 | Apply YAML merge-key precedence |

## Formats and release differences

For both pins the bidirectional format families are YAML (`yaml/y/yml`), JSON (`json/j`), properties (`props/p/properties`), CSV (`csv/c`), TSV (`tsv/t`), XML (`xml/x`), `base64`, `uri`, `toml` and Lua (`lua/l`) in builds with those components. Version 4.54.3 also registers `kyaml/ky`, `base64url`, `hcl/h/tf` and `ini/i` in both directions. KYAML input uses the YAML decoder. The only named output-only family is `shell/s/sh`. Neither registry has a named decoder-only family. The displayed format lists give just the first alias per family. Both pins accept `auto/a` at the CLI. The 4.44.3 TOML encoder handles only scalar results. [4.44.3 registry](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/pkg/yqlib/format.go) · [4.54.3 registry](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/format.go) · [4.44.3 TOML encoder](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/pkg/yqlib/encoder_toml.go)

An automatic input format follows the first filename extension, with YAML as the fallback for stdin and unknown extensions. Automatic output follows detected input. An explicit input decoder with automatic output selects YAML for backward compatibility. Use both `-p` and `-o` to specify a conversion. The original indentation guide is pinned to 4.44.3. Version 4.54.3 clamps YAML widths to 2–9 and rejects negative widths before encoding. Zero still selects compact JSON. [4.44.3 format setup](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/cmd/utils.go) · [4.54.3 format setup](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/cmd/utils.go) · [Original indentation fixtures](yq-eval-option-audit.md#observed-yq-behavior)

Both pins read Lua tables from stdin in the tested official builds. A mapping converted to TOML on 4.54.3, while 4.44.3 returned a scalar-only diagnostic. Supplying the output-only shell format as input failed on both releases. The 4.44.3 executable exited with status 2 and a runtime diagnostic. Version 4.54.3 reported an unsupported decoder and exited with status 1.

Format-specific Details follow the implementations. For example, disabling CSV/TSV auto-parsing keeps structured cells as text while still allowing plain scalar typing. Lua global assignments require a top-level mapping and omit the document prefix and suffix. The 4.54.3 debug printer emits node metadata and ignores the NUL-framing setting. The merge-anchor flag still defaults to false in the 4.54.3 executable, despite a forecast in its help. [CSV decoder](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/decoder_csv_object.go) · [Lua encoder](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/encoder_lua.go) · [Node metadata printer](https://raw.githubusercontent.com/mikefarah/yq/v4.54.3/pkg/yqlib/printer_node_info.go) · [4.54.3 fixed help](../tests/fixtures/yq/4.54.3-eval-help.txt)
