"""Compare the Bun, Ruff and pytest menus to separately recorded versioned declarations."""

import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from core import HelpError, find_context, insert_option


def declarations(menu):
    """Read the union of published spellings and keep each release's parser arity."""
    family = menu.split("-")[0]
    path = ROOT / "tests/fixtures" / family / (menu + "-declarations.tsv")
    result = {}
    with path.open() as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for flag in row["spellings"].split():
                versions = result.setdefault(flag, {})
                if row["release"] in versions:
                    raise ValueError(f"Duplicate {menu} {flag} in {row['release']}")
                versions[row["release"]] = row["operand"]
    return result


def profile(menu):
    """Read one bundled declaration and index its literal selections."""
    data = json.loads((ROOT / "profiles" / (menu + ".json")).read_text())
    return data, {opt["flag"]: opt for category in data["categories"] for opt in category["options"]}


class DevtoolsManualInventoryTests(unittest.TestCase):
    def test_every_versioned_spelling_and_operand(self):
        for menu in ("bun-run", "ruff-check", "ruff-format", "pytest"):
            _, rows = profile(menu)
            inventory = declarations(menu)
            with self.subTest(menu=menu):
                self.assertEqual(rows.keys(), inventory.keys())
            for flag, versions in inventory.items():
                with self.subTest(menu=menu, flag=flag):
                    opt = rows[flag]
                    arity = "optional" if opt["argument_optional"] else "required" if opt["argument"] else "none"
                    self.assertEqual(arity, list(versions.values())[-1])
                    if len(set(versions.values())) > 1:
                        self.assertEqual((menu, flag), ("ruff-check", "--add-noqa"))
                        self.assertIn("0.11.13", opt["detail"])

    def test_bun_child_and_optional_ruff_operand(self):
        bun, options = profile("bun-run")
        for suffix in (" task --watch", " -- task --watch"):
            line = "bun run" + suffix
            with self.assertRaises(HelpError):
                find_context(line, len(line), [bun])
        ruff, rows = profile("ruff-check")
        line = "ruff check  'demo file.py'"
        context = find_context(line, len("ruff check "), [ruff])
        self.assertEqual(insert_option(context, rows["--add-noqa"]),
                         ("ruff check --add-noqa= 'demo file.py'", len("ruff check --add-noqa=")))
        self.assertTrue(options["--inspect"]["argument_optional"])

    def test_pytest_path_and_plugin_boundaries(self):
        data, rows = profile("pytest")
        line = "pytest 'tests/test_cli.py::test_case[two words]' --"
        self.assertEqual(find_context(line, len(line), [data]).query, "--")
        self.assertFalse({"--cov", "--numprocesses", "--reruns"} & rows.keys())
        self.assertTrue(rows["--debug"]["argument_optional"])
        self.assertTrue(rows["--cache-show"]["argument_optional"])
