"""Reconcile both extraction menus with the versioned manual and root-help inventories."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import HelpError, find_context


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def inventory_tables():
    """Collect menu declarations and excluded switch families from the independent inventory."""
    text = (ROOT / "docs/7zip-extraction-manual-inventory.md").read_text(encoding="utf-8")
    declarations, exclusions = text.split("## Grammar and excluded controls")
    rows = {}
    for line in declarations.splitlines():
        if line.startswith("| `-"):
            spelling, operand, releases, _ = line.strip("| ").split(" | ", 3)
            spelling = spelling.strip("`")
            if spelling in rows:
                raise AssertionError(f"Duplicate inventory row for {spelling}")
            rows[spelling] = (operand, releases)
    # A root-help declaration may use a grammar prefix such as -bs that has
    # several complete menu spellings, or a switch for another operation.
    families = set()
    for line in exclusions.splitlines():
        if line.startswith("| `"):
            names = line.split(" | ", 1)[0]
            families.update(re.findall(r"`(--help|-[a-z]+)", names))
    return rows, families


class ExtractionManualInventoryTests(unittest.TestCase):
    def test_menu_spellings_and_value_requirements(self):
        """Pin the full independent surface, including optional attachment and release notes."""
        inventory, _ = inventory_tables()
        for command in ("7z", "7zz"):
            profile = read_json(f"profiles/{command}-x.json")
            options = [row for category in profile["categories"] for row in category["options"]]
            self.assertCountEqual((row["flag"] for row in options), inventory.keys())
            for row in options:
                flag = row["flag"]
                operand, releases = inventory[flag]
                with self.subTest(command=command, flag=flag):
                    self.assertEqual(bool(row.get("argument")), operand != "none")
                    if operand != "none":
                        self.assertIn(operand, {"equals", "optional equals", "attached", "optional attached"})
                        self.assertEqual(value_forms(row), {"equals" if operand.endswith("equals") else "attached"})
                        self.assertEqual(row.get("argument_optional", False), operand.startswith("optional "))
                    if releases == "Upstream":
                        for version in ("26.01", "24.04", "26.04"):
                            self.assertIn(version, row["detail"])
                    elif releases == "Upstream effect":
                        self.assertIn("26.06", row["detail"])
                        self.assertIn("Ubuntu", row["detail"])
                    elif releases == "Resolute and upstream":
                        self.assertRegex(row["detail"], r"(?:Resolute|26\.00)")
                        self.assertRegex(row["detail"], r"(?:Noble|23\.01)")
                    else:
                        self.assertEqual(releases, "All")
            self.assertEqual([r["flag"] for r in options if r["flag"] in {"-o", "-t", "-y", "-bd"}],
                             ["-o", "-t", "-y", "-bd"])

    def test_each_captured_help_declaration_is_classified(self):
        """Account for both clients' switches, including help lines belonging to other commands."""
        inventory, exclusions = inventory_tables()
        captured = read_json("tests/fixtures/7zip-extraction/root-help.json")
        original = read_json("tests/fixtures/help/syntax-7zip-captured.json")
        self.assertEqual(captured["source_arguments"], ["-h"])
        pairs = {(item["executable"], item["release"]) for item in captured["captures"]}
        self.assertEqual(pairs, {("7z", "23.01"), ("7zz", "23.01"), ("7z", "26.00"),
                                 ("7zz", "26.00"), ("7zz", "26.06")})
        for capture in captured["captures"]:
            executable = capture["executable"]
            with self.subTest(executable=executable, release=capture["release"]):
                self.assertIn(capture["release"], capture["banner"])
                lines = captured["switch_tables"][capture["table"]]
                self.assertGreater(len(lines), 40)
                names = set()
                for line in lines:
                    match = re.match(r"\s*(--|-[a-z]+)", line)
                    self.assertIsNotNone(match, line)
                    names.add(match.group(1))
                self.assertFalse(names - inventory.keys() - exclusions)
                baseline = original[executable]
                self.assertEqual(baseline["source_arguments"], ["-h"])
                for flag in re.findall(r"^\s*(-[a-z]+)", baseline["text"], re.MULTILINE):
                    self.assertIn(flag, names)
                    self.assertIn(flag, inventory)

    def test_distinct_suffixes_preserve_archive_and_member_boundaries(self):
        """Mixed literal and attached switches must leave archive and member operands intact."""
        for command in ("7z", "7zz"):
            profile = read_json(f"profiles/{command}-x.json")
            for switches in ("-snl -snld3", "-snl- -snoi-", "-xtd -xtf '-xr!*.tmp'",
                             "-mmemuse=p60 -mmt2", "-mcp=437 -bso0", "-r0 -spm2 -spf2"):
                with self.subTest(command=command, switches=switches):
                    line = f"{command} x {switches} archive.zip 'dir/name.txt' "
                    ctx = find_context(line, len(line), [profile])
                    self.assertEqual(ctx.profile["command"], [command, "x"])
            line = f"{command} x archive.zip -- '-member' "
            with self.assertRaises(HelpError) as error:
                find_context(line, len(line), [profile])
            self.assertEqual(error.exception.code, "end_of_options")
