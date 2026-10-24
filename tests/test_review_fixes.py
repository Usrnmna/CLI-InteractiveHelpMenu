"""Regression contracts for metadata reconciliation and ten added help paths."""

import json
from pathlib import Path
import unittest

from test_review_workflows import ROOT, REGISTRY, profile_for, split_cursor
from command_paths import help_route
from core import HelpError, find_context, insert_option
from discovery import build_profile, parse_help


ROUTES = {
    "gh pr view": ("help", "pr", "view"),
    "gh pr create": ("help", "pr", "create"),
    "cargo test": ("test", "--help"),
    "docker compose logs": ("compose", "logs", "--help"),
    "docker compose exec": ("compose", "exec", "--help"),
    "kubectl describe": ("help", "describe"),
    "kubectl logs": ("help", "logs"),
    "helm upgrade": ("help", "upgrade"),
    "aws s3 sync": ("s3", "sync", "help"),
    "rclone sync": ("sync", "--help"),
}


class AddedPathTests(unittest.TestCase):
    def test_fixed_routes_and_compose_child_boundary(self):
        for command, arguments in ROUTES.items():
            words = command.split()
            with self.subTest(command=command):
                route = help_route(words[0], tuple(words[1:]), REGISTRY)
                self.assertEqual(route.arguments, arguments)
                self.assertIsNone(route.manual)
                self.assertEqual(route.stop_at_positional, command == "docker compose exec")

    def test_combined_edits_preserve_exact_buffer_and_cursor(self):
        scenarios = json.loads((ROOT / "tests/fixtures/help/review-new-paths.json").read_text())
        self.assertEqual({case["command"] for case in scenarios}, set(ROUTES))
        for case in scenarios:
            with self.subTest(command=case["command"], before=case["before"]):
                line, point = split_cursor(case["before"])
                profile = profile_for(case["command"])
                context = find_context(line, point, [profile], driver_registry=REGISTRY)
                self.assertEqual(context.profile["command"], case["command"].split())
                options = {option["flag"]: option for category in profile["categories"] for option in category["options"]}
                self.assertEqual(insert_option(context, options[case["flag"]]), split_cursor(case["after"]))

    def test_runner_child_and_incomplete_value_slots_are_rejected(self):
        cases = {
            "docker compose exec": (" --env ", " --env NAME=value service --", " service sh --", " -- service sh --"),
            "cargo test": (" --features ", " filter -- --nocapture --"),
            "gh pr create": (" --title ", " --body "),
            "helm upgrade": (" app chart --values ",),
            "aws s3 sync": (" source dest --exclude ",),
            "kubectl logs": (" pod --tail ",),
        }
        for command, suffixes in cases.items():
            for suffix in suffixes:
                line = command + suffix
                with self.subTest(line=line), self.assertRaises(HelpError):
                    find_context(line, len(line), [profile_for(command)], driver_registry=REGISTRY)


class MetadataMergeTests(unittest.TestCase):
    def test_larger_arity_wins_in_both_source_orders_and_names_conflict(self):
        sources = [("help", "--pair NAME  Bind a value."), ("manual", "--pair name value  Bind two values.")]
        for ordered in (sources, sources[::-1]):
            with self.subTest(order=[source for source, _ in ordered]):
                profile = build_profile("tool", ordered)
                option = profile["categories"][0]["options"][0]
                self.assertEqual(option["argument_count"], 2)
                self.assertIn("Argument declarations disagree", option["detail"])
                self.assertIn("Source: help", option["detail"])
                self.assertIn("Source: manual", option["detail"])
                complete = "tool --pair label '-value' --"
                self.assertEqual(find_context(complete, len(complete), [profile]).query, "--")

    def test_equal_arity_prefers_required_values_in_both_orders(self):
        sources = [("help", "--color[=WHEN]  Color output."), ("manual", "--color WHEN  Color output.")]
        for ordered in (sources, sources[::-1]):
            profile = build_profile("tool", ordered)
            option = profile["categories"][0]["options"][0]
            self.assertFalse(option["argument_optional"])
            self.assertEqual(option["argument"], "WHEN")
            with self.assertRaisesRegex(HelpError, "preceding option"):
                find_context("tool --color ", 13, [profile])

    def test_negative_equals_default_is_a_value_not_an_alias(self):
        for default in ("-1", "-10", "-literal"):
            with self.subTest(default=default):
                options = parse_help(f"Options:\n    --tail={default}:\n        Number of entries.\n", "help")
                self.assertEqual(len(options), 1)
                self.assertEqual(options[0]["flag"], "--tail=")
                self.assertEqual(options[0]["argument"], default)


if __name__ == "__main__":
    unittest.main()
