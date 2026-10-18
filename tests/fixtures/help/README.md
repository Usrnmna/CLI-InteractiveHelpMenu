# Help-format corpus

[Compatibility matrix and live checks](../../../docs/compatibility.md) ·
[Development and validation](../../../docs/development.md#extended-tests-and-live-compatibility-reports)

`matrix.json` is the maintained list of 49 command paths, tiers, package names,
fixture filenames, expected flags and arguments, excluded forms, live sentinels,
and fixed version requests. Expected values are test assertions; they must not
be regenerated from parser output when a test fails.

The individual `.txt` files are compact, hand-authored format specimens with
paraphrased descriptions. They test argument shapes independently of installed
programs. The original FFmpeg, GCC, npm, and pip specimens were checked against
Ubuntu 24.04 output. The original VLC specimen is synthetic; a separate captured
VLC excerpt now provides real-format coverage.

`captured.json` contains bounded excerpts from installed programs on Ubuntu 24.04
under WSL. Each entry records its fixed source invocation, observed version,
and normalization. ANSI escapes and manual overstrikes are removed; selected
declaration lines and up to two continuation lines are placed under an explicit
Options heading. Local home/environment paths are replaced by placeholders.
Root npm retains its complete short help response. These are
excerpts, not complete manuals or snapshots of every option. The independently
maintained live sentinels and argument counts are also asserted against them.

The corpus includes nested command paths, alias spacing, `--[no-]` negation,
kubectl default values, AWS type labels, jq's two-value declarations, optional
Cargo values, and yt-dlp's partially optional templates. Tests also verify every
synthetic fixture flag's exact midline edit, required-value handling, global
options, positional boundaries, and fixed executable/manual probe arguments.

GCC comma-joined switches, FFmpeg stream selectors, and 7-Zip attached-value
switches are outside the current literal insertion grammar. They must not be
truncated into different flags. Root npm intentionally lacks option declarations;
usage examples must not become insertable flags. `npm-install.txt` separately
covers bracketed option groups, aliases, and repeated values.

`example-tool.1` is an original minimal roff page used for plain and gzip
manual-rendering tests. Compressed fixtures retain their original bytes.

To extend coverage, add a matrix entry, a representative specimen, independently
chosen assertions, and a source-labelled captured excerpt when available. Add or
extend the relevant JSON driver when a special help route or subcommand path is
required. Keep unavailable live validation explicit. The harness installs no
packages; local downloads and environments belong in ignored `.cache/` storage,
and live reports belong in ignored `tests/reports/` storage.
