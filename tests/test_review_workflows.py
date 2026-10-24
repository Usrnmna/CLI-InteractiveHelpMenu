"""Review realistic command composition using literal, independently stated edits.

The existing corpus establishes individual option surfaces. These cases combine
those surfaces with global values, repeated arguments, quoting, and suffixes.
No test dispatches the pending command. The cursor marker is test data only.
"""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option, load_profiles
from discovery import build_profile


REGISTRY = load_driver_registry(ROOT / "config/drivers.example")
BUNDLED = load_profiles(ROOT / "profiles")
CURSOR = "@CURSOR@"

# command, pending line/cursor, selected flag, expected line/cursor
# Each expected line is literal so the oracle does not repeat insertion logic.
EDITS = json.loads((ROOT / "tests/fixtures/help/review-workflows.json").read_text(encoding="utf-8"))
ADDITIONS = json.loads((ROOT / "tests/fixtures/help/review-additions.json").read_text(encoding="utf-8"))

UNADAPTED_PATHS = ("gh pr unknown", "cargo unknown", "docker compose unknown",
                  "kubectl unknown", "helm unknown", "aws s3 unknown", "rclone unknown")


def split_cursor(marked):
    """Convert a single explicit fixture cursor into a character offset."""
    assert marked.count(CURSOR) == 1
    prefix, suffix = marked.split(CURSOR)
    return prefix + suffix, len(prefix)


def profile_for(command):
    """Honor the installed static-profile precedence before using corpus help."""
    for profile in BUNDLED:
        if profile["command"] == command.split():
            return profile
    for capture in ADDITIONS:
        if capture["command"] == command:
            return build_profile(command.split(), [(capture["source"], capture["text"])])
    path = ROOT / "tests/fixtures/help" / (command.replace(" ", "-") + ".txt")
    return build_profile(command.split(), [(str(path.name), path.read_text(encoding="utf-8"))])


class CompositionReviewTests(unittest.TestCase):
    def test_additional_local_help_excerpts_preserve_sentinels(self):
        for capture in ADDITIONS:
            with self.subTest(command=capture["command"]):
                profile = profile_for(capture["command"])
                options = {item["flag"]: item for category in profile["categories"] for item in category["options"]}
                self.assertTrue(set(capture["expected_flags"]) <= set(options))
                for flag, count in capture["argument_counts"].items():
                    self.assertTrue(options[flag]["argument"])
                    self.assertEqual(options[flag].get("argument_count", 1), count)

    def test_realistic_pending_commands(self):
        for case in EDITS:
            command, before, flag, after = (case[key] for key in ("command", "before", "flag", "after"))
            with self.subTest(command=command, before=before):
                profile = profile_for(command)
                line, point = split_cursor(before)
                forbidden = Mock(side_effect=AssertionError("Unexpected discovery"))
                context = find_context(line, point, [profile], discover=forbidden, driver_registry=REGISTRY)
                self.assertEqual(context.profile["command"], command.split())
                options = {option["flag"]: option for category in profile["categories"] for option in category["options"]}
                self.assertIn(flag, options)
                self.assertEqual(insert_option(context, options[flag]), split_cursor(after))
                forbidden.assert_not_called()

    def test_multi_value_and_repeated_arguments_require_all_values(self):
        profile = profile_for("jq")
        options = {item["flag"]: item for category in profile["categories"] for item in category["options"]}
        for flag in ("--arg", "--slurpfile"):
            self.assertEqual(options[flag]["argument_count"], 2)
            for pending in (f"jq {flag} ", f"jq {flag} name --ra", f"jq {flag}=name --ra",
                            f"jq --arg x y {flag} name --ra"):
                with self.subTest(line=pending), self.assertRaisesRegex(HelpError, "preceding option"):
                    find_context(pending, len(pending), [profile], driver_registry=REGISTRY)
        pending = "jq --arg x '--' --slurpfile y '日本 file.json' --ra"
        self.assertEqual(find_context(pending, len(pending), [profile], driver_registry=REGISTRY).query, "--ra")

    def test_requested_unadapted_paths_fail_before_discovery(self):
        for command in UNADAPTED_PATHS:
            probe = Mock(side_effect=AssertionError("Unsupported path reached discovery"))
            line = command + " --"
            with self.subTest(command=command), self.assertRaisesRegex(HelpError, "Unsupported subcommand"):
                find_context(line, len(line), BUNDLED, discover=probe, driver_registry=REGISTRY)
            probe.assert_not_called()

    def test_runner_boundaries_do_not_offer_parent_options(self):
        for command, suffix in (("docker run", "--env A=B image sh --"),
                                ("uv run", "--python 3.12 script.py --"),
                                ("npm run", "--workspace web build --")):
            line = command + " " + suffix
            with self.subTest(line=line), self.assertRaisesRegex(HelpError, "first positional"):
                find_context(line, len(line), [profile_for(command)], driver_registry=REGISTRY)

    def test_invalid_shell_text_never_reaches_discovery(self):
        for line in ("rsync 'unfinished --", "rsync source | cat --", "rsync $(touch marker) --",
                     "rsync >file --", "rsync `touch marker` --", "rsync source; touch marker --",
                     "rsync \\", "rsync\n--", "rsync -- #comment"):
            probe = Mock(side_effect=AssertionError("Invalid shell text reached discovery"))
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), BUNDLED, discover=probe, driver_registry=REGISTRY)
            probe.assert_not_called()

    def test_equal_value_token_and_end_marker_are_not_editable(self):
        for marked in ("rsync --exclude=*.t@CURSOR@mp source dest", "rsync -- source --ar@CURSOR@",
                       "git commit --message 'done' -- file --am@CURSOR@"):
            line, point = split_cursor(marked)
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, point, BUNDLED, driver_registry=REGISTRY)


class MetadataReviewTests(unittest.TestCase):
    def setUp(self):
        """Validate source controls before asserting the reconciled value count.

        The source texts are controlled declarations, not a claim about a
        particular installed program version. Each parses correctly alone.
        """
        help_text = "Options:\n  --pair NAME  Bind a named value.\n"
        manual_text = "OPTIONS\n  --pair name value  Bind a name and value.\n"
        manual = build_profile("tool", [("manual", manual_text)])
        self.assertEqual(manual["categories"][0]["options"][0]["argument_count"], 2)
        self.merged = build_profile("tool", [("help", help_text), ("manual", manual_text)])

    def test_richer_manual_arity_replaces_an_existing_single_value(self):
        """A second explicit value remains required after merging sources."""
        line = "tool --pair label --next"
        with self.assertRaisesRegex(HelpError, "preceding option"):
            find_context(line, len(line), [self.merged])


if __name__ == "__main__":
    unittest.main()
