# Help profiles and compatibility drivers

[Project overview](../README.md) · [Documentation index](README.md)

Commands in this guide are run from the repository root unless stated otherwise.

## Editable help profiles

Each file in `profiles/` describes one command or command/subcommand path. A
minimal additional profile has this structure:

```json
{
  "command": ["example"],
  "description": "Example command help.",
  "categories": [
    {
      "name": "Output",
      "description": "Output configuration.",
      "options": [
        {
          "flag": "--output",
          "argument": "FILE",
          "summary": "Write output to a file",
          "detail": "Enter the file path after inserting the option."
        }
      ]
    }
  ]
}
```

`argument`, `detail`, and the category description are optional. An option with
a trailing equals sign, such as `--exclude=`, leaves the cursor directly after
that sign. Other options insert or reuse one following whitespace character.
Argument placeholders are displayed as help and are never inserted literally.
An option may also set `"argument_optional": true`. Optional arguments are
displayed but do not force entry of a value before another option is selected.
`argument_count` specifies how many following values are required (default `1`,
integer range `1`–`16`). For example, jq's `--arg name value` has
`"argument_count": 2`. Multiple values require a nonempty `argument` placeholder.
An inline `=value` supplies the first value. The count is editable in JSON;
guided edits preserve it, and clearing the argument also clears the count.

Custom profiles can reside in a separate directory:

```bash
export CLI_HELP_PROFILES="$HOME/.config/cli-help/profiles"
python3 cli_help/main.py --list-commands
python3 cli_help/main.py --check
```

A custom profile replaces a bundled profile with the same `command` path.
Two profiles defining the same command within one directory are rejected.
Profiles contain data only. Ordinary option names use literal flag syntax;
structured keyword and concrete colon-selector forms are described below.

`CLI_HELP_PYTHON` optionally selects a Python executable, such as
`/usr/bin/python3`. `CLI_HELP_CONFIG` and `CLI_HELP_PROFILES` must be exported so
the helper process can read them.

## Structured profile metadata

| Field | Behavior |
| --- | --- |
| `options[].kind` | `flag` by default; `keyword` permits a literal bare keyword such as `dev` |
| `options[].attached` | Boolean; recognizes an attached argument for a value-taking flag such as `-p22`; default false |
| `options[].optional_value_kind` | `nonnegative_integer` recognizes one separate ASCII decimal count after a single optional argument, such as `fzf -m 2`; other values are rejected |
| `stop_at_positional` | Profile-level boolean boundary, retained even without a loaded driver |
| `stop_at_options` | Literal option-name array that ends the parent argument region, such as Go test's `-args` |
| `positional_group` | Object with `argument`, `argument_count` (2–16), and `repeatable: true`; complete repeated groups delimit safe insertion positions |
| `identity` | Built-in guard: `mikefarah-yq-v4`, `javascript-yarn`, `esptool-v4`, or `esptool-v5`; cannot contain code or an executable path |

Concrete selectors such as `-c:v:0` are valid flags; `-c:`, placeholder selectors,
whitespace, and shell operators are rejected. Keywords cannot contain shell
syntax. All argument labels remain display-only. Repeated groups are entered
manually; the browser never supplies placeholder values. Guided edits preserve
these JSON fields; clearing a value argument also clears its `attached` and
`optional_value_kind` metadata. Changing an optional argument to required clears
`optional_value_kind`. This field requires a nonempty argument, optional-value
metadata, and an argument count of one. It never consumes arbitrary text,
signed numbers, another option, or an end-of-options marker.
Structured fields can be maintained through JSON/editor review and survive
installation and update workflows.

See [supported forms and exact insertion behavior](invocation-and-structured-arguments.md).

## Loadable compatibility drivers

A driver describes how documentation is obtained; a profile supplies the actual
option documentation. JSON drivers add programs, nested subcommands, global-option
arity, fixed help requests, manual names, and positional boundaries without Python
source changes. Static profiles still take precedence for the exact command path.

To enable the included third-party driver collection from the checkout:

```bash
export CLI_HELP_DRIVERS="$PWD/config/drivers.example"
python3 cli_help/main.py --check
python3 cli_help/main.py --list-drivers
python3 cli_help/main.py --discover pip install
python3 cli_help/main.py --discover npm install
```

