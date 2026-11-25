# Three levels of option help

**Status** — The [reviewed mockups](2026-11-24-menu-detail-levels-preview.md) were approved for implementation. The browser now provides all three levels, compact category labels and a recoverable full title. [Actual terminal frames at both sizes](2026-11-24-menu-detail-levels-verification.md) record the implemented layout. The phase checklist below preserves the review specification.

**Goal** — Make it easy to scan a menu, distinguish adjacent options, and read as much guidance as the current choice needs.

**Implementation scope** — The existing Python curses browser serves bundled profiles, discovered help, custom profiles, and authoring previews. Keep the work in its existing presentation, rendering, and keybinding paths. The request covers how option information appears. Profiles, discovery, shell insertion, and release packaging have separate responsibilities.

## Reading an option

The [six full-screen mockups](2026-11-24-menu-detail-levels-preview.md) show the same FFmpeg selection in all three modes at 80×24 and 60×16. They illustrate proposed spacing, unit labels, and viewport behavior for human review.

| Level | What the user sees | Example for FFmpeg `-b:v BITRATE` |
| --- | --- | --- |
| **Simple** · proposed default | One short summary per option. Show the distinguishing action first. Reserve space for an existing review or uncertainty notice where applicable. | Set the target video bitrate. |
| **Detailed** | The list stays scannable. The selected option gets about two or three lines covering its purpose and the most useful input rule, constraint, or example. | Set the target video bitrate. Enter a value such as `2M` for 2,000,000 bps. Rate control depends on the encoder. |
| **Expanded** | The selected option gets the full scrollable usage explanation. Include the complete spelling, operand syntax, documented forms, defaults, exceptions, applicable versions, and examples wherever available. Show command-wide guidance once in its own labeled section when relevant. | Retain the Detailed guidance and explain decimal prefixes, the binary `i` suffix, and how a final `B` multiplies the rate by eight. Show the documented input forms and their qualifications. |

Line counts refer to ordinary terminal widths. A long flag, a narrow terminal, or a material warning can require another physical line. Keep the list summary visible in every mode. In Simple, allocate zero detail-body rows when the selected entry already shows its complete summary and declaration. Reclaim the unused detail footer/progress row as well. Reserve only the rows needed to recover clipped text or convey an essential warning. Give every remaining content row to the list, including when the user returns from Expanded. A short option can have the same explanation at all levels without repeating that sentence twice on screen.

**Source URLs have no place in any of the three views.** This applies to the list, shared notes, selected details, and authoring preview, including scrolled Expanded content. Omit citation labels, reference locators, and audit history too. Keep a limitation such as “the default varies by version” wherever it affects use. A URL operand or a URL scheme documented as command syntax is distinct from a citation. Maintain the existing profile evidence and search behavior independently of terminal formatting.

### Shared facts and spacing

A two-option excerpt illustrates the proposed spacing. The shared statement identifies exactly which inputs it describes.

```text
OPTIONS · Simple        D change detail
Bare bitrates use bps (bits/second)

> -b:v BITRATE    Set the target video bitrate.

  -b:a BITRATE    Set the target audio bitrate.
```

This excerpt uses the `-b:` filter in FFmpeg’s **Stream codecs** category. The heading fits the existing 39-cell option budget at 60 columns. Clear the filter and the category also contains codecs and filters. Use local unit labels in a mixed list unless the note explicitly names the subset and stays visible with it. A buffer size in bits cannot share a bit-rate heading.

A second kind of repetition occurs **inside a single option**. Today, FFmpeg's `-b:v` repeats “bits/second” across its suffix forms, even as the only search result. In Expanded, put the result unit in one heading and align the accepted literal inputs with their conversions. The excerpt below illustrates four forms. The full view retains every documented form, scope, range, and encoder constraint.

```text
-b:v BITRATE    Set the target video bitrate

Input for N      Rate in bps (bits/second)
N                N
Nk or NK         N × 1,000
NKi              N × 1,024
NB               N × 8
```

### Unit examples from the bundled menus

A planning inventory examined 6,487 option rows across 76 bundled profiles, following shared value definitions and component forms. The examples below pair existing guidance with proposed display and search vocabulary. Compact labels describe meanings. Each command still accepts exactly its documented input spellings.

