# OpenSSH client manual coverage

The SSH login, secure copy and SFTP menus each use the option grammar of their own client. All three offer short options before the first positional operand. An operand-taking selection inserts the flag and positions the cursor for a value. The menu leaves quoted paths and remote command arguments in the pending line.

## Manual inventory

| Client | Original rows | Added | Total | Option declarations, release applicability and exclusions |
| --- | ---: | ---: | ---: | --- |
| `ssh` | 19 | 27 | 46 | [SSH inventory and parser differences](openssh-ssh-inventory.md) |
| `scp` | 15 | 9 | 24 | [Transfer client inventories](openssh-transfer-inventories.md) |
| `sftp` | 17 | 9 | 26 | [Transfer client inventories](openssh-transfer-inventories.md) |

The 96 rows preserve the 51 original spellings, argument placeholders and their relative order. The three upstream synopses account for 46, 23 and 25 spellings respectively. Ubuntu adds an explicit SFTP selector to the scp synopsis. Its sftp client also has a usage action in the parser. Repeated short options, attached operands and short bundles use the same rows. Configuration keywords, session escape sequences and the SFTP prompt have separate grammars. The [first-pass audit](openssh-option-audit.md) records the original selection and its historical tests.

## Changes that affect an invocation

- **SSH and X11 trust.** On both Ubuntu clients, `ssh -X` enables trusted X11 forwarding with the default settings. The menu gives `-X -o ForwardX11Trusted=no` for restricted forwarding. It also distinguishes where a connection originates under `-L`, `-R` and `-D`. [SSH inventory and release references](openssh-ssh-inventory.md#parser-and-release-distinctions)
- **SCP protocol selection.** SFTP is the default. On Noble and Resolute, `scp -O -s` selects SFTP again. Portable 10.6p2 ignores the compatibility spelling `-s`, leaving legacy SCP selected in that sequence. The `-3` and `-R` rows describe where a remote-to-remote copy runs. [SCP inventory and release parsers](openssh-transfer-inventories.md#scp-inventory)
- **SFTP resume.** With `-a`, the Ubuntu clients resume an upload only when a shorter destination file already exists. The existing prefix must match the source. A disposable fixture resumed a two-byte mismatched prefix, leaving those bytes in the completed file. [SFTP inventory and resume prerequisites](openssh-transfer-inventories.md#sftp-inventory)

## Verification

[Packaged client observations and fixture provenance](openssh-packaged-checks.md) cover the actual option parsers and local transfers. The [inventory and terminal regressions](../tests/test_openssh_manual_coverage.py) compare the profile declarations with independent manual synopses, packaged usage and original discovery fixtures. The Bash/tmux regressions use an execution-recording shell function for each command with discovery disabled.

At 220×150 the terminal test walks every option in order and checks its selected row, summary, full Details heading, authored prose and formatted value guidance. At 60×16, the original searches exercise the remote listener and the opposite recursive symlink behavior of scp and sftp. A second set searches for a multiplexing master in ssh and the local server program in each transfer client. It scrolls to the release restriction or quoting rule, cancels to the original line and cursor, then selects `ssh -O`, `scp -D` or `sftp -D` before a quoted value. A separate boundary check tries to open each menu after the remote command or path operands. All sessions use a private tmux socket and Readline buffer. [Original terminal regression](../tests/test_terminal_screen.py) · [Expanded inventory and terminal regressions](../tests/test_openssh_manual_coverage.py)

The numerical review covered 94 changed identities. For each identity, the comparison preserved all observations outside the three profiles. In particular, the original captured manual parser classified `ssh -W` and `-w` as switches. Both take one operand. The separate bundled contracts describe the destination and tunnel-device grammars. The first full run exposed an earlier test that required `scp -3` to appear only in external captures. The revised regression checks those captures alongside the bundled fixed-mode declaration, including the absence of a numerical operand. The strict gate reconciled 899 required contracts across 76 profiles. [Numerical review](numerical-inventory/review.json)

Each sandbox snapshot includes the new tests, captures and audit documents individually with `--include`. The full suites ran `bash tests/run.sh`. On Noble, `RSYNC_TEST_BINARY` points to the private wrapper for the existing rsync fixture. [Offline sandbox instructions](development.md#isolated-local-debugging) · [OpenSSH fixture preparation](openssh-packaged-checks.md#package-verification-and-reproduction) · [Noble rsync fixture](rsync-manual-coverage.md#verification)

| Target | Ubuntu | Python | OpenSSH package | Focused pass / fail / skip | Full pass / fail / skip |
| --- | --- | --- | --- | ---: | ---: |
| `host` | 26.04.1 | 3.14.4 | 1:10.2p1-2ubuntu3.8 | 25 / 0 / 0 | 1,414 / 0 / 1 |
| `noble310` | 24.04.5 | 3.10.20 | 1:9.6p1-3ubuntu13.20 | 25 / 0 / 0 | 1,414 / 0 / 1 |
| `noble312` | 24.04.5 | 3.12.3 | 1:9.6p1-3ubuntu13.20 | 25 / 0 / 0 | 1,414 / 0 / 1 |

All 96 rows and their complete rendered Details passed on each target. The command stubs recorded zero pending-command executions. The 25 focused tests included eight packaged-client regressions. The sole full-suite skip per target was the Windows-specific probe. The manual inventories reconcile with no outstanding OpenSSH coverage gaps.
