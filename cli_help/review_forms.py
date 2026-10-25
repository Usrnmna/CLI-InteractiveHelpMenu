"""Guided, transactional edits of review drafts without executing help routes."""

import json

from core import HelpError
from manual_import import validate_documents
from authoring import driver_context, prepare_profile


PAGE_SIZE = 12


class FormCancelled(Exception):
    """A form was cancelled before its changes were applied to the draft."""


def answer(prompt):
    """Read a form response, reserving /cancel for whole-operation cancellation."""
    value = input(prompt).strip()
    if value == "/cancel":
        raise FormCancelled
    return value


def text_field(label, current="", optional=False, multiline=False):
    """Retain blank responses; explicitly clear optional fields or enter paragraphs."""
    print(label + " current: " + json.dumps(current, ensure_ascii=True))
    hints = "Enter keeps"
    if optional:
        hints += ", /clear empties"
    if multiline:
        hints += ", /lines enters multiple lines"
    value = answer(f"{label} ({hints}): ")
    if not value:
        return current
    if value == "/clear":
        if not optional:
            raise HelpError(label + " is required and cannot be cleared.")
        return ""
    if value == "/lines" and multiline:
        print("Enter lines; a single . finishes, .. inserts a literal dot, /cancel cancels.")
        lines = []
        while True:
            line = input("> ")
            if line == "/cancel":
                raise FormCancelled
            if line == ".":
                return "\n".join(lines)
            lines.append("." if line == ".." else line)
    return value


def yes_no(label, current=False):
    """Require an explicit boolean response or retain the displayed default."""
    while True:
        value = answer(f"{label} [{'Y/n' if current else 'y/N'}]: ").lower()
        if not value:
            return current
        if value in {"y", "yes", "n", "no"}:
            return value in {"y", "yes"}
        print("Enter y or n, or /cancel.")


def position(label, count, current):
    """Read a bounded one-based display position and return its zero-based index."""
    while True:
        value = answer(f"{label} [1-{count}, Enter keeps {current + 1}]: ")
        if not value:
            return current
        if value.isdecimal() and 1 <= int(value) <= count:
            return int(value) - 1
        print(f"Enter a position from 1 to {count}, or /cancel.")


