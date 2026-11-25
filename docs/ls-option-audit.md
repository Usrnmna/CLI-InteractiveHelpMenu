# GNU ls option audit

First recorded 2026-11-22. This first pass covered 19 bundled rows. See the [expanded inventory and verification](ls-manual-coverage.md) for the later manual comparison.

## Sources and versions

- GNU Coreutils 9.12 defines which names appear, which attributes are shown, how names are sorted and quoted, and when indicators and color are emitted. The common block-size section specifies precedence and which fields each variable affects. [GNU ls manual](https://www.gnu.org/software/coreutils/manual/coreutils.html#ls-invocation) and [block size](https://www.gnu.org/software/coreutils/manual/coreutils.html#Block-size)
- Six existing value guides refer specifically to GNU Coreutils 9.6. The release manual covers the four operand-free flags, the hide pattern and the optional color policy. The release source also enumerates the nine color spellings and maps them to three policies. [GNU 9.6 manual source](https://raw.githubusercontent.com/coreutils/coreutils/v9.6/doc/coreutils.texi) and [GNU 9.6 ls source, `when_args` and `when_types`](https://github.com/coreutils/coreutils/blob/v9.6/src/ls.c#L975-L987)
- Ubuntu 24.04 documents GNU Coreutils package `9.4-3ubuntu6.3`. Ubuntu 26.04 documents `rust-coreutils 0.10.0-1ubuntu2~26.04.1`. Both pages cover all 19 entries. The latter is evidence for Ubuntu's default uutils command. [Ubuntu 24.04 ls(1)](https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html) and [Ubuntu 26.04 ls(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)

## Disposition of the original descriptions

The 19 entries distinguished logical length from allocated blocks, directory traversal from explicit operands, and color or classification choices from their insertion forms.

## Material distinctions and version differences

Ubuntu 26.04 supplied uutils. Both GNU and uutils implementations were checked. The three tested binaries used the last of `-a` and `-A` when combined. The GNU 9.12 manual stated a different precedence and its executable was untested.

## Manual-only coverage

The baseline lacked dedicated rows for many long names. Some modes were already accessible by a short spelling, including sort by time and size. The revisit reconciled option families and aliases across implementations.

## Executable observations on disposable fixtures

The following checks invoked binaries directly on temporary sandbox files. Noble supplied GNU ls 9.4. Resolute supplied uutils ls 0.10.0 at `/usr/bin/ls` and GNU ls 9.7 at `/usr/bin/gnuls`.

| Fixture or invocation | Observed result |
| --- | --- |
| Sparse file with length 1,048,576 bytes | All three binaries showed allocation 0 and length 1048576 with `-ls`. Adding `-h` showed 0 and 1.0M. |
| File containing 4,608 bytes | The two `-ls` fields were 8 and 4608. With `BLOCKSIZE=2K` they were 4 and 4608. With `LS_BLOCK_SIZE=1K` and `BLOCK_SIZE=2K` they were 8 and 5. With only `POSIXLY_CORRECT=1` they were 16 and 4608. An explicit one-byte unit overrode `LS_BLOCK_SIZE=1K` and showed 8192 and 4608. |
| Directory containing a name matching a hide pattern | Both attached and separate pattern arguments filtered the directory listing. The explicit matching file remained visible, and both `-a` and `-A` restored the matching entry. `-aA` omitted the implied dot entries and `-Aa` included them on all three binaries. |
| Symlink to a directory | The bare operand showed its contents. `-ld` reported a link, while `-ldL` reported a directory using the link name. Within a single recursive root, `-RL` visited a directory and its sibling symlink on both GNU versions. uutils diagnosed a repeated directory and returned 2. The revisit also checked two separately named operands, which succeeded on all three. |
| Output to a pipe | Bare classify added a directory slash. `--classify=auto` omitted it. With directory colors configured, bare color and the always aliases emitted escapes. The auto and never aliases produced plain text. All three binaries accepted all nine color values, rejected uppercase `AUTO` and rejected an empty color value. |
| Sorting a sparse file and a shorter file with disk blocks | `-S` listed the longer sparse file first and `-Sr` reversed the order. Opposing access and modification times produced opposite orders for `-t --time=atime` and plain `-t`. |
| Hard link, numeric IDs and a filename containing a newline | Both hard-link names had the same inode. `-n` alone produced a long listing with numeric owner and group. Both `-b` and `-Q` showed the newline as `\n`. Only `-Q` surrounded the name with double quotes. |
| Long-format spelling | All three accepted `--format=long`. Only uutils accepted `--long`. |

## Rendered menu and offline tests

The local terminal walks checked the 19 selections, output-format qualifications and exact Readline edits on each sandbox target. [Terminal regression](../tests/test_terminal_screen.py)

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 24.04.5 LTS | 3.10.20 | 1,330 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,330 | 0 | 1 |
| 26.04.1 LTS | 3.14.4 | 1,330 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
