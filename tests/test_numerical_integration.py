"""Verify passive numerical paths across parsing, storage, authoring and UI.

Real command expectations retain the migration/preservation fixtures' bounded
provenance. Synthetic conflicts and malformed edits are deliberate test inputs,
not new upstream facts. Every process, target probe and network boundary fails
unless a test explicitly substitutes a fixed response.
"""

from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub

from authoring import NumericalAuthoringError, numerical_review
from collection import numerical_findings
from core import Context, find_context, insert_option, load_profiles
import discovery
from manual_import import ManualCollection, atomic_json
from review import ReviewSession, preview_profile
from test_functional_matrix import BrowserLoop, FakeScreen
from ui import Browser, draw, load_keys
from value_semantics import format_value_semantics, validate_profile_semantics
from test_value_semantics import contract, expression_form, synthetic_node


def entries(profile):
    """Index literal option records, without treating similar summaries as aliases."""
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


def source_profile(name):
    return json.loads((ROOT / "profiles" / (name + ".json")).read_text(encoding="utf-8"))


def definition_text(profile, option):
    """Use the existing formatter solely to compare preservation, not factual truth."""
    return format_value_semantics(option["value_semantics"], definitions=profile.get("value_definitions"), presentation=True)


class NumericalIntegrationTests(unittest.TestCase):
    def setUp(self):
        """Allocate selected disposable paths and refuse operational execution."""
        parent = (ROOT / ".cache/numerical-integration-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if self.root.resolve().parent != parent or self.root.is_symlink() or getattr(self.root, "is_junction", lambda: False)():
            raise RuntimeError("Disposable test directory left its selected parent")
        self.addCleanup(shutil.rmtree, self.root)
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                       "socket.create_connection", "socket.getaddrinfo", "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Integration attempted an operational action")))
        stack.enter_context(patch.dict(os.environ, {"CLI_HELP_CONFIG": "", "CLI_HELP_DRIVERS": ""}))
        if os.name == "nt":
            original_mkdir = Path.mkdir
            def inherited_mkdir(path, mode=0o777, parents=False, exist_ok=False):
                # Inherited ACLs are needed only inside this disposable test tree.
                selected = path.resolve().is_relative_to(self.root.resolve())
                return original_mkdir(path, mode=0o777 if selected else mode, parents=parents, exist_ok=exist_ok)
            stack.enter_context(patch.object(Path, "mkdir", inherited_mkdir))
        self.serial = 0

    def cycle(self, profile):
        """Exercise real isolated cache, draft, preview, backup, save and reload.

        Only terminal attachment is replaced by a fake window. No semantic field
        is edited here, and no numerical completeness policy is imposed on legacy
        or source-derived content. Absolute review paths/timestamps stay in the
        disposable collection, outside reproducible verification reports.
        """
        original = deepcopy(profile)
        self.serial += 1
        folder = self.root / str(self.serial)
        folder.mkdir()
        cache = folder / "cache.json"
        identity = {"command": profile["command"], "parser_revision": discovery.CACHE_VERSION}
        discovery.write_cache(cache, identity, profile)
        self.assertTrue(cache.is_file(), "A structurally valid profile must reach isolated storage")
        cached = discovery.read_cache(cache, identity, 60)
        self.assertEqual(cached, original)
        driver = {"command": profile["command"][0], "paths": [{"command": profile["command"][1:],
                  "help": [], "man": "-".join(profile["command"])}]}
        destination = folder / "collection"
        with ManualCollection(destination) as collection:
            saved = collection.save_documents(cached, driver)
        report = destination / "scan-report.json"
        atomic_json(report, {"schema_version": 1, "finished": True, "records": [
            {"command": profile["command"], "status": "needs_adjustment", "generated": True}]})
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            before = draft.text
            prepared = session.validate(draft, numerical=False)["profile"]
            self.assertEqual(draft.text, before)
            self.assertEqual(prepared, cached)
            self.assertEqual(numerical_review(prepared)["command"], profile["command"])
            screen = FakeScreen(24, 110, ["\n"])
            with BrowserLoop(screen), patch("curses.wrapper", side_effect=lambda fn, *args: fn(screen, *args), create=True):
                inspected = preview_profile(prepared)
            self.assertIn(inspected["flag"], entries(prepared))
            result = session.save(draft)
        loaded = load_profiles(Path(result["profile_directory"]))[0]
        self.assertEqual(profile, original)
        self.assertEqual(loaded, original)
        self.assertFalse((destination / ".import.lock").exists())
        self.assertFalse((destination / ".scan.lock").exists())
        return loaded, saved, report

    def assert_literal_edit(self, profile, selected):
        """Compare with metadata-free insertion and independently protect pending text."""
        prefix = " ".join(profile["command"]) + "   "
        partial, suffix = "--part", "  'retained text' $(never-execute)"
        line = prefix + partial + suffix
        point = len(prefix) + len(partial)
        context = Context(line, point, len(prefix), point, partial, profile)
        result = insert_option(context, selected)
        legacy = deepcopy(profile)
        legacy.pop("value_definitions", None)
        legacy.pop("positional_value_semantics", None)
        for option in entries(legacy).values():
            option.pop("value_semantics", None)
        old_context = Context(line, point, len(prefix), point, partial, legacy)
        self.assertEqual(result, insert_option(old_context, entries(legacy)[selected["flag"]]))
        self.assertTrue(result[0].startswith(prefix + selected["flag"]))
        self.assertTrue(result[0].endswith(suffix))
        self.assertLessEqual(result[1], result[0].index("'retained text'"))

    def reachable_details(self, browser, height=16, width=60):
        """Read actual detail cells through every scroll offset until clamped."""
        screen = FakeScreen(height, width)
        detail_row = 4 + max(3, (height - 9) // 2)
        content = []
        for offset in range(4000):
            browser.detail_offset = offset
            draw(screen, browser, load_keys(None))
            content.extend(text for (row, _col, _attribute), text in sorted(screen.cells.items())
                           if detail_row < row < height - 3)
            if browser.detail_offset != offset:
                break
        else:
            self.fail("Details never reached a finite final scroll position")
        return " ".join(content), screen

    def test_captured_rate_merge_cache_authoring_preview_reload_and_literal_edit(self):
        bundled = source_profile("rsync")
        original = deepcopy(bundled)
        capture = (ROOT / "tests/fixtures/help/rsync.txt").read_text(encoding="utf-8")
        generated = discovery.build_profile("rsync", [("Maintained capture; installed version not inferred", capture)])
        merged = discovery.merge_profiles([bundled, generated])
        expected_flags = {flag.rstrip("=") for p in (bundled, generated) for flag in entries(p)}
        loaded, _saved, _report = self.cycle(merged)
        self.assertEqual({flag.rstrip("=") for flag in entries(loaded)}, expected_flags)
        selected = entries(loaded)["--bwlimit="]
        browser = Browser(loaded, "--bwlimit")
        view = browser.text(selected)
        evidence = json.loads((ROOT / "tests/fixtures/value-semantics/migration-evidence.json").read_text(encoding="utf-8"))["sources"]["rsync"]
        for token in (evidence["bare_bytes_per_second"] + " bytes/second", evidence["version"], "'KB'", "No bandwidth limit", "RATE"):
            self.assertIn(token, " ".join(view.details))
            browser.set_query(token)
            self.assertIn(selected, browser.options())
        browser.set_query("--bwlimit")
        for height, width in ((16, 60), (30, 140), (16, 60)):
            content, screen = self.reachable_details(browser, height, width)
            self.assertIn("Reference:", content)
            self.assertIn("No bandwidth limit", content)
            self.assertIn("Details", screen.text())
        self.assert_literal_edit(loaded, selected)
        self.assertEqual(bundled, original)

    def test_GNU_shared_rules_reach_saved_details_search_and_literal_aliases(self):
        evidence = json.loads((ROOT / "tests/fixtures/value-semantics/preservation-evidence.json").read_text(encoding="utf-8"))
        commands = sorted({case["command"] for case in evidence["cases"]})
        for command in commands:
            capture = (ROOT / "tests/fixtures/help" / ("workflow-" + command + ".txt")).read_text(encoding="utf-8")
            profile = discovery.build_profile(command, [(evidence["capture_manifest"], capture)])
            loaded, _saved, _report = self.cycle(profile)
            browser = Browser(loaded)
            self.assertFalse(any("value_semantics" in option for option in entries(loaded).values()))
            for case in [case for case in evidence["cases"] if case["command"] == command]:
                for flag in (case["option"], case["alias"]):
                    selected = entries(loaded)[flag]
                    details = " ".join(browser.text(selected).details)
                    with self.subTest(command=command, flag=flag):
                        for fragment in case["fragments"]:
                            self.assertIn(fragment, details)
                            browser.set_query(fragment)
                            self.assertIn(selected, browser.options())
                        self.assert_literal_edit(loaded, selected)
                excluded = entries(loaded)[case["excluded"]]
                self.assertNotIn(case["fragments"][0], " ".join(browser.text(excluded).details))

    def test_conflicting_definitions_stay_inactive_through_cache_save_and_reload(self):
        first = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        second = deepcopy(first)
        first["documentation"], second["documentation"] = {"source": "selected synthetic source"}, {"source": "competing synthetic source"}
        second["value_definitions"]["delay"]["meaning"] = "INACTIVE_SCALE_CLAIM"
        second["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "0.001"
        merged = discovery.merge_profiles([first, second])
        loaded, _saved, _report = self.cycle(merged)
        alternative = next(item for item in loaded["documentation"]["alternatives"] if item.get("option") == "--delay")
        self.assertEqual(alternative["definition_scope"], "profile")
        reference = alternative["metadata"]["variants"][0]["ref"]
        self.assertEqual(loaded["value_definitions"][reference]["meaning"], "INACTIVE_SCALE_CLAIM")
        self.assertEqual(validate_profile_semantics(loaded, alias_groups=[("--delay", "-d")]), ())
        browser = Browser(loaded, "INACTIVE_SCALE_CLAIM")
        self.assertEqual(browser.options(), [])
        details = " ".join(browser.text(entries(loaded)["--delay"]).details)
        self.assertIn("Source review", details)
        self.assertIn("competing synthetic source", details)
        self.assertNotIn("INACTIVE_SCALE_CLAIM", details)

    def test_identity_and_arity_conflicts_are_not_activated_by_authoring_roundtrip(self):
        for conflict in ("identity", "arity", "incoming_arity"):
            first = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
            second = deepcopy(first)
            if conflict == "identity":
                first.update(command=["esptool"], identity="esptool-v4")
                second.update(command=["esptool"], identity="esptool-v5")
                first.pop("value_definitions")
                for option in entries(first).values():
                    option.pop("value_semantics", None)
            else:
                larger = second if conflict == "arity" else first
                entries(larger)["--delay"].update(argument="NAME VALUE", argument_count=2)
                entries(larger)["--delay"].pop("value_semantics")
            merged = discovery.merge_profiles([first, second])
            loaded, _saved, _report = self.cycle(merged)
            with self.subTest(conflict=conflict):
                self.assertNotIn("value_semantics", entries(loaded)["--delay"])
                self.assertTrue(loaded["documentation"]["alternatives"])
                self.assertIn("Source review", Browser(loaded).text(entries(loaded)["--delay"]).compact)
                if conflict == "incoming_arity":
                    retained = next(item for item in loaded["documentation"]["alternatives"] if item.get("option") == "--delay")
                    self.assertEqual(retained.get("declaration", {}).get("argument"), "DURATION")
                    self.assertEqual(retained["declaration"].get("argument_count", 1), 1)

    def test_winning_larger_declaration_keeps_its_own_explicit_composite_metadata(self):
        first = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        second = deepcopy(first)
        pair = synthetic_node("composite", meaning="Two synthetic delays in separate operands", slots=2,
            bare={"state": "not_applicable", "reason": "The components define the two operand meanings"},
            forms=[expression_form("FIRST SECOND")], components=[
                {"id": "first", "slot": 1, "required": True, "semantics": {"ref": "delay"}},
                {"id": "second", "slot": 2, "required": True, "semantics": {"ref": "delay"}}])
        entries(second)["--delay"].update(argument="FIRST SECOND", argument_count=2, value_semantics=contract(pair))
        loaded, _saved, _report = self.cycle(discovery.merge_profiles([first, second]))
        selected = entries(loaded)["--delay"]
        self.assertEqual(selected["argument_count"], 2)
        self.assertEqual(selected["value_semantics"]["variants"][0]["kind"], "composite")
        self.assertIn("Two synthetic delays", " ".join(Browser(loaded).text(selected).details))
        self.assertEqual(validate_profile_semantics(loaded), ())

    def test_positional_chip_qualifications_survive_cycle_without_inserting_values(self):
        profile = source_profile("esptool-write-flash")
        loaded, _saved, _report = self.cycle(discovery.merge_profiles([profile]))
        self.assertEqual(loaded["positional_group"], profile["positional_group"])
        self.assertEqual(loaded["positional_value_semantics"], profile["positional_value_semantics"])
        selected = entries(loaded)["--flash-size"]
        browser = Browser(loaded)
        details = " ".join(browser.text(selected).details)
        for token in ("ADDRESS FILE", "4194304 bytes", "ESP32", "Matching to an installed target is not established"):
            self.assertIn(token, details)
            browser.set_query(token)
            self.assertIn(selected, browser.options())
        self.assert_literal_edit(loaded, selected)

    def test_stale_saved_edit_bypasses_old_discovery_cache_and_keeps_inactive_evidence(self):
        profile = discovery.merge_profiles([source_profile("rsync")])
        loaded, saved, report = self.cycle(profile)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            entries(document["profile"])["--bwlimit="]["argument"] = "LIMIT"
            draft.text = json.dumps(document)
            before = draft.text
            preview = session.validate(draft, numerical=False)["profile"]
            self.assertEqual(draft.text, before)
            self.assertNotIn("value_semantics", entries(preview)["--bwlimit="])
            session.save(draft)
        current = load_profiles(Path(saved["profile_directory"]))[0]
        selected = entries(current)["--bwlimit="]
        browser = Browser(current)
        self.assertIn("Source review", browser.text(selected).compact)
        self.assertNotIn("Evidence: verified", " ".join(browser.text(selected).details))
        self.assertTrue(any(item["code"] == "authoring_semantics_review" for item in numerical_findings(current, "profiles/saved.json")))
        line = "rsync --bwli"
        context = find_context(line, len(line), [current], discover=lambda *a, **k: self.fail("A custom static match must bypass discovery"))
        self.assertEqual(context.profile, current)
        self.assertNotIn("value_semantics", entries(context.profile)["--bwlimit="])
        self.assert_literal_edit(current, selected)
        self.assertIn("value_semantics", entries(loaded)["--bwlimit="])

    def test_invalid_edit_cannot_overwrite_cached_or_saved_valid_profile(self):
        profile = discovery.merge_profiles([source_profile("rsync")])
        _loaded, saved, report = self.cycle(profile)
        cache = self.root / "1/cache.json"
        before_cache, before_profile = cache.read_bytes(), Path(saved["profile"]).read_bytes()
        invalid = deepcopy(profile)
        entries(invalid)["--bwlimit="]["value_semantics"]["variants"][0]["forms"][0]["unit"]["multiplier"] = "0"
        identity = {"command": profile["command"], "parser_revision": discovery.CACHE_VERSION}
        discovery.write_cache(cache, identity, invalid)
        self.assertEqual(cache.read_bytes(), before_cache)
        self.assertEqual(discovery.read_cache(cache, identity, 60), profile)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            document["profile"] = invalid
            draft.text = json.dumps(document)
            bad_text = draft.text
            preview = session.validate(draft, numerical=False)["profile"]
            self.assertIn("guidance unavailable", Browser(preview).text(entries(preview)["--bwlimit="]).compact)
            with self.assertRaises(NumericalAuthoringError):
                session.save(draft)
            self.assertEqual(draft.text, bad_text)
        self.assertEqual(Path(saved["profile"]).read_bytes(), before_profile)

    def test_all_opted_in_profiles_preserve_declarations_explanations_and_insertion(self):
        selected_profiles = 0
        for path in sorted((ROOT / "profiles").glob("*.json")):
            original = json.loads(path.read_text(encoding="utf-8"))
            selected = [option for option in entries(original).values() if "value_semantics" in option]
            if not selected and "positional_value_semantics" not in original:
                continue
            selected_profiles += 1
            prepared = discovery.merge_profiles([original])
            loaded, _saved, _report = self.cycle(prepared)
            browser = Browser(loaded)
            self.assertEqual(set(entries(loaded)), set(entries(original)))
            for option in selected:
                with self.subTest(command=original["command"], flag=option["flag"]):
                    current = entries(loaded)[option["flag"]]
                    self.assertEqual(definition_text(loaded, current), definition_text(original, option))
                    for line in definition_text(original, option):
                        self.assertIn(line, browser.text(current).details)
                        self.assertIn(line.casefold(), browser.text(current).searchable)
                    self.assert_literal_edit(loaded, current)
        self.assertGreater(selected_profiles, 0)  # Enumeration grows with actual optional fields.

    def test_unknown_applicability_variants_remain_qualified_after_cycle(self):
        profile = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        first = deepcopy(profile["value_definitions"]["delay"])
        second = deepcopy(first)
        first["applicability"]["version"] = {"state": "known", "values": ["1"]}
        second["applicability"]["version"] = {"state": "known", "values": ["2"]}
        second["forms"][0]["unit"]["multiplier"] = "0.001"
        for option in (entries(profile)["--delay"], entries(profile)["-d"]):
            option["value_semantics"]["variants"] = [deepcopy(first), deepcopy(second)]
        loaded, _saved, _report = self.cycle(discovery.merge_profiles([profile]))
        browser = Browser(loaded)
        selected = entries(loaded)["--delay"]
        self.assertIn("varies by applicability", browser.text(selected).compact)
        details = " ".join(browser.text(selected).details)
        for token in ("No target match is assumed", "version: 1", "version: 2", "0.001 seconds"):
            self.assertIn(token, details)
        self.assertEqual(validate_profile_semantics(loaded, alias_groups=[("--delay", "-d")]), ())

    def test_unassigned_external_prose_does_not_become_a_verified_option_contract(self):
        text = "Options:\n  --output FILE  Select a destination\n\nMYSTERY is measured in UNASSIGNED_SCALE.\n"
        profile = discovery.build_profile("synthetic-contract", [("Synthetic unresolved source", text)])
        loaded, _saved, _report = self.cycle(profile)
        browser = Browser(loaded, "UNASSIGNED_SCALE")
        self.assertEqual(browser.options(), [])
        selected = entries(loaded)["--output"]
        self.assertNotIn("value_semantics", selected)
        details = " ".join(browser.text(selected).details)
        self.assertIn("UNASSIGNED_SCALE", details)
        self.assertIn("relationship to this option is unverified", details)

    def test_mocked_discovery_cache_hit_and_revision_invalidation_feed_authoring(self):
        target = self.root / "capture-specimen"
        target.write_text("Inert identity specimen; never executable test code", encoding="utf-8")
        cache_dir = self.root / "lookup-cache"
        cache_dir.mkdir()
        settings = discovery.Settings(cache_dir=cache_dir)
        text = "Options:\n  --delay=N  Wait in seconds\n\nUNKNOWN is an undocumented amount.\n"
        with patch("discovery.shutil.which", side_effect=lambda name: str(target) if name == "capture-specimen" else None), \
                patch("discovery.run_probe", return_value=text) as response:
            cold = discovery.discover("capture-specimen", settings)
            warm = discovery.discover("capture-specimen", settings)
            self.assertEqual(cold, warm)
            self.assertEqual(response.call_count, 1)
            self.assertEqual(response.call_args.args[0], [str(target), "--help"])
            with patch("discovery.CACHE_VERSION", discovery.CACHE_VERSION + 1):
                fresh = discovery.discover("capture-specimen", settings)
            self.assertEqual(response.call_count, 2)
        loaded, _saved, _report = self.cycle(fresh)
        self.assertIn("shared_documentation_unassigned", {note["code"] for note in loaded["documentation"]["diagnostics"]})
        browser = Browser(loaded, "seconds")
        self.assertEqual(browser.options()[0]["flag"], "--delay=")
        self.assertNotIn("value_semantics", browser.options()[0])
        self.assertEqual(len(list(cache_dir.glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
