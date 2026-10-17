"""Exercise heterogeneous help formats and their literal edit contracts offline."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover, parse_help


FIXTURES = ROOT / "tests/fixtures/help"
MATRIX = json.loads((FIXTURES / "matrix.json").read_text())


def fixture_text(command):
    return (FIXTURES / (command + ".txt")).read_text(encoding="utf-8")


def options_by_flag(profile):
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


class ProgramCorpusTests(unittest.TestCase):
    def test_npm_bracketed_groups_aliases_and_repeated_values(self):
        profile = build_profile(["npm", "install"], [("fixture", fixture_text("npm-install"))])
        options = options_by_flag(profile)
        self.assertIn("--dry-run", options)
        self.assertEqual(options["--omit"]["argument"], "<dev|optional|peer>")
        self.assertEqual(options["-w"]["argument"], "<workspace-name>")
        self.assertEqual(options["--workspace"]["argument"], "<workspace-name>")
        self.assertFalse(options["--workspace"]["argument_optional"])
        line = "npm install --workspace "
        with self.assertRaises(HelpError):
            find_context(line, len(line), [profile])

    def test_bracketed_declarations_are_rejected_outside_options_or_when_malformed(self):
        for heading in ["Usage:", "Examples:", "Synopsis:"]:
            self.assertEqual(parse_help(heading + "\n[--fake]", "fixture"), [])
        for declaration in ["[--fake;touch marker]", "[--fake] $(bad)", "[--fake] [--other", "[--fake]]", "[--flag=value]"]:
            self.assertEqual(parse_help("Options:\n" + declaration, "fixture"), [], declaration)

    def test_expected_flags_and_argument_shapes(self):
        for case in MATRIX:
            with self.subTest(command=case["command"]):
                entries = parse_help(fixture_text(case["command"]), "fixture")
                if not case["flags"]:
                    self.assertEqual(entries, [])
                    continue
                profile = build_profile(case["command"], [("fixture", fixture_text(case["command"]))])
                validate_profile(profile, Path("fixture"))
                options = options_by_flag(profile)
                for flag, argument in case["flags"].items():
                    self.assertIn(flag, options)
                    self.assertEqual(options[flag]["argument"], argument, flag)
                for flag in case["excluded"]:
                    self.assertNotIn(flag, options)

    def test_required_arguments_reject_another_option_until_value_is_supplied(self):
        for case in MATRIX:
            if not case["flags"]:
                continue
            profile = build_profile(case["command"], [("fixture", fixture_text(case["command"]))])
            for flag, argument in case["flags"].items():
                if not argument or flag.endswith("="):
                    continue
                line = f"{case['command']} {flag} "
                with self.subTest(command=case["command"], flag=flag):
                    with self.assertRaises(HelpError):
                        find_context(line, len(line), [profile])
                    completed = line + "'private value' --"
                    self.assertEqual(find_context(completed, len(completed), [profile]).query, "--")

    def test_every_discovered_flag_edits_only_the_selected_span(self):
        for case in MATRIX:
            if not case["flags"]:
                continue
            profile = build_profile(case["command"], [("fixture", fixture_text(case["command"]))])
            for option in options_by_flag(profile).values():
                prefix = case["command"] + "  "
                suffix = "  'private café/日本 file'"
                line = prefix + "--part" + suffix
                with self.subTest(command=case["command"], flag=option["flag"]):
                    context = find_context(line, len(prefix) + 3, [profile])
                    edited, point = insert_option(context, option)
                    self.assertEqual(edited, prefix + option["flag"] + suffix)
                    self.assertEqual(point, len(prefix + option["flag"]) + (0 if option["flag"].endswith("=") else 1))

    def test_executable_fixtures_never_receive_pending_actions_or_values(self):
        for case in MATRIX:
            with self.subTest(command=case["command"]), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                log = folder / "calls"
                marker = folder / "executed"
                executable = folder / case["command"]
                write_executable(executable,
                                 "import json, pathlib, sys\n"
                                 f"pathlib.Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]))\n"
                                 "if sys.argv[1:] != ['--help']:\n"
                                 f"    pathlib.Path({str(marker)!r}).write_text('action dispatched')\n"
                                 f"print({fixture_text(case['command'])!r})\n")
                line = case["command"] + " install '$(literal private argument)' --"
                with patch.dict(os.environ, {"PATH": directory}):
                    if case["flags"]:
                        context = find_context(line, len(line), [], discover=lambda command: discover(command, Settings(cache_ttl=0)))
                        self.assertEqual(context.profile["command"], [case["command"]])
                    else:
                        with self.assertRaisesRegex(HelpError, "No recognizable option"):
                            find_context(line, len(line), [], discover=lambda command: discover(command, Settings(cache_ttl=0)))
                self.assertEqual(json.loads(log.read_text()), ["--help"])
                self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
