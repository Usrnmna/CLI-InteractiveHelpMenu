"""Verify driver loading, extension, validation, and help-only process isolation."""

import copy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from core import HelpError, find_context, insert_option
from command_paths import help_route, load_driver_registry, resolve_path
from discovery import Settings, discover
from drivers import parse_driver


def driver_document():
    return {"command": "newtool", "global_values": ["--config"], "global_flags": ["--quiet"],
            "paths": [{"command": ["image", "convert"], "help": ["help", "image", "convert"],
                       "man": None, "stop_at_positional": True}]}


def install_driver_fixture(folder):
    """Create a driver and executable that flags every non-help invocation."""
    drivers = folder / "drivers"
    binaries = folder / "bin"
    drivers.mkdir()
    binaries.mkdir()
    (drivers / "newtool.json").write_text(json.dumps(driver_document()))
    log = folder / "calls"
    marker = folder / "executed"
    write_executable(binaries / "newtool",
                     "import json, pathlib, sys\n"
                     f"with open({str(log)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                     "if sys.argv[1:] not in (['help', 'image', 'convert'], ['--help']):\n"
                     f"    pathlib.Path({str(marker)!r}).write_text('action dispatched')\n"
                     "print('Conversion options:\\n  --quality VALUE   Set quality\\n  --fast   Enable faster conversion')\n")
    return drivers, binaries, log, marker


