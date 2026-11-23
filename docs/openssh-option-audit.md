# OpenSSH client option audit

The first-pass menus contained 19 [ssh entries](../profiles/ssh.json), 15 [scp entries](../profiles/scp.json) and 17 [sftp entries](../profiles/sftp.json). All 51 command-line rows were compared with the manuals and inspected in real Bash/tmux sessions on the three supported sandbox targets. Each client retains its original option order, argument placeholders, insertion spelling and positional boundary.

The [full manual-coverage revisit](openssh-manual-coverage.md) records the expanded menus, release-specific options and subsequent verification.

## Manual sources

| Source | Version | References |
| --- | --- | --- |
| OpenSSH upstream | OpenBSD-current manual revisions for ssh (November 2, 2026), scp (September 3, 2026), sftp (September 7, 2026) and ssh_config (October 30, 2026) | [ssh(1)](https://man.openbsd.org/ssh.1), [scp(1)](https://man.openbsd.org/scp.1), [sftp(1)](https://man.openbsd.org/sftp.1), [ssh_config(5)](https://man.openbsd.org/ssh_config.5) |
| Ubuntu 24.04 LTS (Noble) | openssh-client 1:9.6p1-3ubuntu13.20 | [ssh(1)](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html), [scp(1)](https://manpages.ubuntu.com/manpages/noble/man1/scp.1.html), [sftp(1)](https://manpages.ubuntu.com/manpages/noble/man1/sftp.1.html), [ssh_config(5)](https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html) |
| Ubuntu 26.04 LTS (Resolute) | openssh-client 1:10.2p1-2ubuntu3.8 | [ssh(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html), [scp(1)](https://manpages.ubuntu.com/manpages/resolute/man1/scp.1.html), [sftp(1)](https://manpages.ubuntu.com/manpages/resolute/man1/sftp.1.html), [ssh_config(5)](https://manpages.ubuntu.com/manpages/resolute/man5/ssh_config.5.html) |
| Existing structured value guides | OpenSSH Portable 9.9p2 | [ssh.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh.1), [scp.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/scp.1), [sftp.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sftp.1), [ssh_config.5](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5) |

## Dispositions for all 51 entries

The tables assess the original summary and Details together. The first table covers nine flags in each client (27 entries). The remaining tables cover 10 ssh, six scp and eight sftp entries. All three menu headers now describe what the command does.

### Shared spellings

| Flag | ssh | scp | sftp | Finding and revision |
| --- | --- | --- | --- | --- |
| `-4` | Redundant | Redundant | Redundant | Restricts connections to IPv4. Remove the explanation that the digit is not a measurement. |
| `-6` | Redundant | Redundant | Redundant | Restricts connections to IPv6. The flag takes no operand. |
| `-C` | Incomplete | Sufficient | Sufficient | The ssh Details include both session data and forwarded connections. Both transfer clients request SSH compression. |
| `-F` | Incomplete | Incomplete | Incomplete | An alternate user configuration bypasses the system configuration. The special value `none` skips both. The value guide also recognizes `none`. |
| `-i` | Inaccurate | Inaccurate | Inaccurate | The original summary implied a private key file was required. A public key file can select a matching private key in the agent. Multiple identities can be supplied by repeating the flag. Correct the value guide as well. |
| `-J` | Incomplete | Incomplete | Incomplete | Preserve the ordered, comma-separated hop syntax with optional login and port. Explain that command-line settings generally apply to the final destination. Jump hosts can have their own configuration. |
| `-o` | Redundant | Redundant | Redundant | Keep the `ssh_config` keyword/value syntax and the key-specific interpretation. Replace the browser implementation detail with a single usable argument. |
| `-q` | Incomplete | Incomplete | Incomplete | ssh suppresses most warnings and diagnostics. Both transfer clients also suppress the progress meter. |
| `-v` | Incomplete | Incomplete | Incomplete | ssh supports up to three verbosity levels. scp shows diagnostics for both the copy and the SSH connection. sftp increases its logging and passes the option to ssh. |

### ssh-specific rows

| Flag | Disposition | Finding and revision |
| --- | --- | --- |
| `-p PORT` | Redundant | The configured port applies when omitted and defaults to 22. Remove comparisons to physical units. |
| `-l USER` | Sufficient | Retain the remote-login summary and the existing username operand. |
| `-L ADDRESS` | Incomplete | Listen on the client and connect to the destination from the server. Spell out all four combinations of TCP and Unix-socket endpoints. |
| `-R ADDRESS` | Incomplete | Listen on the server and connect from the client. Show the destination-free SOCKS form alongside the four fixed-destination forms. Retain port 0 allocation and describe the server's bind-address policy. |
| `-D ADDRESS` | Inaccurate | The old prose and structured grammar called Unix sockets a documented alternative. The manuals give `[bind_address:]port`. The client opens a local SOCKS listener and the application chooses the destination. |
| `-N` | Sufficient | The original command restriction was correct. A forwarding-only session illustrates why to select it. |
| `-T` | Sufficient | Retain the pseudo-terminal allocation description. |
| `-t` | Incomplete | Force pseudo-terminal allocation. Explicitly distinguish `-tt` when there is no local terminal. |
| `-n` | Incomplete | Prevent reading standard input. This matters for background sessions and loops whose input belongs to the calling shell. |
| `-E LOG_FILE` | Incomplete | Append diagnostics to the selected file in place of standard error. |

### scp-specific rows

| Flag | Disposition | Finding and revision |
| --- | --- | --- |
| `-P PORT` | Redundant | Keep the configured/default port rule and make uppercase `-P` visible beside lowercase preservation mode. |
| `-p` | Incomplete | Specify access time, modification time and file mode bits. |
| `-r` | Incomplete | Recursive traversal follows symbolic links. A target outside the copied tree can therefore be included. |
| `-l LIMIT` | Redundant | Keep the 1024-bit/s unit, integer range, no-suffix rule and zero rejection. Omitting the flag leaves this limit unset. |
| `-O` | Incomplete | SFTP is the default. Legacy SCP uses the remote shell for path interpretation and can be necessary for older servers, wildcard patterns or tilde expansion. |
| `-S PROGRAM` | Incomplete | The connection program must accept ssh command-line options. |

### sftp-specific rows

| Flag | Disposition | Finding and revision |
| --- | --- | --- |
| `-P PORT` | Redundant | Name the uppercase port selector and retain the configured/default port. |
| `-b BATCHFILE` | Incomplete | A single hyphen reads the batch from standard input. Use noninteractive authentication. Failed transfers normally stop the batch, and a command prefix can suppress that termination. |
| `-B BUFFER_SIZE` | Redundant | Show the byte unit, memory trade-off and 32768-byte fallback. Server negotiation can select different read and write sizes. Retain the parser qualifications in the structured value guide. |
| `-R NUM_REQUESTS` | Redundant | Limit concurrent requests. The fallback is 64 and a negotiated server limit can reduce it. This is distinct from buffer size and recursive transfer. |
| `-l LIMIT` | Redundant | Retain the same verified bandwidth scale, integer bounds and zero rule as scp. |
| `-r` | Incomplete | Recursive uploads and downloads skip symbolic links encountered during traversal. |
| `-p` | Incomplete | Preserve access and modification times and file mode bits. |
| `-s SUBSYSTEM` | Incomplete | Accept either an SSH subsystem name or the path to the SFTP server executable on the remote host. |

## Version differences and numerical evidence

**Forwarding and identity selection.** All three ssh manuals and the pinned 9.9p2 manual document a TCP listener for `-D`. The 9.9p2 shared forwarding parser also recognizes path-shaped input. That implementation detail does not establish a documented dynamic-forwarding interface. Fixed local and remote forwarding explicitly document Unix-socket endpoints. The three manuals agree on selecting an agent key with a public key file. Their lists of default identities differ: Noble includes `id_dsa`, Resolute omits it, and the current upstream page includes `id_mldsa44_ed25519`. The menu avoids a version-dependent default filename list. [Pinned forwarding parser](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/readconf.c#L3150), [upstream ssh](https://man.openbsd.org/ssh.1), [Noble ssh](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html) and [Resolute ssh](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html)

**Transfer rates.** The manuals label the `-l` unit Kbit/s. The 9.9p2 clients accept decimal integers from 1 through 104857600 and multiply by 1024 to obtain bits per second. Zero and unit suffixes are rejected. The value guide remains scoped to that release. The corresponding Portable 9.6p1 and 10.2p1 parsers use the same scale. [scp 9.9p2](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/scp.c#L561), [sftp 9.9p2](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sftp.c#L2545), [scp 9.6p1](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/scp.c), [sftp 9.6p1](https://github.com/openssh/openssh-portable/blob/V_9_6_P1/sftp.c), [scp 10.2p1](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/scp.c) and [sftp 10.2p1](https://github.com/openssh/openssh-portable/blob/V_10_2_P1/sftp.c)

**SFTP request and buffer defaults.** The manuals give 32768 bytes and 64 requests. In the pinned client these are fallbacks. When `limits@openssh.com` is available and the caller omits the corresponding flag, the read and write limits govern the two buffer sizes, and a nonzero server handle limit can reduce the request count. Protocol version 0 imposes a further 20480-byte buffer cap. The legacy `-B` and `-R` decimal parsers reject zero and trailing text, but oversized or negative input can wrap or truncate during conversion. The separate `-X` bounds do not define these flags. [9.9p2 parsing](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sftp.c#L2516) and [9.9p2 client negotiation](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sftp-client.c#L565)

## Manual-only coverage

These top-level options fell outside the original 51-row selection. Each option is counted under the program that owns it. SSH configuration keywords, ssh session escapes and commands entered at the interactive `sftp>` prompt have separate grammars.

| Client | Additional documented switches and differences |
| --- | --- |
| ssh | Common to all three manuals: `-A -B -G -I -K -M -O -P -Q -S -V -W -X -Y -a -b -c -e -f -g -k -m -s -w -x -y`. OpenBSD-current also documents `-Z` for listing the public keys the client would try. |
| scp | All three describe `-3 -A -B -D -R -T -X -c`. Both Ubuntu synopses and the pinned 9.9p2 synopsis also include lowercase `-s` without a separate option description. The current upstream synopsis omits it. |
| sftp | All three describe `-A -D -N -S -X -a -c -f`. Flags for interactive commands such as `ls -l` are outside this command-line count. |

## Executable checks

Ubuntu 26.04's OpenSSH 10.2p1 reported the specified port, login, IPv4 family and disabled pseudo-terminal when run with `ssh -G -F none`. This evaluated the configuration without making a connection.

A separate offline fixture compared recursive downloads from the same temporary directory. It contained a regular file and a symlink to another file outside the tree. Both clients used `-D` to communicate with a local SFTP server over subprocess pipes. Both copied the regular file. **scp copied the linked target's contents as a regular file. sftp skipped the link.** Both clients exited successfully. The server executable came from the matching Ubuntu `openssh-sftp-server` package, verified against the package index SHA-256 and extracted only in disposable sandbox storage. The Ubuntu 24.04 sandbox images provide the menu test environment without OpenSSH client binaries. [Ubuntu package](https://security.ubuntu.com/ubuntu/pool/main/o/openssh/openssh-sftp-server_10.2p1-2ubuntu3.8_amd64.deb)

## Rendered menus and offline verification

On each target, Bash/tmux opened all three unfiltered bundled menus at 180×100. Inspection traversed every row in order and checked the command header, literal option declaration, entire summary and Details prose. The checks also confirmed the corrected `-D` grammar and the visible 64-request fallback.

At 60×16 the focused regression searches for “remote listener” in ssh and “symbolic links” in both transfer clients. It scrolls to the qualification, checks each client's guidance, cancels to the original pending line and cursor, then reopens the menu and inserts the literal flag before an existing operand. Execution-detecting shell stubs recorded zero invocations. The four focused tests passed on each target, covering the terminal interactions, SFTP defaults, bandwidth scale and reviewed inventory. The full suite also includes the prior untracked audit documents in each snapshot. [Terminal regression](../tests/test_terminal_screen.py) and [sandbox instructions](development.md#isolated-local-debugging)

An additional insertion check on each target selected the remote-port row before an existing `2222 destination` suffix. The inserted option was lowercase `-p` for ssh and uppercase `-P` for both transfer clients. The original port and destination remained intact, with the cursor at the start of the port.

To reproduce the focused menu test, replace TARGET with `host`, `noble310` or `noble312`.

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_terminal_screen.py -k test_openssh_forwarding_and_recursive_copy_guidance -v
```

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,331 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,331 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,331 | 0 | 1 |

The single skip in each run was the Windows-specific probe test. The coverage gates and bundled-profile validation passed on all three targets.
