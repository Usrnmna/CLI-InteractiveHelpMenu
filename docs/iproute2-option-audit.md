# iproute2 listing and socket option audit

The first pass covered 36 entries: eight for `ip address`, seven for `ip link`, nine for `ip route` and twelve for `ss`. The three `ip` profiles cover listing commands. A keyword such as `nomaster` has a different effect after `set`. The `ss` profile covers socket selection and display. All four retain their selection order, operand labels and literal insertions.

The [manual-coverage revisit](iproute2-manual-coverage.md) expands these four listings to 175 spellings and records the release differences and verification. The dispositions and suite counts below describe the original pass.

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

| Keyword | Disposition | Menu decision |
| --- | --- | --- |
| `show` | Incomplete | Name the objects listed and explain the default invocation. |
| `dev IFNAME` | Incomplete | Restrict the address listing to one named interface, such as `lo`. |
| `scope SCOPE` | Redundant | Replace numerical boilerplate with the meanings of `host`, `link` and `global`. Retain numeric scope IDs. |
| `to PREFIX` | Incomplete | Match a local address inside the prefix. A bare address selects a single host address. |
| `label PATTERN` | Inaccurate | Match an address label. Single quotes preserve shell wildcards such as `'eth0:*'`. |
| `up` | Inaccurate | Match the administrative UP flag. Carrier can be absent. |
| `dynamic` | Incomplete | Match addresses lacking the permanent flag. Stateless autoconfiguration is one possible origin. |
| `permanent` | Incomplete | Match the opposite flag state and give the explicit IPv6-only invocation. |

### ip link

| Keyword | Disposition | Menu decision |
| --- | --- | --- |
| `show` | Incomplete | Identify interfaces in the current network namespace as the objects listed. |
| `dev IFNAME` | Incomplete | Inspect the named device and its attributes. |
| `up` | Inaccurate | Match the administrative flag independently of carrier. |
| `type TYPE` | Incomplete | A link kind such as `bridge` selects the bridges themselves. An unrecognized kind can yield no devices. |
| `master DEVICE` | Incomplete | Show member devices. For a bridge, these are its ports. |
| `nomaster` | Sufficient as written | Retain the membership criterion. Distinguish listing unattached devices from releasing a device with `link set nomaster`. |
| `group GROUP` | Redundant | Accept a device group ID or configured name. Group membership is independent of master membership. |

### ip route

| Keyword | Disposition | Menu decision |
| --- | --- | --- |
| `show` | Incomplete | Explain the ordinary IPv4/main-table default, IPv6 selection and the separate `get` lookup. |
| `dev IFNAME` | Incomplete | Specify the outgoing interface. |
| `table TABLE` | Incomplete | Explain `main`, `local` and the cross-table selector `all`. The table named `default` is separate from the usual listing table. |
| `proto PROTOCOL` | Incomplete | Identify the route's origin, for example `kernel` or `static`. The operand accepts a name or protocol ID. |
| `scope SCOPE` | Redundant | Explain what the selected scope means for reachability. Keep named and numeric forms. |
| `type TYPE` | Incomplete | Explain the effects represented by local and blackhole entries and which tables to inspect. |
| `to PREFIX` | Incomplete | Match the exact destination prefix by default. `root` includes more-specific entries, and `match` includes covering entries. |
| `via ADDRESS` | Incomplete | Match a gateway address or gateway prefix. The optional gateway family precedes the address. |
| `src ADDRESS` | Incomplete | Filter on the route's preferred source for locally generated traffic. An address or prefix is accepted. |

### ss

| Option | Disposition | Menu decision |
| --- | --- | --- |
| `--all` | Inaccurate | Include listening and non-listening sockets. The latter can include unconnected UDP sockets. |
| `--listening` | Incomplete | Keep the listening summary and explain how unconnected UDP sockets appear. |
| `--numeric` | Inaccurate | Suppress service-name lookup and show exact bandwidth values when reported. Hostname resolution uses a separate switch. Correct both prose and structured output guidance. |
| `--tcp` | Sufficient as written | Keep the summary and explain how to include listeners. |
| `--udp` | Sufficient as written | Keep the summary and describe `--all` for unconnected sockets. |
| `--processes` | Incomplete | Identify the name, PID and file descriptor, subject to visibility of the process. |
| `--ipv4` | Redundant | Retain the family selector and its no-operand contract. Show how to narrow by transport. |
| `--ipv6` | Redundant | Apply the corresponding IPv6 guidance. |
| `--extended` | Incomplete | Identify the owner UID, inode and socket cookie that may appear. |
| `--no-header` | Sufficient as written | Keep the original one-line explanation. |
| `--query=QUERY` | Redundant | Keep comma separation and exclusions. Show the quoted Bash spelling `--query='all,!tcp'`. |
| `--filter=FILE` | Incomplete | Show a port predicate and the `-` operand for standard input. |

## Manual qualifications and coverage

Both Ubuntu manuals and upstream describe `up` as “running”. The listing code tests `IFF_UP`; it can show `NO-CARRIER` on an administratively up link. The address manuals describe `dynamic` and `permanent` under IPv6 stateless configuration. The listing code tests opposite states of `IFA_F_PERMANENT` and the IPv4 loopback fixture below also matched `permanent`. These flags cannot establish which service assigned an address. [Address and link filtering](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/ip/ipaddress.c?h=v7.3.0)

For `ip address show to`, the prefix tests membership of a local address. For `ip route show to`, a prefix without a modifier selects an entry with the same network and prefix length. Both `root` and `match` include an exact match. The route listing compares `src` with the preferred-source attribute and `via` with the gateway. The menu inserts `proto`, an accepted abbreviation of the manual's `protocol` keyword. An ordinary bare IP address uses its full address-family width. [Route selection](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/ip/iproute.c?h=v7.3.0) · [Prefix parsing](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/lib/utils.c?h=v7.3.0)

The two joined `ss` rows insert the long spelling through the equals sign. The manuals also document `-A QUERY`, `--socket=QUERY` and `-F FILE`. A filter file supplies socket-expression input. The parser accepts whitespace-separated terms such as `sport = :443`. Process information depends on the file descriptors visible through procfs. [Filter lexer](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/misc/ssfilter.y?h=v7.3.0) · [Socket reporting](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/tree/misc/ss.c?h=v7.3.0)

Manual-only coverage includes address lifetimes, tentative and deprecated flags, address modification and flushing, link creation and configuration, VRFs and link-kind-specific parameters, route maintenance, policy attributes, metrics and multipath operands. Socket memory, timers, TCP internals, events, state expressions and additional socket families also remain in the manuals. Resolute documents `ip link show down` and the `ss` options `--bound-inactive`, `--no-queues` and `--bpf-maps` beyond Noble's manual. None is a bundled row. Discovery-path review remains a separate roadmap item.

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
