# fzf manual inventory

The three tagged command-line parsers recognize 227 distinct root spellings in total. Of these, 218 implement 191 applicable effects. The bundled menu represents those effects with 209 selectable dash spellings and nine searchable plus aliases. The final section accounts for the other nine parser spellings. The [coverage report](fzf-manual-coverage.md) records release-specific behavior, interactive tests and sandbox results.

## Independent sources

| Release | Manuals and parser | Fixed help and manual headings |
| --- | --- | --- |
| N · Ubuntu 24.04 Noble, amd64 package 0.44.1-1ubuntu0.3 | [Noble fzf(1)](https://manpages.ubuntu.com/manpages/noble/man1/fzf.1.html) and [0.44.1 argument parser](https://raw.githubusercontent.com/junegunn/fzf/0.44.1/src/options.go) | 65 fixed-help declarations containing 75 spellings. The 72 option headings in the manual contain 84 spellings. |
| R · Ubuntu 26.04 Resolute, amd64 package 0.67.0-1 | [Resolute fzf(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fzf.1.html) and [v0.67.0 argument parser](https://raw.githubusercontent.com/junegunn/fzf/v0.67.0/src/options.go) | 110 fixed-help declarations containing 121 spellings. The 119 option headings contain 133 spellings. |
| U · upstream Linux amd64, 0.75.0 | [v0.75.0 manual](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/man/man1/fzf.1), [argument parser](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/options.go) and [release](https://github.com/junegunn/fzf/releases/tag/v0.75.0) | 114 fixed-help declarations containing 125 spellings. The 124 option headings contain 138 spellings. |

The distribution packages' decompressed manual sources match the corresponding upstream tags byte for byte. OPTIONS establishes the public declarations. FIELD INDEX EXPRESSION, EXTENDED SEARCH MODE, KEY/EVENT BINDINGS, ENVIRONMENT VARIABLES and EXIT STATUS explain the operand languages and runtime behavior. The pinned 0.60.3 manual and parser remain the source for the original structured value guides. [Pinned manual](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/man/man1/fzf.1) · [Pinned parser](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/src/options.go)

The three fixed-help captures preserve the declaration text, exact artifact identity, archive checksum and full stdout checksum. The new Noble stdout matches the original 6,322-byte installed-help capture. The original 17-row documentation specimen and its provenance remain separately available. The driver uses the fixed root request `fzf --help`, the manual name `fzf`, and a positional boundary. [Versioned declarations](../tests/fixtures/fzf-manual/root-help.json) · [Original installed help](../tests/fixtures/help/followup-systems/fzf.txt) · [Original capture manifest](../tests/fixtures/help/followup-systems/manifest.json) · [Original specimen](../tests/fixtures/help/fzf.txt) · [Driver](../config/drivers.example/fzf.json)

## Native operand forms

- A required long operand accepts `--option VALUE` or `--option=VALUE`. A required text operand consumes the next word even when that word begins with a dash. Each required short option (`-d`, `-n`, `-q`, `-f`) accepts a separate word or the attached suffix. In `-q=abc` the query includes the equals sign.
- Brackets in the table denote an optional value. Long options can be used bare, with a separate value or with an equals sign. A separate optional string must begin with neither `-` nor `+`. A separate optional integer for `--multi`, `--sort`, `--gap`, `-m` or `-s` must start with a decimal digit. A joined value reaches the option-specific parser directly. The integer parser still decides which inputs are valid. For example, `--multi=-1` and `-m-1` are parsed as limits. In `--multi -1`, the second word is the automatic single-match option. In `--multi +2`, the second word sets the 16-color theme.
- The historical `-s` suffix is ignored after enabling sorting. Noble's parser also takes that compatibility path for `--sort=VALUE`. A separate number on Noble, and either long form on the two newer releases, sets the numeric sort field. A positive field enables score sorting. Use `--no-sort` or `+s` to retain input order across versions.
- The manuals bracket several label and position operands, including `--border-label` and `--preview-label-pos`. The matching parser branches require the text or position. In contrast, the parser accepts a bare `--color` or `--scrollbar` despite declarations that show a value. Resolute accepts bare `--wrap`. Upstream also accepts its optional `char` or `word` mode.
- Fixed help gives zero as the default for `--scroll-off` on all three releases. The defaults in the tagged source agree with the corresponding manuals. Noble keeps zero lines at the list edge. Resolute and upstream keep three.
- `--walker-root` consumes one or more directory operands. An equals value supplies the first root directly. For subsequent separate words the parser tests whether the path is an existing directory and stops on the first other word. `FIELDS` covers the native field-index expression. The later `--with-nth` and `--accept-nth` also accept an output template.

## Option effects and spellings

The first column identifies a parser operation. Equivalent spellings share this identifier, including aliases introduced after Noble. Named shortcuts such as reverse layout and word wrapping count as effects in their own right. Inverses likewise have their own effects. The two listener policies are distinct, though they share a parser branch. Release columns identify where a spelling parses, occurs in a manual option heading or appears in a fixed-help declaration. A dash means no heading in the compared sources. Parser cases and manual prose also establish options, such as the explicitly named TTY device. Multiple lines for one effect identify differences between spellings or versions.

Every spelling beginning with a dash in the second column has a menu row. The nine plus spellings appear in the Details of their long equivalents. The profile validator permits dash-prefixed flags and plain-word keywords. On Noble, `+i` is the operative spelling for case sensitivity. Its long equivalent `--no-ignore-case` starts with the two newer releases. [Profile validator](../cli_help/core.py) · [Bundled fzf profile](../profiles/fzf.json)

| Effect | Native spellings | Operand | Parses | Manual heading | Fixed help |
| --- | --- | --- | --- | --- | --- |
| `--accept-nth` | `--accept-nth` | `FIELDS` | RU | RU | RU |
| `--algo` | `--algo` | `ALGORITHM` | NRU | NRU | — |
| `--ambidouble` | `--ambidouble` | none | RU | RU | — |
| `--ansi` | `--ansi` | none | NRU | NRU | NRU |
| `--bash` | `--bash` | none | RU | RU | RU |
| `--bench` | `--bench` | `DURATION` | U | U | — |
| `--bind` | `--bind` | `BINDINGS` | NRU | NRU | NRU |
| `--black` | `--black` | none | NRU | NRU | — |
| `--bold` | `--bold` | none | NRU | — | — |
| `--border` | `--border` | `[STYLE]` | NRU | NRU | NRU |
| `--border-label` | `--border-label` | `LABEL` | NRU | NRU | NRU |
| `--border-label-pos` | `--border-label-pos` | `COL` | NRU | NRU | NRU |
| `--clear` | `--clear` | none | NRU | — | — |
| `--color` | `--color` | `[COLORS]` | NRU | NRU | NRU |
| `--cycle` | `--cycle` | none | NRU | NRU | NRU |
| `--delimiter` | `-d`, `--delimiter` | `STR` | NRU | NRU | NRU |
| `--disabled` | `--disabled` | none | NRU | NRU | NRU |
| `--disabled` | `--phony` | none | NRU | — | — |
| `--ellipsis` | `--ellipsis` | `STR` | NRU | NRU | NRU |
| `--enabled` | `--enabled`, `--no-phony` | none | NRU | — | — |
| `--exact` | `-e`, `--exact` | none | NRU | NRU | NRU |
| `--exit-0` | `-0`, `--exit-0` | none | NRU | NRU | NRU |
| `--expect` | `--expect` | `KEYS` | NRU | NRU | NRU |
| `--extended` | `-x`, `--extended` | none | NRU | NRU | N |
| `--extended-exact` | `--extended-exact` | none | NRU | — | — |
| `--filepath-word` | `--filepath-word` | none | NRU | NRU | NRU |
| `--filter` | `-f`, `--filter` | `STR` | NRU | NRU | NRU |
| `--fish` | `--fish` | none | RU | RU | RU |
| `--footer` | `--footer` | `STR` | RU | RU | RU |
| `--footer-border` | `--footer-border` | `[STYLE]` | RU | RU | RU |
| `--footer-label` | `--footer-label` | `LABEL` | RU | RU | RU |
| `--footer-label-pos` | `--footer-label-pos` | `COL` | RU | RU | RU |
| `--freeze-left` | `--freeze-left` | `N` | RU | RU | RU |
| `--freeze-right` | `--freeze-right` | `N` | RU | RU | RU |
| `--gap` | `--gap` | `[N]` | RU | RU | RU |
| `--gap-line` | `--gap-line` | `[TEXT]` | RU | RU | RU |
| `--ghost` | `--ghost` | `TEXT` | RU | RU | RU |
| `--gutter` | `--gutter` | `CHAR` | RU | RU | RU |
| `--gutter-raw` | `--gutter-raw` | `CHAR` | RU | RU | RU |
| `--header` | `--header` | `STR` | NRU | NRU | NRU |
| `--header-border` | `--header-border` | `[STYLE]` | RU | RU | RU |
| `--header-first` | `--header-first` | none | NRU | NRU | NRU |
| `--header-label` | `--header-label` | `LABEL` | RU | RU | RU |
| `--header-label-pos` | `--header-label-pos` | `COL` | RU | RU | RU |
| `--header-lines` | `--header-lines` | `N` | NRU | NRU | NRU |
| `--header-lines-border` | `--header-lines-border` | `[STYLE]` | RU | RU | RU |
| `--height` | `--height` | `HEIGHT` | NRU | NRU | NRU |
| `--help` | `--help` | none | NRU | RU | RU |
| `--help` | `-h` | none | NRU | — | — |
| `--highlight-line` | `--highlight-line` | none | RU | RU | RU |
| `--history` | `--history` | `FILE` | NRU | NRU | NRU |
| `--history-size` | `--history-size` | `N` | NRU | NRU | NRU |
| `--hscroll` | `--hscroll` | none | NRU | — | — |
| `--hscroll-off` | `--hscroll-off` | `COLS` | NRU | NRU | NRU |
| `--id-nth` | `--id-nth` | `FIELDS` | U | U | U |
| `--ignore-case` | `-i` | none | NRU | NRU | NRU |
| `--ignore-case` | `--ignore-case` | none | RU | RU | RU |
| `--info` | `--info` | `STYLE` | NRU | NRU | NRU |
| `--info-command` | `--info-command` | `COMMAND` | RU | RU | RU |
| `--inline-info` | `--inline-info` | none | NRU | — | — |
| `--input-border` | `--input-border` | `[STYLE]` | RU | RU | RU |
| `--input-label` | `--input-label` | `LABEL` | RU | RU | RU |
| `--input-label-pos` | `--input-label-pos` | `COL` | RU | RU | RU |
| `--jump-labels` | `--jump-labels` | `CHARS` | NRU | NRU | NRU |
| `--keep-right` | `--keep-right` | none | NRU | NRU | NRU |
| `--layout` | `--layout` | `LAYOUT` | NRU | NRU | NRU |
| `--list-border` | `--list-border` | `[STYLE]` | RU | RU | RU |
| `--list-label` | `--list-label` | `LABEL` | RU | RU | RU |
| `--list-label-pos` | `--list-label-pos` | `COL` | RU | RU | RU |
| `--listen` | `--listen` | `[ADDRESS]` | NRU | NRU | NRU |
| `--listen-unsafe` | `--listen-unsafe` | `[ADDRESS]` | NRU | NRU | — |
| `--literal` | `--literal` | none | NRU | NRU | NRU |
| `--man` | `--man` | none | RU | RU | RU |
| `--margin` | `--margin` | `MARGIN` | NRU | NRU | NRU |
| `--marker` | `--marker` | `STR` | NRU | NRU | NRU |
| `--marker-multi-line` | `--marker-multi-line` | `STR` | RU | RU | RU |
| `--min-height` | `--min-height` | `HEIGHT` | NRU | NRU | NRU |
| `--multi` | `-m`, `--multi` | `[MAX]` | NRU | NRU | NRU |
| `--multi-line` | `--multi-line` | none | RU | — | — |
| `--no-256` | `+2`, `--no-256` | none | NRU | — | — |
| `--no-ambidouble` | `--no-ambidouble` | none | RU | — | — |
| `--no-ansi` | `--no-ansi` | none | NRU | — | — |
| `--no-black` | `--no-black` | none | NRU | — | — |
| `--no-bold` | `--no-bold` | none | NRU | NRU | NRU |
| `--no-border` | `--no-border` | none | NRU | — | — |
| `--no-border-label` | `--no-border-label` | none | NRU | — | — |
| `--no-clear` | `--no-clear` | none | NRU | NRU | — |
| `--no-color` | `--no-color` | none | NRU | RU | RU |
| `--no-color` | `+c` | none | NRU | — | — |
| `--no-cycle` | `--no-cycle` | none | NRU | — | — |
| `--no-exact` | `+e`, `--no-exact` | none | NRU | — | — |
| `--no-exit-0` | `+0`, `--no-exit-0` | none | NRU | — | — |
| `--no-expect` | `--no-expect` | none | NRU | — | — |
| `--no-extended` | `+x`, `--no-extended` | none | NRU | — | RU |
| `--no-filepath-word` | `--no-filepath-word` | none | NRU | — | — |
| `--no-footer` | `--no-footer` | none | RU | — | — |
| `--no-footer-border` | `--no-footer-border` | none | RU | — | — |
| `--no-footer-label` | `--no-footer-label` | none | RU | — | — |
| `--no-gap` | `--no-gap` | none | RU | — | — |
| `--no-gap-line` | `--no-gap-line` | none | RU | — | — |
| `--no-header` | `--no-header` | none | NRU | — | — |
| `--no-header-border` | `--no-header-border` | none | RU | — | — |
| `--no-header-first` | `--no-header-first` | none | NRU | — | — |
| `--no-header-label` | `--no-header-label` | none | RU | — | — |
| `--no-header-lines` | `--no-header-lines` | none | NRU | — | — |
| `--no-header-lines-border` | `--no-header-lines-border` | none | RU | — | — |
| `--no-height` | `--no-height` | none | NRU | — | — |
| `--no-highlight-line` | `--no-highlight-line` | none | RU | — | — |
| `--no-history` | `--no-history` | none | NRU | — | — |
| `--no-hscroll` | `--no-hscroll` | none | NRU | NRU | NRU |
| `--no-id-nth` | `--no-id-nth` | none | U | — | — |
| `--no-ignore-case` | `+i` | none | NRU | NRU | NRU |
| `--no-ignore-case` | `--no-ignore-case` | none | RU | RU | RU |
| `--no-info` | `--no-info` | none | NRU | NRU | — |
| `--no-info-command` | `--no-info-command` | none | RU | — | — |
| `--no-inline-info` | `--no-inline-info` | none | NRU | — | — |
| `--no-input` | `--no-input` | none | RU | RU | RU |
| `--no-input-border` | `--no-input-border` | none | RU | — | — |
| `--no-input-label` | `--no-input-label` | none | RU | — | — |
| `--no-keep-right` | `--no-keep-right` | none | NRU | — | — |
| `--no-list-border` | `--no-list-border` | none | RU | — | — |
| `--no-list-label` | `--no-list-label` | none | RU | — | — |
| `--no-listen` | `--no-listen`, `--no-listen-unsafe` | none | NRU | — | — |
| `--no-literal` | `--no-literal` | none | NRU | — | — |
| `--no-margin` | `--no-margin` | none | NRU | — | — |
| `--no-mouse` | `--no-mouse` | none | NRU | NRU | N |
| `--no-multi` | `+m`, `--no-multi` | none | NRU | NRU | — |
| `--no-multi-line` | `--no-multi-line` | none | RU | RU | RU |
| `--no-padding` | `--no-padding` | none | NRU | — | — |
| `--no-popup` | `--no-tmux` | none | RU | — | — |
| `--no-popup` | `--no-popup` | none | U | — | — |
| `--no-preview` | `--no-preview` | none | NRU | — | — |
| `--no-preview-border` | `--no-preview-border` | none | RU | — | — |
| `--no-preview-label` | `--no-preview-label` | none | NRU | — | — |
| `--no-print-query` | `--no-print-query` | none | NRU | — | — |
| `--no-print0` | `--no-print0` | none | NRU | — | — |
| `--no-raw` | `--no-raw` | none | RU | — | — |
| `--no-read0` | `--no-read0` | none | NRU | — | — |
| `--no-reverse` | `--no-reverse` | none | NRU | — | — |
| `--no-scrollbar` | `--no-scrollbar` | none | NRU | NRU | NRU |
| `--no-select-1` | `+1`, `--no-select-1` | none | NRU | — | — |
| `--no-separator` | `--no-separator` | none | NRU | NRU | NRU |
| `--no-sort` | `+s`, `--no-sort` | none | NRU | NRU | NRU |
| `--no-sync` | `--no-sync`, `--async` | none | NRU | — | — |
| `--no-tac` | `--no-tac` | none | NRU | — | — |
| `--no-tail` | `--no-tail` | none | RU | — | — |
| `--no-track` | `--no-track` | none | NRU | — | — |
| `--no-tty-default` | `--no-tty-default` | none | RU | RU | — |
| `--no-unicode` | `--no-unicode` | none | NRU | NRU | — |
| `--no-wrap` | `--no-wrap` | none | RU | — | — |
| `--no-wrap-word` | `--no-wrap-word` | none | U | — | — |
| `--nth` | `-n`, `--nth` | `FIELDS` | NRU | NRU | NRU |
| `--nushell` | `--nushell` | none | U | U | U |
| `--padding` | `--padding` | `PADDING` | NRU | NRU | NRU |
| `--pointer` | `--pointer` | `STR` | NRU | NRU | NRU |
| `--popup` | `--tmux` | `[OPTS]` | RU | R | RU |
| `--popup` | `--popup` | `[OPTS]` | U | U | U |
| `--preview` | `--preview` | `COMMAND` | NRU | NRU | NRU |
| `--preview-border` | `--preview-border` | `[STYLE]` | RU | RU | RU |
| `--preview-label` | `--preview-label` | `LABEL` | NRU | NRU | NRU |
| `--preview-label-pos` | `--preview-label-pos` | `N` | NRU | NRU | NRU |
| `--preview-window` | `--preview-window` | `LAYOUT` | NRU | NRU | NRU |
| `--preview-wrap-sign` | `--preview-wrap-sign` | `STR` | U | U | U |
| `--print-query` | `--print-query` | none | NRU | NRU | NRU |
| `--print0` | `--print0` | none | NRU | NRU | NRU |
| `--prompt` | `--prompt` | `STR` | NRU | NRU | NRU |
| `--query` | `-q`, `--query` | `STR` | NRU | NRU | NRU |
| `--raw` | `--raw` | none | RU | RU | RU |
| `--read0` | `--read0` | none | NRU | NRU | NRU |
| `--reverse` | `--reverse` | none | NRU | NRU | — |
| `--scheme` | `--scheme` | `SCHEME` | NRU | NRU | NRU |
| `--scroll-off` | `--scroll-off` | `LINES` | NRU | NRU | NRU |
| `--scrollbar` | `--scrollbar` | `[CHARS]` | NRU | NRU | NRU |
| `--select-1` | `-1`, `--select-1` | none | NRU | NRU | NRU |
| `--separator` | `--separator` | `STR` | NRU | NRU | NRU |
| `--smart-case` | `--smart-case` | none | RU | RU | RU |
| `--sort` | `-s`, `--sort` | `[N]` | NRU | — | — |
| `--style` | `--style` | `PRESET` | RU | RU | RU |
| `--sync` | `--sync` | none | NRU | NRU | NRU |
| `--tabstop` | `--tabstop` | `SPACES` | NRU | NRU | NRU |
| `--tac` | `--tac` | none | NRU | NRU | NRU |
| `--tail` | `--tail` | `NUM` | RU | RU | RU |
| `--threads` | `--threads` | `N` | U | U | — |
| `--tiebreak` | `--tiebreak` | `CRITERIA` | NRU | NRU | NRU |
| `--toggle-sort` | `--toggle-sort` | `KEY` | NRU | — | — |
| `--track` | `--track` | none | NRU | NRU | NRU |
| `--tty-default` | `--tty-default` | `DEVICE` | RU | — | — |
| `--unicode` | `--unicode` | none | NRU | — | — |
| `--version` | `--version` | none | NRU | NRU | NRU |
| `--walker` | `--walker` | `OPTS` | RU | RU | RU |
| `--walker-root` | `--walker-root` | `DIR...` | RU | RU | RU |
| `--walker-skip` | `--walker-skip` | `DIRS` | RU | RU | RU |
| `--with-nth` | `--with-nth` | `FIELDS` | NRU | NRU | NRU |
| `--with-shell` | `--with-shell` | `STR` | RU | RU | RU |
| `--wrap` | `--wrap` | `[MODE]` | U | U | U |
| `--wrap` | `--wrap` | none | R | R | R |
| `--wrap-sign` | `--wrap-sign` | `STR` | RU | RU | RU |
| `--wrap-word` | `--wrap-word` | none | U | — | — |
| `--zsh` | `--zsh` | none | RU | RU | RU |

## Exclusions and command boundaries

The nine excluded root spellings have the following dispositions.

| Spelling | Releases | Behavior and scope |
| --- | --- | --- |
| `--` | NRU | The parser ignores this word and continues checking options. fzf reads candidates from its input source. The menu retains its own boundary for editing. |
| `--no-winpty` | RU | The Windows proxy passes this flag to its inner process. Only the Windows implementation reads the setting. [Windows proxy](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/winpty_windows.go) |
| `--force-tty-in`, `--no-force-tty-in`, `--proxy-script PATH` | RU | Undocumented integration plumbing. The Vim plugin can request terminal input for a popup. The proxy launches its inner process with the inverse flag and a generated script path. [Vim integration](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/plugin/fzf.vim) · [Proxy](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/proxy.go) |
| `--profile-cpu FILE`, `--profile-mem FILE`, `--profile-block FILE`, `--profile-mutex FILE` | RU | Developer profiling requires a special `pprof` build. The standard build reports an error when any of these output filenames is set. The developer build guide documents these switches. [Build instructions](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/BUILD.md) · [Standard build check](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/src/options_no_pprof.go) |

Binding actions and events are arguments to `--bind`. Preview placeholders, window layout tokens, query operators, field expressions, theme names and environment variables belong to their respective options or manual sections. Commands embedded in the examples have their own parsers. For example, Noble's `--highlight-line` in a quoted preview command belongs to `bat`. Operating-system shell commands for loading completion scripts are separate from the fzf options that emit those scripts. The manuals describe a general inverse naming convention. Only inverses recognized by a compared parser enter the inventory.
