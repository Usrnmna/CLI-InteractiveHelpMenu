"""Protect passive enumeration, source relationships, and durable review identity."""

from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import unittest
from unittest.mock import patch
import uuid


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("numerical_inventory", ROOT / "scripts/inventory_numerical_descriptions.py")
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def review_group(report, name="fixture-review"):
    """Create an explicit unresolved test review, not an inferred unit assignment."""
    return {
        "id": name, "classification": "unresolved", "reason": "Synthetic review contract",
        "disposition": "investigate", "deficiency": "Numerical meanings require review",
        "evidence": "unresolved", "applicability": "Synthetic fixture only",
        "references": ["Source observations"], "proposed_action": "Review the documented value forms",
        "priority": "P2", "findings": ["F7"], "later_steps": [2],
        "verification": "Compare explicit source meanings with the displayed explanation",
        "acceptance": "No undocumented numerical meaning is claimed",
        "entries": {entry["id"]: entry["fingerprint"] for entry in report["entries"]},
    }


class NumericalInventoryTests(unittest.TestCase):
    def setUp(self):
        parent = (ROOT / ".cache/numerical-inventory-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        # Verify the absolute cleanup target before registering a recursive delete.
        if self.root.resolve().parent != parent or self.root.is_symlink():
            raise RuntimeError("Disposable snapshot left its intended test directory")
        self.addCleanup(shutil.rmtree, self.root)
        for relative in ("profiles", "cli_help", "config/drivers.example", "tests/fixtures/help",
                         "tests/fixtures/value-semantics"):
            (self.root / relative).mkdir(parents=True)
        for relative in (*inventory.PROTECTED_SOURCES, "cli_help/command_paths.py", "cli_help/invocation.py"):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.profile = {"command": ["sample"], "description": "Synthetic command",
                        "categories": [{"name": "Options", "options": [
                            {"flag": "--count", "argument": "N", "summary": "Select records"},
                            {"flag": "--quiet", "summary": "Suppress output"}]}]}
        self.write_json("profiles/sample.json", self.profile)
        self.write_json("tests/fixtures/help/matrix.json", [
            {"command": "sample", "flags": {"--count": "N"}, "fixture": "sample.txt", "live_flags": ["--count"]}])
        (self.root / "tests/fixtures/help/sample.txt").write_text(
            "Options:\n  -n, --count N  Select records\n  --other SIZE  Set an external size\n", encoding="utf-8")

    def write_json(self, relative, document):
        """Write synthetic data only within the disposable snapshot."""
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")

    def build(self, reviews=None):
        return inventory.build_inventory(self.root, reviews)

    def completed(self):
        report = self.build()
        reviews = {"format_version": 1, "groups": [review_group(report)]}
        return self.build(reviews), reviews

    def test_independent_counts_and_observation_relationships(self):
        report = self.build()
        profiles = [json.loads(p.read_text()) for p in (self.root / "profiles").glob("*.json")]
        expected = sum(len(c["options"]) for p in profiles for c in p["categories"])
        self.assertEqual(report["counts"]["profile_option_records"], expected)
        entries = {entry["id"]: entry for entry in report["entries"]}
        count = entries["option|sample|--count"]
        self.assertEqual({obs["role"] for obs in count["observations"]},
                         {"bundled_option", "matrix_expectation", "fixture_help"})
        self.assertIn("option|sample|-n", entries)
        self.assertIn("option|sample|--other", entries)  # Not a matrix sentinel.
        self.assertIn(["-n", "--count"], [obs.get("aliases") for obs in count["observations"]])
        self.assertTrue(all(not Path(source["path"]).is_absolute() for source in report["sources"]))

    def test_new_entries_do_not_inherit_review_and_old_identity_survives_insertion(self):
        original, reviews = self.completed()
        old = next(e for e in original["entries"] if e["id"] == "option|sample|--count")
        self.profile["categories"][0]["options"].insert(0, {"flag": "--new", "argument": "VALUE", "summary": "New value"})
        self.write_json("profiles/sample.json", self.profile)
        report = self.build(reviews)
        current = next(e for e in report["entries"] if e["id"] == old["id"])
        self.assertEqual(current["fingerprint"], old["fingerprint"])
        self.assertEqual(current["review_group"], old["review_group"])
        self.assertTrue(any(d["code"] == "review_missing" and d["location"] == "option|sample|--new" for d in report["diagnostics"]))

    def test_fixture_growth_and_unassigned_sources_are_visible(self):
        _, reviews = self.completed()
        path = self.root / "tests/fixtures/help/sample.txt"
        path.write_text(path.read_text() + "  --future TIME  New timeout\n", encoding="utf-8")
        (path.parent / "unowned.txt").write_text("Options:\n  --size SIZE  Size\n", encoding="utf-8")
        report = self.build(reviews)
        self.assertIn("option|sample|--future", {e["id"] for e in report["entries"]})
        self.assertIn("unassigned_help_source", {d["code"] for d in report["diagnostics"]})
        self.assertIn("tests/fixtures/help/unowned.txt", {s["path"] for s in report["sources"]})

    def test_manifest_positions_do_not_stale_unchanged_option_facts(self):
        original, reviews = self.completed()
        matrix = json.loads((self.root / "tests/fixtures/help/matrix.json").read_text())
        matrix.insert(0, {"command": "other", "flags": {"--new": "N"}})
        self.write_json("tests/fixtures/help/matrix.json", matrix)
        updated = self.build(reviews)
        identity = "option|sample|--count"
        self.assertEqual(next(e["fingerprint"] for e in original["entries"] if e["id"] == identity),
                         next(e["fingerprint"] for e in updated["entries"] if e["id"] == identity))

    def test_version_and_keyword_expectations_are_not_displayed_options(self):
        matrix = json.loads((self.root / "tests/fixtures/help/matrix.json").read_text())
        matrix[0].update(keyword_sentinels=["child"], version_sentinels={"2": {
            "flags": ["--variant"], "argument_counts": {"--variant": 1}}})
        self.write_json("tests/fixtures/help/matrix.json", matrix)
        entries = {e["id"]: e for e in self.build()["entries"]}
        variant = entries["option|sample|--variant"]["observations"][0]
        self.assertEqual(variant["role"], "version_expectation")
        self.assertEqual(variant["version_key"], "2")
        self.assertFalse(variant["display_content"])
        route = entries["route|sample|"]
        contract = next(o["expectations"] for o in route["observations"] if o["role"] == "primary_matrix")
        self.assertEqual(contract["keyword_sentinels"], ["child"])
        self.assertNotIn("keyword|sample|child", entries)

    def test_stale_duplicate_conflicting_and_orphan_annotations(self):
        _, reviews = self.completed()
        changed = deepcopy(reviews)
        identity = "option|sample|--count"
        changed["groups"][0]["entries"][identity] = "obsolete"
        duplicate = deepcopy(changed["groups"][0])
        duplicate.update(id="conflicting-review", classification="count")
        duplicate["entries"] = {identity: "obsolete", "option|missing|--old": "old"}
        changed["groups"].append(duplicate)
        codes = {d["code"] for d in self.build(changed)["diagnostics"]}
        self.assertTrue({"review_stale", "review_duplicate", "review_conflict", "review_orphan"} <= codes)

    def test_changed_long_description_requires_review_beyond_excerpt(self):
        self.profile["categories"][0]["options"][0]["detail"] = "x" * 650 + "seconds"
        self.write_json("profiles/sample.json", self.profile)
        _, reviews = self.completed()
        self.profile["categories"][0]["options"][0]["detail"] = "x" * 650 + "milliseconds"
        self.write_json("profiles/sample.json", self.profile)
        self.assertTrue(any(d["code"] == "review_stale" and d["location"] == "option|sample|--count"
                            for d in self.build(reviews)["diagnostics"]))

    def test_capture_manifests_modules_and_arity_are_distinct(self):
        self.write_json("config/drivers.example/sample.json", {
            "command": "sample", "global_values": ["--parent-count"],
            "paths": [{"command": ["child"], "help": ["child", "--help"]}]})
        self.write_json("tests/fixtures/help/new-capture.json", {"cases": [{
            "command": "sample child", "version": "sample 1", "text": "Options:\n  --child N  Child count\n"}],
            "module": {"argv": ["<SELECTED_PYTHON>", "-m", "pip", "--help"],
                       "text": "Options:\n  --timeout SECONDS  Socket timeout\n"}})
        report = self.build()
        entries = {e["id"]: e for e in report["entries"]}
        self.assertIn("option|sample child|--child", entries)
        self.assertIn("option|<selected-python> -m pip|--timeout", entries)
        self.assertIn("route|python3 -m pip install|", entries)
        parent = entries["option|sample|--parent-count"]["observations"][0]
        self.assertFalse(parent["display_content"])
        route = entries["route|sample|"]
        self.assertTrue(route["has_explicit_children"])
        self.assertTrue(any(o["role"] == "implicit_driver_root" for o in route["observations"]))

    def test_passive_and_deterministic_with_hostile_snapshot_source(self):
        marker = self.root / "executed"
        with (self.root / "cli_help/command_paths.py").open("a", encoding="utf-8") as stream:
            stream.write(f"\n__import__('pathlib').Path({str(marker)!r}).write_text('executed')\n")
        before = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.root.rglob("*") if p.is_file()}
        with patch.object(subprocess, "Popen", side_effect=AssertionError("process")), \
                patch.object(subprocess, "run", side_effect=AssertionError("process")), \
                patch.object(socket, "socket", side_effect=AssertionError("network")):
            first = inventory.encoded(self.build())
            second = inventory.encoded(self.build())
        self.assertEqual(first, second)
        self.assertFalse(marker.exists())
        after = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_unsupported_declaration_fails_without_evaluation(self):
        path = self.root / "cli_help/command_paths.py"
        path.write_text(path.read_text().replace('DOCKER_GROUPS = {', 'DOCKER_GROUPS = dict({').replace('\nBUILTIN_PATHS =', ')\nBUILTIN_PATHS ='), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unsupported literal declaration"):
            self.build()

    def test_output_requires_explicit_safe_destination(self):
        report, reviews = self.completed()
        annotations = self.root / inventory.REVIEW_PATH
        self.write_json(inventory.REVIEW_PATH, reviews)
        output = self.root / "tests/reports/inventory.json"
        inventory.write_output(self.root, output, report, annotations)
        original = output.read_bytes()
        inventory.write_output(self.root, output, report, annotations)
        self.assertEqual(output.read_bytes(), original)
        for forbidden in (annotations, self.root / "profiles/sample.json", self.root / "profiles/new.json"):
            with self.subTest(forbidden=forbidden), self.assertRaises(ValueError):
                inventory.write_output(self.root, forbidden, report, annotations)
        other = self.root / "notes.json"
        other.write_text('{"private":true}', encoding="utf-8")
        with self.assertRaises(ValueError):
            inventory.write_output(self.root, other, report, annotations)
        self.assertEqual(other.read_text(), '{"private":true}')

    def test_output_rejects_links_even_to_an_existing_inventory(self):
        report, _ = self.completed()
        target = self.root / "retained.json"
        target.write_text(inventory.encoded(report), encoding="utf-8")
        link = self.root / "linked.json"
        try:
            os.symlink(target, link)
        except OSError as error:
            self.skipTest(f"File links are unavailable: {error}")
        before = target.read_bytes()
        with self.assertRaisesRegex(ValueError, "link"):
            inventory.write_output(self.root, link, report, self.root / inventory.REVIEW_PATH)
        self.assertEqual(target.read_bytes(), before)

    def test_invalid_review_shapes_are_actionable(self):
        for reviews in ([], {"groups": {}}, {"groups": [{"entries": []}]}):
            with self.subTest(reviews=reviews), self.assertRaisesRegex(ValueError, "[Rr]eview"):
                self.build(reviews)

    def test_missing_input_and_duplicate_json_keys_fail_actionably(self):
        (self.root / "tests/fixtures/help/matrix.json").write_text('[{"command":"sample","command":"other"}]', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            self.build()
        (self.root / "tests/fixtures/help/matrix.json").unlink()
        self.write_json("tests/fixtures/help/references.json", [{"command": "sample", "flags": {}, "fixture": "missing.txt"}])
        self.assertIn("missing_fixture", {d["code"] for d in self.build()["diagnostics"]})

    def test_main_defaults_to_stdout_and_check_rejects_missing_review(self):
        before = {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()}
        output = io.StringIO()
        with redirect_stdout(output):
            code = inventory.main(["--root", str(self.root), "--check", "--summary"])
        self.assertEqual(code, 1)
        self.assertGreater(json.loads(output.getvalue())["review_summary"]["diagnostic_counts"]["review_missing"], 0)
        self.assertEqual(before, {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()})

    def test_real_source_counts_are_independent_and_reviews_are_complete(self):
        review_path = ROOT / inventory.REVIEW_PATH
        if not review_path.exists():
            self.skipTest("Curated inventory has not been authored")
        reviews = json.loads(review_path.read_text(encoding="utf-8"))
        report = inventory.build_inventory(ROOT, reviews)
        profiles = [json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "profiles").rglob("*.json")]
        self.assertEqual(report["counts"]["bundled_profiles"], len(profiles))
        self.assertEqual(report["counts"]["profile_option_records"], sum(len(c["options"]) for p in profiles for c in p["categories"]))
        matrix = json.loads((ROOT / "tests/fixtures/help/matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(report["counts"]["primary_matrix_cases"], len(matrix))
        drivers = [json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "config/drivers.example").glob("*.json")]
        self.assertEqual(report["counts"]["example_driver_route_records"], sum(len(d["paths"]) for d in drivers))
        from command_paths import load_driver_registry
        with patch.object(subprocess, "Popen", side_effect=AssertionError("process")), \
                patch.object(socket, "socket", side_effect=AssertionError("network")):
            registry = load_driver_registry(ROOT / "config/drivers.example")
        actual_routes = {(program, *child) for program, driver in registry.items() for child in driver.paths}
        generated_routes = {tuple(e["command"]) for e in report["entries"] if e["kind"] == "route"
                            and any(o["role"] in ("builtin_root", "builtin_explicit", "driver_explicit", "implicit_driver_root") for o in e["observations"])}
        self.assertEqual(generated_routes, actual_routes)
        fixture_files = {p.relative_to(ROOT).as_posix() for p in (ROOT / "tests/fixtures/help").rglob("*") if p.is_file()}
        self.assertTrue(fixture_files <= {source["path"] for source in report["sources"]})
        self.assertEqual(report["diagnostics"], [])


if __name__ == "__main__":
    unittest.main()
