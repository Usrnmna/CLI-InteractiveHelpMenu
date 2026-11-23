# SSH command-line inventory

The three manuals describe 46 distinct `ssh` options. Both Ubuntu manuals describe 45. OpenBSD-current adds `-Z`. The menu retains the 19 pilot rows and adds 27. There are 22 single-operand options and 24 switches, with no documented alternate spelling for a top-level option. [SSH profile](../profiles/ssh.json) · [OpenSSH family revisit](openssh-manual-coverage.md)

## Sources

| Reference | ssh(1) revision | ssh_config(5) revision |
| --- | --- | --- |
| OpenBSD-current | [1.458, November 2, 2026](https://man.openbsd.org/ssh.1) | [1.435, October 30, 2026](https://man.openbsd.org/ssh_config.5) |
| Ubuntu 24.04 Noble, openssh-client 1:9.6p1-3ubuntu13.20 | [1.438, October 11, 2023](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html) | [1.391, October 12, 2023](https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html) |
| Ubuntu 26.04 Resolute, openssh-client 1:10.2p1-2ubuntu3.8 | [1.444, December 4, 2024](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html) | [1.420, October 4, 2025](https://manpages.ubuntu.com/manpages/resolute/man5/ssh_config.5.html) |

The Ubuntu package revisions identify the distribution-specific manuals. The revision numbers and dates are the OpenBSD source markers in the distributed manual files. The command in both packages is `/usr/bin/ssh`. The corresponding Portable parsers establish flag arity and command boundaries. The pinned newer Portable source matches the OpenBSD-current manual revision. The pilot value guides retain their Portable 9.9p2 evidence. The port guide also covers 9.6p1 and 10.2p1 after checking all three conversion functions and callers. [Portable 9.6p1 ssh.c](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_9_6_P1) · [Portable 10.2p1 ssh.c](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_10_2_P1) · [Newer Portable ssh.c](https://anongit.mindrot.org/openssh.git/tree/ssh.c?id=fa4b2a82be7df9768272cfabc2d78e4a12c2b3c0) · [9.9p2 ssh(1)](https://anongit.mindrot.org/openssh.git/tree/ssh.1?h=V_9_9_P2)

## Manual inventory

Each row represents one option heading, with repeated headings for alternate `-L` and `-R` operands counted once. The separate `ssh -Q query_option` synopsis contributes `-Q`. A dash in the operand column means no operand. A required operand may follow a space or attach directly, as in `-p 2222` and `-p2222`. There is no short-option equals separator. In `-p=2222`, the operand starts with a literal equals sign. Switches may be bundled. A value-taking member consumes the rest of its token or the next argument. The menu inserts the short spelling and a space for further editing. [Noble synopsis](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html#synopsis) · [Resolute synopsis](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html#synopsis) · [Upstream synopsis](https://man.openbsd.org/ssh.1#SYNOPSIS)

| Flag | Operand | Scope | Menu | Effect |
| --- | --- | --- | --- | --- |
| `-4` | — | all | original | Use IPv4. |
| `-6` | — | all | original | Use IPv6. |
| `-A` | — | all | added | Make the local authentication agent available through the connection. |
| `-a` | — | all | added | Disable agent forwarding. |
| `-B` | `INTERFACE` | all | added | Bind the outgoing connection to a local interface. |
| `-b` | `BIND_ADDRESS` | all | added | Select a local source address. |
| `-C` | — | all | original | Request compression for session and forwarded data. |
| `-c` | `CIPHER_SPEC` | all | added | Set the ordered list of encryption ciphers. |
| `-D` | `ADDRESS` | all | original | Listen on a local port for SOCKS clients. |
| `-E` | `LOG_FILE` | all | original | Append diagnostics to a local file. |
| `-e` | `ESCAPE_CHAR` | all | added | Set or disable the terminal session escape character. |
| `-F` | `CONFIGFILE` | all | original | Replace the per-user configuration and bypass the system file. |
| `-f` | — | all | added | Background the process after authentication. |
| `-G` | — | all | added | Print the configuration evaluated for the destination. |
| `-g` | — | all | added | Permit other hosts to connect to local forwarded ports. |
| `-I` | `PKCS11_LIBRARY` | all | added | Select a local PKCS#11 provider. |
| `-i` | `IDENTITY_FILE` | all | original | Select an authentication identity. |
| `-J` | `DESTINATION` | all | original | Connect through the listed jump hosts in order. |
| `-K` | — | all | added | Enable GSSAPI authentication and credential delegation. |
| `-k` | — | all | added | Disable delegation of GSSAPI credentials. |
| `-L` | `ADDRESS` | all | original | Listen locally and reach the destination from the SSH server. |
| `-l` | `USER` | all | original | Select the remote login name. |
| `-M` | — | all | added | Establish a connection-sharing master. |
| `-m` | `MAC_SPEC` | all | added | Choose message authentication codes in preference order. |
| `-N` | — | all | original | Connect without starting a remote command. |
| `-n` | — | all | original | Prevent the client from reading standard input. |
| `-O` | `CONTROL_COMMAND` | all | added | Send a request to a running multiplexing master. |
| `-o` | `OPTION` | all | original | Pass one client configuration setting. |
| `-P` | `TAG` | all | added | Supply a configuration tag for Match tagged. |
| `-p` | `PORT` | all | original | Choose the port of the remote SSH server. |
| `-Q` | `QUERY` | all | added | Report a capability of the local client. |
| `-q` | — | all | original | Suppress most diagnostics. |
| `-R` | `ADDRESS` | all | original | Listen on the server and reach the destination from the client. |
| `-S` | `CONTROL_PATH` | all | added | Select or disable a local connection-sharing socket. |
| `-s` | — | all | added | Request the remote subsystem named after the destination. |
| `-T` | — | all | original | Disable pseudo-terminal allocation. |
| `-t` | — | all | original | Force pseudo-terminal allocation. |
| `-V` | — | all | added | Write the client version to standard error and exit. |
| `-v` | — | all | original | Increase diagnostic verbosity. |
| `-W` | `HOST:PORT` | all | added | Carry standard input and output to a TCP destination through SSH. |
| `-w` | `LOCAL_TUN[:REMOTE_TUN]` | all | added | Request specified or automatically allocated tunnel devices. |
| `-X` | — | all | added | Enable X11 forwarding under the configured trust policy. |
| `-x` | — | all | added | Disable X11 forwarding. |
| `-Y` | — | all | added | Enable trusted X11 forwarding. |
| `-y` | — | all | added | Send diagnostics to syslog. |
| `-Z` | — | OpenBSD-current | added | List the public keys that would be offered for a destination. Both Ubuntu clients reject this option. |

## Parser and release distinctions

- **Forwarded endpoints.** In `-L`, the client listens and the server opens the outgoing connection. In `-R`, the server listens and the client opens the outgoing connection. Both accept four combinations of a TCP or Unix-socket listener and a TCP or Unix-socket destination. A destination-free remote TCP listener becomes a SOCKS proxy. Remote port zero requests server allocation, and `-O forward` prints the assigned port. For `-D`, the documented listener is a local TCP port. The SOCKS request selects the destination reached from the server. The shared parser also accepts a path-shaped dynamic-forwarding argument. The menu presents the documented TCP interface. [Noble ssh(1)](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html#R) · [Resolute ssh(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html#D) · [Portable forwarding parser](https://anongit.mindrot.org/openssh.git/tree/readconf.c?h=V_10_2_P1)
- **Forwarding trust.** Upstream `-X` defaults to restricted X11 forwarding. Both Ubuntu manuals document the distribution default `ForwardX11Trusted yes`. The row gives the explicit restricted invocation `-X -o ForwardX11Trusted=no`. The `-Y` switch explicitly enables trusted access to the local display. Separately, `-A` exposes an authentication-agent socket to the remote side. A process with access to it can request signatures while the private keys stay local. [Upstream X11 policy](https://man.openbsd.org/ssh_config.5#ForwardX11Trusted) · [Noble X11 policy](https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html#ForwardX11Trusted) · [Resolute X11 policy](https://manpages.ubuntu.com/manpages/resolute/man5/ssh_config.5.html#ForwardX11Trusted) · [Agent forwarding](https://man.openbsd.org/ssh.1#A)
- **Multiplexing.** `-M` establishes a master, `-S` identifies its local socket, and `-O` takes a control request. A second `-M` requests confirmation. Both Ubuntu parsers recognize `check`, `forward`, `cancel`, `proxy`, `stop` and `exit`. The Noble manual omits the working `proxy` selector. OpenBSD-current additionally documents `conninfo` and `channels`. Both Ubuntu-era parsers reject those requests. `stop` leaves existing sessions running while refusing new sharing requests. `exit` requests termination. [Noble control operations](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html#O) · [Resolute control operations](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html#O) · [Upstream control operations](https://man.openbsd.org/ssh.1#O) · [9.6p1 control parser](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_9_6_P1#n792) · [10.2p1 control parser](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_10_2_P1#n812)
- **Capabilities and identities.** `-G` evaluates a destination's settings, including Host and Match clauses. `-Q` needs no destination and lists locally supported algorithms or other capabilities. The algorithm-list configuration keywords accepted by `-Q` are queries within its operand grammar. The OpenBSD-current manual includes `addressfamily`. Both Ubuntu manuals list `kex-gss`. The Portable source also accepts `compression`. `-Z` displays locally available public keys in authentication preference order for a destination. Only the newer upstream client in this comparison implements it. Neither Ubuntu release lists it in fixed usage or handles it in its parser. [Upstream queries](https://man.openbsd.org/ssh.1#Q) · [Noble queries](https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html#Q) · [Resolute queries](https://manpages.ubuntu.com/manpages/resolute/man1/ssh.1.html#Q) · [Upstream identity selection](https://man.openbsd.org/ssh.1#Z)
- **Values.** `-p` accepts a decimal TCP port from 1 through 65535 or a name resolvable in the local TCP service database. For `-w`, a device ID is a unitless decimal integer from 0 through 2147483645 at the parser, or the case-insensitive keyword `any`. A missing remote device means `any`. Actual allocation depends on tunnel-device availability and permission. `-W` takes one TCP destination on the far side of the SSH connection. It implies a session with neither a remote command nor a pseudo-terminal. [9.9p2 port conversion](https://anongit.mindrot.org/openssh.git/tree/misc.c?h=V_9_9_P2#n536) · [9.6p1 port and tunnel conversion](https://anongit.mindrot.org/openssh.git/tree/misc.c?h=V_9_6_P1) · [10.2p1 port and tunnel conversion](https://anongit.mindrot.org/openssh.git/tree/misc.c?h=V_10_2_P1#n552) · [Tunnel ID constants](https://anongit.mindrot.org/openssh.git/tree/misc.h?h=V_10_2_P1#n150) · [Standard-stream forwarding](https://man.openbsd.org/ssh.1#W)
- **Command boundary and exclusions.** Before a remote command starts, the executable can parse client options immediately following the destination unless `--` ended option parsing. Once a remote command starts, its remaining words are joined with spaces for the server. The menu keeps its existing first-positional boundary so local suggestions stop at the destination. `-1` gives a fatal protocol-version diagnostic and `-2` is an ignored compatibility spelling. Neither selects an operation. The `--` terminator, session escapes, remote commands and configuration keywords belong to separate grammars and get no option row. [9.6p1 argument handling](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_9_6_P1#n747) · [10.2p1 argument handling](https://anongit.mindrot.org/openssh.git/tree/ssh.c?h=V_10_2_P1#n1131) · [SSH escape characters](https://man.openbsd.org/ssh.1#ESCAPE_CHARACTERS)
