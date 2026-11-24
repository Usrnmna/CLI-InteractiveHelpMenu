"""Reconcile native fzf spellings and operands with the bundled root menu."""

import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from command_paths import help_route, load_driver_registry
from presentation import option_text

RELEASES = ("N", "R", "U")
SPELLING = re.compile(r"`(--?[\w-]+|\+\w)`")


def inventory_rows():
    """Read the release-specific effect and arity table from the independent audit."""
    lines = (ROOT / "docs/fzf-manual-inventory.md").read_text(encoding="utf-8").splitlines()
    start = lines.index("| Effect | Native spellings | Operand | Parses | Manual heading | Fixed help |")
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("| "):
            break
        owner, spellings, operand, releases, manual, help_text = line.strip("| ").split(" | ")
        rows.append((owner.strip("`"), SPELLING.findall(spellings), operand.strip("`"),
                     releases, manual, help_text))
    return rows


class FzfManualInventoryTests(unittest.TestCase):
    def test_help_declarations_and_native_arity_by_release(self):
        """Every fixed-help heading maps to a native spelling on that exact release."""
        captures = json.loads((ROOT / "tests/fixtures/fzf-manual/root-help.json").read_text())
        self.assertEqual(captures["request"], ["fzf", "--help"])
        self.assertEqual(set(captures["captures"]), set(RELEASES))
        for release in RELEASES:
            capture = captures["captures"][release]
            native = {}
            manual_headings = set()
            fixed_headings = set()
            for _, spellings, operand, releases, manual, fixed in inventory_rows():
                if release in releases:
                    for spelling in spellings:
                        self.assertNotIn(spelling, native, (release, spelling))
                        native[spelling] = operand
                if release in manual:
                    manual_headings.update(spellings)
                if release in fixed:
                    fixed_headings.update(spellings)
            observed = set()
            for declaration in capture["declarations"]:
                match = re.fullmatch(r"((?:--?[\w-]+|\+\w)(?:, (?:--?[\w-]+|\+\w))*)(.*)",
                                     declaration)
                self.assertIsNotNone(match, declaration)
                for flag in match[1].split(", "):
                    with self.subTest(release=release, flag=flag):
                        observed.add(flag)
                        operand = native[flag]
                        self.assertEqual(bool(match[2]), operand != "none")
                        # Color has a bare form in the parser. The second listen
                        # heading describes the Unix socket variant of an optional address.
                        if flag == "--color" or declaration == "--listen=SOCKET_PATH":
                            self.assertTrue(operand.startswith("["))
                        else:
                            self.assertEqual(match[2].startswith("[="), operand.startswith("["))
            self.assertEqual(observed, fixed_headings, release)
            self.assertLessEqual(manual_headings, set(native), release)
            self.assertEqual(len(manual_headings), {"N": 84, "R": 133, "U": 138}[release])
            self.assertEqual(len(native), {"N": 139, "R": 208, "U": 218}[release])
        original = ROOT / "tests/fixtures/help/followup-systems/fzf.txt"
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),
                         captures["captures"]["N"]["stdout_sha256"])

    def test_complete_selectable_inventory_and_searchable_plus_aliases(self):
        """Check each menu row, the native union arity, and every plus alias owner."""
        profile = json.loads((ROOT / "profiles/fzf.json").read_text())
        menu = {row["flag"]: (category, row) for category in profile["categories"]
                for row in category["options"]}
        arities = {}
        effects = set()
        aliases = {}
        for owner, spellings, operand, _, _, _ in inventory_rows():
            effects.add(owner)
            for spelling in spellings:
                if spelling.startswith("+"):
                    aliases[spelling] = owner
                else:
                    arities.setdefault(spelling, set()).add(operand)
        self.assertEqual((len(effects), len(arities), len(aliases)), (191, 209, 9))
        self.assertEqual(set(menu), set(arities))
        for spelling, operands in arities.items():
            row = menu[spelling][1]
            with self.subTest(spelling=spelling):
                self.assertEqual(bool(row.get("argument")), operands != {"none"})
                self.assertEqual(bool(row.get("argument_optional")),
                                 any(operand.startswith("[") for operand in operands))
                if row.get("argument"):
                    expected = {"separate", "equals"} if spelling.startswith("--") else {"separate", "attached"}
                    self.assertLessEqual(expected, value_forms(row))
        for alias, owner in aliases.items():
            with self.subTest(alias=alias, owner=owner):
                category, row = menu[owner]
                view = option_text(profile, category, row)
                self.assertIn(alias, view.searchable)
                self.assertIn(alias, " ".join(view.details))

    def test_original_order_and_discovery_boundary(self):
        """Keep the original seventeen spellings and the fixed root discovery route."""
        original = (ROOT / "tests/fixtures/help/fzf.txt").read_text()
        baseline = re.findall(r"^  (--?[\w-]+)", original, re.MULTILINE)
        self.assertEqual(len(baseline), 17)
        profile = json.loads((ROOT / "profiles/fzf.json").read_text())
        retained = [row["flag"] for group in profile["categories"] for row in group["options"]
                    if row["flag"] in baseline]
        self.assertEqual(retained, baseline)
        registry = load_driver_registry(ROOT / "config/drivers.example")
        route = help_route("fzf", (), registry)
        self.assertEqual(route.arguments, ("--help",))
        self.assertEqual(route.manual, "fzf")
        self.assertTrue(route.stop_at_positional)
