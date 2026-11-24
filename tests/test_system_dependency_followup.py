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
                if command in {"fd", "fdfind"}:
                    # The historical installed captures and the new Noble run describe
                    # the same release. Newer releases and hidden aliases have separate
                    # versioned coverage in test_fd_manual_inventory.
                    self.assertEqual(record["version"], "fdfind 9.0.0")
                    captures = json.loads((ROOT / "tests/fixtures/fd-manual/root-help.json").read_text())
                    headers = re.findall(r"^ {2,6}(-[\w-].*)$", text.split("Options:", 1)[1], re.MULTILINE)
                    self.assertEqual(headers, captures["captures"]["9.0.0"]["declarations"])
                    continue
                if command == "podman run":
                    self.assert_podman_run_coverage(text, profile)
                    continue
                if command in {"podman build", "podman exec", "podman logs"}:
                    self.assert_podman_leaf_coverage(command, text, profile)
                    continue
                flags = [option["flag"] for category in profile["categories"] for option in category["options"]]
                if command == "yq eval":
                    # The old capture predates three flags and omits the deprecated JSON switch.
                    self.assertEqual(record["version"], "yq (https://github.com/mikefarah/yq/) version v4.54.1")
                    headings = re.findall(r"^  (?:(-\w), |    )(--[\w-]+)\s", text, re.MULTILINE)
                    visible = {flag for pair in headings for flag in pair if flag}
                    self.assertEqual(len(visible), 64)
                    additions = {"--ini-key-value-delimiters", "--security-allow-write-any-path",
                                 "--security-force-never-escape-shell-output", "--tojson", "-j"}
                    self.assertCountEqual(flags, visible | additions)
                    continue
                if command == "fzf":
                    # This installed help covered the original 17 curated spellings.
                    # The release inventory checks the expanded menu, including manual-only flags.
                    self.assertEqual(record["version"], "0.44.1 (debian)")
                    original = (fixture_root.parent / "fzf.txt").read_text()
                    curated = re.findall(r"^  (--?[\w-]+)", original, re.MULTILINE)
                    self.assertEqual(len(curated), 17)
                    self.assertLessEqual(set(curated), set(flags))
                    flags = curated
                if command == "psql":
                    self.assertNotIn("--cluster", text)  # Added by Ubuntu's launcher.
                    flags.remove("--cluster")
                if command in {"esptool write-flash", "esptool.py write-flash"}:
                    # Rich truncated one spelling on capture. The tagged 5.2
                    # declaration independently covers the retired diff switch.
                    self.assertEqual(record["version"], "esptool v5.6.0")
                    self.assertIn("--ignore-flash-enc-efu…", text)
                    flags.remove("--ignore-flash-enc-efuse")
                    flags.remove("--no-diff-verify")
                for flag in flags:
                    pattern = r"(?<![\w-])" + re.escape(flag.rstrip("=")) + r"(?![\w-])"
                    self.assertRegex(text, pattern)

    def assert_podman_run_coverage(self, capture, profile):
        """Reconcile the visible Noble flags and the documented cross-release additions."""
        visible = set()
        for line in capture.splitlines():
            match = re.match(r"^\s+(?:(-\w),\s+)?(--[\w-]+)", line)
            if match:
                visible.update(flag for flag in match.groups() if flag)
        self.assertEqual(len(visible), 155)

        # Noble documents --net as an alias. Its help lists only --network.
        manual_only_on_noble = {"--net"}
        resolute_additions = {
            "--cert-dir", "--creds", "--gpus", "--health-log-destination", "--health-max-log-count",
            "--health-max-log-size", "--hosts-file", "--no-hostname", "--preserve-fd", "--retry",
            "--retry-delay",
        }
        upstream_additions = {"--health-start-interval"}
        flags = [option["flag"] for category in profile["categories"] for option in category["options"]]
        self.assertCountEqual(flags, visible | manual_only_on_noble | resolute_additions | upstream_additions)

    def assert_podman_leaf_coverage(self, command, capture, profile):
        """Compare arity with the independently inventoried manuals and packaged Noble help."""
        inventory = (ROOT / "docs/podman-build-exec-logs-manual-coverage.md").read_text()
        title = command.split()[1].title()
        section = inventory.split(f"## {title} inventory\n", 1)[1].split("\n## ", 1)[0]
        expected = {}
        for line in section.splitlines():
            if not line.startswith("| `--"):
                continue
            spellings, operand = line.split(" | ")[0:2]
            if "(parent)" in operand:
                continue
            requirement = "optional" if operand == "`[=POLICY]`" else "switch" if operand == "—" else "required"
            for flag in re.findall(r"`(-[\w-]+)`", spellings):
                self.assertNotIn(flag, expected)
                expected[flag] = requirement

        actual = {}
        for category in profile["categories"]:
            for option in category["options"]:
                flag = option["flag"].rstrip("=")
                self.assertNotIn(flag, actual)
                actual[flag] = ("optional" if option.get("argument_optional") else
                                "required" if option.get("argument") else "switch")
        self.assertEqual(expected, actual)
        captured = {}
        for line in capture.splitlines():
            match = re.fullmatch(r"\s+(?:(-\w), )?(--[\w-]+)(.*?)\s{2,}\S.*", line)
            if match:
                metavar = match[3].strip()
                for flag in filter(None, match.groups()[:2]):
                    captured[flag] = "optional" if "[=" in metavar else "required" if metavar else "switch"
        self.assertEqual(len(captured), {"Build": 103, "Exec": 18, "Logs": 12}[title])
        for flag, arity in captured.items():
            self.assertEqual(actual[flag], arity, flag)

    def profile(self, name):
        return json.loads((ROOT / "profiles" / (name + ".json")).read_text())

    def context(self, text, profile):
        return find_context(text, len(text), [profile],
                            driver_registry=load_driver_registry(ROOT / "config/drivers.example"))

    def test_podman_pull_policy_is_optional_and_context_stays_positional(self):
        profile = self.profile("podman-build")
        options = {option["flag"]: option for category in profile["categories"]
                   for option in category["options"]}
        self.assertTrue(options["--pull="]["argument_optional"])
        self.assertEqual(options["--pull="]["argument"], "POLICY")
        for text in ("podman build --pull ", "podman build --pull=never ", "podman build --quiet=true --pull=never "):
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
