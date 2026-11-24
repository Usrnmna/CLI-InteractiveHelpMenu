"""Check the fixed media, archive and transfer tables against release declarations."""

import json
import unittest

from test_essential_terminal import FIXTURES, fixed_inputs
from discovery import build_profile

SOURCES = FIXTURES / "discovery-tiers"
RECORDS = json.loads((SOURCES / "extended-tools.json").read_text())
UTILITY_ROUTES = ("vlc", "rclone copy", "restic backup", "borg create", "7z", "7zz",
                  "magick", "convert", "yt-dlp", "rclone", "rclone sync")


def rows(name):
    """Replay only the registered help and optional manual supplied for this route."""
    replies, _ = fixed_inputs({"command": name}, None, RECORDS[name], SOURCES)
    sources = [("man " + argv[-1] if argv[0] == "man" else " ".join(argv), text)
               for argv, text in replies.items()]
    profile = build_profile(name.split(), sources)
    return {o["flag"]: o for group in profile["categories"] for o in group["options"]}


class UtilityTableTests(unittest.TestCase):
    def test_complete_fixed_tables(self):
        for name in UTILITY_ROUTES:
            with self.subTest(command=name):
                self.assertEqual(RECORDS[name]["options"], {f: o.get("argument_count", 1) if o["argument"] else 0
                                                           for f, o in rows(name).items()})

    def test_vlc_opposite_directions_and_styles_example(self):
        view = rows("vlc")
        self.assertIn("forward", view["--key-jump+long"]["detail"].lower())
        self.assertIn("backward", view["--key-jump-long"]["detail"].lower())
        self.assertFalse(view["-v"]["argument"])
        self.assertTrue(view["--verbose"]["argument"])
        self.assertNotIn("--option", view)
        self.assertNotIn("--global-key-jump", view)

    def test_image_operands_and_joined_help_lines(self):
        for name in ("convert", "magick"):
            with self.subTest(name=name):
                view = rows(name)
                self.assertEqual(view["-sparse-color"]["argument_count"], 2)
                self.assertIn("line break", view["-word-break"]["detail"])
                self.assertNotIn("word-break", view["-write-mask"]["detail"])
                self.assertNotIn("-view", view)
                self.assertEqual("-support" in view, name == "convert")
                self.assertEqual("-perceptible" in view, name == "convert")

    def test_yt_dlp_aliases_operands_and_examples(self):
        view = rows("yt-dlp")
        self.assertEqual(3, view["--replace-in-metadata"]["argument_count"])
        self.assertEqual(2, view["--print-to-file"]["argument_count"])
        self.assertEqual(view["--external-downloader"]["argument"], view["--downloader"]["argument"])
        self.assertEqual(view["--srt-lang"]["argument"], "LANGS")
        self.assertIn("--srt-langs", view["--srt-lang"]["detail"])
        self.assertEqual("PRESET", view["-t"]["argument"])
        self.assertNotIn("-t mp3", view)
