"""Exercise prospective coverage with disposable source mutations and no targets.

Claimed verified statuses in toy profiles are controlled validator inputs; no
upstream factual verification is asserted. Real expectations use the separate
migration evidence and the actual browser's draw/search construction.
"""

from contextlib import ExitStack, redirect_stdout
from copy import deepcopy
from dataclasses import replace
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "cli_help"))
import check_numerical_coverage as coverage
from test_numerical_inventory import review_group
from test_value_semantics import contract, expression_form, synthetic_node
from value_semantics import validate_value_semantics

if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub
from ui import Browser, draw, load_keys
from test_functional_matrix import FakeScreen


def claimed_node(kind="duration", **changes):
    """Provide a toy claim with complete fields, never a verified command fact."""
    node = synthetic_node(kind, **changes)
    node["review"] = {"status": "verified", "references": [{
        "source": "https://example.invalid/coverage-specimen/manual", "locator": "Controlled claimed-state input only"}]}
    return node


def empty_policy():
    return {"format_version": 1, "legacy_baseline": {
        "origin_revision": "a" * 40, "reason": "Controlled pre-existing migration debt only.",
        "scope": "Exact toy entries listed below; no inherited eligibility.",
        "invalidation": "Relevant content or review changes require renewed investigation.", "entries": []},
        "exceptions": []}


