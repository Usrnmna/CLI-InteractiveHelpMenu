# Discovered system, container and command-line tool help

These 23 Extended routes cover 21 selectable menus and two usage-only responses. The primary replay contains 1,325 selectable spellings. A second source edition contains 1,449. Every count includes short aliases and counts a spelling once per route. The two editions are independent of the Ubuntu release running the browser. [Primary fixed replies and expected arities](../tests/fixtures/discovery-tiers/extended-tools.json) · [Second source edition](../tests/fixtures/discovery-tiers/system-resolute.json)

## Source inventory

The table gives the command actually requested. A manual request uses `man -P /bin/cat --no-hyphenation --no-justification -s 1:8 -- PAGE`. The original compressed pages came from Ubuntu's release-specific manpage archive. Compact XZ fixtures preserve their rendered text at 100 columns with the C locale, paging disabled and hyphenation and justification disabled. The primary executable replies use the installed Noble WSL captures. The later replies use the corresponding Resolute clients except for the two explicitly identified yq vendor builds. The manually maintained systemd verb table, packaged help declarations, raw definition columns and source-reference audits establish the expected switches and operands independently of discovery output. [Noble and Resolute page URLs and SHA-256 values](../tests/fixtures/discovery-tiers/system-manpages.tsv) · [Noble system capture provenance](../tests/fixtures/help/expansion-system-captures/provenance.json) · [Noble follow-up capture provenance](../tests/fixtures/help/followup-systems/manifest.json)

| Exact route | Executable request | Manual page | Noble / vendor rows | Resolute / vendor rows |
| --- | --- | --- | ---: | ---: |
| `systemctl status` | `systemctl --help` | `systemctl(1)` | 33 | 35 |
| `systemctl list-units` | `systemctl --help` | `systemctl(1)` | 34 | 36 |
| `systemctl show` | `systemctl --help` | `systemctl(1)` | 37 | 39 |
| `journalctl` | `journalctl --help` | `journalctl(1)` | 88 | 97 |
| `ssh` | Manual only | `ssh(1)` | 45 | 45 |
| `scp` | Manual only | `scp(1)` | 23 | 23 |
| `sftp` | Manual only | `sftp(1)` | 25 | 25 |
| `ip address` | `ip address help` | `ip-address(8)` | 8 | 8 |
| `ip link` | `ip link help` | `ip-link(8)` | 0 | 0 |
| `ip route` | `ip route help` | `ip-route(8)` | 0 | 0 |
| `ss` | `ss --help` | `ss(8)` | 78 | 84 |
| `openssl s_client` | `openssl s_client -help` | `openssl-s_client(1ssl)` | 181 | 193 |
| `openssl x509` | `openssl x509 -help` | `openssl-x509(1ssl)` | 73 | 78 |
| `openssl dgst` | `openssl dgst -help` | `openssl-dgst(1ssl)` | 28 | 29 |
| `podman run` | `podman run --help` | `podman-run(1)` | 156 | 167 |
| `podman build` | `podman build --help` | `podman-build(1)` | 106 | 121 |
| `podman exec` | `podman exec --help` | `podman-exec(1)` | 18 | 20 |
| `podman logs` | `podman logs --help` | `podman-logs(1)` | 12 | 12 |
| `psql` | `psql --help` | `psql(1)` | 69 | 69 |
| `yq eval` | `yq --version`, then `yq eval --help` | Vendor help only | 64 | 67 |
| `fd` | `fd --help` | Executable help only | 82 | 84 |
| `fdfind` | `fdfind --help` | `fdfind(1)` | 84 | 86 |
| `fzf` | `fzf --help` | `fzf(1)` | 81 | 131 |

## Corrections and release boundaries