After loading the Bash adapter, pending lines such as `pip install --` and
`npm --prefix project install --` can use Alt-H. A separate included `pip3`
driver provides the same pip routes for that executable name. The
[compatibility matrix](compatibility.md) lists all included programs and tested paths.
To maintain an independent collection, copy the
[example driver files](../config/drivers.example) into a local directory and set
`CLI_HELP_DRIVERS` to that directory. Drivers are reloaded
on each helper invocation.

A minimal driver for another program is:

```json
{
  "command": "example",
  "global_values": ["--config"],
  "global_flags": ["--quiet"],
  "paths": [
    {"command": [], "help": ["--help"], "man": "example"},
    {
      "command": ["image", "convert"],
      "help": ["help", "image", "convert"],
      "man": "example-image-convert",
      "stop_at_positional": true
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `command` | Executable basename; one file per program in the configured directory |
| `global_values` | Global options that consume one following value; attached short values and long `=value` forms are accepted |
| `global_flags` | Global boolean flags; explicit `=true` and `=false` forms are accepted |
| `paths[].command` | Exact subcommand words, or `[]` for root help |
| `paths[].help` | Fixed argument array beginning with `help`, `--help`, `-h`, or `-help`, or exactly the declared command path followed by one of those selectors; `[]` disables executable probing for that path |
| `paths[].man` | Literal manual name in sections 1 or 8; `null` disables the manual source |
| `paths[].stop_at_positional` | Reject insertion after the first positional argument; unknown preceding option arity is also rejected |
| `paths[].stop_at_options` | Reject insertion after named child-argument delimiters; defaults to an empty array |
| `paths[].option_values` | Unique literal options consuming one value before a child command; separate, long `=value`, and short attached values are supported |
| `paths[].option_flags` | Unique literal parent boolean options; explicit `=true`/`=false` forms are supported |

Every route requires at least one help or manual source. Omitted global lists
are empty; the positional boundary defaults to false. Matching built-in routes
are replaced, while other routes remain available. Global lists extend existing
lists; conflicting arity is rejected. An omitted root route retains generic
`--help` and same-name manual discovery. Duplicate program files, duplicate
paths, unknown fields, invalid values, and files over 256 KiB are rejected before
any probe. A changed help route or manual name changes the cache identity.

Parent-option lists extend command recognition, not the executable help request.
For example, the supplied `docker compose` route declares `-f`/`--file`, `-p`/
`--project-name`, and `--profile`, permitting
`docker compose -f local.yml --profile debug up --` to select the leaf route.
Each parent level declares its own options; arity is not guessed or inherited
from unrelated routes. Executable root options retain `global_values` and
`global_flags`; nonempty parent lists on the root route are rejected. Nonempty
parent lists enable strict scanning at that level. Unknown parent options,
empty required parent values, and ambiguous bundles are rejected.
Separate negative numeric values are accepted; other dash-leading values require
an explicit attached spelling. Root global options retain their existing literal
value grammar, including empty or dash-leading operands where the target supports
them. Exact declared option names take precedence over short-option payload
recognition. Attached parent/global short-option values are not editable option
tokens, even when parsed help omits attached-value metadata.
Existing routes without parent lists retain their
previous parent-option behavior. The lists default to empty, cannot overlap,
and are preserved by manual import and review saves.

Drivers contain no executable Python, shell snippets, interpolation, or references
to the pending buffer. Only their fixed help arrays and manual names become probe
arguments. The selected executable remains the one resolved from the typed
executable name; a driver cannot substitute a separate executable. Driver files
are trusted local configuration: a help selector is not a sandbox or proof that
an arbitrary program has no startup side effects. Man-only mode suppresses all
driver executable probes.

The pip example uses `pip help install`; the npm example uses
`npm --help install`. Pending package names, script names, configuration paths,
and flags are never forwarded. `npm run` sets a positional boundary so insertion
cannot accidentally target the script's arguments. Root `npm --help` may have
no option declarations; subcommand discovery supplies the useful option lists.
Suffix selectors support fixed routes such as `terraform plan -help`,
`aws s3 cp help`, and `docker compose up --help`. The words preceding a suffix
selector must exactly match the declared path; additional arguments, templates,
or a different action are rejected. These routes contain no pending buffer values.

Profiles and drivers can also be generated through [manual import](manual-import.md)
or [bulk scanning](bulk-scan.md). The [interactive reviewer](review.md) provides
guided corrections for collections with scan reports. See
[discovery and safety](discovery-and-safety.md) for source limits and cache behavior.
