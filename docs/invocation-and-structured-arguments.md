# Prefixes, Python modules, and structured arguments

[Project overview](../README.md) · [Compatibility matrix](compatibility.md) ·
[Profile reference](profiles-and-drivers.md)

Alt-H resolves a documented command without executing the pending input. Selection
replaces one option or keyword token. All surrounding text, quoting, tabs, spaces,
and suffix arguments remain intact. Cursor offsets are Unicode character offsets;
terminal display columns can differ for wide characters.

## Recognized prefixes

Supported pending examples:

```text
sudo -n -u operator systemctl status --
env LABEL='café 日本' ssh -
command -- python3 -m pip install --
command sudo -gstaff env LABEL='two words' rsync --ar
env LABEL=example sudo --user=operator journalctl --
```

| Prefix | Supported syntax |
| --- | --- |
| `command` | Bare builtin or `command --`, before any external prefix |
| `sudo` | `-n`, `--non-interactive`, `-E`, `--preserve-env`, `-H`, `--set-home`, `-k`, `--reset-timestamp`; value options `-u/--user`, `-g/--group`, `-p/--prompt`; assignments and `--` |
| `env` | Assignments; `-u NAME`, `-uNAME`, `--unset NAME`, `--unset=NAME`; `--` |

Short value options accept attached values; long value options accept `=value`.
Supported unset names use shell variable identifier syntax. Assignments are
recognized only after `env` or `sudo`. Prefix chains retain every original token.
The `command` builtin cannot be placed after an external `sudo` or `env` prefix.

Prefixes are never executed by discovery. Documentation uses the current local
executable lookup and environment, without applying sudo privileges, sudoers
`secure_path`, requested users, or pending environment changes. This identifies
local documentation; it does not establish which installation a privileged
command would eventually execute. An explicit target path can select a local
executable precisely.

Lookup-changing or ambiguous forms fail with a diagnostic. These include
`command -p/-v/-V`, sudo shell/login/remote-host/chdir forms, `env -i/-C/-S`, unknown
prefix options, incomplete option values, and lookup/loading assignments such as
`PATH`, `PYTHONPATH`, `PYTHONHOME`, `MANPATH`, `LD_PRELOAD`, or `LD_LIBRARY_PATH`.
Prefix options and values never become options of the target command.

