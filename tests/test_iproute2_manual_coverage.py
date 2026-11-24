"""Check the independent iproute2 manual inventory and versioned package help."""

import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/iproute2"
MENUS = ("ip-address", "ip-link", "ip-route", "ss")


def read_inventory():
    """Expand the reviewed spelling groups into distinct menu insertion contracts."""
    entries = {name: {} for name in MENUS}
    with (FIXTURES / "manual-inventory.tsv").open() as stream:
        for line in csv.DictReader(stream, delimiter="\t"):
            for flag in line["spellings"].split():
                options = entries[line["menu"]]
                if flag in options:
                    raise ValueError(f"Duplicate inventory spelling: {line['menu']} {flag}")
                options[flag] = (line["operand"], line["releases"])
    return entries


class Iproute2CoverageTests(unittest.TestCase):
    def test_listing_keywords_and_socket_options_match_manual_inventory(self):
        """Require every exact insertion, value boundary and declared optional argument."""
        for menu, expected in read_inventory().items():
            profile = json.loads((ROOT / "profiles" / (menu + ".json")).read_text())
            actual = {}
            for category in profile["categories"]:
                for opt in category["options"]:
                    arg = opt.get("argument") or "-"
                    if opt.get("argument_optional"):
                        arg = f"[{arg}]"
                    actual[opt["flag"]] = arg
            with self.subTest(menu=menu):
                self.assertEqual(actual, {flag: arg for flag, (arg, _) in expected.items()})
                self.assertTrue(profile["stop_at_positional"])

    def test_ss_packaged_help_agrees_with_release_inventory(self):
        """Check the independently captured short/long socket parser surface per release."""
        inventory = read_inventory()["ss"]
        for name, release in (("noble", "N"), ("resolute", "R")):
            captures = (FIXTURES / (name + "-ss-help.txt")).read_text().splitlines()
            spellings = set()
            for line in captures:
                if line.lstrip().startswith("-"):
                    options = re.split(r"\s{2,}", line.strip(), maxsplit=1)[0]
                    spellings.update(re.findall(r"(?<![\w-])--?[A-Za-z0-9][A-Za-z0-9-]*", options))
            # -v is accepted by both clients as an unadvertised alias of -V.
            expected = {flag.rstrip("=") for flag, (_, releases) in inventory.items()
                        if release in releases and flag != "-v"}
            with self.subTest(release=name):
                self.assertEqual(spellings, expected)
