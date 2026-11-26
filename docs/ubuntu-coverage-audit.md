# Ubuntu command coverage audit

The Ubuntu 26.04 amd64 image reconciliation covers 2,385 shipped names, eight versioned kernel paths and all 119 command rows selected by the 100-package ranking. The optional inventory retains its other 86 comparison rows. The shipped replay used the image path and resolved provider, the default driver registry, bundled profiles, fixed package and Bash replies, and the packaged fallback. Each selectable result went through the context resolver and literal insertion. The image check replays missing-manual conditions. The images themselves were inspected as filesystems. [Shipped results](ubuntu-command-coverage/shipped.tsv) · [Kernel results](ubuntu-command-coverage/kernel-companions.tsv) · [Optional results](ubuntu-command-coverage/optional.tsv)

| Ubuntu 26.04 profile | Selectable | Usage or manual guidance |
| --- | ---: | ---: |
| Desktop Default | 1,726 | 315 |
| Desktop Extended | 1,764 | 323 |
| Server Default | 1,506 | 233 |
| Server Minimized | 1,238 | 199 |
| Ubuntu Base | 486 | 56 |
| Server Cloud | 1,329 | 171 |
| Union by command name | 2,039 | 346 |

A name with a selectable result on any applicable invocation counts in the first column. Each profile column in the TSV retains its own result. Comma-separated codes follow the listed invocation forms, with identical results collapsed. The original project comparison columns retain their historical meaning. The usage review records each affected invocation, image, source and outstanding argument evidence. [Usage and unresolved declarations](ubuntu-command-coverage/usage-review.tsv)

| Result | Meaning |
| --- | --- |
| S, P, B, R followed by a number | Number of selectable entries in a bundled static menu, fixed package-manager menu, Bash help topic, or packaged Ubuntu reference respectively. |
| BU, RU | Source-backed usage or documentation reached through Bash or the packaged reference. Optionless helpers and unresolved selection grammars both occur here. |
| L | The executable or snap launcher was identified. The menu points to the installed package or snap. The interface still needs a matching command-specific source. |
| — | The inspected image does not expose this invocation. |

## Runtime and sources

The five APT roots use edition-specific verb and option declarations from the Ubuntu APT source files `cmdline/apt*.cc` and `apt-private/private-cmndline.cc`. A root's fixed `--help` reply or manual identifies the edition. Across `apt`, `apt-cache`, `apt-get`, `apt-config` and `apt-mark` the tables cover 104 root-to-verb routes on Noble and 112 on Resolute. The dpkg, dpkg-deb and dpkg-query menus distinguish actions, short aliases, required tuples and edition-specific spelling. Tests include both the three operands of `dpkg --compare-versions` and archive/directory pairs from forwarded dpkg-deb actions. [APT tables](../cli_help/apt_editions.py) · [Fixed sources](../tests/fixtures/ubuntu-coverage/) · [Package adapters](../cli_help/ubuntu_packaging.py)

All 61 Bash names use fixed, quoted help-topic requests. Bash 5.3 supplied 44 selectable topics and 17 usage results. Bash 5.2 supplied 42 and 19. The tests exercise builtin/external ownership, short-option arguments, `[`, and the `command`, `env` and `sudo` boundaries. The terminal check selects and cancels inside a quoted pending command. [Bash adapter](../cli_help/bash_builtins.py) · [Focused assertions](../tests/test_ubuntu_command_coverage.py)

Server Minimized and Ubuntu Base contained zero installed section 1 or 8 manuals. The approved fallback reads packaged declarations on demand after installed sources fail to produce a menu. The applicable Ubuntu release, installed path, recorded alternatives targets and exact kernel directory constrain eligibility. A known dpkg package revision mismatch returns guidance. A source package can be absent on a stripped image, so a verified image target may use its labelled baseline. Results therefore describe release reference data and their tested editions. They cannot establish the behavior of every subsequent update or local replacement. Explicit driver requests and executable identity checks retain precedence. [Lookup](../cli_help/ubuntu_reference.py) · [Reference data](../config/ubuntu-reference/)

The Noble replay produced selectable menus for all 117 ranked invocations supplied by its package archive. Its fixed compiler roots cover gcc and g++. Redis and SQLite help came from matching Noble binaries and libraries, and the atop synopsis distinguishes its output file from display switches. Noble supplies ImageMagick 6 and its archive supplied no starship package. The optional inventory records both release outcomes.

The ranked bands have 28, 28 and 63 selectable Resolute rows respectively. They include sibling commands such as pigz/unpigz, go/gofmt and the ImageMagick tools. An optional executable must be installed for discovery. All eight kernel entries match the versioned paths from `linux-tools-7.0.0-30` version `7.0.0-30.30`. Source evidence comes from the matching common manuals and the three binaries' embedded usage for acpidbg, rtla and intel-speed-select. Verification did not exercise hardware controls. [Kernel path inventory](ubuntu-command-coverage/kernel-companions.tsv)

## Online manual and provider review

