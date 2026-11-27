"""Reconcile the independent ls manual inventory and exercise its Bash menu."""

from dataclasses import dataclass
import json
import re
import sys
import unittest

from test_terminal_screen import ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option
from presentation import option_label, option_text
from ui import Browser, ellipsize_cells


CAPTURES = ROOT / "tests/fixtures/ls"
GNU_CAPTURES = ("gnu-ls-9.4", "gnu-ls-9.7")
UUTILS_CAPTURE = "uutils-ls-0.10.0"


@dataclass(frozen=True)
class ManualOption:
    """One selectable effect and the spellings declared for it in the audit."""

    flag: str
    aliases: tuple
    operand: str

    @property
    def arity(self):
        if self.operand == "—":
            return "switch"
        return "optional" if self.operand.startswith("[=") else "required"


def manual_options():
    """Read only the six-column declaration table, independent of the profile."""
    audit = (ROOT / "docs/ls-manual-coverage.md").read_text(encoding="utf-8")
    table = audit.split("| Canonical |", 1)[1].split("\n\n", 1)[0]
    for line in table.splitlines():
        if line.startswith("| `-"):
            flag, aliases, operand, _, _, _ = line.strip("| ").split(" | ")
            yield ManualOption(flag.strip("`"), tuple(re.findall(r"`(-[^`]+)`", aliases)),
                               operand.strip("`"))


def fixed_declarations(capture):
    """Recover help heading groups and their operand arity from GNU or uutils output."""
    declarations = {}
    for line in (CAPTURES / f"{capture}-help.txt").read_text(encoding="utf-8").splitlines():
        if not re.match(r"^(?:  |      )-\S", line):
            continue
        heading = re.split(r"\s{2,}", line.strip(), maxsplit=1)[0]
        if heading == "-p, --indicator-style=slash":
            # GNU shows a fixed value here; the general argument-taking option has its own heading.
            heading = "-p"
        if "[=" in heading:
            arity = "optional"
        else:
            arity = "required" if "=" in heading or " <" in heading else "switch"
        spellings = frozenset(re.findall(r"(?:^|, )(-[\w-]+)", heading))
        if spellings in declarations:
            raise ValueError(f"Duplicate heading in {capture}: {heading}")
        declarations[spellings] = arity
    return declarations


def ls_profile():
    return json.loads((ROOT / "profiles/ls.json").read_text(encoding="utf-8"))


