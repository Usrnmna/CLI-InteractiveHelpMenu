"""Curses browser with independently scrollable categories, options, and details."""

import curses
from dataclasses import dataclass, field
import math
import os
import re
from pathlib import Path
import time
import unicodedata

from core import HelpError, read_json
from menu_units import PROSE_ALIAS_QUERIES, search_alias
from presentation import option_label, option_text, terminal_prose, value_text
from terminal_text import strip_terminal_sequences


DEFAULT_KEYS = {
    "up": ["up", "k"], "down": ["down", "j"],
    "page_up": ["pageup"], "page_down": ["pagedown"],
    "first": ["home"], "last": ["end"],
    "previous_category": ["left", "h"], "next_category": ["right", "l"],
    "focus": ["tab"], "accept": ["enter"], "cancel": ["esc", "ctrl-c", "q"],
    "search": ["/"], "clear_search": ["ctrl-u"],
    "detail_up": ["["], "detail_down": ["]"], "detail_page": ["space"], "cycle_detail": ["D"],
    "toggle_summary_scroll": ["m"],
}

NAMED_KEYS = {
    "up": curses.KEY_UP, "down": curses.KEY_DOWN,
    "left": curses.KEY_LEFT, "right": curses.KEY_RIGHT,
    "pageup": curses.KEY_PPAGE, "pagedown": curses.KEY_NPAGE,
    "home": curses.KEY_HOME, "end": curses.KEY_END,
    "space": " ", "f6": curses.KEY_F6, "tab": "\t", "enter": "\n", "esc": "\x1b",
    "ctrl-c": "\x03", "ctrl-u": "\x15",
}


def load_keys(path: Path | None = None) -> dict:
    """Merge optional action bindings and reject ambiguous or unusable controls."""
    bindings = {action: list(keys) for action, keys in DEFAULT_KEYS.items()}
    if path:
        document = read_json(path)
        if not isinstance(document, dict) or set(document) != {"keys"} or not isinstance(document["keys"], dict):
            raise HelpError("The key configuration requires a single 'keys' object.")
        for action, keys in document["keys"].items():
            if action not in bindings:
                raise HelpError(f"Unknown key action: {action}")
            bindings[action] = keys
        # Preserve older bindings that already assign m to another action.
        if "toggle_summary_scroll" not in document["keys"] and any(
                isinstance(values, list) and "m" in values for values in document["keys"].values()):
            del bindings["toggle_summary_scroll"]
        if "cycle_detail" not in document["keys"]:
            occupied = {key for action, values in bindings.items() if action != "cycle_detail"
                        and isinstance(values, list) for key in values if isinstance(key, str)}
            fallback = next((key for key in ("D", "V", "f6") if key not in occupied), None)
            if not fallback:
                raise HelpError("Configure a free key for cycle_detail (D, V and F6 are occupied).")
            bindings["cycle_detail"] = [fallback]
        if "detail_page" not in document["keys"]:
            occupied = {NAMED_KEYS.get(k, k) for action, values in bindings.items() if action != "detail_page"
                        and isinstance(values, list) for k in values if isinstance(k, str)}
            for candidate in ("space", "P", "f6"):
                if NAMED_KEYS.get(candidate, candidate) not in occupied:
                    bindings["detail_page"] = [candidate]
                    break
            else:
                # Older configurations can already own every suggested key.
                del bindings["detail_page"]
    used = set()
    for action, keys in bindings.items():
        if not isinstance(keys, list) or not keys:
            raise HelpError(f"{action} requires at least one key.")
        for key in keys:
            if not isinstance(key, str) or not (key in NAMED_KEYS or len(key) == 1 and key.isprintable()):
                raise HelpError(f"Unsupported key name: {key!r}")
            value = NAMED_KEYS.get(key, key)
            if value in ("\x1b", "\x03") and action != "cancel":
                raise HelpError("Esc and Ctrl-C are reserved for cancellation.")
            if value in used:
                raise HelpError(f"A key is assigned to more than one action: {key}")
            used.add(value)
    return bindings


@dataclass
class Browser:
    """Maintain navigation state independently of terminal drawing."""

    profile: dict
    query: str = ""
    category: int = 0
    selected: int = 0
    detail_offset: int = 0
    focus: str = "options"
    level: str = "Simple"
    accent: int = 0
    section_color: int = 0
    key_color: int = 0
    guided: bool = False
    scroll_summaries: bool = True
    summary_field: tuple | None = field(default=None, init=False, repr=False)
    compact_page: str | None = None
    next_detail_offset: int = field(default=0, init=False)
    _text: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # A modal browser holds one read-only profile. Reopening, including a
        # preview after editing, derives fresh text; nothing is persisted.
        positional = value_text(self.profile, self.profile, positional=True)
        shared_values = {}
        for category in self.profile["categories"]:
            for option in category["options"]:
                self._text[id(option)] = option_text(self.profile, category, option, positional=positional,
                                                     shared_values=shared_values)
        for index in range(len(self.profile["categories"])):
            if self.options(index):
                self.category = index
                break

    def options(self, category=None):
        """Match the existing case-insensitive substring query against display text."""
        category = self.category if category is None else category
        query = self.query.casefold()
        rows = self.profile["categories"][category]["options"]
        if not query:
            return rows.copy()
        alias = search_alias(self.query)
        scan_prose = alias in PROSE_ALIAS_QUERIES
        matches = []
        for option in rows:
            view = self.text(option)
            if query in view.searchable or alias in view.aliases or (scan_prose and alias in view.prose_units):
                matches.append(option)
        return matches

    def text(self, option):
        """Return the same derived explanation used by list, details and search."""
        return self._text[id(option)]

    def visible_summary(self, option, text, row, column, width, focused):
        """Register the exact on-screen summary field only when enabled and truncated."""
        visible = ellipsize_cells(text, width)
        if focused and self.scroll_summaries:
            clean = display_text(text)
            if visible != clean:
                self.summary_field = (id(option), row, column, width, clean)
        return visible

    def move_category(self, amount):
        self.category = max(0, min(len(self.profile["categories"]) - 1, self.category + amount))
        self.selected = self.detail_offset = 0

    def move_option(self, amount):
        self.selected = max(0, min(max(0, len(self.options()) - 1), self.selected + amount))
        self.detail_offset = 0

    def set_query(self, query):
        self.query = query
        self.selected = self.detail_offset = 0
        if not self.options():
            for index in range(len(self.profile["categories"])):
                if self.options(index):
                    self.category = index
                    break


