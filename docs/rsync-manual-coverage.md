# Rsync manual coverage

The bundled menu contains **216 distinct rows**, including the 29 original client rows and 187 additions. Of these, 196 apply only to a transfer client, five apply only to daemon startup and 15 work in both contexts. This gives 211 client options and 20 daemon options across the three releases. There are 92 alias assignments and 306 distinct literal spellings. Two short spellings have context-dependent meanings. [Bundled profile](../profiles/rsync.json) · [First-pass audit](rsync-option-audit.md)

## Manuals and tagged sources

| Release | Client / daemon summary rows | Sources checked |
| --- | ---: | --- |
| Ubuntu 24.04 Noble, 3.2.7-1ubuntu1.5 | 144 / 14 | [Ubuntu rsync(1)](https://manpages.ubuntu.com/manpages/noble/man1/rsync.1.html), [3.2.7 manual source](https://github.com/RsyncProject/rsync/blob/v3.2.7/rsync.1.md), [3.2.7 option parser](https://github.com/RsyncProject/rsync/blob/v3.2.7/options.c) |
| Ubuntu 26.04 Resolute, 3.4.1+ds1-7ubuntu0.3 | 144 / 14 | [Ubuntu rsync(1)](https://manpages.ubuntu.com/manpages/resolute/man1/rsync.1.html), [3.4.1 manual source](https://github.com/RsyncProject/rsync/blob/v3.4.1/rsync.1.md), [3.4.1 option parser](https://github.com/RsyncProject/rsync/blob/v3.4.1/options.c) |
| Upstream 3.5.2 | 157 / 16 | [Published rsync(1)](https://download.samba.org/pub/rsync/rsync.1), [3.5.2 manual source](https://github.com/RsyncProject/rsync/blob/v3.5.2/rsync.1.md), [3.5.2 option parser](https://github.com/RsyncProject/rsync/blob/v3.5.2/options.c) |

The summaries retain the pilot counts. The inventory also uses the full option definitions, including filter rules, transfer rules, sender and receiver terminology, daemon startup and internal options. The three tagged parsers supply the concrete negations, value requirements and accepted compatibility spellings omitted from the printed lists. The two older tags declare the same option names in both parser tables. Both Ubuntu clients print 144 client and 14 daemon summary rows in fixed help.

## Manual inventory

Each primary spelling below has a selectable row. Aliases resolve to the same documented action. A dash in the operand column marks a switch. Each named operand is required. A long option can take its value after an equals sign or in the next word. The short form can take an attached or separate value. The menu inserts the canonical long form with a trailing equals sign when it needs a value. Source and destination remain separate positional operands. A single source without a destination requests a listing.

The mode column describes the initiating process. A client connecting to a module with `host::module` or `rsync://host/module` uses the client parser. A listener started with `--daemon` uses the daemon parser. A remote-shell peer is also a server, even when no persistent daemon is running. “All” refers to option declarations in the three tagged releases. Build capabilities still govern individual features. In particular, both Ubuntu binaries advertise `--crtimes` in help but reject attempts to enable it.

| Canonical | Aliases | Operand | Mode | Releases |
| --- | --- | --- | --- | --- |
| `--verbose` | `-v` | — | both | all |
| `--info` | — | `FLAGS` | client | all |
| `--debug` | — | `FLAGS` | client | all |
| `--stderr` | — | `MODE` | client | all |
| `--quiet` | `-q` | — | client | all |
| `--no-motd` | — | — | client | all |
| `--checksum` | `-c` | — | client | all |
| `--archive` | `-a` | — | client | all |
| `--recursive` | `-r` | — | client | all |
| `--inc-recursive` | `--i-r` | — | client | all |
| `--no-inc-recursive` | `--no-i-r` | — | client | all |
| `--relative` | `-R` | — | client | all |
| `--no-implied-dirs` | `--no-i-d` | — | client | all |
| `--backup` | `-b` | — | client | all |
| `--backup-dir` | — | `DIRECTORY` | client | all |
| `--suffix` | — | `SUFFIX` | client | all |
| `--update` | `-u` | — | client | all |
| `--inplace` | — | — | client | all |
| `--append` | — | — | client | all |
| `--append-verify` | — | — | client | all |
| `--dirs` | `-d` | — | client | all |
| `--old-dirs` | `--old-d` | — | client | all |
| `--mkpath` | — | — | client | all |
| `--links` | `-l` | — | client | all |
| `--copy-links` | `-L` | — | client | all |
| `--copy-unsafe-links` | — | — | client | all |
| `--safe-links` | — | — | client | all |
| `--insecure-links` | — | — | client | upstream only |
| `--confine-root` | — | `DIR` | client | upstream only |
| `--munge-links` | — | — | client | all |
| `--copy-dirlinks` | `-k` | — | client | all |
| `--keep-dirlinks` | `-K` | — | client | all |
| `--hard-links` | `-H` | — | client | all |
| `--perms` | `-p` | — | client | all |
| `--executability` | `-E` | — | client | all |
| `--chmod` | — | `CHMOD` | client | all |
| `--acls` | `-A` | — | client | all |
| `--xattrs` | `-X` | — | client | all |
| `--owner` | `-o` | — | client | all |
| `--group` | `-g` | — | client | all |
| `--devices` | — | — | client | all |
| `--copy-devices` | — | — | client | all |
| `--write-devices` | — | — | client | all |
| `--specials` | — | — | client | all |
| `--drop-D` | — | — | client | upstream only |
| `-D` | — | — | client | all |
| `--times` | `-t` | — | client | all |
| `--atimes` | `-U` | — | client | all |
| `--open-noatime` | — | — | client | all |
| `--crtimes` | `-N` | — | client | all |
| `--omit-dir-times` | `-O` | — | client | all |
| `--omit-link-times` | `-J` | — | client | all |
| `--super` | — | — | client | all |
| `--fake-super` | — | — | client | all |
| `--sparse` | `-S` | — | client | all |
| `--preallocate` | — | — | client | all |
| `--dry-run` | `-n` | — | client | all |
| `--whole-file` | `-W` | — | client | all |
| `--no-whole-file` | `--no-W` | — | client | all |
| `--checksum-choice` | `--cc` | `STR` | client | all |
| `--one-file-system` | `-x` | — | client | all |
| `--block-size` | `-B` | `SIZE` | client | all |
| `--rsh` | `-e` | `COMMAND` | client | all |
| `--rsync-path` | — | `PROGRAM` | client | all |
| `--existing` | `--ignore-non-existing` | — | client | all |
| `--ignore-existing` | — | — | client | all |
| `--remove-source-files` | — | — | client | all |
| `--delete` | — | — | client | all |
| `--delete-before` | — | — | client | all |
| `--delete-during` | `--del` | — | client | all |
| `--delete-delay` | — | — | client | all |
| `--delete-after` | — | — | client | all |
| `--delete-excluded` | — | — | client | all |
| `--ignore-missing-args` | — | — | client | all |
| `--delete-missing-args` | — | — | client | all |
| `--ignore-errors` | — | — | client | all |
| `--force` | — | — | client | all |
| `--max-delete` | — | `NUM` | client | all |
| `--max-size` | — | `SIZE` | client | all |
| `--min-size` | — | `SIZE` | client | all |
| `--max-alloc` | — | `SIZE` | client | all |
| `--partial` | — | — | client | all |
| `--partial-dir` | — | `DIR` | client | all |
| `--delay-updates` | — | — | client | all |
| `--delay-symlinks` | — | — | client | upstream only |
| `--prune-empty-dirs` | `-m` | — | client | all |
| `--numeric-ids` | — | — | client | all |
| `--usermap` | — | `STRING` | client | all |
| `--groupmap` | — | `STRING` | client | all |
| `--chown` | — | `USER:GROUP` | client | all |
| `--timeout` | — | `SECONDS` | client | all |
| `--contimeout` | — | `SECONDS` | client | all |
| `--ignore-times` | `-I` | — | client | all |
| `--size-only` | — | — | client | all |
| `--modify-window` | `-@` | `NUM` | client | all |
| `--temp-dir` | `-T` | `DIR` | both | all |
| `--fuzzy` | `-y` | — | client | all |
| `--compare-dest` | — | `DIR` | client | all |
| `--copy-dest` | — | `DIR` | client | all |
| `--link-dest` | — | `DIR` | client | all |
| `--compress` | `-z` | — | client | all |
| `--compress-choice` | `--zc` | `STR` | client | all |
| `--compress-level` | `--zl` | `NUM` | client | all |
| `--compress-threads` | `--zt` | `NUM` | client | upstream only |
| `--skip-compress` | — | `LIST` | client | all |
| `--cvs-exclude` | `-C` | — | client | all |
| `--filter` | `-f` | `RULE` | client | all |
| `-F` | — | — | client | all |
| `--exclude` | — | `PATTERN` | client | all |
| `--exclude-from` | — | `FILE` | client | all |
| `--include` | — | `PATTERN` | client | all |
| `--include-from` | — | `FILE` | client | all |
| `--files-from` | — | `FILE` | client | all |
| `--from0` | `-0` | — | client | all |
| `--old-args` | — | — | client | all |
| `--secluded-args` | `-s`, `--protect-args` | — | client | all |
| `--trust-sender` | — | — | client | all |
| `--copy-as` | — | `USER[:GROUP]` | client | all |
| `--address` | — | `ADDRESS` | both | all |
| `--port` | — | `PORT` | both | all |
| `--sockopts` | — | `OPTIONS` | both | all |
| `--blocking-io` | — | — | client | all |
| `--outbuf` | — | `MODE` | client | all |
| `--stats` | — | — | client | all |
| `--8-bit-output` | `-8` | — | client | all |
| `--human-readable` | `-h` | — | client | all |
| `--progress` | — | — | client | all |
| `-P` | — | — | client | all |
| `--itemize-changes` | `-i` | — | client | all |
| `--remote-option` | `-M` | `OPT` | client | all |
| `--out-format` | `--log-format` | `FORMAT` | client | all |
| `--log-file` | — | `FILE` | both | all |
| `--log-file-format` | — | `FMT` | both | all |
| `--password-file` | — | `FILE` | client | all |
| `--early-input` | — | `FILE` | client | all |
| `--list-only` | — | — | client | all |
| `--bwlimit` | — | `RATE` | both | all |
| `--stop-after` | `--time-limit` | `MINS` | client | all |
| `--stop-at` | — | `y-m-dTh:m` | client | all |
| `--fsync` | — | — | client | all |
| `--write-batch` | — | `FILE` | client | all |
| `--only-write-batch` | — | `FILE` | client | all |
| `--read-batch` | — | `FILE` | client | all |
| `--protocol` | — | `NUM` | both | all |
| `--iconv` | — | `CONVERT_SPEC` | client | all |
| `--checksum-seed` | — | `NUM` | client | all |
| `--ipv4` | `-4` | — | both | all |
| `--ipv6` | `-6` | — | both | all |
| `--nice` | — | `SETTINGS` | both | upstream only |
| `--no-nice` | — | — | both | upstream only |
| `--version` | `-V` | — | client | all |
| `--help` | `-h` | — | both | all |
| `--no-verbose` | `--no-v` | — | both | all |
| `--msgs2stderr` | — | — | client | all |
| `--no-msgs2stderr` | — | — | client | all |
| `--motd` | — | — | client | all |
| `--no-human-readable` | `--no-h` | — | client | all |
| `--no-recursive` | `--no-r` | — | client | all |
| `--no-dirs` | `--no-d` | — | client | all |
| `--no-perms` | `--no-p` | — | client | all |
| `--no-acls` | `--no-A` | — | client | all |
| `--no-xattrs` | `--no-X` | — | client | all |
| `--no-times` | `--no-t` | — | client | all |
| `--no-atimes` | `--no-U` | — | client | all |
| `--no-open-noatime` | — | — | client | all |
| `--no-crtimes` | `--no-N` | — | client | all |
| `--no-omit-dir-times` | `--no-O` | — | client | all |
| `--no-omit-link-times` | `--no-J` | — | client | all |
| `--no-super` | — | — | client | all |
| `--no-owner` | `--no-o` | — | client | all |
| `--no-group` | `--no-g` | — | client | all |
| `--no-D` | — | — | client | all |
| `--no-devices` | — | — | client | all |
| `--no-write-devices` | — | — | client | all |
| `--no-specials` | — | — | client | all |
| `--no-drop-D` | — | — | client | upstream only |
| `--no-links` | `--no-l` | — | client | all |
| `--no-insecure-links` | — | — | client | upstream only |
| `--no-munge-links` | — | — | client | all |
| `--no-hard-links` | `--no-H` | — | client | all |
| `--no-relative` | `--no-R` | — | client | all |
| `--implied-dirs` | `--i-d` | — | client | all |
| `--no-one-file-system` | `--no-x` | — | client | all |
| `--no-sparse` | `--no-S` | — | client | all |
| `--no-inplace` | — | — | client | all |
| `--no-append` | — | — | client | all |
| `--no-force` | — | — | client | all |
| `--no-ignore-errors` | — | — | client | all |
| `--no-checksum` | `--no-c` | — | client | all |
| `--no-fuzzy` | `--no-y` | — | client | all |
| `--old-compress` | — | — | client | all |
| `--new-compress` | — | — | client | all |
| `--no-compress` | `--no-z` | — | client | all |
| `--no-progress` | — | — | client | all |
| `--no-partial` | — | — | client | all |
| `--no-delay-updates` | — | — | client | all |
| `--no-delay-symlinks` | — | — | client | upstream only |
| `--no-prune-empty-dirs` | `--no-m` | — | client | all |
| `--no-itemize-changes` | `--no-i` | — | client | all |
| `--no-bwlimit` | — | — | client | all |
| `--no-backup` | — | — | client | all |
| `--no-from0` | — | — | client | all |
| `--no-old-args` | — | — | client | all |
| `--no-secluded-args` | `--no-protect-args`, `--no-s` | — | client | all |
| `--no-numeric-ids` | — | — | client | all |
| `--no-timeout` | — | — | client | all |
| `--no-contimeout` | — | — | client | all |
| `--no-iconv` | — | — | client | all |
| `--no-8-bit-output` | `--no-8` | — | client | all |
| `--no-mkpath` | — | — | client | all |
| `--no-blocking-io` | — | — | client | all |
| `--config` | — | `FILE` | daemon | all |
| `--daemon` | — | — | daemon | all |
| `--dparam` | `-M` | `OVERRIDE` | daemon | all |
| `--detach` | — | — | daemon | all |
| `--no-detach` | — | — | daemon | all |

## Differences the summaries conceal

- **Negations and order.** The tagged parsers declare 60 distinct actions spelled with a leading `--no-`, including daemon and upstream-only actions. Each has a selectable literal. For example, `-a --no-r` clears recursion while `--no-r -a` enables it. Argument order applies to explicit assignments. Defaults established after parsing can still take effect. With `--files-from`, archive mode uses an explicit list and recursion requires `-r` regardless of option order. Likewise, supplying `--backup-dir` enables backups after the options are read. The parsers accept `--no-backup` and have no `--no-b` entry, even though upstream prose suggests that every negation has a short-name counterpart. An arbitrary positive flag cannot be turned off by prepending `no-`. [Upstream negations](https://download.samba.org/pub/rsync/rsync.1#opt--no-OPTION) · [Parser and post-processing](https://github.com/RsyncProject/rsync/blob/v3.5.2/options.c)
- **Short and repeated forms.** The independent short rows `-D`, `-F` and `-P` each expand to multiple actions or a predefined rule. A second `-F` also excludes the per-directory filter file. Repeatable flags keep the same selectable literal so that another occurrence can be inserted. Examples include `-xx` to omit mount points entirely, `-UU` to also request opens that preserve access times, `-XX` to copy rsync's special extended attributes, and `-ii` to list unchanged items with a suitable peer. A lone client `-h` requests help, whereas `-h` on a transfer controls numeric display. In daemon mode `-h` prints startup help. [Upstream options](https://download.samba.org/pub/rsync/rsync.1#OPTIONS)
- **Compatibility spellings.** The table includes earlier names such as `--protect-args`, `--time-limit` and `--log-format`. The fixed-value forms `--old-compress` and `--new-compress` select zlib and zlibx respectively. The old `--msgs2stderr` and `--no-msgs2stderr` select different stderr modes. Each fixed-value switch retains its own operand-free row. The upstream 3.5.2 compression-thread discussion refers once to `--compression-choice`. The declared option is `--compress-choice` or `--zc`. [Compression options](https://download.samba.org/pub/rsync/rsync.1#opt--compress-choice) · [Tagged declarations](https://github.com/RsyncProject/rsync/blob/v3.5.2/options.c)
- **Release differences.** Ten rows are specific to the 3.5.2 parser in this comparison. They cover confinement, symlink handling, device and special-file refusal, compression threads and process priorities, including their declared negations. Other apparent additions to the upstream summary, including `--i-r`, `--no-i-r`, `--old-d`, `--no-W` and `--ignore-non-existing`, are already present in both Ubuntu parsers. Ubuntu lists binary-scaled human-readable sizes using the same suffix letters as decimal sizes. The upstream manual distinguishes binary units with an additional `i`. [Noble options](https://manpages.ubuntu.com/manpages/noble/man1/rsync.1.html) · [Resolute options](https://manpages.ubuntu.com/manpages/resolute/man1/rsync.1.html) · [Upstream size display](https://download.samba.org/pub/rsync/rsync.1#opt--human-readable)
- **Startup and transfer options.** Client `-M` sends an option to the remote rsync process. Under `--daemon`, `-M` supplies a global `NAME=VALUE` configuration override. The daemon parser also accepts `--detach`, `--protocol`, `--temp-dir` and `--no-verbose`, which its summary omits. The client rate operand supports size suffixes and fractional values. The daemon parser uses an integer cap in KiB/s. The client can request a lower cap. Ports, bind addresses, logging, verbosity and address-family preferences also depend on the selected mode. [Daemon options](https://download.samba.org/pub/rsync/rsync.1#DAEMON_OPTIONS) · [Daemon parser](https://github.com/RsyncProject/rsync/blob/v3.5.2/options.c)

## Coverage boundaries

- `--no-OPTION` and `--delete-WHEN` represent families. The menu inserts the concrete choices. Negative short forms such as `--no-O` and `--no-o` are case-sensitive and control different attributes.
- The documented internal switches `--server` and `--sender` coordinate rsync processes. The source also retains deprecated `--remove-sent-files` for wire compatibility and an undocumented `--qsort` implementation selector. These four parser names are outside the operator menu. The option for normal sender-side cleanup is `--remove-source-files`. [Internal options](https://download.samba.org/pub/rsync/rsync.1#INTERNAL_OPTIONS) · [Peer argument construction](https://github.com/RsyncProject/rsync/blob/v3.5.2/options.c)
- The `-Z` example in the permissions section requires a custom `~/.popt` alias. Neither Ubuntu rsync package ships such an alias. The modify-window examples also define personal aliases for `-a` and `-t`. These definitions and local shell aliases can be customized independently of the bundled spellings. [Permissions](https://download.samba.org/pub/rsync/rsync.1#opt--perms)
- Module directives such as `read only`, environment variables, filter-rule prefixes, log-format escapes, and SSH arguments belong to their respective configuration, expression or transport grammars. They can be operands of applicable options. The `--list` example invokes the separate `iconv` program. [Daemon configuration](https://download.samba.org/pub/rsync/rsyncd.conf.5) · [Remote-shell selection](https://download.samba.org/pub/rsync/rsync.1#opt--rsh) · [Filename conversion](https://download.samba.org/pub/rsync/rsync.1#opt--iconv)

## Material changes in the menu

- **Source paths.** For an existing destination directory, `src` copies the named directory and `src/` copies its contents. `--relative` retains leading path components and accepts a `/./` cut point. A `--files-from` list is relative to the source root. It implies directory entries and relative paths, but archive mode now needs an explicit `-r` to descend. `--from0` lets a list contain filenames with embedded newlines. [Path lists](https://download.samba.org/pub/rsync/rsync.1#opt--files-from)
- **Filters and deletion.** The first matching rule on each side wins. A sender exclusion can stop traversal into a directory. An ordinary exclusion also protects matching receiver files. With `--delete-excluded`, an unqualified rule applies only to the sender, so receiver protection must be explicit. `--delete-delay` computes deletions during traversal. `--delete-after` can use freshly transferred per-directory rules when it computes them. Sender I/O errors ordinarily stop deletion. For a preview, `--dry-run --itemize-changes` shows the paths that would change. [Filtering](https://download.samba.org/pub/rsync/rsync.1#FILTER_RULES) · [Deletion limits](https://download.samba.org/pub/rsync/rsync.1#opt--max-delete)
- **Transfer selection and recovery.** The default quick check uses file length and modification time. `--checksum` reads file data to decide which files need an update. `--whole-file` instead changes how selected data is sent. Ordinary partial-file retention can leave an incomplete file at the destination name. A private partial directory can retain retry data separately. With `--inplace`, readers and other hard links see the changes immediately. Both append modes assume a growing file and skip equal or longer receiver files. Only `--append-verify` includes the existing bytes in its verification with current protocols. [Quick check](https://download.samba.org/pub/rsync/rsync.1#opt--checksum) · [Partial files](https://download.samba.org/pub/rsync/rsync.1#opt--partial-dir) · [Append verification](https://download.samba.org/pub/rsync/rsync.1#opt--append-verify)
- **Ownership and links.** The menu identifies the end that follows a symlink or needs permission to set metadata. An unprivileged receiver can usually assign only its own groups. Ordinary Linux users normally copy xattrs in the user namespace. A receiver using `--fake-super` needs writable extended attributes. Some options require a capable peer, filesystem or build. [Symlinks](https://download.samba.org/pub/rsync/rsync.1#SYMBOLIC_LINKS) · [Fake super-user](https://download.samba.org/pub/rsync/rsync.1#opt--fake-super)
- **Rates and limits.** A bare client bandwidth is in KiB/s. Size suffixes distinguish 1000 from 1024, and the client truncates the scaled rate to whole bytes/s. Zero leaves the client uncapped, 1 through 511 is rejected, and 512 rounds to 1 KiB/s. A daemon startup rate accepts whole KiB/s only. The size filters instead default to bytes. A zero `--max-delete` on these clients reports excess candidates and removes none. A pre-3.0.0 client treated zero as unlimited. The Details also distinguish I/O inactivity from the initial TCP connection deadline. [Bandwidth](https://download.samba.org/pub/rsync/rsync.1#opt--bwlimit) · [Size syntax](https://download.samba.org/pub/rsync/rsync.1#opt--max-size)

## Packaged observations

The Resolute sandbox used the host's packaged executable. The two prebuilt Noble images omit rsync. Each received the same Ubuntu amd64 executable and Noble shared libraries in its disposable snapshot. The rsync package SHA-256 was `8f952895697d19a6f1caa71f17c7d4e8c1f1fb485eb824ffe3e4c77dd587b338`. Package hashes were checked against the Ubuntu archive index before extraction. No installation or daemon startup was needed. [Noble package archive](https://archive.ubuntu.com/ubuntu/pool/main/r/rsync/)

Unmodified standard output from `LC_ALL=C rsync --help` and `LC_ALL=C rsync --daemon --help` is preserved separately for each release. Both Noble targets produced byte-identical captures. The older three-row discovery fixture is representative input for the discovery parser. [Noble client](../tests/fixtures/rsync/noble-client.txt) · [Noble daemon](../tests/fixtures/rsync/noble-daemon.txt) · [Resolute client](../tests/fixtures/rsync/resolute-client.txt) · [Resolute daemon](../tests/fixtures/rsync/resolute-daemon.txt) · [Discovery fixture](../tests/fixtures/help/rsync.txt)

- Both packages accepted daemon startup parsing with `--bwlimit=2 --help` and rejected `1K` and `1.5` as invalid numeric values in daemon mode. Separate client dry runs accepted `0.1B`, `0` and `512B` and rejected `1B` and `511B`. Fixed argument checks rejected the tested upstream confinement, link-delay, device-refusal, thread and scheduling options. Both clients rejected `--no-b`. Although `--crtimes` appears in the help output, a local dry run returned an unsupported-feature diagnostic. The corresponding `--no-crtimes` and `--no-N` switches succeeded.
- Local transfer fixtures confirmed the source trailing-slash distinction, the effect of reversing `-a` and `--no-recursive`, and explicit recursion with `--files-from`. A deletion preview preserved both destination files on disk. Its itemized output named the excluded file for deletion only after adding `--delete-excluded`. Separate local dry runs on both releases accepted zero for `--max-alloc`, `--block-size`, `--max-size` and `--min-size`. [Packaged client regressions](../tests/test_rsync_manual_coverage.py)

## Verification

The terminal regression opens real Bash and tmux with discovery disabled and an rsync shell stub. It compares selected rows, summaries and the complete Details pane, including formatted operand guidance. At 60×16 it searches for a sender I/O error qualification, a daemon configuration file and the historical alias `--protect-args`. Escape must restore the exact original buffer and cursor. Selecting `--files-from=` before two quoted operands must preserve the suffix and place the cursor immediately after the equals sign. These checks also assert that the stub was never invoked. Real rsync behavior uses separate disposable fixtures. [Terminal and inventory tests](../tests/test_rsync_manual_coverage.py) · [Offline sandbox instructions](development.md#isolated-local-debugging)

The focused sandbox command ran the strict numerical gate, the rsync module, the original insertion pin, the search-navigation class and the earlier terminal deletion regression. The full command ran `bash tests/run.sh` through `tests/run_sandbox.py`. Each snapshot explicitly included the new audit, test module and four fixed-help files. On Noble, `RSYNC_TEST_BINARY` pointed to a private wrapper for rsync 3.2.7, with libpopt0 1.19+dfsg-1build1, libxxhash0 0.8.2-2build1 and liblz4-1 1.9.4-1build1.1 extracted from Ubuntu packages. These package fixtures live outside the bundled menu. The strict gate reconciled 854 required contracts across 76 profiles. For the 209 changed inventory identities, the numerical review retained every source observation outside the rsync profile. [Numerical review](numerical-inventory/review.json)

| Target | Ubuntu | Python | rsync package | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 3.4.1+ds1-7ubuntu0.3 | 22 / 0 / 0 | 1,368 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 3.2.7-1ubuntu1.5 | 22 / 0 / 0 | 1,368 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 3.2.7-1ubuntu1.5 | 22 / 0 / 0 | 1,368 / 0 / 1 |

The single full-suite skip on each target covers the Windows-specific probe limitation. All ten rsync inventory, package and rendered-menu regressions ran on every target. No manual-coverage or verification items remain open for rsync.
