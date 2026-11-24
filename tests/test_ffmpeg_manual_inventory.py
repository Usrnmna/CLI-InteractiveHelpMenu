"""Compare the bundled menu with the release inventories and original help specimen."""

import csv
import hashlib
import json
import lzma
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import find_context
from errors import HelpError
from presentation import option_text


def inventory(filename, key):
    """Read the independent, release-scoped inventory and reject duplicate identifiers."""
    with (ROOT / "tests/fixtures/ffmpeg" / filename).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate {key} in {filename}")
    return result


class FFmpegManualInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((ROOT / "profiles/ffmpeg.json").read_bytes())
        cls.menu = {option["flag"]: (category, option) for category in cls.profile["categories"]
                    for option in category["options"]}
        cls.native = inventory("cli-options.tsv", "spelling")
        cls.library = inventory("avoptions.tsv", "name")

    def test_exact_menu_union_and_arity(self):
        """Require all native spellings and directly routed names from any reviewed build."""
        native = {name for name, row in self.native.items() if row["disposition"] == "select"}
        releases = ("noble", "resolute", "upstream")
        direct = {"-" + name for name, row in self.library.items()
                  if any(row[release] == "direct" for release in releases)}
        conditional = set()
        for file in ("format-options.tsv", "device-options.tsv", "protocol-options.tsv", "av-codec-source.tsv"):
            with (ROOT / "tests/fixtures/ffmpeg" / file).open(encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream, delimiter="\t"):
                    if row["disposition"] in {"select", "conditional"}:
                        conditional.add("-" + row["name"])
                    if row["disposition"] == "existing":
                        self.assertIn("-" + row["name"], self.menu)
        self.assertEqual(set(self.menu), native | direct | conditional)
        for flag, (_, option) in self.menu.items():
            with self.subTest(flag=flag):
                arity = self.native[flag]["operand"] if flag in native else "required"
                self.assertEqual(bool(option.get("argument")), arity != "none")
                self.assertEqual(bool(option.get("argument_optional")), arity == "optional")
                if arity != "none":
                    self.assertEqual(value_forms(option), {"separate"})

    def test_inventories_against_three_levels_of_actual_help(self):
        """Check every captured CLI heading and independently enumerate full-help AVOption names."""
        folder = ROOT / "tests/fixtures/ffmpeg/help"
        manifest = json.loads((folder / "manifest.json").read_bytes())
        for release, code in (("noble", "N"), ("resolute", "R"), ("upstream", "U")):
            captures = manifest["builds"][release]["captures"]
            for mode in ("short", "long", "full"):
                with self.subTest(release=release, mode=mode):
                    raw = lzma.decompress((folder / captures[mode]["file"]).read_bytes())
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), captures[mode]["sha256"])
                    native, _, library = raw.decode().partition("AVCodecContext AVOptions:")
                    headings = set(re.findall(r"^(-[^\s\[:=]+)", native, re.MULTILINE))
                    expected = {name for name, row in self.native.items() if code in row["releases"]}
                    self.assertLessEqual(headings, expected)
                    self.assertIn("-version", headings)
                    self.assertIn("-i", native)  # Input group opener appears in usage.
                    if mode == "full":
                        # Full help includes runtime-only fields without a dash and array operands in brackets.
                        names = set(re.findall(r"^  [- ](\S+)\s+(?:<|\[<)", library, re.MULTILINE))
                        self.assertEqual(names, {name for name, row in self.library.items()
                                                 if row[release] != "absent"})

    def test_optional_build_captures_and_component_ownership(self):
        """Verify the companion build and options missing from the baseline upstream capture."""
        folder = ROOT / "tests/fixtures/ffmpeg/help"
        manifest = json.loads((folder / "manifest.json").read_bytes())
        for mode, entry in manifest["supplemental_builds"]["upstream-optional"]["captures"].items():
            raw = (folder / entry["file"]).read_bytes()
            if entry["file"].endswith(".xz"):
                raw = lzma.decompress(raw)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
            if mode == "full":
                for name in ("max_redirects", "cenc_decryption_keys", "handshake_timeout", "video_stream_expr"):
                    self.assertRegex(raw.decode(), rf"(?m)^  -{name}\s")
                    self.assertIn("-" + name, self.menu)
        for flag in ("-key", "-connect_timeout"):
            _, option = self.menu[flag]
            self.assertEqual(option["value_semantics"]["variants"], [{"ref": "av-component"}])

    def test_original_order_and_fixed_help_specimen(self):
        """Preserve the original menu spellings and separately check the compact discovery specimen."""
        original = ("-i", "-map", "-y", "-n", "-ss", "-t", "-c:v", "-c:a", "-c:v:0", "-c:a:0",
                    "-b:v", "-b:a", "-filter:v", "-filter:a", "-vn", "-an")
        self.assertEqual(tuple(flag for flag in self.menu if flag in original), original)
        self.assertFalse(self.profile.get("stop_at_positional"))
        fixtures = ROOT / "tests/fixtures/help"
        self.assertEqual(hashlib.sha256((fixtures / "ffmpeg.txt").read_bytes()).hexdigest(),
                         "ca19f5b1966973a0344ac685d3435458f63ccdb200559ddbfc857bcb0b7db446")
        route, = (row for row in json.loads((fixtures / "matrix.json").read_bytes())
                  if row["command"] == "ffmpeg")
        self.assertEqual(route["fixture"], "ffmpeg.txt")
        self.assertEqual(route["excluded"], ["-c:"])
        self.assertLessEqual(set(route["flags"]), set(self.menu))

    def test_qualified_values_and_dash_operands_between_files(self):
        """The editor must consume the entire operand of the applicable FFmpeg option."""
        for arguments in ("-i - -map -0:a:0 -c:a:1 copy", "-/filter:v:1 graph.txt", "-f null -"):
            line = f"ffmpeg {arguments} -filter_ 'out file'"
            point = line.index(" 'out file'")
            self.assertEqual(find_context(line, point, [self.profile]).query, "-filter_")
        for arguments in ("-c:a:1", "-/filter:v:1", "-map"):
            line = f"ffmpeg {arguments} "
            with self.assertRaises(HelpError) as caught:
                find_context(line, len(line), [self.profile])
            self.assertEqual(caught.exception.code, "option_value_required")

    def test_library_ownership_and_aliases(self):
        """Keep rejected scaler settings, native collisions and resampler aliases distinct."""
        states = lambda name: tuple(self.library[name][release] for release in ("noble", "resolute", "upstream"))
        self.assertEqual(states("srcw"), ("rejected",) * 3)
        self.assertNotIn("-srcw", self.menu)
        self.assertEqual(states("apply_cropping"), ("direct", "cli", "cli"))
        self.assertEqual(states("top"), ("cli", "cli", "direct"))
        self.assertEqual(states("id3v2_version"), ("direct",) * 3)
        for name in ("osr", "out_sample_rate"):
            alias = self.library[name]["aliases"]
            self.assertEqual({name, alias}, {"osr", "out_sample_rate"})
            group, option = self.menu["-" + name]
            self.assertIn("-" + alias, option_text(self.profile, group, option).searchable)

    def test_help_alias_and_qualified_family_ownership(self):
        """Check useful aliases, the media shortcuts and the documented rejected spelling."""
        group, help_option = self.menu["-h"]
        self.assertIn("-?", option_text(self.profile, group, help_option).searchable)
        for flag, effect in (("-vf", "-filter:v"), ("-af", "-filter:a"), ("-lavfi", "-filter_complex"),
                             ("-vcodec", "-c:v"), ("-acodec", "-c:a")):
            with self.subTest(flag=flag):
                self.assertEqual(self.native[flag]["effect"], effect)
                group, option = self.menu[flag]
                self.assertIn(effect, option_text(self.profile, group, option).searchable)
        self.assertNotIn("-sbsf", self.menu)
        self.assertEqual(self.native["-sbsf"]["manual_heading"], "N")
        self.assertEqual(self.native["-sbsf"]["disposition"], "unregistered")
        self.assertEqual(self.native["-sseof"]["scope"], "input")
        self.assertIn("U:output", self.native["-thread_queue_size"]["scope"])
