"""Curses browser with independently scrollable categories, options, and details."""

import curses
from dataclasses import dataclass, field
import os
from pathlib import Path
import unicodedata

from core import HelpError, read_json
from presentation import option_label, option_text, value_text
from terminal_text import strip_terminal_sequences


DEFAULT_KEYS = {
    "up": ["up", "k"], "down": ["down", "j"],
    "page_up": ["pageup"], "page_down": ["pagedown"],
    "first": ["home"], "last": ["end"],
    "previous_category": ["left", "h"], "next_category": ["right", "l"],
    "focus": ["tab"], "accept": ["enter"], "cancel": ["esc", "ctrl-c", "q"],
    "search": ["/"], "clear_search": ["ctrl-u"],
    "detail_up": ["["], "detail_down": ["]"],
}

NAMED_KEYS = {
    "up": curses.KEY_UP, "down": curses.KEY_DOWN,
    "left": curses.KEY_LEFT, "right": curses.KEY_RIGHT,
    "pageup": curses.KEY_PPAGE, "pagedown": curses.KEY_NPAGE,
    "home": curses.KEY_HOME, "end": curses.KEY_END,
    "tab": "\t", "enter": "\n", "esc": "\x1b",
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
    _text: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # A modal browser holds one read-only profile. Reopening, including a
        # preview after editing, derives fresh text; nothing is persisted.
        positional = value_text(self.profile, self.profile, positional=True)
        for category in self.profile["categories"]:
            for option in category["options"]:
                self._text[id(option)] = option_text(self.profile, category, option, positional=positional)
        for index in range(len(self.profile["categories"])):
            if self.options(index):
                self.category = index
                break

    def options(self, category=None):
        """Match the existing case-insensitive substring query against display text."""
        category = self.category if category is None else category
        query = self.query.casefold()
        return [option for option in self.profile["categories"][category]["options"]
                if query in self.text(option).searchable]

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
    return min(longest, 40, (budget - 4) // 2)


def option_row(option, view, budget, label_width, selected=False):
    """Align a literal declaration with its summary within a terminal-cell budget.

    Review notices precede the summary. A value hint is appended only if the
    complete summary and qualified hint fit; all omitted text remains in details.
    """
    label = ellipsize_cells(option_label(option), label_width)
    padding = " " * (label_width - sum(cell_width(c) for c in label))
    description_width = budget - label_width - 4
    description = (view.notice + " " if view.notice else "") + view.summary
    if view.list_hint:
        with_hint = description + " | " + view.list_hint
        if sum(cell_width(c) for c in display_text(with_hint)) <= description_width:
            description = with_hint
    return (("> " if selected else "  ") + label + padding + "  "
            + ellipsize_cells(description, description_width))


def draw(screen, browser: Browser, keys, searching=False, preview=False):
    """Render scroll windows around the selected category and option."""
    height, width = screen.getmaxyx()
    screen.erase()
    if height < 16 or width < 60:
        write(screen, 0, 0, "Resize to at least 60 columns x 16 rows; Esc cancels.", width - 1)
        screen.refresh()
        return 1
    category_width = min(26, width // 3)
    rows = max(3, (height - 9) // 2)
    title = ("Help preview | " if preview else "Interactive help | ") + " ".join(browser.profile["command"])
    write(screen, 0, 0, title, width - 1, curses.A_BOLD)
    write(screen, 1, 0, browser.profile["description"], width - 1)
    search_label = "Search (Enter applies, Esc restores): " if searching else "Filter: "
    write(screen, 2, 0, search_label + browser.query, width - 1, curses.A_REVERSE if searching else 0)
    write(screen, 3, 0, "CATEGORIES" + (" *" if browser.focus == "categories" else ""), category_width - 1, curses.A_BOLD)
    write(screen, 3, category_width, "OPTIONS" + (" *" if browser.focus == "options" else ""), width - category_width - 1, curses.A_BOLD)
    categories = browser.profile["categories"]
    first_category = max(0, browser.category - rows + 1)
    for row, index in enumerate(range(first_category, min(len(categories), first_category + rows)), 4):
        marker = "> " if index == browser.category else "  "
        text = marker + categories[index]["name"] + f" ({len(browser.options(index))})"
        write(screen, row, 0, text, category_width - 1, curses.A_REVERSE if index == browser.category else 0)
    options = browser.options()
    budget = width - category_width - 1
    label_width = option_label_width(categories[browser.category], budget)
    first_option = max(0, browser.selected - rows + 1)
    for row, index in enumerate(range(first_option, min(len(options), first_option + rows)), 4):
        option = options[index]
        text = option_row(option, browser.text(option), budget, label_width, index == browser.selected)
        write(screen, row, category_width, text, budget,
              curses.A_REVERSE if index == browser.selected else 0)
    if not options:
        write(screen, 4, category_width, "No matches. Clear the filter or change category.", width - category_width - 1)
    detail_row = 4 + rows
    count = f"Category {browser.category + 1}/{len(categories)} | Option {browser.selected + 1 if options else 0}/{len(options)}"
    write(screen, detail_row, 0, count, width - 1, curses.A_BOLD)
    category = categories[browser.category]
    if options:
        detail = "\n".join(browser.text(options[browser.selected]).details)
    else:
        detail = category.get("description", "")
    if not options and browser.profile.get("positional_group"):
        group = browser.profile["positional_group"]
        detail += "\nRepeated value group: " + group["argument"] + ". Enter each complete group manually; placeholders are never inserted."
    lines = [wrapped for paragraph in detail.splitlines() for wrapped in wrap_cells(paragraph, width - 2)]
    detail_rows = height - detail_row - 4
    browser.detail_offset = max(0, min(browser.detail_offset, max(0, len(lines) - detail_rows)))
    for row, text in enumerate(lines[browser.detail_offset:browser.detail_offset + detail_rows], detail_row + 1):
        write(screen, row, 0, text, width - 1)
    labels = lambda action: "/".join(keys[action])
    visible_end = min(len(lines), browser.detail_offset + detail_rows)
    progress = f"Details {browser.detail_offset + 1}-{visible_end}/{len(lines)}"
    if len(lines) > detail_rows:
        progress += f" | {labels('detail_up')}/{labels('detail_down')} scroll"
    write(screen, height - 3, 0, progress, width - 1)
    footer = f"{labels('up')}/{labels('down')} move | {labels('focus')} focus | {labels('previous_category')}/{labels('next_category')} category"
    write(screen, height - 2, 0, footer, width - 1)
    accept_label = "inspect" if preview else "insert"
    footer = f"{labels('accept')} {accept_label} | {labels('cancel')} cancel | {labels('search')} search | {labels('detail_up')}/{labels('detail_down')} details"
    write(screen, height - 1, 0, footer, width - 1)
    screen.refresh()
    return rows


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
    searching = False
    saved_query = query
    while True:
        # A helper launched through Bash process substitution may not receive
        # the foreground shell's resize signal. Poll the controlling terminal
        # so resizing remains reliable even when SIGWINCH is not delivered.
        size = os.get_terminal_size(0)
        if (size.lines, size.columns) != screen.getmaxyx():
            curses.resizeterm(size.lines, size.columns)
        rows = draw(screen, browser, keys, searching, preview)
        try:
            key = screen.get_wch()
        except curses.error:
            continue
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
