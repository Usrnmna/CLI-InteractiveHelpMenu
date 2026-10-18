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
from discovery import ProbeError, Settings, build_profile, discover, parse_help
from command_paths import help_route, load_driver_registry, resolve_path


FIXTURES = ROOT / "tests/fixtures/help"
MATRIX = json.loads((FIXTURES / "matrix.json").read_text())
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")
CAPTURED = json.loads((FIXTURES / "captured.json").read_text())


def fixture_text(command):
    return (FIXTURES / (command.replace(" ", "-") + ".txt")).read_text(encoding="utf-8")


def options_by_flag(profile):
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


class ProgramCorpusTests(unittest.TestCase):
    def test_captured_help_satisfies_independent_sentinels(self):
        self.assertEqual(set(CAPTURED), {case["command"] for case in MATRIX})
        for case in MATRIX:
            with self.subTest(command=case["command"]):
                text = CAPTURED[case["command"]]["text"]
                if case.get("allow_empty"):
                    self.assertEqual(parse_help(text, "capture"), [])
                    continue
                options = options_by_flag(build_profile(case["command"].split(), [("capture", text)]))
                self.assertTrue(set(case["live_flags"]) <= set(options), set(case["live_flags"]) - set(options))
                self.assertFalse(set(case["excluded"]) & set(options))
                for flag, count in case.get("live_argument_counts", {}).items():
                    self.assertTrue(options[flag]["argument"])
                    self.assertEqual(options[flag].get("argument_count", 1), count)

    def test_default_values_negation_and_numeric_aliases(self):
        text = "Options:\n    --watch=false:\n        Observe updates.\n    --output='':\n        Choose format.\n  --[no-]frozen-lockfile  Require the existing lockfile.\n  -<number>, -n <number>, --max-count=<number>\n      Limit entries.\n"
        options = options_by_flag(build_profile("tool", [("fixture", text)]))
        self.assertEqual(options["--watch"]["argument"], "")
        self.assertIn("--output=", options)
        self.assertIn("--frozen-lockfile", options)
        self.assertIn("--no-frozen-lockfile", options)
        self.assertEqual(options["-n"]["argument"], "<number>")
        self.assertIn("--max-count=", options)
        self.assertNotIn("-", options)
        for declaration in ("--[maybe-]flag", "--[no-]flag;touch", "-<number>;touch, --flag", "-o{Directory}", "-c:v codec"):
            self.assertEqual(parse_help(declaration, "fixture"), [], declaration)

    def test_aligned_aliases_typed_columns_and_partially_optional_values(self):
        text = "Options:\n  -O,  --output-document=FILE      Write output.\n  --include  (string)  Include a pattern.\n  -o, --output [TYPES:]TEMPLATE  Choose output template.\n  --slurpfile name file set a variable.\n"
        options = options_by_flag(build_profile("tool", [("fixture", text)]))
        self.assertEqual(options["-O"]["argument"], "FILE")
        self.assertEqual(options["--include"]["argument"], "(string)")
        self.assertEqual(options["--output"]["argument"], "[TYPES:]TEMPLATE")
        self.assertFalse(options["--output"]["argument_optional"])
        self.assertEqual(options["--slurpfile"]["argument_count"], 2)

    def test_matrix_covers_every_requested_program_and_tier(self):
        expected = set("git curl wget rsync docker pip pip3 uv npm pnpm jq rg ffmpeg ffprobe gh kubectl helm aws terraform tofu cargo cmake ninja gcc clang rclone restic borg 7z 7zz magick convert yt-dlp vlc".split())
        self.assertEqual({case["command"].split()[0] for case in MATRIX}, expected)
        self.assertEqual({case["tier"] for case in MATRIX}, {"essential", "next", "extended"})
        self.assertEqual(len({case["command"] for case in MATRIX}), len(MATRIX))
        for case in MATRIX:
            words = case["command"].split()
            with self.subTest(command=words):
                self.assertEqual(resolve_path(words, [], REGISTRY).words, tuple(words))
                self.assertTrue(case["live_flags"] or case.get("allow_empty"))
                self.assertTrue((FIXTURES / case["fixture"]).is_file())

    def test_jq_requires_both_variable_name_and_value(self):
        profile = build_profile("jq", [("fixture", fixture_text("jq"))])
        for flag in ("--arg", "--slurpfile"):
            for suffix in (" ", " name ", "=name "):
                line = "jq " + flag + suffix
                with self.subTest(line=line), self.assertRaises(HelpError):
                    find_context(line, len(line), [profile])
            line = "jq " + flag + " name 'private value' --"
            self.assertEqual(find_context(line, len(line), [profile]).query, "--")

    def test_aws_typed_values_and_boolean_pairs(self):
        profile = build_profile(["aws", "ec2", "describe-instances"], [("fixture", fixture_text("aws ec2 describe-instances"))])
        options = options_by_flag(profile)
        self.assertEqual(options["--filters"]["argument"], "(list)")
        self.assertEqual(options["--dry-run"]["argument"], "")
        self.assertEqual(options["--no-dry-run"]["argument"], "")

    def test_runner_boundaries_and_end_of_options(self):
        for command in ("uv run", "npm run", "docker run", "gh repo clone", "cargo build"):
            profile = build_profile(command.split(), [("fixture", fixture_text(command))])
            line = command + " -- child --"
            with self.subTest(command=command), self.assertRaises(HelpError):
                find_context(line, len(line), [profile], driver_registry=REGISTRY)
        for command in ("uv run", "npm run", "docker run"):
            profile = build_profile(command.split(), [("fixture", fixture_text(command))])
            for suffix in (" script --", " --unknown script --"):
                line = command + suffix
                with self.subTest(line=line), self.assertRaises(HelpError):
                    find_context(line, len(line), [profile], driver_registry=REGISTRY)

    def test_global_values_do_not_become_nested_command_words(self):
        for line, expected in [
            ("kubectl --context private get", "kubectl get"),
            ("aws --profile private --region=private ec2 describe-instances", "aws ec2 describe-instances"),
            ("terraform -chdir=private plan", "terraform plan"),
            ("helm -nprivate install", "helm install"),
            ("uv --directory private pip install", "uv pip install"),
            ("docker --context private compose up", "docker compose up")]:
            self.assertEqual(resolve_path(line.split(), [], REGISTRY).words, tuple(expected.split()))
        for line in ("aws s3 unknown", "uv pip unknown", "kubectl --unknown get"):
            with self.subTest(line=line), self.assertRaises(ValueError):
                resolve_path(line.split(), [], REGISTRY)

    def test_multiple_value_count_validation_and_merge(self):
        profile = build_profile("jq", [("help", "--arg  Bind a variable"), ("manual", "--arg name value  Bind a variable")])
        option = options_by_flag(profile)["--arg"]
        self.assertEqual(option["argument_count"], 2)
        for invalid in (True, 0, -1, 17, "2", None):
            option["argument_count"] = invalid
            with self.subTest(value=invalid), self.assertRaises(HelpError):
                validate_profile(profile, Path("fixture"))

    def test_failed_sources_do_not_become_expected_empty_help(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "npm"
            write_executable(executable, "print('No option declarations')\n")
            with patch.dict(os.environ, {"PATH": directory}), patch("discovery.run_probe", side_effect=ProbeError("timed out")):
                with self.assertRaises(ProbeError):
                    discover("npm", Settings(cache_ttl=0), driver_registry=REGISTRY)

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
                profile = build_profile(case["command"].split(), [("fixture", fixture_text(case["command"]))])
                validate_profile(profile, Path("fixture"))
                options = options_by_flag(profile)
                for flag, argument in case["flags"].items():
                    self.assertIn(flag, options)
                    self.assertEqual(options[flag]["argument"], argument, flag)
                for flag in case["excluded"]:
                    self.assertNotIn(flag, options)
                for flag, count in case.get("argument_counts", {}).items():
                    self.assertEqual(options[flag].get("argument_count", 1), count)

    def test_required_arguments_reject_another_option_until_value_is_supplied(self):
        for case in MATRIX:
            if not case["flags"]:
                continue
            profile = build_profile(case["command"].split(), [("fixture", fixture_text(case["command"]))])
            options = options_by_flag(profile)
            for flag, argument in case["flags"].items():
                if not argument or flag.endswith("=") or options[flag].get("argument_optional"):
                    continue
                line = f"{case['command']} {flag} "
                with self.subTest(command=case["command"], flag=flag):
                    with self.assertRaises(HelpError):
                        find_context(line, len(line), [profile], driver_registry=REGISTRY)
                    completed = line + "'private value' " * options[flag].get("argument_count", 1) + "--"
                    self.assertEqual(find_context(completed, len(completed), [profile], driver_registry=REGISTRY).query, "--")

    def test_every_discovered_flag_edits_only_the_selected_span(self):
        for case in MATRIX:
            if not case["flags"]:
                continue
            profile = build_profile(case["command"].split(), [("fixture", fixture_text(case["command"]))])
            for option in options_by_flag(profile).values():
                prefix = case["command"] + "  "
                suffix = "  'private café/日本 file'"
                line = prefix + "--part" + suffix
                with self.subTest(command=case["command"], flag=option["flag"]):
                    context = find_context(line, len(prefix) + 3, [profile], driver_registry=REGISTRY)
                    edited, point = insert_option(context, option)
                    self.assertEqual(edited, prefix + option["flag"] + suffix)
                    self.assertEqual(point, len(prefix + option["flag"]) + (0 if option["flag"].endswith("=") else 1))

    def test_executable_fixtures_never_receive_pending_actions_or_values(self):
        for case in MATRIX:
            with self.subTest(command=case["command"]), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                log = folder / "calls"
                marker = folder / "executed"
                words = case["command"].split()
                route = help_route(words[0], tuple(words[1:]), REGISTRY)
                executable = folder / words[0]
                write_executable(executable,
                                 "import json, pathlib, sys\n"
                                 f"pathlib.Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]))\n"
                                 f"if sys.argv[1:] != {list(route.arguments)!r}:\n"
                                 f"    pathlib.Path({str(marker)!r}).write_text('action dispatched')\n"
                                 f"print({fixture_text(case['command'])!r})\n")
                manual_log = folder / "manual-calls"
                write_executable(folder / "man", "import pathlib, sys\n"
                                 f"pathlib.Path({str(manual_log)!r}).write_text(repr(sys.argv[1:]))\n"
                                 f"print({fixture_text(case['command'])!r})\n")
                prefix = case["command"] + " --"
                line = prefix + " '$(literal private argument)'"
                discover_case = lambda command, subcommands=(): discover(command, Settings(cache_ttl=0),
                    subcommands=subcommands, driver_registry=REGISTRY)
                with patch.dict(os.environ, {"PATH": directory}):
                    if case["flags"]:
                        context = find_context(line, len(prefix), [], discover=discover_case, driver_registry=REGISTRY)
                        self.assertEqual(context.profile["command"], words)
                    else:
                        with self.assertRaisesRegex(HelpError, "No recognizable option"):
                            find_context(line, len(prefix), [], discover=discover_case, driver_registry=REGISTRY)
                if route.arguments:
                    self.assertEqual(json.loads(log.read_text()), list(route.arguments))
                else:
                    self.assertFalse(log.exists())
                self.assertEqual(manual_log.exists(), bool(route.manual))
                self.assertFalse(marker.exists())
                # Man-only policy must suppress every supplied executable route,
                # including routes with a trailing help selector.
                log.unlink(missing_ok=True)
                with patch.dict(os.environ, {"PATH": directory}):
                    if route.manual and case["flags"]:
                        discover(words[0], Settings(mode="man", cache_ttl=0), subcommands=tuple(words[1:]), driver_registry=REGISTRY)
                    else:
                        with self.assertRaises(HelpError):
                            discover(words[0], Settings(mode="man", cache_ttl=0), subcommands=tuple(words[1:]), driver_registry=REGISTRY)
                self.assertFalse(log.exists())
                self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
