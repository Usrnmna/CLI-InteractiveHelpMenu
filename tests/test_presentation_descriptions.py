"""Protect concise option details without changing source evidence or execution boundaries."""

from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from discovery import build_profile, merge_profiles
from presentation import concise_description, option_text
from test_numerical_presentation import CellScreen
from test_value_semantics import contract, synthetic_node
from ui import Browser, draw, load_keys


class DescriptionPresentationTests(unittest.TestCase):
    def setUp(self):
        """Keep every case passive, including parsing the captured help."""
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen",
                       "socket.socket", "socket.create_connection", "discovery.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Passive presentation attempted execution")))

    def profile(self, summary, detail=None):
        """Construct a plain option whose rendered prose can be checked exactly."""
        option = {"flag": "--sample", "summary": summary}
        if detail is not None:
            option["detail"] = detail
        return {"command": ["specimen"], "description": "Presentation specimen",
                "categories": [{"name": "Options", "options": [option]}]}

    def test_real_captured_opening_descriptions_appear_once(self):
        captures = json.loads((ROOT / "tests/fixtures/help/captured.json").read_text(encoding="utf-8"))
        cases = (("git commit", "-m", "Use the given <msg> as the commit message. If multiple -m options are given, their"),
                 ("docker run", "-e", "Set environment variables"),
                 ("curl", "-H", "Pass custom header(s) to server"),
                 ("terraform plan", "-var", "Set a value for one of the input variables in the root"),
                 ("kubectl logs", "-c", "Print the logs of this container"),
                 ("ffmpeg", "-y", "overwrite output files"))
        for command, flag, summary in cases:
            with self.subTest(command=command):
                profile = build_profile(command.split(), [("captured help", captures[command]["text"])])
                before = deepcopy(profile)
                browser = Browser(profile)
                option = next(o for c in profile["categories"] for o in c["options"] if o["flag"] == flag)
                view = browser.text(option)
                rendered = "\n".join(view.details)
                self.assertEqual(rendered.count(summary.split(".")[0]), 1)
                self.assertNotIn("Source: captured help", rendered)
                # Legacy cross-field searches remain valid, including the old
                # summary/detail boundary, even though display is deduplicated.
                legacy = option["flag"] + " " + option["summary"] + " " + option["detail"]
                self.assertIn(legacy.casefold(), view.searchable)
                self.assertEqual(profile, before)

    def test_wrapped_prose_and_repetitions_are_simplified(self):
        cases = [
            ("Brief.", "Brief.\nMore.\n\nSource: fixture", "Brief.\nMore."),
            ("Brief.", " Brief. \r\nMore.\nBrief.", "Brief.\nMore."),
            ("First line", "First line\ncontinues here.", "First line continues here."),
            ("Brief.", None, "Brief."),
            ("Brief.", "Brief. Extra qualification.", "Brief.\nExtra qualification."),
        ]
        for summary, detail, expected in cases:
            with self.subTest(summary=summary, detail=detail):
                profile = self.profile(summary, detail)
                before = deepcopy(profile)
                category = profile["categories"][0]
                view = option_text(profile, category, category["options"][0])
                self.assertEqual("\n".join(view.details), "Option: --sample\n" + expected)
                self.assertEqual(profile, before)

    def test_merged_sources_keep_search_evidence_without_display_repetition(self):
        first = build_profile("specimen", [("first source", "Options:\n  --sample  Brief.\n    First context.")])
        second = build_profile("specimen", [("second source", "Options:\n  --sample  Brief.\n    Second context.")])
        profile = merge_profiles([first, second])
        before = deepcopy(profile)
        option = profile["categories"][0]["options"][0]
        view = Browser(profile).text(option)
        rendered = "\n".join(view.details)
        self.assertEqual(rendered.splitlines().count("Brief."), 1)
        for fragment in ("First context.", "Second context.", "Source: first source", "Source: second source"):
            self.assertEqual(fragment in rendered, not fragment.startswith("Source:"))
            self.assertIn(fragment.casefold(), view.searchable)
        self.assertEqual(profile, before)

    def test_warning_and_value_guidance_order_survives_description_suppression(self):
        profile = self.profile("Brief.", "Brief.\nSource: fixture")
        option = profile["categories"][0]["options"][0]
        option.update(argument="N", value_semantics=contract(synthetic_node("duration")))
        profile["documentation"] = {"diagnostics": [{"option": "--sample", "source": "fixture",
                                                     "message": "Conflicting source claims."}]}
        browser = Browser(profile)
        view = browser.text(option)
        rendered = "\n".join(view.details)
        self.assertTrue(rendered.startswith("Conflicting or incomplete value guidance;"))
        self.assertLess(rendered.index("bare numbers: seconds"), rendered.index("Option:"))
        self.assertLess(rendered.index("Applicability unconfirmed"), rendered.index("Option:"))
        self.assertNotIn("Conflicting source claims.", rendered)
        self.assertNotIn("Source:", rendered)
        self.assertEqual(rendered.splitlines().count("Brief."), 1)
        for query in ("Brief.", "seconds", "Conflicting source claims.", "Source: fixture"):
            browser.set_query(query)
            self.assertEqual(browser.options(), [option])

    def test_distinct_curated_summary_and_detail_remain_visible(self):
        profile = json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))
        browser = Browser(profile, "--archive")
        option = browser.options()[0]
        view = browser.text(option)
        self.assertIn("Enable archive mode", view.details)
        self.assertIn("ACLs, extended attributes, and hard links require separate options.", view.details)

    def test_browser_draws_one_opening_description(self):
        profile = self.profile("Pass custom header(s) to server", "Pass custom header(s) to server\nSource: fixture")
        screen = CellScreen(24, 100)
        draw(screen, Browser(profile), load_keys())
        details = [v for (r, _c, _a), v in sorted(screen.cells.items()) if 12 <= r < 21]
        self.assertEqual(details.count("Pass custom header(s) to server"), 1)
        self.assertNotIn("Source: fixture", details)

    def test_metadata_examples_and_background_are_removed(self):
        profile = self.profile("Select output format", """Select output format.
Version: 2.4
Updated: 2026-10-26
Source: https://example.test/manual
Allowed choices: json, yaml. Requires UTF-8.
Added in version 2.4. Internally, a cache stores the setting.
See the manual for background.
Example:
  specimen --sample json
Source: second capture
Only one format may be selected.
```sh
specimen --sample yaml
```
""")
        option = profile["categories"][0]["options"][0]
        option["argument"] = "FORMAT"
        before = deepcopy(profile)
        view = Browser(profile).text(option)
        text = "\n".join(view.details)
        for expected in ("Select output format", "json, yaml", "Requires UTF-8",
                         "Only one format", "Argument required."):
            self.assertIn(expected, text)
        for removed in ("2026", "2.4", "https://", "Internally", "specimen", "Example:", "Source:"):
            self.assertNotIn(removed, text)
        self.assertEqual(text.count("FORMAT"), 1)
        self.assertEqual(profile, before)

    def test_protocol_versions_date_formats_and_constraints_are_not_metadata(self):
        text = "Use HTTP/1.1. Requires TLS 1.2. Date format: YYYY-MM-DD. Range: 0.01 to 2.5."
        self.assertEqual(" ".join(concise_description(text)), text)
        self.assertEqual(concise_description("Use a. Use A."), ("Use a.", "Use A."))

    def test_no_value_flag_omits_argument_instructions_and_suggestions(self):
        profile = json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))
        browser = Browser(profile, "--dry-run")
        view = browser.text(browser.options()[0])
        self.assertEqual(view.details, ("Option: --dry-run", "Show a trial run without changing files"))

    def test_required_optional_attached_and_multiple_values_keep_arity(self):
        for fields, label in (({}, "Argument required."),
                              ({"argument_optional": True}, "Optional argument."),
                              ({"argument_style": "attached_only"}, "Attached argument required."),
                              ({"argument_style": "attached_only", "argument_optional": True},
                               "Optional attached argument."),
                              ({"argument_count": 2}, "Argument required.")):
            profile = self.profile("Select entries", "Requires complete pairs. Zero means all entries.")
            option = profile["categories"][0]["options"][0]
            option.update(argument="START END", **fields)
            view = Browser(profile).text(option)
            self.assertIn(label, view.details)
            self.assertIn("Requires complete pairs.", view.details)
            self.assertIn("Zero means all entries.", view.details)
            self.assertEqual("\n".join(view.details).count("START END"), 1)

    def test_similar_words_do_not_suppress_distinct_behavior(self):
        profile = self.profile("Mute", "Only mute the selected stream.")
        option = profile["categories"][0]["options"][0]
        option.update(argument="N", value_semantics=contract(synthetic_node("count", meaning="Unmute entries")))
        self.assertIn("Mute", Browser(profile).text(option).details)

    def test_shared_choices_remain_with_each_target_variant(self):
        profile = json.loads((ROOT / "profiles/esptool-write-flash.json").read_text(encoding="utf-8"))
        browser = Browser(profile, "--flash-size")
        text = "\n".join(browser.text(browser.options()[0]).details)
        variants = text.split("Value variant ")[1:]
        self.assertEqual(len(variants), 3)
        for variant in variants:
            self.assertIn("Input 4MB", variant)
            self.assertIn("4194304 bytes", variant)
            self.assertIn("chip:", variant)
        self.assertNotIn("Input 256KB", variants[1])


if __name__ == "__main__":
    unittest.main()