All 61 Bash topics had local edition-specific help. GNU's index provides the topic-to-manual cross-reference. The fixed Bash responses remain the authority for differences between 5.2 and 5.3. [GNU Bash builtin index](https://www.gnu.org/software/bash/manual/html_node/Builtin-Index.html)

For the 143 remaining shipped names, exact-name section 1 and 8 lookups on Ubuntu's Resolute manpage service returned 20 pages. Nineteen described HPLIP commands. The remaining page described the Debian package provider of `hwctl`; the snap launcher has its own capture. Ubuntu release and updates source indexes were checked against the signed archive metadata. Package manuals, argument declarations, documented wrappers and matching snap revisions supplied 109 selectable menus and 34 command-specific usage results among those 143 names. The source table identifies the online references, including lookups where Ubuntu publishes docs under a sibling name. Menus read the packaged data offline. [Per-command source evidence](ubuntu-command-coverage/online-sources.tsv) · [Ubuntu hp-align manual](https://manpages.ubuntu.com/manpages/resolute/man1/hp-align.1.html) · [Mozilla geckodriver flags](https://firefox-source-docs.mozilla.org/testing/geckodriver/Flags.html)

HP printer options preserve joined short operands and long options with equals signs. The Twisted package suffixes its executables with `3` while its source manuals use the upstream names. Firefox and Thunderbird snap launchers require the recorded snap revision. Their Debian wrappers additionally check the known package revision. Graphical-only launchers and internal helpers receive guidance about their entry point. The approved digit-leading keyword grammar supports literal printer models such as `1025` and `2600n` in `getweb`. Focused insertion checks preserve trailing arguments and reject punctuation that would introduce shell syntax.

## Reproducing coverage checks

Run `python3 -B scripts/check_ubuntu_coverage.py` from the checkout. It validates source identities, reconstructs both editions' menus, checks image applicability and reconciles the recorded result codes. The focused tests use independently specified spellings and argument counts. The complete fixed Bash and package replies can be compared with the collector in each supported fixture environment.

Each installed JSON Lines record contains an invocation, source package and revision, manual or fixed request, source digest, literal declarations and usage. The digest identifies rendered UTF-8 text for manual and help inputs, binary bytes for embedded usage, or the inspected path tuple for location evidence. To refresh a manual, render the matching package page at width 100 with `man -P /bin/cat --no-hyphenation --no-justification -l PAGE`. Give the reference builder a complete edition manifest mapping each command to `package`, `version`, `page` and `file`. A `variants` array can distinguish providers by `targets` and `directory`. A source with separately reviewed declarations can supply `declarations` in the same record. Build into an empty directory and review the differences against the installed shards. [Reference builder](../scripts/build_ubuntu_reference.py) · [Numerical review and reconciliation](numerical-inventory/README.md)

## Verification

The fixture environments use Ubuntu 26.04.1 with Python 3.14.4 and Bash 5.3.9, and Ubuntu 24.04.5 with Python 3.10.20 or 3.12.3 and Bash 5.2.21. The captured package revisions are APT 3.2.1ubuntu0.1 and dpkg 1.23.7ubuntu1 on Resolute, and APT 2.8.4ubuntu0.1 and dpkg 1.22.6ubuntu6.6 on Noble. The full suites use the existing target-specific FFmpeg, fzf, OpenSSH, rsync and yq fixture setup.


### Combined offline matrix, 2026-11-26

Each full run used the same frozen source snapshot `33268767f1b67e82f2bd570036ea0774ff886f38a7a993ad53a8f64ce9011f51`. The target-specific fixture hashes were checked before attaching the fixtures. The impacted selector requested the full matrix for shared inputs. The strict numerical gate passed with 4,426 of 4,426 required contracts complete, 93 warnings, 11 informational diagnostics and zero errors or debt. Both profile collections and the two-edition Ubuntu inventory replay passed.

| Target | Initial focused passes | Diagnostic correction focused passes | Full passes | Full skips | Full suite time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Host, Resolute | 66 | 36 | 2,021 | 1 | 2,507.5 s |
| Noble, Python 3.10 | 47 | 36 | 2,021 | 1 | 2,771.0 s |
| Noble, Python 3.12 | 47 | 36 | 2,021 | 1 | 2,513.8 s |

The skip on each target covers the Windows-only case. The earlier combined run exposed the same three passive diagnostic failures on every target. Explicit nested profiles using a builtin name had been labeled as Bash help. The three failures reproduced on the host, then passed after route and cache provenance followed the selected profile. Two earlier, interrupted runs were superseded as additional manual evidence was incorporated. They contributed no full-suite pass results.

Of the 2,355 shipped names that lacked maintained project evidence in the original comparison, 2,009 now have selectable menus and 346 have usage or documentation. The six names that previously had selectable subpaths only now have a selectable root. Among ranked optional invocations, 96 gained coverage from a baseline without maintained evidence and eight gained a selectable root alongside existing subpaths.

With the host manual directory empty, discovery for `getweb 10 'untouched value'` selected the packaged model `1025` and preserved the quoted argument. The clean-install fallback smoke check produced 12 selectable entries for `cmp`. The per-image conclusions come from filesystem and route replay. The matrix exercised the host and the two Noble fixture environments.
