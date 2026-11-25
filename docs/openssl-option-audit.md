# OpenSSL option audit

First recorded 2026-11-22. This first pass covered 33 bundled rows. See the [expanded inventory and verification](openssl-manual-coverage.md) for the later manual comparison.

## Sources and versions

| Command | Upstream OpenSSL 4.1.0 | Ubuntu 24.04 LTS, 3.0.13-0ubuntu3.16 | Ubuntu 26.04 LTS, 3.5.5-1ubuntu3.7 |
| --- | --- | --- | --- |
| [s_client profile](../profiles/openssl-s_client.json) | [s_client manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-s_client.pod.in) | [Noble s_client(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-s_client.1ssl.html) | [Resolute s_client(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-s_client.1ssl.html) |
| [x509 profile](../profiles/openssl-x509.json) | [x509 manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-x509.pod.in) | [Noble x509(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-x509.1ssl.html) | [Resolute x509(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-x509.1ssl.html) |
| [dgst profile](../profiles/openssl-dgst.json) | [dgst manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-dgst.pod.in) | [Noble dgst(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-dgst.1ssl.html) | [Resolute dgst(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-dgst.1ssl.html) |

The upstream comparison uses the tagged release. The profiles' structured value records retain their separate OpenSSL 3.0.16 scope. Where the manuals and packaged clients differ, the observations below identify the version and operation tested. [4.1.0 release](https://github.com/openssl/openssl/releases/tag/openssl-4.1.0) · [3.0.16 format rules](https://github.com/openssl/openssl/blob/openssl-3.0.16/doc/man1/openssl-format-options.pod) · [3.0.16 verification parameters](https://github.com/openssl/openssl/blob/openssl-3.0.16/doc/man1/openssl-verification-options.pod)

## Disposition of the original entries

### openssl s_client

The TLS client used `-verify` to enable verification diagnostics. The treatment of errors and chain depth depended on the verification and handshake switches.

### openssl x509

The expiry test reported whether the certificate would expire by its cutoff through the exit status.

### openssl dgst

Digest display and signature verification required distinct output formats, including binary signature bytes.

## Manual qualifications and version differences

The audit distinguished an otherwise valid chain from depth handling during a certificate error. The later comparison inventories TLS, X.509, provider, MAC and digest choices by edition and operation.

## Executable verification

The Ubuntu 26.04 sandbox used its system OpenSSL 3.5.5. The two Noble images lack the CLI, so their disposable snapshots included OpenSSL 3.0.13 and its matching Ubuntu shared libraries extracted from the 24.04 packages. No packages were installed. Each target generated a short-lived certificate, disposable keys and a message file. TLS checks connected only to a private loopback server. [Noble CLI package](https://archive.ubuntu.com/ubuntu/pool/main/o/openssl/openssl_3.0.13-0ubuntu3.16_amd64.deb) · [Noble libraries](https://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl3t64_3.0.13-0ubuntu3.16_amd64.deb)

| Fixture | Result on the three targets |
| --- | --- |
| TLS client | With explicit PEM trust and hostname verification, both TLS 1.2 and TLS 1.3 connections succeeded. The server received the selected SNI name. The client printed the transmitted certificate. A mismatched expected hostname caused failure with `-verify_return_error`. Both client versions rejected zero and negative `-verify` operands. |
| Certificate input and output | Unspecified input format accepted PEM, DER and a single certificate in PKCS#12. Explicit PEM and DER each rejected the other encoding. `-noout -text -dates -subject -issuer -out` wrote the requested fields to the file without an encoded certificate. |
| Fingerprint and expiry | The default fingerprint and the explicit SHA-256 fingerprint matched independent hashes of the DER bytes. On a two-day certificate, zero, −1 and a one-day hexadecimal interval returned zero. A three-day interval returned nonzero. |
| Digests and signatures | SHA-256 and SHA-512 produced the expected binary bytes and coreutils-style text. HMAC matched an independent calculation using the literal text key. An RSA signature verified for its original input and failed for changed data. Ed25519 signing without a digest selection succeeded only on 3.5.5. Explicit SHA-256 was rejected for that key. |

## Rendered menus and offline suite

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py) · [Source-derived numerical expectations](../tests/fixtures/value-semantics/debt-resolution-evidence.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 15 / 0 / 0 | 1,341 / 0 / 1 | 480.661 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 15 / 0 / 0 | 1,341 / 0 / 1 | 542.709 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 15 / 0 / 0 | 1,341 / 0 / 1 | 480.757 s |

Each Linux suite skipped the Windows-specific probe.
