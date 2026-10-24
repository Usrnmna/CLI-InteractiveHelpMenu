# Explicit value forms and short-option bundles

[Documentation index](README.md) · [Profile schema](profiles-and-drivers.md) ·
[Invocation boundaries](invocation-and-structured-arguments.md)

Argument syntax is declared per profile option. It does not evaluate a shell,
validate an entire command, or change any fixed documentation request. Selecting
an option edits the pending buffer; values and operands are never dispatched.

## Value forms

An option with one required or optional value can set `argument_style`:

| Value | Accepted spellings | Selection |
| --- | --- | --- |
| `separate` | `-n VALUE` or `--name VALUE` | Flag and a separator |
| `equals` | `--name=VALUE` or `-n=VALUE` | Flag followed by `=` |
| `attached` | `-nVALUE` and `-n VALUE` | Flag and a separator |
| `attached_only` | `-nVALUE`, including `-o'quoted directory'` | Flag with no following separator; type the value immediately |

The explicit styles require a flag, a nonempty display-only `argument`, and
`argument_count` of one. A flag ending in `=` requires style `equals` when a
style is specified. Styles cannot be combined with the legacy `attached` field.
Omission retains the old grammar: separate and equals values, plus joined values
when `attached: true` is declared. Existing JSON does not acquire bundle support.
Explicit syntax profiles reject duplicate canonical names such as separate
`--name` and `--name=` definitions, which would otherwise hide each other's arity.

`argument_optional` describes whether the entire value can be omitted. It is
independent of optional components inside a required value, such as `HOST[:PORT]`.
A required value is not made optional by brackets inside its placeholder.
Explicit required values must be complete before another option is selected.
Separate negative numeric values are accepted; dash-leading nonnumeric values
must use a permitted attached form. Empty required attached values are rejected.
Optional values retain conservative behavior and do not consume arbitrary
following words. The separately documented `optional_value_kind` count grammar
remains unchanged.
An optional attached-only or equals-only value can be omitted with the bare
flag; when a value is present, it must use the declared attached form.

## Bundles

`bundle: true` opts a single-character short flag into bundle recognition.
Every member must be declared. Boolean members can repeat; a required-value
member ends the bundle and consumes either the remaining payload or a following
value only when its own metadata permits that form. Optional-value members,
multi-value members, keywords, long names, and equals-only members cannot opt in.

For example, boolean `-a` and `-b`, plus required `-n` with style `attached`,
can represent `-abn5` or `-abn 5`. Style `separate` permits only the latter.
Style `attached_only` requires a remaining payload. An exact declared `-ab`
name takes precedence over splitting `-a` and `-b`. If two remaining declared
interpretations are possible, the token is rejected with `ambiguous_short_token`.
Unknown members and unknown completed options in an explicit-form/bundle profile
are rejected rather than assigned guessed arity.
Known value-taking members with missing attached payloads report
`option_value_required`; a value using a disallowed spelling reports
`unsupported_value_form`. Neither error reproduces the payload.

The bundled OpenSSH profile opts in only `-4`, `-6`, `-C`, `-q`, `-v`, and `-p`.
This permits `ssh -vCp22 -i` before the destination, including repeated `-v`.
It retains the destination and child-command boundary. The
[OpenSSH reference](https://man.openbsd.org/ssh.1) and captured manual establish
these flags; no SSH session is launched by the browser or its tests.

An existing bundle or attached payload is protected as a complete token. Help
cannot replace it from a cursor inside the payload, nor edit across positional,
`--`, or child-command boundaries. Literal quotes, whitespace, Unicode, suffixes,
and character cursor offsets outside the selected option remain preserved.

## Bounded 7-Zip subset

The bundled `7z x` and `7zz x` static profiles expose `-o`, `-t`, `-y`, and `-bd`.
`-o` and `-t` use `attached_only`: selecting `-o` leaves the cursor immediately
after it, ready for a directory. Existing `-o'café dir'` and `-tzip` payloads
are protected. This subset does not validate archive types or perform extraction.
The [output-directory reference](https://7-zip.opensource.jp/chm/cmdline/switches/output_dir.htm)
limits `-o` to extraction, and the
[archive-type reference](https://7-zip.opensource.jp/chm/cmdline/switches/type.htm)
describes the attached type value. Captures use installed 7-Zip 23.01.

These are static profile paths, reported as `profile_only` by `--explain` with
the supplied drivers. The root drivers retain their existing fixed `-h` request;
adding only an `x` child driver would narrow other root command contexts.
`--discover 7z x` and `--discover 7zz x` therefore remain unavailable. Their
live evidence uses the fixed root `-h` output separately from curated edits.
Generic discovery still excludes brace-attached declarations instead of
truncating `-o{Directory}` into an inaccurately spaced option.

General short bundles, GCC comma-joined passthrough, placeholder stream selectors,
arbitrary expressions, and general shell parsing remain excluded. Declaring one
program's forms does not enable them for other programs or parent-driver options.