class NumericalCoverageTests(unittest.TestCase):
    def setUp(self):
        """Allocate an inherited-permission snapshot and block operational APIs."""
        parent = (ROOT / ".cache/numerical-coverage-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if self.root.resolve().parent != parent or self.root.is_symlink():
            raise RuntimeError("Disposable snapshot left the selected cache directory")
        self.addCleanup(shutil.rmtree, self.root)
        for relative in (*coverage.inventory.PROTECTED_SOURCES, "cli_help/command_paths.py", "cli_help/invocation.py"):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        for relative in ("profiles", "config/drivers.example", "tests/fixtures/help", "tests/fixtures/value-semantics"):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        self.write("tests/fixtures/help/matrix.json", [])
        self.profile = {"command": ["coverage-specimen"], "description": "Toy numerical claim, not a real target",
                        "categories": [{"name": "Values", "options": [{"flag": "--delay", "argument": "N",
                            "summary": "Select a toy wait", "value_semantics": contract(claimed_node())}]}]}
        self.write_profile()
        self.reviews = self.reviewed()
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                       "socket.create_connection", "socket.getaddrinfo", "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Coverage attempted an operational action")))

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def write_profile(self):
        self.write("profiles/specimen.json", self.profile)

    def reviewed(self, overrides=None):
        """Create explicit synthetic reviews; production reconciliation never does so."""
        report = coverage.inventory.build_inventory(self.root)
        groups = {}
        classes = {"duration": "quantity", "quantity": "quantity", "count": "count", "index": "identifier_or_index",
                   "identifier": "identifier_or_index", "level": "level_or_enumeration", "enumeration": "level_or_enumeration",
                   "timestamp": "timestamp_or_duration_expression", "duration_expression": "timestamp_or_duration_expression",
                   "delegated": "delegated_value", "composite": "composite", "nonnumerical": "nonnumerical"}
        records = {record["id"]: record for record in coverage.profile_records(self.profile, "profiles/specimen.json")}
        for entry in report["entries"]:
            record = records.get(entry["id"])
            nodes = list(coverage.semantic_nodes(record["metadata"], self.profile.get("value_definitions"))) if record else []
            classification = classes.get(nodes[0].get("kind"), "nonnumerical") if nodes else "nonnumerical"
            classification = (overrides or {}).get(entry["id"], classification)
            if classification not in groups:
                group = review_group({"entries": []}, "toy-" + classification)
                group.update(classification=classification, evidence="source-derived")
                groups[classification] = group
            groups[classification]["entries"][entry["id"]] = entry["fingerprint"]
        return {"format_version": 1, "groups": list(groups.values()), "coverage_policy": empty_policy()}

    def check(self, mode="prospective"):
        return coverage.check_coverage(self.root, self.reviews, mode=mode)

    def codes(self, report):
        return {item["code"] for item in report["diagnostics"] if item["severity"] == "error"}

    def row(self):
        """Construct one explicitly selected toy deferral for failure mutations."""
        record = next(coverage.profile_records(self.profile, "profiles/specimen.json"))
        report = coverage.inventory.build_inventory(self.root, self.reviews)
        entry = next(entry for entry in report["entries"] if entry["id"] == record["id"])
        group = next(group for group in self.reviews["groups"] if group["id"] == entry["review_group"])
        items = validate_value_semantics(record["metadata"], mode="maintained", context=record["context"],
                                         definitions=self.profile.get("value_definitions"))
        return {"id": record["id"], "source": record["source"], "fingerprint": coverage.record_fingerprint(record),
                "review_fingerprint": coverage.review_fingerprint(group), "codes": sorted({item.code for item in items})}

    def test_complete_profile_and_normal_local_gate(self):
        report = self.check()
        self.assertTrue(report["passed"], report["diagnostics"])
        self.assertTrue(report["full_maintained_ready"])
        self.assertEqual(report["remaining_debt"], [])
        self.assertIn("display_search_propagation", report["active_gates"])

    def test_concise_details_and_original_evidence_have_separate_obligations(self):
        """Check fixed value facts independently of the display formatter."""
        option = self.profile["categories"][0]["options"][0]
        view = Browser(self.profile).text(option)
        details = " ".join(view.details)
        for phrase in ("bare numbers: seconds", "Applicability unconfirmed", "Input N"):
            self.assertIn(phrase, details)
        for phrase in ("Evidence: verified.", "https://example.invalid/coverage-specimen/manual"):
            self.assertNotIn(phrase, details)
            self.assertIn(phrase.casefold(), view.searchable)
        self.assertTrue(self.check()["passed"], self.check()["diagnostics"])

    def test_partial_loss_of_value_rules_qualifications_or_search_evidence_fails(self):
        """A populated pane or search corpus cannot hide one missing obligation."""
        original = coverage.presentation.option_text
        for prefix in ("Value", "Applicability unconfirmed", "Input N"):
            def omit(*args, **kwargs):
                view = original(*args, **kwargs)
                return replace(view, details=tuple(line for line in view.details if not line.startswith(prefix)))
            with self.subTest(prefix=prefix), patch.object(coverage.presentation, "option_text", side_effect=omit):
                self.assertIn("coverage_details_missing", self.codes(self.check()))
        def omit_reference(*args, **kwargs):
            view = original(*args, **kwargs)
            return replace(view, searchable=view.searchable.replace(
                "https://example.invalid/coverage-specimen/manual", ""))
        with patch.object(coverage.presentation, "option_text", side_effect=omit_reference):
            self.assertIn("coverage_search_missing", self.codes(self.check()))

    def test_new_profile_category_required_optional_fixed_and_keyword_are_discovered(self):
        original = deepcopy(self.profile)
        for kind in ("profile", "category", "required", "optional", "fixed", "keyword"):
            with self.subTest(kind=kind):
                self.profile = deepcopy(original)
                new = {"flag": "--new", "argument": "SIZE", "summary": "Select a size"}
                if kind == "profile":
                    document = deepcopy(self.profile)
                    document["command"] = ["new-profile"]
                    document["categories"][0]["options"] = [new]
                    self.write("profiles/new.json", document)
                elif kind == "category":
                    self.profile["categories"].append({"name": "New category", "options": [new]})
                else:
                    if kind == "optional":
                        new["argument_optional"] = True
                    elif kind == "fixed":
                        new.pop("argument")
                        new["flag"] = "-9"
                    elif kind == "keyword":
                        new.update(flag="limit", kind="keyword")
                    self.profile["categories"][0]["options"].append(new)
                self.write_profile()
                codes = self.codes(self.check())
                self.assertIn("review_missing", codes)
                self.assertIn("sem_metadata_missing", codes)
                if kind == "profile":
                    (self.root / "profiles/new.json").unlink()

    def test_new_fixture_outside_matrix_and_semantic_reference_need_exact_review(self):
        for relative, data in (("tests/fixtures/help/outside.json", {"command": "outside", "text": "Options:\n  --wait N  Wait in seconds\n"}),
                               ("tests/fixtures/value-semantics/extra.json", {"scope": "Synthetic reference only"})):
            with self.subTest(source=relative):
                self.write(relative, data)
                self.assertIn("review_missing", self.codes(self.check()))
        self.reviews = self.reviewed()
        report = self.check()
        self.assertTrue(report["passed"], report["diagnostics"])
        self.assertGreater(report["external_only_logical_entries"], 0)
        self.assertTrue(any(item["code"] == "coverage_external_uncertainty" for item in report["diagnostics"]))

    def test_missing_classification_is_not_promoted_from_metadata(self):
        identity = "option|coverage-specimen|--delay"
        for group in self.reviews["groups"]:
            group["entries"].pop(identity, None)
        self.assertTrue({"review_missing", "coverage_classification_missing"} <= self.codes(self.check()))

    def test_exact_legacy_baseline_is_prospective_and_strict_stays_red(self):
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"]["legacy_baseline"]["entries"] = [self.row()]
        report = self.check()
        self.assertTrue(report["passed"], report["diagnostics"])
        self.assertFalse(report["full_maintained_ready"])
        self.assertEqual(report["diagnostic_counts"]["debt"], 1)
        self.assertIn("sem_metadata_missing", self.codes(self.check("strict")))
        self.profile["categories"][0]["options"].append({"flag": "--new", "argument": "N", "summary": "New value"})
        self.write_profile()
        baseline = deepcopy(self.reviews["coverage_policy"])
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"] = baseline
        report = self.check()
        self.assertIn("sem_metadata_missing", self.codes(report))
        self.assertNotIn("coverage_exception_stale", self.codes(report))  # The old sibling was untouched.
        self.assertIsNone(next(item for item in report["remaining_debt"] if item["id"].endswith("--new"))["deferred_by"])

    def test_relevant_edit_does_not_inherit_debt_even_after_census_refresh(self):
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"]["legacy_baseline"]["entries"] = [self.row()]
        baseline = deepcopy(self.reviews["coverage_policy"])
        self.profile["categories"][0]["options"][0]["summary"] = "Wait in milliseconds"
        self.write_profile()
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"] = baseline
        self.assertTrue({"coverage_exception_stale", "sem_metadata_missing"} <= self.codes(self.check()))

    def test_referenced_definition_change_invalidates_consumer_deferral(self):
        node = claimed_node()
        node["review"]["status"] = "source_derived"
        self.profile["value_definitions"] = {"wait": node}
        self.profile["categories"][0]["options"][0]["value_semantics"] = contract({"ref": "wait"})
        self.write_profile()
        self.reviews = self.reviewed()
        baseline = [self.row()]
        self.profile["value_definitions"]["wait"]["forms"][0]["unit"]["multiplier"] = "0.001"
        self.write_profile()
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"]["legacy_baseline"]["entries"] = baseline
        self.assertIn("coverage_exception_stale", self.codes(self.check()))

    def test_changed_review_decision_invalidates_deferral(self):
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"]["legacy_baseline"]["entries"] = [self.row()]
        next(group for group in self.reviews["groups"] if "option|coverage-specimen|--delay" in group["entries"])["reason"] += " Changed disposition."
        self.assertIn("coverage_exception_stale", self.codes(self.check()))

    def test_same_command_and_flag_in_new_source_cannot_inherit_baseline(self):
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        policy = deepcopy(self.reviews["coverage_policy"])
        policy["legacy_baseline"]["entries"] = [self.row()]
        self.write("profiles/second-observation.json", self.profile)
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"] = policy
        report = self.check()
        self.assertIn("sem_metadata_missing", self.codes(report))
        added = next(item for item in report["remaining_debt"] if item["source"] == "profiles/second-observation.json")
        self.assertIsNone(added["deferred_by"])

    def test_exceptions_are_narrow_actionable_and_never_hide_structure(self):
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        row = {**self.row(), "reason": "The toy meaning requires a separate source investigation.",
               "evidence": "unresolved", "applicability": "Only the controlled toy implementation version 1.",
               "investigation": "Obtain the missing specification for the toy operand.",
               "review_condition": "Invalidate on any relevant value declaration or source change."}
        self.reviews["coverage_policy"]["exceptions"] = [row]
        self.assertTrue(self.check()["passed"])
        mutations = {
            "coverage_exception_broad": {"source": "profiles/*"},
            "coverage_exception_orphan": {"id": "option|missing|--value"},
            "coverage_exception_stale": {"fingerprint": "b" * 64},
            "coverage_exception_requirements": {"codes": ["unsupported_rule"]},
            "coverage_exception_reason": {"reason": "TODO"},
        }
        for code, changes in mutations.items():
            with self.subTest(code=code):
                self.reviews["coverage_policy"]["exceptions"] = [{**row, **changes}]
                report = self.check()
                self.assertIn(code, self.codes(report))
                item = next(d for d in report["diagnostics"] if d["code"] == code)
                self.assertEqual(item["policy_pointer"], "/coverage_policy/exceptions/0")
                self.assertEqual(item["policy_source"], "docs/numerical-inventory/review.json")
                self.assertEqual(item["identity"], changes.get("id", row["id"]))
        self.reviews["coverage_policy"]["exceptions"] = [row, row]
        self.assertIn("coverage_exception_duplicate", self.codes(self.check()))
        self.reviews["coverage_policy"]["exceptions"] = [{k: v for k, v in row.items() if k != "review_condition"}]
        self.assertIn("coverage_exception_invalid", self.codes(self.check()))

    def test_resolved_debt_and_expanded_requirement_cannot_keep_old_baseline(self):
        original = deepcopy(self.profile)
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        self.reviews = self.reviewed()
        row = self.row()
        row["codes"].append("sem_unit_missing")
        self.reviews["coverage_policy"]["legacy_baseline"]["entries"] = [row]
        self.assertIn("coverage_exception_requirements", self.codes(self.check()))
        self.profile = original
        self.write_profile()
        baseline = deepcopy(self.reviews["coverage_policy"])
        self.reviews = self.reviewed()
        self.reviews["coverage_policy"] = baseline
        self.assertIn("coverage_exception_stale", self.codes(self.check()))

    def test_explicit_unresolved_maintained_entry_requires_precise_exception(self):
        node = synthetic_node("unresolved", investigation="Identify the toy implementation's documented value grammar")
        node["review"]["status"] = "unresolved"
        self.profile["categories"][0]["options"][0]["value_semantics"] = contract(node)
        self.write_profile()
        self.reviews = self.reviewed({"option|coverage-specimen|--delay": "unresolved"})
        self.assertIn("sem_unresolved", self.codes(self.check()))
        self.assertNotIn("coverage_classification_missing", self.codes(self.check()))
        row = {**self.row(), "reason": "The toy source lacks the needed implementation-specific grammar.",
               "evidence": "unresolved", "applicability": "Only the controlled toy version and source snapshot.",
               "investigation": "Obtain and review the missing grammar before declaring numerical meaning.",
               "review_condition": "Reassess on changes to the implementation identity or operand declaration."}
        self.reviews["coverage_policy"]["exceptions"] = [row]
        report = self.check()
        self.assertTrue(report["passed"], report["diagnostics"])
        self.assertFalse(report["full_maintained_ready"])

    def test_shared_validator_rejects_missing_ambiguous_contradictory_and_unsupported_forms(self):
        cases = []
        node = claimed_node()
        node["forms"][0].pop("unit")
        cases.append((node, "sem_unit_missing"))
        node = claimed_node()
        node.pop("bare")
        cases.append((node, "sem_bare_missing"))
        node = claimed_node()
        node["forms"][0]["unit"].pop("multiplier")
        cases.append((node, "sem_scale"))
        node = claimed_node()
        node["forms"][0]["notation"] = "magic-suffix"
        cases.append((node, "sem_choice"))
        node = claimed_node()
        node["meaning"] = "time"
        cases.append((node, "sem_meaning_vague"))
        node = claimed_node("count")
        node["subject"] = "number"
        cases.append((node, "sem_meaning_vague"))
        for node, code in cases:
            with self.subTest(code=code):
                self.profile["categories"][0]["options"][0]["value_semantics"] = contract(node)
                self.write_profile()
                self.reviews = self.reviewed()
                self.assertIn(code, self.codes(self.check()))

    def test_structural_failure_is_not_excused_by_matching_completeness_exception(self):
        self.profile["categories"][0]["options"][0]["value_semantics"]["variants"][0]["forms"][0]["unit"]["base"] = "undefined"
        self.write_profile()
        self.reviews = self.reviewed()
        row = {**self.row(), "reason": "Toy data requires investigation of an invalid unit type.", "evidence": "unresolved",
               "applicability": "Only the controlled toy data is affected here.", "investigation": "Replace the unsupported unit using the documented schema.",
               "review_condition": "Reassess after the malformed declaration has been corrected."}
        self.reviews["coverage_policy"]["exceptions"] = [row]
        report = self.check()
        self.assertFalse(report["passed"])
        self.assertTrue(any(d["gate"] == "structural" and d["severity"] == "error" for d in report["diagnostics"]))

    def test_new_positional_components_and_shared_references_are_checked(self):
        host = claimed_node("nonnumerical", meaning="Toy host name", forms=[expression_form("HOST")],
                            bare={"state": "not_applicable", "reason": "Host names are text"})
        index = claimed_node("index", meaning="Toy endpoint index")
        composite = claimed_node("composite", meaning="Toy host and endpoint index", slots=2,
            bare={"state": "not_applicable", "reason": "The components describe token meaning"},
            forms=[expression_form("HOST INDEX")], components=[
                {"id": "host", "slot": 1, "required": True, "semantics": host},
                {"id": "index", "slot": 2, "required": True, "semantics": index}])
        self.profile["positional_group"] = {"argument": "HOST INDEX", "argument_count": 2, "repeatable": True}
        self.profile["positional_value_semantics"] = contract(composite)
        self.write_profile()
        self.assertIn("review_missing", self.codes(self.check()))
        self.reviews = self.reviewed()
        self.assertTrue(self.check()["passed"], self.check()["diagnostics"])
        composite["components"][1]["semantics"].pop("origin")
        self.write_profile()
        self.reviews = self.reviewed()
        self.assertIn("sem_index_origin", self.codes(self.check()))
        self.profile["categories"][0]["options"][0]["value_semantics"] = contract({"ref": "missing"})
        self.write_profile()
        self.assertIn("sem_reference", self.codes(self.check()))

    def test_explicit_aliases_are_validated_and_similar_text_does_not_infer_aliases(self):
        second = deepcopy(self.profile["categories"][0]["options"][0]); second["flag"] = "-d"
        second["value_semantics"]["variants"][0]["forms"][0]["unit"]["multiplier"] = "0.001"
        self.profile["categories"][0]["options"].append(second)
        self.assertEqual(coverage.check_profile(self.profile, "profiles/toy.json"), [])
        self.assertIn("sem_alias_conflict", {d["code"] for d in coverage.check_profile(
            self.profile, "profiles/toy.json", alias_groups=[("--delay", "-d")])})
        second["value_semantics"] = contract({"ref": "absent-definition"})
        self.assertIn("sem_reference", {d["code"] for d in coverage.check_profile(self.profile, "profiles/toy.json")})

    def test_real_units_reach_actual_browser_details_search_and_fake_window(self):
        profile = json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))
        evidence = json.loads((ROOT / "tests/fixtures/value-semantics/migration-evidence.json")
                              .read_text(encoding="utf-8"))["sources"]["rsync"]
        option = next(o for c in profile["categories"] for o in c["options"] if o["flag"] == "--bwlimit=")
        browser = Browser(profile, "--bwlimit")
        view = browser.text(option)
        # Independent reference expectations, not reconstructed formatter output.
        for expected in (evidence["bare_bytes_per_second"] + " bytes/second", "'K'", "'KB'"):
            self.assertIn(expected, " ".join(view.details))
            browser.set_query(expected)
            self.assertIn(option, browser.options())
        self.assertNotIn(evidence["version"], " ".join(view.details))
        browser.set_query(evidence["version"])
        self.assertIn(option, browser.options())
        browser.set_query("--bwlimit")
        screen = FakeScreen(24, 160)
        draw(screen, browser, load_keys(None))
        self.assertIn("1024 bytes/second", screen.text())

    def test_omission_mutations_fail_actual_details_and_search_propagation(self):
        original = coverage.presentation.option_text
        for field in ("details", "searchable"):
            def omit(*args, **kwargs):
                view = original(*args, **kwargs)
                return coverage.presentation.OptionText(view.compact, () if field == "details" else view.details,
                                                       "" if field == "searchable" else view.searchable)
            with self.subTest(field=field), patch.object(coverage.presentation, "option_text", side_effect=omit):
                self.assertIn("coverage_" + ("details_missing" if field == "details" else "search_missing"), self.codes(self.check()))

    def test_heuristic_disagreement_and_valid_counterexamples(self):
        record = next(coverage.profile_records(self.profile, "profiles/specimen.json"))
        self.assertIn("coverage_numerical_placeholder", {d["code"] for d in coverage.heuristic_signals(record, "nonnumerical")})
        for option in ({"flag": "--unit", "argument": "UNIT", "summary": "Select a systemd service"},
                       {"flag": "--port", "argument": "PORT", "summary": "Serial device path"},
                       {"flag": "--volume", "argument": "PATH", "summary": "Mounted filesystem"},
                       {"flag": "--http2", "summary": "HTTP2 protocol"},
                       {"flag": "--id", "argument": "IDENTIFIER", "summary": "Opaque identifier"},
                       {"flag": "--setting", "argument": "KEY=VALUE", "summary": "Delegated configuration"}):
            with self.subTest(option=option["flag"]):
                counterexample = {**record, "option": option, "metadata": None}
                self.assertEqual(coverage.heuristic_signals(counterexample, "nonnumerical"), [])
        self.reviews = self.reviewed({"option|coverage-specimen|--delay": "nonnumerical"})
        report = self.check()
        self.assertTrue(report["passed"])
        self.assertTrue(any(d["code"] == "coverage_classification_disagreement" and d["severity"] == "warning"
                            for d in report["diagnostics"]))

    def test_valid_count_index_level_expression_and_delegated_forms_need_no_invented_unit(self):
        for kind in ("count", "identifier", "index", "level", "enumeration", "timestamp", "duration_expression", "delegated", "nonnumerical"):
            node = claimed_node(kind, meaning="Toy selection of records")
            if kind in {"timestamp", "duration_expression", "delegated", "nonnumerical"}:
                node.update(forms=[expression_form()], bare={"state": "not_applicable", "reason": "The named grammar determines interpretation"})
            if kind == "delegated":
                node["grammar"] = {"name": "Toy settings grammar", "reference": {"source": "synthetic:settings", "locator": "Key-dependent rules"}}
            if kind in {"level", "enumeration"}:
                node["forms"][0]["grammar"] = "Toy modes 1, 2 and 3 select the documented alternatives"
            self.profile["categories"][0]["options"][0]["value_semantics"] = contract(node)
            self.write_profile()
            self.reviews = self.reviewed()
            with self.subTest(kind=kind):
                self.assertTrue(self.check()["passed"], self.check()["diagnostics"])

    def test_external_unresolved_and_malformed_browsing_stays_nonfatal(self):
        profile = deepcopy(self.profile)
        option = profile["categories"][0]["options"][0]
        option["summary"] = "Useful captured wait description"
        node = synthetic_node("unresolved", investigation="Identify the captured version and documented operand units")
        node["review"]["status"] = "unresolved"
        option["value_semantics"] = contract(node)
        for metadata in (option["value_semantics"], {"schema_version": 1, "variants": "malformed"}, None):
            option["value_semantics"] = metadata
            browser = Browser(profile, "Useful captured")
            self.assertIn(option, browser.options())
            self.assertIn("Useful captured", " ".join(browser.text(option).details))
        # A supplied synthetic claim cannot be promoted into production coverage.
        self.profile["categories"][0]["options"][0]["value_semantics"] = contract(synthetic_node())
        self.write_profile()
        self.reviews = self.reviewed()
        self.assertIn("coverage_synthetic_production", self.codes(self.check()))

    def test_determinism_immutability_hostile_snapshot_and_explicit_write_boundary(self):
        marker = self.root / "executed"
        with (self.root / "cli_help/command_paths.py").open("a", encoding="utf-8") as stream:
            stream.write(f"\n__import__('pathlib').Path({str(marker)!r}).write_text('executed')\n")
        self.reviews = self.reviewed()
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        reviews_before = deepcopy(self.reviews)
        first, second = self.check(), self.check()
        self.assertEqual(first, second)
        self.assertEqual(self.reviews, reviews_before)
        self.assertFalse(marker.exists())
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        for forbidden in (self.root / "profiles/specimen.json", self.root / "notes.json"):
            with self.assertRaisesRegex(ValueError, "tests/reports"):
                coverage.write_report(self.root, forbidden, first)
        destination = self.root / "tests/reports/numerical-coverage.json"
        coverage.write_report(self.root, destination, first)
        old = destination.read_bytes()
        coverage.write_report(self.root, destination, second)
        self.assertEqual(old, destination.read_bytes())
        self.write(coverage.inventory.REVIEW_PATH, self.reviews)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(coverage.main(["--root", str(self.root), "--summary"]), 0)
        self.assertTrue(json.loads(output.getvalue())["passed"])
        self.profile["categories"][0]["options"][0].pop("value_semantics")
        self.write_profile()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(coverage.main(["--root", str(self.root)]), 1)

    def test_local_runner_and_ci_use_the_same_nonoptional_gate(self):
        runner = (ROOT / "tests/run.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        command = "python3 -B scripts/check_numerical_coverage.py"
        self.assertIn(command, runner)
        self.assertIn("set -euo pipefail", runner)
        step = workflow.split("- name: Enforce numerical coverage", 1)[1].split("      - name:", 1)[0]
        self.assertIn(command, step)
        self.assertIn("set -euo pipefail", step)
        self.assertNotIn("continue-on-error", step)
        self.assertNotIn("|| true", step)
        self.assertIn("tests/reports/ci/numerical-coverage.json", workflow)


if __name__ == "__main__":
    unittest.main()
