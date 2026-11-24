# OpenSSL manual coverage

The three menus grew from 33 first-pass rows to 370. Each option and separate alias spelling has an insertable row. The fixed digest lists supply concrete spellings for the open-ended digest selector in the certificate and digest manuals.

| Command | Original | Added | Total | Fixed named options in Noble / Resolute / upstream | Additional coverage |
| --- | ---: | ---: | ---: | --- | --- |
| `openssl s_client` | 12 | 198 | 210 | 181 / 193 / 203 | Three conditional spellings absent from all three fixed help listings |
| `openssl x509` | 11 | 93 | 104 | 73 / 78 / 78 | 79 named options across versions and 25 digest names |
| `openssl dgst` | 10 | 46 | 56 | 28 / 29 / 29 | 31 named options across versions and 25 digest names |

## Manuals, source and builds

The inventory reconciles each command's synopsis and option definitions, the referenced common verification, TLS configuration, provider and random-state groups, and the binary's option table. The upstream column uses OpenSSL 4.1.0, released 23 October 2026. Its POD files were expanded with that release's own `doc/perlvars.pm`. The upstream executable was built locally from the release tarball with `Configure no-shared no-tests no-docs`. The release tarball SHA-256 was `50c17baf54cb008f6ce42d50deb4b28050a1aad711636cabd4b241c7e90cc2fd`. Build-dependent features are identified separately. [OpenSSL release and checksums](https://github.com/openssl/openssl/releases/tag/openssl-4.1.0) · [Shared manual definitions](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/perlvars.pm)

