"""Exercise terminal controls as escaped data through passive help rendering."""

from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, validate_profile
import discovery
from test_numerical_presentation import CellScreen
from test_terminal_screen import TMUX_AVAILABLE, TmuxShell
from ui import Browser, display_text, draw, load_keys


class TerminalSanitizationTests(unittest.TestCase):
    def setUp(self):
        """Reject target execution and networking while parsing supplied text."""
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen",
                       "socket.socket", "socket.create_connection", "discovery.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Passive sanitizer attempted execution")))

    def parsed(self, description):
        """Require normal profile validation after cleaning a supplied description."""
        profile = discovery.build_profile("specimen", [("fixture", "Options:\n  --sample   " + description
                                                        + "\n  --other   Other description\n")])
        validate_profile(profile, Path("fixture.json"))
        options = {o["flag"]: o for c in profile["categories"] for o in c["options"]}
        self.assertEqual(set(options), {"--sample", "--other"})
        return profile, options["--sample"]

    def test_known_remnants_are_removed_before_profile_validation_and_rendering(self):
        for raw in ("\x1b[31mPlain\x1b[0m", "\x1b(BPlain", "\x9b31mPlain\x9b0m"):
            with self.subTest(raw=repr(raw)):
                profile, option = self.parsed(raw)
                self.assertEqual(option["summary"], "Plain")
                self.assertEqual(option["detail"], "Plain\nSource: fixture")
                screen = CellScreen(24, 100)
                draw(screen, Browser(profile, "--sample"), load_keys())
                self.assertIn("Plain", screen.text())
                for remnant in ("(BPlain", "31m", "0m"):
                    self.assertNotIn(remnant, screen.text())

    def test_character_sets_csi_and_single_escape_controls_preserve_literal_declarations(self):
        controls = ("\x1b(B", "\x1b)0", "\x1b%G", "\x1b#8", "\x1b7", "\x1b8",
                    "\x1b[?25l", "\x1b[1;38:2::12:34:56m", "\x9b0m", "\x1b[0 q", "\x1b[!p")
        for control in controls:
            with self.subTest(control=repr(control)):
                profile = discovery.build_profile("specimen", [("fixture", control + "--path FILE   Plain" + control)])
                validate_profile(profile, Path("fixture.json"))
                option = profile["categories"][0]["options"][0]
                self.assertEqual((option["flag"], option["argument"], option["summary"]), ("--path", "FILE", "Plain"))

    def test_esc_and_c1_control_strings_remove_payloads_and_keep_link_labels(self):
        for intro in ("\x1b]", "\x9d", "\x1bP", "\x90", "\x1bX", "\x98",
                      "\x1b^", "\x9e", "\x1b_", "\x9f"):
            endings = ("\x1b\\", "\x9c", "\x18", "\x1a")
            if intro in ("\x1b]", "\x9d"):
                endings += ("\x07",)
            for end in endings:
                with self.subTest(intro=repr(intro), end=repr(end)):
                    _, option = self.parsed("Before " + intro + "hidden payload" + end + "after")
                    self.assertEqual(option["summary"], "Before after")
        _, option = self.parsed("\x1b]8;;https://example.invalid\x1b\\Label\x1b]8;;\x1b\\")
        self.assertEqual(option["summary"], "Label")

    def test_incomplete_sequences_recover_without_consuming_following_prose(self):
        cases = (
            ("\x1b", ""), ("\x1b(", ""), ("\x1b[31", ""), ("\x9b31;", ""),
            ("\x1b[31\nNext line", "\nNext line"), ("\x1b[31界", "界"),
            ("\x1b[31\x1b[0mPlain", "Plain"), ("\x1b[31\x18Plain", "Plain"),
            ("\x1b(\nNext line", "\nNext line"), ("\x1b界Plain", "界Plain"),
            ("\x1b]unfinished prose", "unfinished prose"),
            ("\x9dunfinished\nNext line", "unfinished\nNext line"),
            ("\x1bPunfinished\rNext line", "unfinished\nNext line"),
            ("\x1b]unfinished\x1b[31mPlain", "unfinishedPlain"),
        )
        for raw, expected in cases:
            with self.subTest(raw=repr(raw)):
                self.assertEqual(discovery.clean_output(raw), expected)
        for prefix in ("\x1b]unterminated", "\x90unterminated", "\x1b[31", "\x1b("):
            profile = discovery.build_profile("specimen", [("fixture", prefix + "\nOptions:\n  --safe   Plain")])
            validate_profile(profile, Path("fixture.json"))
            self.assertEqual(profile["categories"][0]["options"][0]["flag"], "--safe")

    def test_plain_unicode_brackets_newlines_tabs_and_overstrikes_survive(self):
        plain = "Options:\r\n\t--color[=WHEN]\tCafé e\u0301 日本 [31m] (B) <FILE> {a,b}\rNext\n"
        self.assertEqual(discovery.clean_output(plain), plain.replace("\r\n", "\n").replace("\r", "\n"))
        profile = discovery.build_profile("specimen", [("fixture", "Options:\n  _\b-\b--flag   P\bPlain")])
        validate_profile(profile, Path("fixture.json"))
        self.assertEqual(profile["categories"][0]["options"][0]["summary"], "Plain")
        self.assertEqual(discovery.clean_output("Header\n" + "x" + "\b" * 100000 + "--flag"), "Header\n--flag")

    def test_display_defense_does_not_weaken_profile_validation(self):
        profile, option = self.parsed("Plain")
        for control in ("\x1b(B", "\x9b31m", "\x1b]hidden\x07"):
            with self.subTest(control=repr(control)):
                invalid = deepcopy(profile)
                invalid["categories"][0]["options"][0]["summary"] = control + "Plain"
                with self.assertRaises(HelpError):
                    validate_profile(invalid, Path("invalid.json"))
                self.assertEqual(display_text(control + "Plain"), "Plain")
        self.assertEqual(display_text("a\ud800b"), "a b")
        self.assertEqual(display_text("[31m] (B) 界"), "[31m] (B) 界")
        self.assertEqual(discovery.clean_output("Before\x84\x85\x88\x8d\x9cafter"), "Beforeafter")

    def test_large_and_repeated_unterminated_inputs_remain_bounded(self):
        """Long scans and many restart points must not require recursive parsing."""
        text = "\x1b]" + "x" * 250000 + "\n--flag   Plain"
        self.assertEqual(discovery.clean_output(text), "x" * 250000 + "\n--flag   Plain")
        text = ("\x1b]x" * 50000) + "\n--flag   Plain"
        self.assertEqual(discovery.clean_output(text), "x" * 50000 + "\n--flag   Plain")
        self.assertEqual(discovery.clean_output("\x1b[" + "1;" * 100000 + "mPlain"), "Plain")

    def test_previous_sanitizer_cache_identity_cannot_reuse_remnants(self):
        profile, _ = self.parsed("Plain")
        parent = ROOT / ".cache"
        parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="cli-help-sanitizer-cache-", dir=parent) as folder:
            path = Path(folder) / "cache.json"
            old_identity = {"command": ["specimen"], "version": 15}
            current = {"command": ["specimen"], "version": discovery.CACHE_VERSION}
            discovery.write_cache(path, old_identity, profile)
            self.assertIsNone(discovery.read_cache(path, current, 60))
            discovery.write_cache(path, current, profile)
            self.assertEqual(discovery.read_cache(path, current, 60), profile)


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class TerminalSanitizationScreenTests(unittest.TestCase):
    def test_cleaned_fixture_renders_without_remnants_and_preserves_pending_input(self):
        """Render validated fixture data with discovery disabled in a private terminal."""
        with tempfile.TemporaryDirectory(prefix="cli-help-sanitized-screen-") as folder:
            profiles = Path(folder) / "profiles"
            profiles.mkdir()
            raw = "Options:\n  --sample   \x1b(B\x9b31mPlain\x9b0m \x1b]hidden\x07description"
            profile = discovery.build_profile("specimen", [("fixture", raw)])
            validate_profile(profile, Path("fixture.json"))
            (profiles / "specimen.json").write_text(json.dumps(profile), encoding="utf-8")
            shell = TmuxShell(folder, profile_directory=profiles)
            try:
                pending = "specimen --sample"
                shell.text(pending)
                state = shell.open_menu()
                cells = "\n".join(state.cells)
                self.assertIn("Plain description", cells)
                for remnant in ("(BPlain", "31m", "0m", "hidden"):
                    self.assertNotIn(remnant, cells)
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (pending, len(pending)))
                self.assertFalse(shell.executed.exists())
            finally:
                shell.close()


if __name__ == "__main__":
    unittest.main()
