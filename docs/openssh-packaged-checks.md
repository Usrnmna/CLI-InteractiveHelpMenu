# OpenSSH packaged-client checks

The three sandbox targets exercised real Ubuntu clients separately from the [terminal menu checks](openssh-manual-coverage.md). All client invocations used the C locale and private files. The SSH probes used local queries or dumped configuration with `-G -F none` or an explicit private configuration file. The transfer probes used an argument-recording transport or a local SFTP server over subprocess pipes. No SSH daemon, agent, credentials or remote host participated.

## Executables and fixed usage

| Sandbox | Ubuntu / Python | Ubuntu openssh-client and openssh-sftp-server | Client directory | OpenSSL reported by ssh |
| --- | --- | --- | --- | --- |
| host | 26.04.1 / 3.14.4 | 1:10.2p1-2ubuntu3.8 | `/usr/bin` | 3.5.5, 27 Jan 2026 |
| noble310 | 24.04.5 / 3.10.20 | 1:9.6p1-3ubuntu13.20 | `/tmp/openssh/usr/bin` | 3.0.13, 30 Jan 2024 |
| noble312 | 24.04.5 / 3.12.3 | 1:9.6p1-3ubuntu13.20 | `/tmp/openssh/usr/bin` | 3.0.13, 30 Jan 2024 |

The client directory contains `ssh`, `scp` and `sftp`. Both Noble images lacked all three clients, and all three targets lacked the server binary. Each sandbox used a matching server extracted to `/tmp/openssh/usr/lib/openssh/sftp-server`. Package extraction used disposable storage and required no installation. On Resolute, the installed client version came from host dpkg metadata and the version banner inside the sandbox.

Invoking the binaries with no arguments produced usage on stderr and zero bytes on stdout. Status was 255 for ssh and 1 for scp and sftp. In all three environments `ssh -V` returned 0 with the version on stderr and empty stdout. The two Noble targets produced byte-identical captures. Six files preserve raw usage and the manifest records the invocation, output streams, status and version. [Fixed captures and metadata](../tests/fixtures/openssh/captures.json)

## Observed behavior

| Fixture | Result on both packaged releases unless specified |
| --- | --- |
| Local SSH queries | `ssh -Q cipher` included `aes128-ctr`. Both `-Q kex-gss` and `-Q key-ca-sign` returned algorithm lists on stdout, status 0 and empty stderr. `-Q addressfamily` returned 255 with empty stdout and an unsupported-query error on stderr. |
| Upstream-only options | `ssh -Z` returned 255, empty stdout and an unknown-option error followed by usage on stderr. With `-G -F none`, `-O conninfo` and `-O channels` returned 255, empty stdout and `Invalid multiplex command.` on stderr. The control commands `proxy` and `forward` passed argument parsing with `-G`. No master was required or contacted. |
| Effective SSH configuration | `-MM` yielded `controlmaster ask`. `-X` yielded both `forwardx11 yes` and `forwardx11trusted yes`, including when the user and system configuration files were bypassed. Explicit `-oForwardX11Trusted=no` changed the latter to `no`. A Unix-socket-to-socket `-L` retained both paths. `-R 0` gave `remoteforward 0 [socks]:0`. These were configuration dumps, without binding listeners. |
| SSH options and operands | With `-G -T -F none`, `fixture.invalid -p 2022 echo -p 2023` yielded `port 2022`. With only `fixture.invalid echo -p 2023`, it stayed 22. Both packages accepted tunnel device `2147483645:any` and rejected `2147483646` (255, empty stdout, bad-device diagnostic). Both resolved `-p ssh` to 22 with a service database. The host sandbox initially returned a bad-port error with no database. Adding `ssh 22/tcp` and `opensshfixture 54321/tcp` to its private tmpfs `/etc/services` made both names resolve. |
| Configuration filenames | Each client consumed the complete filename in `-F=private.conf` and in `-F -private.conf`. SSH read the private file named `=private.conf` or `-private.conf` and printed its configured port 54321. For scp and sftp the transport recorder received the same filename byte for byte. |
| Compatibility and usage | All three rejected `-1` with status 255 and a protocol-v1 diagnostic. With `-2`, ssh retained the normal version output and both transfer clients generated the same transport arguments as with the flag omitted. `sftp -h` returned its ordinary usage on stderr, status 1, without an unknown-option error. |
| scp protocol and route | With `-S` pointing to a recorder that exits 73, `-O -s` requested the SSH `sftp` subsystem (client 255, empty stdout, connection-closed stderr). `-s -O` requested `scp -f input` (client 1, both streams empty). An actual `-O -s -D SERVER` copy succeeded, status 0, both streams empty. For two remote operands, default mode and `-3` first requested SFTP at the destination. `-R` instead requested that the origin run `scp from dest.invalid:to`. |
| sftp subsystem and server | With the recorder, `-s custom` requested an SSH subsystem named `custom`. A value containing a slash was passed as the remote command without the transport's subsystem flag. `-D 'SERVER -e -l VERBOSE'` started a local server process with those logging arguments, allowing observation of individual requests. |
| Bandwidth and SFTP tuning | For both transfer clients, `-l1` and `-l 104857600` reached the recorder. `0`, `104857601` and `1K` returned usage and status 1 before transport. For `-X`, `buffer=256K` and `nrequests=262144` reached transport. Zero, one above either maximum and the misspelled key `requests` failed with status 255 and an invalid-option or invalid-value diagnostic. The separate sftp `-B` and `-R` accepted `-1` and `262145` through parsing and rejected `0` and `1K`. No transfers ran with those large legacy settings. The bandwidth conversion factor and negotiated request/buffer defaults come from the tagged source. |
| Recursive downloads | The input directory contained a regular file and a symlink to an external sibling file in the fixture. Both clients returned 0 and copied the regular file. scp copied the linked target's data as a regular file. sftp omitted the link. |
| Resume, flush and batch failures | A download and an upload with `-a` preserved an existing two-byte prefix of `xx`, yielding `xx23456789` from source `0123456789`. A download to a missing file succeeded. An upload to a missing remote file returned 1 with `stat remote: No such file or directory` on stderr and stopped before the next batch command. Prefixing a failing `get` with `-` let the next upload run and the batch exit 0. For `-f`, the local server's stderr recorded an explicit `fsync` request for the uploaded file. |

