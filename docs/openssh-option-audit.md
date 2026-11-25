# OpenSSH client option audit

First recorded 2026-11-22. This first pass covered 51 bundled rows. See the [expanded inventory and verification](openssh-manual-coverage.md) for the later manual comparison.

## Manual sources

| Source | Version | References |
| --- | --- | --- |
| OpenSSH upstream | OpenBSD-current manual revisions for ssh (November 2, 2026), scp (September 3, 2026), sftp (September 7, 2026) and ssh_config (October 30, 2026) | [ssh(1)](https://man.openbsd.org/ssh.1), [scp(1)](https://man.openbsd.org/scp.1), [sftp(1)](https://man.openbsd.org/sftp.1), [ssh_config(5)](https://man.openbsd.org/ssh_config.5) |
| Ubuntu 24.04 LTS (Noble) | openssh-client 1:9.6p1-3ubuntu13.20 | [ssh(1)](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html), [scp(1)](https://manpages.ubuntu.com/manpages/noble/man1/scp.1.html), [sftp(1)](https://manpages.ubuntu.com/manpages/noble/man1/sftp.1.html), [ssh_config(5)](https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html) |
| Ubuntu 26.04 LTS (Resolute) | openssh-client 1:10.2p1-2ubuntu3.8 | [ssh(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html), [scp(1)](https://manpages.ubuntu.com/manpages/resolute/man1/scp.1.html), [sftp(1)](https://manpages.ubuntu.com/manpages/resolute/man1/sftp.1.html), [ssh_config(5)](https://manpages.ubuntu.com/manpages/resolute/man5/ssh_config.5.html) |
| Existing structured value guides | OpenSSH Portable 9.9p2 | [ssh.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh.1), [scp.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/scp.1), [sftp.1](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sftp.1), [ssh_config.5](https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5) |

## Dispositions for all 51 entries

### Shared spellings

Ports, forwarding, configuration and diagnostics depended on the client.

### ssh-specific rows

The dynamic forward row distinguished its local listening socket from the remote destination.

### scp-specific rows

Uppercase `-P` supplied a port. Recursive scp followed symbolic links in the tested transfer.

### sftp-specific rows

The recursive SFTP transfer skipped the symbolic link in the same fixture.

## Version differences and numerical evidence

The audit compared 9.6p1 and 10.2p1 with upstream manuals and retained version-qualified forwarding and transfer syntax.

## Manual-only coverage

The baseline covered 51 client command-line rows. Additional documented flags and the later package comparisons are indexed in the client and transfer inventories.

## Executable checks

Ubuntu 26.04's OpenSSH 10.2p1 reported the specified port, login, IPv4 family and disabled pseudo-terminal when run with `ssh -G -F none`. This evaluated the configuration without making a connection.

A separate offline fixture compared recursive downloads from the same temporary directory. It contained a regular file and a symlink to another file outside the tree. Both clients used `-D` to communicate with a local SFTP server over subprocess pipes. Both copied the regular file. **scp copied the linked target's contents as a regular file. sftp skipped the link.** Both clients exited successfully. The server executable came from the matching Ubuntu `openssh-sftp-server` package, verified against the package index SHA-256 and extracted only in disposable sandbox storage. The Ubuntu 24.04 sandbox images provide the menu test environment without OpenSSH client binaries. [Ubuntu package](https://security.ubuntu.com/ubuntu/pool/main/o/openssh/openssh-sftp-server_10.2p1-2ubuntu3.8_amd64.deb)

## Rendered menus and offline verification

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_terminal_screen.py)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,331 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,331 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,331 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