- **systemd.** The three verbs receive the identical root response. A search in `systemctl show` now finds `--property=` and `--value`. A search in `list-units` finds `--recursive`. Manager actions such as `--now` and `--boot-loader-entry=` stay outside these views. The source comparison uses systemd 255.4-1ubuntu8.18 and 259.9-0ubuntu0.1. The optional IDs after journalctl's catalog listing commands are positional filters. The fixed help and heading inventory identify which commands are available in each release. [Upstream and both Ubuntu manuals](systemd-manual-coverage.md) · [Independent verb and argument table](../tests/fixtures/systemd/systemctl-inventory.tsv)
- **OpenSSH.** A single SSH forwarding rule is one operand, including the colon-separated components. The manual gives four forms for `-L` and five for `-R`. Their definitions now retain the alternatives together. The parser also recovers the required arguments of `-D`, `-W`, `-w` and SFTP's `-s`. SSH's interactive `-KL` sequence no longer becomes a command-line switch. Both editions have the same row counts, from OpenSSH 9.6p1 and 10.2p1. [Portable OpenSSH and Ubuntu sources](openssh-manual-coverage.md) · [Packaged client versions and invocations](../tests/fixtures/openssh/captures.json)
- **iproute2.** The fixed replies use iproute2 6.1.0 and 6.19.0. The address manual owns the negative selection predicates. Its prose explicitly equates `-dynamic` with `permanent` and `-permanent` with `dynamic`. The link and route replies explain a keyword grammar with zero selectable dash-option definitions. Their fixed probes exclude the independent `ip(8)` global-option page. For `ss`, `-N` and `--net` take a namespace name even when help omits the placeholder. Resolute adds the inactive-bound TCP and BPF-storage displays. [Upstream and release manuals, option and keyword inventory](iproute2-manual-coverage.md)
- **OpenSSL.** The `+int` and `PEM|DER` declarations each describe one value. Discovery now supplies it for switches including `s_client -port`, `-certform` and `dgst -xoflen`. The selected client determines availability of the three manual-only conditional TLS switches omitted from Ubuntu's builds. Likewise, `-digest` and `-*` stand for an algorithm name. The driver never asks for a digest list, so open-ended algorithm names do not become literal rows. Noble's `-engine_impl` is a switch even though the manual adds an operand. The packaged releases are 3.0.13 and 3.5.5. [Upstream and both Ubuntu manuals, option tables and fixed capture comparison](openssl-manual-coverage.md)
- **Podman.** The 4.9.3 and 5.7.0 help tables are paired with their own OPTIONS sections. The previous parser put the volume's mount suffixes, including ID mapping, under the preceding `--variant`. A full option heading now starts a new definition even when its operand has nested brackets or spaces. The build command accepts bare `--pull` or an attached value. Bare means `always`. Both Ubuntu clients map `newer` to `missing`. They differ for explicit `false`, which maps to `missing` on Noble and `never` on Resolute. The build parent option `--runtime`, a mention of `--storage` in prose, and the unimplemented run option `--link-local-ip` are excluded. The fixed help omits some working aliases that the manuals supply, including `--net`. [Build, exec and logs sources](podman-build-exec-logs-manual-coverage.md) · [Run sources](podman-run-manual-coverage.md)
- **PostgreSQL.** The versioned clients are 16.15 and 18.6. The menu describes bare `--help` and its optional attached topic. The short spelling `'-?'` is searchable with its Bash quoting guidance. The `--cluster` option belongs to Ubuntu's separate wrapper. The driver requests the client's fixed help and its SQL terminal manual. [Upstream and Ubuntu sources, client and wrapper distinction](psql-manual-coverage.md)
- **Mike Farah yq.** Both checks verify identity before accepting help. The primary source is v4.54.1 and the second vendor build is v4.54.3. Ubuntu ships Kislyuk's jq wrapper under the same name. Noble's package has no section 1 page and the Resolute page documents the other implementation. [Ubuntu and vendor references](yq-eval-option-audit.md) · [Vendor checksums and complete captures](yq-eval-manual-coverage.md)
- **fd and fdfind.** Both point to the Ubuntu `fdfind` client, 9.0.0 on Noble and 10.3.0 on Resolute. Only the `fdfind` driver requests its manual. Its OPTIONS section supplies `--mount` and `--xdev` as aliases for `--one-file-system`. Opposite settings and date aliases explicitly named within a declaration are independently searchable. The executable's `--exec <cmd>...` and `--exec-batch <cmd>...` now consume the child command name and retain the child argument boundary. [Upstream and Ubuntu manuals](fd-option-audit.md) · [Separate packaged option declarations](../tests/fixtures/fd-manual/root-help.json)
- **fzf.** The inputs are fzf 0.44.1 and 0.67.0. The long spelling in `+s, --no-sort` can be selected. A stand-alone `+i` is searchable in Details. The fixed literal grammar excludes plus-prefixed insertion. An option example in the manual previously produced a spurious `-2` row. Optional listening addresses remain optional even where the same help also prints an explicit socket path. Both the long listening variants and effect of the unsafe variant are identified in their own definitions. [Upstream and Ubuntu manuals](fzf-manual-coverage.md) · [Independent packaged declarations](../tests/fixtures/fzf-manual/root-help.json)

## Verification

The [family regression](../tests/test_discovery_system_tools.py) checks each primary spelling and arity, source boundaries and material corrections. The [second-edition terminal module](../tests/verify_system_source_editions.py) runs explicitly so the full suite does not repeat both editions during every ordinary test run. Both use the shared real Bash/tmux discovery harness. Reproduce the second pass inside each project sandbox with `PYTHONPATH=tests python3 -B -m unittest -v verify_system_source_editions`.

The 26.04 source collection invoked only Podman's four fixed help requests, the versioned psql client's help, and their version printers in the offline sandbox. The first psql collection lacked the packaged libpq dependency and exited 127. The repeated collection, with the matching extracted library, returned status zero for every request. Other executable inputs are preserved release captures. Terminal checks replay these sources and inspect the interactive menu and Readline state without starting services or executing a pending command.


The first focused selection ran 31 shared source-association tests, 29 family tests and all 23 second-edition terminal routes. A follow-up repeated the 29 family checks and four terminal cases after the final fzf and psql Details edits, using both source editions. Each successful terminal run recorded zero unexpected invocations.

| Target | Ubuntu / Python | First pass / fail / skip | Duration | Follow-up pass / fail / skip | Duration |
| --- | --- | ---: | ---: | ---: | ---: |
| `host` | 26.04.1 / 3.14.4 | 83 / 0 / 0 | 118.076 s | 33 / 0 / 0 | 23.250 s |
| `noble310` | 24.04.5 / 3.10.20 | 83 / 0 / 0 | 131.833 s | 33 / 0 / 0 | 26.896 s |
| `noble312` | 24.04.5 / 3.12.3 | 83 / 0 / 0 | 116.702 s | 33 / 0 / 0 | 23.299 s |

During setup the first host sandbox launch stopped before testing because its process namespace was unavailable. The next snapshot omitted an untracked runtime dependency and had one module import error. The corrected early host parser run passed 31/31 in 0.625 s. A separate passive development run initially passed 28/29 family cases. Its assertion for the supplied `ip route` manual expected the generic empty result. Passive import retains its source-scope diagnostic, while the normal CLI reports that neither fixed reply contained a selectable option definition. The updated check verifies that distinction. The table records the completed selections.

A check with a differently indented SSH manual also verified the generic reader fallback. After that change the same 33-case follow-up passed again, with zero failures and skips, in 23.396 s on `host`, 26.695 s on `noble310` and 23.329 s on `noble312`.
