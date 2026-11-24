"""Reconcile each Go command's flag ownership, release coverage and insertion grammar."""

import csv
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option, validate_profile
from value_semantics import validate_profile_semantics


FIXTURES = ROOT / "tests/fixtures/go-manual"
MENUS = ("build", "test", "run", "mod-tidy")
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")


def read_table(filename):
    """Read an independently recorded, tab-separated source or insertion inventory."""
    with (FIXTURES / filename).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def inventory(menu, edition):
    """Expand reviewed aliases for the given command and Go release."""
    result = {}
    version = tuple(map(int, edition.removeprefix("go").split(".")))
    for row in read_table("inventory.tsv"):
        if menu not in row["menus"].split(","):
            continue
        if row["since"] != "-" and version < tuple(map(int, row["since"].split("."))):
            continue
        for flag in (row["spelling"], row["test_binary_alias"]):
            if flag == "-":
                continue
            if flag in result:
                raise ValueError(f"Duplicate {menu} inventory spelling {flag}")
            result[flag] = row
    return result


def command_profile(menu):
    """Read the maintained JSON and index its exact selectable spellings."""
    path = ROOT / "profiles" / f"go-{menu}.json"
    profile = json.loads(path.read_text(encoding="utf-8"))
    validate_profile(profile, path)
    return profile, {o["flag"]: o for c in profile["categories"] for o in c["options"]}


