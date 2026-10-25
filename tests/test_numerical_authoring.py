"""Numerical authoring lifecycle checks using fixed data and controlled processes.

Reviewed bundled data supplies declared verified cases. Mutations model authoring
errors and corrections, not new upstream facts. All other cases are synthetic.
"""

from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub

from authoring import NumericalAuthoringError, numerical_review, prepare_profile, validate_authored_profile
from bulk_scan import scan_record
from collection import numerical_findings
from core import find_context, insert_option, load_profiles
from discovery import build_profile
from manual_import import ManualCollection, atomic_json, import_manual
from review import Draft, ReviewSession, edit_draft, preview_profile, review_numerical
from review_forms import FormCancelled, apply_document, edit_options
from test_functional_matrix import BrowserLoop, FakeScreen
from test_value_semantics import contract, synthetic_node
from ui import Browser, load_keys, run_browser


def option(profile):
    return profile["categories"][0]["options"][0]


def driver(profile):
    return {"command": profile["command"][0], "paths": [{"command": profile["command"][1:], "help": [], "man": "-".join(profile["command"])}]}


def draft_for(profile):
    text = json.dumps({"profile": profile, "driver": driver(profile)}, ensure_ascii=False, indent=2) + "\n"
    return Draft(0, text, text, {})


class NumericalAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original = json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))
        selected = next(o for c in original["categories"] for o in c["options"] if o["flag"] == "--bwlimit=")
        cls.profile = {"command": original["command"], "description": original["description"],
                       "categories": [{"name": "Rates", "options": [selected]}]}
        cls.synthetic = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))

    def setUp(self):
        parent = (ROOT / ".cache/numerical-authoring-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if self.root.resolve().parent != parent or self.root.is_symlink():
            raise RuntimeError("Test directory escaped its selected parent")
        self.addCleanup(shutil.rmtree, self.root)
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                       "socket.create_connection", "socket.getaddrinfo", "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Authoring attempted a target, process or network operation")))
        if os.name == "nt":
            original_mkdir = Path.mkdir
            def inherited_mkdir(path, mode=0o777, parents=False, exist_ok=False):
                # Managed Windows hosts cannot reopen mode-0700 test directories.
                # Only this selected test subtree uses inherited permissions.
                selected = path.resolve().is_relative_to(self.root.resolve())
                return original_mkdir(path, mode=0o777 if selected else mode, parents=parents, exist_ok=exist_ok)
            stack.enter_context(patch.object(Path, "mkdir", inherited_mkdir))
        stack.enter_context(patch.dict(os.environ, {"CLI_HELP_DRIVERS": "", "CLI_HELP_CONFIG": ""}))

    def collection(self, profile=None):
        profile = deepcopy(profile or self.profile)
        destination = self.root / "collection"
        with ManualCollection(destination) as collection:
            saved = collection.save_documents(profile, driver(profile))
        report = destination / "scan-report.json"
        atomic_json(report, {"schema_version": 1, "finished": True, "records": [
            {"command": profile["command"], "status": "needs_adjustment", "generated": True}]})
        return saved, report

    def test_valid_metadata_survives_draft_preview_save_reload_and_backup(self):
        saved, report = self.collection()
        before = Path(saved["profile"]).read_bytes()
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            profile = session.validate(draft)["profile"]
            screen = FakeScreen(24, 100, ["\n"])
            with BrowserLoop(screen), patch("curses.wrapper", side_effect=lambda fn, *args: fn(screen, *args), create=True):
                chosen = preview_profile(profile)
            self.assertEqual(chosen["flag"], "--bwlimit=")
            result = session.save(draft)
        restored = load_profiles(Path(result["profile_directory"]))[0]
        self.assertEqual(restored, self.profile)
        review = json.loads(report.read_text(encoding="utf-8"))["records"][0]["review"]
        self.assertEqual((Path(review["backup"]) / "0.json").read_bytes(), before)
        self.assertFalse((report.parent / ".scan.lock").exists())
        self.assertFalse((report.parent / ".import.lock").exists())

    def test_guided_placeholder_edit_quarantines_prior_claim_and_preview_warns(self):
        draft = draft_for(deepcopy(self.profile))
        with patch("builtins.input", side_effect=["e", "1", "", "", "", "LIMIT", "n"]), patch("builtins.print"):
            edit_options(draft)
        profile = draft.document()["profile"]
        self.assertNotIn("value_semantics", option(profile))
        self.assertEqual(option(profile)["argument"], "LIMIT")
        self.assertTrue(profile["documentation"]["alternatives"])
        view = Browser(profile).text(option(profile))
        self.assertIn("Source review", view.compact)
        self.assertIn("requires review", " ".join(view.details))

    def test_lossless_moves_reordering_and_blank_fields_preserve_all_metadata(self):
        profile = deepcopy(self.synthetic)
        draft = draft_for(profile)
        with patch("builtins.input", side_effect=["e", "1", "", "", "", "", "n"]), patch("builtins.print"):
            edit_options(draft)
        retained = draft.document()["profile"]
        self.assertEqual(option(retained)["value_semantics"], option(profile)["value_semantics"])
        self.assertEqual(retained["value_definitions"], profile["value_definitions"])
        self.assertNotIn("documentation", retained)
        moved = draft.document()
        source = moved["profile"]["categories"][0]
        selected = source["options"].pop(0)
        moved["profile"]["categories"].insert(0, {"name": "Moved", "options": [selected]})
        with patch("builtins.print"):
            apply_document(draft, moved)
        self.assertEqual(option(draft.document()["profile"])["value_semantics"], selected["value_semantics"])
        self.assertEqual(draft.document()["profile"]["value_definitions"], profile["value_definitions"])

    def test_raw_identity_argument_style_and_prose_changes_require_review(self):
        mutations = [lambda p: option(p).update(flag="--different="),
                     lambda p: option(p).update(summary="Synthetic edited description"),
                     lambda p: option(p).update(detail="Synthetic edited suffix guidance"),
                     lambda p: option(p).update(argument="LIMIT"),
                     lambda p: option(p).update(argument_optional=True),
                     lambda p: p.update(command=["different-command"]),
                     lambda p: p.update(stop_at_positional=True),
                     lambda p: p.update(description="Changed contextual numerical description")]
        for mutate in mutations:
            old, new = deepcopy(self.profile), deepcopy(self.profile)
            mutate(new)
            result = prepare_profile(old, new)
            self.assertNotIn("value_semantics", option(result))
            self.assertTrue(result["documentation"]["alternatives"])
            validate_authored_profile(result)
            self.assertEqual(old, self.profile)

    def test_arity_removal_attached_and_bundle_changes_deactivate_stale_metadata(self):
        original = deepcopy(self.synthetic)
        for change in ({"argument_count": 2}, {"argument_style": "attached_only"},
                       {"attached": True}, {"bundle": True}, {"argument_optional": True}):
            new = deepcopy(original)
            option(new).update(change)
            result = prepare_profile(original, new)
            self.assertNotIn("value_semantics", option(result))
        new = deepcopy(original)
        option(new).pop("argument")
        result = prepare_profile(original, new)
        self.assertNotIn("value_semantics", option(result))

    def test_deletion_preserves_definitions_and_only_copy_of_reviewed_evidence(self):
        old = deepcopy(self.synthetic)
        new = deepcopy(old)
        new["categories"][0]["options"].pop(0)
        result = prepare_profile(old, new)
        self.assertEqual(result["value_definitions"], old["value_definitions"])
        self.assertEqual(option(result)["flag"], "-d")
        self.assertIn("value_semantics", option(result))
        self.assertEqual(result["documentation"]["alternatives"][0]["metadata"], option(old)["value_semantics"])

    def test_changed_shared_definition_identifies_every_explicit_consumer(self):
        old = deepcopy(self.synthetic)
        report = numerical_review(old)
        self.assertEqual(report["definition_consumers"]["delay"], ["--delay", "-d"])
        new = deepcopy(old)
        new["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "0.001"
        result = prepare_profile(old, new)
        self.assertTrue(all("value_semantics" not in o for o in result["categories"][0]["options"][:2]))
        self.assertEqual(result["value_definitions"], new["value_definitions"])
        self.assertEqual(old, self.synthetic)

    def test_verified_definition_edit_requires_explicit_review_even_when_unused(self):
        old = deepcopy(self.profile)
        node = option(old)["value_semantics"]["variants"][0]
        old["value_definitions"] = {"unused": deepcopy(node)}
        new = deepcopy(old)
        # This is a synthetic lifecycle mutation, not a claim about rsync.
        new["value_definitions"]["unused"]["meaning"] = "Changed meaning awaiting source review"
        with self.assertRaises(NumericalAuthoringError) as rejected:
            prepare_profile(old, new)
        self.assertEqual(rejected.exception.diagnostics[0].code, "authoring_definition_review")
        self.assertIn("unused", rejected.exception.diagnostics[0].pointer)
        self.assertEqual(prepare_profile(old, new, reviewed=True)["value_definitions"], new["value_definitions"])

    def test_changed_verified_library_preview_is_nonfatal_while_save_requires_review(self):
        old = deepcopy(self.profile)
        node = deepcopy(option(old)["value_semantics"]["variants"][0])
        old["value_definitions"] = {"rate": node}
        option(old)["value_semantics"] = {"schema_version": 1, "variants": [{"ref": "rate"}]}
        _, report = self.collection(old)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            current = draft.document()
            current["profile"]["value_definitions"]["rate"]["meaning"] += " (synthetic changed wording)"
            draft.text = json.dumps(current)
            original = draft.text
            preview = session.validate(draft, numerical=False)["profile"]
            self.assertNotIn("value_semantics", option(preview))
            self.assertEqual(draft.text, original)
            with self.assertRaises(NumericalAuthoringError):
                session.save(draft)

    def test_removing_unused_definition_preserves_its_reference_closure(self):
        old = deepcopy(self.synthetic)
        old["value_definitions"]["unused"] = deepcopy(old["value_definitions"]["delay"])
        new = deepcopy(old)
        new["value_definitions"].pop("unused")
        result = prepare_profile(old, new)
        archive = next(item for item in result["documentation"]["alternatives"] if item["option"] == "<definition unused>")
        self.assertEqual(archive["definitions"]["unused"], old["value_definitions"]["unused"])
        self.assertEqual(option(result)["value_semantics"], option(old)["value_semantics"])

    def test_explicit_review_retains_declared_status_and_survives_lossless_moves(self):
        draft = draft_for(deepcopy(self.profile))
        changed = draft.document()
        option(changed["profile"])["summary"] += " (reviewed wording)"
        draft.text = json.dumps(changed)
        with patch("builtins.input", return_value="y"), patch("builtins.print"):
            review_numerical(draft)
        prepared = draft.prepare()
        status = option(prepared["profile"])["value_semantics"]["variants"][0]["review"]["status"]
        self.assertEqual(status, "verified")
        moved = draft.document()
        moved["profile"]["categories"][0]["name"] = "Renamed category"
        moved["profile"]["categories"].append({"name": "Legacy addition", "options": [{"flag": "--quiet", "summary": "Legacy flag"}]})
        draft.text = json.dumps(moved)
        self.assertIn("value_semantics", option(draft.prepare()["profile"]))
        later = draft.document()
        option(later["profile"])["argument"] = "DIFFERENT"
        draft.text = json.dumps(later)
        self.assertNotIn("value_semantics", option(draft.prepare()["profile"]))

    def test_review_never_promotes_source_derived_or_synthetic_status(self):
        draft = draft_for(deepcopy(self.synthetic))
        with patch("builtins.input", return_value="y"), patch("builtins.print"):
            review_numerical(draft)
        self.assertEqual(draft.prepare()["profile"], self.synthetic)
        draft = draft_for(deepcopy(self.profile))
        original = draft.text
        with patch("builtins.input", return_value="n"), patch("builtins.print"):
            review_numerical(draft)
        self.assertIsNone(draft.numerical_baseline)
        self.assertEqual(draft.text, original)

    def test_unverified_metadata_edit_expires_previous_acknowledgement(self):
        profile = deepcopy(self.synthetic)
        node = deepcopy(profile["value_definitions"]["delay"])
        node["review"]["status"] = "source_derived"
        node["investigation"] = "Verify the synthetic source before treating this declaration as established"
        option(profile)["value_semantics"] = contract(node)
        draft = draft_for(profile)
        with patch("builtins.input", return_value="y"), patch("builtins.print"):
            review_numerical(draft)
        current = draft.document()
        option(current["profile"])["value_semantics"]["variants"][0]["meaning"] += " with an unreviewed edit"
        draft.text = json.dumps(current)
        self.assertFalse(draft.numerical_reviewed(current))
        prepared = draft.prepare()["profile"]
        self.assertEqual(option(prepared)["value_semantics"]["variants"][0]["review"]["status"], "source_derived")
        self.assertNotEqual(prepared.get("documentation", {}).get("semantic_sources", {}).get("--delay"), "authored numerical review")

    def test_structural_errors_are_actionable_and_no_completeness_gate_is_activated(self):
        profile = deepcopy(self.profile)
        option(profile)["value_semantics"] = {"schema_version": 99}
        with self.assertRaises(NumericalAuthoringError) as rejected:
            validate_authored_profile(profile, "profiles/example.json")
        diagnostic = rejected.exception.diagnostics[0]
        self.assertEqual(diagnostic.source, "profiles/example.json")
        self.assertEqual(diagnostic.command, ("rsync",))
        self.assertEqual(diagnostic.option, "--bwlimit=")
        legacy = deepcopy(self.profile)
        option(legacy).pop("value_semantics")
        self.assertEqual(validate_authored_profile(legacy), ())

    def test_missing_references_cycles_and_explicit_alias_inconsistency_reject_save(self):
        profile = deepcopy(self.synthetic)
        profile["value_definitions"].pop("delay")
        with self.assertRaises(NumericalAuthoringError):
            validate_authored_profile(profile)
        profile = deepcopy(self.synthetic)
        profile["value_definitions"]["delay"] = {"ref": "delay"}
        with self.assertRaises(NumericalAuthoringError):
            validate_authored_profile(profile)
        profile = deepcopy(self.synthetic)
        profile["categories"][0]["options"][1]["value_semantics"] = contract(synthetic_node("count"))
        with self.assertRaises(NumericalAuthoringError) as rejected:
            validate_authored_profile(profile, alias_groups=[("--delay", "-d")])
        self.assertIn("sem_alias_conflict", {d.code for d in rejected.exception.diagnostics})

    def test_positional_and_composite_changes_retain_original_components_inactively(self):
        for path in sorted((ROOT / "profiles").glob("*.json")):
            old = json.loads(path.read_text(encoding="utf-8"))
            if "positional_value_semantics" not in old:
                continue
            new = deepcopy(old)
            new["positional_group"]["argument_count"] += 1
            result = prepare_profile(old, new)
            self.assertNotIn("positional_value_semantics", result)
            self.assertTrue(any(item["option"] == "<positional_group>" for item in result["documentation"]["alternatives"]))
            owned = deepcopy(old)
            owned["documentation"] = {"semantic_sources": {"<positional_group>": "old source"}}
            removed = deepcopy(owned)
            removed.pop("positional_value_semantics")
            result = prepare_profile(owned, removed)
            self.assertNotIn("<positional_group>", result["documentation"]["semantic_sources"])

    def test_preservation_is_deterministic_nonmutating_and_repeated_preparation_is_stable(self):
        old, new = deepcopy(self.profile), deepcopy(self.profile)
        option(new)["argument"] = "LIMIT"
        before = deepcopy(new)
        first = prepare_profile(old, new)
        second = prepare_profile(old, new)
        self.assertEqual(first, second)
        self.assertEqual(prepare_profile(old, first), first)
        self.assertEqual(new, before)
        self.assertEqual(old, self.profile)

    def test_manual_replacement_retains_profile_provenance_and_unselected_semantics(self):
        saved, _report = self.collection()
        source = self.root / "replacement.txt"
        source.write_text("Options:\n  --bwlimit=RATE  External description with unresolved scale\n  --new COUNT  New count\n", encoding="utf-8")
        import_manual(["rsync"], Path(saved["profile_directory"]).parent, text_file=source, replace=True)
        current = json.loads(Path(saved["profile"]).read_text(encoding="utf-8"))
        self.assertNotIn("value_semantics", option(current))
        self.assertTrue(any(item.get("profile") == self.profile for item in current["documentation"]["sources"]))
        self.assertEqual({o["flag"] for c in current["categories"] for o in c["options"]}, {"--bwlimit=", "--new"})

    def test_bulk_record_uses_fixed_mocked_source_and_shared_save_guard(self):
        destination = self.root / "bulk"
        text = "Options:\n  --wait SECONDS  Wait in seconds; 0 disables the timer\n"
        with ManualCollection(destination) as collection, patch("bulk_scan.read_manual", return_value=(text, "synthetic capture", "tool")) as read:
            result = scan_record({"command": ["tool"], "manual": "tool"}, collection, {}, 2.0, False)
        read.assert_called_once_with(["tool"], "tool", timeout=2.0)
        profile = json.loads(Path(result["profile"]).read_text(encoding="utf-8"))
        self.assertIn("seconds", option(profile)["summary"])
        self.assertNotIn("value_semantics", option(profile))
        self.assertEqual(result["option_count"], 1)

    def test_import_draft_inspect_preview_save_reload_does_not_execute_source_examples(self):
        saved, report = self.collection()
        source = self.root / "capture.txt"
        source.write_text("Options:\n  --wait SECONDS  Wait seconds; use a duration, not milliseconds\n\nSIZE is bytes.\n", encoding="utf-8")
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            session.import_source(draft, "text", str(source), "rsync")
            current = session.validate(draft, numerical=False)["profile"]
            review = numerical_review(current)
            self.assertTrue(review["source_notes"]["sources"])
            browser = Browser(current, "milliseconds")
            self.assertEqual(browser.options()[0]["flag"], "--wait")
            session.save(draft)
        reloaded = load_profiles(Path(saved["profile_directory"]))[0]
        self.assertEqual(reloaded["categories"], current["categories"])

    def test_invalid_raw_draft_and_editor_output_remain_recoverable_without_writes(self):
        saved, report = self.collection()
        before = Path(saved["profile"]).read_bytes()
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            changed = draft.document()
            option(changed["profile"])["value_semantics"] = {"schema_version": 99}
            draft.text = json.dumps(changed)
            invalid_text = draft.text
            with self.assertRaises(NumericalAuthoringError):
                session.save(draft)
            self.assertEqual(draft.text, invalid_text)
            self.assertEqual(Path(saved["profile"]).read_bytes(), before)
            current = session.validate(draft, numerical=False)["profile"]
            self.assertIn("guidance unavailable", Browser(current).text(option(current)).compact)

    def test_read_only_preview_reconciles_a_copy_without_mutating_draft_text(self):
        _, report = self.collection()
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            option(document["profile"])["argument"] = "LIMIT"
            draft.text = json.dumps(document)
            original = draft.text
            preview = session.validate(draft, numerical=False)["profile"]
            self.assertNotIn("value_semantics", option(preview))
            self.assertEqual(draft.text, original)
            self.assertIn("value_semantics", option(draft.document()["profile"]))

    def test_external_editor_invocation_is_literal_mocked_and_invalid_json_is_retained(self):
        draft = draft_for(deepcopy(self.profile))
        selected = self.root / "editor"
        selected.mkdir()
        class SelectedDirectory:
            def __enter__(self):
                return str(selected)
            def __exit__(self, *args):
                return False
        calls = []
        def edited(arguments, **kwargs):
            calls.append((arguments, kwargs))
            Path(arguments[-1]).write_text("{invalid", encoding="utf-8")
            return type("Result", (), {"returncode": 0})()
        with patch("review.tempfile.TemporaryDirectory", return_value=SelectedDirectory()), \
             patch.dict(os.environ, {"VISUAL": "editor --literal", "EDITOR": ""}), patch("review.subprocess.run", side_effect=edited):
            edit_draft(draft)
        self.assertEqual(calls[0][0][:-1], ["editor", "--literal"])
        self.assertEqual(calls[0][1], {"shell": False})
        self.assertEqual(draft.text, "{invalid")
        with self.assertRaises(ValueError):
            draft.document()

    def test_cancelled_guided_edits_preserve_draft_and_review_acknowledgement(self):
        draft = draft_for(deepcopy(self.profile))
        with patch("builtins.input", return_value="y"), patch("builtins.print"):
            review_numerical(draft)
        text, baseline = draft.text, deepcopy(draft.numerical_baseline)
        with patch("builtins.input", side_effect=["e", "1", "/cancel"]), patch("builtins.print"):
            with self.assertRaises(FormCancelled):
                edit_options(draft)
        self.assertEqual(draft.text, text)
        self.assertEqual(draft.numerical_baseline, baseline)

    def test_driver_boundary_edit_affects_selected_profile_without_changing_routes(self):
        draft = draft_for(deepcopy(self.profile))
        document = draft.document()
        document["driver"]["paths"][0]["stop_at_positional"] = True
        with patch("builtins.print"):
            apply_document(draft, document)
        self.assertNotIn("value_semantics", option(draft.document()["profile"]))
        self.assertEqual(draft.document()["driver"], document["driver"])
        unchanged = draft_for(deepcopy(self.profile))
        document = unchanged.document()
        document["driver"]["paths"].append({"command": ["other"], "help": [], "man": "other"})
        with patch("builtins.print"):
            apply_document(unchanged, document)
        self.assertEqual(unchanged.document()["profile"], self.profile)

    def test_collection_reports_structured_errors_and_pending_reviews_without_io(self):
        bad = deepcopy(self.profile)
        option(bad)["value_semantics"] = {"schema_version": 99}
        with patch("builtins.open", side_effect=AssertionError("Unexpected I/O")):
            findings = numerical_findings(bad, "profiles/test.json")
        self.assertTrue(any(item["severity"] == "error" for item in findings))
        self.assertEqual(findings[0]["diagnostic"]["command"], ["rsync"])
        changed = deepcopy(self.profile)
        option(changed)["argument"] = "LIMIT"
        stale = prepare_profile(self.profile, changed)
        self.assertIn("authoring_semantics_review", {item["code"] for item in numerical_findings(stale, "profiles/test.json")})
        legacy = deepcopy(self.profile)
        option(legacy).pop("value_semantics")
        self.assertEqual(numerical_findings(legacy, "profiles/test.json"), [])

    def test_concurrent_change_and_failed_save_retain_original_numerical_evidence(self):
        saved, report = self.collection()
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            Path(saved["profile"]).write_text(json.dumps(self.profile) + " ", encoding="utf-8")
            before = Path(saved["profile"]).read_bytes()
            with self.assertRaisesRegex(ValueError, "outside this review"):
                session.save(draft)
            self.assertEqual(Path(saved["profile"]).read_bytes(), before)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            with patch.object(session.collection, "save_documents", side_effect=OSError("synthetic write failure")):
                with self.assertRaisesRegex(ValueError, "Save incomplete"):
                    session.save(draft)
            self.assertTrue(session.save_failed)
            self.assertTrue(any((report.parent / ".review-backups").glob("*/manifest.json")))

    def test_representative_meanings_and_uncertainty_survive_lossless_serialization(self):
        for path in sorted((ROOT / "profiles").glob("*.json")):
            profile = json.loads(path.read_text(encoding="utf-8"))
            new = deepcopy(profile)
            new["categories"].reverse()
            for category in new["categories"]:
                category["options"].reverse()
            self.assertEqual(prepare_profile(profile, new), new)
            validate_authored_profile(new)
            self.assertEqual(json.loads(json.dumps(new)), new)

    def test_authoring_preparation_requires_no_file_network_process_or_evaluation_access(self):
        original, current = deepcopy(self.profile), deepcopy(self.profile)
        option(current)["argument"] = "LIMIT"
        with ExitStack() as stack:
            for name in ("builtins.open", "builtins.eval", "builtins.exec", "pathlib.Path.open", "pathlib.Path.write_text"):
                stack.enter_context(patch(name, side_effect=AssertionError("Unexpected authoring side effect")))
            prepared = prepare_profile(original, current)
            validate_authored_profile(prepared)
            numerical_review(prepared)
        self.assertNotIn("value_semantics", option(prepared))
        self.assertEqual(original, self.profile)

    def test_reviewed_correction_saves_and_reloads_without_inherited_source_ownership(self):
        profile = deepcopy(self.profile)
        profile["documentation"] = {"semantic_sources": {"--bwlimit": "original capture"}}
        saved, report = self.collection(profile)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            current = draft.document()
            option(current["profile"])["summary"] += " (reviewed presentation wording)"
            draft.text = json.dumps(current)
            with patch("builtins.input", return_value="y"), patch("builtins.print"):
                review_numerical(draft)
            session.save(draft)
        result = json.loads(Path(saved["profile"]).read_text(encoding="utf-8"))
        self.assertIn("value_semantics", option(result))
        self.assertEqual(result["documentation"]["semantic_sources"]["--bwlimit"], "authored numerical review")
        self.assertTrue(any(item.get("semantic_source") == "original capture" for item in result["documentation"]["sources"]))
        self.assertFalse(any(item.get("code") == "authoring_semantics_review" for item in result["documentation"]["diagnostics"]))

    def test_reactivating_inactive_verified_claim_requires_new_explicit_review(self):
        changed = deepcopy(self.profile)
        option(changed)["argument"] = "LIMIT"
        inactive = prepare_profile(self.profile, changed)
        candidate = deepcopy(inactive)
        option(candidate)["value_semantics"] = deepcopy(option(self.profile)["value_semantics"])
        self.assertNotIn("value_semantics", option(prepare_profile(inactive, candidate)))
        corrected = prepare_profile(inactive, candidate, reviewed=True)
        self.assertIn("value_semantics", option(corrected))
        self.assertFalse(corrected["documentation"]["alternatives"])
        self.assertTrue(corrected["documentation"]["sources"])

    def test_collection_uncertainty_is_warning_only_for_explicit_metadata(self):
        profile = deepcopy(self.synthetic)
        findings = numerical_findings(profile, "profiles/synthetic.json")
        self.assertFalse(any(item["severity"] == "error" for item in findings))
        unverified = deepcopy(profile)
        node = unverified["value_definitions"]["delay"]
        node["review"]["status"] = "source_derived"
        node["investigation"] = "Verify the source version before treating the scale as established"
        findings = numerical_findings(unverified, "profiles/synthetic.json")
        self.assertIn("sem_review_required", {item["code"] for item in findings})
        self.assertTrue(all(item["severity"] == "warning" for item in findings))
        validate_authored_profile(unverified)

    def test_explicitly_edited_bad_arity_is_rejected_without_hiding_the_error(self):
        saved, report = self.collection(self.synthetic)
        with ReviewSession(report) as session:
            draft = session.open_draft(0)
            document = draft.document()
            selected = option(document["profile"])
            selected["argument_count"] = 2
            # Synthetic composite has three slots but the declaration has two.
            component = synthetic_node("count")
            selected["value_semantics"] = contract(synthetic_node("composite", slots=3,
                bare={"state": "not_applicable", "reason": "Composite grammar"},
                forms=[{"id": "joined", "notation": "expression", "syntax": "A B C", "grammar": "Three token slots"}],
                components=[{"id": f"part{i}", "slot": i, "required": True, "semantics": component} for i in (1, 2, 3)]))
            draft.text = json.dumps(document)
            before = Path(saved["profile"]).read_bytes()
            with self.assertRaises(NumericalAuthoringError) as rejected:
                session.save(draft)
            self.assertIn("sem_arity_conflict", {d.code for d in rejected.exception.diagnostics})
            self.assertEqual(Path(saved["profile"]).read_bytes(), before)

    def test_semantic_owner_changes_require_review_without_affecting_other_entries(self):
        old = deepcopy(self.profile)
        old["documentation"] = {"semantic_sources": {"--bwlimit": "first capture"}}
        new = deepcopy(old)
        new["documentation"]["semantic_sources"]["--bwlimit"] = "different capture"
        result = prepare_profile(old, new)
        self.assertNotIn("value_semantics", option(result))
        self.assertTrue(any(item["semantic_source"] == "first capture" for item in result["documentation"]["alternatives"]))

    def test_direct_collection_boundary_edit_cannot_retain_stale_verified_metadata(self):
        saved, _ = self.collection()
        with ManualCollection(Path(saved["profile_directory"]).parent) as collection:
            changed = driver(self.profile)
            changed["paths"][0]["stop_at_positional"] = True
            collection.save_documents(deepcopy(self.profile), changed, replace=True)
        current = json.loads(Path(saved["profile"]).read_text(encoding="utf-8"))
        self.assertNotIn("value_semantics", option(current))


if __name__ == "__main__":
    unittest.main()
