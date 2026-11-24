# 7-Zip extraction switch inventory

This inventory covers the Linux console commands `7z x` and `7zz x`. Each row applies to both executable names. “All” means upstream 26.06, Ubuntu Noble 23.01+dfsg-11 and Ubuntu Resolute 26.00+dfsg-1. The full client can load plugins. The standalone client uses its compiled-in handlers. Availability of an individual codec, code page or hash function can depend on the build.

The upstream reference is the Linux release's `MANUAL/cmdline/syntax.htm`, `commands/extract.htm`, `commands/extract_full.htm`, `switches/index.htm` and the switch pages identified below. Ubuntu's `7z(1)` pages cover all commands together. Each `7zz(1)` refers readers to the corresponding `7z(1)`. Both Ubuntu source packages retain the “22.01” manual header from May 2023. The package versions identify the clients audited here. [Upstream 26.06 distribution](https://github.com/ip7z/7zip/releases/download/26.06/7z2606-linux-x64.tar.xz) · [Noble 7z(1)](https://manpages.ubuntu.com/manpages/noble/man1/7z.1.html) · [Noble 7zz(1)](https://manpages.ubuntu.com/manpages/noble/man1/7zz.1.html) · [Resolute 7z(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7z.1.html) · [Resolute 7zz(1)](https://manpages.ubuntu.com/manpages/resolute/man1/7zz.1.html)

## Selectable inventory

“Attached” requires a value in the same shell word. “Optional attached” permits the bare switch and leaves the following word available as an operand. For an “equals” row the displayed key includes the inserted equals sign. A switch can contain a value and still be inserted as a complete literal, such as `-aou`. The release column identifies availability of the spelling and any restrictions on its Linux effect. Page names below are relative to `MANUAL/cmdline/switches/`.

| Menu spelling | Operand | Linux releases | Meaning, forms and upstream locator |
| --- | --- | --- | --- |
| `-o` | attached | All | Destination directory. Quote an attached path with spaces. An asterisk can stand for the archive basename. See `output_dir.htm`. |
| `-t` | attached | All | Select or constrain the input handler. See `type.htm` for forced, combined, top-level, nested and parser modes. |
| `-y` | none | All | Accept replacement without an interactive confirmation. An explicit overwrite mode takes precedence. See `yes.htm` and `overwrite.htm`. |
| `-bd` | none | All | Suppress percentage progress. See the quick reference and fixed root help. |
| `-ai` | attached | All | Include archives by name pattern or list file. See `ar_include.htm` and `include.htm`. |
| `-ax` | attached | All | Exclude candidate archives by pattern or list file. See `ar_exclude.htm`. |
| `-an` | none | All | Remove the positional archive-name slot. Supply archives through includes. See `ar_no.htm`. |
| `-i` | attached | All | Include matching members from the selected archive. See `include.htm`. |
| `-x` | attached | All | Exclude matching members. See `exclude.htm`. |
| `-xtd` | none | All | Skip directory records, including their metadata. Selected files can still create their parent directories. See `exclude.htm`. |
| `-xtf` | none | All | Skip file records and retain selected directory records. This counterpart to `-xtd` is present in all three tagged parsers and extractors. |
| `-aoa` | none | All | Replace the existing file with the incoming file. See `overwrite.htm`. |
| `-aos` | none | All | Keep the existing file and skip the incoming file. See `overwrite.htm`. |
| `-aou` | none | All | Keep the existing name and give the incoming file an unused numbered name. See `overwrite.htm`. |
| `-aot` | none | All | Move the existing file to an unused numbered name and write the incoming file under the original name. See `overwrite.htm`. |
| `-r` | optional attached | All | Recurse when finding named members. `-r0` limits recursive search to wildcard names. `-r-` disables recursive search. Matched directories still include their children. See `recurse.htm`. |
| `--` | none | All | End both switch and positional list-file recognition. See `stop_switch.htm`. |
| `-spd` | none | All | Match wildcard characters literally. See the switch quick reference. |
| `-ssc` | optional attached | All | Match case sensitively. `-ssc-` ignores case. See `ssc.htm`. |
| `-spm` | optional attached | All | Require the directory separator on directory patterns. `-spm2` makes an exception for literal names, and `-spm-` permits unmarked directory names. See `spm.htm`. |
| `-stx` | attached | All | Exclude a handler from input format detection. Repeat for additional exclusions. See `stx.htm`. |
| `-p` | optional attached | All | Supply the decryption password. Omitting the entire switch permits a prompt. A bare switch supplies an empty password to extraction. See `password.htm` and the console extraction callback. |
| `-si` | optional attached | All | Read a streamable archive on stdin. An attached name can identify the stream. Positional names select members. See `stdin.htm`. |
| `-so` | none | All | Send extracted data bytes to stdout. Matching several files can concatenate their data. See `stdout.htm`. |
| `-bb` | optional attached | All | Select log detail from 0 to 3. Bare requests level 1. See `bb.htm`. |
| `-ba` | none | All | Suppress the normal banner and headers. See the quick reference and console output implementation. |
| `-bt` | none | All | Report run-time statistics. See the switch quick reference and fixed root help. |
| `-bso` | attached | All | Select the destination for normal messages with 0 (off), 1 (stdout) or 2 (stderr). See `bs.htm`. |
| `-bse` | attached | All | Route errors using the same three digits. See `bs.htm`. |
| `-bsp` | attached | All | Route progress using the same three digits. See `bs.htm`. |
| `-scc` | attached | All | Select the console text encoding. See `scc.htm`. |
| `-scs` | attached | All | Select list-file encoding, UTF-8 by default. See `charset.htm`. Its short command list omits extraction, but the extraction parser passes the selected encoding to the list reader. |
| `-scrc` | optional attached | All | Calculate hashes of extracted data. A name chooses a hash method. A quoted asterisk selects the available methods. See `scrc.htm`. |
| `-m` | attached | All | Pass a property to a handler. Its effect depends on the property, input format and decoder. See `method.htm`. |
| `-mmt` | optional attached | All | Configure workers for decoders that support threading. See `method.htm`, multithreading sections. |
| `-mcp=` | optional equals | All | Set a code page for legacy ZIP member names. Bare `-mcp` and `-mcp=` explicitly select the handler’s default OEM code page. Resolute documents this explicitly. The tagged ZIP handlers also accept the property on Noble. For the same legacy filename byte, Resolute distinguished CP437 from CP1252. Noble and the upstream Linux binary retained the byte. See `method.htm`, ZIP parameters. |
| `-mmemuse=` | equals | All | Set a decoder memory budget for handlers that implement it. A value can use binary size units or the `pN` percentage form. The XZ decoder also accepts `-mmemuse2g` as an attached method property. See `method.htm`, memory use. |
| `-spf` | optional attached | All | Honor absolute stored paths, which can reach beyond the output directory. `-spf2` selects full paths without the drive-letter mode. See `spf.htm`. |
| `-spe` | optional attached | All | Remove duplication between the output directory and an archive root directory of the same name. `-spe-` disables this behavior. See the quick reference and extractor. |
| `-spod` | none | Upstream | Interpret the output path literally, including asterisks. See `output_dir.htm`. |
| `-spoc` | none | Upstream | Append the archive basename to the output directory. See `output_dir.htm`. |
| `-spor` | none | Upstream | Substitute the archive basename for an asterisk in the output path. This explicit mode and the other two `-spo` controls arrived in 26.01. See `output_dir.htm`. |
| `-snt` | optional attached | Upstream effect | Replace trailing dots and spaces in path components with underscores. The default and `-snt-` preserve them. The tagged Ubuntu implementations restrict this rewrite to Windows. See the quick reference and `ExtractingFilePath.cpp`. |
| `-sns` | optional attached | All | Include alternate streams when present. `-sns-` disables them. See `sns.htm`. |
| `-snc` | none | All | Interpret a colon in an archived filename as an alternate-stream separator. See the quick reference and `OpenArchive.cpp`. |
| `-snr` | none | All | Separate a main name and an alternate-stream name with an underscore on disk. See the quick reference and extraction callback. |
| `-snh` | none | All | Enable restoration of hard links for handlers identifying shared inode records. See the parser and extractor. |
| `-snh-` | none | All | Disable the inode-based hard-link reconstruction pass. The format can also encode a hard link with an explicit target. See `Extract.cpp`. |
| `-snl` | none | All | Enable restoration of archive symbolic links. See the extraction callback. |
| `-snl-` | none | All | Disable symbolic-link restoration. See the extraction callback. |
| `-snld` | optional attached | All | Set the restoration policy for potentially unsafe links. Noble supports the historical bare or minus toggle. Resolute and upstream support numerical levels. See the quick reference and versioned parsers. |
| `-snoi` | optional attached | All | Request archived numeric owner and group IDs where supported. `-snoi-` disables restoration. See the quick reference and extraction callback. |
| `-slsl` | optional attached | Resolute and upstream | Print paths with slash separators. `-slsl-` selects backslashes for display. See the quick reference and console extractor. |
| `-slmu` | optional attached | Resolute and upstream | Display UTC timestamps, including collision prompts. `-slmu-` uses local time. See the quick reference and console extractor. |
| `-stm` | optional attached | All | Apply a hexadecimal CPU affinity mask to the process. The parser also accepts bare `-stm` and takes no action. See the quick reference and parser. |
| `-smemx` | attached | Resolute and upstream | Set the allowed memory for a RAR unpacking request where the handler implements the memory callback. The tagged parser accepts bytes or binary unit suffixes. See the quick reference and extraction callback. |
| `-slp` | optional attached | Upstream effect | Configure large pages. On Linux the 26.06 allocator supports colon-prefixed page-size and threshold controls and `-slp:nohuge`. Both older Ubuntu clients accept the bare spelling and lack the Linux huge-page implementation. See `large_pages.htm`. |

## Grammar and excluded controls

The archive is normally the first filename after the command. Additional names, wildcard expressions and newline-delimited `@listfile` operands select members. `!` introduces an immediate name or pattern **inside a filter**, and `@` introduces a list filename. The four filters accept local recursion (`r`, `r0`, `r-`), directory-mark (`m`, `m2`, `m-`) and wildcard (`w`, `w-`) modifiers before the marker. The archive filters control which archives to open, independently of which members to extract. Single quotes protect the complete filter or wildcard from the shell. The two Ubuntu manuals abbreviate the modifier grammar. All three tagged parsers implement it.

A switch name matches case-insensitively. The tagged console parser recognizes the initial dash, takes the longest matching name and checks the remainder against that switch's operand form. The general HTML introduction also mentions slash-prefixed switches and switch combination. In the audited Linux parser a leading slash starts a pathname and a no-operand switch followed by another switch name in the same token fails its length check. Digits, punctuation and attached mode letters in this inventory describe values or complete spellings. They do not introduce additional aliases. [Tagged console token parser](https://github.com/ip7z/7zip/blob/26.06/CPP/Common/CommandLineParser.cpp)

| Source spellings outside the extraction rows | Disposition |
| --- | --- |
| `-ao`, `-bs`, `-spo` | Grammar prefixes. Choose the complete overwrite or output-directory mode, or the required stream selector and destination. Both Ubuntu releases predate the complete `-spo` family. |
| `-sa{a,e,s}`, `-u…`, `-vSIZE`, `-w[PATH]`, `-sfx[NAME]`, `-sdel`, `-stl`, `-sse`, `-seml[.]` | Archive naming, update policy, volume creation, temporary work files, self-extracting archive creation, deletion of input files, created archive timestamps, source-open policy and email belong to archive creation or update. |
| `-mx[N]` and encoder properties of `-m` | Compression level, encoding method/parameters, header/solid block construction, metadata storage and encryption choices act when writing an archive. The extraction decoder reads the resulting archive metadata. |
| `-shdDIR`, `-ssp`, `-ssw` | Hash manifests can name external files for checking with `t`. The extraction implementation refuses to unpack such a manifest before using its base directory. The shared callback uses the access-time and sharing flags when reading those files. Ordinary extraction has no corresponding source-file behavior. |
| `-slf…`, `-slt` | Hash-command column selection and technical archive listings. The separate path-separator and time display switches also affect extraction messages. |
| `-sni`, `-snz[0/1/2]` | Restore Windows NT security descriptors or propagate Zone.Identifier on Windows. The Linux clients parse these switches but the Windows operations are compiled out. |
| `-snon[-]` | Store textual owner names during archive creation. During extraction the ownership flag comes from `-snoi`. |
| `-ad` | Display a GUI dialog in the graphical program. |
| `-h`, `-?`, `--help`; `a`, `b`, `d`, `e`, `h`, `i`, `l`, `rn`, `t`, `u`, `x` | Root help aliases short-circuit extraction. Command words choose operations before parsing the archive and member operands. |
| `@listfile`, `!pattern`, `#` and `/` | Positional list-file marker, filter syntax, a Windows-only shared map marker inside filter grammar, and Linux's path separator. A `#` after `-t` instead selects parser mode. |

The extraction group in the tagged parser and the Linux extraction callback resolve the differences between each short manual and its binary. The switch-specific manual introduces some controls only in the quick reference, and the shared root help also lists switches for other commands. The extraction engine distinguishes alternate-stream filenames, platform security metadata, ordinary files, explicit hard-link targets and shared inode records. [23.01 parser](https://github.com/ip7z/7zip/blob/23.01/CPP/7zip/UI/Common/ArchiveCommandLine.cpp) · [26.00 parser](https://github.com/ip7z/7zip/blob/26.00/CPP/7zip/UI/Common/ArchiveCommandLine.cpp) · [26.06 parser](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Common/ArchiveCommandLine.cpp) · [Archive opening](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Common/OpenArchive.cpp) · [Extraction engine](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Common/Extract.cpp) · [Extraction callback](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Common/ArchiveExtractCallback.cpp) · [Console output](https://github.com/ip7z/7zip/blob/26.06/CPP/7zip/UI/Console/ExtractCallbackConsole.cpp)
