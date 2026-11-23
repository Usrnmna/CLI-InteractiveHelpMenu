# OpenSSH file transfer option inventories

The `scp` menu covers 24 options, including nine additions to its 15 original rows. The `sftp` menu covers 26 options, including nine additions to its 17 original rows. Neither client documents a second spelling for a selectable option. Each inventory compares the command-line synopsis and option definitions with the corresponding client's top-level parser. Packaged observations and rendered-menu results are in the [OpenSSH verification report](openssh-manual-coverage.md).

## Sources

| Reference | scp(1) revision | sftp(1) revision | ssh_config(5) revision |
| --- | --- | --- | --- |
| OpenBSD-current, also represented in Portable 10.6p2 | [September 3, 2026](https://man.openbsd.org/scp.1) | [September 7, 2026](https://man.openbsd.org/sftp.1) | [October 30, 2026](https://man.openbsd.org/ssh_config.5) |
| Ubuntu 24.04, openssh-client 1:9.6p1-3ubuntu13.20 | [Noble scp](https://manpages.ubuntu.com/manpages/noble/man1/scp.1.html), December 16, 2022 | [Noble sftp](https://manpages.ubuntu.com/manpages/noble/man1/sftp.1.html), December 16, 2022 | [Noble ssh_config](https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html), October 12, 2023 |
| Ubuntu 26.04, openssh-client 1:10.2p1-2ubuntu3.8 | [Resolute scp](https://manpages.ubuntu.com/manpages/resolute/man1/scp.1.html), October 4, 2025 | [Resolute sftp](https://manpages.ubuntu.com/manpages/resolute/man1/sftp.1.html), December 6, 2024 | [Resolute ssh_config](https://manpages.ubuntu.com/manpages/resolute/man5/ssh_config.5.html), October 4, 2025 |

The Ubuntu columns identify the package published by the manpage service and the corresponding upstream manual datelines. The package supplies `/usr/bin/scp` and `/usr/bin/sftp`. The pilot guides retain their Portable 9.9p2 scope. The two release parsers supply the evidence for the new value guides. [9.6p1 released manuals and source](https://github.com/openssh/openssh-portable/tree/V_9_6_P1) · [9.9p2 release](https://github.com/openssh/openssh-portable/tree/V_9_9_P2) · [10.2p1 release](https://github.com/openssh/openssh-portable/tree/V_10_2_P1) · [10.6p2 release](https://github.com/openssh/openssh-portable/tree/V_10_6_P2)

## Reading the tables

An em dash marks a flag with no operand. Each named operand is required and occupies one argument. Both clients accept a separate word or text immediately after the letter. For example, `-P 2222` and `-P2222` select the same port. An equals sign immediately after a short option becomes part of its value. Flags can be combined until a value-taking option consumes the remainder of the word or the following argument. The menu inserts a flag and a space for a required value. The first path or destination operand, or an explicit `--`, closes the menu's option scope. [scp parser 9.6p1](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c#L508) · [scp parser 10.2p1](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L495) · [sftp parser 9.6p1](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp.c#L2466) · [sftp parser 10.2p1](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp.c#L2465)

## scp inventory

All three manuals describe 23 options. Both Ubuntu synopses supply an additional lowercase `-s`. The rows below follow manual order. All apply to all three manual releases except where qualified. [Upstream synopsis](https://man.openbsd.org/scp.1#SYNOPSIS) · [Noble synopsis](https://manpages.ubuntu.com/manpages/noble/man1/scp.1.html#SYNOPSIS) · [Resolute synopsis](https://manpages.ubuntu.com/manpages/resolute/man1/scp.1.html#SYNOPSIS)

| Flag | Operand | Menu | Effect |
| --- | --- | --- | --- |
| `-3` | — | Added | Relay a remote-to-remote copy through the local client. This is the default. With legacy SCP, the second connection uses batch mode. |
| `-4` | — | Original | Restrict SSH connections to IPv4. |
| `-6` | — | Original | Restrict SSH connections to IPv6. |
| `-A` | — | Added | Forward access to the local agent. Forwarding is off by default. |
| `-B` | — | Added | Enable SSH batch mode and suppress authentication prompts. |
| `-C` | — | Original | Request SSH transport compression. |
| `-c` | CIPHER | Added | Pass a cipher preference or an ordered comma-separated list to SSH. |
| `-D` | SFTP_SERVER_PATH | Added | Start one local server executable directly for an SFTP transfer. The value can contain a space in its pathname. |
| `-F` | CONFIGFILE | Original | Replace per-user configuration and bypass system configuration. The special file name `none` skips both. |
| `-i` | IDENTITY_FILE | Original | Offer an identity file or select the agent's matching private key with a public file. Repeat for more identities. |
| `-J` | DESTINATION | Original | Connect through ordered jump hosts. Each hop accepts an optional user and port. |
| `-l` | LIMIT | Original | Limit the transfer to LIMIT × 1024 bits/s. Use a decimal integer from 1 to 104857600. |
| `-O` | — | Original | Use legacy SCP, including its remote shell pathname interpretation. SFTP is the default. |
| `-o` | OPTION | Original | Pass a setting in SSH configuration syntax. Each occurrence consumes one argument. |
| `-P` | PORT | Original | Select the remote TCP port or a TCP service name resolved locally. |
| `-p` | — | Original | Preserve access time, modification time and mode bits. |
| `-q` | — | Original | Suppress progress and most SSH diagnostics. |
| `-R` | — | Added | Start scp on the origin for a remote-to-remote copy. It must authenticate to the destination without a password prompt. Portable 10.6p2 warns of deprecation. |
| `-r` | — | Original | Copy directory trees recursively and follow symbolic links encountered inside them. |
| `-S` | PROGRAM | Original | Select a local connection program that accepts SSH's arguments. |
| `-s` | — | Added | Explicitly select SFTP on Noble and Resolute, including after `-O`. Portable 10.6p2 ignores this compatibility flag. |
| `-T` | — | Added | Allow the remote end to choose incoming filenames without matching the requested patterns during nonrecursive legacy SCP downloads. |
| `-v` | — | Original | Print transfer and SSH debugging messages. |
| `-X` | SFTP_OPTION | Added | Tune SFTP request size or concurrency with a single key/value operand. |

**Protocol and routing.** Lowercase `-s` assigns SFTP in both Ubuntu release parsers. Portable 10.6p2 omits it from the synopsis and accepts it without changing the protocol, so `-O -s` has different results. Noble's `-3` paragraph gives conflicting accounts of the default route. Both release parsers initialize `throughlocal` to one. The final `-3` or `-R` determines the route. The manuals instruct callers to omit the target URI port under `-R`. The Ubuntu source rejects a nondefault target port and tolerates an explicit 22. [9.6p1 routing and protocol selection](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c#L508) · [10.2p1 origin-host dispatch](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L1141) · [10.6p2 compatibility handling](https://github.com/openssh/openssh-portable/blob/V_10_6_P2/scp.c#L510)

**Paths and names.** The positionals are one or more sources and one target. A local name containing a colon can be made unambiguous with `./` or an absolute path. Remote source and target forms include `[user@]host:[path]` and `scp://[user@]host[:port][/path]`. In legacy remote-to-local transfers, `sink()` enables matching only for a nonrecursive download with an expected source and without `-T`. Disabling matching still rejects invalid path components. SFTP downloads use the client's own requests. [Upstream paths and filename checks](https://man.openbsd.org/scp.1#DESCRIPTION) · [9.6p1 receiver](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c#L1698) · [10.2p1 receiver](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L1691)

## sftp inventory

All three manuals document the same 25 launch options. The released parsers also recognize a usage action. The separate option lists under INTERACTIVE COMMANDS belong to commands read after startup. [Upstream synopsis](https://man.openbsd.org/sftp.1#SYNOPSIS) · [Noble synopsis](https://manpages.ubuntu.com/manpages/noble/man1/sftp.1.html#SYNOPSIS) · [Resolute synopsis](https://manpages.ubuntu.com/manpages/resolute/man1/sftp.1.html#SYNOPSIS)

| Flag | Operand | Menu | Effect |
| --- | --- | --- | --- |
| `-4` | — | Original | Restrict SSH connections to IPv4. |
| `-6` | — | Original | Restrict SSH connections to IPv6. |
| `-A` | — | Added | Forward the authentication agent to the remote host. |
| `-a` | — | Added | Resume transfers using the existing destination length. A mismatched prefix can corrupt the resulting file. On both Ubuntu releases a resumed upload needs an existing remote file shorter than the source. |
| `-B` | BUFFER_SIZE | Original | Set the buffer size per request in bytes. Omission allows the two directions to negotiate different sizes. |
| `-b` | BATCHFILE | Original | Read a batch of commands. A single hyphen reads stdin. Checked failures stop processing unless the command has a minus prefix. |
| `-C` | — | Original | Request SSH transport compression. |
| `-c` | CIPHER | Added | Set SSH cipher preferences. |
| `-D` | SFTP_SERVER_COMMAND | Added | Start a local SFTP server over pipes. Quote the executable and any server arguments together as one option value. |
| `-F` | CONFIGFILE | Original | Supply a replacement SSH configuration file or the special value `none`. |
| `-f` | — | Added | Flush downloaded files locally and request an upload flush when the server supports `fsync@openssh.com`. |
| `-i` | IDENTITY_FILE | Original | Select an authentication identity. Repeat for multiple files. A public file can identify a key held by the agent. |
| `-J` | DESTINATION | Original | Route the SSH connection through one or more ordered jump hosts. |
| `-l` | LIMIT | Original | Limit the transfer to LIMIT × 1024 bits/s, with the same positive decimal range as scp. |
| `-N` | — | Added | Override client quiet mode, including the quiet mode implicit in `-b`. |
| `-o` | OPTION | Original | Supply one setting from the SSH configuration grammar. |
| `-P` | PORT | Original | Select the SSH port by number or locally known TCP service name. |
| `-p` | — | Original | Preserve access time, modification time and mode bits. |
| `-q` | — | Original | Hide the progress meter and most SSH diagnostics. |
| `-R` | NUM_REQUESTS | Original | Limit concurrent SFTP requests. The fallback is 64 and negotiation can reduce this default. |
| `-r` | — | Original | Transfer directory trees recursively, skipping symbolic links encountered during traversal. |
| `-S` | PROGRAM | Added | Use an alternative local SSH transport executable. |
| `-s` | SUBSYSTEM | Original | Request a remote subsystem name or, if the value contains a slash, a remote server path. |
| `-v` | — | Original | Increase SFTP and SSH diagnostic verbosity. |
| `-X` | SFTP_OPTION | Added | Set request size or concurrency with a bounded key/value operand. |
| `-h` | — | Added | Print the usage synopsis on standard error and exit with status 1. This explicit parser action has no manual entry. |

**Destination and server selection.** A normal session accepts `[user@]host[:path]` or an `sftp://` URI. A file path requests a download, and a directory or omitted path opens a session. A trailing slash forces directory interpretation. In local direct mode the Ubuntu parsers split `-D` into program and arguments and launch that command over pipes. The `scp -D` code instead passes the entire value as the executable name. [Noble sftp(1)](https://manpages.ubuntu.com/manpages/noble/man1/sftp.1.html) · [9.6p1 direct mode](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp.c#L2656) · [10.2p1 scp direct mode](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L1003)

**Resume prerequisites.** The download path opens or creates its destination, checks its length and starts reading at that offset. The upload path first queries the remote file and requires it to be smaller than the source. This makes a new upload with global resume mode fail on both Ubuntu releases. The [packaged fixture results](openssh-manual-coverage.md) exercise this difference using a local server. [9.6p1 upload](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp-client.c#L2085) · [10.2p1 upload](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp-client.c#L2076)

**SFTP request settings.** Both Ubuntu clients accept the lowercase keys `buffer=` and `nrequests=`. Each parsed value must be in the inclusive range 1–262144. Counts are decimal integers. Sizes use OpenSSH's scaled-number parser and accept, for example, `32K`. The `sftp -B` and `sftp -R` parsers use decimal `strtol`, reject a zero result and trailing text, and lack the range check of `-X`. Negative or oversized input can convert to an unintended unsigned value. Each spelling sets the same field as its corresponding `-X` key, so the last assignment wins. [9.6p1 scp parser](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c#L590) · [10.2p1 scp parser](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L577) · [9.6p1 sftp parser](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp.c#L2513) · [10.2p1 sftp parser](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp.c#L2512)

Omitted settings begin at 32768 bytes and 64 requests. Only the unset fields are adjusted using `limits@openssh.com`. Server read and write limits independently size the two buffers, subject to the client's message-size ceiling and minimum. A smaller nonzero open-handle limit can reduce the fallback request count. SFTP protocol version zero imposes a further 20480-byte buffer cap. The rate argument `-l` uses a separate parser in each transfer client. Zero and suffixes are rejected. The port parser also rejects zero but accepts a local TCP service name. [9.6p1 SFTP negotiation](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp-client.c#L565) · [10.2p1 SFTP negotiation](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp-client.c#L555) · [9.6p1 service lookup](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/misc.c#L515) · [10.2p1 service lookup](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/misc.c#L552)

## Excluded spellings

Both clients reject `-1` with a protocol-version error and silently accept the obsolete `-2` without changing behavior. The scp parser recognizes `-d` (target must be a directory), `-f` (send) and `-t` (receive) for its legacy peer protocol. Its getopt string also mentions `-M` with a required operand, but no switch case handles it, so even a supplied value ends in usage failure. None is a public transfer action. For sftp, `-h` has an explicit usage case, unlike an unknown option which also produces an invalid-option diagnostic. Configuration keywords, URI components, the `--` terminator and commands or flags accepted at the `sftp>` prompt have separate roles and do not add option rows. [9.6p1 scp parser](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c#L508) · [10.2p1 scp parser](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c#L495) · [9.6p1 sftp parser](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp.c#L2466) · [10.2p1 sftp parser](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp.c#L2465)
