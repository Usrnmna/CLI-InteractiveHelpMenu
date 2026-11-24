"""Compare the maintained eval route with the pinned upstream flag listings."""

import json
import re
import unittest

from test_expansion_systems import ROOT, context_for, options_for, profile_for
from core import HelpError


FIXTURES = ROOT / "tests/fixtures/yq"
HEADER = re.compile(r"^  (?:(-\w), |    )(--[\w-]+)(?: (int|string|char))?  +", re.M)


def declarations(capture):
    """Read long and short spellings from Cobra's fixed-width flag declarations."""
    flags = {}
    for short, long, operand in HEADER.findall(capture):
        flags[long] = bool(operand)
        if short:
            flags[short] = bool(operand)
    return flags


class YqInventoryTests(unittest.TestCase):
    def test_release_help_and_deprecated_spellings(self):
        profile = profile_for("yq eval")
        options = options_for(profile)
        previous = declarations((FIXTURES / "4.44.3-eval-help.txt").read_text())
        current = declarations((FIXTURES / "4.54.3-eval-help.txt").read_text())
        self.assertEqual((len(previous), len(current)), (55, 67))
        self.assertEqual(previous, {key: current[key] for key in previous})
        current.update({"--tojson": False, "-j": False})
        self.assertEqual({flag: bool(row["argument"]) for flag, row in options.items()}, current)
        self.assertEqual(sum(len(c["options"]) for c in profile["categories"]), len(current))
        for flag in current.keys() - previous.keys() - {"-j", "--tojson"}:
            self.assertIn("absent in 4.44.3", options[flag]["detail"])
        for alias, long, _ in HEADER.findall((FIXTURES / "4.54.3-eval-help.txt").read_text()):
            if alias:
                self.assertIn(alias, options[long]["detail"])
                self.assertIn(long, options[alias]["detail"])

    def test_historical_capture_provenance_and_first_pass_order(self):
        old = ROOT / "tests/fixtures/help"
        source = json.loads((old / "followup-systems/manifest.json").read_text())["yq eval"]
        self.assertIn("v4.54.1", source["version"])
        captured = declarations((old / "followup-systems" / source["file"]).read_text())
        current = declarations((FIXTURES / "4.54.3-eval-help.txt").read_text())
        self.assertEqual(current.keys() - captured.keys(), {
            "--ini-key-value-delimiters", "--security-allow-write-any-path",
            "--security-force-never-escape-shell-output"})
        self.assertEqual(captured, {key: current[key] for key in captured})
        original = re.findall(r"^  ([-\w]+)", (old / "yq-eval.txt").read_text(), re.M)
        self.assertEqual(len(original), 15)
        self.assertEqual(list(options_for(profile_for("yq eval")))[:15], original)

    def test_query_operands_and_first_positional_boundary(self):
        profile = profile_for("yq eval")
        for arguments in ("--from-file 'my rule.yq'", "--from-file=rule.yq",
                          "-I4", "-I 4", "-fprocess", "-s '.name'",
                          """--expression '.value == "--inplace"'"""):
            line = "yq eval " + arguments + " --"
            with self.subTest(line=line):
                context_for(line, len(line), profile)
        for operand in ("first.yml", """'.value == "--from-file"'""", "--"):
            line = "yq eval " + operand + " --"
            with self.subTest(line=line), self.assertRaises(HelpError):
                context_for(line, len(line), profile)
