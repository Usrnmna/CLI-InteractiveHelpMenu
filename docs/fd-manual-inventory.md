# fd and fdfind manual inventory

The same inventory applies to both menus. Noble uses fd-find **9.0.0-1**, Resolute uses **10.3.0-2ubuntu1**, and the upstream reference is **10.5.2**. Each Ubuntu package supplies a public `/usr/bin/fdfind` symlink, its target `/usr/lib/cargo/bin/fd`, and `fdfind(1)`. The independent sources below establish the option names and operand forms. The [coverage report](fd-manual-coverage.md) records measured behavior and terminal results.

## Sources and discovery

| Source | Scope |
| --- | --- |
| [Upstream release](https://github.com/sharkdp/fd/releases/tag/v10.5.2) and [fd(1)](https://github.com/sharkdp/fd/blob/v10.5.2/doc/fd.1) | DESCRIPTION and OPTIONS supply the pattern and root grammar and the user-facing declarations. PATTERN SYNTAX, ENVIRONMENT, FILES, and EXAMPLES qualify how they work. |
| [Noble fdfind(1)](https://manpages.ubuntu.com/manpages/noble/man1/fdfind.1.html) and [Resolute fdfind(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fdfind.1.html) | The packaged OPTIONS sections have 45 and 47 headings respectively, counting the separate heading for `-1`. The upstream manual has 49. Aliases in prose and hidden overrides supplement those headings. |
| [9.0.0 CLI](https://github.com/sharkdp/fd/blob/v9.0.0/src/cli.rs), [10.3.0 CLI](https://github.com/sharkdp/fd/blob/v10.3.0/src/cli.rs), [10.5.2 CLI](https://github.com/sharkdp/fd/blob/v10.5.2/src/cli.rs) and [release history](https://github.com/sharkdp/fd/blob/v10.5.2/CHANGELOG.md) | `Opts` supplies aliases, conflicts, hidden options and build-dependent completions. `Exec::augment_args` declares variadic child arguments and their terminator. `FileType` declares the accepted type names. |
| [Versioned fixed help](../tests/fixtures/fd-manual/root-help.json) and [original installed-help manifest](../tests/fixtures/help/followup-systems/manifest.json) | The new captures preserve fixed `--help` declaration lines for the two Ubuntu packages and upstream Linux release. The older Ubuntu 9.0.0 captures retain their complete original text and request spelling. The [original 19-row specimens](../tests/fixtures/help/expansion-systems-captured.json) are documentation-derived examples. |
| [10.2.0 manual](https://github.com/sharkdp/fd/blob/v10.2.0/doc/fd.1) and [parser](https://github.com/sharkdp/fd/blob/v10.2.0/src/cli.rs) | Baseline for the structured guides on the pre-existing rows. Their release provenance remains separate from the three inventory versions. |

The [fd driver](../config/drivers.example/fd.json) and [fdfind driver](../config/drivers.example/fdfind.json) specify fixed root help requests. The fd driver uses only `fd --help`. Its manual-only mode has no configured source. The fdfind driver permits both `fdfind --help` and a section 1 or 8 lookup of `fdfind`. These fixed help requests describe whichever executable of that name resolves on the search path. Neither request establishes that the program and the separately resolved man page came from the same distribution. Ubuntu's `fdfind(1)` is appropriate for the packaged finder. Its `fd(1)` instead resolves to the fdclone package, 3.01j-1 on Noble and 3.01j-1.1 on Resolute. Both web pages identify the shell for fdclone. An upstream installation can supply the intended sharkdp `fd(1)` under that same name. With the example drivers disabled, generic root discovery can still request the same-name manual. Static profiles with discovery off use neither source. [Noble fd(1)](https://manpages.ubuntu.com/manpages/noble/man1/fd.1.html) · [Resolute fd(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fd.1.html)

## Option and spelling inventory

The 98 selectable spellings cover 58 option families. Counting treats the fixed one-result shortcut as part of the result-limit family and the long and short help displays as one help family. All inverse operations have their own families.

Every backticked spelling in the first column has its own selectable row in each profile. Separate rows in this table can share an effect when release availability or operand syntax differs. “All” includes the three release builds above. “10.3+” means Resolute and the upstream release in this comparison. “10.5” means only the upstream release in this comparison. The operand column gives the native grammar. A required long value accepts a separate word or an equals sign and a required short value also accepts an attached suffix. Brackets denote an optional operand. The operand and its brackets are never literal insertion text.

| Selectable spellings | Operand | Releases | Source qualification |
| --- | --- | --- | --- |
| `--hidden`, `-H` | none | All | Admit hidden names while retaining active ignore rules. The default exclusion of the Git directory under this switch changed in 10.0. |
| `--no-hidden` | none | All | Documented in the hidden-option prose. Restores normal hidden-name filtering. |
| `--no-ignore`, `-I` | none | All | Disable standard ignore files. Explicit exclusion patterns still apply. |
| `--ignore` | none | All | Restore standard ignore-file processing. |
| `--no-ignore-vcs` | none | All | Disable Git's ignore rules. Other ignore sources still apply. |
| `--ignore-vcs` | none | All | Restore Git ignore processing after its inverse. |
| `--no-require-git` | none | All | Apply Git ignore rules outside a detected repository. |
| `--require-git` | none | All | Restore the repository requirement. |
| `--no-ignore-parent` | none | All | Skip ignore files inherited from parent directories. |
| `--ignore-parent` | none | 10.5 | Hidden inverse in the 10.5.2 parser, introduced in 10.5.0. |
| `--no-global-ignore-file` | none | All | Hidden parser switch for fd’s own global ignore file. Git's global ignore is a separate rule source. |
| `--unrestricted`, `-u` | none | All | Combined hidden and no-ignore search. Repeating the short switch adds no third mode. From 10.5.1 an inverse after it can cancel just one half. |
| `--case-sensitive`, `-s` | none | All | Override smart case. |
| `--ignore-case`, `-i` | none | All | Force case folding including for uppercase patterns. |
| `--glob`, `-g` | none | All | Whole-name glob matching. Shell metacharacters need quoting. |
| `--regex` | none | All | Restore the default regex matching mode after a glob setting. |
| `--fixed-strings`, `-F`, `--literal` | none | All | Literal substring matching. The tagged parser declares the final alias. |
| `--exact` | none | 10.5 | Whole-name or whole-path literal comparison. Introduced in 10.5.0. |
| `--and` | PATTERN | All | Require each additional search expression to match. Repeat once per expression. |
| `--absolute-path`, `-a` | none | All | Print absolute paths. |
| `--relative-path` | none | All | Cancel the absolute-output option. |
| `--list-details`, `-l` | none | All | Delegate a detailed listing to a platform listing program. |
| `--follow`, `-L`, `--dereference` | none | All | Follow directory symlinks. The parser supplies the dereference alias. |
| `--no-follow` | none | All | Restore ordinary symlink traversal policy. |
| `--full-path`, `-p` | none | All | Apply the search pattern to the absolute path. |
| `--print0`, `-0` | none | All | Use a NUL record delimiter. |
| `--max-results` | COUNT | All | Bound the number of results. |
| `-1` | none | All | Fixed `--max-results=1` shortcut. The parser has no general negative-digit result-count switch. |
| `--quiet`, `-q`, `--has-results` | none | All | Test for matches by status, with no result list. |
| `--show-errors` | none | All | Display filesystem traversal errors. |
| `--strip-cwd-prefix` | [=WHEN] | All | Noble accepts only the bare switch. Later builds also accept an optional equals value. |
| `--one-file-system`, `--mount`, `--xdev` | none | All | Restrict traversal to the starting filesystem. |
| `--help`, `-h` | none | All | Long help is detailed and short help is a summary. |
| `--version`, `-V` | none | All | Report the executable version. |
| `--max-depth`, `-d`, `--maxdepth` | DEPTH | All | Maximum traversal depth. The last spelling is a parser alias. |
| `--min-depth` | DEPTH | All | Minimum depth of returned entries. |
| `--mindepth` | DEPTH | 10.3+ | Parser alias for minimum depth. |
| `--exact-depth` | DEPTH | All | Set both depth limits together. |
| `--prune` | none | All | Stop descending into directories that match the search. |
| `--type`, `-t` | TYPE | All | Repeatable type filter. Noble accepts `d` and `directory`. The alias `dir` appears in the later parsers. |
| `--extension`, `-e` | EXT | All | Repeatable case-insensitive extension filter. Can select directories. |
| `--exclude`, `-E` | GLOB | All | Repeatable explicit exclusion that prunes matched directories. |
| `--ignore-file` | PATH | All | Load an additional ignore file with gitignore syntax. |
| `--ignore-contain` | NAME | 10.5 | Exclude directories directly containing a named marker. Introduced in 10.4.0. |
| `--color`, `-c` | WHEN | All | Set the color-output policy. The value is required. |
| `--hyperlink`, `--hyper` | [=WHEN] | 10.3+ | Choose terminal hyperlink escapes. The alias and optional equals syntax come from the parser. |
| `--threads`, `-j` | COUNT | All | Set a positive worker count. |
| `--max-buffer-time` | MILLISECONDS | All | Hidden parser control for how long results are buffered before streaming. |
| `--size`, `-S` | SIZE | All | Select files by exact size or inclusive lower/upper bounds. |
| `--changed-within`, `--change-newer-than`, `--newer`, `--changed-after` | TIME | All | Lower modification-time bound. Both manuals and parsers supply the aliases. |
| `--changed-before`, `--change-older-than`, `--older` | TIME | All | Upper modification-time bound. |
| `--owner`, `-o` | OWNER | All | Unix user/group filter with names, numeric IDs or negated components. |
| `--base-directory` | PATH | All | Change working directory before resolving search roots. |
| `-C` | PATH | 10.5 | Short spelling for the base directory in upstream 10.5.2. |
| `--path-separator` | SEPARATOR | All | Set the path separator used in output. |
| `--search-path` | PATH | All | Supply a search root without a positional root. Repeat for more roots. |
| `--format` | TEMPLATE | 10.3+ | Format each result with a template. |
| `--exec`, `-x` | COMMAND... | All | Run one command per match. The parser consumes child options through a literal semicolon or end of input. |
| `--exec-batch`, `-X` | COMMAND... | All | Pass a batch of paths to a command. Uses the same child boundary. |
| `--batch-size` | COUNT | All | Cap the number of results in one batch. |
| `--gen-completions` | [SHELL] | All | Hidden and exclusive. Requires a build with shell-completion generation. Its optional value can be a separate word. |

## Grammar and exclusions

The native positional grammar is `[PATTERN] [PATH]...`. A literal `--` ends option parsing so a pattern beginning with a dash can be passed as data. `-uu` repeats the unrestricted switch. The program accepts additional options after a pattern or root. The profile stops offering parent options after the first positional operand. These forms belong to argument parsing and Details. They add no separate option effect. The Ubuntu help headings use a trailing ellipsis on `--unrestricted...` and all three use it on `<cmd>...`. Those dots are notation for repetition.

For `--exec` and `--exec-batch`, child command names, arguments, placeholders, the literal semicolon argument and shell quoting belong to the command template. They are not parent options. Similarly, type names, size units, timestamps, ownership components, output-template placeholders, environment variables and ignore-file names are values or configuration. The applicable option's Details and the linked manuals describe them. Options from fdclone and from commands such as `ls` have no entry in the finder inventory.
