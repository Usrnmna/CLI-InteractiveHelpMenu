# iproute2 listing and socket option audit

First recorded 2026-11-22. This first pass covered 36 bundled rows. See the [expanded inventory and verification](iproute2-manual-coverage.md) for the later manual comparison.

## Sources and versions

| Bundled menu | Upstream iproute2 7.3.0 | Ubuntu 24.04 LTS, 6.1.0-1ubuntu6.4 | Ubuntu 26.04 LTS, 6.19.0-1ubuntu1.1 |
| --- | --- | --- | --- |
| [ip address](../profiles/ip-address.json) | [ip-address(8)](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/man/man8/ip-address.8.in?h=v7.3.0) | [Noble ip-address(8)](https://manpages.ubuntu.com/manpages/noble/man8/ip-address.8.html) | [Resolute ip-address(8)](https://manpages.ubuntu.com/manpages/resolute/man8/ip-address.8.html) |
| [ip link](../profiles/ip-link.json) | [ip-link(8)](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/man/man8/ip-link.8.in?h=v7.3.0) | [Noble ip-link(8)](https://manpages.ubuntu.com/manpages/noble/man8/ip-link.8.html) | [Resolute ip-link(8)](https://manpages.ubuntu.com/manpages/resolute/man8/ip-link.8.html) |
| [ip route](../profiles/ip-route.json) | [ip-route(8)](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/man/man8/ip-route.8.in?h=v7.3.0) | [Noble ip-route(8)](https://manpages.ubuntu.com/manpages/noble/man8/ip-route.8.html) | [Resolute ip-route(8)](https://manpages.ubuntu.com/manpages/resolute/man8/ip-route.8.html) |
| [ss](../profiles/ss.json) | [ss(8)](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/man/man8/ss.8?h=v7.3.0) | [Noble ss(8)](https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html) | [Resolute ss(8)](https://manpages.ubuntu.com/manpages/resolute/man8/ss.8.html) |

The upstream release archive contains all four manuals. The structured value guidance retains its existing 6.13.0 scope. The reference for each link and route `dev` entry now points to the corresponding listing command. The prefix grammar retains the IPv4 and IPv6 bit limits and specifies what a bare address selects. [Upstream 7.3.0 release](https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-7.3.0.tar.xz) · [Pinned 6.13.0 release](https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-6.13.0.tar.xz)

## Disposition of the original entries

### ip address

Address-prefix filtering tested membership. Dynamic and permanent reflected address flags.

### ip link

The listing keyword `up` selected administrative state, including an interface without carrier.

### ip route

A bare prefix following `to` selected an exact network and length. The `root` and `match` forms also included an exact match.

### ss

`--numeric` suppressed service-name lookup and printed exact bandwidth values. Visibility of process details depended on access to the owning descriptors.

## Manual qualifications and coverage

The ip profiles covered listing operations. The meaning of a keyword can change after `set`. The socket filter accepted a file or stdin, and the joined query row inserted a literal equals sign.

## Executable and terminal verification

The fixtures ran read-only `ip` listings in a private network namespace on each target. Resolute supplied iproute2 6.19.0. Both Noble sandboxes used the extracted Ubuntu 6.1.0 package and its libraries in disposable storage. Only the socket fixture opened endpoints, using ephemeral loopback ports. [Ubuntu Noble binary package](https://archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_6.1.0-1ubuntu6.4_amd64.deb)

- **Address and link.** The IPv4 loopback address matched the host scope, the `127.0.0.0/8` prefix, the `l*` label and the permanent flag. The dynamic listing omitted it. Link selection agreed with the interface's UP flag. The default group and no-master selectors found the loopback device. An unknown link kind produced no plain-text device rows.
- **Route.** In the local table, `to 127.0.0.0/8` returned just that prefix. Adding `root` included the host route for `127.0.0.1`. Using `match 127.0.0.1` returned both entries. A kernel/local route matched the loopback device, host scope and preferred source. An unrelated gateway matched no entry.
- **Socket.** A private TCP listener appeared with `--listening` and `--all` and disappeared from the default TCP listing. A bound UDP socket appeared as `UNCONN`. IPv6 selection omitted the IPv4 listener. The owning process and extended inode/cookie fields were visible. File and stdin forms of the same port filter reproduced the command-line result. With traffic on a private TCP connection, the send rate in `ss --info` changed from scaled Gbps to integer bps with `--numeric` on all three targets.

A separate Bash/tmux run on each target compared all 36 highlighted labels, summaries and full Details panes at 210×100. Each menu restored the pending line and cursor on cancellation. Selection inserted `dev` in the address and link menus, `to` in route and `--query=` in ss, preserving the suffix each time. Shell stubs would have recorded any execution of the pending command. No execution occurred. At 60×16 the route regression searched for “covering routes”, scrolled to the `to match PREFIX` guidance, cancelled, then repeated the search and inserted the keyword. [Terminal regression](../tests/test_expansion_terminal.py) · [Offline sandbox](development.md#isolated-local-debugging)

At 60×16 the other three menus also exposed their qualifications through search. “no carrier” found the address `up` filter, “ports attached” found the link `master` filter, and “exclude it” found the socket-table query. Typing `'all,!tcp'` immediately after the inserted `--query=` preserved the existing ` --numeric` suffix.

The numerical inventory flagged 47 changed fingerprints across these four files, their headers and categories, and the affected option or keyword records. The checked facts included prefix widths, selector IDs, address-family switches, joined-value syntax and numeric rate output. The inventory check passed after those records were refreshed. [Numerical review](numerical-inventory/review.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 12 / 0 / 0 | 1,339 / 0 / 1 | 472.881 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 12 / 0 / 0 | 1,339 / 0 / 1 | 534.898 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 12 / 0 / 0 | 1,339 / 0 / 1 | 473.193 s |

The full suite included the untracked audit documents and ran the shell syntax checks, numerical coverage gate and profile validation with and without the example drivers. The one skip on each target was the Windows-specific probe limitation. These results cover local sandboxes.
