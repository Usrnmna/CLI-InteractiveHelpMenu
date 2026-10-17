"""Contract checks for literal edits, preserved buffers, and validated configuration."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from core import HelpError, find_context, insert_option, load_profiles, tokenize, validate_profile
from ui import Browser, load_keys


class EditingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = load_profiles(ROOT / "profiles")

    def context(self, line, point=None):
        point = len(line) if point is None else point
        return find_context(line, point, self.profiles)

    def option(self, context, flag):
        return next(option for category in context.profile["categories"] for option in category["options"] if option["flag"] == flag)

    def edit(self, line, flag, point=None):
        context = self.context(line, point)
        return insert_option(context, self.option(context, flag))

    def test_append_literal_option(self):
        self.assertEqual(self.edit("rsync ", "--archive"), ("rsync --archive ", 16))

    def test_replace_whole_partial_token_at_middle_cursor(self):
        line = 'rsync --arch source "destination folder"'
        edited, point = self.edit(line, "--archive", len("rsync --ar"))
        self.assertEqual(edited, 'rsync --archive source "destination folder"')
        self.assertEqual(point, len("rsync --archive "))

    def test_equal_option_leaves_cursor_at_value(self):
        self.assertEqual(self.edit("rsync --ex", "--exclude="), ("rsync --exclude=", 16))

    def test_unicode_character_cursor_and_suffix(self):
        line = 'rsync "café/日本" --ar target'
        cursor = len('rsync "café/日本" --ar')
        edited, point = self.edit(line, "--archive", cursor)
        self.assertEqual(edited, 'rsync "café/日本" --archive target')
        self.assertEqual(point, len('rsync "café/日本" --archive '))

    def test_unicode_space_is_part_of_a_shell_word(self):
        self.assertEqual(self.edit("rsync folder\u3000name --ar", "--archive")[0], "rsync folder\u3000name --archive ")
        with self.assertRaises(HelpError):
            self.context("rsync\u3000--ar")

    def test_whitespace_is_preserved(self):
        line = "rsync   --ar   "
        edited, point = self.edit(line, "--archive", len("rsync   --ar"))
        self.assertEqual(edited, "rsync   --archive   ")
        self.assertEqual(point, len("rsync   --archive "))

    def test_subcommand_and_absolute_executable(self):
        self.assertEqual(self.context("/usr/bin/git commit --m").profile["command"], ["git", "commit"])
        self.assertEqual(self.edit("git commit --m", "--message")[0], "git commit --message ")

    def test_invalid_context_is_rejected(self):
        lines = ["", "rsync", "unknown --", "git --", "rsync filename", "rsync --exclude=value",
                 "rsync -- ", "git commit --message ", "rsync 'unfinished", "rsync \\",
                 "rsync ; ls ", "ls | grep --", "rsync > out ", "rsync && ls --",
                 "rsync $(touch marker) --", "rsync `touch marker` --", "rsync $HOME --",
                 "rsync\n--", "rsync # comment"]
        for line in lines:
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line)

    def test_quoted_shell_symbols_are_literal(self):
        self.assertEqual(self.edit("rsync '$(literal);file' --ar", "--archive")[0], "rsync '$(literal);file' --archive ")

    def test_completed_value_allows_next_option(self):
        self.assertEqual(self.edit('git commit --message "a message" --a', "--all")[0], 'git commit --message "a message" --all ')

    def test_end_marker_used_as_value_does_not_disable_options(self):
        self.assertEqual(self.edit('git commit --message -- --a', "--all")[0], 'git commit --message -- --all ')

    def test_cursor_inside_command_or_outside_buffer_is_rejected(self):
        for line, point in [("rsync --", 3), ("rsync --", 100), ("rsync --", -1)]:
            with self.subTest(line=line, point=point), self.assertRaises(HelpError):
                self.context(line, point)

    def test_foreign_option_is_rejected(self):
        with self.assertRaises(HelpError):
            insert_option(self.context("rsync "), {"flag": "--evil"})

    def test_malicious_profile_flag_is_rejected(self):
        profile = copy.deepcopy(self.profiles[0])
        for flag in ["--ok;touch marker", "$(touch marker)", "--ok\nexit", "--flag value", "--x='text'"]:
            profile["categories"][0]["options"][0]["flag"] = flag
            with self.subTest(flag=flag), self.assertRaises(HelpError):
                validate_profile(profile, Path("test.json"))

    def test_custom_profile_overrides_bundled_definition(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = copy.deepcopy(self.profiles[0])
            profile["description"] = "Custom definition"
            Path(folder, "custom.json").write_text(json.dumps(profile))
            profiles = load_profiles(ROOT / "profiles", Path(folder))
            result = next(item for item in profiles if item["command"] == profile["command"])
            self.assertEqual(result["description"], "Custom definition")


class BrowserTests(unittest.TestCase):
    def setUp(self):
        self.profile = next(item for item in load_profiles(ROOT / "profiles") if item["command"] == ["rsync"])

    def test_category_and_option_navigation_are_bounded(self):
        browser = Browser(self.profile)
        browser.move_category(1000)
        self.assertEqual(browser.category, len(self.profile["categories"]) - 1)
        browser.move_option(1000)
        self.assertEqual(browser.selected, len(browser.options()) - 1)
        browser.move_category(-1000)
        self.assertEqual((browser.category, browser.selected), (0, 0))

    def test_search_finds_category_and_handles_no_matches(self):
        browser = Browser(self.profile, "--dry")
        self.assertEqual(browser.options()[0]["flag"], "--dry-run")
        browser.set_query("no-such-option")
        self.assertEqual(browser.options(), [])
        browser.set_query("")
        self.assertTrue(browser.options())

    def test_config_validation(self):
        for keys in [{"accept": ["j"]}, {"cancel": []}, {"unknown": ["x"]}, {"accept": ["esc"]}]:
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder, "keys.json")
                path.write_text(json.dumps({"keys": keys}))
                with self.subTest(keys=keys), self.assertRaises(HelpError):
                    load_keys(path)

    def test_custom_keys_merge_with_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "keys.json")
            path.write_text(json.dumps({"keys": {"accept": ["a"], "next_category": ["n"]}}))
            keys = load_keys(path)
            self.assertEqual(keys["accept"], ["a"])
            self.assertIn("up", keys["up"])


if __name__ == "__main__":
    unittest.main()