def choose(labels, title):
    """Select a stable item index from a paginated, searchable list."""
    if not labels:
        print("No entries are available.")
        raise FormCancelled
    page, query = 0, ""
    while True:
        indices = [index for index, label in enumerate(labels) if query.casefold() in label.casefold()]
        page = min(page, max(0, (len(indices) - 1) // PAGE_SIZE))
        print(f"{title}: {len(indices)} matches | page {page + 1}")
        for index in indices[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]:
            print(f"{index + 1}. " + json.dumps(labels[index][:160], ensure_ascii=True))
        value = answer("Select number | n/p page | f filter | Enter cancels: ").lower()
        if not value:
            raise FormCancelled
        if value == "n":
            page += 1
        elif value == "p":
            page = max(0, page - 1)
        elif value == "f":
            query, page = answer("Contains (blank clears): "), 0
        elif value.isdecimal() and int(value) - 1 in indices:
            return int(value) - 1
        else:
            print("Select a matching number or a navigation action.")


def apply_document(draft, document):
    """Validate a complete operation before replacing draft text; never save files.

    Removing the final option may leave the same empty profile used by a new
    review entry. It remains editable but cannot be previewed or saved until an
    option is added. A temporary validation profile is never persisted.
    """
    previous = draft.document()
    if document["profile"]["command"] != previous["profile"]["command"]:
        raise HelpError("Guided edits must retain the selected command path.")
    document["profile"] = prepare_profile(previous["profile"], document["profile"],
        reviewed=draft.numerical_reviewed(document),
        context_changed=driver_context(previous["profile"], previous["driver"]) != driver_context(document["profile"], document["driver"]))
    check = dict(document["profile"])
    if not check["categories"]:
        check["categories"] = [{"name": "Draft", "options": [{"flag": "--draft", "summary": "Draft validation"}]}]
    validate_documents(check, document["driver"])
    draft.text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    notes = document["profile"].get("documentation", {}).get("diagnostics", []) if isinstance(document["profile"].get("documentation"), dict) else []
    if isinstance(notes, list) and any(isinstance(note, dict) and note.get("code") == "authoring_semantics_review" for note in notes):
        print("Numerical declarations require review and remain inactive. Use Edit JSON and Numerical review; original evidence is retained.")
    print("Draft updated. Preview or Save to continue.")


def edit_options(draft):
    """Edit, move, reorder, or delete one existing option using a detached document."""
    document = draft.document()
    categories = document["profile"]["categories"]
    action = answer("Options: [e]dit [m]ove/reorder [d]elete: ").lower()
    if action not in {"e", "m", "d"}:
        raise FormCancelled
    locations = [(category_index, option_index) for category_index, category in enumerate(categories)
                 for option_index in range(len(category["options"]))]
    labels = [categories[ci]["name"] + " | " + categories[ci]["options"][oi]["flag"] + " | "
              + categories[ci]["options"][oi]["summary"] for ci, oi in locations]
    category_index, option_index = locations[choose(labels, "Options")]
    category = categories[category_index]
    option = category["options"][option_index]
    if action == "e":
        option["flag"] = text_field("Literal flag", option["flag"])
        option["summary"] = text_field("Summary", option["summary"])
        option["detail"] = text_field("Detail", option.get("detail", ""), optional=True, multiline=True)
        argument = text_field("Argument placeholder", option.get("argument", ""), optional=True)
        if argument:
            option["argument"] = argument
            option["argument_optional"] = yes_no("Argument optional?", option.get("argument_optional", False))
            if not option["argument_optional"]:
                option.pop("optional_value_kind", None)
        else:
            option.pop("argument", None)
            option.pop("argument_optional", None)
            option.pop("argument_count", None)
            option.pop("attached", None)
            option.pop("argument_style", None)
            option.pop("optional_value_kind", None)
    elif action == "d":
        if not yes_no("Delete this option?"):
            return
        category["options"].pop(option_index)
    else:
        destination_index = choose([item["name"] for item in categories] + ["[New category]"], "Destination categories")
        if destination_index == len(categories):
            destination = {"name": text_field("New category name"),
                           "description": text_field("New category description", optional=True, multiline=True), "options": []}
            categories.append(destination)
        else:
            destination = categories[destination_index]
        category["options"].pop(option_index)
        default_position = option_index if destination is category else len(destination["options"])
        target = position("Option position", len(destination["options"]) + 1, default_position)
        destination["options"].insert(target, option)
    if not category["options"]:
        categories.remove(category)
        print("The empty source category was removed from this operation.")
    apply_document(draft, document)


def edit_categories(draft):
    """Edit category metadata or profile description; reorder or remove categories."""
    document = draft.document()
    profile = document["profile"]
    categories = profile["categories"]
    action = answer("Categories: [e]dit [m]ove/reorder [d]elete [t]op-level description: ").lower()
    if action == "t":
        profile["description"] = text_field("Profile description", profile["description"], multiline=True)
    elif action in {"e", "m", "d"}:
        index = choose([category["name"] for category in categories], "Categories")
        category = categories[index]
        if action == "e":
            category["name"] = text_field("Category name", category["name"])
            category["description"] = text_field("Category description", category.get("description", ""),
                                                  optional=True, multiline=True)
        elif action == "m":
            target = position("Category position", len(categories), index)
            categories.insert(target, categories.pop(index))
        else:
            if not yes_no(f"Delete this category and its {len(category['options'])} options?"):
                return
            categories.pop(index)
    else:
        raise FormCancelled
    apply_document(draft, document)


def edit_driver(draft):
    """Edit global-option arity or an existing fixed documentation route as data."""
    document = draft.document()
    driver = document["driver"]
    action = answer("Driver: [g]lobal options [r]oute settings: ").lower()
    if action == "g":
        print("Enter space-separated flags. Built-in global options remain active.")
        for key, label in (("global_values", "Globals requiring values"), ("global_flags", "Global boolean flags")):
            driver[key] = text_field(label, " ".join(driver.get(key, [])), optional=True).split()
    elif action == "r":
        routes = driver["paths"]
        index = choose([" ".join([driver["command"], *route["command"]]) for route in routes], "Driver routes")
        route = routes[index]
        route["man"] = text_field("Manual page", route.get("man") or "", optional=True) or None
        print("Help arguments are fixed words, without the executable name; /clear disables executable help.")
        route["help"] = text_field("Help arguments", " ".join(route.get("help", [])), optional=True).split()
        route["stop_at_positional"] = yes_no("Stop at the first positional argument?", route.get("stop_at_positional", False))
    else:
        raise FormCancelled
    apply_document(draft, document)