class DriverValidationTests(unittest.TestCase):
    def test_example_drivers_load_without_installed_programs(self):
        registry = load_driver_registry(ROOT / "config/drivers.example")
        self.assertEqual(help_route("pip", ("install",), registry).arguments, ("help", "install"))
        self.assertEqual(help_route("npm", ("install",), registry).arguments, ("--help", "install"))
        self.assertEqual(help_route("npm", ("install",), registry).manual, "npm-install")
        self.assertIn("git", registry)

    def test_malformed_driver_fields_are_rejected(self):
        for field, values in {"command": [None, [], "../tool", "tool;bad", "-tool"],
                              "global_values": [None, {}, ["--x", "--x"], ["--x=value"]],
                              "global_flags": [["--config"]], "paths": [None, [], {}], "unknown": [True]}.items():
            for value in values:
                document = driver_document()
                document[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    parse_driver(document)

    def test_routes_reject_templates_shell_text_and_action_first_argv(self):
        changes = [("help", ["convert", "--help"]), ("help", ["--help", "$(touch marker)"]),
                   ("help", ["help", "{pending}"]), ("help", ["help", "two words"]),
                   ("help", ["help", "bad\nword"]), ("command", ["--option"]),
                   ("man", "../manual"), ("stop_at_positional", "true"), ("unknown", True)]
        for field, value in changes:
            document = driver_document()
            document["paths"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                parse_driver(document)

    def test_empty_sources_and_duplicate_routes_are_rejected(self):
        for document in [{"command": "tool", "paths": [{"command": [], "help": [], "man": None}]},
                         {**driver_document(), "paths": driver_document()["paths"] * 2}]:
            with self.assertRaises(ValueError):
                parse_driver(document)

    def test_suffix_help_must_match_the_exact_declared_path(self):
        for selector in ("help", "--help", "-help", "-h"):
            document = driver_document()
            document["paths"][0]["help"] = ["image", "convert", selector]
            name, driver = parse_driver(document)
            self.assertEqual(driver.paths[("image", "convert")].arguments, ("image", "convert", selector))
        for arguments in (["convert", "--help"], ["image", "delete", "--help"],
                          ["image", "convert", "private-file", "--help"],
                          ["image", "convert", "--output=private", "--help"], ["image", "convert"]):
            document = driver_document()
            document["paths"][0]["help"] = arguments
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                parse_driver(document)

    def test_unknown_programs_keep_generic_root_discovery(self):
        registry = load_driver_registry()
        self.assertEqual(help_route("unknown-tool", (), registry).arguments, ("--help",))
        with self.assertRaises(ValueError):
            help_route("unknown-tool", ("action",), registry)

    def test_parent_route_can_have_options_and_child_commands(self):
        document = driver_document()
        document["paths"].append({"command": ["image"], "help": ["help", "image"]})
        name, driver = parse_driver(document)
        registry = {name: driver}
        path = resolve_path(["newtool", "image", "--verbose"], [], registry)
        self.assertEqual(path.words, ("newtool", "image"))
        self.assertEqual(path.argument_start, 2)
        self.assertEqual(resolve_path(["newtool", "image", "convert"], [], registry).words,
                         ("newtool", "image", "convert"))

    def test_manual_only_driver_route_uses_no_target_arguments(self):
        name, driver = parse_driver({"command": "example", "paths": [{"command": ["action"], "man": "example-action"}]})
        route = help_route(name, ("action",), {name: driver})
        self.assertEqual(route.arguments, ())
        self.assertEqual(route.manual, "example-action")

    def test_overlay_replaces_only_the_requested_builtin_route(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "git.json"
            path.write_text(json.dumps({"command": "git", "paths": [{"command": ["commit"], "man": "custom-commit"}]}))
            registry = load_driver_registry(Path(folder))
            self.assertEqual(help_route("git", ("commit",), registry).manual, "custom-commit")
            self.assertEqual(help_route("git", ("branch",), registry).manual, "git-branch")
            self.assertIn("-C", registry["git"].global_values)

    def test_duplicate_program_files_and_arity_conflicts_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            for name in ["a.json", "b.json"]:
                (path / name).write_text(json.dumps(driver_document()))
            with self.assertRaisesRegex(ValueError, "Duplicate executable"):
                load_driver_registry(path)
            (path / "b.json").unlink()
            (path / "a.json").write_text(json.dumps({"command": "git", "global_flags": ["-C"],
                                                    "paths": [{"command": [], "help": ["--help"]}]}))
            with self.assertRaisesRegex(ValueError, "arity"):
                load_driver_registry(path)

    def test_invalid_json_and_oversized_files_fail_without_partial_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            for data in ["not json", "[" * 2000, " " * (256 * 1024 + 1)]:
                path.write_text(data)
                with self.subTest(size=len(data)), self.assertRaises(ValueError):
                    load_driver_registry(Path(folder))

    def test_seeded_schema_mutations_have_controlled_errors(self):
        rng = random.Random(95713)
        values = [None, [], {}, True, 1, "", [None], {"nested": []}, ["--config"], "$(bad)"]
        for index in range(300):
            document = driver_document()
            if rng.choice([True, False]):
                document[rng.choice(list(document))] = rng.choice(values)
            else:
                document["paths"][0][rng.choice(["command", "help", "man", "stop_at_positional"])] = rng.choice(values)
            with self.subTest(seed=95713, case=index):
                try:
                    parse_driver(document)
                except ValueError:
                    pass


class LoadedDriverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.directory, self.binaries, self.log, self.marker = install_driver_fixture(self.folder)
        self.registry = load_driver_registry(self.directory)
        self.settings = Settings(cache_dir=self.folder / "cache")
        self.environment = patch.dict(os.environ, {"PATH": str(self.binaries)})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def context(self, line, point=None):
        return find_context(line, len(line) if point is None else point, [], driver_registry=self.registry,
                            discover=lambda command, subcommands=(): discover(command, self.settings,
                                subcommands=subcommands, driver_registry=self.registry))

    def test_loaded_path_inserts_without_forwarding_pending_arguments(self):
        prefix = "newtool --config 'private config' image convert --fa"
        line = prefix + " 'private input' 'private output'"
        context = self.context(line, len(prefix))
        option = context.profile["categories"][0]["options"][1]
        self.assertEqual(insert_option(context, option)[0], line.replace("--fa ", "--fast "))
        self.assertEqual(json.loads(self.log.read_text()), ["help", "image", "convert"])
        self.assertFalse(self.marker.exists())

    def test_unknown_paths_and_missing_global_values_do_not_probe(self):
        for line in ["newtool --config --", "newtool image unknown --", "newtool --unknown image convert --"]:
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line)
        self.assertFalse(self.log.exists())

    def test_npm_example_driver_uses_help_selector_and_never_forwards_package(self):
        from test_program_corpus import fixture_text
        write_executable(self.binaries / "npm", "import json, pathlib, sys\n"
                         f"pathlib.Path({str(self.log)!r}).write_text(json.dumps(sys.argv[1:]))\n"
                         "if sys.argv[1:] != ['--help', 'install']:\n"
                         f"    pathlib.Path({str(self.marker)!r}).write_text('action dispatched')\n"
                         f"print({fixture_text('npm-install')!r})\n")
        self.registry = load_driver_registry(ROOT / "config/drivers.example")
        line = "npm --prefix private-directory install private-package --dry"
        context = self.context(line)
        option = next(option for category in context.profile["categories"] for option in category["options"]
                      if option["flag"] == "--dry-run")
        self.assertEqual(insert_option(context, option)[0], line[:-5] + "--dry-run ")
        self.assertEqual(json.loads(self.log.read_text()), ["--help", "install"])
        self.assertFalse(self.marker.exists())

    def test_driver_positional_boundary_is_enforced(self):
        with self.assertRaises(HelpError):
            self.context("newtool image convert private-input --")
        self.assertFalse(self.marker.exists())

    def test_changed_help_route_invalidates_cached_profile(self):
        self.context("newtool image convert --")
        document = driver_document()
        document["paths"][0]["help"] = ["--help"]
        (self.directory / "newtool.json").write_text(json.dumps(document))
        self.registry = load_driver_registry(self.directory)
        self.context("newtool image convert --")
        self.assertEqual([json.loads(line) for line in self.log.read_text().splitlines()],
                         [["help", "image", "convert"], ["--help"]])

    def test_cli_check_and_listing_validate_drivers_without_probes(self):
        for mode in ["--check", "--list-drivers"]:
            result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), mode],
                                    env={**os.environ, "CLI_HELP_DRIVERS": str(self.directory)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            if mode == "--list-drivers":
                self.assertIn("newtool image convert", result.stdout)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
