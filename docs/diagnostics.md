# Passive diagnostics and troubleshooting

[Project overview](../README.md) · [Documentation index](README.md) ·
[Discovery and execution boundaries](discovery-and-safety.md)

Commands in this guide run from the repository root. Both diagnostic modes emit
JSON. They do not invoke target programs, run documentation probes, write caches
or bytecode, change bindings, open a terminal browser, or edit pending input.
Filesystem configuration and existing cache envelopes are inspected read-only.
Executable availability does not establish executable versions or live operation.

## Runtime and configuration inspection

```bash
python3 cli_help/main.py --doctor
```

The report identifies Python, Linux, UTF-8, curses, Bash, stty, and optional man
availability. Bash 4.4 or newer remains required; its version is not established
by this passive check. Terminal availability is informational, so redirected
diagnostic output remains supported. The selected profile, driver, key, and cache
locations are reported with configuration validity and discovery settings.
Other environment values and configuration file contents are omitted.
If the configured interpreter cannot start, the native launcher reports the
runtime role and operating-system error without echoing `CLI_HELP_PYTHON`.
The Bash adapter reports `interpreter_unavailable`, preserves pending input, and
directs inspection of `CLI_HELP_PYTHON` and `PATH` without reproducing their values.
These startup failures precede JSON report generation; passive Python reports
require a usable interpreter.
`configuration.escape_delay_ms` reports the validated curses key-sequence delay;
invalid values produce `invalid_escape_delay` without reproducing the value.
The UTF-8 check examines the shell locale rather than Python UTF-8 mode. An ASCII
`C` locale remains incompatible even when Python's preferred encoding is UTF-8.
Unexpandable configuration home paths produce an attention/rejection report
instead of a traceback; selected paths can remain unexpanded in that report.

The supplied driver collection remains explicitly enabled:

```bash
export CLI_HELP_DRIVERS="$PWD/config/drivers.example"
python3 cli_help/main.py --doctor
```