def display_text(value: str) -> str:
    """Strip terminal sequences before suppressing other controls and surrogates."""
    return "".join(char if char.isprintable() else " " for char in strip_terminal_sequences(value))


def cell_width(character):
    """Measure ordinary Unicode cells; ambiguous-width and emoji clusters remain terminal-dependent."""
    if unicodedata.category(character) in {"Mn", "Me"}:
        return 0
    return 2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1


def clip_cells(text, width):
    """Keep complete base/combining characters inside a cell budget."""
    result, used = [], 0
    for char in display_text(text):
        size = cell_width(char)
        if used + size > width:
            break
        if size or result:
            result.append(char)
            used += size
    return "".join(result)


def ellipsize_cells(text, width):
    """Make clipping explicit; full declarations and explanations remain in details."""
    text = display_text(text)
    if sum(cell_width(char) for char in text) <= width:
        return text
    return clip_cells(text, max(0, width - 1)) + ("…" if width > 0 else "")


def summary_windows(text, width):
    """Yield successive clipped views, keeping combining marks with each base character."""
    text = display_text(text)
    remaining = sum(map(cell_width, text))
    start = 0
    while remaining > width - 1 and start < len(text):
        remaining -= cell_width(text[start])
        start += 1
        while start < len(text) and not cell_width(text[start]):
            start += 1
        if remaining <= width - 1:
            yield "…" + text[start:], True
            return
        yield "…" + clip_cells(text[start:], width - 2) + "…", False


class SummaryScroll:
    """Schedule one horizontal pass for the active field and repaint only its cells."""

    def __init__(self):
        self.target = None
        self.deadline = None
        self.frames = None
        self.visible = ""

    def select(self, target, now):
        """Restart after a changed selection or layout, measured from its opening frame."""
        if target == self.target:
            return
        self.target = target
        self.visible = ""
        self.deadline = None
        self.frames = None
        if target:
            _, _, _, width, text = target
            self.frames = summary_windows(text, width)
            self.deadline = now + 2.0

    def paint(self, screen):
        """Restore the visible slice after a full draw or paint a single timed step."""
        _, row, column, width, _ = self.target
        padding = width - sum(map(cell_width, self.visible))
        write(screen, row, column, self.visible + " " * padding, width, curses.A_REVERSE)

    def tick(self, screen, now):
        """Advance a due frame once and stop polling the animation after the last slice."""
        if self.deadline is not None and now >= self.deadline:
            self.visible, finished = next(self.frames)
            self.paint(screen)
            screen.refresh()
            self.deadline = None if finished else now + 0.25


def wrap_cells(text, width):
    """Wrap normalized paragraphs by terminal cells, splitting long words safely."""
    lines, current, used = [], [], 0
    for char in display_text(text).expandtabs():
        size = cell_width(char)
        if used + size > width:
            split = max((index for index, value in enumerate(current) if value.isspace()), default=-1)
            if split >= 0:
                lines.append("".join(current[:split]).rstrip())
                current = current[split + 1:]
            else:
                lines.append("".join(current))
                current = []
            used = sum(cell_width(value) for value in current)
        if (current or not char.isspace()) and (size or current):
            current.append(char)
            used += size
    if current:
        lines.append("".join(current).rstrip())
    return lines or [""]


def escape_delay():
    """Validate an explicit slow-terminal override while retaining the 40 ms default."""
    try:
        delay = int(os.environ.get("CLI_HELP_ESCAPE_DELAY", "40"))
    except ValueError:
        raise HelpError("CLI_HELP_ESCAPE_DELAY requires 20-1000 milliseconds.", "invalid_escape_delay") from None
    if not 20 <= delay <= 1000:
        raise HelpError("CLI_HELP_ESCAPE_DELAY requires 20-1000 milliseconds.", "invalid_escape_delay")
    return delay


def write(screen, row, column, text, width, attribute=0):
    """Clip text and tolerate resize races and wide characters at terminal edges."""
    try:
        clipped = clip_cells(text, max(0, width))
        screen.addnstr(row, column, clipped, len(clipped), attribute)
    except curses.error:
        pass


