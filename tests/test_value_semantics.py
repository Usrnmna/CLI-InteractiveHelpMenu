"""Protect opt-in descriptive contracts without asserting upstream CLI facts."""

from copy import deepcopy
import builtins
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import find_context, insert_option, load_profiles, validate_profile
from value_semantics import (
    ValueContext, ValueSemanticsError, format_value_semantics,
    validate_profile_semantics, validate_value_semantics,
)


def synthetic_node(kind="quantity", **changes):
    """Construct a fully labeled synthetic case, never verified target metadata."""
    node = {
        "kind": kind, "meaning": "Synthetic transfer buffer size",
        "review": {"status": "synthetic", "references": [
            {"source": "synthetic:unit-tests", "locator": "explicit test declaration"}]},
        "applicability": {
            "implementation": {"state": "known", "values": ["synthetic-contract"]},
            "version": {"state": "known", "min": "1", "before": "2"},
            "platform": {"state": "any"},
            "chip": {"state": "not_applicable", "reason": "No hardware is involved"}},
        "bare": {"state": "accepted", "form": "plain"},
        "forms": [{"id": "plain", "notation": "number", "syntax": "N"}],
        "when_absent": {"state": "known", "meaning": "Automatic synthetic selection"},
        "when_value_omitted": {"state": "not_accepted", "reason": "The flag requires an operand"},
    }
    if kind in {"quantity", "duration"}:
        node["forms"][0]["unit"] = {"base": "second" if kind == "duration" else "byte", "multiplier": "1"}
    if kind in {"count", "index", "identifier"}:
        node["subject"] = "Selected synthetic records"
    if kind == "index":
        node["origin"] = "0"
    if kind == "level":
        node["ordering"] = "Larger values select more detail"
    if kind in {"timestamp", "duration_expression"}:
        node["time_basis"] = "UTC with an explicit timezone; relative expressions use the documented reference instant"
    node.update(changes)
    return node


def contract(*nodes):
    return {"schema_version": 1, "variants": list(nodes or [synthetic_node()])}


def expression_form(syntax="EXPR", grammar="Synthetic grammar defined in this fixture"):
    return {"id": "expression", "notation": "expression", "syntax": syntax, "grammar": grammar}


