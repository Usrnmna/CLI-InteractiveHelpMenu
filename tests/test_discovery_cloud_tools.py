"""Check the cloud and embedded fixed replies against independently reviewed declarations."""

import json
import lzma
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from discovery import build_profile

FIXTURES = ROOT / "tests/fixtures/discovery-tiers"
CASES = json.loads((FIXTURES / "cloud.json").read_text())


def profile_for(command, record=None):
    """Reconstruct a discovery profile from this command's help and manual responses."""
    sources = []
    for item in (record or CASES[command])["sources"]:
        if item.get("identity"):
            continue
        path = FIXTURES / item["file"]
        text = lzma.decompress(path.read_bytes()).decode() if path.suffix == ".xz" else path.read_text()
        sources.append((" ".join(item["argv"]), text))
    return build_profile(command.split(), sources)


def rows_for(command):
    """Index the independently selectable rows by their literal spellings."""
    return {row["flag"]: row for category in profile_for(command)["categories"] for row in category["options"]}


class CloudToolDiscoveryTests(unittest.TestCase):
    def test_entire_native_inventories(self):
        for command, case in CASES.items():
            with self.subTest(command=command):
                actual = {name: row.get("argument_count", 1) if row["argument"] else 0
                          for name, row in rows_for(command).items()}
                self.assertEqual(actual, case["options"])

    def test_aws_native_manual_distinguishes_version_and_symlink_switches(self):
        rows = rows_for("aws s3 cp")
        self.assertFalse(rows["--version"]["argument"])
        self.assertIn("without taking an operand", rows["--version"]["detail"])
        self.assertIn("Skip symbolic links", rows["--no-follow-symlinks"]["summary"])
        self.assertTrue(rows["--cli-read-timeout"]["argument"])
        self.assertTrue(rows["--sse-c"]["argument_optional"])
        self.assertIn("[--grants <value> [<value>...]]", rows["--grants"]["detail"])

    def test_resolute_aws_title_case_manual_has_the_complete_distribution_set(self):
        records = json.loads((FIXTURES / "cloud-captures/aws-resolute.json").read_text())
        for name, record in records.items():
            with self.subTest(command=name):
                profile = profile_for(name, record)
                actual = {row["flag"]: row.get("argument_count", 1) if row["argument"] else 0
                          for category in profile["categories"] for row in category["options"]}
                self.assertEqual(actual, record["options"])
                self.assertIn("--no-cli-pager", actual)
                self.assertNotIn("--v2-debug", actual)

    def test_optional_cobra_values_are_attached(self):
        for command, flag, default in (("helm install", "--wait", "watcher"),
                                       ("helm upgrade", "--dry-run", "unset"),
                                       ("arduino-cli compile", "--show-properties", "expanded")):
            with self.subTest(command=command):
                row = rows_for(command)[flag]
                self.assertTrue(row["argument_optional"])
                self.assertEqual(row["argument_style"], "equals")
                self.assertIn(default, row["detail"])

    def test_azure_colon_table_inherits_required_argument_on_alias(self):
        rows = rows_for("az storage blob list")
        for name in ("--container-name", "-c"):
            self.assertIn("Required for this command", rows[name]["detail"])
            self.assertTrue(rows[name]["argument"])
        self.assertFalse(rows["--show-next-marker"]["argument"])
        self.assertIn("AZURE_STORAGE_AUTH_MODE", rows["--auth-mode"]["detail"])

    def test_google_global_index_respects_leaf_ownership(self):
        categories = {row["flag"]: category["name"] for category in profile_for("gcloud storage ls")["categories"]
                      for row in category["options"]}
        self.assertNotIn("--format", categories)
        self.assertNotEqual(categories["--format="], "GCLOUD WIDE FLAGS")
        self.assertEqual(categories["--project="], "GCLOUD WIDE FLAGS")
        self.assertNotIn("-q", categories)
        self.assertNotIn("--region", rows_for("gcloud config list"))

    def test_esptool_does_not_insert_a_truncated_rich_cell(self):
        name = "esptool write-flash"
        path = ROOT / "tests/fixtures/help/followup-systems/esptool-write-flash.txt"
        profile = build_profile(name.split(), [("80-column capture", path.read_text())])
        narrow_rows = {row["flag"] for category in profile["categories"] for row in category["options"]}
        self.assertFalse(any(flag.startswith("--ignore-flash") for flag in narrow_rows))
        rows = rows_for(name)
        self.assertIn("--ignore-flash-enc-efuse", rows)
        self.assertEqual(rows["--encrypt-files"]["argument_count"], 2)
        self.assertIn("ESP32-S3", rows["-sc"]["detail"])
