# Ubuntu command coverage audit

The maintainer accepted these source and invocation results for v0.5.0-alpha. The [candidate checklist](../ROADMAP.md#remaining-work) tracks local package verification separately.

The Ubuntu 26.04 amd64 image reconciliation covers 2,385 shipped names, eight versioned kernel paths and all 119 command rows selected by the 100-package ranking. The optional inventory retains its other 86 comparison rows. The shipped replay used the image path and resolved provider, the default driver registry, bundled profiles, fixed package and Bash replies, and the packaged fallback. Each selectable result went through the context resolver and literal insertion. The image check replays missing-manual conditions. The images themselves were inspected as filesystems. [Shipped results](ubuntu-command-coverage/shipped.tsv) · [Kernel results](ubuntu-command-coverage/kernel-companions.tsv) · [Optional results](ubuntu-command-coverage/optional.tsv)

| Ubuntu 26.04 profile | Selectable | Usage or manual guidance |
| --- | ---: | ---: |
| Desktop Default | 1,860 | 181 |
| Desktop Extended | 1,901 | 186 |
| Server Default | 1,609 | 130 |
| Server Minimized | 1,321 | 116 |
| Ubuntu Base | 506 | 36 |
| Server Cloud | 1,424 | 76 |
| Union by command name | 2,189 | 196 |

A name with a selectable result on any applicable invocation counts in the first column. Each profile column in the TSV retains its own result. Comma-separated codes follow the listed invocation forms, with identical results collapsed. The original project comparison columns retain their historical meaning. The usage review records each affected invocation, image, source and outstanding argument evidence. [Usage and unresolved declarations](ubuntu-command-coverage/usage-review.tsv)

| Result | Meaning |
| --- | --- |
| S, P, B, R followed by a number | Number of selectable entries in a bundled static menu, fixed package-manager menu, Bash help topic, or packaged Ubuntu reference respectively. |
| BU, RU | Source-backed usage or documentation reached through Bash or the packaged reference. Optionless helpers and unresolved selection grammars both occur here. |
| L | The executable or snap launcher was identified. The menu points to the installed package or snap. The interface still needs a matching command-specific source. |
| — | The inspected image does not expose this invocation. |

## Phase 1 provider review

The original 346 guidance-only names exposed 347 invocation paths. Both paths for `on_ac_power` resolve to the same argument-free helper. Bash `true` and `false` also have usage records, but their external forms already supplied selectable menus and placed those names outside this batch. [Exact invocations, image outcomes, revisions and limitations](ubuntu-command-coverage/phase1-review.tsv)

| Review group | Invocations | Newly selectable roots | Retained guidance | Selectable declarations |
| --- | ---: | ---: | ---: | ---: |
| Named option in manual | 12 | 10 | 2 | 458 |
| Option-bearing synopsis | 45 | 39 | 6 | 771 |
| Remaining providers | 290 | 101 | 189 | 970 |
| Total | 347 | 150 | 197 | 2,199 |

Counts include each literal spelling once per root. The 197 retained invocations represent 196 names. Separate and attached operands, equals forms, optional values, aliases and commands selected after an operand have distinct findings in the ledger. For example, the FUSE mount helpers read the source and destination before `-o`, and `fprintd-delete` accepts root help while its finger selector follows a username. The provider review also exposed a partial-name edit failure for single-dash options such as Tcl’s `-encoding`. Selecting a known partial name now preserves the following operand. Completed prior tokens, declared bundles and attached arguments retain their argument checks.

The original ISO layer manifests, Ubuntu Base dpkg database and Cloud dpkg database supplied installed revisions for all six profiles. The fallback checks the executable path, resolved target and package revision. A separately verified revision can carry its own source digest, declarations and manual fingerprints. The 111 alternate name/revision pairs in this batch cover 98 names. Signed Ubuntu archive indexes and package payloads supplied the older editions. Evidence includes byte comparisons, matching option-parser sections and fixed help from extracted binaries. [Per-revision verification](ubuntu-command-coverage/revision-evidence.tsv) · [Ubuntu snapshot service](https://snapshot.ubuntu.com/)

For 22 Resolute roots, generic parsing recovered an incomplete menu or assigned another program’s options to the root. Examples include the unsupported-option list in `xzgrep(1)`, `git archive --remote` in the server helper’s manual, and `poff` options in the shared PPP manual. Discovery fingerprints the existing fixed manual reply and selects the reviewed record only when its executable provider, package revision and manual digest match. Explicit drivers retain precedence. These roots recheck the actual reply on each lookup. A missing manual uses the existing fallback. The Resolute C and C.UTF-8 replays covered 43 distinct rendered-manual/revision cases across 37 command/revision pairs. Eighteen roots also passed live installed-manual discovery on the host. The three open-iscsi roots and `mysqld_qslower-bpfcc` used archived package manuals. [Installed and archived manual fingerprints](ubuntu-command-coverage/manual-evidence.tsv) · [Fixed discovery and revision regressions](../tests/test_ubuntu_reference_revisions.py)

The host replay of the reviewed Noble counterparts added 645 declarations across 75 newly selectable roots. Exact manual matching also applies to the Noble revisions of `plog`, `pod2html` and `sh`. The archive’s owning binaries and manuals were checked at their recorded revisions. Rendering those pages with Noble and host tooling in C and C.UTF-8 produced eight distinct fingerprints. `netaddr`, `threadsnoop-bpfcc` and `spa-json-dump` retain Noble-specific guidance. Both Noble Python targets subsequently passed the combined offline suite. [Phase 3 verification](audit-history.md#phase-3-combined-verification)

Three invocations require more provider evidence before a root choice can be added. The shipped `lxc` and `lxd` wrappers delegate to a separately installed LXD snap. Its revision determines the command table. For `/usr/bin/ptardiff -h`, the Perl manual describes a flag, while the script requires an argument and then calls an undefined handler. Other limitations include options supplied by a user-selected editor or pager and literal spellings outside the current profile grammar. For example, bdftruncate’s `+w` and xsetpointer’s `+c` are plus-prefixed switches. The xsetmode and wpa_action choices follow a required operand, and the Perl menu preserves attached debugger and module operands without validating their internal syntax. The ledger identifies the applicable profiles and provider at each invocation. [Remaining guidance](ubuntu-command-coverage/usage-review.tsv)

### Phase 2 follow-up on retained guidance

The follow-up added zero declarations. All 347 invocation dispositions and six image columns in the Phase 1 ledger retain their recorded results. The following observations identify when the outstanding choices can be reopened. [Invocation, edition, provider revision and source digest](ubuntu-command-coverage/phase1-review.tsv)

| Invocation or boundary | Evidence and disposition | Reopen when |
| --- | --- | --- |
| `/usr/bin/ptardiff -h` | The Desktop Default, Desktop Extended, Server Default and Server Minimized Perl package is `5.40.1-7ubuntu0.1`. Cloud has `5.40.1-7ubuntu0.3`. Both package manuals advertise help. Both extracted scripts have SHA-256 `1d7d45bd4f48409a479886e6cfb6e3e8093fea89b10ce906d399484d92a86cc0`. In a host Perl replay of the Cloud script, bare `-h` printed usage and exited 255 through the missing-value path. With `-h 1` the script exited 255 at the undefined `usages()` handler. Retain archive-operand guidance. | A matching provider revision supplies a working help flag with consistent arity. |
| `/usr/sbin/lxc`, `/usr/sbin/lxd` | Server Default, Server Minimized and Server Cloud have `lxd-installer 14ubuntu0`. The server ISO base layer contains the wrapper, the `lxd -> lxc` link and snap seeds for core24, hwctl and snapd. The standard layer adds lxd-agent-loader. The Cloud root archive contains both wrapper paths and an empty snap payload directory. Neither the applicable images nor the maintained fixtures identify an LXD snap revision. Retain wrapper guidance for both names. | Evidence ties an installed snap revision to the image and supplies its client and daemon command tables. Channels can move between publications. [Canonical snap revision and channel documentation](https://documentation.ubuntu.com/lxd/latest/reference/releases-snap/) |
| Post-operand choices | The FUSE helpers take source and destination before switches. The fingerprint selector follows a username in `fprintd-delete`. The mode follows the device in `xsetmode`, and the action follows the interface in `wpa_action`. Keep each existing root choice and operand boundary. Service-specific arguments and applet, script and plugin options retain the owning context in the ledger. | A matching provider exposes a root form, or an approved position-aware reference can select the documented later argument. |
| Plus and punctuation spellings | Retain `-w` for `bdftruncate` and the existing `xsetpointer` menu. Their `+w` and `+c`, the plus-prefixed shell toggles, and the `-?` aliases in `cryptdisks_start` and `nautilus-sendto` lack supported literal insertion on this reference path. For `zstdless`, less 668-1build1 documents `-#` alongside the covered `--shift`. An in-memory replay adding a standalone `-#` declaration to the real reference returned `reference_invalid`. The normalized parser expects this punctuation in an alias signature. | An approved literal or alias representation can round-trip each exact spelling, including safe shell treatment of glob characters. |
| Delegated and compound arguments | The selected editor, browser, pager, terminal or comparison program owns its own flags. The reference preserves documented wrapper-owned choices. Numeric and variable spellings such as grep's `-NUM`, Vim's mode-dependent operands, Perl's attached debugger/module syntax and pppd's keyword-plus-value forms retain their ledger boundaries. Positional-only commands retain guidance. | A fixed provider, revision and argument form establish the exact choice for that invocation, or an approved extension can represent it without changing the meaning of the pending arguments. |

## Runtime and sources

The five APT roots use edition-specific verb and option declarations from the Ubuntu APT source files `cmdline/apt*.cc` and `apt-private/private-cmndline.cc`. A root's fixed `--help` reply or manual identifies the edition. Across `apt`, `apt-cache`, `apt-get`, `apt-config` and `apt-mark` the tables cover 104 root-to-verb routes on Noble and 112 on Resolute. The dpkg, dpkg-deb and dpkg-query menus distinguish actions, short aliases, required tuples and edition-specific spelling. Tests include both the three operands of `dpkg --compare-versions` and archive/directory pairs from forwarded dpkg-deb actions. [APT tables](../cli_help/apt_editions.py) · [Fixed sources](../tests/fixtures/ubuntu-coverage/) · [Package adapters](../cli_help/ubuntu_packaging.py)

### APT option guidance in Simple, Detailed and Expanded

Each option in the five APT menus now has a short summary, operational guidance in Detailed and a further qualification, configuration setting or example in Expanded. Counts below include each spelling on each applicable root or verb. Subcommand keywords are counted separately from options. The existing simulation guidance accounts for 228 option entries on each edition.

| Edition and installed APT revision | apt | apt-cache | apt-get | apt-config | apt-mark | Newly explained | Total option entries |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Noble · 2.8.4ubuntu0.1 | 1,757 | 444 | 1,618 | 50 | 432 | 4,073 | 4,301 |
| Resolute · 3.2.1ubuntu0.1 | 2,315 | 501 | 1,734 | 62 | 510 | 4,894 | 5,122 |

The installed apt(8), apt-get(8), apt-cache(8), apt-mark(8) and apt-config(8) manuals provide the option behavior. Where a manual leaves a spelling or setting implicit, the matching package's `apt-private/private-cmndline.cc`, command implementations, apt.conf(5) and protocol documentation establish its scope. For example, `apt install -f` repairs dependencies, `apt search -f` prints full records, and `apt-mark -f` selects the state file. The fixtures preserve edition-specific declarations. [Fixed manuals](../tests/fixtures/ubuntu-coverage/) · [Noble source archive](https://archive.ubuntu.com/ubuntu/pool/main/a/apt/apt_2.8.4ubuntu0.1.tar.xz) · [Resolute source archive](https://archive.ubuntu.com/ubuntu/pool/main/a/apt/apt_3.2.1ubuntu0.1.tar.xz) · [Option guidance](../cli_help/apt_option_help.py)

The focused checks replay all 109 Noble and 117 Resolute routes, including the five roots. They compare declared flags and arity, check all three rendered levels, and exercise command-specific aliases and inverse spellings. A live Bash check on each target searches for the manual's asterisk notation for purge, cycles detail levels, cancels and then inserts the option before a quoted package name. The focused group passed 50 tests each on Resolute and both Noble Python targets. [Edition replay assertions](../tests/test_ubuntu_command_coverage.py) · [Bash terminal check](../tests/test_terminal_screen.py) · [100×26 APT demo](menu-demo-storyboards.md#1-apt--preview-a-package-install)

The unsharded offline suites used the same program and test changes. Resolute (Python 3.14.4), Noble (3.10.20) and Noble (3.12.3) each discovered 2,080 tests. Each had 2,078 passes, one failure, one Windows-only skip and exit status 1. The APT cases passed. All three failures were the 60×16 Git child-command title assertion, also reproduced from unmodified commit `35d23aa` on Noble. The first Resolute attempt received SIGTERM during the discovery screens and supplied no final result. Its retry supplied the count here. The numerical inventory reconciled and the strict gate passed all 4,426 required contracts. Local transcripts are in `tests/reports/apt-option-review/`. [Git resize evidence and open header decision](terminal-resize-review.md#phase-1--review-the-layout-boundary)

### Bash and reference providers

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

Each installed JSON Lines record contains an invocation, source package and revision, manual or fixed request, source digest, literal declarations and usage. The digest identifies rendered UTF-8 text for manual and help inputs, binary bytes for embedded usage, or the inspected path tuple for location evidence. To refresh a manual, render the matching package page at width 100 with `man -P /bin/cat --no-hyphenation --no-justification -l PAGE`. Give the reference builder a complete edition manifest mapping each command to `package`, `version`, `page` and `file`. A `variants` array can distinguish providers by `targets` and `directory`. A source with separately reviewed declarations can supply `declarations` in the same record. Use `revision_variants` for additional verified package revisions. A revision entry identifies its own source and may replace declarations with evidence for that edition. For an exact-manual override, record the SHA-256 of each fixed rendered reply in `reviewed_manual_sha256` on that revision, identify the executable owner separately if the manual ships in a different package, and add the root to `REVIEWED_MANUAL_ROOTS`. Build into an empty directory and review the differences against the installed shards. [Reference builder](../scripts/build_ubuntu_reference.py) · [Numerical review and reconciliation](numerical-inventory/README.md)

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

Of the 2,355 shipped names that lacked maintained project evidence in the original comparison, 2,009 had selectable menus and 346 had usage or documentation at that snapshot. The six names that previously had selectable subpaths only now have a selectable root. Among ranked optional invocations, 96 gained coverage from a baseline without maintained evidence and eight gained a selectable root alongside existing subpaths.

With the host manual directory empty, discovery for `getweb 10 'untouched value'` selected the packaged model `1025` and preserved the quoted argument. The clean-install fallback smoke check produced 12 selectable entries for `cmp`. The per-image conclusions come from filesystem and route replay. The matrix exercised the host and the two Noble fixture environments.
