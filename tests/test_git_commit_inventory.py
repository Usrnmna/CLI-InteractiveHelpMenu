"""Compare the bundled commit options with the manual table and fixed Git usage."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import HelpError, find_context, insert_option, validate_profile


def manual_entries():
    """Read the independent manual spelling, operand and release declarations."""
    document = (ROOT / "docs/git-commit-manual-inventory.md").read_text()
    entries = {}
    for line in document.split("## Coverage and ownership", 1)[0].splitlines():
        if not line.startswith("| `"):
            continue
        names, operand, releases, _ = line.strip("| ").split(" | ")
        for name in re.findall(r"`([^`]+)`", names):
            if name in entries:
                raise ValueError(f"Duplicate manual spelling {name}")
            entries[name] = (operand, releases)
    return entries


def usage_flags(usage):
    """Expand negatable spellings from fixed help declarations, omitting synopsis prose."""
    flags = set()
    for line in usage.splitlines():
        if not line.startswith("    -"):
            continue
        declaration = re.split(r"\s{2,}", line.strip(), maxsplit=1)[0]
        for prefix, name, short in re.findall(r"--(\[no-\])?([a-z][a-z-]*)|(-[A-Za-z])", declaration):
            if short:
                flags.add(short)
            else:
                flags.add("--" + name)
                if prefix:
                    flags.add("--no-" + name)
    return flags


class CommitInventoryTests(unittest.TestCase):
    def setUp(self):
        """Load the current public profile without command discovery."""
        path = ROOT / "profiles/git-commit.json"
        self.profile = json.loads(path.read_text())
        validate_profile(self.profile, path)
        self.rows = [row for category in self.profile["categories"] for row in category["options"]]

    def test_manual_spellings_required_and_optional_operands(self):
        expected = manual_entries()
        self.assertCountEqual((row["flag"] for row in self.rows), expected.keys())
        for row in self.rows:
            flag = row["flag"]
            operand, _ = expected[flag]
            with self.subTest(flag=flag):
                optional = operand.startswith("optional ")
                self.assertEqual(row.get("argument_optional", False), optional)
                if operand == "none":
                    self.assertFalse(row.get("argument"))
                else:
                    self.assertEqual(row["argument"], operand.removeprefix("optional "))
                    self.assertIn("value_semantics", row)
                    if flag.startswith("--"):
                        forms = {"equals"} if optional else {"equals", "separate"}
                    else:
                        forms = {"attached"} if optional else {"attached", "separate"}
                    self.assertEqual(value_forms(row), forms)

    def test_usage_declarations_for_each_packaged_release(self):
        """Every fixed-help spelling belongs to a released row or a known usage omission."""
        expected = manual_entries()
        for release in ("noble", "resolute"):
            path = ROOT / "tests/fixtures/git-commit-log" / (release + "-usage.json")
            capture = json.loads(path.read_text())["usage"]["commit"]
            self.assertEqual(capture["argv"], ["git", "commit", "-h"])
            self.assertEqual(capture["status"], 129)
            flags = usage_flags(capture["stdout"] + capture["stderr"])
            release_flags = {flag.rstrip("=") for flag, (_, releases) in expected.items()
                             if release == "resolute" or releases != "Resolute/upstream"}
            omitted = {"-h", "--help-all", "--help", "--allow-empty", "--allow-empty-message",
                       "--no-allow-empty", "--no-allow-empty-message"}
            with self.subTest(release=release):
                self.assertEqual(release_flags - omitted, flags)

    def test_original_commit_literals_order_and_cursor(self):
        """All nine existing edits retain their relative order and exact end position."""
        originals = ["--message", "--file", "--edit", "--all", "--patch", "--amend",
                     "--dry-run", "--verbose", "--short"]
        prefix, suffix = "git commit ", ' "quoted suffix"'
        context = find_context(prefix + suffix, len(prefix), [self.profile])
        original_rows = [row for row in self.rows if row["flag"] in originals]
        self.assertEqual([row["flag"] for row in original_rows], originals)
        for row in original_rows:
            flag = row["flag"]
            with self.subTest(flag=flag):
                self.assertEqual(insert_option(context, row), (prefix + flag + suffix, len(prefix + flag) + 1))

    def test_completed_short_bundles_keep_value_and_path_boundaries(self):
        """Required short operands can finish a cluster or use the next word."""
        for preceding in ("-am 'two words'", "-amTEXT", "-vv", "-mTEXT", "-qF 'message file'",
                          "-aCHEAD", "-uno", "-SKEY"):
            with self.subTest(preceding=preceding):
                line = "git commit " + preceding + " --sh"
                self.assertEqual(find_context(line, len(line), [self.profile]).query, "--sh")
        for preceding, reason in (("-am", "option_value_required"), ("-vv --", "end_of_options"),
                                  ("-am 'text' -- 'a path'", "end_of_options")):
            with self.subTest(preceding=preceding):
                line = "git commit " + preceding + " --sh"
                with self.assertRaises(HelpError) as raised:
                    find_context(line, len(line), [self.profile])
                self.assertEqual(raised.exception.code, reason)
