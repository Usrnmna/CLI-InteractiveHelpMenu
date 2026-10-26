"""Enumerate command coverage and exercise every available option without probes.

Each named command has its own test ID. Routes without documentation fixtures
receive routing evidence only; no synthetic help is presented as real coverage.
"""

from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import help_route, load_driver_registry, resolve_path
from core import find_context, insert_option, validate_profile
from discovery import build_profile, parse_help
from invocation import module_driver
from test_functional_matrix import BrowserLoop, FakeScreen
from test_numerical_presentation import CellScreen
from ui import Browser, draw, load_keys, run_browser

FIXTURES = ROOT / "tests/fixtures/help"
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")
EVIDENCE = {}


def inventory():
    """Union registered routes, bundled profiles and maintained fixture manifests."""
    result = {}

    def entry(command):
        command = " ".join(command) if isinstance(command, list) else command
        return result.setdefault(command, {"sources": [], "profiles": [], "documents": []})

    for name, driver in REGISTRY.items():
        for path, route in driver.paths.items():
            item = entry(" ".join((name, *path)))
            source = Path(route.source).relative_to(ROOT).as_posix() if route.source else "cli_help/command_paths.py"
            item["sources"].append(source)
    for path in sorted((ROOT / "profiles").glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        item = entry(profile["command"])
        item["profiles"].append((path.relative_to(ROOT).as_posix(), profile))

    for path in sorted(FIXTURES.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(document, list):
            records = [(record.get("command"), record) for record in document if isinstance(record, dict)]
        elif isinstance(document.get("cases"), list):
            records = [(record.get("command"), record) for record in document["cases"]]
        elif isinstance(document.get("captures"), list):
            records = [(record.get("command"), record) for record in document["captures"]]
        else:
            records = [(key, record) for key, record in document.items()
                       if isinstance(record, dict) and ("text" in record or "fixture" in record)]
        for command, record in records:
            if not command:
                continue
            # Capture labels include upstream editions and help topics that are
            # evidence for a route, rather than additional executable paths.
            if isinstance(command, str):
                command = re.sub(r" \((?:classic|modern)\)$", "", command)
                command = {"go help build": "go build", "go help testflag": "go test"}.get(command, command)
            # These two manual capture keys identify pages, not argv paths.
            if path.name == "workflow-manual-edge-cases.json" and command == "git-show":
                command = "git show"
            item = entry(command)
            source = path.relative_to(ROOT).as_posix()
            item["sources"].append(source)
            text = record.get("text", record.get("output"))
            if "fixture" in record:
                fixture = FIXTURES / record["fixture"]
                text = fixture.read_text(encoding="utf-8")
                source = fixture.relative_to(ROOT).as_posix()
            if isinstance(text, str) and not any(existing[1] == text for existing in item["documents"]):
                item["documents"].append((source, text))
    modules = json.loads((FIXTURES / "python-module-captured.json").read_text(encoding="utf-8"))
    for interpreter in ("python", "python3"):
        for module in ("pip", "pytest"):
            for suffix in module_driver(module).paths:
                command = " ".join((interpreter, "-m", module, *suffix))
                item = entry(command)
                item["sources"].append("cli_help/invocation.py")
                item["documents"].append(("tests/fixtures/help/python-module-captured.json",
                                          modules[" ".join((module, *suffix))]["text"]))
    for item in result.values():
        item["sources"] = sorted(set(item["sources"] + [source for source, _ in item["profiles"]]))
    return dict(sorted(result.items()))


INVENTORY = inventory()
STATIC_PATHS = [tuple(profile["command"]) for item in INVENTORY.values() for _, profile in item["profiles"]]


class InventoryRegressionTests(unittest.TestCase):
    def setUp(self):
        """Fail immediately if passive parsing, rendering or insertion starts I/O."""
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen",
                       "socket.socket", "socket.create_connection", "discovery.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Passive inventory attempted execution")))

    def exercise_profile(self, profile):
        """Check every category/option at three sizes, literal edits and modal controls."""
        original = deepcopy(profile)
        validate_profile(profile, Path("inventory-fixture.json"))
        browser = Browser(profile)
        command = " ".join(profile["command"])
        editable = dict(profile)
        # Installed-version identity is independently tested with controlled probes.
        editable.pop("identity", None)
        prefix, suffix = command + "  ", "  'café/日本 destination'"
        pending = prefix + "--partial" + suffix
        context = find_context(pending, len(prefix) + 4, [editable], driver_registry=REGISTRY)
        count = 0
        screen = CellScreen(24, 100)
        for index, category in enumerate(profile["categories"]):
            browser.category = index
            for selected, option in enumerate(category["options"]):
                count += 1
                browser.selected = selected
                browser.detail_offset = 0
                for height, width in ((16, 60), (24, 100), (32, 160), (16, 60)):
                    screen.lines, screen.columns = height, width
                    draw(screen, browser, load_keys())
                    self.assertIn("OPTIONS", screen.text())
                    self.assertIs(browser.options()[browser.selected], option)
                view = browser.text(option)
                self.assertIn(option["summary"].casefold(), view.searchable)
                self.assertIn(option, Browser(profile, option["flag"]).options(index))
                flag = option["flag"]
                if option.get("argument_style") == "equals" and not flag.endswith("="):
                    flag += "="
                edited, point = insert_option(context, option)
                self.assertEqual(edited, prefix + flag + suffix)
                joined = flag.endswith("=") or option.get("argument_style") == "attached_only"
                self.assertEqual(point, len(prefix + flag) + (0 if joined else 1))
                self.assertEqual(context.line, pending)
        browser.set_query("no-match-inventory-7f32")
        draw(screen, browser, load_keys())
        self.assertIn("No matches", screen.text())
        self.assertNotIn("Option:", screen.text())
        browser.set_query("")
        draw(screen, browser, load_keys())
        self.assertNotIn("No matches", screen.text())
        # Escape cancels search before Enter selects the original first option.
        screen = FakeScreen(24, 100, ["/", "\u2603", "\x1b", "\n"])
        with BrowserLoop(screen):
            self.assertEqual(run_browser(screen, profile, "", load_keys()), profile["categories"][0]["options"][0])
        # Exercise focus, category/option movement, detail scrolling and preview.
        screen = FakeScreen(24, 100, ["\t", "j", "\n", "j", "]", "[", "h", "l", "\x1b"])
        with BrowserLoop(screen):
            self.assertIsNone(run_browser(screen, profile, "", load_keys(), preview=True))
        self.assertEqual(Browser(profile).detail_offset, 0)
        self.assertEqual(profile, original)
        return count

    def verify_path(self, command, item):
        """Record route, fixture and bundled coverage separately for one path."""
        evidence = EVIDENCE[command] = {"test": self.id(), "sources": item["sources"],
            "route": "not tested", "bundled": [], "fixtures": [], "live_target": "not tested"}
        words = command.split()
        if len(words) > 2 and words[1] == "-m":
            route = module_driver(words[2]).paths[tuple(words[3:])]
            self.assertTrue(route.arguments)
            evidence["route"] = "pass (module grammar and explicit fixture profile)"
        elif words[0] in REGISTRY and tuple(words[1:]) in REGISTRY[words[0]].paths:
            self.assertEqual(resolve_path(words, STATIC_PATHS, REGISTRY).words, tuple(words))
            route = help_route(words[0], tuple(words[1:]), REGISTRY)
            self.assertTrue(route.arguments or route.manual)
            evidence["route"] = "pass"
        else:
            self.assertEqual(resolve_path(words, STATIC_PATHS, REGISTRY).words, tuple(words))
            evidence["route"] = "pass (static profile or generic root resolution)"
        for source, profile in item["profiles"]:
            evidence["bundled"].append({"source": source, "options": self.exercise_profile(profile),
                "categories": len(profile["categories"]), "status": "pass"})
        for source, text in item["documents"]:
            entries = parse_help(text, source)
            if not entries:
                evidence["fixtures"].append({"source": source, "options": 0,
                    "status": "pass (empty parse)", "rendering": "not tested (no parsed options)"})
                continue
            profile = build_profile(words, [(source, text)])
            evidence["fixtures"].append({"source": source, "options": self.exercise_profile(profile),
                "categories": len(profile["categories"]), "status": "pass"})


def path_test(command, item):
    """Bind one test to its command path without executing fixture programs."""
    def test(self):
        self.verify_path(command, item)
    test.__doc__ = "Offline route and available-document coverage: " + command
    return test


for index, (command, item) in enumerate(INVENTORY.items()):
    name = f"test_path_{index:03d}_" + re.sub(r"\W+", "_", command)
    setattr(InventoryRegressionTests, name, path_test(command, item))


if __name__ == "__main__":
    unittest.main()