The executable regression compares the six usage captures byte for byte and checks the transfer results against arguments, file contents and server logs. [Executable regression module](../tests/test_openssh_packaged.py)

## Package verification and reproduction

Package SHA-256 values were checked against the Ubuntu amd64 package indexes. The corresponding index hashes matched their signed InRelease files. Verification with the Ubuntu archive keyring identified signing key `F6ECB3762474EDA9D21B7022871920D1991BC93C`. [Noble release](https://archive.ubuntu.com/ubuntu/dists/noble/InRelease) · [Noble updates](https://archive.ubuntu.com/ubuntu/dists/noble-updates/InRelease) · [Resolute security](https://security.ubuntu.com/ubuntu/dists/resolute-security/InRelease)

| Archive | SHA-256 |
| --- | --- |
| [Noble openssh-client 9.6p1-3ubuntu13.20](https://archive.ubuntu.com/ubuntu/pool/main/o/openssh/openssh-client_9.6p1-3ubuntu13.20_amd64.deb) | `5fb4429e9eff60a5b4ddb68ccf0c46ee67066b445794ede5fe181e64c4a8b795` |
| [Noble openssh-sftp-server 9.6p1-3ubuntu13.20](https://archive.ubuntu.com/ubuntu/pool/main/o/openssh/openssh-sftp-server_9.6p1-3ubuntu13.20_amd64.deb) | `111fb22cab9abf220b681f97eefa195ccfacef7d85561772ecef22e88db2d7bb` |
| [Noble libedit2](https://archive.ubuntu.com/ubuntu/pool/main/libe/libedit/libedit2_3.1-20230828-1build1_amd64.deb) | `3afbc8ddf835049dd4d88275b9d13680e4c4cdd59e191cbd63424152cc08e00e` |
| [Noble libbsd0](https://archive.ubuntu.com/ubuntu/pool/main/libb/libbsd/libbsd0_0.12.1-1build1.1_amd64.deb) | `f3857b0863ac5cfd4263e9bf6cfb1d4be88d5321e4070d5bc2b62b0949e6c86f` |
| [Noble libmd0](https://archive.ubuntu.com/ubuntu/pool/main/libm/libmd/libmd0_1.1.0-2build1.1_amd64.deb) | `e5ba01d3c41f256aaf57ec59aa0554857162e3e7f97cdfbff1ed2c0e8d720ee7` |
| [Resolute openssh-sftp-server 10.2p1-2ubuntu3.8](https://security.ubuntu.com/ubuntu/pool/main/o/openssh/openssh-sftp-server_10.2p1-2ubuntu3.8_amd64.deb) | `8093b5bbc911802f946069953640796ecc40234cf25aea3892f0b05304908ed4` |

Pass the verified target-specific packages to the [sandbox runner](development.md#isolated-local-debugging) with `--include`, either individually or in one temporary tar archive. Inside the sandbox, extract each package with `dpkg-deb -x PACKAGE /tmp/openssh`. Set `OPENSSH_TEST_SERVER=/tmp/openssh/usr/lib/openssh/sftp-server` for every target. On Noble, also export `OPENSSH_TEST_BINDIR=/tmp/openssh/usr/bin` and `OPENSSH_TEST_LIBDIR=/tmp/openssh/usr/lib/x86_64-linux-gnu`. Only child processes under this regression receive the alternate library path. Run `python3 -m unittest discover -s tests -p test_openssh_packaged.py -v`. The full Noble suite also uses the separate [rsync package fixture](rsync-manual-coverage.md#verification).
