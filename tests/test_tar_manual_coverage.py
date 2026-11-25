"""Reconcile independent GNU tar declarations and inspect the real offline menu."""

import json
import re
import sys
import unittest

from test_terminal_screen import ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from presentation import option_label, option_text
from ui import Browser


def tar_profile():
    """Load the profile from the current sandbox snapshot."""
    return json.loads((ROOT / "profiles/tar.json").read_text(encoding="utf-8"))


def help_declarations(text):
    """Read GNU argp option headings and propagate each operand to its short aliases."""
    declarations = {}
    token = r"(--[a-z][a-z0-9-]*|-[A-Za-z?])(\[=|=)?"
    for line in text.split("Mandatory or optional arguments", 1)[0].splitlines():
        if not re.match(r"^ {2,6}-", line):
            continue
        heading = re.split(r"\s{2,}", line.strip())[0]
        aliases = [re.match(token, field) for field in heading.split(", ")]
        markers = {match[2] for match in aliases if match[2]}
        arity = "optional" if "[=" in markers else "required" if markers else "switch"
        for match in aliases:
            name = match[1]
            if name in declarations:
                raise ValueError("Duplicate fixed-help spelling " + name)
            declarations[name] = arity
    return declarations


class TarInventoryTests(unittest.TestCase):
    def test_menu_matches_man_pages_and_versioned_fixed_help(self):
        """Every documented spelling resolves to one row with the declared arity."""
        profile = tar_profile()
        browser = Browser(profile)
        rows = [o for c in profile["categories"] for o in c["options"]]
        by_name = {o["flag"].rstrip("="): o for o in rows}
        audit = (ROOT / "docs/tar-manual-coverage.md").read_text(encoding="utf-8")
        inventory = {}
        primary = []
        for line in audit.splitlines():
            if not line.startswith("| `-"):
                continue
            canonical, alias_column, operand = (c.strip() for c in line.strip("|").split("|"))
            name = canonical.strip("`")
            primary.append(name)
            option = by_name[name]
            arity = "optional" if operand.startswith("`[=") else "switch" if operand == "—" else "required"
            actual = "optional" if option.get("argument_optional") else "required" if option.get("argument") else "switch"
            self.assertEqual(actual, arity, name)
            self.assertEqual(option["flag"], name + ("=" if arity == "required" else ""))
            for spelling in [name, *re.findall(r"`([^`]+)`", alias_column)]:
                self.assertNotIn(spelling, inventory)
                inventory[spelling] = arity
                self.assertIn(spelling.casefold(), browser.text(option).searchable)
                if spelling != name:
                    self.assertRegex(option["detail"], r"(?<![\w-])" + re.escape(spelling) + r"(?![\w-])")
        self.assertCountEqual(primary, [o["flag"].rstrip("=") for o in rows])
        self.assertEqual((len(rows), len(inventory)), (157, 216))
        capture = (ROOT / "tests/fixtures/tar/gnu-tar-1.35-help.txt").read_text(encoding="utf-8")
        self.assertEqual(inventory, help_declarations(capture))

    def test_record_and_tape_units_and_signal_omission(self):
        """Check exact input units independently of the text formatter."""
        options = {o["flag"]: o for c in tar_profile()["categories"] for o in c["options"]}
        for flag, bare_unit in (("--record-size=", "1"), ("--tape-length=", "1024")):
            node = options[flag]["value_semantics"]["variants"][0]
            multipliers = {token: form["unit"]["multiplier"] for form in node["forms"]
                           for token in form.get("tokens", [None])}
            self.assertEqual((multipliers[None], multipliers["b"], multipliers["B"], multipliers["M"]),
                             (bare_unit, "512", "1024", "1048576"))
        totals = options["--totals"]
        self.assertTrue(totals["argument_optional"])
        signal = totals["value_semantics"]["variants"][0]
        self.assertEqual(signal["kind"], "enumeration")
        self.assertIn("at completion", signal["when_value_omitted"]["meaning"])
        self.assertIn("--totals=SIGNAL", totals["detail"])


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class TarMenuTests(TerminalTestCase):
    def pending_tar(self, columns, rows):
        """Leave the cursor between a blank option slot and an existing member."""
        shell = self.start()
        shell.resize(columns, rows)
        prefix, suffix = "tar ", " member.txt"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_every_row_and_all_details(self):
        """Compare visible cells with every authored sentence and formatted value rule."""
        profile = tar_profile()
        shell, prefix, suffix = self.pending_tar(210, 100)
        shell.verify_profile(profile)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_search_scroll_cancel_and_literal_selection_at_minimum_size(self):
        """Search unfiltered menus, read the last qualification and verify the cursor."""
        cases = (
            ("original working directory", "--directory=", "original working directory."),
            ("NUL-delimited file lists", "--null", "a filename character."),
            ("--get", "--extract", None),
            ("--totals=SIGNAL", "--totals", "separate word remains a member operand."),
        )
        for query, flag, final_text in cases:
            with self.subTest(flag=flag):
                shell, prefix, suffix = self.pending_tar(60, 16)
                for action in ("Escape", "Enter"):
                    menu = shell.open_menu()
                    self.assertEqual(menu.cells[2].rstrip(), "Filter:")
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    state = shell.wait_for(lambda state: state.cells[2] == "Filter: " + query)
                    self.assertIn("> " + flag, state.cells[4])
                    if final_text:
                        shell.find_detail(final_text)
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                point = len(prefix + flag) + int(not flag.endswith("="))
                self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, point))
                if flag == "--totals":
                    shell.keys("Left")
                    shell.text("=USR1")
                    self.assertEqual(shell.read_buffer(), (prefix + "--totals=USR1" + suffix,
                                                           len(prefix + "--totals=USR1")))
                self.assertFalse(shell.executed.exists())
