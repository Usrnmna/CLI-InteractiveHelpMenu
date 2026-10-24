"""Regressions derived from isolated distribution and upstream help captures."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option


class SystemDependencyFollowupTests(unittest.TestCase):
    def test_installed_leaf_help_provenance_and_curated_flags(self):
        fixture_root = ROOT / "tests/fixtures/help/followup-systems"
        evidence = json.loads((fixture_root / "manifest.json").read_text())
        expected = {"podman run", "podman build", "podman exec", "podman logs", "psql",
                    "yq eval", "fd", "fdfind", "fzf", "ansible-playbook", "esptool write-flash",
                    "esptool.py write-flash", "esptool.py write_flash"}
        self.assertEqual(set(evidence), expected)
        for command, record in evidence.items():
            with self.subTest(command=command):
                self.assertTrue(record["source_url"].startswith("https://"))
                self.assertTrue(record["version"])
                self.assertEqual(record["request"], command.split() + ["--help"])
                self.assertEqual(record["returncode"], 0)
                text = (fixture_root / record["file"]).read_text()
                profile = self.profile(command.replace(" ", "-"))
                for category in profile["categories"]:
                    for option in category["options"]:
                        pattern = r"(?<![\w-])" + re.escape(option["flag"].rstrip("=")) + r"(?![\w-])"
                        self.assertRegex(text, pattern)

    def profile(self, name):
        return json.loads((ROOT / "profiles" / (name + ".json")).read_text())

    def context(self, text, profile):
        return find_context(text, len(text), [profile],
                            driver_registry=load_driver_registry(ROOT / "config/drivers.example"))

    def test_podman_pull_policy_is_optional_and_context_stays_positional(self):
        profile = self.profile("podman-build")
        options = {option["flag"]: option for category in profile["categories"]
                   for option in category["options"]}
        self.assertTrue(options["--pull"]["argument_optional"])
        self.assertEqual(options["--pull"]["argument"], "POLICY")
        for text in ("podman build --pull ", "podman build --pull=never "):
            context = self.context(text, profile)
            edited = text + "--quiet "
            self.assertEqual(insert_option(context, options["--quiet"]), (edited, len(edited)))
        for text in ("podman build --pull . ", "podman build --pull=never 'café 日本' "):
            with self.assertRaisesRegex(HelpError, "positional"):
                self.context(text, profile)

    def test_fzf_short_multi_alias_preserves_optional_value_forms(self):
        profile = self.profile("fzf")
        options = {option["flag"]: option for category in profile["categories"]
                   for option in category["options"]}
        self.assertEqual(options["-m"]["argument"], "MAX")
        self.assertTrue(options["-m"]["argument_optional"])
        self.assertTrue(options["-m"]["attached"])
        for text in ("fzf -m ", "fzf -m2 ", "fzf -m 2 ", "fzf --multi=2 ",
                     "fzf --multi 2 ", "fzf -m --query 'café 日本' "):
            context = self.context(text, profile)
            edited = text + "--exact "
            self.assertEqual(insert_option(context, options["--exact"]), (edited, len(edited)))
        with self.assertRaisesRegex(HelpError, "argument|value"):
            self.context("fzf -m2", profile)


if __name__ == "__main__":
    unittest.main()
