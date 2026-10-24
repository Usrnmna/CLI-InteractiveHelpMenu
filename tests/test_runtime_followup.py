"""Check runtime compatibility against installed-version help and source captures."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import help_route, load_driver_registry
from core import HelpError, find_context, insert_option


FIXTURE = json.loads((ROOT / "tests/fixtures/help/runtime-followup-captured.json").read_text(encoding="utf-8"))
CAPTURES = {entry["command"]: entry for entry in FIXTURE["captures"]}
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")

# Independent contracts transcribed from leaf help, referenced Go build/testflag
# help, and exact SDK source for options whose aliases are hidden from help.
# Tuples contain required single values, zero-value flags, and optional values.
CONTRACTS = {
    "go build": ("-o -tags -ldflags -gcflags -mod", "-v -n -x -race -trimpath", ""),
    "go test": ("-run -bench -count -timeout -coverprofile -o -tags -ldflags -gcflags -mod",
                "-cover -json -failfast -v -n -x -race -trimpath", ""),
    "go run": ("-exec -tags -ldflags -gcflags -mod", "-v -n -x -race -trimpath", ""),
    "go mod tidy": ("-go -compat", "-e -v -x -diff", ""),
    "dotnet build": ("-c --configuration -f --framework -r --runtime -o --output -v --verbosity",
                     "--no-restore --nologo --no-incremental --no-dependencies --force", ""),
    "dotnet test": ("-c --configuration -f --framework -r --runtime -o --output -v --verbosity "
                    "--filter --logger --results-directory --collect",
                    "--no-restore --nologo --no-build --list-tests", ""),
    "dotnet run": ("-c --configuration -f --framework -r --runtime --project --launch-profile -v --verbosity",
                   "--no-launch-profile --no-build --no-restore", ""),
    "dotnet publish": ("-c --configuration -f --framework -r --runtime -o --output -v --verbosity",
                       "--no-restore --nologo --no-build --no-self-contained --use-current-runtime", "--self-contained"),
    "dotnet restore": ("-s --source --packages --configfile -r --runtime -v --verbosity",
                       "--disable-parallel --ignore-failed-sources --no-cache --force --locked-mode --use-lock-file", ""),
    "bun run": ("--cwd --env-file --preload", "--watch --hot --bun --silent --if-present", ""),
    "arduino-cli compile": ("-b --fqbn --board-options --build-path --output-dir --build-property --libraries --warnings -j --jobs",
                            "--clean --export-binaries -v --verbose --only-compilation-database", ""),
}


def profile_for(command):
    """Read the maintained static profile independently of captured declarations."""
    return json.loads((ROOT / "profiles" / (command.replace(" ", "-") + ".json")).read_text(encoding="utf-8"))


def options_for(profile):
    return {entry["flag"]: entry for category in profile["categories"] for entry in category["options"]}


class RuntimeFollowupTests(unittest.TestCase):
    def test_all_eleven_routes_have_versioned_fixed_help_and_verified_archives(self):
        self.assertEqual(len(CONTRACTS), 11)
        self.assertTrue(set(CONTRACTS).issubset(CAPTURES))
        for command in CONTRACTS:
            with self.subTest(command=command):
                words = command.split()
                capture = CAPTURES[command]
                self.assertEqual(capture["argv"], [words[0], *help_route(words[0], tuple(words[1:]), REGISTRY).arguments])
                self.assertTrue(capture["version"])
                self.assertGreater(len(capture["output"]), 100)
        self.assertEqual({entry["name"] for entry in FIXTURE["installations"]}, {"go", "dotnet", "bun", "arduino"})
        for entry in FIXTURE["installations"]:
            self.assertEqual(entry["upstream_checksum"], entry["verified_checksum"])
            self.assertTrue(entry["archive_url"].startswith("https://"))
            self.assertFalse(entry["system_install"])

    def test_every_curated_runtime_option_matches_independent_arity_contract(self):
        for command, (required, switches, optional) in CONTRACTS.items():
            with self.subTest(command=command):
                options = options_for(profile_for(command))
                self.assertEqual(set(options), set((required + " " + switches + " " + optional).split()))
                for flag in required.split():
                    self.assertTrue(options[flag]["argument"], flag)
                    self.assertFalse(options[flag]["argument_optional"], flag)
                    self.assertEqual(options[flag].get("argument_count", 1), 1, flag)
                for flag in switches.split():
                    self.assertFalse(options[flag]["argument"], flag)
                for flag in optional.split():
                    self.assertTrue(options[flag]["argument"], flag)
                    self.assertTrue(options[flag]["argument_optional"], flag)

    def test_all_option_names_have_leaf_inherited_or_exact_source_evidence(self):
        source = "\n".join(entry["output"] for entry in FIXTURE["source_excerpts"])
        for command in CONTRACTS:
            text = CAPTURES[command]["output"]
            if command in ("go run", "go test"):
                text += CAPTURES["go help build"]["output"].split("The build flags are shared", 1)[1]
            if command == "go test":
                text += CAPTURES["go help testflag"]["output"]
            for flag in options_for(profile_for(command)):
                with self.subTest(command=command, flag=flag):
                    # SDK help suppresses some accepted aliases and implicit
                    # restore options. These require separately captured source.
                    hidden = command.startswith("dotnet ") and flag in ("--verbosity", "--nologo", "--no-cache", "--force")
                    evidence = text + (source if hidden else "")
                    self.assertRegex(evidence, r"(?<![\w-])" + re.escape(flag) + r"(?![\w-])")

    def test_go_run_excludes_build_only_output_and_preserves_child_boundary(self):
        run = profile_for("go run")
        self.assertNotIn("-o", options_for(run))
        self.assertIn("-o", options_for(profile_for("go build")))
        self.assertIn("-o", options_for(profile_for("go test")))
        self.assertNotIn("-o", CAPTURES["go run"]["output"])
        self.assertIn("For more about build flags, see 'go help build'.", CAPTURES["go run"]["output"])
        for line in ('go run "main \u96ea.go" --race', 'go run . --race'):
            with self.assertRaises(HelpError):
                find_context(line, len(line), [run], driver_registry=REGISTRY)

    def test_sdk_hidden_aliases_and_optional_boolean_have_exact_source_evidence(self):
        source = "\n".join(entry["output"] for entry in FIXTURE["source_excerpts"])
        self.assertIn('"--verbosity", "-v", "--v", "-verbosity"', source)
        self.assertIn('"--no-logo", "--nologo", "-nologo"', source)
        self.assertIn('new Option<bool>("--no-cache")', source)
        self.assertIn('new Option<bool>("--self-contained", "--sc")', source)
        self.assertIn("Arity = ArgumentArity.ZeroOrOne", source)
        self.assertIn("ImplicitRestoreOptions.AddTo(Options)", source)
        self.assertTrue(all("a8dd0577c5c13f43a2f57fe33b4ff11b90f6371e" in entry["source"]
                            for entry in FIXTURE["source_excerpts"] if "dotnet" in entry["source"]))

    def test_literal_edits_preserve_quoted_values_and_prefix_offsets(self):
        for command in CONTRACTS:
            profile = profile_for(command)
            for flag, option in options_for(profile).items():
                with self.subTest(command=command, flag=flag):
                    prefix = "command -- env MODE='\u96ea value' "
                    line = prefix + command + "  --"
                    context = find_context(line, len(line), [profile], driver_registry=REGISTRY)
                    expected = prefix + command + "  " + flag + " "
                    self.assertEqual(insert_option(context, option), (expected, len(expected)))
        profile = profile_for("dotnet publish")
        line = 'dotnet publish --self-contained false --'
        context = find_context(line, len(line), [profile], driver_registry=REGISTRY)
        expected = 'dotnet publish --self-contained false --no-restore '
        self.assertEqual(insert_option(context, options_for(profile)["--no-restore"]), (expected, len(expected)))


if __name__ == "__main__":
    unittest.main()
