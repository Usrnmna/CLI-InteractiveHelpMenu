"""Optional numeric values retain literal edits and strict positional boundaries."""

from copy import deepcopy
from pathlib import Path
import unittest

from core import HelpError, find_context, insert_option, validate_profile


PROFILE = {
    "command": ["counted"], "description": "Independent optional-number contract",
    "stop_at_positional": True,
    "categories": [{"name": "Options", "options": [
        {"flag": "-m", "argument": "MAX", "argument_optional": True,
         "optional_value_kind": "nonnegative_integer", "attached": True, "summary": "Limit selections"},
        {"flag": "--multi", "argument": "MAX", "argument_optional": True,
         "optional_value_kind": "nonnegative_integer", "summary": "Limit selections"},
        {"flag": "--query", "argument": "TEXT", "summary": "Set query text"}]}],
}


class OptionalIntegerTests(unittest.TestCase):
    def test_separate_joined_quoted_and_absent_counts_preserve_surrounding_text(self):
        for count in ("-m", "-m 2", "-m2", "--multi", "--multi 0", "--multi=2", "-m '12'"):
            line = "env NOTE='café 日本' counted\t" + count + "  --qu 'retained suffix'"
            point = line.index("--qu") + 4
            with self.subTest(count=count):
                context = find_context(line, point, [PROFILE])
                edited, cursor = insert_option(context, PROFILE["categories"][0]["options"][-1])
                self.assertEqual(edited, line.replace("--qu", "--query", 1))
                self.assertEqual(cursor, point + 4)  # Reuse and advance over the existing separator.

    def test_only_one_ascii_nondash_integer_is_consumed(self):
        for suffix in ("input", "2 input", "2 3", "--", "-- --query", "-2", "+2", "２", "2x"):
            line = "counted -m " + suffix + " "
            with self.subTest(suffix=suffix), self.assertRaises(HelpError):
                find_context(line, len(line), [PROFILE])
        line = "counted -m --query '-2 日本' --qu"
        context = find_context(line, len(line), [PROFILE])
        self.assertEqual(insert_option(context, PROFILE["categories"][0]["options"][-1])[0],
                         "counted -m --query '-2 日本' --query ")

    def test_cursor_inside_numeric_value_cannot_replace_it(self):
        for line in ("counted -m 12", "counted -m12", "counted --multi=12"):
            for point in (len(line) - 1, len(line)):
                with self.subTest(line=line, point=point), self.assertRaises(HelpError):
                    find_context(line, point, [PROFILE])

    def test_untyped_optional_arguments_do_not_gain_numeric_consumption(self):
        profile = deepcopy(PROFILE)
        profile["categories"][0]["options"][0].pop("optional_value_kind")
        line = "counted -m 2 "
        with self.assertRaises(HelpError):
            find_context(line, len(line), [profile])

    def test_optional_value_schema_rejects_ambiguous_metadata(self):
        validate_profile(PROFILE, Path("<contract>"))
        for update in ({"optional_value_kind": "expression"}, {"optional_value_kind": None},
                       {"argument_optional": False}, {"argument": ""}, {"argument_count": 2}):
            profile = deepcopy(PROFILE)
            profile["categories"][0]["options"][0].update(update)
            with self.subTest(update=update), self.assertRaises(HelpError):
                validate_profile(profile, Path("<invalid>"))


if __name__ == "__main__":
    unittest.main()
