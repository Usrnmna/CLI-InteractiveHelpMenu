"""Independent literal contracts for explicit value forms and opt-in bundles."""

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option, validate_profile
from manual_import import ManualCollection
from ui import cell_width, clip_cells, wrap_cells, escape_delay


PROFILE = {"command": ["typed"], "description": "Fixture", "categories": [{"name": "Options", "options": [
    {"flag": "-a", "bundle": True, "summary": "Alpha"}, {"flag": "-b", "bundle": True, "summary": "Beta"},
    {"flag": "-n", "argument": "N", "argument_style": "attached", "bundle": True, "summary": "Number"},
    {"flag": "-o", "argument": "PATH", "argument_style": "attached_only", "summary": "Output"},
    {"flag": "--value", "argument": "VALUE", "argument_style": "equals", "summary": "Value"},
    {"flag": "--flag", "summary": "Flag"}]}]}


class ArgumentSyntaxTests(unittest.TestCase):
    def test_declared_forms_and_bundles_preserve_literal_input(self):
        for prefix in ("typed -ab ", "typed -abn5 ", "typed -ban -5 ", "typed -o'café dir' ",
                       "typed --value='café value' ", "typed -a -b -n 2 "):
            line = prefix + "--fl\t'suffix file'"
            context = find_context(line, len(prefix + "--fl"), [PROFILE])
            self.assertEqual(insert_option(context, PROFILE["categories"][0]["options"][-1]),
                             (prefix + "--flag\t'suffix file'", len(prefix + "--flag\t")))

    def test_value_style_insertion_places_cursor_before_payload(self):
        for flag, expected in (("-o", "typed -o"), ("--value", "typed --value=")):
            option = next(option for option in PROFILE["categories"][0]["options"] if option["flag"] == flag)
            context = find_context("typed ", len("typed "), [PROFILE])
            self.assertEqual(insert_option(context, option), (expected, len(expected)))

    def test_ambiguous_unknown_missing_and_existing_payloads_fail_safely(self):
        for line, reason in (("typed -ax --fl", "unsupported_option"), ("typed -abn --fl", "option_value_required"),
                             ("typed -o file --fl", "option_value_required"), ("typed --value data --fl", "unsupported_value_form"),
                             ("typed --value= --fl", "option_value_required"), ("typed -ab", "cursor_in_bundle"),
                             ("typed -abn --flag --fl", "option_value_required"),
                             ("typed -a=PRIVATE_SENTINEL --fl", "unsupported_value_form"),
                             ("typed -oPRIVATE_SENTINEL", "cursor_in_value"), ("typed -abnPRIVATE_SENTINEL", "cursor_in_bundle"),
                             ("typed -- child --fl", "end_of_options")):
            with self.subTest(line=line), self.assertRaises(HelpError) as raised:
                find_context(line, len(line), [PROFILE])
            self.assertEqual(raised.exception.code, reason)
            self.assertNotIn("PRIVATE_SENTINEL", str(raised.exception))
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"][0].update(argument="V", argument_style="attached")
        profile["categories"][0]["options"].append({"flag": "-ab", "argument": "V", "argument_style": "attached_only", "summary": "Exact"})
        line = "typed -abVALUE --fl"
        with self.assertRaises(HelpError) as raised:
            find_context(line, len(line), [profile])
        self.assertEqual(raised.exception.code, "ambiguous_short_token")

    def test_exact_names_override_bundle_interpretation_and_boundaries_hold(self):
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"].append({"flag": "-ab", "summary": "Exact flag"})
        self.assertEqual(find_context("typed -ab --fl", len("typed -ab --fl"), [profile]).query, "--fl")
        profile["stop_at_options"] = ["-b"]
        with self.assertRaises(HelpError) as raised:
            find_context("typed -ba --fl", len("typed -ba --fl"), [profile])
        self.assertEqual(raised.exception.code, "child_argument_boundary")

    def test_schema_conflicts_and_legacy_defaults(self):
        validate_profile(PROFILE, Path("fixture"))
        for change in ({"argument_style": []}, {"argument_style": "unknown"}, {"argument_style": "attached_only", "attached": True},
                       {"argument_style": "attached_only", "argument_count": 2}, {"bundle": "true"},
                       {"bundle": True, "flag": "--long"}, {"bundle": True, "argument_optional": True},
                       {"bundle": True, "argument_style": "equals"}):
            profile = copy.deepcopy(PROFILE)
            profile["categories"][0]["options"][2].update(change)
            with self.subTest(change=change), self.assertRaises(HelpError):
                validate_profile(profile, Path("fixture"))
        legacy = copy.deepcopy(PROFILE)
        for option in legacy["categories"][0]["options"]:
            option.pop("bundle", None)
            option.pop("argument_style", None)
        self.assertEqual(find_context("typed --value=one --fl", len("typed --value=one --fl"), [legacy]).query, "--fl")
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"].append({"flag": "--value=", "argument": "V", "summary": "Conflicting alias"})
        with self.assertRaises(HelpError):
            validate_profile(profile, Path("fixture"))

    def test_metadata_survives_collection_import_review_save(self):
        with tempfile.TemporaryDirectory() as directory:
            with ManualCollection(Path(directory)) as collection:
                result = collection.save(PROFILE, "typed")
            self.assertEqual(json.loads(Path(result["profile"]).read_text()), PROFILE)
            with ManualCollection(Path(directory)) as collection:
                result = collection.save_documents(PROFILE, {"command": "typed", "paths": [{"command": [], "help": [], "man": "typed"}]}, replace=True)
            self.assertEqual(json.loads(Path(result["profile"]).read_text()), PROFILE)

    def test_required_component_and_explicit_separate_forms_remain_distinct(self):
        profile = copy.deepcopy(PROFILE)
        value = profile["categories"][0]["options"][2]
        value.update(argument="HOST[:PORT]", argument_style="separate")
        for prefix in ("typed -n host ", "typed -abn -5 "):
            self.assertEqual(find_context(prefix + "--fl", len(prefix + "--fl"), [profile]).query, "--fl")
        for line in ("typed -nHOST --fl", "typed -n=HOST --fl", "typed -abnHOST --fl", "typed -n --fl"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [profile])

    def test_optional_attached_only_value_is_not_a_required_component(self):
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"][3]["argument_optional"] = True
        for prefix in ("typed -o ", "typed -o'café dir' "):
            self.assertEqual(find_context(prefix + "--fl", len(prefix + "--fl"), [profile]).query, "--fl")
        for value in ("-o'café dir'", "-abn5"):
            line = "typed " + value + " --fl 'suffix 日本'"
            for point in (len("typed "), len("typed ") + 2, len("typed " + value)):
                with self.subTest(value=value, point=point), self.assertRaises(HelpError):
                    find_context(line, point, [profile])

    def test_seven_zip_leaf_profile_preserves_values_and_uses_only_fixed_help(self):
        from command_paths import help_route, load_driver_registry
        registry = load_driver_registry(ROOT / "config/drivers.example")
        for name in ("7z", "7zz"):
            profile = json.loads((ROOT / "profiles" / (name + "-x.json")).read_text())
            options = {option["flag"]: option for category in profile["categories"] for option in category["options"]}
            self.assertEqual(set(options), {"-o", "-t", "-y", "-bd"})
            for flag, argument in (("-o", "Directory"), ("-t", "Type")):
                self.assertEqual(options[flag]["argument"], argument)
                self.assertEqual(options[flag]["argument_style"], "attached_only")
                self.assertFalse(options[flag].get("argument_optional", False))
            capture = json.loads((ROOT / "tests/fixtures/help/syntax-7zip-captured.json").read_text())[name]
            self.assertEqual(capture["source_arguments"], ["-h"])
            self.assertIn("23.01", capture["version"])
            self.assertEqual(capture["text"], (ROOT / "tests/fixtures/help" / ("syntax-" + name + "-x.txt")).read_text())
            self.assertEqual(help_route(name, (), registry).arguments, ("-h",))
            with self.assertRaises(ValueError):
                help_route(name, ("x",), registry)
            line = name + " x 'archive.7z' -o'café dir' -tzip -y"
            lookup = Mock(return_value=profile)
            context = find_context(line, len(line), [profile], discover=lookup, driver_registry=registry)
            lookup.assert_not_called()
            self.assertEqual(insert_option(context, profile["categories"][0]["options"][2]), (line + " ", len(line) + 1))

    def test_bounded_openssh_bundles_keep_the_destination_boundary(self):
        profile = json.loads((ROOT / "profiles/ssh.json").read_text())
        for prefix in ("ssh -vCp22 ", "ssh -vv -p 22 ", "ssh -4q "):
            self.assertEqual(find_context(prefix + "-i", len(prefix + "-i"), [profile]).query, "-i")
        for line in ("ssh -vCp --fl", "ssh -vZ -i", "ssh -vCp22 host -i", "ssh -vCp22 -- -i"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [profile])

    def test_new_errors_and_passive_reports_omit_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "typed.json").write_text(json.dumps(PROFILE))
            environment = {key: value for key, value in os.environ.items() if not key.startswith("CLI_HELP_")}
            environment.update(CLI_HELP_PROFILES=str(folder), CLI_HELP_DRIVERS="", CLI_HELP_DISCOVERY="off")
            before = {path.name: path.read_bytes() for path in folder.iterdir()}
            for line in ("typed -a=PRIVATE_SENTINEL --fl", "typed -azPRIVATE_SENTINEL --fl", "typed -oPRIVATE_SENTINEL"):
                environment.update(CLI_HELP_LINE=line, CLI_HELP_POINT=str(len(line)))
                for arguments in (["--bash"], ["--explain"]):
                    result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), *arguments],
                                            env=environment, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 1)
                    self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)
            environment["CLI_HELP_ESCAPE_DELAY"] = "PRIVATE_SENTINEL"
            result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--doctor"],
                                    env=environment, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["configuration"]["code"], "invalid_escape_delay")
            self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)
            self.assertEqual(before, {path.name: path.read_bytes() for path in folder.iterdir()})


class CellWidthTests(unittest.TestCase):
    def test_cell_clipping_wrapping_and_combining_marks(self):
        self.assertEqual(cell_width("界"), 2)
        self.assertEqual(cell_width("\u0301"), 0)
        self.assertEqual(clip_cells("界界x", 3), "界")
        self.assertEqual(clip_cells("e\u0301x", 1), "e\u0301")
        self.assertEqual(wrap_cells("界界 界界", 4), ["界界", "界界"])
        self.assertEqual(wrap_cells("e\u0301e\u0301e\u0301", 2), ["e\u0301e\u0301", "e\u0301"])

    def test_escape_delay_validation_omits_rejected_values(self):
        import os
        from unittest.mock import patch
        for value in ("PRIVATE_SENTINEL", "0", "1001"):
            with patch.dict(os.environ, {"CLI_HELP_ESCAPE_DELAY": value}), self.assertRaises(HelpError) as raised:
                escape_delay()
            if value == "PRIVATE_SENTINEL":
                self.assertNotIn(value, str(raised.exception))
