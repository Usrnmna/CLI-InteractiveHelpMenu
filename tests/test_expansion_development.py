"""Check development CLI route contracts, editing boundaries and fixed probes."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import help_route, load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover


FIXTURES = ROOT / "tests/fixtures/help"
CASES = json.loads((FIXTURES / "expansion-development.json").read_text(encoding="utf-8"))
CAPTURES = json.loads((FIXTURES / "expansion-development-captured.json").read_text(encoding="utf-8"))
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")

# Maintained independently of the profile files and parser-produced metadata.
SENTINELS = {
    "pytest": ("-k", "EXPRESSION", 1),
    "ruff check": ("--select", "RULES", 1),
    "ruff format": ("--check", "", 0),
    "uv sync": ("--extra", "EXTRA", 1),
    "uv add": ("--group", "GROUP", 1),
    "uv lock": ("--upgrade-package", "PACKAGE", 1),
    "uv venv": ("--prompt", "PROMPT", 1),
    "uv tool install": ("--with", "PACKAGE", 1),
    "go build": ("-ldflags", "FLAGS", 1),
    "go test": ("-run", "REGEXP", 1),
    "go run": ("-exec", "COMMAND", 1),
    "go mod tidy": ("-compat", "VERSION", 1),
    "dotnet build": ("--configuration", "CONFIGURATION", 1),
    "dotnet test": ("--filter", "EXPRESSION", 1),
    "dotnet run": ("--project", "PROJECT", 1),
    "dotnet publish": ("--self-contained", "[BOOL]", 1),
    "dotnet restore": ("--source", "SOURCE", 1),
    "yarn install": ("--mode", "MODE", 1),
    "yarn add": ("--dev", "", 0),
    "yarn run": ("--require", "MODULE", 1),
    "bun run": ("--preload", "MODULE", 1),
    "az account show": ("--query", "QUERY", 1),
    "az vm list": ("--resource-group", "GROUP", 1),
    "az storage blob list": ("--container-name", "CONTAINER", 1),
    "gcloud config list": ("--all", "", 0),
    "gcloud compute instances list": ("--filter", "EXPRESSION", 1),
    "gcloud storage ls": ("--recursive", "", 0),
    "git stash": ("--message", "MESSAGE", 1),
    "git stash push": ("--pathspec-from-file", "FILE", 1),
    "git stash pop": ("--index", "", 0),
    "git stash apply": ("--index", "", 0),
    "git stash list": ("--max-count=", "COUNT", 1),
    "git stash show": ("--name-status", "", 0),
    "git worktree": ("-h", "", 0),
    "git worktree add": ("--reason", "REASON", 1),
    "git worktree list": ("--porcelain", "", 0),
    "git worktree remove": ("--force", "", 0),
    "git worktree prune": ("--expire", "TIME", 1),
    "pio run": ("--environment", "ENVIRONMENT", 1),
    "pio device monitor": ("--baud", "BAUD", 1),
    "platformio run": ("--environment", "ENVIRONMENT", 1),
    "platformio device monitor": ("--baud", "BAUD", 1),
    "esptool write-flash": ("--flash-mode", "MODE", 1),
    "esptool.py write-flash": ("--flash-mode", "MODE", 1),
    "esptool.py write_flash": ("--flash_mode", "MODE", 1),
    "arduino-cli compile": ("--fqbn", "FQBN", 1),
}


def options(profile):
    """Index literal insertions while retaining their declared argument metadata."""
    return {entry["flag"]: entry for category in profile["categories"] for entry in category["options"]}


def specimen(case):
    return (FIXTURES / case["fixture"]).read_text(encoding="utf-8")


def profile_for(case):
    """Use curated route metadata where needed, otherwise parse the version specimen."""
    if case.get("profile"):
        return json.loads((ROOT / "profiles" / case["profile"]).read_text(encoding="utf-8"))
    return build_profile(case["command"].split(), [("specimen", specimen(case))])


def context_for(line, point, profile):
    """Supply a deterministic identity callback without launching an executable."""
    return find_context(line, point, [profile], discover=lambda *args, **kwargs: profile,
                        driver_registry=REGISTRY)


class DevelopmentExpansionTests(unittest.TestCase):
    def test_every_required_development_path_has_independent_metadata_and_provenance(self):
        self.assertEqual(set(SENTINELS), {case["command"] for case in CASES})
        self.assertEqual(len(CASES), len(SENTINELS))
        for case in CASES:
            with self.subTest(command=case["command"]):
                self.assertTrue(case["provenance"]["source"].startswith("https://"))
                self.assertIn("hand-authored", case["provenance"]["kind"])
                profile = profile_for(case)
                validate_profile(profile, Path(case["fixture"]))
                flag, argument, count = SENTINELS[case["command"]]
                entry = options(profile)[flag]
                self.assertEqual(entry.get("argument", ""), argument)
                self.assertEqual(entry.get("argument_count", 1) if argument else 0, count)
                self.assertEqual(resolve_path(case["command"].split(), [], REGISTRY).words,
                                 tuple(case["command"].split()))

    def test_specimens_retain_aliases_argument_shapes_and_exclusions(self):
        for case in CASES:
            with self.subTest(command=case["command"]):
                parsed = options(build_profile(case["command"].split(), [("specimen", specimen(case))]))
                self.assertEqual({flag: entry["argument"] for flag, entry in parsed.items()}, case["flags"])
                self.assertFalse(set(case["excluded"]) & parsed.keys())
                for flag, argument in case["flags"].items():
                    self.assertEqual(parsed[flag].get("argument_optional", False), argument.startswith("["))
        for command, left, right in (("pytest", "-x", "--exitfirst"),
                                     ("dotnet build", "-c", "--configuration"),
                                     ("pio run", "-e", "--environment"),
                                     ("git worktree remove", "-f", "--force")):
            case = next(case for case in CASES if case["command"] == command)
            indexed = options(profile_for(case))
            self.assertEqual(indexed[left]["argument"], indexed[right]["argument"])

    def test_each_literal_replacement_preserves_unicode_quotes_whitespace_and_cursor(self):
        for case in CASES:
            profile = profile_for(case)
            for entry in options(profile).values():
                prefix = case["command"] + "\t  "
                fragment = "ad" if entry.get("kind") == "keyword" else "--par"
                suffix = "  'café 日本 files'  \"literal value\""
                line = prefix + fragment + suffix
                with self.subTest(command=case["command"], flag=entry["flag"]):
                    context = context_for(line, len(prefix) + 1, profile)
                    edited, point = insert_option(context, entry)
                    self.assertEqual(edited, prefix + entry["flag"] + suffix)
                    self.assertEqual(point, len(prefix + entry["flag"]) + (not entry["flag"].endswith("=")))
                    self.assertNotIn(entry.get("argument", "PLACEHOLDER") or "PLACEHOLDER", edited)

    def test_required_values_attached_values_negative_values_and_incomplete_input(self):
        for case in CASES:
            profile = profile_for(case)
            for entry in options(profile).values():
                if not entry.get("argument") or entry.get("argument_optional"):
                    continue
                flag = entry["flag"]
                if flag.endswith("="):
                    continue
                with self.subTest(command=case["command"], flag=flag):
                    incomplete = case["command"] + " " + flag + " "
                    with self.assertRaises(HelpError):
                        context_for(incomplete, len(incomplete), profile)
                    for value in ("'日本 value'", "-1", "'--expression-flag'"):
                        line = incomplete + value + " --"
                        self.assertEqual(context_for(line, len(line), profile).query, "--")
                    attached = case["command"] + " " + flag + "='quoted 日本' --"
                    self.assertEqual(context_for(attached, len(attached), profile).query, "--")

    def test_runner_child_commands_and_end_markers_are_not_parent_options(self):
        runners = {"go run", "dotnet run", "yarn run", "bun run"}
        for case in CASES:
            profile = profile_for(case)
            line = case["command"] + " -- '--child-value' --"
            with self.subTest(command=case["command"]), self.assertRaises(HelpError):
                context_for(line, len(line), profile)
            if case["command"] in runners:
                for child in ("'script 日本'", "package", "app.dll"):
                    line = case["command"] + " " + child + " --"
                    with self.subTest(command=case["command"], child=child), self.assertRaises(HelpError):
                        context_for(line, len(line), profile)

    def test_test_routes_allow_options_after_packages_and_projects_until_child_boundary(self):
        for command, before, flag, after in (
            ("go test", "go test './日本 package' ./...  -ru", "-run",
             "go test './日本 package' ./...  -run "),
            ("dotnet test", "dotnet test '日本 project/tests.csproj'  --fi", "--filter",
             "dotnet test '日本 project/tests.csproj'  --filter "),
        ):
            profile = profile_for(next(case for case in CASES if case["command"] == command))
            with self.subTest(command=command):
                self.assertFalse(profile["stop_at_positional"])
                route = help_route(command.split()[0], tuple(command.split()[1:]), REGISTRY)
                self.assertFalse(route.stop_at_positional)
                context = context_for(before, len(before), profile)
                self.assertEqual(insert_option(context, options(profile)[flag]), (after, len(after)))
                line = after + "'Name~日本|Name~--flag' --"
                self.assertEqual(context_for(line, len(line), profile).query, "--")
                for suffix in (" -- --", " -- child --"):
                    line = command + " 'project 日本'" + suffix
                    with self.assertRaises(HelpError):
                        context_for(line, len(line), profile)
        case = next(case for case in CASES if case["command"] == "go test")
        profile = profile_for(case)
        self.assertEqual(profile["stop_at_options"], ["-args"])
        self.assertEqual(help_route("go", ("test",), REGISTRY).stop_at_options, ("-args",))
        for line in ("go test ./... -args -ru", "go test -args --", "go test ./... -args '日本' --"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                context_for(line, len(line), profile)

    def test_curated_leaf_options_do_not_inherit_other_git_commands(self):
        exclusions = {"git stash pop": {"--message", "--patch", "--include-untracked"},
                      "git stash apply": {"--message", "--pathspec-from-file"},
                      "git worktree remove": {"--porcelain", "--expire", "-b"},
                      "git worktree list": {"--force", "--expire", "--detach"}}
        for command, excluded in exclusions.items():
            case = next(case for case in CASES if case["command"] == command)
            self.assertFalse(options(profile_for(case)).keys() & excluded)

    def test_worktree_keyword_insertion_and_leaf_transition(self):
        root = profile_for(next(case for case in CASES if case["command"] == "git worktree"))
        line = "git worktree ad"
        context = context_for(line, len(line), root)
        self.assertEqual(insert_option(context, options(root)["add"]), ("git worktree add ", 17))
        leaf = profile_for(next(case for case in CASES if case["command"] == "git worktree add"))
        line = "git worktree add --"
        self.assertEqual(find_context(line, len(line), [root, leaf], driver_registry=REGISTRY).profile["command"],
                         ["git", "worktree", "add"])

    def test_esptool_groups_and_spelling_are_explicit(self):
        for command, flag, rejected in (("esptool write-flash", "--flash-mode", "--flash_mode"),
                                        ("esptool.py write-flash", "--flash-mode", "--flash_mode"),
                                        ("esptool.py write_flash", "--flash_mode", "--flash-mode")):
            profile = profile_for(next(case for case in CASES if case["command"] == command))
            self.assertNotIn(rejected, options(profile))
            self.assertEqual(profile["positional_group"],
                             {"argument": "ADDRESS FILE", "argument_count": 2, "repeatable": True})
            for suffix in (" 0x1000 ", " 0x1000 'firmware 日本.bin' 0x8000 "):
                line = command + suffix
                with self.assertRaises(HelpError):
                    context_for(line, len(line), profile)
            line = command + " 0x1000 'firmware 日本.bin' 0x8000 second.bin --"
            context = context_for(line, len(line), profile)
            edited, _ = insert_option(context, options(profile)[flag])
            self.assertEqual(edited, line[:-2] + flag + " ")
            self.assertNotIn("ADDRESS FILE", edited)

    def test_global_values_never_become_command_words(self):
        cases = (("go -C '日本 source' mod tidy --", "go mod tidy"),
                 ("uv --directory '日本 source' tool install --", "uv tool install"),
                 ("az --subscription 'private sub' storage blob list --", "az storage blob list"),
                 ("gcloud --project='private project' compute instances list --", "gcloud compute instances list"),
                 ("esptool --port /dev/ttyUSB0 --baud 460800 write-flash --", "esptool write-flash"))
        for line, command in cases:
            profile = profile_for(next(case for case in CASES if case["command"] == command))
            with self.subTest(line=line):
                self.assertEqual(context_for(line, len(line), profile).profile["command"], command.split())

    def test_fixed_probes_never_receive_pending_values_actions_or_prefixes(self):
        for case in CASES:
            words = case["command"].split()
            route = help_route(words[0], tuple(words[1:]), REGISTRY)
            fixed = list(route.arguments)
            if words == ["pytest"]:
                fixed = ["--help", "--noconftest"]
            if words == ["yarn", "run"]:
                fixed = ["run", "-h=1"]
            calls = []

            def probe(argv, *args, **kwargs):
                calls.append(argv)
                if words[0] == "yarn" and argv[1:] == ["--version"]:
                    return "4.9.4"
                if words[0] in ("esptool", "esptool.py") and argv[1:] == ["--help"]:
                    return "esptool v5.1.0" if words[1] == "write-flash" else "esptool.py v4.8.1"
                return specimen(case)

            def lookup(executable, **kwargs):
                return sys.executable

            callback = lambda executable, **kwargs: discover(executable, Settings(cache_ttl=0),
                driver_registry=REGISTRY, **kwargs)
            line = case["command"] + " -- 'private 日本 operand'"
            point = len(case["command"] + " --")
            with self.subTest(command=case["command"]), patch("discovery.run_probe", side_effect=probe), \
                    patch("discovery.shutil.which", side_effect=lookup):
                context = find_context(line, point, [], discover=callback, driver_registry=REGISTRY)
                self.assertEqual(context.profile["command"], words)
                for argv in calls:
                    is_manual = "--no-hyphenation" in argv
                    self.assertTrue(is_manual or argv[1:] in (fixed, ["--help"], ["--version"]))
                    self.assertFalse(any("private" in argument or "日本" in argument for argument in argv))
                self.assertTrue(calls)

    def test_manual_and_disabled_modes_do_not_issue_executable_help(self):
        for case in CASES:
            words = case["command"].split()
            profile = profile_for(case)
            route = help_route(words[0], tuple(words[1:]), REGISTRY)
            for mode in ("man", "off"):
                with self.subTest(command=case["command"], mode=mode), \
                        patch("discovery.shutil.which", return_value=sys.executable), \
                        patch("discovery.run_probe", return_value=specimen(case)) as probe:
                    callback = lambda executable, **kwargs: discover(executable, Settings(mode=mode, cache_ttl=0),
                        driver_registry=REGISTRY, **kwargs)
                    line = case["command"] + " --"
                    if case.get("profile") and not profile.get("identity"):
                        self.assertEqual(find_context(line, len(line), [profile], discover=callback,
                            driver_registry=REGISTRY).profile["command"], words)
                        probe.assert_not_called()
                    else:
                        with self.assertRaises(HelpError):
                            find_context(line, len(line), [profile] if case.get("profile") else [],
                                discover=callback, driver_registry=REGISTRY)
                        probe.assert_not_called()
                    if mode == "man" and route.manual:
                        discover(words[0], Settings(mode=mode, cache_ttl=0), subcommands=tuple(words[1:]),
                                 driver_registry=REGISTRY)
                        self.assertTrue(all("--no-hyphenation" in call.args[0] for call in probe.call_args_list))

    def test_real_yarn_major_versions_keep_distinct_option_sets_and_arity(self):
        expected = {("classic", "install"): {"--frozen-lockfile", "--production", "--ignore-scripts"},
                    ("modern", "install"): {"--immutable", "--immutable-cache", "--mode"},
                    ("classic", "add"): {"--dev", "--peer", "--exact"},
                    ("modern", "add"): {"--dev", "--peer", "--exact"},
                    ("classic", "run"): {"--silent", "--cwd", "--scripts-prepend-node-path"},
                    ("modern", "run"): {"--inspect", "--top-level", "--require"}}
        for (variant, command), sentinels in expected.items():
            capture = CAPTURES[f"yarn {command} ({variant})"]
            with self.subTest(variant=variant, command=command):
                self.assertEqual(capture["returncode"], 0)
                self.assertIn("temporary HOME", capture["environment"])
                profile = build_profile(["yarn", command], [("capture", capture["text"])])
                parsed = options(profile)
                self.assertTrue(sentinels <= parsed.keys(), sentinels - parsed.keys())
                if variant == "modern" and command in ("install", "run"):
                    entry = parsed["--mode" if command == "install" else "--require"]
                    self.assertEqual(entry["argument"], "#0")
                    self.assertEqual(entry.get("argument_count", 1), 1)
                    line = "yarn " + command + " " + entry["flag"] + " "
                    with self.assertRaises(HelpError):
                        context_for(line, len(line), profile)
                if variant == "classic":
                    self.assertNotIn("--immutable", parsed)
                elif command == "run":
                    self.assertNotIn("--production", parsed)
        self.assertEqual(CAPTURES["yarn run"]["status"], "unsupported")

    def test_available_help_captures_satisfy_independent_live_sentinels(self):
        for case in CASES:
            capture = CAPTURES.get(case["command"], {})
            if "text" not in capture:
                continue
            with self.subTest(command=case["command"]):
                self.assertEqual(capture["returncode"], 0)
                self.assertTrue(capture["version"])
                self.assertIn("temporary HOME", capture["environment"])
                parsed = options(build_profile(case["command"].split(), [("capture", capture["text"])]))
                self.assertTrue(set(case["live_flags"]) <= parsed.keys())
                for flag, count in case["live_argument_counts"].items():
                    self.assertTrue(parsed[flag]["argument"])
                    self.assertEqual(parsed[flag].get("argument_count", 1), count)
                for keyword in case.get("keyword_sentinels", []):
                    self.assertIn(keyword, capture["text"])


if __name__ == "__main__":
    unittest.main()