class LsInventoryTests(unittest.TestCase):
    def test_manual_declarations_match_each_fixed_help(self):
        """Keep platform-only aliases and the undocumented literal alias out of other help sets."""
        options = list(manual_options())
        self.assertEqual(len(options), 60)
        spellings = [flag for row in options for flag in (row.flag, *row.aliases)]
        self.assertCountEqual(spellings, set(spellings))
        for capture in (*GNU_CAPTURES, UUTILS_CAPTURE):
            with self.subTest(capture=capture):
                absent = {"--l"}  # A hidden uutils alias and a GNU abbreviation.
                if capture in GNU_CAPTURES:
                    absent.update(("--long", "-V"))
                expected = {frozenset((row.flag, *row.aliases)) - absent: row.arity
                            for row in options}
                self.assertEqual(fixed_declarations(capture), expected)

    def test_value_guides_and_release_specific_spellings(self):
        """Keep the original GNU review and map each additional contract to its own implementation."""
        profile = ls_profile()
        options = {row["flag"]: row for category in profile["categories"] for row in category["options"]}
        for flag in ("--human-readable", "--size", "--inode", "--numeric-uid-gid", "--hide=", "--color="):
            with self.subTest(flag=flag):
                variants = options[flag]["value_semantics"]["variants"]
                scopes = {(implementation, version) for variant in variants
                          for implementation in variant["applicability"]["implementation"]["values"]
                          for version in variant["applicability"]["version"]["values"]}
                self.assertEqual(scopes, {("GNU coreutils", "9.4"), ("GNU coreutils", "9.6"),
                                          ("GNU coreutils", "9.7"), ("uutils coreutils", "0.10.0")})
        browser = Browser(profile)
        for flag, alias in (("-l", "--long"), ("--version", "-V"), ("--classify", "-F="),
                            ("--literal", "--l")):
            with self.subTest(alias=alias):
                details = " ".join(browser.text(options[flag]).details)
                self.assertIn("uutils", details)
                self.assertIn(alias, details)
        for flag, token, supported in (("--sort=", "name", {"9.7", "0.10.0"}),
                                       ("--format=", "columns", {"0.10.0"})):
            with self.subTest(flag=flag, value=token):
                releases = {version for variant in options[flag]["value_semantics"]["variants"]
                            if any(token in form["tokens"] for form in variant["forms"])
                            for version in variant["applicability"]["version"]["values"]}
                self.assertEqual(releases, supported)
        for variant in options["--color="]["value_semantics"]["variants"]:
            self.assertEqual(variant["when_value_omitted"]["value"], "always")
            tokens = {token for form in variant["forms"] for token in form["tokens"]}
            self.assertEqual(tokens, {"always", "yes", "force", "never", "no", "none",
                                      "auto", "tty", "if-tty"})

    def test_rows_cover_insertions_and_searchable_aliases(self):
        """Require each canonical spelling exactly once and a discoverable explanation of each alias."""
        profile = ls_profile()
        browser = Browser(profile)
        options = [row for category in profile["categories"] for row in category["options"]]
        by_name = {row["flag"].removesuffix("="): row for row in options}
        self.assertCountEqual([row["flag"].removesuffix("=") for row in options],
                              [row.flag for row in manual_options()])
        context = find_context("ls  'some dir'", 3, [profile])
        for declaration in manual_options():
            with self.subTest(flag=declaration.flag):
                option = by_name[declaration.flag]
                view = browser.text(option)
                details = " ".join(view.details)
                for alias in declaration.aliases:
                    self.assertRegex(details, r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])")
                    self.assertIn(alias.casefold(), view.searchable)
                if declaration.flag == "--classify":
                    # Retain the bare pilot insertion. A manually typed policy attaches with '='.
                    self.assertIn("--classify=", details)
                    expected_argument = None
                elif declaration.arity == "switch":
                    expected_argument = None
                else:
                    expected_argument = declaration.operand.removeprefix("[=").removesuffix("]")
                self.assertEqual(option.get("argument"), expected_argument)
                self.assertEqual(bool(option.get("argument_optional")),
                                 expected_argument is not None and declaration.arity == "optional")
                flag = declaration.flag + ("=" if expected_argument is not None else "")
                self.assertEqual(option["flag"], flag)
                line, point = insert_option(context, option)
                self.assertEqual(line, f"ls {flag} 'some dir'")
                self.assertEqual(point, len("ls " + flag) + int(expected_argument is None))
                pending = "ls " + declaration.flag + " "
                if declaration.arity == "required":
                    with self.assertRaises(HelpError) as caught:
                        find_context(pending, len(pending), [profile])
                    self.assertEqual(caught.exception.code, "option_value_required")
                    pending += "'value' "
                self.assertEqual(find_context(pending, len(pending), [profile]).query, "")


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class LsMenuTests(TerminalTestCase):
    def pending(self, columns, rows):
        """Position the cursor before a quoted pathname in the stubbed ls command."""
        shell = self.start()
        shell.resize(columns, rows)
        prefix, suffix = "ls ", " 'some dir'"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_every_row_and_complete_details(self):
        """Check visible option labels, summaries, authored prose and formatted value guidance."""
        profile = ls_profile()
        shell, prefix, suffix = self.pending(220, 150)
        shell.verify_profile(profile)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_alias_search_and_new_value_insertion_at_minimum_size(self):
        """Search for the uutils long alias and insert a new value prefix before the pathname."""
        shell, prefix, suffix = self.pending(60, 16)
        for query, expected, key in (("--long", "-l", "Escape"), ("--tabsize=", "--tabsize=", "Enter")):
            with self.subTest(query=query):
                self.assertEqual(shell.open_menu().cells[2].rstrip(), "")
                shell.keys("/")
                shell.text(query)
                shell.keys("Enter")
                state = shell.wait_for(lambda screen: screen.cells[2] == "Filter: " + query)
                self.assertIn("> " + expected, state.cells[4])
                shell.cancel(key)
                insertion = "" if key == "Escape" else expected
                self.assertEqual(shell.read_buffer(), (prefix + insertion + suffix, len(prefix + insertion)))
        shell.text("4")
        self.assertEqual(shell.read_buffer(), (prefix + "--tabsize=4" + suffix, len(prefix + "--tabsize=4")))
        self.assertFalse(shell.executed.exists())
