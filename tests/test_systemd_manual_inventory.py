"""Check systemd menu membership, spelling and arity against the reviewed ledgers."""

import csv
import re
import unittest

from test_expansion_systems import ROOT, options_for, profile_for


FIXTURES = ROOT / "tests/fixtures/systemd"
NOBLE = ROOT / "tests/fixtures/help/expansion-system-captures"
COMMANDS = ("systemctl list-units", "systemctl show", "systemctl status", "journalctl")


def declarations(capture):
    """Read the leading usage column, including separate -P NAME and optional values."""
    found = {}
    for line in capture.splitlines():
        if not line.lstrip().startswith("-"):
            continue
        usage = re.split(r"\s{2,}", line.lstrip(), maxsplit=1)[0]
        flags = re.findall(r"(?:^| )(--?[A-Za-z][\w-]*)", usage)
        optional = "[=" in usage
        required = "=" in usage or bool(re.search(r" [A-Z][A-Z_]+$", usage))
        for flag in flags:
            found[flag] = "optional" if optional else "required" if required else "no"
    return found


def inventory(tool):
    """Load the manual, package and parser presence columns for one executable."""
    with (FIXTURES / (tool + "-inventory.tsv")).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


class SystemdManualInventoryTests(unittest.TestCase):
    def test_all_reviewed_spellings_and_operand_contracts(self):
        for command in COMMANDS:
            tool, *verbs = command.split()
            route = verbs[0] if verbs else tool
            expected = {r["spelling"]: r["operand"] for r in inventory(tool)
                        if route in r["menus"].split(",")}
            profile = profile_for(command)
            observed = {}
            for category in profile["categories"]:
                for row in category["options"]:
                    spelling = row["flag"].rstrip("=")
                    with self.subTest(command=command, spelling=spelling):
                        self.assertNotIn(spelling, observed)
                        if row.get("argument"):
                            self.assertIn("value_semantics", row)
                            if spelling.startswith("--"):
                                self.assertTrue(row["flag"].endswith("="))
                            else:
                                self.assertTrue(row["attached"])
                    observed[spelling] = ("optional" if row.get("argument_optional")
                                          else "required" if row.get("argument") else "no")
            with self.subTest(command=command):
                self.assertEqual(expected, observed)

    def test_captured_help_and_per_release_membership(self):
        for tool in ("journalctl", "systemctl"):
            items = inventory(tool)
            self.assertEqual(len(items), len({row["spelling"] for row in items}))
            for index, path in enumerate((NOBLE / (tool + ".txt"), FIXTURES / ("259-" + tool + "-help.txt"))):
                observed = declarations(path.read_text(encoding="utf-8"))
                expected = {row["spelling"]: row["operand"] for row in items
                            if row["help_255_259"][index] == "Y"}
                with self.subTest(tool=tool, source=path):
                    self.assertEqual(expected, observed)
                    self.assertTrue(all(row["parser_255_259_262"][index] == "Y" for row in items
                                        if row["manual_255_259_262"][index] == "Y" or
                                        row["help_255_259"][index] == "Y"))

    def test_command_boundaries_and_compatibility_spellings(self):
        original = ["--user", "--system", "--no-pager", "--no-legend", "--full", "--all",
                    "--type=", "--state=", "--plain", "--lines=", "--output="]
        for command in COMMANDS[:3]:
            options = options_for(profile_for(command))
            first = original + (["--property=", "--value"] if command.endswith("show") else [])
            self.assertEqual(list(options)[:len(first)], first)
            for unrelated in ("--job-mode=", "--kill-whom=", "--show-types", "--stdin", "--now", "-."):
                self.assertNotIn(unrelated, options)
            self.assertIn("Ubuntu 24.04", options["--capsule="]["detail"])
            self.assertIn("262", options["--introspect-cli"]["detail"])
        journal = options_for(profile_for("journalctl"))
        self.assertFalse(journal["-I"].get("argument"))
        self.assertTrue(journal["--invocation="]["argument"])
        self.assertIn("cat", journal["--exclude-identifier="]["detail"])
        self.assertIn("Ubuntu 24.04", journal["-i"]["detail"])
        self.assertIn("checkpoint", journal["--cursor-file="]["detail"])