class GoManualCoverageTests(unittest.TestCase):
    def test_versioned_sources_reconcile_with_each_inventory(self):
        """Compare public flags, shared module registrations and real test-binary aliases."""
        sources = {(r["edition"], r["topic"]): set(r["declarations"].split())
                   for r in read_table("source-declarations.tsv")}
        for edition in ("go1.22.12", "go1.26.0", "go1.27.4"):
            build = sources[edition, "build"]
            shared = build - {"-o"}
            expected = {
                "build": build,
                "test": shared | sources[edition, "test"] | sources[edition, "testflag"]
                        | sources[edition, "test-binary"] | sources[edition, "forwarders"],
                "run": shared | sources[edition, "run"],
                "mod-tidy": sources[edition, "mod-tidy"] | sources[edition, "module-common"] | {"-C"},
            }
            for menu, declarations in expected.items():
                with self.subTest(edition=edition, menu=menu):
                    self.assertEqual(inventory(menu, edition).keys(), declarations)

        for suite, edition in (("noble", "go1.22.12"), ("resolute", "go1.26.0")):
            for topic in ("build", "test", "run", "testflag"):
                manual = sources[suite, topic]
                client = sources[edition, topic]
                with self.subTest(suite=suite, topic=topic):
                    self.assertEqual(manual - client,
                                     {"-i"} if suite == "noble" and topic in {"build", "test"} else set())
                    missing = {"build": {"-C", "-cover", "-covermode", "-coverpkg", "-pgo"},
                               "testflag": {"-fullpath", "-skip"}}
                    self.assertEqual(client - manual, missing.get(topic, set()) if suite == "noble" else set())

    def test_preserved_client_help_matches_upstream_declarations(self):
        """Cross-check fresh inventories against the pre-existing Go 1.27.3 raw captures."""
        history = json.loads((ROOT / "tests/fixtures/help/runtime-followup-captured.json").read_text())
        captures = {item["command"]: item for item in history["captures"]}
        sources = {r["topic"]: set(r["declarations"].split()) for r in read_table("source-declarations.tsv")
                   if r["edition"] == "go1.27.4"}
        for topic, command in (("build", "go help build"), ("testflag", "go help testflag"),
                               ("test", "go test")):
            capture = captures[command]
            declared = set(re.findall(r"^\t(-[a-zA-Z][a-zA-Z0-9]*)(?: [^\n]*)?$",
                                      capture["output"], re.MULTILINE))
            if topic == "build":
                self.assertIn("[-o output]", capture["output"])
                declared.add("-o")
            with self.subTest(topic=topic):
                self.assertIn("go1.27.3", capture["version"])
                self.assertEqual(declared, sources[topic])

    def test_profile_arity_value_semantics_and_alias_ownership(self):
        """Check option and alias insertions, exact arity and complete parameter contracts."""
        for menu in MENUS:
            profile, options = command_profile(menu)
            rows = inventory(menu, "go1.27.4")
            self.assertEqual({f.rstrip("=") for f in options}, rows.keys(), menu)
            aliases = []
            for flag, row in rows.items():
                option = options[flag + "=" if flag == "-buildvcs" else flag]
                with self.subTest(menu=menu, flag=flag):
                    self.assertEqual(option["argument"] or "-", row["operand"])
                    self.assertEqual(option["argument_optional"], row["operand"].startswith("["))
                    self.assertTrue(option.get("detail", "").strip())
                    if option["argument"]:
                        self.assertIn("value_semantics", option)
                    if row["test_binary_alias"] == flag:
                        primary = row["spelling"]
                        aliases.append((primary, flag))
                        self.assertIn(primary, option["detail"])
                        self.assertIn(flag, options[primary]["detail"])
            self.assertEqual(validate_profile_semantics(profile, mode="maintained",
                                                        alias_groups=aliases), ())

    def test_forwarding_package_and_value_boundaries(self):
        """Only Go test accepts parent flags after packages, up to a forwarding marker."""
        run, _ = command_profile("run")
        test, options = command_profile("test")
        for profile, lines in (
            (run, ["go run -p 2 'main 日本.go' -par", "go run -buildvcs=false . -par"]),
            (test, ["go test ./... -args -par", "go test ./... --args -par", "go test ./... -- -par"]),
        ):
            for line in lines:
                with self.subTest(line=line), self.assertRaises(HelpError):
                    find_context(line, len(line), [profile], driver_registry=REGISTRY)
        prefix = "go test ./... -test.cpu '1,2' "
        line = prefix + "-sh  '日本 suffix'"
        context = find_context(line, len(prefix) + 3, [test], driver_registry=REGISTRY)
        self.assertEqual(insert_option(context, options["-test.shuffle"]),
                         (prefix + "-test.shuffle  '日本 suffix'", len(prefix + "-test.shuffle ")))
        for menu, fragment, flag in (("build", "-ov", "-overlay"), ("test", "-pa", "-parallel")):
            profile, entries = command_profile(menu)
            line = f"go {menu} {fragment}"
            context = find_context(line, len(line), [profile], driver_registry=REGISTRY)
            expected = f"go {menu} {flag} "
            self.assertEqual(insert_option(context, entries[flag]), (expected, len(expected)))
        for menu in ("build", "run", "test"):
            profile, options = command_profile(menu)
            line = f"go {menu} -bu"
            context = find_context(line, len(line), [profile], driver_registry=REGISTRY)
            expected = f"go {menu} -buildvcs="
            self.assertEqual(insert_option(context, options["-buildvcs="]), (expected, len(expected)))

    def test_counts_lists_time_budgets_and_sampling_units(self):
        """Guard quantities and special values whose numerical meanings differ by flag."""
        profile, options = command_profile("test")

        def node(flag):
            value = options[flag]["value_semantics"]["variants"][0]
            return profile["value_definitions"][value["ref"]] if "ref" in value else value

        for flag, default in (("-benchtime", "1s"), ("-fuzztime", "unlimited"), ("-fuzzminimizetime", "60s")):
            with self.subTest(flag=flag):
                self.assertIn(default, node(flag)["when_absent"]["meaning"])
                self.assertIn("Nx", [form["syntax"] for form in node(flag)["forms"]])
        self.assertIn("disable", options["-fuzzminimizetime"]["detail"].lower())
        self.assertEqual(node("-blockprofilerate")["forms"][0]["unit"],
                         {"base": "second", "multiplier": "0.000000001"})
        self.assertEqual(node("-memprofilerate")["forms"][0]["unit"], {"base": "byte", "multiplier": "1"})
        self.assertEqual(node("-mutexprofilefraction")["kind"], "count")
        self.assertEqual(node("-cpu")["forms"][0]["bounds"]["min"], "1")
        self.assertIn("comma", node("-cpu")["forms"][1]["grammar"].lower())
        self.assertIn("decimal", options["-shuffle"]["detail"])
