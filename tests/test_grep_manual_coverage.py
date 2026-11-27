"""Check GNU grep's independent declarations and the cells Bash users see."""

import json
import re
import sys
import unittest

from test_terminal_screen import ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from presentation import option_label, option_text
from ui import Browser


def grep_profile():
    """Load the bundled profile from the active sandbox snapshot."""
    return json.loads((ROOT / "profiles/grep.json").read_text(encoding="utf-8"))


def manual_rows():
    """Read the option inventory without treating later audit tables as declarations."""
    audit = (ROOT / "docs/grep-manual-coverage.md").read_text(encoding="utf-8")
    table = audit.split("| Canonical |", 1)[1].split("\n\n", 1)[0]
    for line in table.splitlines():
        if line.startswith("| `-"):
            flag, aliases, operand, scope, disposition = line.strip("| ").split(" | ")
            yield (flag.strip("`"), re.findall(r"`([^`]+)`", aliases),
                   operand.strip("`"), scope, disposition)


def capture_arities(version):
    """Parse GNU help headings, including the split color/colour declaration."""
    source = ROOT / f"tests/fixtures/grep/gnu-grep-{version}-help.txt"
    arities = {}
    for line in source.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^ +-", line):
            continue
        heading = re.split(r"\s{2,}", line.lstrip())[0].rstrip(",")
        if "[=" in heading:
            arity = "optional"
        else:
            arity = "required" if "=" in heading or heading == "-NUM" else "switch"
        for field in heading.split(", "):
            spelling = re.split(r"\[?=", field)[0]
            if spelling in arities:
                raise ValueError(f"Duplicate spelling {spelling} in GNU grep {version} help")
            arities[spelling] = arity
    return arities


class GrepInventoryTests(unittest.TestCase):
    def test_inventory_covers_both_release_captures_and_historical_forms(self):
        """Distinguish concrete insertions, fixed-value switches and the digit shorthand."""
        arities = {}
        for flag, aliases, operand, scope, _ in manual_rows():
            self.assertEqual(scope, "both", flag)
            if operand == "[=WHEN]":
                arity = "optional"
            else:
                arity = "switch" if operand == "—" else "required"
            for name in [flag, *aliases]:
                self.assertNotIn(name, arities)
                arities[name] = arity
        # These supported spellings occur in the release source outside fixed help.
        hidden = {"--fixed-regexp": "switch", "-y": "switch", "-X": "required"}
        for version in ("3.11", "3.12"):
            with self.subTest(version=version):
                declared = capture_arities(version)
                self.assertEqual(len(declared), 84)
                self.assertTrue(declared.keys().isdisjoint(hidden))
                self.assertEqual(arities, {**declared, **hidden})
                source = ROOT / f"tests/fixtures/grep/gnu-grep-{version}-version.txt"
                self.assertEqual(source.read_text(encoding="utf-8").splitlines()[0],
                                 "grep (GNU grep) " + version)

    def test_all_rows_insert_the_reviewed_spelling_and_expose_their_aliases(self):
        profile = grep_profile()
        browser = Browser(profile)
        options = [o for c in profile["categories"] for o in c["options"]]
        by_name = {o["flag"].removesuffix("="): o for o in options}
        primary = []
        for flag, aliases, operand, _, _ in manual_rows():
            with self.subTest(flag=flag):
                primary.append(flag)
                option = by_name[flag]
                value = {"—": None, "[=WHEN]": "WHEN"}.get(operand, operand)
                self.assertEqual(option.get("argument"), value)
                self.assertEqual(bool(option.get("argument_optional")), operand == "[=WHEN]")
                self.assertEqual(option["flag"], flag + ("=" if value and flag.startswith("--") else ""))
                visible = " ".join(browser.text(option).details)
                for alias in aliases:
                    self.assertRegex(visible, r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])")
                    self.assertIn(alias.casefold(), browser.text(option).searchable)
        self.assertCountEqual(primary, [o["flag"].removesuffix("=") for o in options])
        self.assertEqual(len(primary), len(set(primary)))
        self.assertEqual(len(primary), 48)
        self.assertNotIn("-NUM", by_name)
        self.assertTrue({"--binary-files", "--binary", "--text", "-I"} <= by_name.keys())
        binary_details = " ".join(browser.text(by_name["--binary"]).details)
        self.assertIn("Windows", binary_details)
        self.assertIn("Ubuntu", binary_details)
        perl_details = " ".join(browser.text(by_name["--perl-regexp"]).details)
        for version in ("3.11", "3.12"):
            capture = ROOT / f"tests/fixtures/grep/gnu-grep-{version}-version.txt"
            pcre_version = re.search(r"uses PCRE2 ([0-9.]+)", capture.read_text(encoding="utf-8"))[1]
            self.assertIn(pcre_version, perl_details)
        self.assertIn("10.43", perl_details)


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class GrepMenuTests(TerminalTestCase):
    def pending_grep(self, columns, rows):
        """Use the shell stub and leave two quoted operands beyond the cursor."""
        shell = self.start()
        shell.resize(columns, rows)
        prefix, suffix = "grep ", " 'two words' 'input file'"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_every_selectable_row_and_complete_details(self):
        profile = grep_profile()
        shell, prefix, suffix = self.pending_grep(210, 100)
        shell.verify_profile(profile)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def search(self, shell, query, flag):
        """Apply a manual spelling as a fresh search and inspect the selected row."""
        state = shell.open_menu()
        self.assertEqual(state.cells[2].rstrip(), "")
        shell.keys("/")
        shell.text(query)
        shell.keys("Enter")
        state = shell.wait_for(lambda s: s.cells[2] == "Filter: " + query)
        self.assertIn("> " + flag, state.cells[4])
        return state

    def test_quiet_alias_scroll_and_cancellation_at_minimum_size(self):
        shell, prefix, suffix = self.pending_grep(60, 16)
        state = self.search(shell, "--silent", "--quiet")
        shell.find_detail("A selected line gives status 0 even after an earlier file error.")
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_value_prefixes_preserve_both_quoted_operands(self):
        for query, flag, value in (("historical -NUM", "--context=", "2"), ("--colour", "--color=", "always")):
            with self.subTest(query=query):
                shell, prefix, suffix = self.pending_grep(60, 16)
                self.search(shell, query, flag)
                shell.cancel("Enter")
                inserted = prefix + flag
                self.assertEqual(shell.read_buffer(), (inserted + suffix, len(inserted)))
                shell.text(value)
                self.assertEqual(shell.read_buffer(), (inserted + value + suffix, len(inserted + value)))
                self.assertFalse(shell.executed.exists())
