"""Reconcile .NET SDK help, independent manual entries and literal Bash edits."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import help_route, load_driver_registry
from core import HelpError, find_context, insert_option
from value_semantics import validate_profile_semantics


def load(relative):
    """Read a repository fixture or profile using the same UTF-8 contract."""
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


EVIDENCE = load("tests/fixtures/dotnet-manual/option-headings.json")
COMMANDS = tuple(EVIDENCE["manual_synopses"])
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")
AUDIT = (ROOT / "docs/dotnet-manual-coverage.md").read_text(encoding="utf-8")


def inventory():
    """Expand the manual's command groups without reading the maintained profiles."""
    result = {command: {} for command in COMMANDS}
    for line in AUDIT.splitlines():
        if not re.match(r"^\| (?:all|build|publish|restore|run|test)[a-z ]* \| `-", line):
            continue
        commands, spellings, operand, _ = line.strip(" |").split(" | ", 3)
        for command in COMMANDS if commands == "all" else commands.split():
            for flag in re.findall(r"`([^`]+)`", spellings):
                if flag in result[command]:
                    raise AssertionError(f"Duplicate inventory entry {command} {flag}")
                result[command][flag] = operand
    return result


def captures():
    """Include the unchanged 10.0.402 runtime fixture using its original declarations."""
    versions = dict(EVIDENCE["sdk_help"])
    historical = load("tests/fixtures/help/runtime-followup-captured.json")
    versions["10.0.402"] = {
        row["command"].split()[1]: [
            re.split(r"\s{2,}", line.strip())[0] for line in row["output"].splitlines()
            if re.match(r"^  -", line)
        ]
        for row in historical["captures"] if row["command"].startswith("dotnet ")
    }
    return versions


class DotnetManualInventoryTests(unittest.TestCase):
    def test_versioned_help_synopses_and_qualified_exceptions(self):
        """Reconcile each SDK's actual headings and look up manual-only spellings."""
        table = inventory()
        versions = captures()
        self.assertEqual(set(versions), {"9.0.200", "10.0.100", "10.0.402", "11.0.100"})
        self.assertEqual(EVIDENCE["request"], ["<command>", "--help"])
        for command in COMMANDS:
            names = {flag.rstrip(":") for flag in table[command]}
            help_names = set()
            for version, command_help in versions.items():
                for declaration in command_help[command]:
                    flags, _, arg = declaration.partition(" <")
                    for flag in flags.split(", "):
                        with self.subTest(command=command, version=version, flag=flag):
                            help_names.add(flag)
                            if flag == "-?":
                                self.assertIn("-?", AUDIT)
                                continue
                            self.assertIn(flag, names)
                            # SDK help displays these optional booleans without a placeholder.
                            operand = table[command][flag]
                            if flag in {"--self-contained", "--sc", "--interactive"}:
                                self.assertEqual(operand, "[BOOL]")
                            else:
                                self.assertEqual(bool(arg), operand != "none")
            documented_only = set(EVIDENCE["manual_synopses"][command]) - names
            self.assertEqual(documented_only, {"publish": {"-s"}, "run": {"--force", "--no-dependencies"}}.get(command, set()))
            self.assertIn("-?", help_names)
            route = help_route("dotnet", (command,), REGISTRY)
            self.assertEqual(route.arguments, (command, "--help"))

    def test_each_manual_entry_has_the_native_operand_and_literal_insertion(self):
        """Check every row including colon attachment, independent paths and arity."""
        table = inventory()
        for command, inventory_rows in table.items():
            with self.subTest(command=command):
                profile = load(f"profiles/dotnet-{command}.json")
                rows = [row for category in profile["categories"] for row in category["options"]]
                self.assertCountEqual((r["flag"] for r in rows), inventory_rows.keys())
                self.assertEqual(validate_profile_semantics(profile, mode="maintained"), ())
                line = f"dotnet {command}  'project with spaces.csproj'"
                point = len(f"dotnet {command} ")
                ctx = find_context(line, point, [profile], driver_registry=REGISTRY)
                for row in rows:
                    flag = row["flag"]
                    operand = inventory_rows[flag]
                    with self.subTest(flag=flag):
                        self.assertTrue(row.get("detail"))
                        self.assertEqual(bool(row.get("argument")), operand != "none")
                        self.assertEqual(bool(row.get("argument_optional")), operand.startswith("["))
                        self.assertEqual(row.get("argument_style") == "attached_only", flag.endswith(":"))
                        updated, cursor = insert_option(ctx, row)
                        self.assertEqual(updated, line[:point] + flag + line[point:])
                        self.assertEqual(cursor, point + len(flag) + (not flag.endswith(":")))

    def test_numeric_timeout_runner_boundary_and_mtp_conflicts(self):
        """Retain duration units and protect application and runner-specific arguments."""
        profile = load("profiles/dotnet-test.json")
        rows = {row["flag"]: row for group in profile["categories"] for row in group["options"]}
        node = rows["--blame-hang-timeout"]["value_semantics"]["variants"][0]
        units = {f["id"]: f["unit"]["multiplier"] for f in node["forms"]}
        self.assertEqual(node["bare"]["form"], "ms-bare")
        self.assertEqual(units, {"ms-bare": "0.001", "ms": "0.001", "s": "1", "m": "60", "h": "3600"})
        self.assertEqual(node["when_absent"]["meaning"], "One hour when hang collection is enabled.")
        for flag in set(EVIDENCE["mtp_synopsis"]) - rows.keys():
            self.assertIn(flag, AUDIT.split("## Reference differences and runner selection", 1)[1])
        self.assertIn("binary", rows["--output"]["summary"])
        for cmd, text in (("run", "-- --application"), ("test", "-- Name=Value")):
            current = load(f"profiles/dotnet-{cmd}.json")
            line = f"dotnet {cmd} {text} --"
            with self.assertRaises(HelpError):
                find_context(line, len(line), [current], driver_registry=REGISTRY)
