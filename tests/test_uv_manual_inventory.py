"""Compare uv menu spellings, argument boundaries and versions with release evidence."""

import csv
import re
import unittest

from test_expansion_systems import ROOT, context_for, options_for, profile_for
from core import HelpError, insert_option
from value_semantics import validate_profile_semantics


FIXTURES = ROOT / "tests/fixtures/uv-manual"
VERSIONS = ("0.6.14", "0.13.9")
# Per path: long-help spelling counts, manual spelling counts, combined menu rows.
COUNTS = {
    "add": ((79, 92), (79, 100), 113),
    "lock": ((59, 64), (59, 67), 76),
    "sync": ((81, 90), (81, 96), 110),
    "tool-install": ((67, 80), (67, 89), 98),
    "venv": ((45, 47), (45, 50), 57),
}
DECLARATION = re.compile(r"^ {2,6}(?:(-[A-Za-z]), )?(--[\w-]+)(?:\.\.\.)?(?: <([A-Z_]+)>)?$")


def long_help(release, command):
    """Read the two literal names and single operand in each captured clap declaration."""
    flags = {}
    for line in (FIXTURES / f"{release}-{command}.txt").read_text(encoding="utf-8").splitlines():
        match = DECLARATION.fullmatch(line)
        if not match:
            if line.lstrip().startswith("-"):
                raise AssertionError(f"Unrecognized release declaration: {line}")
            continue
        short, long, operand = match.groups()
        flags[long] = (long, bool(operand))
        if short:
            flags[short] = (long, bool(operand))
    return flags


def supplements(filename, release, command):
    """Read release-specific spellings recorded separately from the native help headings."""
    with (FIXTURES / filename).open(encoding="utf-8", newline="") as source:
        return {
            row["spelling"]: (row.get("equivalent") or row["equivalent_or_self"], row["operand"] != "-")
            for row in csv.DictReader(source, delimiter="\t")
            if row["release"] == release and row["command"] == command
        }


def release_options(release, command):
    """Merge the public options with supplemental parser and manual spellings."""
    flags = long_help(release, command)
    flags.update(supplements("compatibility.tsv", release, command))
    return flags


class UvManualInventoryTests(unittest.TestCase):
    def test_release_manuals_aliases_and_operand_arity(self):
        for command, (help_counts, manual_counts, total) in COUNTS.items():
            profile = profile_for("uv " + command.replace("-", " "))
            options = options_for(profile)
            self.assertEqual(sum(len(c["options"]) for c in profile["categories"]), total)
            complete = {}
            for index, release in enumerate(VERSIONS):
                help_flags = long_help(release, command)
                manual = dict(help_flags)
                manual.update(supplements("manual-aliases.tsv", release, command))
                accepted = release_options(release, command)
                with self.subTest(command=command, release=release):
                    self.assertEqual(len(help_flags), help_counts[index])
                    self.assertEqual(len(manual), manual_counts[index])
                    self.assertLessEqual(manual.keys(), accepted.keys())
                    for declarations in (accepted, manual):
                        for flag, (canonical, takes_value) in declarations.items():
                            row = options[flag]
                            self.assertEqual(bool(row["argument"]), takes_value, flag)
                            self.assertFalse(row.get("argument_optional", False), flag)
                            self.assertEqual(row.get("argument_count", 1), 1, flag)
                            if flag != canonical:
                                self.assertIn(canonical, row["detail"], flag)
                                self.assertIn(flag, options[canonical]["detail"], canonical)
                            if takes_value and len(flag) == 2:
                                self.assertTrue(row["attached"], flag)
                complete.update(accepted)
            self.assertEqual(options.keys(), complete.keys())

    def test_first_pass_order_and_literal_selection(self):
        for command in COUNTS:
            path = "uv " + command.replace("-", " ")
            profile = profile_for(path)
            options = options_for(profile)
            previous = ROOT / f"tests/fixtures/help/expansion-uv-{command}.txt"
            flags = re.findall(r"^  (--[\w-]+)", previous.read_text(encoding="utf-8"), re.M)
            self.assertEqual(list(options)[:len(flags)], flags)
            prefix, suffix = path + "  ", "  'café fixture'"
            context = context_for(prefix + "--part" + suffix, len(prefix) + 2, profile)
            for flag, row in options.items():
                with self.subTest(command=path, flag=flag):
                    self.assertEqual(insert_option(context, row),
                                     (prefix + flag + suffix, len(prefix + flag) + 1))

    def test_operands_and_fixed_output_levels_have_verified_release_scopes(self):
        for command in COUNTS:
            profile = profile_for("uv " + command.replace("-", " "))
            self.assertFalse(validate_profile_semantics(profile, mode="maintained"))
            by_release = {v: release_options(v, command) for v in VERSIONS}
            for flag, row in options_for(profile).items():
                supported = {v for v in VERSIONS if flag in by_release[v]}
                if len(supported) == 1:
                    self.assertIn(next(iter(supported)), row["detail"], (command, flag))
                if not row["argument"] and flag not in {"-v", "--verbose", "-q", "--quiet"}:
                    continue
                variants = row["value_semantics"]["variants"]
                nodes = [profile["value_definitions"][v["ref"]] if "ref" in v else v for v in variants]
                with self.subTest(command=command, flag=flag):
                    self.assertTrue(all(n["review"]["status"] == "verified" for n in nodes))
                    self.assertEqual({v for n in nodes for v in n["applicability"]["version"]["values"]},
                                     supported)

    def test_release_specific_date_prerelease_and_backend_forms(self):
        lock = options_for(profile_for("uv lock"))
        dates = {tuple(n["applicability"]["version"]["values"]): n
                 for n in lock["--exclude-newer"]["value_semantics"]["variants"]}
        self.assertEqual({form["syntax"] for form in dates[("0.6.14",)]["forms"]},
                         {"YYYY-MM-DD", "YYYY-MM-DDThh:mm:ssZ"})
        self.assertEqual({form["syntax"] for form in dates[("0.13.9",)]["forms"]},
                         {"YYYY-MM-DD", "YYYY-MM-DDThh:mm:ssZ", "P7D", "7 days", "false"})
        self.assertIn("24 hours", dates[("0.13.9",)]["time_basis"])
        self.assertIn("if-necessary-or-explicit", lock["--prerelease"]["detail"])
        tool = options_for(profile_for("uv tool install"))
        torch = tool["--torch-backend"]["value_semantics"]["variants"][0]
        for name in ("auto", "cpu", "cu126", "rocm6.2.4", "xpu"):
            self.assertIn(name, torch["forms"][0]["grammar"])

    def test_separate_joined_and_quoted_values_and_end_marker(self):
        for path, arguments in (
            ("uv add", "-r'reqs file.txt' -m \"python_version < '3.12'\""),
            ("uv lock", "--exclude-newer='7 days' -P'demo<2'"),
            ("uv sync", "-vv --only-install-package demo"),
            ("uv tool install", "example --with-executables-from=helper -p3.12"),
            ("uv venv", "'my env' --prompt 'example env' -p3.12"),
        ):
            profile = profile_for(path)
            line = path + " " + arguments + " --"
            with self.subTest(line=line):
                context_for(line, len(line), profile)
                end = path + " -- operand --"
                with self.assertRaises(HelpError):
                    context_for(end, len(end), profile)
        for path, operand in (("uv add", "-r"), ("uv lock", "--config-settings"),
                              ("uv sync", "--only-install-package"),
                              ("uv tool install", "-w"), ("uv venv", "-p")):
            line = path + " " + operand + " "
            with self.subTest(line=line), self.assertRaises(HelpError):
                context_for(line, len(line), profile_for(path))
