"""Exercise guided form corrections, cancellation, validation, and terminal safety."""

from copy import deepcopy
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from test_bash_pty import BashSession
from core import HelpError, load_profiles, find_context, insert_option
from command_paths import load_driver_registry
from manual_import import ManualCollection, atomic_json
from review import Draft
from review_forms import FormCancelled, choose, edit_options, edit_categories, edit_driver, yes_no


DOCUMENT = {
    "profile": {"command": ["newtool", "run"], "description": "Test profile", "categories": [
        {"name": "Output", "description": "Output settings", "options": [
            {"flag": "--output", "argument": "FILE", "argument_optional": False, "summary": "Write output",
             "detail": "First line\nSecond line"},
            {"flag": "--verbose", "summary": "Show detail"}]},
        {"name": "Input", "options": [{"flag": "--input", "summary": "Choose input"}]}]},
    "driver": {"command": "newtool", "global_values": ["--config"], "global_flags": ["--quiet"], "paths": [
        {"command": ["run"], "man": "newtool-run", "help": [], "stop_at_positional": True},
        {"command": ["inspect"], "man": "newtool-inspect", "help": []}]}}


class GuidedEditingTests(unittest.TestCase):
    def test_typed_optional_value_survives_review_until_argument_contract_changes(self):
        document = self.draft.document()
        option = document["profile"]["categories"][0]["options"][0]
        option.update(argument="MAX", argument_optional=True, optional_value_kind="nonnegative_integer")
        self.draft.text = json.dumps(document)
        edited = self.apply(edit_options, ["e", "1", "", "", "", "", "y"])
        self.assertEqual(edited["profile"]["categories"][0]["options"][0]["optional_value_kind"], "nonnegative_integer")
        edited = self.apply(edit_options, ["e", "1", "", "", "", "", "n"])
        self.assertNotIn("optional_value_kind", edited["profile"]["categories"][0]["options"][0])
        option["argument_optional"] = True
        self.draft.text = json.dumps(document)
        edited = self.apply(edit_options, ["e", "1", "", "", "", "/clear"])
        self.assertNotIn("optional_value_kind", edited["profile"]["categories"][0]["options"][0])

    def setUp(self):
        text = json.dumps(DOCUMENT)
        self.draft = Draft(0, text, text, {})

    def apply(self, function, responses):
        with patch("builtins.input", side_effect=responses), patch("builtins.print"):
            function(self.draft)
        return self.draft.document()

    def test_edit_existing_option_flag_description_and_optional_argument(self):
        document = self.apply(edit_options, ["e", "1", "--destination", "Select destination",
                                             "New detail", "PATH", "y"])
        option = document["profile"]["categories"][0]["options"][0]
        self.assertEqual(option, {"flag": "--destination", "summary": "Select destination", "detail": "New detail",
                                  "argument": "PATH", "argument_optional": True})
        self.assertEqual(document["driver"], DOCUMENT["driver"])

    def test_clear_argument_removes_arity_and_detail_can_be_cleared(self):
        document = self.apply(edit_options, ["e", "1", "", "", "/clear", "/clear"])
        option = document["profile"]["categories"][0]["options"][0]
        self.assertNotIn("argument", option)
        self.assertNotIn("argument_optional", option)
        self.assertEqual(option["detail"], "")

    def test_multiple_value_count_is_preserved_until_argument_is_cleared(self):
        document = self.draft.document()
        document["profile"]["categories"][0]["options"][0]["argument_count"] = 2
        self.draft.text = json.dumps(document)
        retained = self.apply(edit_options, ["e", "1", "", "", "", "", ""])
        self.assertEqual(retained["profile"]["categories"][0]["options"][0]["argument_count"], 2)
        cleared = self.apply(edit_options, ["e", "1", "", "", "", "/clear"])
        self.assertNotIn("argument_count", cleared["profile"]["categories"][0]["options"][0])

    def test_blank_fields_retain_existing_values(self):
        document = self.apply(edit_options, ["e", "1", "", "", "", "", ""])
        self.assertEqual(document, DOCUMENT)

    def test_multiline_details_are_edited_without_json_escapes(self):
        document = self.apply(edit_options, ["e", "1", "", "", "/lines", "Updated line", "", "..", ".", "", ""])
        self.assertEqual(document["profile"]["categories"][0]["options"][0]["detail"], "Updated line\n\n.")

    def test_duplicate_and_unsafe_flags_reject_the_whole_operation(self):
        for flag in ["--input", "--x;touch-marker", "--$HOME", "--bad flag"]:
            with self.subTest(flag=flag):
                before = self.draft.text
                with self.assertRaises(ValueError):
                    self.apply(edit_options, ["e", "1", flag, "Changed summary", "Changed detail", "/clear"])
                self.assertEqual(self.draft.text, before)

    def test_cancellation_and_interrupt_at_every_field_preserve_draft(self):
        responses = ["e", "1", "--destination", "Summary", "Detail", "PATH", "y"]
        for count in range(len(responses)):
            for cancellation in [FormCancelled, KeyboardInterrupt, EOFError]:
                with self.subTest(count=count, cancellation=cancellation):
                    before = self.draft.text
                    final = "/cancel" if cancellation is FormCancelled else cancellation()
                    with self.assertRaises(cancellation):
                        self.apply(edit_options, responses[:count] + [final])
                    self.assertEqual(self.draft.text, before)

    def test_move_option_between_categories_and_reorder_within_category(self):
        document = self.apply(edit_options, ["m", "1", "2", "1"])
        self.assertEqual([option["flag"] for option in document["profile"]["categories"][1]["options"]],
                         ["--output", "--input"])
        document = self.apply(edit_options, ["m", "2", "2", "2"])
        self.assertEqual([option["flag"] for option in document["profile"]["categories"][1]["options"]],
                         ["--input", "--output"])

    def test_move_last_option_to_new_category_preserves_all_options(self):
        document = self.apply(edit_options, ["m", "3", "3", "Files", "File settings", ""])
        self.assertEqual([category["name"] for category in document["profile"]["categories"]], ["Output", "Files"])
        self.assertEqual(document["profile"]["categories"][1]["options"][0]["flag"], "--input")
        self.assertEqual(sum(len(category["options"]) for category in document["profile"]["categories"]), 3)

    def test_delete_requires_confirmation_and_removes_empty_source_category(self):
        before = self.draft.text
        self.apply(edit_options, ["d", "3", ""])
        self.assertEqual(self.draft.text, before)
        document = self.apply(edit_options, ["d", "3", "y"])
        self.assertEqual(len(document["profile"]["categories"]), 1)
        self.assertEqual(len(document["profile"]["categories"][0]["options"]), 2)

    def test_edit_category_and_profile_descriptions(self):
        document = self.apply(edit_categories, ["e", "1", "Writing", "/clear"])
        self.assertEqual(document["profile"]["categories"][0]["name"], "Writing")
        self.assertEqual(document["profile"]["categories"][0]["description"], "")
        document = self.apply(edit_categories, ["t", "/lines", "First paragraph", "", "Second paragraph", "."])
        self.assertEqual(document["profile"]["description"], "First paragraph\n\nSecond paragraph")

    def test_duplicate_or_cleared_required_category_name_is_rejected(self):
        before = self.draft.text
        for responses in [["e", "1", "Input", "Description"], ["e", "1", "/clear"]]:
            with self.assertRaises(ValueError):
                self.apply(edit_categories, responses)
            self.assertEqual(self.draft.text, before)

    def test_reorder_and_delete_categories_without_losing_unselected_content(self):
        document = self.apply(edit_categories, ["m", "2", "0", "99", "1"])
        self.assertEqual(document["profile"]["categories"][0], DOCUMENT["profile"]["categories"][1])
        document = self.apply(edit_categories, ["d", "2", "y"])
        self.assertEqual(document["profile"]["categories"], [DOCUMENT["profile"]["categories"][1]])
        document = self.apply(edit_categories, ["d", "1", "y"])
        self.assertEqual(document["profile"]["categories"], [])
        with self.assertRaises(FormCancelled):
            self.apply(edit_options, ["e"])

    def test_driver_globals_are_updated_together_and_conflicts_rejected(self):
        document = self.apply(edit_driver, ["g", "--root -C", "/clear"])
        self.assertEqual(document["driver"]["global_values"], ["--root", "-C"])
        self.assertEqual(document["driver"]["global_flags"], [])
        self.assertEqual(document["driver"]["paths"], DOCUMENT["driver"]["paths"])
        before = self.draft.text
        for responses in [["g", "--root", "--root"], ["g", "--root --root", ""], ["g", "--root;touch", ""]]:
            with self.assertRaises(ValueError):
                self.apply(edit_driver, responses)
            self.assertEqual(self.draft.text, before)

    def test_route_settings_preserve_other_routes_and_never_execute(self):
        with patch("subprocess.run") as process:
            document = self.apply(edit_driver, ["r", "1", "different-manual", "help run", "n"])
            process.assert_not_called()
        self.assertEqual(document["driver"]["paths"][0],
                         {"command": ["run"], "man": "different-manual", "help": ["help", "run"], "stop_at_positional": False})
        self.assertEqual(document["driver"]["paths"][1], DOCUMENT["driver"]["paths"][1])
        document = self.apply(edit_driver, ["r", "1", "/clear", "", ""])
        self.assertIsNone(document["driver"]["paths"][0]["man"])
        before = self.draft.text
        with self.assertRaises(ValueError):
            self.apply(edit_driver, ["r", "1", "", "/clear", ""])
        self.assertEqual(self.draft.text, before)

    def test_executable_action_or_template_cannot_be_a_help_route(self):
        before = self.draft.text
        for arguments in ["run dangerous", "help $(touch marker)", "help `whoami`", "help a;echo"]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.apply(edit_driver, ["r", "1", "", arguments, ""])
            self.assertEqual(self.draft.text, before)

    def test_builtin_global_arity_cannot_be_overridden_by_a_form(self):
        document = deepcopy(DOCUMENT)
        document["profile"]["command"] = ["docker", "run"]
        document["driver"]["command"] = "docker"
        self.draft.text = json.dumps(document)
        before = self.draft.text
        with self.assertRaisesRegex(HelpError, "arity"):
            self.apply(edit_driver, ["g", "/clear", "--host"])
        self.assertEqual(self.draft.text, before)

    def test_selection_search_pagination_empty_results_and_terminal_escaping(self):
        labels = [f"Option {index}" for index in range(30)]
        labels[26] = "Special\x1b[31m"
        with patch("builtins.input", side_effect=["n", "p", "f", "absent", "1", "f", "special", "27"]), patch("builtins.print") as output:
            self.assertEqual(choose(labels, "Options"), 26)
        printed = " ".join(str(call.args[0]) for call in output.call_args_list)
        self.assertNotIn("\x1b", printed)
        self.assertIn("\\u001b", printed)
        with patch("builtins.input", side_effect=["maybe", "yes"]), patch("builtins.print"):
            self.assertTrue(yes_no("Confirm?"))

    def test_terminal_guided_corrections_preview_save_and_literal_insertion(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            collection = folder / "collection"
            with ManualCollection(collection) as destination:
                result = destination.save_documents(deepcopy(DOCUMENT["profile"]), deepcopy(DOCUMENT["driver"]))
            report = collection / "scan-report.json"
            atomic_json(report, {"schema_version": 1, "records": [
                {"command": ["newtool", "run"], "status": "needs_adjustment", "generated": True}]})
            marker = folder / "executed-target"
            write_executable(folder / "newtool", f"import pathlib\npathlib.Path({str(marker)!r}).touch()\n")
            shell = BashSession(folder, extra_environment={"PATH": str(folder) + os.pathsep + os.environ["PATH"],
                                                          "EDITOR": "/nonexistent-editor"})
            def respond(prompt, value):
                shell.expect(prompt.encode())
                shell.send(value + "\n")
            try:
                shell.send(shlex.quote(sys.executable) + " " + shlex.quote(str(ROOT / "cli_help/main.py")) +
                           " --review-report " + shlex.quote(str(report)) + "\n")
                respond("Review: number", "1")
                respond("Entry:", "o")
                respond("Options: [e]", "e")
                respond("Select number", "1")
                respond("Literal flag (", "--destination")
                respond("Summary (", "Choose destination")
                respond("Detail (", "")
                respond("Argument placeholder (", "PATH")
                respond("Argument optional?", "y")
                respond("Entry:", "c")
                respond("Categories: [e]", "e")
                respond("Select number", "1")
                respond("Category name (", "Writing")
                respond("Category description (", "Output controls")
                respond("Entry:", "d")
                respond("Driver: [g]", "g")
                respond("Globals requiring values (", "--root")
                respond("Global boolean flags (", "--silent")
                respond("Entry:", "d")
                respond("Driver: [g]", "r")
                respond("Select number", "1")
                respond("Manual page (", "newtool-execution")
                respond("Help arguments (", "")
                respond("Stop at the first positional argument?", "n")
                respond("Entry:", "p")
                shell.expect(b"Help preview")
                shell.send("\n")
                shell.expect(b"Preview selection only: --destination")
                respond("Entry:", "s")
                respond("mark reviewed?", "y")
                shell.expect(b"Saved and marked reviewed")
                respond("Entry:", "b")
                respond("Review: number", "q")
                shell.expect(b"__HELP_TEST_PROMPT__")
            finally:
                shell.close()
            self.assertFalse(marker.exists())
            profiles = load_profiles(collection / "profiles")
            drivers = load_driver_registry(collection / "drivers")
            self.assertEqual(profiles[0]["categories"][0]["name"], "Writing")
            self.assertEqual(drivers["newtool"].paths[("run",)].manual, "newtool-execution")
            self.assertFalse(drivers["newtool"].paths[("run",)].stop_at_positional)
            self.assertIn("--root", drivers["newtool"].global_values)
            line = "newtool --root private run --dest"
            context = find_context(line, len(line), profiles, driver_registry=drivers,
                                   discover=lambda *a, **k: self.fail("Unexpected discovery"))
            self.assertEqual(insert_option(context, profiles[0]["categories"][0]["options"][0])[0],
                             "newtool --root private run --destination ")
            self.assertTrue(Path(result["profile"]).is_file())


if __name__ == "__main__":
    unittest.main()
