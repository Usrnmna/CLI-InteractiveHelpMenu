"""Systems route regressions with independent syntax and literal edit evidence."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import help_route, load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover, parse_help


FIXTURES = ROOT / "tests/fixtures/help"
CASES = json.loads((FIXTURES / "expansion-systems.json").read_text(encoding="utf-8"))
CAPTURED = json.loads((FIXTURES / "expansion-systems-captured.json").read_text(encoding="utf-8"))
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")


def profile_for(command):
    """Read the curated profile independently of automatic discovery."""
    return json.loads((ROOT / "profiles" / (command.replace(" ", "-") + ".json")).read_text(encoding="utf-8"))


def options_for(profile):
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


def context_for(line, point, profile):
    """Supply successful fixture identity evidence without running a vendor tool."""
    return find_context(line, point, [profile], discover=lambda *args, **kwargs: profile,
                        driver_registry=REGISTRY)


class SystemsExpansionTests(unittest.TestCase):
    def test_complete_route_inventory_and_provenance(self):
        expected = {
            "systemctl status", "systemctl list-units", "systemctl show", "journalctl",
            "ssh", "scp", "sftp", "ip address", "ip link", "ip route", "ss",
            "openssl s_client", "openssl x509", "openssl dgst", "podman run", "podman build",
            "podman exec", "podman logs", "psql", "yq eval", "fd", "fdfind", "fzf", "ansible-playbook",
        }
        self.assertEqual({case["command"] for case in CASES}, expected)
        self.assertEqual(set(CAPTURED), expected)
        for case in CASES:
            command = case["command"]
            with self.subTest(command=command):
                self.assertEqual(resolve_path(command.split(), [], REGISTRY).words, tuple(command.split()))
                evidence = CAPTURED[command]
                self.assertIn(evidence["kind"], ("installed-capture", "documented-fixture"))
                self.assertTrue(evidence["source_url"].startswith("https://"))
                self.assertEqual(evidence["text"], (FIXTURES / case["fixture"]).read_text(encoding="utf-8"))
                profile = profile_for(command)
                validate_profile(profile, Path(command))
                self.assertGreaterEqual(len(options_for(profile)), 7)

    def test_real_or_documented_help_matches_independent_declarations(self):
        for case in CASES:
            with self.subTest(command=case["command"]):
                text = (FIXTURES / case["fixture"]).read_text(encoding="utf-8")
                if case.get("keyword_sentinels"):
                    # ip leaf help is keyword grammar, not a list of dash flags.
                    self.assertEqual(parse_help(text, "fixture"), [])
                    for keyword in case["keyword_sentinels"]:
                        self.assertIn(keyword, text)
                    continue
                options = options_for(build_profile(case["command"].split(), [("fixture", text)]))
                for flag, argument in case["flags"].items():
                    self.assertIn(flag, options)
                    self.assertEqual(options[flag]["argument"], argument, flag)
                    self.assertEqual(options[flag].get("argument_count", 1), 1)

    def test_curated_shape_aliases_optional_values_and_exclusions(self):
        for case in CASES:
            profile = profile_for(case["command"])
            options = options_for(profile)
            for flag, expected in case["profile_sentinels"].items():
                with self.subTest(command=case["command"], flag=flag):
                    self.assertEqual(options[flag].get("argument", ""), expected["argument"])
                    self.assertEqual(options[flag].get("argument_count", 1), expected["argument_count"])
                    self.assertEqual(options[flag].get("kind", "flag"), expected["kind"])
        for command, alias, long in (("journalctl", "-u", "--unit="), ("psql", "-d", "--dbname"),
                                     ("podman run", "-e", "--env"), ("fd", "-t", "--type"),
                                     ("ansible-playbook", "-e", "--extra-vars")):
            options = options_for(profile_for(command))
            self.assertEqual(options[alias]["argument"], options[long]["argument"])
            self.assertTrue(options[alias]["attached"])
        journal = options_for(profile_for("journalctl"))
        self.assertTrue(journal["--boot="]["argument_optional"])
        self.assertTrue(journal["--lines="]["argument_optional"])
        self.assertTrue(options_for(profile_for("fzf"))["--multi"]["argument_optional"])
        self.assertNotIn("\\dt", options_for(profile_for("psql")))
        self.assertNotIn("--exec", options_for(profile_for("fd")))
        self.assertEqual(profile_for("fd")["categories"], profile_for("fdfind")["categories"])
        self.assertEqual(profile_for("yq eval")["identity"], "mikefarah-yq-v4")

    def test_every_curated_entry_preserves_whitespace_unicode_and_cursor(self):
        for case in CASES:
            command = case["command"]
            profile = profile_for(command)
            for option in options_for(profile).values():
                prefix = command + " \t "
                query = option["flag"][:2] if option.get("kind") == "keyword" else "--part"
                suffix = "  'café/日本 file'"
                line = prefix + query + suffix
                with self.subTest(command=command, flag=option["flag"]):
                    context = context_for(line, len(prefix) + 1, profile)
                    edited, point = insert_option(context, option)
                    self.assertEqual(edited, prefix + option["flag"] + suffix)
                    self.assertEqual(point, len(prefix + option["flag"]) + (0 if option["flag"].endswith("=") else 1))
                    self.assertNotIn(option.get("argument", "NOT_A_VALUE") or "NOT_A_VALUE", edited)

    def test_values_are_opaque_and_missing_values_block_parent_options(self):
        for case in CASES:
            command = case["command"]
            profile = profile_for(command)
            for option in options_for(profile).values():
                if not option.get("argument") or option.get("argument_optional") or option["flag"].endswith("="):
                    continue
                with self.subTest(command=command, flag=option["flag"]):
                    line = command + " " + option["flag"] + " "
                    with self.assertRaises(HelpError):
                        context_for(line, len(line), profile)
                    for value in ("'café 日本'", "'-123'", "'--child-option'", "'$(literal text)'"):
                        completed = line + value + " "
                        self.assertEqual(context_for(completed, len(completed), profile).query, "")
                    if option.get("attached"):
                        completed = command + " " + option["flag"] + "value "
                        self.assertEqual(context_for(completed, len(completed), profile).query, "")

    def test_child_commands_expressions_and_end_markers_are_not_parent_options(self):
        boundaries = {
            "ssh": "host.example printf --child", "scp": "'local file' host:remote",
            "sftp": "host.example", "podman run": "image sh --child",
            "podman exec": "container sh --child", "podman build": ".",
            "yq eval": "'.value == \"--inplace\"' input.yml", "ss": "state connected",
            "fd": "pattern directory", "fdfind": "pattern directory", "fzf": "unexpected-positional",
        }
        for command, suffix in boundaries.items():
            line = command + " " + suffix + " --"
            with self.subTest(command=command), self.assertRaises(HelpError):
                context_for(line, len(line), profile_for(command))
        for case in CASES:
            line = case["command"] + " -- --"
            with self.subTest(command=case["command"]), self.assertRaises(HelpError):
                context_for(line, len(line), profile_for(case["command"]))

    def test_ip_keywords_are_literal_arguments_and_values_are_not_keywords(self):
        for command in ("ip address", "ip link", "ip route"):
            profile = profile_for(command)
            line = command + " show de"
            context = context_for(line, len(line), profile)
            self.assertEqual(insert_option(context, options_for(profile)["dev"]), (command + " show dev ", len(command + " show dev ")))
            line = command + " show dev "
            with self.assertRaises(HelpError):
                context_for(line, len(line), profile)
            completed = line + "'日本 interface' "
            self.assertEqual(context_for(completed, len(completed), profile).query, "")
            unknown = command + " arbitrary"
            with self.assertRaises(HelpError):
                context_for(unknown, len(unknown), profile)
            for suffix in ("arbitrary ", "add 192.0.2.1/24 dev eth0 ", "show dev eth0 unknown "):
                line = command + " " + suffix
                with self.subTest(line=line), self.assertRaises(HelpError):
                    context_for(line, len(line), profile)

    def test_profiles_work_without_discovery_except_vendor_identity_gate(self):
        for case in CASES:
            command = case["command"]
            profile = profile_for(command)
            line = command + " "
            callback = Mock(side_effect=HelpError("discovery disabled"))
            with self.subTest(command=command):
                if profile.get("identity"):
                    with self.assertRaises(HelpError):
                        find_context(line, len(line), [profile], discover=callback, driver_registry=REGISTRY)
                    callback.assert_called_once()
                else:
                    self.assertEqual(find_context(line, len(line), [profile], discover=callback, driver_registry=REGISTRY).profile, profile)
                    callback.assert_not_called()

    def test_incomplete_groups_cannot_consume_options_or_end_markers_as_files(self):
        profile = profile_for("esptool write-flash")
        for suffix in ("0x0 -- --flash-size", "0x0 --flash-size ", "0x0 -- --"):
            line = "esptool write-flash " + suffix
            with self.subTest(line=line), self.assertRaises(HelpError):
                context_for(line, len(line), profile)

    def test_discovery_receives_only_fixed_help_or_manual_routes(self):
        for case in CASES:
            command = case["command"]
            words = command.split()
            route = help_route(words[0], tuple(words[1:]), REGISTRY)
            for mode in ("auto", "man", "off"):
                with self.subTest(command=command, mode=mode), tempfile.TemporaryDirectory() as directory:
                    folder = Path(directory)
                    executable = folder / words[0]
                    executable.write_text("fixture identity", encoding="utf-8")
                    manual = folder / "man"
                    manual.write_text("fixture manual", encoding="utf-8")
                    calls = []
                    def probe(argv, *args, **kwargs):
                        calls.append(argv)
                        if argv[1:] == ["--version"] and words[0] == "yq":
                            return "yq (https://github.com/mikefarah/yq/) version v4.44.3\n"
                        return (FIXTURES / case["fixture"]).read_text(encoding="utf-8")
                    def which(name):
                        return str(manual if name == "man" else executable)
                    with patch("discovery.shutil.which", side_effect=which), patch("discovery.run_probe", side_effect=probe):
                        pending = command + " -- 'pending-private-argument'"
                        def discover_context(name, subcommands=()):
                            return discover(name, Settings(mode=mode, cache_ttl=0), subcommands=subcommands,
                                            driver_registry=REGISTRY)
                        try:
                            find_context(pending, len(command) + 3, [], discover=discover_context,
                                         driver_registry=REGISTRY)
                        except HelpError:
                            self.assertTrue(mode == "off" or not route.manual and mode == "man" or case.get("keyword_sentinels") or words[0] == "yq")
                    if mode == "off":
                        self.assertEqual(calls, [])
                    for argv in calls:
                        if argv[0] == str(manual):
                            self.assertEqual(argv[-1], route.manual)
                            self.assertIn("--", argv)
                        elif argv[1:] == ["--version"] and words[0] == "yq":
                            self.assertEqual(mode, "auto")
                        else:
                            self.assertEqual(mode, "auto")
                            self.assertEqual(argv, [str(executable), *route.arguments])
                        self.assertNotIn("pending-private-argument", argv)


if __name__ == "__main__":
    unittest.main()
