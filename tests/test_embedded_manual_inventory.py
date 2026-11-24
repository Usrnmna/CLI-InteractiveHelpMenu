"""Check the public esptool and Arduino compile declarations against the menus."""

import csv
import json
import re
import unittest

from test_expansion_systems import ROOT, context_for, options_for, profile_for
from core import HelpError, insert_option
from value_semantics import validate_profile_semantics


FIXTURES = ROOT / "tests/fixtures/embedded-manual"
ESP_ROUTES = ("esptool.py write_flash", "esptool.py write-flash", "esptool write-flash")


def inventory(name):
    """Read a versioned parser or fixed-help transcription independent of the profiles."""
    with (FIXTURES / name).open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


class EmbeddedManualInventoryTests(unittest.TestCase):
    def test_esp_public_declarations_and_alias_arities_match_each_guard(self):
        declarations = inventory("esptool-options.tsv")
        for cmd in ESP_ROUTES:
            profile = profile_for(cmd)
            options = options_for(profile)
            major = "4" if cmd.endswith("write_flash") else "5"
            expected = set()
            with self.subTest(command=cmd):
                self.assertEqual(profile["identity"], "esptool-v" + major)
                for item in declarations:
                    if not any(v.startswith(major + ".") for v in item["releases"].split(",")):
                        continue
                    names = item["spellings"].split()
                    if item["visibility"] == "hidden":
                        self.assertTrue(options.keys().isdisjoint(names))
                        continue
                    expected.update(names)
                    slots = int(item["operand_slots"].rstrip("+"))
                    for flag in names:
                        row = options[flag]
                        self.assertEqual(row.get("argument_count", 1) if row["argument"] else 0, slots, flag)
                        self.assertFalse(row["argument_optional"], flag)
                        self.assertIn("detail", row)
                        for alias in names:
                            if alias != flag:
                                self.assertIn(alias, row["detail"])
                        if slots:
                            self.assertIn("value_semantics", row)
                self.assertEqual(options.keys(), expected)
                self.assertEqual(len(options), 23 if major == "4" else 27)
                self.assertFalse(validate_profile_semantics(profile, mode="maintained"))
        self.assertEqual(profile_for(ESP_ROUTES[1])["categories"], profile_for(ESP_ROUTES[2])["categories"])

    def test_esp_legacy_spelling_and_verification_are_version_qualified(self):
        legacy = options_for(profile_for(ESP_ROUTES[0]))
        for term in ("4.7.0", "4.12.0", "no longer"):
            self.assertIn(term, legacy["--verify"]["detail"])
        for cmd in ESP_ROUTES[1:]:
            options = options_for(profile_for(cmd))
            for flag in ("--flash-mode", "--flash-freq", "--flash-size"):
                self.assertIn(flag.replace("flash-", "flash_"), options[flag]["detail"])
            for term in ("5.2.0", "5.3.0", "--trust-flash-content"):
                self.assertIn(term, options["--no-diff-verify"]["detail"])
            self.assertIn("--diff-with", options["--trust-flash-content"]["detail"])
            self.assertNotIn("--verify", options)

    def test_arduino_help_types_and_inherited_scope(self):
        profile = profile_for("arduino-cli compile")
        options = options_for(profile)
        scopes = {row["flag"]: category["name"] for category in profile["categories"] for row in category["options"]}
        captures = json.loads((ROOT / "tests/fixtures/help/runtime-followup-captured.json").read_text(encoding="utf-8"))
        help_text = next(entry["output"] for entry in captures["captures"] if entry["command"] == "arduino-cli compile")
        expected = set()
        for decl in inventory("arduino-compile-options.tsv"):
            names = decl["spellings"].split()
            operand_type = decl["helptype"]
            expected.update(names)
            for flag in names:
                with self.subTest(flag=flag):
                    row = options[flag]
                    self.assertRegex(help_text, r"(?<![\w-])" + re.escape(flag) + r"(?![\w-])")
                    self.assertEqual(scopes[flag] == "Inherited options", decl["scope"] == "global")
                    self.assertEqual(bool(row["argument"]), operand_type != "none")
                    self.assertEqual(row["argument_optional"], operand_type.startswith('string[='))
                    if operand_type != "none":
                        self.assertIn("value_semantics", row)
                    for alias in set(names) - {flag}:
                        self.assertIn(alias, row["detail"])
        self.assertEqual(options.keys(), expected)
        self.assertEqual(len(expected), 50)
        self.assertFalse(validate_profile_semantics(profile, mode="maintained"))

    def test_arduino_optional_equals_and_quoted_directory_boundaries(self):
        profile = profile_for("arduino-cli compile")
        options = options_for(profile)
        prefix = "arduino-cli compile --build-path 'café dir' "
        suffix = " 'sketch folder'"
        context = context_for(prefix + "--sh" + suffix, len(prefix + "--sh"), profile)
        self.assertEqual(insert_option(context, options["--show-properties"]),
                         (prefix + "--show-properties=" + suffix, len(prefix + "--show-properties=")))
        line = prefix + "--show-properties=unexpanded --"
        self.assertEqual(context_for(line, len(line), profile).query, "--")
        with self.assertRaises(HelpError):
            context_for(prefix + "--build-path ", len(prefix + "--build-path "), profile)
        self.assertIn("--upload", options["--verify"]["detail"])
        self.assertIn("pre* hooks", options["--only-compilation-database"]["detail"])
