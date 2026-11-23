"""Reconcile log menu declarations against the three-release manual inventory."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import HelpError, find_context


class LogManualInventoryTests(unittest.TestCase):
    def test_manual_spellings_operands_and_release_details(self):
        """Check each literal, accepted operand forms and qualified release against its row."""
        profile = json.loads((ROOT / "profiles/git-log.json").read_text(encoding="utf-8"))
        options = [o for cat in profile["categories"] for o in cat["options"]]
        rows = {o["flag"]: o for o in options}
        inventory = (ROOT / "docs/git-log-manual-inventory.md").read_text(encoding="utf-8")
        table = inventory.split("## Selectable inventory", 1)[1].split("## Release", 1)[0]
        encountered = []
        for line in table.splitlines():
            if not line.startswith("| `-"):
                continue
            names, operand, syntax, releases, _effect = line.strip("| ").split(" | ")
            for flag in re.findall(r"`([^`]+)`", names):
                encountered.append(flag)
                with self.subTest(flag=flag):
                    row = rows[flag]
                    if releases == "2.56 only":
                        self.assertIn("2.56", row["detail"])
                        self.assertIn("Ubuntu", row["detail"])
                    elif releases == "Resolute and upstream":
                        self.assertIn("24.04", row["detail"])
                    else:
                        self.assertEqual(releases, "All")
                    if operand == "—":
                        self.assertFalse(row.get("argument"))
                        continue
                    short = not flag.startswith("--")
                    optional = syntax in ("optional =", "short attached, long =")
                    self.assertEqual(row.get("argument_optional", False), optional)
                    placeholder = operand.strip("`")
                    if flag in ("--stat", "--decorate"):
                        # These original rows insert a bare flag. Their optional
                        # operand never consumes a following revision or path.
                        self.assertEqual(row["argument"], "[=" + placeholder + "]")
                        for option in (flag, flag + "=VALUE"):
                            line = "git log " + option + " -- path "
                            with self.assertRaises(HelpError) as error:
                                find_context(line, len(line), [profile])
                            self.assertEqual(error.exception.code, "end_of_options")
                        self.assertTrue(row.get("value_semantics"))
                        continue
                    if optional and short:
                        placeholder = "[" + placeholder + "]"
                    self.assertEqual(row["argument"], placeholder)
                    if optional:
                        forms = {"attached"} if short else {"equals"}
                    elif syntax == "= only":
                        forms = {"equals"}
                    elif short:
                        self.assertIn(syntax, ("attached or separate",
                                              "short attached or separate, long = or separate"))
                        forms = {"attached", "separate"}
                    else:
                        self.assertIn(syntax, ("= or separate",
                                              "short attached or separate, long = or separate"))
                        forms = {"equals", "separate"}
                    self.assertEqual(value_forms(row), forms)
                    self.assertTrue(row.get("value_semantics"))
        self.assertCountEqual(encountered, [o["flag"] for o in options])
        self.assertEqual(len(options), len(rows))
        self.assertEqual([row["flag"] for row in options if row.get("numeric_shorthand")], ["-n"])

    def test_short_bundles_respect_the_git_parser_boundary(self):
        """Accept diff-only bundles and keep mixed log, revision and diff stages separate."""
        profile = json.loads((ROOT / "profiles/git-log.json").read_text(encoding="utf-8"))
        for spelling in ("-pu", "-pR", "-Rp", "-pGexample", "-zS example",
                         "-q -p", "-q -L1,1:tracked", "-p -U0"):
            with self.subTest(spelling=spelling):
                line = "git log " + spelling + " "
                self.assertEqual(find_context(line, len(line), [profile]).profile["command"], ["git", "log"])
        for spelling in ("-pq", "-pL1,1:tracked", "-gp", "-pg"):
            with self.subTest(spelling=spelling):
                line = "git log " + spelling + " "
                with self.assertRaises(HelpError) as error:
                    find_context(line, len(line), [profile])
                self.assertEqual(error.exception.code, "unsupported_option")

    def test_fixed_usage_and_versioned_discovery_capture(self):
        """Every option in both packages' short usage and the existing man excerpt is accounted for."""
        profile = json.loads((ROOT / "profiles/git-log.json").read_text(encoding="utf-8"))
        flags = {row["flag"].rstrip("=") for c in profile["categories"] for row in c["options"]}
        for release in ("noble", "resolute"):
            path = ROOT / "tests/fixtures/git-commit-log" / f"{release}-usage.json"
            usage = json.loads(path.read_text(encoding="utf-8"))["usage"]["log"]
            self.assertEqual((usage["argv"], usage["status"], usage["stderr"]),
                             (["git", "log", "-h"], 129, ""))
            declarations = []
            for line in usage["stdout"].splitlines():
                if not line.startswith("    -"):
                    continue
                heading = re.split(r"\s{2,}", line.strip(), maxsplit=1)[0]
                for negated, name, short in re.findall(r"--(\[no-\])?([\w-]+)|(?<!-)-([a-zA-Z])\b", heading):
                    declarations.append("-" + short if short else "--" + name)
                    if negated:
                        declarations.append("--no-" + name)
            self.assertIn("-L", declarations)
            self.assertFalse(set(declarations) - flags)
        capture = json.loads((ROOT / "tests/fixtures/help/captured.json").read_text())["git log"]
        self.assertEqual(capture["version"], "git version 2.43.0")
        for spelling in ("-<number>", "-n", "--max-count", "--all", "--oneline"):
            self.assertIn(spelling, capture["text"])
            if spelling != "-<number>":
                self.assertIn(spelling, flags)
