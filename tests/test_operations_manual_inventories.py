"""Compare the Ansible and PlatformIO menus with release-specific CLI declarations."""

import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry
from core import find_context, insert_option

INVENTORIES = ROOT / "tests/fixtures/operations-manual"
HISTORICAL = ROOT / "tests/fixtures/help"


def inventory(name):
    """Map spellings in a separately transcribed release declaration to operand counts."""
    result = {}
    for line in (INVENTORIES / (name + ".txt")).read_text().splitlines():
        if line.startswith("#"):
            continue
        count, spellings = line.split(" | ")
        for spelling in spellings.split():
            if spelling in result:
                raise ValueError(f"Duplicate {spelling} in {name}")
            result[spelling] = int(count)
    return result


def menu(name):
    """Index the actual profile rows, requiring exactly one row per selectable spelling."""
    profile = json.loads((ROOT / "profiles" / (name + ".json")).read_text())
    rows = [row for category in profile["categories"] for row in category["options"]]
    result = {row["flag"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate literal in {name}")
    return result


def fixed_help(text):
    """Read the option column of the retained Ansible argparse and PlatformIO Click help."""
    declarations = {}
    for line in text.splitlines():
        if line.startswith("  -"):
            column = re.split(r" {2,}", line.strip(), maxsplit=1)[0]
            flags = re.findall(r"(?<!\S)-{1,2}[\w-]+", column)
            operand = re.search(r"(?:^| )([A-Z][A-Z_]+|\[[A-Z|]+\])(?: |$)", column)
            declarations.update((flag, int(bool(operand))) for flag in flags)
    return declarations


class OperationsManualInventoryTests(unittest.TestCase):
    def assert_menu(self, name, expected):
        rows = menu(name)
        self.assertEqual(rows.keys(), expected.keys())
        for flag, required in expected.items():
            with self.subTest(menu=name, flag=flag):
                row = rows[flag]
                arity = row.get("argument_count", 1) if row["argument"] else 0
                self.assertEqual(arity, required)
                self.assertFalse(row.get("argument_optional", False))
                self.assertTrue(row["detail"].strip())
                if required:
                    self.assertTrue(row["value_semantics"]["variants"])

    def test_ansible_public_options_and_aliases(self):
        self.assert_menu("ansible-playbook", inventory("ansible-playbook"))

    def test_platformio_release_union_and_executable_aliases(self):
        for route in ("run", "device-monitor"):
            expected = {}
            for version in ("4.3.4", "6.1.18", "6.2.0"):
                expected.update(inventory(f"platformio-{version}-{route}"))
            for executable in ("pio", "platformio"):
                self.assert_menu(f"{executable}-{route}", expected)
            self.assertEqual(menu("pio-" + route), menu("platformio-" + route))

    def test_platformio_global_and_leaf_short_options(self):
        """Resolve root options without consuming the leaf's config or filter spelling."""
        registry = load_driver_registry(ROOT / "config/drivers.example")
        for executable in ("pio", "platformio"):
            for route, leaf_flag in (("run", "-c"), ("device monitor", "-f")):
                command = [executable, *route.split()]
                profile_name = "-".join(command)
                profile = json.loads((ROOT / "profiles" / (profile_name + ".json")).read_text())
                option = menu(profile_name)[leaf_flag]
                for selector in ("-c 'device monitor'", "--caller=run"):
                    prefix = f"{executable} {selector} -f {route} "
                    line = prefix + "-- 'pending value'"
                    with self.subTest(line=line):
                        context = find_context(line, len(prefix) + 2, [profile], driver_registry=registry)
                        self.assertEqual(context.profile["command"], command)
                        self.assertEqual(insert_option(context, option),
                                         (prefix + leaf_flag + " 'pending value'", len(prefix + leaf_flag + " ")))

    def test_historical_native_captures(self):
        ansible = (HISTORICAL / "followup-systems/ansible-playbook.txt").read_text()
        self.assertEqual(fixed_help(ansible), inventory("ansible-playbook"))
        captured = json.loads((HISTORICAL / "expansion-development-captured.json").read_text())
        for route in ("run", "device monitor"):
            declaration = inventory("platformio-6.1.18-" + route.replace(" ", "-"))
            for executable in ("pio", "platformio"):
                entry = captured[f"{executable} {route}"]
                self.assertIn("6.1.18", entry["version"])
                self.assertEqual(fixed_help(entry["text"]), declaration)

    def test_release_specific_options_are_identified_in_details(self):
        for route in ("run", "device-monitor"):
            old = inventory(f"platformio-4.3.4-{route}")
            previous = inventory(f"platformio-6.1.18-{route}")
            current = inventory(f"platformio-6.2.0-{route}")
            rows = menu("pio-" + route)
            for flag in current.keys() - old.keys():
                self.assertIn("Noble 4.3.4", rows[flag]["detail"])
            for flag in current.keys() - previous.keys():
                self.assertIn("6.1.18", rows[flag]["detail"])
                self.assertIn("6.2.0", rows[flag]["detail"])

    def test_ansible_execution_and_listing_qualifications(self):
        rows = menu("ansible-playbook")
        self.assertIn("check_mode: false", rows["--check"]["detail"])
        self.assertIn("still applies", rows["--diff"]["detail"])
        self.assertIn("dynamic includes", rows["--list-tasks"]["detail"])
        self.assertIn("trailing comma", rows["--inventory"]["detail"])
        self.assertIn("Deprecated", rows["--inventory-file"]["detail"])