class ValueSemanticsTests(unittest.TestCase):
    def assert_valid(self, metadata, **kwargs):
        self.assertEqual(validate_value_semantics(metadata, mode="maintained", **kwargs), ())

    def codes(self, metadata, mode="maintained", **kwargs):
        return {d.code for d in validate_value_semantics(metadata, mode=mode, **kwargs)}

    def test_synthetic_fixture_shared_definitions_and_explicit_aliases(self):
        path = ROOT / "tests/fixtures/value-semantics/synthetic-profile.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        validate_profile(profile, path)
        self.assertEqual(validate_profile_semantics(profile, path, mode="maintained",
                                                    alias_groups=[("--delay", "-d")]), ())
        option = profile["categories"][0]["options"][0]
        lines = format_value_semantics(option["value_semantics"], definitions=profile["value_definitions"])
        self.assertIn("bare numbers: seconds", lines[0])
        self.assertTrue(any("0.001 seconds" in line and "'ms'" in line for line in lines))
        self.assertTrue(any("Unlimited wait" in line for line in lines))

    def test_time_rate_and_size_scales_remain_distinct(self):
        for base, factor, per in (("second", "1", None), ("second", "0.001", None),
                                  ("bit", "1000", "second"), ("byte", "1024", "second"),
                                  ("byte", "1000000", None), ("byte", "1048576", None)):
            with self.subTest(base=base, factor=factor, per=per):
                node = synthetic_node()
                unit = {"base": base, "multiplier": factor}
                if per:
                    unit["per"] = per
                node["forms"][0]["unit"] = unit
                self.assert_valid(contract(node))
                lines = format_value_semantics(contract(node))
                if factor != "1":
                    self.assertIn(factor, lines[0])
                self.assertIn({"second": "seconds", "bit": "bits", "byte": "bytes"}[base], lines[0])

    def test_literal_token_does_not_imply_conventional_scale(self):
        node = synthetic_node(bare={"state": "not_accepted", "reason": "A literal token is required"}, forms=[{
            "id": "flash", "notation": "literal", "syntax": "4MB", "tokens": ["4MB"],
            "case": "sensitive", "meaning": "Exactly four binary mebibytes in this synthetic protocol",
            "unit": {"base": "byte", "multiplier": "4194304"}}])
        self.assert_valid(contract(node))
        text = "\n".join(format_value_semantics(contract(node)))
        self.assertIn("'4MB'", text)
        self.assertIn("4194304 bytes", text)
        self.assertNotIn("4000000", text)

    def test_explicit_units_with_a_literal_zero_exception(self):
        node = synthetic_node("duration", bare={"state": "not_accepted", "reason": "Ordinary values need a unit"}, forms=[{
            "id": "seconds", "notation": "suffix", "syntax": "Ns", "tokens": ["s"], "case": "sensitive",
            "unit": {"base": "second", "multiplier": "1"}}, {
            "id": "disabled", "notation": "literal", "syntax": "0", "tokens": ["0"],
            "case": "sensitive", "sentinel": True, "meaning": "Disable the synthetic timeout"}])
        self.assert_valid(contract(node))
        self.assertIn("ordinary bare numbers not accepted", format_value_semantics(contract(node))[0])
        node["bare"] = {"state": "accepted", "form": "seconds"}
        self.assertIn("sem_bare_conflict", self.codes(contract(node)))

    def test_counts_identifiers_and_indices_need_no_physical_unit(self):
        for kind in ("count", "identifier", "index"):
            node = synthetic_node(kind, meaning="Select synthetic records")
            self.assert_valid(contract(node))
            self.assertNotIn("unit/scale", "\n".join(format_value_semantics(contract(node))))
        node = synthetic_node("index")
        del node["origin"]
        self.assertIn("sem_index_origin", self.codes(contract(node)))
        node = synthetic_node("count")
        del node["subject"]
        self.assertIn("sem_incomplete", self.codes(contract(node)))

    def test_levels_enumerations_and_numeric_fixed_flags(self):
        forms = [{"id": "low", "notation": "literal", "syntax": "0 or quiet", "tokens": ["0", "quiet"],
                  "case": "insensitive", "meaning": "Minimum synthetic detail"},
                 {"id": "high", "notation": "literal", "syntax": "2 or verbose", "tokens": ["2", "verbose"],
                  "case": "insensitive", "meaning": "Maximum synthetic detail"}]
        for kind in ("level", "enumeration"):
            self.assert_valid(contract(synthetic_node(kind, forms=forms,
                bare={"state": "not_accepted", "reason": "Only listed literal choices are accepted"})))
        node = synthetic_node("level", forms=[{**forms[1], "syntax": "-2", "tokens": ["-2"]}],
            bare={"state": "not_applicable", "reason": "The complete flag selects a fixed level"},
            when_value_omitted={"state": "not_applicable", "reason": "This fixed flag has no operand"})
        self.assert_valid(contract(node), context=ValueContext(argument_count=0, value_optional=False))

    def test_percentages_mixed_forms_and_custom_measurements(self):
        node = synthetic_node("count", meaning="Synthetic display height", subject="Terminal rows")
        node["forms"].append({"id": "percent", "notation": "suffix", "syntax": "N%", "tokens": ["%"],
            "case": "sensitive", "unit": {"base": "ratio", "multiplier": "0.01", "relative_to": "available terminal rows"},
            "bounds": {"min": "0", "max": "100"}})
        self.assert_valid(contract(node))
        text = "\n".join(format_value_semantics(contract(node)))
        self.assertIn("0.01 of available terminal rows", text)
        self.assertIn("[0, 100]", text)
        node["forms"][1]["unit"].pop("relative_to")
        self.assertIn("sem_incomplete", self.codes(contract(node)))
        custom = synthetic_node()
        custom["forms"][0]["unit"] = {"base": "custom", "name": "synthetic display cells", "multiplier": "1",
            "definition": "Width computed by the synthetic reference table, not bytes or code points"}
        self.assert_valid(contract(custom))
        self.assertIn("reference table", "\n".join(format_value_semantics(contract(custom))))

    def test_timestamp_duration_expression_and_delegated_grammar(self):
        for kind in ("timestamp", "duration_expression", "delegated", "nonnumerical"):
            node = synthetic_node(kind, forms=[expression_form()],
                bare={"state": "not_applicable", "reason": "The documented grammar determines value meaning"})
            if kind == "delegated":
                node["grammar"] = {"name": "Synthetic key=value grammar", "reference": {
                    "source": "synthetic:settings", "locator": "key-dependent units"}}
            self.assert_valid(contract(node))
        node = synthetic_node("timestamp", forms=[expression_form()])
        del node["time_basis"]
        self.assertIn("sem_incomplete", self.codes(contract(node)))
        self.assertIn("sem_grammar_missing", self.codes(contract(synthetic_node("delegated"))))

    def composite(self, slots=1):
        """Joined HOST:INDEX components occupy one token; ADDRESS FILE uses two."""
        host = synthetic_node("nonnumerical", meaning="Synthetic host name", forms=[expression_form("HOST")],
            bare={"state": "not_applicable", "reason": "A host name is text"})
        index = synthetic_node("index", meaning="Synthetic endpoint index", subject="Endpoint index")
        return synthetic_node("composite", meaning="HOST:INDEX joins two components in one token" if slots == 1 else "ADDRESS FILE has two token slots",
            bare={"state": "not_applicable", "reason": "Components define the grammar"}, forms=[expression_form("HOST:INDEX" if slots == 1 else "ADDRESS FILE")],
            slots=slots, components=[
                {"id": "host", "slot": 1, "required": True, "semantics": host},
                {"id": "index", "slot": slots, "required": True, "semantics": index}])

    def test_composites_map_components_to_existing_arity(self):
        for slots in (1, 2):
            node = self.composite(slots)
            ctx = ValueContext(argument_count=slots)
            self.assert_valid(contract(node), context=ctx)
            self.assertTrue(any("Component index" in line for line in format_value_semantics(contract(node), context=ctx)))
        self.assertIn("sem_arity_conflict", self.codes(contract(self.composite(2)), context=ValueContext(argument_count=1)))
        node = self.composite(2)
        node["components"][1]["slot"] = 1
        self.assertIn("sem_component_slots", self.codes(contract(node)))
        node["components"][1]["slot"] = 9
        self.assertIn("sem_component_slots", self.codes(contract(node)))
        node["components"][1]["id"] = "host"
        self.assertIn("sem_duplicate", self.codes(contract(node)))

    def test_zero_negative_defaults_unlimited_and_omission_are_distinct(self):
        node = synthetic_node("count", subject="Synthetic records")
        form = node["forms"][0]
        form["bounds"] = {"min": "1", "max": "8"}
        form["special_values"] = [{"value": "0", "meaning": "Unlimited records"},
                                  {"value": "-1", "meaning": "Automatic selection"}]
        node["when_absent"] = {"state": "known", "form": "plain", "value": "0"}
        node["when_value_omitted"] = {"state": "known", "form": "plain", "value": "-1"}
        self.assert_valid(contract(node), context=ValueContext(argument_count=1, value_optional=True))
        text = "\n".join(format_value_semantics(contract(node)))
        self.assertIn("Option absent: Unlimited records (input N; magnitude 0)", text)
        self.assertIn("Operand omitted: Automatic selection (input N; magnitude -1)", text)
        self.assertIn("sem_arity_conflict", self.codes(contract(node), context=ValueContext(argument_count=1, value_optional=False)))
        node["when_absent"]["value"] = "9"
        self.assertIn("sem_default_conflict", self.codes(contract(node)))
        form["special_values"].append({"value": "0.0", "meaning": "Contradictory interpretation"})
        self.assertIn("sem_special_conflict", self.codes(contract(node)))

    def test_modes_separate_structure_completeness_and_external_uncertainty(self):
        self.assertEqual(validate_value_semantics(None), ())
        self.assertIn("sem_metadata_missing", self.codes(None))
        external = validate_value_semantics(None, mode="external")
        self.assertEqual({d.severity for d in external}, {"warning"})
        node = synthetic_node()
        del node["forms"][0]["unit"]
        del node["meaning"]
        self.assertEqual(validate_value_semantics(contract(node)), ())
        self.assertTrue({"sem_unit_missing", "sem_incomplete"} <= self.codes(contract(node)))
        self.assertEqual({d.severity for d in validate_value_semantics(contract(node), mode="external")}, {"warning"})
        unresolved = synthetic_node("unresolved", meaning="External value requires investigation",
            forms=[expression_form()], investigation="Verify default magnitude in the applicable release manual",
            bare={"state": "unverified", "reason": "The captured help omits the unit"})
        unresolved["review"]["status"] = "unresolved"
        self.assertEqual(validate_value_semantics(contract(unresolved)), ())
        self.assertIn("sem_unresolved", self.codes(contract(unresolved), mode="external"))
        self.assertTrue(all(d.severity == "warning" for d in validate_value_semantics(contract(unresolved), mode="external")))
        self.assertIn("unresolved", format_value_semantics(contract(unresolved))[0])
        unresolved["review"]["status"] = "verified"
        unresolved["review"]["references"][0]["source"] = "https://example.invalid/reference"
        self.assertIn("sem_false_verification", self.codes(contract(unresolved), mode="structural"))

    def test_applicability_variants_overlap_and_version_boundaries(self):
        first, second = synthetic_node(), synthetic_node()
        second["forms"][0]["unit"]["multiplier"] = "1024"
        second["applicability"]["version"] = {"state": "known", "min": "2", "before": "3"}
        self.assert_valid(contract(first, second))
        self.assertTrue(any("version: >= 2; < 3" in line for line in format_value_semantics(contract(first, second))))
        second["applicability"]["version"]["min"] = "1.5"
        self.assertIn("sem_variant_conflict", self.codes(contract(first, second)))
        second["applicability"]["version"] = {"state": "known", "values": ["2.0"]}
        self.assert_valid(contract(first, second))
        second["applicability"]["version"]["values"] = ["1.0.0"]
        self.assertIn("sem_variant_conflict", self.codes(contract(first, second)))
        second["applicability"]["platform"] = {"state": "known", "values": ["platform-b"]}
        first["applicability"]["platform"] = {"state": "known", "values": ["platform-a"]}
        self.assert_valid(contract(first, second))
        second["applicability"]["platform"] = {"state": "any"}
        second["applicability"]["version"] = {"state": "unverified", "reason": "Legacy behavior needs verification"}
        self.assertIn("sem_variant_conflict", self.codes(contract(first, second), mode="structural"))

    def test_explicit_aliases_and_shared_references_cannot_conflict(self):
        node = synthetic_node()
        profile = {"command": ["synthetic"], "description": "Synthetic profile", "value_definitions": {"buffer": node},
            "categories": [{"name": "Options", "options": [
                {"flag": "--size", "argument": "N", "summary": "Same summary", "value_semantics": contract({"ref": "buffer"})},
                {"flag": "-s", "argument": "N", "summary": "Same summary", "value_semantics": contract(deepcopy(node))}]}]}
        self.assertEqual(validate_profile_semantics(profile, mode="maintained", alias_groups=[("--size", "-s")]), ())
        profile["categories"][0]["options"][1]["value_semantics"]["variants"][0]["forms"][0]["unit"]["multiplier"] = "1024"
        self.assertEqual(validate_profile_semantics(profile, mode="maintained"), ())  # No inferred alias relationship.
        self.assertIn("sem_alias_conflict", {d.code for d in validate_profile_semantics(profile, mode="maintained", alias_groups=[("--size", "-s")])})
        self.assertIn("sem_reference_override", self.codes(contract({"ref": "buffer", "meaning": "Override"}), definitions={"buffer": node}))
        self.assertIn("sem_reference", self.codes(contract({"ref": "missing"})))
        self.assertIn("sem_reference_cycle", self.codes(contract({"ref": "a"}), definitions={"a": {"ref": "b"}, "b": {"ref": "a"}}))

    def test_actionable_diagnostics_have_stable_order_and_locations(self):
        node = synthetic_node()
        node["forms"][0]["unit"] = {"base": "speed", "multiplier": "many"}
        ctx = ValueContext(source="fixtures/example.json", command=("synthetic", "child"), option="--rate",
                           pointer="/categories/0/options/1/value_semantics")
        a = validate_value_semantics(contract(node), context=ctx)
        b = validate_value_semantics(json.loads(json.dumps(contract(node), sort_keys=True)), context=ctx)
        self.assertEqual(a, b)
        self.assertTrue({"sem_choice", "sem_scale"} <= {d.code for d in a})
        for d in a:
            self.assertEqual(d.source, "fixtures/example.json")
            self.assertEqual(d.command, ("synthetic", "child"))
            self.assertEqual(d.option, "--rate")
            self.assertTrue(d.pointer.startswith(ctx.pointer))
            self.assertTrue(d.message)
            self.assertIsInstance(json.dumps(d.to_dict()), str)
        composite = self.composite()
        composite["components"][1]["semantics"].pop("origin")
        diagnostics = validate_value_semantics(contract(composite), mode="maintained", context=ctx)
        self.assertTrue(any(d.component == ("index",) and d.code == "sem_index_origin" for d in diagnostics))

    def test_legacy_loading_is_unchanged_and_opt_in_completeness_is_separate(self):
        profiles = load_profiles(ROOT / "profiles")
        for profile in profiles:
            with self.subTest(command=profile["command"]):
                self.assertEqual(validate_profile_semantics(profile), ())
        self.assertTrue(any(d.code == "sem_metadata_missing" for profile in profiles
                            for d in validate_profile_semantics(profile, mode="maintained")))
        synthetic = deepcopy(profiles[0])
        synthetic["categories"][0]["options"][0]["value_semantics"] = {"schema_version": "invalid"}
        validate_profile(synthetic, Path("synthetic.json"))  # Legacy validation does not opt in.
        self.assertTrue(validate_profile_semantics(synthetic))

    def test_positional_contract_is_additive_and_preserves_literal_editing(self):
        path = ROOT / "tests/fixtures/value-semantics/synthetic-profile.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        profile["positional_group"] = {"argument": "ADDRESS FILE", "argument_count": 2, "repeatable": True}
        profile["positional_value_semantics"] = contract(self.composite(2))
        validate_profile(profile, path)
        self.assertEqual(validate_profile_semantics(profile, mode="maintained"), ())
        original = deepcopy(profile)
        legacy = deepcopy(profile)
        legacy.pop("positional_value_semantics")
        legacy.pop("value_definitions")
        for option in legacy["categories"][0]["options"]:
            option.pop("value_semantics", None)
        line = "synthetic-contract   --d  tail"
        point = len("synthetic-contract   --d")
        def edit(p):
            context = find_context(line, point, [p], driver_registry={})
            return insert_option(context, p["categories"][0]["options"][0])
        self.assertEqual(edit(profile), edit(legacy))
        self.assertEqual(edit(profile), ("synthetic-contract   --delay  tail", len("synthetic-contract   --delay ")))
        self.assertEqual(profile, original)
        profile["positional_value_semantics"]["variants"][0]["slots"] = 1
        self.assertIn("sem_arity_conflict", {d.code for d in validate_profile_semantics(profile)})

    def test_partial_and_malformed_json_fields_never_cause_secondary_exceptions(self):
        path = ROOT / "tests/fixtures/value-semantics/synthetic-profile.json"
        specimen = json.loads(path.read_text(encoding="utf-8"))["value_definitions"]["delay"]
        samples = [specimen, synthetic_node("index"), self.composite()]
        def paths(value, prefix=()):
            if isinstance(value, dict):
                for key, item in value.items():
                    yield prefix + (key,)
                    yield from paths(item, prefix + (key,))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    yield prefix + (index,)
                    yield from paths(item, prefix + (index,))
        for sample in samples:
            for location in paths(sample):
                for bad in (None, True, 3, [], {}, ""):
                    node = deepcopy(sample)
                    target = node
                    for part in location[:-1]:
                        target = target[part]
                    target[location[-1]] = bad
                    with self.subTest(location=location, bad=bad):
                        diagnostics = validate_value_semantics(contract(node))
                        if not any(d.severity == "error" for d in diagnostics):
                            self.assertIsInstance(format_value_semantics(contract(node)), tuple)

    def test_unverified_states_and_false_review_claims_remain_explicit(self):
        node = synthetic_node()
        node["forms"][0]["unit"] = {"state": "unverified", "reason": "The source omits the scale"}
        node["applicability"]["chip"] = {"state": "unverified", "reason": "Chip variants require investigation"}
        external = validate_value_semantics(contract(node), mode="external")
        self.assertTrue(external)
        self.assertTrue(all(d.severity == "warning" for d in external))
        text = "\n".join(format_value_semantics(contract(node)))
        self.assertIn("unit/scale not verified", text)
        self.assertIn("Chip variants require investigation", text)
        node["review"] = {"status": "verified", "references": [
            {"source": "https://example.invalid/synthetic-placeholder", "locator": "not fetched"}]}
        self.assertIn("sem_false_verification", self.codes(contract(node), mode="structural"))
        node = synthetic_node()
        node["review"]["status"] = "verified"
        self.assertIn("sem_false_verification", self.codes(contract(node), mode="structural"))
        node["review"]["references"][0]["source"] = "https://example.invalid/not-fetched"
        node["forms"][0].pop("unit")
        self.assertIn("sem_false_verification", self.codes(contract(node), mode="structural"))

    def test_quantity_literals_require_units_or_explicit_sentinel_status(self):
        node = synthetic_node(bare={"state": "not_accepted", "reason": "Only listed values are accepted"}, forms=[{
            "id": "auto", "notation": "literal", "syntax": "auto", "tokens": ["auto"],
            "case": "sensitive", "meaning": "Automatic buffer size"}])
        self.assertIn("sem_unit_missing", self.codes(contract(node)))
        node["forms"][0]["sentinel"] = True
        self.assert_valid(contract(node))
        node["forms"][0]["unit"] = {"base": "byte", "multiplier": "1"}
        self.assertIn("sem_unit_conflict", self.codes(contract(node)))
        node["forms"] = [expression_form()]
        self.assertIn("sem_unit_missing", self.codes(contract(node)))

    def test_mapping_key_order_does_not_change_explanations(self):
        metadata = contract(self.composite())
        reordered = json.loads(json.dumps(metadata, sort_keys=True))
        self.assertEqual(format_value_semantics(metadata), format_value_semantics(reordered))
        node = synthetic_node("level")
        self.assertIn("sem_incomplete", self.codes(contract(node)))
        node["forms"][0]["grammar"] = "Integer levels 0 through 3, increasingly detailed"
        node["forms"][0]["bounds"] = {"min": "0", "max": "3"}
        self.assert_valid(contract(node))

    def test_prefixes_describe_input_notation_without_parsing_operands(self):
        node = synthetic_node("index", meaning="Synthetic address slot", subject="Address slots",
            bare={"state": "not_accepted", "reason": "A hexadecimal prefix is required"}, forms=[{
                "id": "hex", "notation": "prefix", "syntax": "0xHEX", "tokens": ["0x"], "case": "sensitive",
                "grammar": "Unsigned hexadecimal digits after the prefix; metadata bounds use mathematical magnitudes",
                "bounds": {"min": "0", "max": "255"}}])
        self.assert_valid(contract(node))
        text = "\n".join(format_value_semantics(contract(node)))
        self.assertIn("literal prefix tokens '0x'", text)
        self.assertIn("hexadecimal digits", text)

    def test_implementation_chip_and_opaque_release_scope_conflicts(self):
        first, second = synthetic_node(), synthetic_node()
        second["forms"][0]["unit"]["multiplier"] = "1024"
        second["applicability"]["implementation"]["values"] = ["different-synthetic-implementation"]
        self.assert_valid(contract(first, second))
        second["applicability"]["implementation"] = deepcopy(first["applicability"]["implementation"])
        first["applicability"]["chip"] = {"state": "known", "values": ["chip-a"]}
        second["applicability"]["chip"] = {"state": "known", "values": ["chip-b"]}
        self.assert_valid(contract(first, second))
        first["applicability"]["chip"] = {"state": "not_applicable", "reason": "Unknown relationship to chip families"}
        self.assertIn("sem_variant_conflict", self.codes(contract(first, second)))
        second["applicability"]["version"] = {"state": "known", "values": ["release-candidate"]}
        self.assertIn("sem_variant_conflict", self.codes(contract(first, second)))
        first["applicability"]["version"] = {"state": "known", "values": ["stable-release"]}
        self.assert_valid(contract(first, second))

    def test_alias_variant_order_and_nested_applicability_are_handled(self):
        first = synthetic_node()
        second = deepcopy(first)
        second["applicability"]["version"] = {"state": "known", "min": "2", "before": "3"}
        profile = {"command": ["synthetic"], "categories": [{"options": [
            {"flag": "--one", "argument": "N", "value_semantics": contract(first, second)},
            {"flag": "--two", "argument": "N", "value_semantics": contract(second, first)}]}]}
        self.assertEqual(validate_profile_semantics(profile, mode="maintained", alias_groups=[("--one", "--two")]), ())
        self.assertIn("sem_alias_group", {d.code for d in validate_profile_semantics(profile, alias_groups=[("--one", "--missing")])})
        a, b = self.composite(), self.composite()
        b["components"][0]["semantics"]["applicability"]["platform"] = {"state": "known", "values": ["only-one-platform"]}
        self.assertIn("sem_variant_conflict", self.codes(contract(a, b)))

    def test_formatter_handles_explicit_partial_drafts_and_rejects_bad_scales(self):
        partial = contract({"kind": "quantity"})
        self.assertEqual(validate_value_semantics(partial), ())
        text = "\n".join(format_value_semantics(partial))
        self.assertIn("meaning not documented", text)
        self.assertIn("bare-number meaning not verified", text)
        self.assertIn("Accepted forms: not documented", text)
        for factor in ("NaN", "Infinity", "1e3", "-1", "0", 1, True):
            node = synthetic_node()
            node["forms"][0]["unit"]["multiplier"] = factor
            with self.subTest(factor=factor):
                self.assertIn("sem_scale", self.codes(contract(node), mode="structural"))

    def test_optional_operand_and_fixed_flag_omission_cannot_be_redefined(self):
        metadata = contract(synthetic_node())
        self.assertIn("sem_arity_conflict", self.codes(metadata, context=ValueContext(argument_count=1, value_optional=True)))
        self.assertIn("sem_arity_conflict", self.codes(metadata, context=ValueContext(argument_count=0, value_optional=False)))
        node = synthetic_node("count")
        node["when_absent"] = {"state": "known", "meaning": "Contradictory prose", "form": "plain", "value": "0"}
        self.assertIn("sem_default_conflict", self.codes(contract(node)))

    def test_one_invalid_entry_does_not_hide_other_variant_conflicts(self):
        first, second = synthetic_node(), synthetic_node()
        second["forms"][0]["unit"]["multiplier"] = "1024"
        profile = {"command": ["synthetic"], "categories": [{"options": [
            {"flag": "--missing", "argument": "N"},
            {"flag": "--broken", "argument": "N", "value_semantics": contract({"kind": "invalid"})},
            {"flag": "--conflict", "argument": "N", "value_semantics": contract(first, second)}]}]}
        diagnostics = validate_profile_semantics(profile, mode="maintained")
        self.assertTrue(any(d.option == "--missing" and d.code == "sem_metadata_missing" for d in diagnostics))
        self.assertTrue(any(d.option == "--broken" and d.code == "sem_choice" for d in diagnostics))
        self.assertTrue(any(d.option == "--conflict" and d.code == "sem_variant_conflict" for d in diagnostics))

    def test_literal_default_and_special_case_rules_agree(self):
        node = synthetic_node("enumeration", meaning="Synthetic mode",
            bare={"state": "not_accepted", "reason": "Only literal choices are allowed"}, forms=[{
                "id": "mode", "notation": "literal", "syntax": "auto", "tokens": ["auto"],
                "case": "insensitive", "meaning": "Synthetic automatic mode",
                "special_values": [{"value": "auto", "meaning": "Choose the synthetic platform mode"}]}],
            when_absent={"state": "known", "form": "mode", "value": "AUTO"})
        self.assert_valid(contract(node))
        self.assertTrue(any("Option absent: Choose the synthetic platform mode (literal AUTO)" in line
                            for line in format_value_semantics(contract(node))))
        node["forms"][0]["special_values"].append({"value": "AUTO", "meaning": "Different interpretation"})
        self.assertIn("sem_special_conflict", self.codes(contract(node)))

    def test_case_rules_can_be_irrelevant_or_explicitly_unverified(self):
        node = synthetic_node("enumeration", bare={"state": "not_accepted", "reason": "Only listed numbers are accepted"},
            forms=[{"id": "one", "notation": "literal", "syntax": "1", "tokens": ["1"], "meaning": "One synthetic mode"}])
        self.assert_valid(contract(node))  # Digits do not need a case rule.
        self.assertNotIn("case ", "\n".join(format_value_semantics(contract(node))))
        node["forms"][0]["tokens"] = ["one"]
        node["forms"][0]["syntax"] = "one"
        node["forms"][0]["case"] = "not_applicable"
        self.assertIn("sem_form_conflict", self.codes(contract(node)))
        node["forms"][0]["case"] = "unverified"
        diagnostics = validate_value_semantics(contract(node), mode="external")
        self.assertTrue(all(d.severity == "warning" for d in diagnostics))
        self.assertIn("sem_unverified", {d.code for d in diagnostics})
        self.assertIn("case unverified", "\n".join(format_value_semantics(contract(node))))

    def test_pure_apis_do_not_execute_access_network_read_write_or_mutate(self):
        path = ROOT / "tests/fixtures/value-semantics/synthetic-profile.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        original = deepcopy(profile)
        sources = sorted((ROOT / "profiles").glob("*.json"))
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in sources}
        metadata = profile["categories"][0]["options"][0]["value_semantics"]
        definitions = profile["value_definitions"]
        patches = [(builtins, "open"), (Path, "open"), (subprocess, "Popen"), (socket, "socket"),
                   (builtins, "eval"), (builtins, "exec")]
        from contextlib import ExitStack
        with ExitStack() as stack:
            for owner, name in patches:
                stack.enter_context(patch.object(owner, name, side_effect=AssertionError("Unexpected side effect")))
            self.assertEqual(validate_profile_semantics(profile, mode="maintained", alias_groups=[("--delay", "-d")]), ())
            self.assertEqual(validate_value_semantics(metadata, mode="maintained", definitions=definitions), ())
            a = format_value_semantics(metadata, definitions=definitions)
            self.assertEqual(a, format_value_semantics(deepcopy(metadata), definitions=deepcopy(definitions)))
        self.assertEqual(profile, original)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in sources})

    def test_malformed_contracts_produce_diagnostics_not_secondary_exceptions(self):
        for bad in ([], "quantity", True, 1, {"schema_version": 2, "variants": []},
                    {"schema_version": 1, "variants": [None]},
                    contract({"kind": "unsupported"})):
            with self.subTest(bad=bad):
                diagnostics = validate_value_semantics(bad)
                self.assertTrue(diagnostics)
                with self.assertRaises(ValueSemanticsError) as failure:
                    format_value_semantics(bad)
                self.assertTrue(failure.exception.diagnostics)
        for location in (("review",), ("applicability",), ("bare",), ("forms",),
                         ("forms", 0, "bounds"), ("forms", 0, "unit"), ("forms", 0, "special_values")):
            for bad in ([], "invalid", True, 5):
                if location[-1] == "special_values" and bad == []:
                    continue  # An explicitly empty list declares no special cases.
                node = synthetic_node()
                target = node
                for part in location[:-1]:
                    target = target[part]
                target[location[-1]] = bad
                with self.subTest(location=location, bad=bad):
                    self.assertTrue(validate_value_semantics(contract(node)))

    def test_contradictory_forms_ranges_and_scales_are_rejected(self):
        node = synthetic_node()
        node["forms"][0]["unit"]["multiplier"] = "0"
        self.assertIn("sem_scale", self.codes(contract(node)))
        node = synthetic_node()
        node["forms"][0]["bounds"] = {"min": "10", "max": "1"}
        self.assertIn("sem_bounds", self.codes(contract(node)))
        node["forms"][0]["bounds"] = {"min": "1", "max": "1", "min_inclusive": False}
        self.assertIn("sem_bounds", self.codes(contract(node)))
        node = synthetic_node()
        node["forms"] += [{"id": "k", "notation": "suffix", "syntax": "Nk", "tokens": ["k"], "case": "insensitive",
                           "unit": {"base": "byte", "multiplier": "1000"}},
                          {"id": "K", "notation": "suffix", "syntax": "NK", "tokens": ["K"], "case": "sensitive",
                           "unit": {"base": "byte", "multiplier": "1024"}}]
        self.assertIn("sem_form_conflict", self.codes(contract(node)))
        node["forms"][1]["case"] = "sensitive"
        self.assert_valid(contract(node))


if __name__ == "__main__":
    unittest.main()