No driver collection is automatically enabled or combined by diagnostic modes.
`configuration.driver_selection` reports `source` (`built_in` or
`CLI_HELP_DRIVERS`), the selected `directory`, the supplied directory's
availability, and `supplied_selected`. The latter is true only when that exact
directory is selected, including a symbolic-link spelling of it. Copies in a
combined custom collection remain custom selections; content is not used to
infer activation. Composition remains `built_in_then_one_directory`.
See [manual driver composition](profiles-and-drivers.md#activation-and-manual-composition)
for precedence, conflict rules, and preserving local changes.

## Explain a command context

`--explain` reads the same `CLI_HELP_LINE` and character-based `CLI_HELP_POINT`
inputs as the Bash helper. It does not print the input buffer or operand values.
The following example inspects a separate buffer without accepting a shell line:

```bash
CLI_HELP_LINE='docker compose -f local.yml --profile debug up --det'
export CLI_HELP_LINE
export CLI_HELP_POINT=${#CLI_HELP_LINE}
python3 cli_help/main.py --explain
unset CLI_HELP_LINE CLI_HELP_POINT
```

The report includes the resolved documentation path, static-profile provenance
when available, discovery policy, relevant cache status, and a stable reason code.
`driver_selection` uses the same activation fields as `--doctor`. The `route`
object identifies `configured`, `built_in`, `generic`, `module_adapter`,
`profile_only`, or `unconfigured` provenance, its documentation selectors and driver positional
boundaries. `profile_only` permits an explicit static profile without inventing
an automatic discovery request. Its help array is empty and its manual is null;
when caching is enabled, cache status is `not_applicable` for that path.
An intermediate driver path with neither a profile nor its own help route is
`unconfigured`; recognizing the path does not establish usable documentation.
Configured routes include their JSON `file`; retained built-in
routes remain labelled built-in even when another route in that program is
overlaid. `global_options` identifies the overlay file and whether its global
arity is combined with built-in declarations. Static-profile provenance remains
separate: the selected profile can avoid discovery while the route still defines
context boundaries. Reports describe metadata, not live executable behavior.
Only recognized documentation selectors and resolved route words are retained
in `help_arguments`. Other fixed configured operands are shown as `<redacted>`;
`help_arguments_redacted` indicates substitution. Custom manual aliases are
also redacted unless they match the canonical executable or command-path manual,
with `manual_redacted` reporting that substitution. Redaction affects reports
only. Discovery retains its configured fixed requests and execution policy.
Configuration locations remain visible and require review before sharing.

Root pytest reports its mandatory `--help --noconftest` request and
`help_override: pytest_no_conftest`, including when a driver supplies another
declaration. Yarn run reports `help_arguments_pending_identity: true` because
its effective request depends on the existing active version check. Passive
inspection never performs that check.
The actual resolver and argument-position validator perform the inspection.
No alias, shell function, substitution, or pending option value is evaluated.

| Status | Meaning |
| --- | --- |
| `ready` | Available metadata permits the editable position; no insertion or execution occurred |
| `needs_discovery` | Fresh help, a static profile, or active executable-identity evidence is required |
| `metadata_unverified` | A cached candidate permits argument inspection, but its required identity request was not run |
| `rejected` | Configuration, syntax, cursor position, or an argument boundary prevents the context |

`ready` does not prove a complete command is valid. It can describe an ordinary
static profile without an installed executable. Cache inspection does not make
generated documentation authoritative. Module and vendor/version cache candidates
remain unverified until their normal active identity checks run.

Passive cache inspection reports age, TTL, source-warning count, and fixed warning
codes such as `source_timeout`, `source_unparsed`, and `manual_unavailable` without
printing cached descriptions or arbitrary probe output. Identity-dependent
lookups inspect at most 128 cache envelopes. `inspection_limited` indicates that
additional entries may exist; absence from that bounded inspection is not proof
that no matching entry exists.
Cache readers reject symbolic links and special files, including FIFOs. The
byte limit applies to actual reads as well as initial size metadata, so a growing
entry cannot cause an unbounded read. Rejected entries are treated as misses.

## Rejection codes and recovery

| Code | Interpretation and next step |
| --- | --- |
| `unsupported_option` | A global or parent option has unknown arity; inspect the driver declarations |
| `option_value_required` | Complete the preceding required argument; use an attached form for ambiguous dash-leading parent values |
| `unsupported_subcommand` | Add an explicit supported route or static profile |
| `cursor_in_operand`, `cursor_in_value` | Move to an empty argument or editable option name |
| `end_of_options`, `child_argument_boundary` | Move before the delimiter or child-command region |
| `incomplete_quote`, `incomplete_escape` | Complete the literal shell word |
| `unsupported_shell_syntax` | Use a supported single simple command |
| `invalid_cursor` | Supply a valid character offset within the buffer |
| `invalid_executable` | Supply a literal executable name; malformed option-looking tokens are omitted before resolved metadata is reported |
| `discovery_required` | Obtain documentation through an explicit active lookup or a reviewed static profile |
| `identity_verification_required` | Normal auto discovery must verify module or executable identity |
| `discovery_disabled` | Supply an ordinary static profile or explicitly select another discovery mode |
| `configuration_invalid`, `inspection_failed` | Inspect selected files, permissions, and documented configuration constraints |

Unsupported tokens and their attached values are omitted from normal errors.
For example, an unrecognized `--token=...` global option reports unknown arity
without reproducing its value. The original pending command can still be visible
at the Bash prompt; preserving that buffer is separate from diagnostic output.

## Explicit active inspection and timing

An active lookup requires a separate invocation:

```bash
python3 cli_help/main.py --discover docker compose up --refresh
```

This command uses existing fixed documentation routes and may run the target
program's help request in auto mode. Only the executable and reviewed command
path belong in `--discover`; pending options, credentials, filenames, and child
commands must not be supplied. The result contains discovered documentation,
unlike the passive reports above.

The normal timeout remains two seconds per source. Cold ordinary lookups can
query help and a manual sequentially. Auto-mode Python module lookups check a
fixed version response before cache reuse; a cold lookup additionally obtains
module help. Guarded vendor/version routes also perform their identity request
before cache reuse. A warm cache therefore does not imply zero subprocesses for
these identity-dependent routes.

For an explicitly slower diagnostic lookup:

```bash
CLI_HELP_DISCOVERY_TIMEOUT=15 python3 cli_help/main.py --discover docker compose up --refresh
```

A result at this longer limit does not establish responsiveness at the normal
two-second limit. The timeout applies per request, rather than to the complete
browser-opening sequence. See [cache freshness](discovery-and-safety.md#cache-and-inspection)
for invalidation and refresh limits.

Exit status `0` means passive inspection completed, including an explicit
`needs_discovery` or `metadata_unverified` outcome. Status `1` means a rejected
context or runtime/configuration attention is required. Status `2` indicates
invalid CLI arguments. No diagnostic status establishes rendered terminal or
operational third-party compatibility.

## Collection consistency

`--check-collection DIRECTORY` inspects collection-owned metadata and evidence
without executing discovery, writing files, or altering locks. It is independent
of the pending buffer and personal configuration. Reports distinguish invalid
metadata from intentional unpaired collections, stale review evidence, and
uncertain lock ownership. [Collection inspection and explicit recovery](collection-recovery.md)
documents the JSON statuses, reason codes, bounds, privacy, and separate
snapshot-bound restoration action. Recovery is an explicit write operation;
it is not part of passive inspection or normal browser startup.
