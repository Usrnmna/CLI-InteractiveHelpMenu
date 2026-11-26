"""Curses browser with independently scrollable categories, options, and details."""

import curses
from dataclasses import dataclass, field
import os
import re
from pathlib import Path
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
    "detail_up": ["["], "detail_down": ["]"], "cycle_detail": ["D"],
}

NAMED_KEYS = {
    "up": curses.KEY_UP, "down": curses.KEY_DOWN,
    "left": curses.KEY_LEFT, "right": curses.KEY_RIGHT,
    "pageup": curses.KEY_PPAGE, "pagedown": curses.KEY_NPAGE,
    "home": curses.KEY_HOME, "end": curses.KEY_END,
    "f6": curses.KEY_F6, "tab": "\t", "enter": "\n", "esc": "\x1b",
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
        if "cycle_detail" not in document["keys"]:
            occupied = {key for action, values in bindings.items() if action != "cycle_detail"
                        and isinstance(values, list) for key in values if isinstance(key, str)}
            fallback = next((key for key in ("D", "V", "f6") if key not in occupied), None)
            if not fallback:
                raise HelpError("Configure a free key for cycle_detail (D, V and F6 are occupied).")
            bindings["cycle_detail"] = [fallback]
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
    "Cache and registries": "Cache/registries", "Certificate checking": "Cert checks",
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
    "Container selection": "Select container", "Protocol and version": "Protocol/version",
    "Actions and history": "Actions/history", "Test binary flags": "Test binary args",
    "Runtime and security": "Runtime/security",
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


def option_accent():
    """Use the terminal's foreground/background policy and fall back cleanly to monochrome."""
    if os.environ.get("NO_COLOR"):
        return 0
    # COLORFGBG is optional. Use bold/markers when the terminal does not report
    # its background; cyan on an unknown light background can be unreadable.
    background = os.environ.get("COLORFGBG", "").rsplit(";", 1)[-1]
    if not background.isascii() or not background.isdigit() or len(background) > 3:
        return 0
    try:
        if not curses.has_colors() or curses.COLOR_PAIRS < 2:
            return 0

        def luminance(index):
            """Convert the terminal's reported RGB values to relative luminance."""
            rgb = [component / 1000 for component in curses.color_content(index)]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
            return sum(channel * weight for channel, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

        bg = luminance(int(background))
        for accent in (curses.COLOR_CYAN, curses.COLOR_BLUE):
            fg = luminance(accent)
            if (max(bg, fg) + 0.05) / (min(bg, fg) + 0.05) >= 4.5:
                curses.use_default_colors()
                curses.init_pair(1, accent, -1)
                return curses.color_pair(1)
    except (AttributeError, ValueError, curses.error):
        pass
    return 0


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


def draw(screen, browser: Browser, keys, searching=False, preview=False):
    """Lay out one frame and return the focused pane's selectable page capacity."""
    height, width = screen.getmaxyx()
    screen.erase()
    if height < 16 or width < 60:
        write(screen, 0, 0, "Resize to at least 60 columns x 16 rows; Esc cancels.", width - 1)
        screen.refresh()
        return 1
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
        if level == "Detailed":
            detail.extend(view.detailed)
        elif level == "Expanded":
            detail.extend(view.expanded)
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
    lines = [row for line in detail if line for row in wrap_cells(line, width - 1)]
    top = 4 + bool(note)
    # Reserve at least two selectable rows at minimum size.
    available = height - 2 - top
    body_cap = available - 3
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
    stride = 2 if slots >= 3 else 1
    capacity = (slots + stride - 1) // stride
    first = max(0, min(len(options) - capacity, browser.selected - (capacity - 1) // 2))

    hint = level + "   " + keys["cycle_detail"][0] + " change view"
    hint_width = sum(map(cell_width, hint))
    title = ("Help preview | " if preview else "Interactive help | ") + " ".join(browser.profile["command"])
    write(screen, 0, 0, title, width - hint_width - 2, curses.A_BOLD)
    write(screen, 0, width - hint_width - 1, hint, hint_width, curses.A_BOLD)
    write(screen, 1, 0, ellipsize_cells(category_title, width - 1), width - 1)
    write(screen, 2, 0, ("Search (Enter applies, Esc restores): " if searching else "Filter: ") + browser.query,
          width - 1, curses.A_REVERSE if searching else 0)
    write(screen, 3, 0, "CATEGORIES" + (" *" if browser.focus == "categories" else ""), left - 2, curses.A_BOLD)
    write(screen, 3, left, "OPTIONS" + (" *" if browser.focus == "options" else ""), budget, curses.A_BOLD)
    count = f"{browser.selected + 1 if options else 0}/{len(options)}"
    write(screen, 3, width - len(count) - 1, count, len(count))
    if note:
        write(screen, 4, left, note, budget)
    category_capacity = end - 4
    start = max(0, browser.category - category_capacity + 1)
    for y, c in enumerate(browser.profile["categories"][start:start + category_capacity], 4):
        index = start + y - 4
        selected = index == browser.category
        name = c["name"]
        count = f" ({len(browser.options(index))})" if browser.query else ""
        name_budget = left - 4 - len(count)
        text = ("> " if selected else "  ") + category_label(name, name_budget) + count
        write(screen, y, 0, text, left - 2, curses.A_BOLD if selected else 0)
    for i, item in enumerate(options[first:first + capacity], first):
        y = top + (i - first) * stride
        selected = i == browser.selected
        flag = ellipsize_cells(option_label(item), fw)
        attr = curses.A_REVERSE if selected else 0
        marker = "> " if selected else "  "
        text = row_summary(browser.text(item), group)
        row = marker + flag + " " * (fw - sum(map(cell_width, flag)) + 2) + ellipsize_cells(text, description_width)
        write(screen, y, left, row, budget, attr)
        if not selected and browser.accent:
            write(screen, y, left + 2, flag, fw, browser.accent)
    if not options:
        write(screen, top, left, "No matches. Clear the filter or change category.", budget)
    browser.detail_offset = min(max(0, browser.detail_offset), max(0, len(lines) - body))
    offset = browser.detail_offset
    if header:
        counter = f"Lines {offset + 1}–{offset + body}/{len(lines)}" if body < len(lines) else ""
        header_width = width - len(counter) - 2
        page = lines[offset:offset + body]
        heading = category["name"] if browser.focus == "categories" else label or category["name"]
        # Keep conversion units visible when scrolling past their table heading.
        if offset and page and re.match(r"^\S.*?\s{2,}N(?: × |$)", page[0]):
            heading = "Result (bps)"
        heading = ellipsize_cells(heading, header_width - 3)
        write(screen, end, 0, heading + " " + "─" * max(0, header_width - sum(map(cell_width, heading)) - 1),
              header_width, curses.A_BOLD)
        if counter:
            write(screen, end, width - 1 - len(counter), counter, len(counter))
        for y, line in enumerate(page, end + 1):
            write(screen, y, 0, line, width - 1)
    key = lambda action: keys[action][0]
    write(screen, height - 2, 0, f"{key('up')}/{key('down')} move  {key('previous_category')}/{key('next_category')} category  "
          f"{key('focus')} focus  {key('search')} search", width - 1)
    footer = f"{key('accept')} {'inspect' if preview else 'insert'}  {key('cancel')} cancel"
    if body < len(lines):
        footer += f"  {key('detail_up')}/{key('detail_down')} scroll details"
    write(screen, height - 1, 0, footer, width - 1)
    for y in range(3, end):
        write(screen, y, left - 2, "│", 1)
    screen.refresh()
    return category_capacity if browser.focus == "categories" else capacity


def run_browser(screen, profile, query, keys, preview=False):
    """Run a modal selector; return an option or None without accepting a shell line."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.raw()
    screen.keypad(True)
    screen.timeout(150)
    curses.set_escdelay(escape_delay())
    actions = {NAMED_KEYS.get(key, key): action for action, names in keys.items() for key in names}
    if "\n" in actions:
        actions["\r"] = actions["\n"]
        actions[curses.KEY_ENTER] = actions["\n"]
    browser = Browser(profile, query)
    browser.accent = option_accent()
    searching = False
    saved_query = query
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
            rows = draw(screen, browser, keys, searching, preview)
            drawn_size = geometry
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
        move = browser.move_category if browser.focus == "categories" else browser.move_option
        if action in ("up", "down", "page_up", "page_down", "first", "last"):
            move({"up": -1, "down": 1, "page_up": -rows, "page_down": rows, "first": -1000000, "last": 1000000}[action])
        elif action == "previous_category":
            browser.move_category(-1)
        elif action == "next_category":
            browser.move_category(1)
        elif action == "focus":
            browser.focus = "categories" if browser.focus == "options" else "options"
        elif action == "cycle_detail":
            browser.level = LEVELS[(LEVELS.index(browser.level) + 1) % len(LEVELS)]
            browser.detail_offset = 0
        elif action == "detail_up":
            browser.detail_offset = max(0, browser.detail_offset - 1)
        elif action == "detail_down":
            browser.detail_offset += 1
        elif action == "clear_search":
            browser.set_query("")
        elif action == "search":
            saved_query = browser.query
            searching = True
        elif action == "accept":
            if browser.focus == "categories":
                browser.focus = "options"
            elif browser.options():
                return browser.options()[browser.selected]
