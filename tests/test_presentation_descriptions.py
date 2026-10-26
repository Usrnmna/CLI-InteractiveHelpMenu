"""Protect exact opening-summary suppression without changing source evidence."""

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
from presentation import option_text
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
                self.assertEqual(rendered.splitlines().count(summary), 1)
                self.assertIn(option["detail"], rendered)
                self.assertIn("Source: captured help", rendered)
                # Legacy cross-field searches remain valid, including the old
                # summary/detail boundary, even though display is deduplicated.
                legacy = option["flag"] + " " + option["summary"] + " " + option["detail"]
                self.assertIn(legacy.casefold(), view.searchable)
                self.assertEqual(profile, before)

    def test_exact_line_boundary_rule_preserves_blank_lines_and_near_matches(self):
        cases = [
            ("Brief.", "Brief.", "Brief."),
            ("Brief.", "Brief.\nMore.\n\nSource: fixture", "Brief.\nMore.\n\nSource: fixture"),
            ("Brief.", "Brief.\n\nMore.\n", "Brief.\n\nMore.\n"),
            ("Brief.", "Brief.\r\nMore.", "Brief.\r\nMore."),
            ("Brief.", "Brief.\rMore.", "Brief.\rMore."),
            ("First\nSecond", "First\nSecond\nMore.", "First\nSecond\nMore."),
            ("Brief.", None, "Brief."),
            ("Brief.", "", "Brief."),
            ("Brief.", "Brief. Extra qualification.", "Brief.\nBrief. Extra qualification."),
            ("Brief.", "brief.\nMore.", "Brief.\nbrief.\nMore."),
            ("Brief.", " Brief.\nMore.", "Brief.\n Brief.\nMore."),
            ("Brief.", "Brief. \nMore.", "Brief.\nBrief. \nMore."),
            ("Brief.", "\nBrief.\nMore.", "Brief.\n\nBrief.\nMore."),
            ("Brief.", "Intro.\nBrief.\nMore.", "Brief.\nIntro.\nBrief.\nMore."),
            ("Brief.", "Brief.\nMore.\nBrief.", "Brief.\nMore.\nBrief."),
        ]
        for summary, detail, expected in cases:
            with self.subTest(summary=summary, detail=detail):
                profile = self.profile(summary, detail)
                before = deepcopy(profile)
                category = profile["categories"][0]
                view = option_text(profile, category, category["options"][0])
                self.assertEqual("\n".join(view.details), "Option: --sample\n" + expected)
                self.assertEqual(profile, before)

    def test_merged_sources_keep_attribution_and_later_repetition(self):
        first = build_profile("specimen", [("first source", "Options:\n  --sample  Brief.\n    First context.")])
        second = build_profile("specimen", [("second source", "Options:\n  --sample  Brief.\n    Second context.")])
        profile = merge_profiles([first, second])
        before = deepcopy(profile)
        option = profile["categories"][0]["options"][0]
        view = Browser(profile).text(option)
        rendered = "\n".join(view.details)
        self.assertEqual(rendered.splitlines().count("Brief."), 2)
        self.assertIn(option["detail"], rendered)
        for fragment in ("First context.", "Second context.", "Source: first source", "Source: second source"):
            self.assertIn(fragment, rendered)
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
        self.assertTrue(rendered.startswith("Source review needed;"))
        self.assertLess(rendered.index("bare numbers: seconds"), rendered.index("Option:"))
        self.assertLess(rendered.index("Applies to:"), rendered.index("Option:"))
        self.assertLess(rendered.index("Conflicting source claims."), rendered.index("Option:"))
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
        self.assertIn(option["detail"], view.details)

    def test_browser_draws_one_opening_description(self):
        profile = self.profile("Pass custom header(s) to server", "Pass custom header(s) to server\nSource: fixture")
        screen = CellScreen(24, 100)
        draw(screen, Browser(profile), load_keys())
        details = [v for (r, _c, _a), v in sorted(screen.cells.items()) if 12 <= r < 21]
        self.assertEqual(details.count("Pass custom header(s) to server"), 1)
        self.assertIn("Source: fixture", details)


if __name__ == "__main__":
    unittest.main()
