"""Compare both complete Ubuntu fixed media help tables with independent declarations."""

import csv
import lzma
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context
from discovery import build_profile, clean_output
from presentation import option_text

FIXTURES = ROOT / "tests/fixtures"
RELEASES = ("noble", "resolute")


def media_input(program, release):
    """Load the complete merged stderr/stdout of the fixed --help request."""
    path = FIXTURES / "essential" / f"{release}-{program}-help.xz"
    return lzma.decompress(path.read_bytes()).decode()


def media_inventory(program, text):
    """Reconcile names against physical table rows, native arity and typed library columns."""
    expected = {}
    with (FIXTURES / "ffmpeg/cli-options.tsv").open() as fh:
        native = {r["spelling"]: int(r["operand"] != "none") for r in csv.DictReader(fh, delimiter="\t")}
    for line in text.splitlines():
        if not line.startswith(("-", "  -")):
            continue
        name = line.split()[0].partition("[:")[0]
        if not re.fullmatch(r"--?[\w-]+", name):
            continue
        if line.startswith("  -"):
            # Named values below this declaration are indented further and have no switch.
            if not re.search(r"[.A-Z]{5,}X[.A-Z]{2,}", line):
                expected.setdefault(name, 1)
        elif program == "ffmpeg":
            expected[name] = native[name]
        else:
            columns = re.split(r"\s{2,}", line.strip(), maxsplit=1)
            value = len(columns[0].split()) > 1
            if name in {"-print_format", "-show_log", "-show_optional_fields", "-show_data_hash"}:
                value = True
            expected[name] = int(value and name != "-hide_banner")
    return expected


def media_manual(program, release):
    """Return the matching distribution manual as rendered at discovery's fixed width."""
    path = FIXTURES / "essential" / f"{release}-{program}-man.xz"
    return lzma.decompress(path.read_bytes()).decode()


def combined_inventory(program, release):
    """Count options in POD's declaration column separately from native active registrations."""
    expected = media_inventory(program, media_input(program, release))
    text = clean_output(media_manual(program, release))
    chapter = re.split(r"\n[A-Z][A-Z ]{2,}\n", text.split("\nOPTIONS\n", 1)[1])[0]
    with (FIXTURES / "ffmpeg/cli-options.tsv").open() as fh:
        native = {r["spelling"]: r for r in csv.DictReader(fh, delimiter="\t")}
    for line in chapter.splitlines():
        if not line.startswith("       -"):
            continue
        heading = line.strip()
        names = re.findall(r"(?:^|, | \| )(--?[a-zA-Z0-9_][\w-]*)", heading)
        for flag in names:
            if program == "ffmpeg":
                # sws_flags comes from libswscale, outside the native option ledger.
                if flag == "-sws_flags":
                    expected[flag] = 1
                elif native[flag]["disposition"] == "select":
                    expected[flag] = int(native[flag]["operand"] != "none")
            elif flag != "-show_format_entry" and flag not in expected:
                # The section-1 page adds generic options missing from the short help.
                expected[flag] = int(flag in {"-h", "-help", "--help", "-sources", "-sinks",
                                              "-cpuflags", "-cpucount", "-loglevel", "-v", "-max_alloc"})
    return expected


class EssentialMediaTests(unittest.TestCase):
    def test_complete_ubuntu_help_tables(self):
        for name in ("ffmpeg", "ffprobe"):
            for release in RELEASES:
                with self.subTest(name=name, release=release):
                    text = media_input(name, release)
                    profile = build_profile(name, [(name + " --help", text)])
                    found = {o["flag"]: int(bool(o["argument"])) for c in profile["categories"] for o in c["options"]}
                    self.assertEqual(media_inventory(name, text), found)
                    self.assertNotIn("-?", found)
                    self.assertNotIn("-c:", found)

    def test_selector_reaches_details_and_search(self):
        text = media_input("ffmpeg", "resolute")
        self.assertIn("-c[:<stream_spec>] <codec>", text)
        profile = build_profile("ffmpeg", [("ffmpeg --help", text)])
        category, row = next((c, o) for c in profile["categories"] for o in c["options"] if o["flag"] == "-c")
        self.assertEqual(row["argument"], "<codec>")
        view = option_text(profile, category, row)
        self.assertIn("without reencoding", view.searchable)
        self.assertIn("stream specifier", " ".join(view.details))
        self.assertIn("-c[:<stream_spec>]", " ".join(view.details))

    def test_stream_specifier_owns_its_value_even_with_only_short_help(self):
        profile = build_profile("ffmpeg", [("ffmpeg --help", media_input("ffmpeg", "resolute"))])
        profile["discovery"] = {"sources": ["ffmpeg --help"]}
        def context(line):
            return find_context(line, len(line), [], discover=lambda *args: profile)
        with self.assertRaises(HelpError) as missing:
            context("ffmpeg -c:a:1 ")
        self.assertEqual(missing.exception.code, "option_value_required")
        self.assertEqual(context("ffmpeg -c:a:1 copy -c:").query, "-c:")
        self.assertEqual(context("ffmpeg -unknown_advanced_flag value ").profile, profile)

    def test_types_defaults_and_component_owners_survive(self):
        for release in RELEASES:
            profile = build_profile("ffprobe", [("ffprobe --help", media_input("ffprobe", release))])
            rows = {o["flag"]: o for c in profile["categories"] for o in c["options"]}
            probe = rows["-probesize"]
            self.assertEqual(probe["argument"], "<int64>")
            self.assertIn("AVFormatContext", probe["detail"])
            self.assertIn("default 5000000", probe["detail"])
            self.assertNotIn("-ignidx", rows)
            self.assertIn("reduce buffering", rows["-avioflags"]["detail"])
