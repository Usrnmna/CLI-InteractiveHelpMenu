# OpenSSL option audit

The three bundled menus contain 33 options. The twelve `s_client` entries cover TLS connections and peer verification, the eleven `x509` entries inspect or encode certificates, and the ten `dgst` entries hash data and create or verify signatures. Option order, operand labels and literal insertions are preserved.

## Sources and versions

| Command | Upstream OpenSSL 4.1.0 | Ubuntu 24.04 LTS, 3.0.13-0ubuntu3.16 | Ubuntu 26.04 LTS, 3.5.5-1ubuntu3.7 |
| --- | --- | --- | --- |
| [s_client profile](../profiles/openssl-s_client.json) | [s_client manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-s_client.pod.in) | [Noble s_client(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-s_client.1ssl.html) | [Resolute s_client(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-s_client.1ssl.html) |
| [x509 profile](../profiles/openssl-x509.json) | [x509 manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-x509.pod.in) | [Noble x509(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-x509.1ssl.html) | [Resolute x509(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-x509.1ssl.html) |
| [dgst profile](../profiles/openssl-dgst.json) | [dgst manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-dgst.pod.in) | [Noble dgst(1ssl)](https://manpages.ubuntu.com/manpages/noble/man1/openssl-dgst.1ssl.html) | [Resolute dgst(1ssl)](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-dgst.1ssl.html) |

The upstream comparison uses the tagged release. The profiles' structured value records retain their separate OpenSSL 3.0.16 scope. Where the manuals and packaged clients differ, the observations below identify the version and operation tested. [4.1.0 release](https://github.com/openssl/openssl/releases/tag/openssl-4.1.0) · [3.0.16 format rules](https://github.com/openssl/openssl/blob/openssl-3.0.16/doc/man1/openssl-format-options.pod) · [3.0.16 verification parameters](https://github.com/openssl/openssl/blob/openssl-3.0.16/doc/man1/openssl-verification-options.pod)

## Disposition of the original entries

### openssl s_client

| Option | Disposition | Menu decision |
| --- | --- | --- |
| `-connect HOST:PORT` | Redundant | Show the endpoint, the default port 4433 and bracketed IPv6. Retain separate host and service guidance and single-token syntax. |
| `-servername NAME` | Incomplete | Explain SNI, its DNS-name default and the separate `-verify_hostname` check. |
| `-CAfile FILE` | Incomplete | Identify the file as a trust source. Use a PEM bundle on the Ubuntu clients and distinguish loading trust from stopping on errors. |
| `-cert FILE` | Incomplete | The server must request a client certificate for it to be sent. Identify the matching key. |
| `-key FILE` | Incomplete | Accept a filename or supported URI. Without this option, the client looks for the key in the selected certificate file. |
| `-verify DEPTH` | Inaccurate | Enable peer verification and describe the diagnostic depth. Use a positive decimal value. The separate `-verify_depth` parameter limits intermediate CAs. |
| `-verify_return_error` | Sufficient | Retain the stop-on-error meaning. Explain that it enables peer verification and how to request a DNS name check. |
| `-showcerts` | Incomplete | Show the peer's certificate list in transmitted order. It can be incomplete and does not establish trust. |
| `-starttls PROTOCOL` | Incomplete | Explain the application-protocol exchange before TLS and the independent destination selection. |
| `-quiet` | Incomplete | Suppress session and certificate output. It also implies ignoring stdin EOF. Place `-no_ign_eof` afterward to override this. |
| `-tls1_2` | Incomplete | Require exactly TLS 1.2. The peer must support that version. |
| `-tls1_3` | Incomplete | Require exactly TLS 1.3, with the same negotiation constraint. |

### openssl x509

| Option | Disposition | Menu decision |
| --- | --- | --- |
| `-in FILE` | Sufficient | Retain the certificate-input summary. Identify stdin as the default and the request-input case with `-req`. |
| `-out FILE` | Incomplete | Write the requested output to the named file, including printed fields. The default destination is stdout. |
| `-inform FORMAT` | Inaccurate | The former structured default claimed PEM. Omitting the option enables detection. Explicit PEM or DER constrains decoding. |
| `-outform FORMAT` | Incomplete | Encoding applies to the output certificate. PEM is the default, DER is binary and display fields remain text. |
| `-text` | Incomplete | Identify the fields shown and the role of `-noout` when only text is wanted. |
| `-noout` | Sufficient | Preserve the encoded-output distinction and show how to print only requested fields. |
| `-subject` | Incomplete | Identify the subject name field. DNS names used for hostname matching can appear in the subject alternative name extension. |
| `-issuer` | Sufficient | Identify the issuer name field and distinguish reading it from verifying the certificate. |
| `-dates` | Incomplete | Name both validity boundaries and point to `-checkend` for an exit-status test. |
| `-fingerprint` | Incomplete | Hash the entire DER-encoded certificate. The default is SHA-1. Specify `-sha256` for a SHA-256 fingerprint. |
| `-checkend SECONDS` | Incomplete | State the exit-status polarity and the scope of the expiry check. Retain signed seconds, numeric syntax, zero and platform bounds in Details. |

### openssl dgst

| Option | Disposition | Menu decision |
| --- | --- | --- |
| `-sha256` | Incomplete | Identify the default for ordinary hashing and the 32-byte or 64-hex-digit result. |
| `-sha512` | Sufficient | Keep the algorithm selection and give the 64-byte or 128-hex-digit result. |
| `-hex` | Incomplete | Ordinary digests default to hex. The signature verifier consumes binary signature bytes. |
| `-binary` | Incomplete | Write raw digest or signature bytes. Binary is the normal signature output. |
| `-out FILE` | Incomplete | Identify the output as the digest or signature and the default destination as stdout. |
| `-sign FILE` | Incomplete | Sign one message using a private key file or URI. Explain binary output and the Ubuntu difference for one-shot EdDSA keys. |
| `-verify FILE` | Incomplete | The operand is the public key. Supply the signature separately and verify against the original message. Report the success text and status. |
| `-signature FILE` | Incomplete | Read the binary signature. The original message is a separate input. A printed hex signature needs conversion to bytes. |
| `-hmac KEY` | Incomplete | The argument supplies literal key text. Hex-looking characters are used as text. |
| `-r` | Incomplete | Describe the digest, asterisk and filename in the coreutils-style file checksum line. |

## Manual qualifications and version differences

- **Verification depth.** The `s_client` manuals describe a maximum chain length. The client assigns `-verify` to its verification callback, which consults the depth when processing a certificate error. An otherwise valid chain can exceed that depth. When an error occurs deeper than the supplied value, the callback rejects the chain. The separate `-verify_depth` option sets the chain verification parameter. Its limit counts intermediate CAs and excludes the leaf and trust anchor. For a check that must stop on errors, add `-verify_return_error`. The earlier numerical review and its independent regression fixture now reflect that distinction. [Client argument handling](https://github.com/openssl/openssl/blob/openssl-3.0.16/apps/s_client.c) · [Error callback](https://github.com/openssl/openssl/blob/openssl-3.0.16/apps/lib/s_cb.c) · [Verification parameter assignment](https://github.com/openssl/openssl/blob/openssl-3.0.16/apps/lib/opt.c)
- **Numeric spelling.** The packaged clients validate `-verify` as a positive integer, then read the accepted argument using decimal conversion. Use ordinary positive decimal digits. Upstream 4.1.0 uses the parsed integer directly. The separate `x509 -checkend` implementation reads a signed integer offset and checks its conversion to the platform time type. [3.5.5 client](https://github.com/openssl/openssl/blob/openssl-3.5.5/apps/s_client.c) · [4.1.0 client](https://github.com/openssl/openssl/blob/openssl-4.1.0/apps/s_client.c) · [3.0.16 expiry implementation](https://github.com/openssl/openssl/blob/openssl-3.0.16/apps/x509.c)
- **Trust files and certificate files.** The general verification reference describes broader `-CAfile` format support than the tested TLS clients accepted. They both loaded the PEM trust file and rejected the same certificate in DER at trust-file loading. By contrast, `x509` read that DER file directly with no format flag. The pinned `-inform` default now matches the certificate decoder. [General trust-file reference](https://github.com/openssl/openssl/blob/openssl-3.5.5/doc/man1/openssl-verification-options.pod) · [TLS trust-file loading](https://github.com/openssl/openssl/blob/openssl-3.5.5/apps/lib/apps.c)
- **Quiet output and signing.** Upstream 4.1.0 documents an additional implied `-verify_quiet` for `s_client -quiet`. The EOF consequence applies to both Ubuntu versions. Noble's `dgst` lacks Ed25519/Ed448 signing. Resolute supports one-shot signing with these keys if no digest is explicitly selected. The Resolute manual gives a 16 MB input limit for that mode. [4.1.0 client manual](https://github.com/openssl/openssl/blob/openssl-4.1.0/doc/man1/openssl-s_client.pod.in) · [Noble dgst](https://manpages.ubuntu.com/manpages/noble/man1/openssl-dgst.1ssl.html) · [Resolute dgst](https://manpages.ubuntu.com/manpages/resolute/man1/openssl-dgst.1ssl.html)

Manual-only coverage includes TLS hostname and IP verification switches, chain-building parameters, ALPN, cipher suites, session reuse, certificate requests and issuance, extension display, digest providers, MAC key encodings and algorithm-specific signature settings. Upstream 4.1.0 also documents `x509 -multi -checkend` for testing expiry across multiple input certificates. The table above describes the bundled single-certificate case. No discovery path is counted as reviewed by this audit.

## Executable verification

The Ubuntu 26.04 sandbox used its system OpenSSL 3.5.5. The two Noble images lack the CLI, so their disposable snapshots included OpenSSL 3.0.13 and its matching Ubuntu shared libraries extracted from the 24.04 packages. No packages were installed. Each target generated a short-lived certificate, disposable keys and a message file. TLS checks connected only to a private loopback server. [Noble CLI package](https://archive.ubuntu.com/ubuntu/pool/main/o/openssl/openssl_3.0.13-0ubuntu3.16_amd64.deb) · [Noble libraries](https://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl3t64_3.0.13-0ubuntu3.16_amd64.deb)

| Fixture | Result on the three targets |
| --- | --- |
| TLS client | With explicit PEM trust and hostname verification, both TLS 1.2 and TLS 1.3 connections succeeded. The server received the selected SNI name. The client printed the transmitted certificate. A mismatched expected hostname caused failure with `-verify_return_error`. Both client versions rejected zero and negative `-verify` operands. |
| Certificate input and output | Unspecified input format accepted PEM, DER and a single certificate in PKCS#12. Explicit PEM and DER each rejected the other encoding. `-noout -text -dates -subject -issuer -out` wrote the requested fields to the file without an encoded certificate. |
| Fingerprint and expiry | The default fingerprint and the explicit SHA-256 fingerprint matched independent hashes of the DER bytes. On a two-day certificate, zero, −1 and a one-day hexadecimal interval returned zero. A three-day interval returned nonzero. |
| Digests and signatures | SHA-256 and SHA-512 produced the expected binary bytes and coreutils-style text. HMAC matched an independent calculation using the literal text key. An RSA signature verified for its original input and failed for changed data. Ed25519 signing without a digest selection succeeded only on 3.5.5. Explicit SHA-256 was rejected for that key. |

## Rendered menus and offline suite

Each target opened all three bundled menus in Bash/tmux with discovery disabled. At 210×100 the highlighted label, summary and full Details pane matched for all 33 rows. Cancellation restored the pending command and its Readline cursor. Selecting `-verify`, `-checkend` or `-signature` inserted that literal option before an existing suffix. A shell stub recorded unexpected execution. It remained unused.

At 60×16 a search from each unfiltered menu reached a consequential qualification. “to limit intermediate” found the TLS client's diagnostic depth and chain-limit guidance, “by the cutoff” found the expiry exit status, and “hex dump back” found the binary signature requirement. Each qualification was reachable by scrolling. The persistent regression also filled the depth value to produce `openssl s_client -verify 2 -showcerts` and checked the cursor. The digest menu accepted a signature filename while preserving the message filename to its right. [Terminal regression](../tests/test_expansion_terminal.py) · [Offline sandbox procedure](development.md#isolated-local-debugging)

The 15 focused checks per target covered profile declarations, literal edits, real terminal interaction, OpenSSL depth, expiry and endpoint contracts, and inventory completeness. Review of the 43 changed fingerprints covered the three profile files, their command and category descriptions, all affected rows and the corrected independent depth fixture. [Numerical inventory review](numerical-inventory/review.json) · [Source-derived numerical expectations](../tests/fixtures/value-semantics/debt-resolution-evidence.json)

| Offline sandbox | Focused passed / failed / skipped | Full suite passed / failed / skipped | Full suite time |
| --- | ---: | ---: | ---: |
| Ubuntu 26.04.1 / Python 3.14.4 | 15 / 0 / 0 | 1,341 / 0 / 1 | 480.661 s |
| Ubuntu 24.04.5 / Python 3.10.20 | 15 / 0 / 0 | 1,341 / 0 / 1 | 542.709 s |
| Ubuntu 24.04.5 / Python 3.12.3 | 15 / 0 / 0 | 1,341 / 0 / 1 | 480.757 s |

Each full run included the untracked audit documents and passed shell syntax, numerical coverage, profile validation and unittest discovery. Each skipped the Windows-only probe on Linux.