The grammar follows bounded subsets of the upstream
[Bash command builtin](https://www.gnu.org/software/bash/manual/html_node/Bash-Builtins.html),
[GNU env invocation](https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html),
and [sudo command syntax](https://www.sudo.ws/docs/man/sudo.man/).

## Python module documentation

`python -m pip` and `python3 -m pip` support root help and `install`, `uninstall`,
`download`, and `list`, matching the pip driver collection. Both interpreter names
also support `-m pytest`. Literal paths ending in `python` or `python3` select that
interpreter, including virtual environment symlinks.

Before `-m`, the supported switches are `-I`, `-E`, `-s`, `-S`, `-B`, `-u`, `-O`,
and `-OO`. Their order and original buffer text are retained. Interpreter options
with values, `-c`, script paths, joined `-mpip`, arbitrary modules, and pip's
interpreter-changing global `--python` form are rejected. Some supported switches,
especially `-S`, can make an installed module unavailable; that remains a discovery
failure rather than a fallback to a different installation.

Normal auto discovery invokes a fixed module version request, followed on a cache
miss by fixed module help through the selected interpreter:
`python3 -m pip help install`, for example. Pending package names, pytest test
paths, `-p` plugins, Python code, and module search paths are never forwarded.
Pip identity uses `--version`; pytest identity uses `--version --noconftest`.
Pytest help uses `--help --noconftest` with plugin autoload disabled in a temporary
working directory. Explicit interpreter isolation switches are retained. Ordinary
JSON drivers cannot replace the selected interpreter or module help route.

Automatic module help does not merge a separately installed pip executable or
system manual into the selected interpreter's result. Manual-only mode uses a
fixed module manual without running Python and labels its installed-version
context as unverified. Discovery-off mode requires an explicit reviewed profile
whose command is, for example, `["python3", "-m", "pip", "install"]`; an ordinary
`["pip", "install"]` profile cannot substitute. Cache version 8 includes the
interpreter invocation path, file identity, module, interpreter switches, route,
mode, virtual-environment configuration identity, a hash of the probe HOME
context, and executable variant evidence. Auto
module lookups additionally fingerprint fixed version output before each cache
read, detecting changed versions and reported pip import locations. Unrecognized
or failed version responses disable cache reads and writes for that request;
fresh help is still attempted. Same-version local edits with unchanged version
output require expiration or explicit refresh. Man-only and discovery-off modes
never perform module-version requests. [Passive explanations](diagnostics.md)
label module cache candidates as unverified without invoking the interpreter.

## Keywords, joined selectors, and value groups

`ip address`, `ip link`, and `ip route` have curated listing/filter keywords.
Entries such as `show`, `dev`, `scope`, and `table` are marked **[keyword]** in
the browser. A keyword can replace an unquoted or quoted partial keyword token;
values such as an interface name remain ordinary arguments. Required keyword
values must be completed before another entry can be selected. These profiles
cover the documented listing/filter subset, not every mutating ip subgrammar.

Concrete colon-joined flags such as `-c:v`, `-c:a`, and `-c:v:0` are complete
literal names. The bundled FFmpeg profile provides common codec, bitrate, and
filter selectors. A selection inserts the selector followed by a space; it never
inserts `CODEC` or another placeholder. Generic placeholders such as
`-c[:stream_specifier]` and incomplete `-c:` are not valid profile replacements.
See [FFmpeg stream specifiers](https://ffmpeg.org/ffmpeg.html#Stream-specifiers).
GCC comma pass-through forms and 7-Zip brace-attached forms remain unsupported.

An option marked `attached: true` consumes an attached value, such as SSH
`-p22`, when locating subsequent options. A cursor inside that value cannot
replace it as though it were an option name. Selection itself inserts only the
literal flag and a separator, leaving value entry to the operator. `=value`
supplies the first value of a multi-value option. Negative values and quoted
Unicode values occupy argument slots without being reparsed as new flags.

The fzf multi-selection switches accept an optional nonnegative count:
`-m`, `-m2`, `-m 2`, `--multi`, `--multi=2`, and `--multi 2`.
Explicit `optional_value_kind: "nonnegative_integer"` metadata permits one
separate ASCII decimal token. Untyped optional arguments retain their conservative
boundary; arbitrary text, signed numbers, and `--` are not swallowed as counts.
Selection still inserts only the flag and separator.

Esptool `write-flash` profiles represent a repeated `ADDRESS FILE` positional
group. Complete pairs can be followed by another pair or an option. An incomplete
pair blocks option insertion. `--` or an option-looking filename cannot complete
a missing file slot; use an unambiguous path such as `./-firmware.bin` where the
target supports it. The browser describes the group, but never inserts addresses,
filenames, or placeholders. Discovery does not open serial ports or flash firmware.

Child-command boundaries stop parent option insertion after the SSH destination,
container/service name, script or Go program, and comparable runner positionals.
`--` stops parent option insertion. Expression-oriented profiles such as yq also
stop before an expression can expose its internal flags as parent options.
Go test and .NET test retain parent options after package/project paths. Go
`-args` and the general `--` marker delimit child arguments. Unknown preceding
option arity is rejected at strict positional boundaries.

## Names, versions, and offline use

- `fd` and Debian/Ubuntu's `fdfind` have separate routes for the same fd syntax.
- `pio` and `platformio` each provide `run` and `device monitor` routes.
- Mike Farah yq v4 is identified by fixed `--version` output. Other `yq` products
  are rejected rather than treated as compatible YAML processors.
- JavaScript Yarn is distinguished from Debian `cmdtest`'s namesake. Classic and
  modern Yarn runner help use separate fixed selectors selected from version
  evidence. Dynamic help retains the installed version's options; no tiny shared
  profile masks their differences.
- Esptool v5+ uses `esptool write-flash` or the explicit `esptool.py write-flash` alias. The legacy v4 `esptool.py write_flash` route is
  separate and never silently rewritten. Version checks reject a spelling outside
  its declared version family.
- Guarded vendor/version profiles need normal discovery to establish identity.
  Manual-only and discovery-off modes reject them unless an explicitly reviewed
  custom profile removes the `identity` requirement. Such an override represents
  operator-maintained documentation, not automatic version verification.

Ordinary curated profiles remain usable without installed targets in all discovery
modes. Curated documentation specifies a maintained option subset; successful
browser insertion does not establish a valid complete workload or physical result.