| Command | Upstream 4.1.0 | Ubuntu 24.04 Noble 3.0.13-0ubuntu3.16 | Ubuntu 26.04 Resolute 3.5.5-1ubuntu3.7 |
| --- | --- | --- | --- |
| `s_client` | [Manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-s_client.pod.in) · [option table](https://github.com/openssl/openssl/blob/openssl-4.1.0/apps/s_client.c) | [Noble s_client(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-s_client.1ssl.html) | [Resolute s_client(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-s_client.1ssl.html) |
| `x509` | [Manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-x509.pod.in) · [option table](https://github.com/openssl/openssl/blob/openssl-4.1.0/apps/x509.c) | [Noble x509(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-x509.1ssl.html) | [Resolute x509(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-x509.1ssl.html) |
| `dgst` | [Manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-dgst.pod.in) · [option table](https://github.com/openssl/openssl/blob/openssl-4.1.0/apps/dgst.c) | [Noble dgst(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-dgst.1ssl.html) | [Resolute dgst(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-dgst.1ssl.html) |

TLS limits, cipher lists and certificate validation have separate references. For example, `-verify_depth` counts intermediate CAs, and `-verify_hostname` sets an expected certificate identity independently of SNI. `-serverpref`, `-client_renegotiation`, `-no_resumption_on_reneg`, `-prioritize_chacha` and `-prefer_no_dhe_kex` have server-side effects in the shared SSL configuration interface. `-issuer_checks`, `-no_alt_chains` and `-debug_broken_protocol` remain accepted compatibility spellings. [Verification parameters](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-verification-options.pod) · [SSL configuration](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man3/SSL_CONF_cmd.pod) · [General options](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl.pod)

The captures use fixed `openssl version`, `openssl SUBCOMMAND -help` and `openssl dgst -list` arguments with `LC_ALL=C` and `OPENSSL_CONF=/dev/null`. Output combines standard output and standard error. The three Noble help captures matched the existing repository captures byte for byte. The inventory regression compares each release column to its own captures, including the arity of every fixed option.

## Release differences and boundaries

- The Noble and Resolute manuals document conditional `-ssl3`, `-sctp` and `-sctp_label_bug`. The actual Ubuntu packages omit all three. OpenSSL 4 removed SSLv3. The upstream manual retains the SCTP pair. Resolute enables `-ktls` and `-tfo`, which the upstream manual documents but the local upstream build omits. All five rows identify availability. The WATT-32-only source switch `-wdebug` falls outside the Linux/manual inventory.
- Resolute adds QUIC, raw public key negotiation, certificate compression controls and provider parameters over Noble. Upstream 4.1 adds Encrypted ClientHello settings, DTLS 1.3 and required OCSP status checks. The old engine options are specific to OpenSSL 3. Noble accepts a single decimal record-padding block size. Its parser reads the decimal prefix with `atoi`, so a comma and second number have no independent effect. Resolute and upstream can use different byte counts for application data and for handshake/alert records. [Noble padding parser](https://github.com/openssl/openssl/blob/openssl-3.0.13/ssl/ssl_conf.c) · [Resolute padding syntax](https://github.com/openssl/openssl/blob/openssl-3.5.5/doc/man3/SSL_CONF_cmd.pod)
- Certificate creation distinguishes the signing key, public key to embed, CA certificate, request extensions and CA serial file. `-key` and `-signkey` are aliases. Noble uses `-subj`, while Resolute and upstream also accept `-set_subject` and an explicit issuer or validity period. Only upstream includes `-multi`, which can check expiry across an entire input bundle.
- The manuals write `-digest` for a selected algorithm and fixed help displays `-*`. These are metavariables. The rows use 25 actual selector spellings, including the aliases `-ripemd`, `-ripemd160`, `-rmd160`, `-ssl3-md5` and `-ssl3-sha1`. Upstream's local build lists 23. The Ubuntu builds additionally list `-md4` and `-whirlpool`, both of which failed with only the default provider. Alternative algorithm names and aliases supplied by an installed provider form an open-ended namespace. `-list` and the provider options expose that boundary.
- Upstream adds `dgst -hmac-env` and `-hmac-stdin`. `-xoflen` sets a positive byte count for XOF output. With `-shake128` and `-shake256`, request at least 32 and 64 bytes respectively for full security strength.
- The TLS destination `host[:port]` and digest input filenames are positional operands. Interactive TLS command letters act after connecting. General OpenSSL commands, provider properties, X.509 extension names and TLS cipher-suite expressions have their own grammars. They remain operands or separate commands.

## Disposable client checks

The Ubuntu 26.04.1 sandbox used its OpenSSL 3.5.5. The Ubuntu 24.04.5 Python 3.10 and 3.12 sandboxes used the extracted Noble 3.0.13 executable and matching Ubuntu libraries. Each run used a temporary directory, empty OpenSSL configuration and a fresh RSA key and certificate. TLS parsing targeted a nonexistent Unix-domain socket inside that directory, so successful credential decoding reached a local missing-socket error without a handshake. The 4.1.0 executable also ran these checks in its private build environment. [Noble fixtures and source package references](openssl-option-audit.md#executable-verification)

| Check | Observed result |
| --- | --- |
| Explicit input encoding | Across all three OpenSSL versions, PEM succeeded in `dgst -keyform` signing and `x509 -CAform` issuance. Explicit DER rejected the same PEM files. Correct PEM for `s_client -certform`, `-xcertform` and `-xkeyform` reached the socket attempt. Explicit DER rejected the credential first. The rows describe enforced decoding despite misleading format hints in fixed help. |
| Certificate identity | For a certificate with `DNS:menu.test`, a wrong DNS name, email address and IP each printed a mismatch. Each check exited **0 on Noble** and **1 on Resolute and upstream**. A matching `-ext subjectAltName,keyUsage` display included the DNS entry. |
| Digest lengths and selectors | SHAKE128 with `-xoflen 33 -binary` matched 33 independently computed bytes. Zero was rejected. The RIPEMD and SSL3-MD5 aliases produced digests. MD4 and Whirlpool failed in the tested default-provider configurations. |
| Conditional TLS options | All binaries rejected `-ssl3`, `-sctp`, `-sctp_label_bug` and `-wdebug` before connection. |

The [combined verification record](iproute2-systemd-openssl-verification.md) owns rendered-menu and full-suite evidence for the shared snapshot. The [first-pass audit](openssl-option-audit.md) preserves the original 33 dispositions and their separately scoped structured contracts.

## Inventory key

**M** means the release manual documents the spelling. **H** means that build's fixed command help lists it. **D** means the build's `dgst -list` advertises the concrete digest selector accepted by the command's digest-option parser, subject to fetch and operation support. A dash means no evidence in that release column. Operand placeholders show a single following shell argument, including when the operand contains a list. A dash in the operand column means the switch is complete as inserted. The [packaged and upstream captures](../tests/fixtures/openssl) and [original Noble help](../tests/fixtures/help/expansion-system-captures) preserve the fixed output used for comparison.

## openssl s_client inventory

| Spelling | Operand | Noble | Resolute | Upstream |
| --- | --- | --- | --- | --- |
| `-4` | — | MH | MH | MH |
| `-6` | — | MH | MH | MH |
| `-CAfile` | `FILE` | MH | MH | MH |
| `-CApath` | `DIR` | MH | MH | MH |
| `-CAstore` | `URI` | MH | MH | MH |
| `-CRL` | `FILE` | MH | MH | MH |
| `-CRLform` | `FORMAT` | MH | MH | MH |
| `-adv` | — | — | MH | MH |
| `-allow_no_dhe_kex` | — | MH | MH | MH |
| `-allow_proxy_certs` | — | MH | MH | MH |
| `-alpn` | `PROTOCOLS` | MH | MH | MH |
| `-async` | — | MH | MH | MH |
| `-attime` | `SECONDS` | MH | MH | MH |
| `-auth_level` | `LEVEL` | MH | MH | MH |
| `-bind` | `HOST:PORT` | MH | MH | MH |
| `-brief` | — | MH | MH | MH |
| `-bugs` | — | MH | MH | MH |
| `-build_chain` | — | MH | MH | MH |
| `-cert` | `FILE` | MH | MH | MH |
| `-cert_chain` | `FILE` | MH | MH | MH |
| `-certform` | `FORMAT` | MH | MH | MH |
| `-chainCAfile` | `FILE` | MH | MH | MH |
| `-chainCApath` | `DIR` | MH | MH | MH |
| `-chainCAstore` | `URI` | MH | MH | MH |
| `-check_ss_sig` | — | MH | MH | MH |
| `-cipher` | `CIPHERLIST` | MH | MH | MH |
| `-ciphersuites` | `SUITES` | MH | MH | MH |
| `-client_renegotiation` | — | MH | MH | MH |
| `-client_sigalgs` | `ALGORITHMS` | MH | MH | MH |
| `-comp` | — | MH | MH | MH |
| `-connect` | `HOST:PORT` | MH | MH | MH |
| `-crl_check` | — | MH | MH | MH |
| `-crl_check_all` | — | MH | MH | MH |
| `-crl_download` | — | MH | MH | MH |
| `-crlf` | — | MH | MH | MH |
| `-ct` | — | MH | MH | MH |
| `-ctlogfile` | `FILE` | MH | MH | MH |
| `-curves` | `GROUPS` | MH | MH | MH |
| `-dane_ee_no_namechecks` | — | MH | MH | MH |
| `-dane_tlsa_domain` | `DOMAIN` | MH | MH | MH |
| `-dane_tlsa_rrdata` | `RRDATA` | MH | MH | MH |
| `-debug` | — | MH | MH | MH |
| `-debug_broken_protocol` | — | MH | MH | MH |
| `-dtls` | — | MH | MH | MH |
| `-dtls1` | — | MH | MH | MH |
| `-dtls1_2` | — | MH | MH | MH |
| `-dtls1_3` | — | — | — | MH |
| `-early_data` | `FILE` | MH | MH | MH |
| `-ech_config_list` | `BASE64` | — | — | MH |
| `-ech_grease` | — | — | — | MH |
| `-ech_grease_suite` | `SUITE` | — | — | MH |
| `-ech_grease_type` | `TYPE` | — | — | MH |
| `-ech_ignore_cid` | — | — | — | MH |
| `-ech_no_outer_sni` | — | — | — | MH |
| `-ech_outer_alpn` | `PROTOCOLS` | — | — | MH |
| `-ech_outer_sni` | `HOST` | — | — | MH |
| `-ech_select` | `INDEX` | — | — | MH |
| `-enable_client_rpk` | — | — | MH | MH |
| `-enable_pha` | — | MH | MH | MH |
| `-enable_server_rpk` | — | — | MH | MH |
| `-engine` | `ID` | MH | MH | — |
| `-expected-rpks` | `FILE` | — | — | MH |
| `-explicit_policy` | — | MH | MH | MH |
| `-extended_crl` | — | MH | MH | MH |
| `-fallback_scsv` | — | MH | MH | MH |
| `-grease` | — | — | — | MH |
| `-groups` | `GROUPS` | MH | MH | MH |
| `-help` | — | MH | MH | MH |
| `-host` | `HOST` | MH | MH | MH |
| `-ign_eof` | — | MH | MH | MH |
| `-ignore_critical` | — | MH | MH | MH |
| `-ignore_unexpected_eof` | — | MH | MH | MH |
| `-inhibit_any` | — | MH | MH | MH |
| `-inhibit_map` | — | MH | MH | MH |
| `-issuer_checks` | — | MH | MH | MH |
| `-key` | `FILE` | MH | MH | MH |
| `-keyform` | `FORMAT` | MH | MH | MH |
| `-keylogfile` | `FILE` | MH | MH | MH |
| `-keymatexport` | `LABEL` | MH | MH | MH |
| `-keymatexportlen` | `BYTES` | MH | MH | MH |
| `-ktls` | — | — | MH | M |
| `-legacy_renegotiation` | — | MH | MH | MH |
| `-legacy_server_connect` | — | MH | MH | MH |
| `-max_pipelines` | `COUNT` | MH | MH | MH |
| `-max_protocol` | `VERSION` | MH | MH | MH |
| `-max_send_frag` | `BYTES` | MH | MH | MH |
| `-maxfraglen` | `BYTES` | MH | MH | MH |
| `-min_protocol` | `VERSION` | MH | MH | MH |
| `-msg` | — | MH | MH | MH |
| `-msgfile` | `FILE` | MH | MH | MH |
| `-mtu` | `BYTES` | MH | MH | MH |
| `-name` | `HOST` | MH | MH | MH |
| `-named_curve` | `CURVE` | MH | MH | MH |
| `-nameopt` | `OPTIONS` | MH | MH | MH |
| `-nbio` | — | MH | MH | MH |
| `-nbio_test` | — | MH | MH | MH |
| `-nextprotoneg` | `PROTOCOLS` | MH | MH | MH |
| `-no-CAfile` | — | MH | MH | MH |
| `-no-CApath` | — | MH | MH | MH |
| `-no-CAstore` | — | MH | MH | MH |
| `-no-interactive` | — | — | MH | MH |
| `-no_alt_chains` | — | MH | MH | MH |
| `-no_check_time` | — | MH | MH | MH |
| `-no_comp` | — | MH | MH | MH |
| `-no_ems` | — | — | MH | MH |
| `-no_etm` | — | MH | MH | MH |
| `-no_ign_eof` | — | MH | MH | MH |
| `-no_legacy_server_connect` | — | MH | MH | MH |
| `-no_middlebox` | — | MH | MH | MH |
| `-no_renegotiation` | — | MH | MH | MH |
| `-no_resumption_on_reneg` | — | MH | MH | MH |
| `-no_rx_cert_comp` | — | — | MH | MH |
| `-no_ssl3` | — | MH | MH | MH |
| `-no_ticket` | — | MH | MH | MH |
| `-no_tls1` | — | MH | MH | MH |
| `-no_tls1_1` | — | MH | MH | MH |
| `-no_tls1_2` | — | MH | MH | MH |
| `-no_tls1_3` | — | MH | MH | MH |
| `-no_tx_cert_comp` | — | — | MH | MH |
| `-nocommands` | — | MH | MH | MH |
| `-noct` | — | MH | MH | MH |
| `-noservername` | — | MH | MH | MH |
| `-ocsp_check_all` | — | — | — | MH |
| `-ocsp_check_leaf` | — | — | — | MH |
| `-partial_chain` | — | MH | MH | MH |
| `-pass` | `SOURCE` | MH | MH | MH |
| `-policy` | `OID` | MH | MH | MH |
| `-policy_check` | — | MH | MH | MH |
| `-policy_print` | — | MH | MH | MH |
| `-port` | `PORT` | MH | MH | MH |
| `-prefer_no_dhe_kex` | — | — | MH | MH |
| `-prexit` | — | MH | MH | MH |
| `-prioritize_chacha` | — | MH | MH | MH |
| `-propquery` | `QUERY` | MH | MH | MH |
| `-provider` | `NAME` | MH | MH | MH |
| `-provider-path` | `DIR` | MH | MH | MH |
| `-provparam` | `NAME=VALUE` | — | MH | MH |
| `-proxy` | `HOST:PORT` | MH | MH | MH |
| `-proxy_pass` | `SOURCE` | MH | MH | MH |
| `-proxy_user` | `USER` | MH | MH | MH |
| `-psk` | `HEX` | MH | MH | MH |
| `-psk_identity` | `IDENTITY` | MH | MH | MH |
| `-psk_session` | `FILE` | MH | MH | MH |
| `-purpose` | `PURPOSE` | MH | MH | MH |
| `-quic` | — | — | MH | MH |
| `-quiet` | — | MH | MH | MH |
| `-rand` | `FILES` | MH | MH | MH |
| `-read_buf` | `BYTES` | MH | MH | MH |
| `-reconnect` | — | MH | MH | MH |
| `-record_padding` | `BYTES[,BYTES]` | MH | MH | MH |
| `-requestCAfile` | `FILE` | MH | MH | MH |
| `-sctp` | — | M | M | M |
| `-sctp_label_bug` | — | M | M | M |
| `-security_debug` | — | MH | MH | MH |
| `-security_debug_verbose` | — | MH | MH | MH |
| `-serverinfo` | `TYPES` | MH | MH | MH |
| `-servername` | `NAME` | MH | MH | MH |
| `-serverpref` | — | MH | MH | MH |
| `-sess_in` | `FILE` | MH | MH | MH |
| `-sess_out` | `FILE` | MH | MH | MH |
| `-showcerts` | — | MH | MH | MH |
| `-sigalgs` | `ALGORITHMS` | MH | MH | MH |
| `-split_send_frag` | `BYTES` | MH | MH | MH |
| `-srp_lateuser` | — | MH | MH | MH |
| `-srp_moregroups` | — | MH | MH | MH |
| `-srp_strength` | `BITS` | MH | MH | MH |
| `-srppass` | `SOURCE` | MH | MH | MH |
| `-srpuser` | `USER` | MH | MH | MH |
| `-ssl3` | — | M | M | — |
| `-ssl_client_engine` | `ID` | MH | MH | — |
| `-ssl_config` | `SECTION` | MH | MH | MH |
| `-starttls` | `PROTOCOL` | MH | MH | MH |
| `-state` | — | MH | MH | MH |
| `-status` | — | MH | MH | MH |
| `-strict` | — | MH | MH | MH |
| `-suiteB_128` | — | MH | MH | MH |
| `-suiteB_128_only` | — | MH | MH | MH |
| `-suiteB_192` | — | MH | MH | MH |
| `-tfo` | — | — | MH | M |
| `-timeout` | — | MH | MH | MH |
| `-tls1` | — | MH | MH | MH |
| `-tls1_1` | — | MH | MH | MH |
| `-tls1_2` | — | MH | MH | MH |
| `-tls1_3` | — | MH | MH | MH |
| `-tlsextdebug` | — | MH | MH | MH |
| `-trace` | — | MH | MH | MH |
| `-trusted_first` | — | MH | MH | MH |
| `-unix` | `PATH` | MH | MH | MH |
| `-use_deltas` | — | MH | MH | MH |
| `-use_srtp` | `PROFILES` | MH | MH | MH |
| `-verify` | `DEPTH` | MH | MH | MH |
| `-verifyCAfile` | `FILE` | MH | MH | MH |
| `-verifyCApath` | `DIR` | MH | MH | MH |
| `-verifyCAstore` | `URI` | MH | MH | MH |
| `-verify_depth` | `COUNT` | MH | MH | MH |
| `-verify_email` | `EMAIL` | MH | MH | MH |
| `-verify_hostname` | `HOST` | MH | MH | MH |
| `-verify_ip` | `ADDRESS` | MH | MH | MH |
| `-verify_name` | `METHOD` | MH | MH | MH |
| `-verify_quiet` | — | MH | MH | MH |
| `-verify_return_error` | — | MH | MH | MH |
| `-writerand` | `FILE` | MH | MH | MH |
| `-x509_strict` | — | MH | MH | MH |
| `-xcert` | `CERT` | MH | MH | MH |
| `-xcertform` | `FORMAT` | MH | MH | MH |
| `-xchain` | `FILE` | MH | MH | MH |
| `-xchain_build` | — | MH | MH | MH |
| `-xkey` | `KEY` | MH | MH | MH |
| `-xkeyform` | `FORMAT` | MH | MH | MH |
| `-xmpphost` | `HOST` | MH | MH | MH |

## openssl x509 inventory

| Spelling | Operand | Noble | Resolute | Upstream |
| --- | --- | --- | --- | --- |
| `-CA` | `CERT` | MH | MH | MH |
| `-CAcreateserial` | — | MH | MH | MH |
| `-CAform` | `FORMAT` | MH | MH | MH |
| `-CAkey` | `KEY` | MH | MH | MH |
| `-CAkeyform` | `FORMAT` | MH | MH | MH |
| `-CAserial` | `FILE` | MH | MH | MH |
| `-addreject` | `PURPOSE` | MH | MH | MH |
| `-addtrust` | `PURPOSE` | MH | MH | MH |
| `-alias` | — | MH | MH | MH |
| `-badsig` | — | MH | MH | MH |
| `-blake2b512` | — | D | D | D |
| `-blake2s256` | — | D | D | D |
| `-certopt` | `OPTIONS` | MH | MH | MH |
| `-checkemail` | `EMAIL` | MH | MH | MH |
| `-checkend` | `SECONDS` | MH | MH | MH |
| `-checkhost` | `HOST` | MH | MH | MH |
| `-checkip` | `ADDRESS` | MH | MH | MH |
| `-clrext` | — | MH | MH | MH |
| `-clrreject` | — | MH | MH | MH |
| `-clrtrust` | — | MH | MH | MH |
| `-copy_extensions` | `MODE` | MH | MH | MH |
| `-dateopt` | `FORMAT` | MH | MH | MH |
| `-dates` | — | MH | MH | MH |
| `-days` | `DAYS` | MH | MH | MH |
| `-email` | — | MH | MH | MH |
| `-enddate` | — | MH | MH | MH |
| `-engine` | `ID` | MH | MH | — |
| `-ext` | `EXTENSIONS` | MH | MH | MH |
| `-extensions` | `SECTION` | MH | MH | MH |
| `-extfile` | `FILE` | MH | MH | MH |
| `-fingerprint` | — | MH | MH | MH |
| `-force_pubkey` | `KEY` | MH | MH | MH |
| `-hash` | — | MH | MH | MH |
| `-help` | — | MH | MH | MH |
| `-in` | `FILE` | MH | MH | MH |
| `-inform` | `FORMAT` | MH | MH | MH |
| `-issuer` | — | MH | MH | MH |
| `-issuer_hash` | — | MH | MH | MH |
| `-issuer_hash_old` | — | MH | MH | MH |
| `-key` | `KEY` | MH | MH | MH |
| `-keyform` | `FORMAT` | MH | MH | MH |
| `-md4` | — | D | D | — |
| `-md5` | — | D | D | D |
| `-md5-sha1` | — | D | D | D |
| `-modulus` | — | MH | MH | MH |
| `-multi` | — | — | — | MH |
| `-nameopt` | `OPTIONS` | MH | MH | MH |
| `-new` | — | MH | MH | MH |
| `-next_serial` | — | MH | MH | MH |
| `-nocert` | — | MH | MH | MH |
| `-noout` | — | MH | MH | MH |
| `-not_after` | `TIME` | — | MH | MH |
| `-not_before` | `TIME` | — | MH | MH |
| `-ocsp_uri` | — | MH | MH | MH |
| `-ocspid` | — | MH | MH | MH |
| `-out` | `FILE` | MH | MH | MH |
| `-outform` | `FORMAT` | MH | MH | MH |
| `-passin` | `SOURCE` | MH | MH | MH |
| `-preserve_dates` | — | MH | MH | MH |
| `-propquery` | `QUERY` | MH | MH | MH |
| `-provider` | `NAME` | MH | MH | MH |
| `-provider-path` | `DIR` | MH | MH | MH |
| `-provparam` | `NAME=VALUE` | — | MH | MH |
| `-pubkey` | — | MH | MH | MH |
| `-purpose` | — | MH | MH | MH |
| `-rand` | `FILES` | MH | MH | MH |
| `-req` | — | MH | MH | MH |
| `-ripemd` | — | D | D | D |
| `-ripemd160` | — | D | D | D |
| `-rmd160` | — | D | D | D |
| `-serial` | — | MH | MH | MH |
| `-set_issuer` | `NAME` | — | MH | MH |
| `-set_serial` | `SERIAL` | MH | MH | MH |
| `-set_subject` | `NAME` | — | MH | MH |
| `-setalias` | `NAME` | MH | MH | MH |
| `-sha1` | — | D | D | D |
| `-sha224` | — | D | D | D |
| `-sha256` | — | D | D | D |
| `-sha3-224` | — | D | D | D |
| `-sha3-256` | — | D | D | D |
| `-sha3-384` | — | D | D | D |
| `-sha3-512` | — | D | D | D |
| `-sha384` | — | D | D | D |
| `-sha512` | — | D | D | D |
| `-sha512-224` | — | D | D | D |
| `-sha512-256` | — | D | D | D |
| `-shake128` | — | D | D | D |
| `-shake256` | — | D | D | D |
| `-signkey` | `KEY` | MH | MH | MH |
| `-sigopt` | `NAME:VALUE` | MH | MH | MH |
| `-sm3` | — | D | D | D |
| `-ssl3-md5` | — | D | D | D |
| `-ssl3-sha1` | — | D | D | D |
| `-startdate` | — | MH | MH | MH |
| `-subj` | `NAME` | MH | MH | MH |
| `-subject` | — | MH | MH | MH |
| `-subject_hash` | — | MH | MH | MH |
| `-subject_hash_old` | — | MH | MH | MH |
| `-text` | — | MH | MH | MH |
| `-trustout` | — | MH | MH | MH |
| `-vfyopt` | `NAME:VALUE` | MH | MH | MH |
| `-whirlpool` | — | D | D | — |
| `-writerand` | `FILE` | MH | MH | MH |
| `-x509toreq` | — | MH | MH | MH |

## openssl dgst inventory

| Spelling | Operand | Noble | Resolute | Upstream |
| --- | --- | --- | --- | --- |
| `-binary` | — | MH | MH | MH |
| `-blake2b512` | — | D | D | D |
| `-blake2s256` | — | D | D | D |
| `-c` | — | MH | MH | MH |
| `-d` | — | MH | MH | MH |
| `-debug` | — | MH | MH | MH |
| `-engine` | `ID` | MH | MH | — |
| `-engine_impl` | — | MH | MH | — |
| `-fips-fingerprint` | — | MH | MH | MH |
| `-help` | — | MH | MH | MH |
| `-hex` | — | MH | MH | MH |
| `-hmac` | `KEY` | MH | MH | MH |
| `-hmac-env` | `VARIABLE` | — | — | MH |
| `-hmac-stdin` | — | — | — | MH |
| `-keyform` | `FORMAT` | MH | MH | MH |
| `-list` | — | MH | MH | MH |
| `-mac` | `ALGORITHM` | MH | MH | MH |
| `-macopt` | `NAME:VALUE` | MH | MH | MH |
| `-md4` | — | D | D | — |
| `-md5` | — | D | D | D |
| `-md5-sha1` | — | D | D | D |
| `-out` | `FILE` | MH | MH | MH |
| `-passin` | `SOURCE` | MH | MH | MH |
| `-propquery` | `QUERY` | MH | MH | MH |
| `-provider` | `NAME` | MH | MH | MH |
| `-provider-path` | `DIR` | MH | MH | MH |
| `-provparam` | `NAME=VALUE` | — | MH | MH |
| `-prverify` | `KEY` | MH | MH | MH |
| `-r` | — | MH | MH | MH |
| `-rand` | `FILES` | MH | MH | MH |
| `-ripemd` | — | D | D | D |
| `-ripemd160` | — | D | D | D |
| `-rmd160` | — | D | D | D |
| `-sha1` | — | D | D | D |
| `-sha224` | — | D | D | D |
| `-sha256` | — | D | D | D |
| `-sha3-224` | — | D | D | D |
| `-sha3-256` | — | D | D | D |
| `-sha3-384` | — | D | D | D |
| `-sha3-512` | — | D | D | D |
| `-sha384` | — | D | D | D |
| `-sha512` | — | D | D | D |
| `-sha512-224` | — | D | D | D |
| `-sha512-256` | — | D | D | D |
| `-shake128` | — | D | D | D |
| `-shake256` | — | D | D | D |
| `-sign` | `FILE` | MH | MH | MH |
| `-signature` | `FILE` | MH | MH | MH |
| `-sigopt` | `NAME:VALUE` | MH | MH | MH |
| `-sm3` | — | D | D | D |
| `-ssl3-md5` | — | D | D | D |
| `-ssl3-sha1` | — | D | D | D |
| `-verify` | `FILE` | MH | MH | MH |
| `-whirlpool` | — | D | D | — |
| `-writerand` | `FILE` | MH | MH | MH |
| `-xoflen` | `BYTES` | MH | MH | MH |
