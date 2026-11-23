# GNU ls option audit

The first pass reviewed the 19 entries then bundled in three categories. The [full manual-coverage revisit](ls-manual-coverage.md) records the expanded menu and the subsequent package and terminal checks. The review covers the menu opened for a pending `ls` command with discovery disabled. Ubuntu 26.04 supplies a different implementation under the same command name.

## Sources and versions

- GNU Coreutils 9.12 defines which names appear, which attributes are shown, how names are sorted and quoted, and when indicators and color are emitted. The common block-size section specifies precedence and which fields each variable affects. [GNU ls manual](https://www.gnu.org/software/coreutils/manual/coreutils.html#ls-invocation) and [block size](https://www.gnu.org/software/coreutils/manual/coreutils.html#Block-size)
- Six existing value guides refer specifically to GNU Coreutils 9.6. The release manual covers the four operand-free flags, the hide pattern and the optional color policy. The release source also enumerates the nine color spellings and maps them to three policies. [GNU 9.6 manual source](https://raw.githubusercontent.com/coreutils/coreutils/v9.6/doc/coreutils.texi) and [GNU 9.6 ls source, `when_args` and `when_types`](https://github.com/coreutils/coreutils/blob/v9.6/src/ls.c#L975-L987)
- Ubuntu 24.04 documents GNU Coreutils package `9.4-3ubuntu6.3`. Ubuntu 26.04 documents `rust-coreutils 0.10.0-1ubuntu2~26.04.1`. Both pages cover all 19 entries. The latter is evidence for Ubuntu's default uutils command. [Ubuntu 24.04 ls(1)](https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html) and [Ubuntu 26.04 ls(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)

## Disposition of the original descriptions

The rows follow menu order. The disposition applies to the original row and Details together. An existing summary can remain useful when its Details need revision.

| Menu entry | Original wording | Finding and resolution |
| --- | --- | --- |
| `--all` | Incomplete | Dot-prefixed names include the implied current and parent directory entries. Name both in Details. |
| `--almost-all` | Inaccurate | The original profile named both exceptions correctly, but the rendered row displayed a single dot twice. Put `.` and `..` inside the sentence and distinguish an explicit hidden operand from an implied entry. |
| `-l` | Incomplete | Identify the long-listing columns. Regular-file length normally uses bytes and can be scaled. Block and character devices show major and minor numbers in that field. |
| `--human-readable` | Redundant | Retain the summary. Details now associate `-l` with length and `-s` with disk usage. Retain the meaning of M and the decimal alternative `--si`. |
| `--classify` | Incomplete | Decode the common Linux indicators. An executable regular file gets an asterisk and an ordinary nonexecutable file has no suffix. The menu's bare spelling enables classification even on a pipe. |
| `--color=` | Incomplete | Explain terminal, pipe and disabled output. Standalone `--color` selects always. The menu inserts the equals sign and the user supplies WHEN. |
| `--inode` | Redundant | Keep the summary. Replace generic numerical disclaimers with the filesystem scope of an inode number and the relationship between hard links. |
| `--size` | Redundant | Keep allocation in the summary. Put the default, override order and sparse-file distinction in Details. The first field of `-ls` reports disk usage. |
| `--numeric-uid-gid` | Incomplete | Selecting numeric IDs also selects long format. A separate `-l` is unnecessary. |
| `--quote-name` | Incomplete | Double quotes delimit the name and C-style escapes represent nongraphic characters inside it. |
| `--escape` | Sufficient as written | The existing summary identifies the escaping convention and the characters affected. It also serves as the Details description. |
| `--hide=` | Incomplete | Use a quoted shell pattern. It filters names discovered while listing directories. Explicit operands still appear, and either `-a` or `-A` overrides the pattern. |
| `--reverse` | Incomplete | Reverse the active sort. Explain the effect on time and size and the exception for unsorted output. |
| `-t` | Incomplete | Retain the default of most recently modified first. Identify `--time` as the way to select another timestamp. |
| `-S` | Incomplete | “File size” could describe either column of `-ls`. Specify file length as the sort key. |
| `--group-directories-first` | Incomplete | Sort directories and other entries independently. Unsorted mode disables grouping. |
| `--recursive` | Incomplete | Descend into subdirectories. Following symbolic links encountered during descent requires dereferencing. |
| `--directory` | Incomplete | Contrast the long listing of an explicit directory, a symbolic link to it and the target shown by `-ldL`. |
| `--dereference` | Incomplete | Use the target's attributes under the link's name. Distinguish ordinary handling of a named link to a directory and the command-line-only scope of `-H`. |

The sort-key findings follow the GNU selection of timestamp, size and grouping. The quoting review compares the C quoting style with escape style, which omits the surrounding quotes. [GNU sorting rules](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-the-output) and [GNU filename formatting](https://www.gnu.org/software/coreutils/manual/coreutils.html#Formatting-the-file-names)

## Material distinctions and version differences

**Length and allocation.** The long listing normally gives the logical length of a regular file in bytes. The separate `-s` field gives space used on the filesystem, normally in 1024-byte display blocks rounded up. Display units are independent of filesystem allocation units. An explicit `--block-size` takes precedence over the environment. The first applicable variable is `LS_BLOCK_SIZE`, then `BLOCK_SIZE`, then `BLOCKSIZE`. The last affects fields normally printed in blocks. With none set, `POSIXLY_CORRECT` selects 512-byte blocks for usage. The normal length field still uses bytes. Human-readable formatting scales fields selected by other options. [GNU file information](https://www.gnu.org/software/coreutils/manual/coreutils.html#What-information-is-listed) and [GNU display units](https://www.gnu.org/software/coreutils/manual/coreutils.html#Block-size)

**Names and traversal.** Filtering during directory enumeration differs from naming an operand. A plain listing of a named symlink to a directory ordinarily shows the contents. Long format, directory mode and classification change GNU's default treatment of this operand. Explicit dereference options can change it again. The GNU 9.6 and 9.12 manuals also say `-a` overrides `-A`. The GNU 9.6 option parser assigns the mode on each occurrence. All three tested binaries honored the last of the two when combined. GNU 9.12 executable behavior for the combination remains unverified. The menu describes each option independently. [GNU file selection](https://www.gnu.org/software/coreutils/manual/coreutils.html#Which-files-are-listed) and [GNU 9.6 option parser](https://github.com/coreutils/coreutils/blob/v9.6/src/ls.c#L1975-L2080)

**Accepted syntax and insertion.** GNU accepts `-l` and `--format=long`. The Resolute man page also advertises `--long` and the short version switch `-V`. The menu offers `-l`. The classify row inserts the complete flag. The color and hide rows insert literal prefixes that take values, `--color=` and `--hide=`. A bare `--color` enables color even on a pipe. An explicitly empty color policy is rejected. The nine color spellings, four operand-free flags and required pattern retain their GNU 9.6 value guidance and review scope. [GNU output formatting](https://www.gnu.org/software/coreutils/manual/coreutils.html#General-output-formatting) and [Ubuntu 26.04 ls(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)

## Manual-only coverage

At the end of the first pass, the following long option names had no dedicated row. Attached values count under their base option. Some modes still have a selectable short spelling, such as `-t` and `-S` for two values of `--sort`.

| Purpose | Additional long names shared by the GNU manual and both Ubuntu pages |
| --- | --- |
| File selection and link traversal | `--ignore`, `--ignore-backups`, `--dereference-command-line`, `--dereference-command-line-symlink-to-dir` |
| Metadata, sizes and ordering | `--author`, `--block-size`, `--context`, `--kibibytes`, `--no-group`, `--si`, `--sort`, `--time` |
| Layout, timestamps and name rendering | `--dired`, `--file-type`, `--format`, `--full-time`, `--hide-control-chars`, `--hyperlink`, `--indicator-style`, `--literal`, `--quoting-style`, `--show-control-chars`, `--tabsize`, `--time-style`, `--width`, `--zero` |
| Program information | `--help`, `--version` |

The shared short spellings outside the three selectable short rows are
`-1 -A -B -C -D -F -G -H -I -L -N -Q -R -T -U -X -Z -a -b -c -d -f -g -h -i -k -m -n -o -p -q -r -s -u -v -w -x`.
This list includes aliases of selectable long rows. Resolute's additional `--long` and `-V` spellings have no dedicated rows. [GNU ls options](https://www.gnu.org/software/coreutils/manual/coreutils.html#ls-invocation), [GNU common options](https://www.gnu.org/software/coreutils/manual/coreutils.html#Common-options), [Noble declarations](https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html) and [Resolute declarations](https://manpages.ubuntu.com/manpages/resolute/man1/ls.1.html)

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


In each of the three environments, a private Bash/tmux session opened the unfiltered bundled menu at 160×64. Inspection followed every category and row in order and compared the visible label, complete summary and Details prose with the profile. All 19 passed, including the literal dot entries and the color policy aliases. A shell stub recorded any execution attempt. Cancellation returned to the original pending command.

The focused regression opens the menu in the middle of `ls  existing-dir`, shrinks the unfiltered view to 60×16, searches for “allocated” and finds `--size`. Scrolling reaches the sparse-file qualification. Escape restores the exact line and cursor. Reopening and selecting `--hide=PATTERN` inserts only `--hide=`, preserves the suffix and leaves the cursor ready for the pattern. The stub recorded zero executions. The regression and the numerical-inventory review check both passed on all three targets. [Terminal regression](../tests/test_terminal_screen.py) and [sandbox runner instructions](development.md#isolated-local-debugging)

To repeat the focused menu check, substitute `host`, `noble310` or `noble312` for TARGET.

```bash
python3 -I tests/run_sandbox.py --target TARGET -- python3 -m unittest discover \
  -s tests -p test_terminal_screen.py -k test_ls_allocated_space_search_and_midline_hide_insertion -v
```

Each full offline run included the untracked tar, grep and ls audit documents in its snapshot. The runner's coverage gates and bundled-profile checks passed. The table records the subsequent unittest results. The single skip on each target was the Windows-specific probe test.

| Ubuntu | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| 24.04.5 LTS | 3.10.20 | 1,330 | 0 | 1 |
| 24.04.5 LTS | 3.12.3 | 1,330 | 0 | 1 |
| 26.04.1 LTS | 3.14.4 | 1,330 | 0 | 1 |