| Menu and current guidance | Proposed presentation | Distinction to verify |
| --- | --- | --- |
| [rsync bandwidth](../../../profiles/rsync.json#L2855) repeats “1024 bytes/second” for a bare rate and binary suffixes | Use `KiB/s` for the bare rate. Group the other forms under a byte-rate heading, with `B/s`, `kB/s`, or `KiB/s` where appropriate. | Decimal `KB` and binary `K` are distinct rsync inputs. A byte-rate operand does not gain a bit-rate search alias. |
| [GNU ls display blocks](../../../profiles/ls.json#L1082) gives 1,024 and 1,000 bytes per unit across multiple spellings | Show the literal suffixes beside compact meanings such as `KiB`, `kB`, `MiB`, and `MB`. | Keep accepted casing, per-form bounds, and implementation-specific variants. |
| [Go test timeouts](../../../profiles/go-test.json#L56) repeats decimal fractions of a second and the same timeout rule across forms | Group units as `ns`, `µs`, `ms`, `s`, `min`, and `h`. State the shared rule once. [OpenSSL certificate validity](../../../profiles/openssl-x509.json#L1742) can show “days” directly in place of “86400 seconds” for each day. | Go accepts `m` for minutes and several microsecond spellings. Retain its bare-zero exception. OpenSSL takes a count of days. |
| [esptool flash clocks](../../../profiles/esptool-write-flash.json#L47) repeats both “20000000 hertz” and “20 MHz” for the same choice | Use a “Clock (MHz)” column and retain literal tokens such as `20m` and `40m`. | Preserve chip-specific choices and the separate meaning of `keep`. A search for MHz does not imply that `20MHz` is accepted input. |
| [FFmpeg video rate](../../../profiles/ffmpeg.json#L6261) and [audio sample rate](../../../profiles/ffmpeg.json#L8059) both use hertz | Show `fps` for frames per second and `Hz` for audio sample rate. Keep rational video rates such as `30000/1001`. | The subject determines whether `fps` applies. A frequency dimension alone is insufficient. |
| [fzf height](../../../profiles/fzf.json#L315) repeats terminal rows and “0.01 of terminal height.” [7-Zip memory](../../../profiles/7z-x.json#L1541) also uses percentages. | Group fzf’s forms under “rows” and “% of terminal height.” Label the 7-Zip percentage as “% of available decoder RAM.” | Keep the percentage basis and the effects of fzf’s negative and adaptive forms. |
| [Podman device bandwidth](../../../profiles/podman-run.json#L4524) and [device I/O rate](../../../profiles/podman-run.json#L4855) both use `PATH:RATE` | Label the rate component `B/s` or `IOPS` (I/O operations per second). | The literal flag `--device-read-bps` still matches a text search for `bps`. Its operand is a **byte** rate. The device path cannot inherit either unit. |
| [OpenSSH scp bandwidth](../../../profiles/scp.json#L735) repeats “1024 bits/second.” [ss connection info](../../../profiles/ss.json#L455) mentions bit rates only in prose. | Show “1 unit = 1,024 bps” for scp. Let `bps` find the ss options explaining output rates. | scp takes an integer without a suffix. ss describes reported output, so the search match must not create an operand hint. |
| [FFmpeg display rotation](../../../profiles/ffmpeg.json#L6913) repeats “degrees.” [PlatformIO monitor](../../../profiles/pio-device-monitor.json#L41) repeats “baud.” | Use `°` with the rotation direction. State “baud” once for the serial signalling rate. | Retain counterclockwise direction. Baud alone does not establish bits per second. |

### Search behavior

- Preserve the existing case-insensitive substring search over flags, original descriptions, and evidence, including queries spanning fields. Add unit aliases as an independent match on the same option. Return each match once in profile order. A change of level, filter, or selected row must not change an option's aliases.
- Make `bps`, `bits/s`, `bit/s`, and “bits per second” find documented bit rates. Cover scaled bit rates, individual forms, composite components, command-wide positional guidance where applicable, and explicit input **or output** units in prose-only help. Resolve shared definitions. Membership belongs to each documented option and scope, independent of whether the unit is visible, grouped, or abbreviated. Recognize explicit unit expressions in operational prose without inferring units from a flag, an arbitrary substring, or a reference URL.
- Proposed for the other surveyed units: index the displayed abbreviation and its unambiguous expanded name per applicable form. Match unit symbols as complete aliases, preserving meaningful case and scale, including `b/s` versus `B/s` and `MB` versus `MiB`. Keep original literal-text matches. When variants disagree, allow discovery of each documented active alternative with its qualification. Exclude inactive declarations from semantic aliases and suppress shared headings for unresolved conflicts.

**Proposed controls and layout for review**

- Open each browser in Simple. Press `D` to cycle Simple → Detailed → Expanded → Simple for the current session. Show the active level and actual configured key. Switching retains the filter, focus, category, and selected option, and starts the new explanation at the top. In the search editor, the same printable key enters a search character.
- Use one blank terminal row between visible option entries when space permits and retain the aligned declaration/summary columns. Terminal cells are the layout unit. Keep categories independently scrollable. At the existing 60-column × 16-row minimum, use the compact layout if the spacer would prevent two options from fitting when two exist. Retain the marker and horizontal gutter in compact mode.
- Keep color optional. As a candidate, use a bold heading and one cyan accent for option names on a suitable theme. Use the terminal’s normal foreground for prose. Selection keeps the `>` marker and reverse video, and focus keeps the `*` marker. Match roles by label, position, and emphasis in monochrome. Decide whether to ship the accent after checking dark and light backgrounds and color-vision simulations.

## Workflow and task chart

Read top to bottom. Each row has a reviewable result. Record an observation or an edit against the phase ID when reviewing.

| Phase | Depends on | Implementation deliverable | AI review evidence | Human review decision |
| --- | --- | --- | --- | --- |
| P0 · Agree on examples | Human review of this draft | Frames for all three levels, a single option’s forms, a mixed list, and a long discovered option | Map each displayed fact to active guidance and record viewport budgets | Review the wording, shortcut, and spacing at actual terminal widths |
| P1 · Build the three text views | P0 | Each level works on existing and partial profiles, with citations excluded | Check operational coverage, source suppression, and legacy search | Read the same option at each level and identify what new information each step adds |
| P2 · Connect levels to controls | P1 | Normal browser and preview support the same level switch | Exercise search, scroll, resize, remapping, insert, and cancel | Find and change the level using the visible controls alone |
| P3 · Group and search units | P1, P2 | Compact units across options and within one option, with searchable abbreviations | Check applicability, conversions, new matches, and legacy match order | Identify a form’s unit and find it by its displayed abbreviation |
| P4 · Allocate space and apply optional color | P2, P3 | Simple returns unused rows to the list, with spacing and visible focus at each size | Check cell positions, page sizes, selection, and monochrome fallback | Compare full screens at 80×24 and 60×16, then inspect theme-specific color captures |
| P5 · Verify the integrated browser | P1–P4 | Terminal evidence, regression results, and updated controls guide | Compare behavior across menu sources and verification targets | Accept the reading experience or reopen a phase with an example |

### P0 · Capture representative screens

- [ ] Capture the current working-tree behavior at 80×24 and 60×16 using the rendered-screen harness. Use FFmpeg `-b:v`/`-b:a` for shared units, `-maxrate`/`-bufsize` for mixed units, an ordinary `ls` flag, and a long option from a fixed discovery fixture. Record command, category, filter, and selected flag so another reviewer can reproduce each observation.
- [ ] Mark the exact repeated phrases to collapse and the guidance to recover in Expanded. Include an inline source URL, an uncertainty notice, and a URL-valued operand among the fixtures. Record any requested change to the mockup directly in this plan before relying on it as a specification.
- [ ] Compare full proposed frames at the same selection for all three levels at 80×24 and for Simple and Expanded at 60×16. Include filter, footer, a complete short row, a clipped declaration, and a single-option Expanded conversion table. Count visible selectable options and occupied detail rows. Use the unit examples above to establish the expected literal inputs, display labels, and search hits before changing the formatter.

### P1 · Produce concise and complete operational text

- [ ] Start in [presentation.py](../../../cli_help/presentation.py) with `OptionText`, `option_text`, and the shared value formatter. The existing `details` already omits examples and release annotations. The case-folded `searchable` includes evidence and loses display formatting. Build the three views from the original summary, detail, and active value guidance. Retain the current search construction and ordering. Reuse validated per-open value text.
- [ ] Prioritize purpose in Simple and one or two actionable facts in Detailed. For empty or placeholder summaries such as “Documented option,” use the first usable operational sentence, then documented syntax. If neither explains the selection, show “Description unavailable.” Expanded retains attached or optional operands, scoped alternatives, special values, meaningful version differences, and original usage examples. In merged discovery text, keep a conflict warning adjacent to the differing claims and identify each as an alternative.
- [ ] Exclude citations in the always-visible profile header, category fallback on an empty search, option summaries, and the selected pane. Test standalone and inline references, a delegated grammar with its name and citation on the same line, and an actual URL operand in a usage example. Preserve the grammar name, operational qualifications, literal operands, and the user's typed filter. Check normal browsing and preview across all levels and every Expanded page. Retain cell-safe sanitization throughout.
- [ ] Extend [description tests](../../../tests/test_presentation_descriptions.py) and [numerical tests](../../../tests/test_numerical_presentation.py). Check that a unique fact available only in Expanded survives, a known citation is absent from every rendered level, a literal URL operand remains usable, and all legacy matches retain their relative order. P3 separately checks the additional results for applicable unit aliases. Include missing and malformed metadata, multi-component values, and unknown applicability.

### P2 · Switch levels in place

- [ ] Extend `Browser`, `draw`, and `run_browser` in [ui.py](../../../cli_help/ui.py). Carry the level per browser open, reset the detail offset on a level change, and reuse the existing detail scroll actions. Display the level and switch affordance within the minimum width. In preview, Enter retains its existing inspect action.
- [ ] Add a `cycle_detail` action to `DEFAULT_KEYS` and the [example key configuration](../../../config/keys.example.json). Proposed fallback order for an omitted action is `D`, `V`, then F6. Add F6 to named keys and the curses stub. Old configurations cannot already assign a named F6. Test remaps consuming the first one and first two choices. If a new config claims all three, request an explicit cycle binding in the key diagnostic. Continue diagnosing explicit duplicate assignments. Show the effective hint at 60 columns.
- [ ] In the existing scripted browser tests, cycle through all levels and back, scroll Expanded to its final line, filter on hidden text, type `D` inside a query, cancel the query, and reopen the browser. Check selection identity, the expected filter, focus, and the correct insert/inspect behavior. Cover an empty result and a resize while scrolled.
- [ ] Exercise two distinct transitions. Cycling preserves the current selection. Escape in the search editor restores the saved query using the existing category/selection behavior.

### P3 · Group repeated units and make them searchable

- [ ] Reuse validated active value semantics for grouping. Compare the bare-number form, physical unit and scale, denominator, subject, applicable target, and review status. Include a ratio’s reference quantity and a custom unit’s name and definition. Check option-level conflicts even when the active metadata is verified. Exercise differing ratio bases, custom definitions, target variants, and merged-source conflicts. Preserve local guidance wherever a common statement would mislead.
- [ ] Anchor the note above the entries it describes. Scope it to an explicitly named group, or to the whole filtered category when every entry qualifies. Keep the note visible for as long as the dependent rows use it. Recompute its scope after filtering or changing categories. When a note cannot fit or only one row qualifies, show the unit locally. Preserve the profile order.
- [ ] Test the examples above, bits versus bytes, SI versus binary multipliers, two target-specific variants, and an option without unit metadata. Verify that filtering from a homogeneous group to a mixed group restores the local labels. Check that Expanded can still explain suffix effects and exceptions without reprinting the general unit sentence for each form.
- [ ] Within Expanded, group compatible forms under one local result-unit heading. Keep the literal spelling, multiplier, case, range, exceptions, and target visible with the affected form. Repeat or restore the heading when scrolling or wrapping would separate values from their meaning. Verify FFmpeg’s suffixes both in a mixed list and as the only result. Repeat the check on Go durations, rsync transfer rates, and esptool clocks using the inventory above.
- [ ] Implement the additive matches described in **Search behavior** across bundled, discovered, custom, and preview profiles. Test `bps` on FFmpeg rates, scp’s scaled rate, ss output prose, a composite bit-rate component, and a scoped shared definition. Check aliases with the list filtered down to one entry, cleared, and in every detail level. A buffer size in bits, a frequency, or a byte-rate operand acquires no bit-rate alias. Preserve literal matches such as Podman’s `--device-read-bps`. Test byte, duration, clock, frame-rate, and percent aliases using the same fixtures as the display checks.

### P4 · Space rows and verify visual roles

- [ ] In `draw`, allocate chrome and actual detail content before distributing the available rows. In Simple, return the entire unused detail budget to the option list. Recalculate on selection, search, resize, and level changes. For a long category at 80×24 and 60×16, assert that a complete short selection has no empty detail pane, the list fills the recovered area, and switching back from Expanded restores capacity. For a clipped flag or warning, verify its recovery consumes only the rows it needs within a budget that keeps the selected option visible. Insert spacers only between entries. Page movement uses the focused pane’s actual selectable capacity.
- [ ] Use the existing cell-width, clipping, and wrapping helpers. Keep long declarations recoverable in the selected pane. Check 120×40, 80×24, 60×16, and below minimum. Check empty results, the last partial page, wide and combining characters, and shrink/grow while the last entry is selected. Spacers must never receive focus.
- [ ] Apply curses attributes by role. Use optional color only when initialization and available pairs support it. Honor a nonempty `NO_COLOR`; exercise monochrome, failed pair initialization, and the [curses test stub](../../../tests/curses_stub.py). Preserve selection contrast when the accent and reverse video interact.
- [ ] Use plain tmux cell captures for positioning and markers. Inspect color-preserving captures from identified light and dark themes, then grayscale and protanopia, deuteranopia, and tritanopia simulations. Record theme, size, and observations for headings, flags, focus, selection, and review notices. If the accent obscures a role on a tested theme, adjust or omit it.

### P5 · Verify end to end and update the guide

- [ ] Add tier transitions to [rendered-screen tests](../../../tests/test_terminal_screen.py) and [native numerical terminal tests](../../../tests/test_native_numerical_terminal.py). Migrate existing assertions about long default Details to the appropriate level and retain their original coverage. Scroll through Expanded and inspect rendered cells for a known source URL and its locator, including wrapped or split fragments.
- [ ] Verify bundled FFmpeg and a small ordinary profile, fixed discovered help, a legacy custom profile, and authoring preview. From the actual Bash shortcut, check literal mid-line insertion, cursor position, cancellation, and terminal restoration. Check search by a hidden qualification and confirm the full operational context remains reachable without changing the filter.
- [ ] Update the [numerical coverage checker](../../../scripts/check_numerical_coverage.py#L178) and [omission tests](../../../tests/test_numerical_coverage.py#L433) to test what users can reach in Expanded, in command-wide positional guidance, or in a visible shared note. Deliberately remove a unit, scope, and positional rule in separate tests and confirm each fails even if old internal text still contains it. Keep an independent check for searchable provenance and legacy cross-field matches.
- [ ] Follow the [sandbox verification procedure](../../development.md#isolated-local-debugging). During iteration run the focused presentation and terminal modules. For final integration run the following offline suites and record failures or skips by target.

  ```sh
  python3 -I tests/run_sandbox.py --target host
  python3 -I tests/run_sandbox.py --target noble310
  python3 -I tests/run_sandbox.py --target noble312
  ```

- [ ] Compare FFmpeg open time and redraw responsiveness against the same working baseline, with a small-menu control. Adapt the [paired timing tool](../../../tools/menu_benchmark/terminal.py#L215) to use each revision’s own expected screens for equivalent open, filter, and select actions. Adapt the [parity recorder](../../../tools/menu_benchmark/parity.py#L51) to observe the active viewport instead of fixed detail rows. Independently verify the new frames against the reviewed layouts. Require parity for insertion, cancellation, and legacy matches, with additional matches explicitly expected for eligible unit aliases. Use the existing [measurement procedure](../../ffmpeg-menu-performance-plan.md#before-and-after-measurement).
- [ ] Update the [controls guide](../../usage.md#browser-controls), affected numerical-presentation guidance, and the [roadmap](../../../ROADMAP.md) with the actual binding, layout behavior, verification results, and remaining findings. Review existing media for misleading instructions and identify affected frames before replacing any.

## Implementation record

| Phase | Delivered result |
| --- | --- |
| P0 | The six mockups were reviewed before implementation. |
| P1 | Simple, Detailed and Expanded use the same selected option. Expanded retains operational examples and target-specific values. Terminal views suppress citation URLs. |
| P2 | The configurable `cycle_detail` action defaults to `D` and works in the browser and authoring preview. |
| P3 | A shared note identifies options with the same verified bare unit. Expanded preserves literal suffixes. Search indexes active definitions, components, positional values and explicit units in prose. |
| P4 | Simple reclaims detail space. Compact category names fit the minimum sidebar across the bundled profiles. Original titles appear above the menu and oversized titles can be read in the scrollable pane. |
| P5 | The [terminal verification record](2026-11-24-menu-detail-levels-verification.md) contains the six real screens, viewport counts, color checks and paired timings. The [controls guide](../../usage.md#browser-controls) describes operation. |

## Review record

Edit the proposed choices in place or add a finding below. Use the phase ID, a concrete option and terminal size, the observed text or behavior, and the expected change. Record evidence before marking an implementation task complete.

| Reviewer | Phase and example | Decision or requested edit | Evidence or follow-up |
| --- | --- | --- | --- |
| User decisions | P3, P4 | Reclaim unused Simple detail rows. Make `bps` searchable wherever it applies. | Incorporated in the layout, unit vocabulary, search contract, and acceptance checks. |
| AI agent | P0–P5 · coverage and feasibility | Original findings incorporated into this revision. | [Review of the earlier draft](2026-11-24-menu-detail-levels-review.md) |
| Human | Revised plan | Pending. Implementation is on hold. | Review full-screen allocation, abbreviations, literal-input examples, shortcut fallback, and optional color. |
