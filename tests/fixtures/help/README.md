# Help-format corpus

These compact, hand-authored fixtures preserve representative declaration shapes
and use paraphrased descriptions. They are not complete command documentation.
FFmpeg, GCC, npm, and pip shapes were checked against local Ubuntu 24.04 help
output. VLC shapes are synthetic; no local VLC executable was available.

`matrix.json` records expected literal flags, argument placeholders, unsupported
forms, and a small set of stable flags for optional live checks. npm's root help
deliberately has no declarations: usage examples must not become insertable flags.
GCC comma-joined options and FFmpeg stream-specifier flags are outside the current
literal insertion grammar and must not be truncated into different options.
`npm-install.txt` covers bracketed subcommand options, shared aliases, and repeated
value syntax. `example-tool.1` is an original minimal roff page used for plain and
gzip manual-rendering checks.

Additional fixtures can be added with a matching matrix entry. A missing live
command is reported as skipped; offline coverage does not prove compatibility
with an installed version. No packages are installed by the harness.

The [development and validation guide](../../../docs/development.md#extended-tests-and-live-compatibility-reports)
describes the test harness and live report commands. The
[documentation index](../../../docs/README.md) links setup and compatibility guides.
