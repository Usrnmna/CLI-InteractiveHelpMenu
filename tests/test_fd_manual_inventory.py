"""Reconcile the finder menus with independent source inventories and fixed help."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from command_paths import help_route, load_driver_registry


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def manual_spellings():
    """Read the independent table of flag spellings, native operands and releases."""
    inventory = {}
    for line in (ROOT / "docs/fd-manual-inventory.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| `-"):
            names, operand, releases, _ = line.strip("| ").split(" | ", 3)
            for flag in re.findall(r"`(-[\w-]+)`", names):
                if flag in inventory:
                    raise AssertionError(f"Duplicate spelling in manual inventory: {flag}")
                inventory[flag] = (operand, releases)
    return inventory


# These spellings are declared outside the three help option lists, including
# aliases printed in prose and build-dependent flags declared in the parser.
SUPPLEMENTAL = {
    "--change-newer-than", "--change-older-than", "--changed-after", "--dereference",
    "--gen-completions", "--has-results", "--hyper", "--ignore", "--ignore-parent",
    "--ignore-vcs", "--literal", "--max-buffer-time", "--maxdepth", "--mindepth",
    "--mount", "--newer", "--no-follow", "--no-global-ignore-file", "--no-hidden",
    "--older", "--relative-path", "--require-git", "--xdev",
}
RELEASES = {
    "9.0.0": {"All"},
    "10.3.0": {"All", "10.3+"},
    "10.5.2": {"All", "10.3+", "10.5"},
}


class FinderManualInventoryTests(unittest.TestCase):
    def test_captured_declarations_and_release_specific_arity(self):
        """Account for every help heading and separate parser/manual-only spellings."""
        inventory = manual_spellings()
        evidence = read_json("tests/fixtures/fd-manual/root-help.json")
        self.assertEqual(evidence["request"], ["--help"])
        self.assertEqual(evidence["captures"].keys(), RELEASES.keys())
        for version, capture in evidence["captures"].items():
            expected = {flag: operand for flag, (operand, releases) in inventory.items()
                        if releases in RELEASES[version]}
            if version == "9.0.0":
                expected["--strip-cwd-prefix"] = "none"
            visible = set()
            for heading in capture["declarations"]:
                match = re.fullmatch(r"(?:(-\w), )?(--?[\w-]+)(.*)", heading)
                self.assertIsNotNone(match, heading)
                for flag in filter(None, match.groups()[:2]):
                    with self.subTest(version=version, flag=flag):
                        self.assertNotIn(flag, visible)
                        visible.add(flag)
                        operand = expected[flag]
                        syntax = match[3]
                        if operand == "none":
                            self.assertIn(syntax, ("", "...") if flag in ("-u", "--unrestricted") else ("",))
                        elif operand == "[=WHEN]":
                            self.assertEqual(syntax, "[=<when>]")
                        elif operand == "COMMAND...":
                            self.assertEqual(syntax, " <cmd>...")
                        else:
                            self.assertRegex(syntax, r"^ <[^>]+>$")
            self.assertEqual(visible, expected.keys() - SUPPLEMENTAL, version)

    def test_both_profiles_match_manual_spellings_and_native_value_forms(self):
        """The release union preserves the arity of each spelling including short suffixes."""
        inventory = manual_spellings()
        for command in ("fd", "fdfind"):
            profile = read_json(f"profiles/{command}.json")
            rows = [row for group in profile["categories"] for row in group["options"]]
            self.assertCountEqual(inventory.keys(), (row["flag"] for row in rows))
            for row in rows:
                flag = row["flag"]
                operand, _ = inventory[flag]
                with self.subTest(command=command, flag=flag):
                    self.assertEqual(bool(row.get("argument")), operand != "none")
                    self.assertEqual(bool(row.get("argument_optional")), operand.startswith("["))
                    if operand != "none":
                        forms = value_forms(row)
                        if operand == "[=WHEN]":
                            self.assertEqual(forms, {"equals"})
                        else:
                            self.assertIn("separate", forms)
                            if flag.startswith("--"):
                                self.assertIn("equals", forms)
                            else:
                                self.assertIn("attached", forms)

    def test_configured_routes_distinguish_finder_help_from_fdclone_manual(self):
        """The fixed executable request and manual lookup use independent identities."""
        registry = load_driver_registry(ROOT / "config/drivers.example")
        for command, manual in (("fd", None), ("fdfind", "fdfind")):
            route = help_route(command, (), registry)
            self.assertEqual(route.arguments, ("--help",))
            self.assertEqual(route.manual, manual)
            self.assertTrue(route.stop_at_positional)
            self.assertEqual(set(route.stop_at_options), {"-x", "--exec", "-X", "--exec-batch"})

    def test_original_selectable_spellings_still_insert_in_order(self):
        """Retain the order of the independent 19-spelling documentation specimens."""
        specimens = read_json("tests/fixtures/help/expansion-systems-captured.json")
        for command in ("fd", "fdfind"):
            original = specimens[command]
            self.assertEqual(original["kind"], "documented-fixture")
            old = re.findall(r"^  (-[\w-]+)", original["text"], re.MULTILINE)
            self.assertEqual(len(old), 19)
            profile = read_json(f"profiles/{command}.json")
            ordered = [row["flag"] for group in profile["categories"] for row in group["options"]]
            self.assertEqual([flag for flag in ordered if flag in old], old)