def option_label_width(category, budget):
    """Reserve a stable declaration column and at least half the row for prose.

    Measure the whole category so scrolling and filtering cannot shift columns.
    The marker and two-cell gap use four cells outside the declaration budget.
    """
    longest = max(sum(cell_width(c) for c in display_text(option_label(option)))
                  for option in category["options"])
    return min(longest, 40, (budget - 4) // 2, max(12, budget * 2 // 5))


# Sidebar names for bundled headings that lose their distinguishing words at 60 columns.
# The full profile name remains the category identity and is always available above the list.
_SHORT_CATEGORIES = {
    "Files and selection": "File selection", "Help and components": "Help & parts",
    "Formats and mapping": "Formats & maps", "Seeking and timestamps": "Seek & time",
    "Input rate and output limits": "Rates & limits", "Filters and bitstreams": "Stream filters",
    "Video and frame timing": "Frame timing", "Audio and subtitles": "Audio & subs",
    "Encoding and hardware": "Encoding & HW", "Progress and diagnostics": "Progress & logs",
    "Alternate spellings": "Aliases", "Inverse switches": "Inverse flags",
    "Codec parameters": "Codec settings", "Container and I/O parameters": "Container I/O",
    "Audio codec options": "Audio codecs", "Subtitle and other codec options": "Other codecs",
    "Container-specific options": "Containers", "Capture and output devices": "Capture/output",
    "Shared component options": "Shared options", "Optional media formats": "Extra formats",
    "Windows capture devices": "Windows capture", "DeckLink capture and playback": "DeckLink",
    "Apple and Android devices": "Mobile devices", "Additional protocol options": "More protocols",
    "Archive and member selection": "Archive members", "Archive input and decoded data": "Archive input",
    "Build inputs and stages": "Build stages", "Build mounts and networking": "Mounts & net",
    "Cache and registries": "Cache/registry", "Certificate checking": "Cert checks",
    "Certificate output": "Cert output", "Certificate printing": "Cert printing",
    "Certificate trust output": "Trust output", "Console and resource controls": "Console/limits",
    "Existing files and output paths": "Files & paths", "Expression permissions": "Expr access",
    "Extended certificate": "Cert details", "Extraction and replacement": "Extract/replace",
    "Filesystems and devices": "FS & devices", "Formatting and decoration": "Display format",
    "Image metadata and output": "Image output", "Images and registries": "Images/registry",
    "Input and integration": "Input & setup", "Links, ownership and stream names": "Links & owners",
    "Networking and namespaces": "Net/namespaces", "Ownership and timestamps": "Owners & times",
    "Process and lifecycle": "Process cycle", "Resource limits and namespaces": "Limits & scopes",
    "Selection and patterns": "Select/patterns", "Software bills of materials": "SBOM",
    "Additional reflogs and paths": "Reflogs & paths", "Ancestry and ordering": "Ancestry/order",
    "Environment and metadata": "Env & metadata", "Filtering and ordering": "Filter/order",
    "Matching and sorting": "Match & sort", "Optional codec builds A–M": "Extra codecs A–M",
    "Optional codec builds N–Z": "Extra codecs N–Z", "Merge comparisons": "Merge diffs",
    "Container selection": "Container", "Protocol and version": "Protocol/ver.",
    "Change summaries": "Change summary", "Change detection": "Detect changes",
    "Comparison rules": "Compare rules", "Borders and labels": "Borders/labels",
    "Prompt and headers": "Prompt/headers", "Digest selectors": "Digest types",
    "Queries and output": "Queries/output", "Users and security": "Users/security",
    "Contents and usage": "Contents/usage",
    "Actions and history": "Actions/history", "Test binary flags": "Test args",
    "Runtime and security": "Runtime/secure",
}


def category_label(name, budget):
    """Keep short names intact, then prefer a meaningful alias before cell-safe clipping."""
    if sum(map(cell_width, name)) <= budget:
        return name
    short = _SHORT_CATEGORIES.get(name, name)
    short = short.replace(" and ", " & ").replace(" options", "").replace("Additional command", "More flags")
    short = short.replace("Video codecs ", "V. codecs ").replace("Extra codecs ", "Extra codec ")
    return ellipsize_cells(short.strip() or name, budget)


LEVELS = ("Simple", "Detailed", "Expanded")


def menu_colors():
    """Choose distinct readable pairs for declarations, headings and keyboard hints.

    A reported terminal background keeps its native appearance. With no reliable
    report, give only the accented text an explicit background for contrast.
    """
    plain = (0, 0, 0)
    if os.environ.get("NO_COLOR"):
        return plain
    try:
        if not curses.has_colors() or curses.COLORS < 8:
            return plain
        report = os.environ.get("COLORFGBG", "").rsplit(";", 1)[-1]
        background = curses.COLOR_BLACK
        pair_background = background
        try:
            curses.use_default_colors()
        except curses.error:
            pass  # Explicit pairs remain usable on terminals without default colors.
        else:
            if report.isascii() and report.isdigit() and len(report) <= 3 and int(report) < curses.COLORS:
                background = int(report)
                pair_background = -1

        def luminance(index):
            """Convert the reported RGB channels to relative luminance."""
            rgb = [channel / 1000 for channel in curses.color_content(index)]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
            return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

        bg = luminance(background)
        # Each role takes the next unused color that meets text contrast.
        candidates = (curses.COLOR_CYAN, curses.COLOR_YELLOW, curses.COLOR_GREEN,
                      curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_RED,
                      curses.COLOR_WHITE, curses.COLOR_BLACK)
        styles = []
        for candidate in candidates:
            fg = luminance(candidate)
            if (max(bg, fg) + 0.05) / (min(bg, fg) + 0.05) < 4.5:
                continue
            pair = len(styles) + 1
            if pair >= curses.COLOR_PAIRS:
                break
            curses.init_pair(pair, candidate, pair_background)
            styles.append(curses.color_pair(pair))
            if len(styles) == 3:
                break
        return tuple(styles) + plain[len(styles):]
    except (AttributeError, ValueError, curses.error):
        return plain


def key_label(keys, action):
    """Use terminal glyphs for named arrows and preserve custom key spellings."""
    key = keys[action][0]
    return {"up": "↑", "down": "↓", "left": "←", "right": "→", "space": "Space", " ": "Space"}.get(key, key)


def key_pair(keys, first, second):
    """Join a familiar glyph pair, or separate custom bindings for legibility."""
    a, b = key_label(keys, first), key_label(keys, second)
    return a + b if (a, b) in {("↑", "↓"), ("←", "→"), ("[", "]")} else a + "/" + b


def detail_page_hint(browser, keys):
    """Offer one page action, or the configured line controls for legacy bindings."""
    if "detail_page" in keys:
        return key_label(keys, "detail_page"), "next" if browser.next_detail_offset else "top"
    return key_pair(keys, "detail_up", "detail_down"), "scroll"


def draw_controls(screen, row, width, browser, keys, searching, preview, scrolling):
    """Fit whole key hints by priority, leaving a gutter between neighboring actions."""
    if searching:
        hints = [("enter", "apply"), ("esc", "restore")]
    else:
        accept = "open" if browser.focus == "categories" else "inspect" if preview else "insert"
        hints = [(key_pair(keys, "up", "down"), "move"), (keys["accept"][0], accept),
                 (keys["cancel"][0], "cancel")]
        if scrolling:
            hints.append(detail_page_hint(browser, keys))
        hints.extend([(key_pair(keys, "previous_category", "next_category"), "category"),
                      (keys["search"][0], "search"), (keys["focus"][0], "focus")])
    draw_hints(screen, row, width, hints, browser.key_color)


def draw_hints(screen, row, width, hints, color):
    """Draw complete shortcuts with bold keycaps and three-cell gutters."""
    x = 0
    for key, action in hints:
        label = (key + " " + action).rstrip()
        size = sum(map(cell_width, label))
        if x + size <= width:
            write(screen, row, x, label, size)
            write(screen, row, x, key, size, curses.A_BOLD | color)
            x += size + 3


def shared_note(browser, options, budget):
    """Name the selected option's verified unit group only if the full scope fits."""
    key = browser.text(options[browser.selected]).group
    if not key or len(options) < 2:
        return "", ()
    members = [option["flag"] for option in options if browser.text(option).group == key]
    if len(members) < 2:
        return "", ()
    unit = "bits/second (bps)" if key[0] == "bps" else key[0]
    subject = "/".join(members) + ": bare N in " if len(members) < len(options) else "Bare values in "
    note = subject + unit
    return (note, key) if sum(map(cell_width, note)) <= budget else ("", ())


def row_summary(view, group):
    """Remove only the explicit unit that is already visible above this row."""
    summary = view.summary
    if group and view.group == group:
        suffix = re.escape(group[0])
        equivalents = {"bps": r"bits?/(?:s|sec(?:ond)?s?)|bits? per second",
                       "B/s": r"bytes?/(?:s|second)|bytes? per second",
                       "s": "seconds?", "ms": "milliseconds?", "µs": "microseconds?",
                       "ns": "nanoseconds?", "min": "minutes?", "h": "hours?",
                       "Hz": "hertz", "MHz": "megahertz", "fps": "frames per second", "°": "degrees?"}
        if group[0] in equivalents:
            suffix += "|" + equivalents[group[0]]
        unit = "(?:" + suffix + ")"
        # Remove only a complete trailing unit clause. Keep examples and qualifiers intact.
        summary = re.sub(rf"\s+(?:\((?:(?:bare (?:rate|values?) )?in )?{unit}\)|(?:measured )?in {unit})[.]?$",
                         "", summary) or summary
        summary = re.sub(r"^Set the target (.* bitrate)$", r"Set \1", summary)
    elif view.group:
        unit = view.group[0]
        if (unit not in summary.split() and not re.search(r"\b(?:bits?|bytes?|seconds?|degrees?|baud|percent|rows|columns|hertz)\b", summary, re.I)
                and unit not in summary.strip("().").split()):
            summary += " (" + unit + ")"
    return (view.notice + " " if view.notice else "") + summary


@dataclass
class DetailRow:
    """Visible text plus cell-positioned emphasis, shared by color and monochrome."""
    text: str = ""
    highlights: list = field(default_factory=list)
    bitrate: bool = False


@dataclass
class DetailEntry:
    """A list entry with its literal, unstyled explanation and scoped notes."""
    prefix: str
    literal: str
    explanation: str
    kind: str
    notes: list = field(default_factory=list)


def detail_entry(line, bitrate, value_list):
    """Recognize the formatter's list rows and explicitly separated option declarations."""
    if bitrate:
        match = re.fullmatch(r"(.+?)\s{2,}(N(?: × [\d,.]+)?)", line)
        if match:
            return DetailEntry("", match[1], line[len(match[1]):], "conversion")
    if line.startswith("Input ") and (" · " in line or re.fullmatch(r"Input [A-Z][A-Z_0-9|\[\].+-]*", line)):
        name, separator, explanation = line[6:].partition(" · ")
        return DetailEntry("Input ", name, separator + explanation, "value")
    if line.startswith("Special input ") and ": " in line:
        name, separator, explanation = line[14:].partition(": ")
        literal, comma, qualification = name.partition(", ")
        return DetailEntry("Special input ", literal, comma + qualification + separator + explanation, "special")
    if value_list:
        match = re.fullmatch(r"([^\s:]+)(: |\s{2,})(.+)", line)
        if match:
            return DetailEntry("", match[1], match[2] + match[3], "literal")
    match = re.fullmatch(r"(-{1,2}[\w][\w.=-]*(?: [A-Z][A-Z_0-9]*)?)(\s{2,}|: )(.+)", line)
    if match:
        return DetailEntry("", match[1], match[2] + match[3], "option")
    return None


def wrapped_entry(entry, width, accent):
    """Wrap one entry within its column and emphasize only the literal's cells."""
    text = entry.prefix + entry.literal + entry.explanation
    literal_start = len(entry.prefix)
    literal_end = literal_start + len(entry.literal)
    style = curses.A_BOLD | accent if entry.kind == "option" else curses.A_UNDERLINE
    rows = []
    offset = 0
    for line in wrap_cells(text, width):
        start = text.index(line, offset)
        offset = start + len(line)
        first, last = max(start, literal_start), min(offset, literal_end)
        highlights = []
        if first < last:
            highlights.append((sum(map(cell_width, text[start:first])), text[first:last], style))
        rows.append(DetailRow(line, highlights, entry.kind == "conversion"))
    for note in entry.notes:
        rows.extend(DetailRow("  " + part) for part in wrap_cells(note, width - 2))
    return rows


def list_rows(entries, width, accent):
    """Choose the widest useful column count and balance contiguous whole entries by height."""
    gutter = 3
    # Use at least three entries per column and leave room for a short explanation.
    for count in range(min(3, max(1, len(entries) // 3)), 0, -1):
        stride = (width + gutter) // count
        column_width = stride - gutter
        if count > 1 and column_width < 30:
            continue
        blocks = [wrapped_entry(entry, column_width, accent) for entry in entries]
        height = sum(map(len, blocks))
        if count == 1:
            return [row for block in blocks for row in block]
        # Allow occasional wrapping. Extra lines beyond half the entry count cost too much height.
        if height - len(entries) > max(2, len(entries) // 2):
            continue
        columns = []
        index = 0
        for remaining in range(count, 0, -1):
            column = []
            target = height / remaining
            while index < len(entries) - remaining + 1:
                block = blocks[index]
                if remaining > 1 and column and abs(len(column) - target) <= abs(len(column) + len(block) - target):
                    break
                column.extend(block)
                index += 1
            columns.append(column)
            height -= len(column)
        rows = [DetailRow() for _ in range(max(map(len, columns)))]
        for col, column in enumerate(columns):
            for row, cell in zip(rows, column):
                start = stride * col
                row.text += " " * (start - sum(map(cell_width, row.text))) + cell.text
                row.highlights.extend((start + x, word, attr) for x, word, attr in cell.highlights)
                row.bitrate |= cell.bitrate
        return rows


def layout_details(lines, width, accent):
    """Flow adjacent entries as a list. Full-width headings and prose delimit each list."""
    rows = []
    index = 0
    bitrate = value_list = False
    while index < len(lines):
        line = display_text(lines[index])
        entry = detail_entry(line, bitrate, value_list)
        index += 1
        if entry is None:
            bitrate = line == "Input             Result (bps)"
            value_list = line.casefold() in {"values:", "accepted values:", "accepted suffixes:", "choices:"}
            heading = re.match(r"^(?:Value(?: variant \d+)?(?: \([^)]+\))?|Component [^:]+):", line)
            for part in wrap_cells(line, width):
                highlights = []
                if bitrate or line.endswith(":"):
                    highlights.append((0, part, curses.A_BOLD))
                elif heading and part.startswith(heading[0]):
                    highlights.append((0, heading[0], curses.A_BOLD))
                rows.append(DetailRow(part, highlights))
            continue
        entries = [entry]
        while index < len(lines):
            following = detail_entry(display_text(lines[index]), bitrate, value_list)
            if not following or following.kind != entry.kind:
                break
            entries.append(following)
            index += 1
        # Single-form qualifications belong to that literal, including when a column breaks.
        # Keep shared qualifications spanning several forms below the complete list.
        if entry.kind in {"value", "conversion"}:
            names = {}
            for item in entries:
                # Repeated spellings can have different descriptions. A shared note stays full-width.
                names[item.literal] = None if item.literal in names else item
            shared = []
            while index < len(lines):
                note_line = display_text(lines[index])
                name, separator, _ = note_line.partition(": ")
                if not separator:
                    break
                if names.get(name) is not None:
                    names[name].notes.append(note_line)
                elif name in names or (", " in name and all(word in names for word in name.split(", "))):
                    shared.append(lines[index])
                else:
                    break
                index += 1
            rows.extend(list_rows(entries, width, accent))
            rows.extend(DetailRow(part) for note in shared for part in wrap_cells(note, width))
        else:
            rows.extend(list_rows(entries, width, accent))
        bitrate = value_list = False
    return rows


def draw_title(screen, browser, keys, preview, width):
    """Show the command and the effective level binding within the available cells."""
    key = key_label(keys, "cycle_detail")
    if len(key) == 1 and "A" <= key <= "Z":
        key = "Shift+" + key
    hint = browser.level + "   " + key + " change view"
    hint_width = sum(map(cell_width, hint))
    title = ("Help preview | " if preview else "Interactive help | ") + " ".join(browser.profile["command"])
    title_width = width - hint_width - 1
    write(screen, 0, 0, ellipsize_cells(title, title_width), title_width, curses.A_BOLD | browser.section_color)
    write(screen, 0, width - hint_width, hint, hint_width, curses.A_BOLD)


def level_guidance(view, level):
    """Read the selected explanation lazily in both layouts."""
    if level == "Expanded":
        return view.expanded
    if level == "Detailed":
        return view.detailed
    return ()


def draw_compact(screen, browser, keys, searching, preview):
    """Show one step of category selection, option selection or reading below 80 columns."""
    height, width = screen.getmaxyx()
    width -= 1
    page = browser.compact_page
    categories = browser.profile["categories"]
    category = categories[browser.category]
    options = browser.options()
    selected = options[browser.selected] if options else None
    draw_title(screen, browser, keys, preview, width)
    context = "" if page == "categories" else "  ·  " + category["name"]
    heading = page.capitalize() + context
    if searching:
        heading = "Search: " + browser.query
    elif browser.query and page == "options":
        heading = "Options  ·  Filter: " + browser.query
    position = ""
    if page != "details" and not searching:
        total = len(categories) if page == "categories" else len(options)
        index = browser.category if page == "categories" else browser.selected
        position = f"{index + 1 if total else 0}/{total}"
        write(screen, 1, width - len(position), position, len(position))
    heading_width = width - len(position) - 2 if position else width
    write(screen, 1, 0, ellipsize_cells(heading, heading_width), heading_width, curses.A_BOLD | browser.section_color)
    write(screen, 2, 0, "━" * width, width)
    start, stop = 4, height - 3  # Keep a blank row inside each horizontal boundary.
    capacity = (stop - start + 1) // 2
    key = lambda action: keys[action][0]
    back = key_label(keys, "previous_category")
    forward = key_label(keys, "next_category")
    move = key_pair(keys, "up", "down")
    accept = "inspect" if preview else "insert"
    if page == "details":
        heading = option_label(selected) if selected else category["name"]
        write(screen, start - 1, 0, ellipsize_cells(heading, width), width, curses.A_BOLD | browser.accent)
        if selected:
            view = browser.text(selected)
            paragraphs = list(level_guidance(view, browser.level))
            if not paragraphs:
                paragraphs = [view.summary]
            elif view.summary not in paragraphs:
                paragraphs = [view.summary, "", *paragraphs]
            if ellipsize_cells(heading, width) != heading:
                paragraphs.insert(0, heading)
        else:
            paragraphs = [terminal_prose(category.get("description", ""))]
            if browser.profile.get("positional_group"):
                paragraphs.append("Repeated value group: " + browser.profile["positional_group"]["argument"])
        lines = layout_details(paragraphs, width, browser.accent)
        body = stop - start
        last = max(0, len(lines) - body)
        offset = browser.detail_offset = min(max(0, browser.detail_offset), last)
        browser.next_detail_offset = min(offset + body, last) if offset < last else 0
        for row, line in enumerate(lines[offset:offset + body], start):
            write(screen, row, 0, line.text, width)
            for column, word, attr in line.highlights:
                write(screen, row, column, word, width - column, attr)
        hints = [(back, "back")]
        if last:
            hints.append(detail_page_hint(browser, keys))
        if selected:
            hints.append((key("accept"), accept))
    else:
        picking = page == "categories"
        entries = categories if picking else options
        index = browser.category if picking else browser.selected
        first = max(0, min(len(entries) - capacity, index - (capacity - 1) // 2))
        fw = option_label_width(category, width) if options and not picking else 0
        for i, item in enumerate(entries[first:first + capacity], first):
            row = start + 2 * (i - first)
            label = item["name"] if picking else ellipsize_cells(option_label(item), fw)
            prefix = "> " if i == index else "  "
            text = prefix + label
            if not picking:
                summary = browser.visible_summary(item, row_summary(browser.text(item), ()), row,
                                                  fw + 4, width - fw - 4, i == index and not searching)
                text += " " * (fw - sum(map(cell_width, label)) + 2) + summary
            write(screen, row, 0, ellipsize_cells(text, width), width, curses.A_REVERSE if i == index else 0)
            if i != index:
                write(screen, row, 2, label, width - 2, curses.A_BOLD | (browser.section_color if picking else browser.accent))
        if not entries:
            write(screen, start, 0, "No matches. Clear the filter or go back.", width)
        hints = [(move, "move" if picking or width >= 65 else "")]
        if picking:
            hints.append((forward, "options"))
        else:
            hints.extend([(back, "back"), (forward, "details")])
            if selected:
                hints.append((key("accept"), accept))
    hints.append((key("cancel"), "exit"))
    if page != "details":
        hints.append((key("search"), "find"))
    if searching:
        hints = [("enter", "apply"), ("esc", "restore")]
    write(screen, height - 2, 0, "━" * width, width)
    draw_hints(screen, height - 1, width, hints, browser.key_color)
    return capacity


def draw(screen, browser: Browser, keys, searching=False, preview=False, scroll=None):
    """Present a complete frame, retaining the current slice on unrelated redraws."""
    capacity = draw_frame(screen, browser, keys, searching, preview)
    if scroll and scroll.target == browser.summary_field and scroll.visible:
        scroll.paint(screen)
    screen.refresh()
    if scroll:
        scroll.select(browser.summary_field, time.monotonic())
    return capacity


def draw_frame(screen, browser: Browser, keys, searching, preview):
    """Lay out one frame and return the focused pane's selectable page capacity."""
    height, width = screen.getmaxyx()
    browser.summary_field = None
    screen.erase()
    if height < 16 or width < 60:
        write(screen, 0, 0, "Resize to at least 60 columns x 16 rows; Esc cancels.", width - 1)
        return 1
    if browser.guided and width < 80:
        if not browser.compact_page:
            if browser.focus == "categories" or (not browser.query and len(browser.profile["categories"]) > 1):
                browser.compact_page = "categories"
            else:
                browser.compact_page = "options"
        browser.focus = "categories" if browser.compact_page == "categories" else "options"
        return draw_compact(screen, browser, keys, searching, preview)
    # Remember the narrow reading screen over a wide resize. Wide navigation
    # still determines which pane has focus when the terminal shrinks again.
    if browser.guided:
        if browser.focus == "categories":
            browser.compact_page = "categories"
        elif browser.compact_page != "details" or searching:
            browser.compact_page = "options"
    left = min(26, width // 3)
    budget = width - left - 1
    category = browser.profile["categories"][browser.category]
    options = browser.options()
    level = browser.level
    option = options[browser.selected] if options else None
    view = browser.text(option) if option else None
    note, group = shared_note(browser, options, budget) if view else ("", ())
    fw = option_label_width(category, budget)
    description_width = budget - fw - 4
    label = option_label(option) if option else ""
    detail = []
    clipped_label = False
    if view:
        summary = row_summary(view, group)
        clipped_label = ellipsize_cells(label, fw) != label
        detail.extend(level_guidance(view, level))
        if ellipsize_cells(summary, description_width) != summary:
            detail.append(summary)
        if clipped_label and sum(map(cell_width, label)) > width - 22:
            detail.insert(0, label)
    else:
        detail.append(terminal_prose(category.get("description", "")))
        if browser.profile.get("positional_group"):
            detail.append("Repeated value group: " + browser.profile["positional_group"]["argument"])
    category_title = f"Category {browser.category + 1}/{len(browser.profile['categories'])} | " + category["name"]
    if sum(map(cell_width, category_title)) > width - 1:
        detail.insert(0, category["name"])
    if browser.focus == "categories":
        detail = [category["name"], terminal_prose(category.get("description", "")),
                  terminal_prose(browser.profile["description"])]
    lines = layout_details([line for line in detail if line], width - 1, browser.accent)
    top = 4 + bool(note)
    # Reserve at least two selectable rows at minimum size.
    available = height - 2 - top
    body_cap = available - 4
    if level == "Expanded":
        body_cap = min(body_cap, max(6, height // 2 - 1))
    if level == "Simple":
        body_cap = min(body_cap, 1)
    elif level == "Detailed":
        body_cap = min(body_cap, 3)
    body = min(len(lines), body_cap)
    header = bool(body or (clipped_label and browser.focus == "options"))
    end = height - 2 - body - header
    slots = end - top
    capacity = (slots + 1) // 2
    first = max(0, min(len(options) - capacity, browser.selected - (capacity - 1) // 2))

    draw_title(screen, browser, keys, preview, width - 1)
    write(screen, 1, 0, ellipsize_cells(category_title, width - 1), width - 1)
    if searching or browser.query:
        write(screen, 2, 0, ("Search: " if searching else "Filter: ") + browser.query,
              width - 1, curses.A_REVERSE if searching else 0)
    count = f"{browser.selected + 1 if options else 0}/{len(options)}"
    for x, pane, span in ((0, "categories", left - 3), (left, "options", budget - len(count) - 1)):
        name = pane.upper() + (" *" if browser.focus == pane else "")
        write(screen, 3, x, name, span, curses.A_BOLD | browser.section_color)
        rule = span - len(name) - 1
        write(screen, 3, x + len(name) + 1, "━" * rule, rule)
    write(screen, 3, width - len(count) - 1, count, len(count))
    if note:
        write(screen, 4, left, note, budget)
    start = max(0, browser.category - capacity + 1)
    for index, c in enumerate(browser.profile["categories"][start:start + capacity], start):
        y = top + (index - start) * 2
        selected = index == browser.category
        name = c["name"]
        count = f" ({len(browser.options(index))})" if browser.query else ""
        name_budget = left - 5 - len(count)
        text = ("> " if selected else "  ") + category_label(name, name_budget) + count
        write(screen, y, 0, text, left - 3, (curses.A_BOLD | browser.section_color) if selected else 0)
    for i, item in enumerate(options[first:first + capacity], first):
        y = top + (i - first) * 2
        selected = i == browser.selected
        flag = ellipsize_cells(option_label(item), fw)
        attr = curses.A_REVERSE if selected else 0
        marker = "> " if selected else "  "
        text = row_summary(browser.text(item), group)
        visible = browser.visible_summary(item, text, y, left + fw + 4, description_width,
                                          selected and browser.focus == "options" and not searching)
        row = marker + flag + " " * (fw - sum(map(cell_width, flag)) + 2) + visible
        write(screen, y, left, row, budget, attr)
        if not selected:
            write(screen, y, left + 2, flag, fw, curses.A_BOLD | browser.accent)
    if not options:
        write(screen, top, left, "No matches. Clear the filter or change category.", budget)
    browser.detail_offset = min(max(0, browser.detail_offset), max(0, len(lines) - body))
    offset = browser.detail_offset
    browser.next_detail_offset = min(offset + body, len(lines) - body) if offset + body < len(lines) else 0
    if header:
        counter = f"Lines {offset + 1}–{offset + body}/{len(lines)}" if body < len(lines) else ""
        header_width = width - len(counter) - 2
        page = lines[offset:offset + body]
        heading = category["name"] if browser.focus == "categories" else label or category["name"]
        # Keep conversion units visible when scrolling past their table heading.
        if offset and page and page[0].bitrate:
            heading = "Result (bps)"
        option_heading = option and browser.focus == "options" and heading == label
        heading = ellipsize_cells(heading, header_width - 3)
        write(screen, end, 0, heading + " " + "─" * max(0, header_width - sum(map(cell_width, heading)) - 1),
              header_width, curses.A_BOLD)
        if option_heading and browser.accent:
            write(screen, end, 0, heading, header_width, curses.A_BOLD | browser.accent)
        if counter:
            write(screen, end, width - 1 - len(counter), counter, len(counter))
        for y, line in enumerate(page, end + 1):
            write(screen, y, 0, line.text, width - 1)
            for column, word, attr in line.highlights:
                write(screen, y, column, word, width - 1 - column, attr)
    write(screen, height - 2, 0, "━" * (width - 1), width - 1)
    draw_controls(screen, height - 1, width - 1, browser, keys, searching, preview, body < len(lines))
    for y in range(3, end):
        write(screen, y, left - 2, "│", 1)
    return capacity


def run_browser(screen, profile, query, keys, preview=False):
    """Run a modal selector; return an option or None without accepting a shell line."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.raw()
    screen.keypad(True)
    curses.set_escdelay(escape_delay())
    actions = {NAMED_KEYS.get(key, key): action for action, names in keys.items() for key in names}
    if "\n" in actions:
        actions["\r"] = actions["\n"]
        actions[curses.KEY_ENTER] = actions["\n"]
    browser = Browser(profile, query, guided=os.environ.get("CLI_HELP_NARROW_MENU") == "1")
    browser.accent, browser.section_color, browser.key_color = menu_colors()
    scroll = SummaryScroll()
    browser.scroll_summaries = os.environ.get("CLI_HELP_SCROLL_SUMMARIES", "1") == "1"
    searching = False
    saved_query = query
    search_origin = None
    drawn_size = None
    while True:
        # A helper launched through Bash process substitution may not receive
        # the foreground shell's resize signal. Poll the controlling terminal
        # so resizing remains reliable even when SIGWINCH is not delivered.
        size = os.get_terminal_size(0)
        geometry = (size.lines, size.columns)
        if geometry != screen.getmaxyx():
            curses.resizeterm(*geometry)
            drawn_size = None
        if geometry != drawn_size:
            rows = draw(screen, browser, keys, searching, preview, scroll)
            drawn_size = geometry
        if scroll.deadline is not None:
            scroll.tick(screen, time.monotonic())
        # Keep polling geometry while waiting for the next animation frame.
        wait = 150
        if scroll.deadline is not None:
            wait = min(wait, max(1, math.ceil((scroll.deadline - time.monotonic()) * 1000)))
        screen.timeout(wait)
        try:
            key = screen.get_wch()
        except curses.error:
            # A timeout leaves the frame and its paging capacity valid.
            continue
        drawn_size = None
        if key == curses.KEY_RESIZE:
            continue
        if searching:
            if key in ("\n", "\r", curses.KEY_ENTER):
                searching = False
            elif key == "\x1b":
                browser.set_query(saved_query)
                if browser.compact_page and search_origin:
                    browser.compact_page = search_origin
                searching = False
            elif key == "\x03":
                return None
            elif key in ("\x7f", "\b", curses.KEY_BACKSPACE):
                browser.set_query(browser.query[:-1])
            elif key == "\x15":
                browser.set_query("")
            elif isinstance(key, str) and key.isprintable():
                browser.set_query(browser.query + key)
            continue
        action = actions.get(key)
        if action == "cancel" or key in ("\x1b", "\x03"):
            return None
        if screen.getmaxyx()[0] < 16 or screen.getmaxyx()[1] < 60:
            continue
        if action == "toggle_summary_scroll":
            browser.scroll_summaries = not browser.scroll_summaries
            continue
        if action == "cycle_detail":
            browser.level = LEVELS[(LEVELS.index(browser.level) + 1) % len(LEVELS)]
            browser.detail_offset = 0
            continue
        page = browser.compact_page if geometry[1] < 80 else None
        if page:
            if action in ("focus", "previous_category", "next_category", "accept"):
                if action == "accept" and page != "categories":
                    if browser.options():
                        return browser.options()[browser.selected]
                    continue
                if action == "previous_category" or (action == "focus" and page != "categories"):
                    destination = "options" if page == "details" else "categories"
                elif page == "categories":
                    destination = "options"
                else:
                    destination = "details"
                if destination == page:
                    continue
                browser.compact_page = destination
                browser.focus = "categories" if destination == "categories" else "options"
                browser.detail_offset = 0
                continue
            if page == "details" and action not in ("detail_up", "detail_down", "detail_page"):
                continue
            if action == "search":
                browser.compact_page = "options"
                browser.focus = "options"
        move = browser.move_category if browser.focus == "categories" else browser.move_option
        if action in ("up", "down", "page_up", "page_down", "first", "last"):
            move({"up": -1, "down": 1, "page_up": -rows, "page_down": rows, "first": -1000000, "last": 1000000}[action])
        elif action == "previous_category":
            browser.move_category(-1)
        elif action == "next_category":
            browser.move_category(1)
        elif action == "focus":
            browser.focus = "categories" if browser.focus == "options" else "options"
        elif action == "detail_page":
            browser.detail_offset = browser.next_detail_offset
        elif action == "detail_up":
            browser.detail_offset = max(0, browser.detail_offset - 1)
        elif action == "detail_down":
            browser.detail_offset += 1
        elif action == "clear_search":
            browser.set_query("")
        elif action == "search":
            search_origin = page
            saved_query = browser.query
            searching = True
        elif action == "accept":
            if browser.focus == "categories":
                browser.focus = "options"
            elif browser.options():
                return browser.options()[browser.selected]
