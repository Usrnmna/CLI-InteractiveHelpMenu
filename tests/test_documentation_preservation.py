"""Protect source documentation, atomic semantics and passive cache round trips.

Real source assertions use immutable captures and a separate reference manifest.
Synthetic profiles exercise merge rules without claiming target-program facts.
Every discovery response is mocked; target execution and network access fail.
"""

from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
import discovery
from core import Context, HelpError, insert_option, validate_profile
from value_semantics import format_value_semantics, validate_profile_semantics, validate_value_semantics


def options(profile):
    """Index literal records without inferring aliases from text."""
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


class PreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.synthetic = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        cls.evidence = json.loads((ROOT / "tests/fixtures/value-semantics/preservation-evidence.json").read_text(encoding="utf-8"))

    def setUp(self):
        parent = (ROOT / ".cache/documentation-preservation-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.folder = parent / uuid.uuid4().hex
        self.folder.mkdir()
        # Resolved absolute cleanup targets remain within this disposable root.
        if (self.folder.resolve().parent != parent or self.folder.is_symlink()
                or getattr(self.folder, "is_junction", lambda: False)()):
            raise RuntimeError("Test directory escaped its selected cache location")
        self.addCleanup(shutil.rmtree, self.folder)
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "socket.socket", "socket.create_connection",
                       "socket.getaddrinfo", "os.system", "os.popen", "discovery.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Target execution or network access attempted")))

    def profile(self, source="synthetic:first"):
        result = deepcopy(self.synthetic)
        result["documentation"] = {"source": source, "implementation": "synthetic-contract", "version": "1"}
        return result

    def codes(self, profile):
        return {note["code"] for note in profile["documentation"]["diagnostics"]}

    def test_gnu_shared_definitions_reach_only_explicit_targets_and_aliases(self):
        for case in self.evidence["cases"]:
            command = case["command"]
            path = ROOT / f"tests/fixtures/help/workflow-{command}.txt"
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            profile = discovery.build_profile(command, [(f"GNU coreutils 9.4 {command} help", path.read_text(encoding="utf-8"))])
            records = options(profile)
            with self.subTest(command=command, flag=case["option"]):
                for fragment in case["fragments"]:
                    self.assertIn(fragment, records[case["option"]]["detail"])
                    self.assertIn(fragment, records[case["alias"]]["detail"])
                    self.assertNotIn(fragment, records[case["excluded"]]["detail"])
                self.assertTrue(any(case["option"] in item["options"] for item in profile["documentation"]["shared"]))
                self.assertTrue(all(item["source"] and item["line"] > 0 for item in profile["documentation"]["shared"]))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
        # A display-default paragraph explicitly names block-size; sharing the
        # SIZE grammar does not give threshold the display environment defaults.
        du = discovery.build_profile("du", [("capture", (ROOT / "tests/fixtures/help/workflow-du.txt").read_text())])
        self.assertNotIn("POSIXLY_CORRECT", options(du)["--threshold="]["detail"])
        sort = discovery.build_profile("sort", [("capture", (ROOT / "tests/fixtures/help/workflow-sort.txt").read_text())])
        self.assertNotIn("both are origin 1", options(sort)["--debug"]["detail"])

    def test_generic_metavariables_wrap_and_preserve_unassigned_information(self):
        text = ("Options:\n  -q, --quota=AMOUNT  Set quota\n  --mode=NAME  Select a name\n"
                "  --version  Show version\n\nAMOUNT may use a decimal or binary suffix.\n"
                "Zero disables the quota; negative values are invalid.\n\n"
                "The UNDECLARED argument is measured in milliseconds.\n\nCopyright notice.\n")
        profile = discovery.build_profile("synthetic", [("synthetic:wrapped", text)])
        records = options(profile)
        self.assertIn("binary suffix", records["--quota="]["detail"])
        self.assertIn("negative values", records["-q"]["detail"])
        self.assertNotIn("milliseconds", records["--version"]["detail"])
        self.assertNotIn("milliseconds", records["--quota="]["detail"])
        self.assertIn("shared_documentation_unassigned", self.codes(profile))
        self.assertTrue(any("UNDECLARED" in item["text"] and not item["options"]
                            for item in profile["documentation"]["shared"]))
        self.assertFalse(any("value_semantics" in entry for entry in records.values()))

    def test_shared_examples_are_not_insertable_and_new_options_section_resumes(self):
        text = ("Options:\n  --size=AMOUNT  Size\n\nAMOUNT is a byte count.\n"
                "  --example-not-a-declaration  Example syntax inside this paragraph\n"
                "Other options:\n  --quiet  Suppress messages\n")
        profile = discovery.build_profile("synthetic", [("synthetic:example", text)])
        self.assertEqual(set(options(profile)), {"--size=", "--quiet"})
        self.assertIn("--example-not-a-declaration", options(profile)["--size="]["detail"])

    def test_indented_manual_definitions_keep_inline_units_and_separate_notes(self):
        text = ("OPTIONS\n       --delay MS\n              Wait in milliseconds.\n"
                "              Zero disables the wait.\n\nNOTES\n"
                "       MS is a count of milliseconds, not seconds.\n"
                "       Negative values are not accepted.\n")
        profile = discovery.build_profile("synthetic", [("synthetic:manual", text)])
        self.assertEqual(set(options(profile)), {"--delay"})
        self.assertIn("Wait in milliseconds", options(profile)["--delay"]["detail"])
        self.assertIn("not seconds", options(profile)["--delay"]["detail"])

    def test_shared_sections_and_later_categories_retain_applicability_qualifiers(self):
        text = ("Options:\n  --size=AMOUNT  Set size\n\nESP32 ONLY, VERSION 5:\n"
                "AMOUNT is a byte count for this chip and release.\n")
        parsed = discovery.build_profile("synthetic", [("synthetic:qualified", text)])
        self.assertIn("ESP32 ONLY, VERSION 5", options(parsed)["--size="]["detail"])
        first, second = self.profile(), self.profile("synthetic:qualified-category")
        second["categories"][0].update(name="Synthetic OS version 2", description="Only synthetic-chip accepts this scale")
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(merged["categories"][0]["name"], first["categories"][0]["name"])
        detail = options(merged)["--delay"]["detail"]
        self.assertIn("Synthetic OS version 2", detail)
        self.assertIn("Only synthetic-chip", detail)
        self.assertEqual(merged["documentation"]["sources"][1]["categories"][0]["description"], second["categories"][0]["description"])

    def test_later_summary_and_detail_survive_without_replacing_first_meaning(self):
        first, second = self.profile(), self.profile("synthetic:later")
        options(first)["--delay"].update(summary="Wait in seconds", detail="")
        options(second)["--delay"].update(summary="Bare values are seconds; ms is supported", detail="Zero disables the wait")
        before = deepcopy([first, second])
        merged = discovery.merge_profiles([first, second])
        delay = options(merged)["--delay"]
        self.assertEqual(delay["summary"], "Wait in seconds")
        self.assertIn("ms is supported", delay["detail"])
        self.assertIn("Zero disables", delay["detail"])
        self.assertIn("Source: synthetic:later", delay["detail"])
        self.assertEqual([first, second], before)
        options(second)["--delay"]["detail"] = ""
        options(second)["--delay"]["summary"] = "Wait in seconds"
        self.assertEqual(options(discovery.merge_profiles([first, second]))["--delay"]["summary"], "Wait in seconds")

    def test_numerical_text_conflicts_are_review_candidates_without_invented_units(self):
        merged = discovery.build_profile("synthetic", [("synthetic:a", "  --delay=N  Wait in seconds\n"),
                                                        ("synthetic:b", "  --delay=N  Wait in milliseconds\n")])
        self.assertEqual(options(merged)["--delay="]["summary"], "Wait in seconds")
        self.assertIn("milliseconds", options(merged)["--delay="]["detail"])
        self.assertIn("numerical_text_review", self.codes(merged))
        self.assertNotIn("value_semantics", options(merged)["--delay="])

    def test_definition_collisions_never_rebind_source_references(self):
        first, second = self.profile(), self.profile("synthetic:milliseconds")
        second["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "0.001"
        options(second)["--delay"]["flag"] = "--later-delay"
        options(second)["-d"]["flag"] = "--later-alias"
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(validate_profile_semantics(merged, alias_groups=[["--delay", "-d"], ["--later-delay", "--later-alias"]]), ())
        definitions = merged["value_definitions"]
        early_ref = options(merged)["--delay"]["value_semantics"]["variants"][0]["ref"]
        later_ref = options(merged)["--later-delay"]["value_semantics"]["variants"][0]["ref"]
        self.assertNotEqual(early_ref, later_ref)
        self.assertEqual(definitions[early_ref]["forms"][0]["unit"]["multiplier"], "1")
        self.assertEqual(definitions[later_ref]["forms"][0]["unit"]["multiplier"], "0.001")

    def test_nested_definitions_are_scoped_even_when_reference_objects_match(self):
        first, second = self.profile(), self.profile("synthetic:other")
        for profile in (first, second):
            profile["value_definitions"]["outer"] = {"ref": "delay"}
            options(profile)["--delay"]["value_semantics"]["variants"] = [{"ref": "outer"}]
        second["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "1024"
        options(second)["--delay"]["flag"] = "--other"
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(validate_profile_semantics(merged), ())
        text = "\n".join(format_value_semantics(options(merged)["--other"]["value_semantics"], definitions=merged["value_definitions"]))
        self.assertIn("1024 seconds", text)

    def test_conflicting_semantics_remain_atomic_and_qualified(self):
        first, second = self.profile(), self.profile("synthetic:conflict")
        second["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "0.001"
        merged = discovery.merge_profiles([first, second])
        self.assertIn("value_semantics_conflict", self.codes(merged))
        self.assertEqual(options(merged)["--delay"]["value_semantics"], options(first)["--delay"]["value_semantics"])
        self.assertTrue(any(item.get("option") == "--delay" and item.get("definition_scope") == "profile"
                            for item in merged["documentation"]["alternatives"]))
        self.assertEqual(validate_profile_semantics(merged), ())
        self.assertEqual(merged["value_definitions"]["delay"]["review"]["status"], "synthetic")

    def test_disjoint_versions_preserve_alternatives_without_claiming_conflict(self):
        first, second = self.profile(), self.profile("synthetic:version3")
        node = second["value_definitions"]["delay"]
        node["applicability"]["version"] = {"state": "known", "values": ["3"]}
        node["forms"][0]["unit"]["multiplier"] = "0.001"
        merged = discovery.merge_profiles([first, second])
        self.assertNotIn("value_semantics_conflict", self.codes(merged))
        self.assertTrue(any(item["field"] == "value_semantics" for item in merged["documentation"]["alternatives"]))
        self.assertTrue(any(node["applicability"]["version"].get("values") == ["3"] for node in merged["value_definitions"].values()))

    def test_missing_and_malformed_references_remain_inactive_evidence(self):
        first, second = self.profile(), self.profile("synthetic:dangling")
        second["value_definitions"] = {}
        options(second)["--delay"]["flag"] = "--unresolved"
        merged = discovery.merge_profiles([first, second])
        self.assertNotIn("value_semantics", options(merged)["--unresolved"])
        self.assertIn("source_semantics_invalid", self.codes(merged))
        self.assertEqual(validate_profile_semantics(merged), ())
        self.assertTrue(any(item.get("definition_scope") == "source" and item.get("value_definitions") == {}
                            for item in merged["documentation"]["alternatives"]))
        malformed = self.profile("synthetic:malformed")
        malformed["value_definitions"]["broken"] = {"kind": "not-a-kind"}
        merged = discovery.merge_profiles([malformed])
        self.assertIn("delay", merged["value_definitions"])
        self.assertNotIn("broken", merged["value_definitions"])
        self.assertIn("source_definitions_invalid", self.codes(merged))

    def test_unrelated_flags_never_inherit_semantics_from_matching_summaries(self):
        first, second = self.profile(), self.profile("synthetic:unrelated")
        unrelated = {"flag": "--unrelated", "argument": "NAME", "summary": options(first)["--delay"]["summary"]}
        second["categories"][0]["options"] = [unrelated]
        second.pop("value_definitions")
        merged = discovery.merge_profiles([first, second])
        self.assertNotIn("value_semantics", options(merged)["--unrelated"])
        third = self.profile("synthetic:other-command")
        third["command"] = ["other-command"]
        with self.assertRaises(HelpError):
            discovery.merge_profiles([first, third])

    def test_later_metadata_keeps_its_source_through_remerge_and_cache(self):
        first, second = self.profile("synthetic:legacy"), self.profile("synthetic:semantics")
        first.pop("value_definitions")
        for option in options(first).values():
            option.pop("value_semantics", None)
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(merged["documentation"]["semantic_sources"]["--delay"], "synthetic:semantics")
        self.assertEqual(discovery.merge_profiles([merged])["documentation"]["semantic_sources"],
                         merged["documentation"]["semantic_sources"])
        path = self.folder / "provenance.json"
        identity = {"command": merged["command"]}
        discovery.write_cache(path, identity, merged)
        self.assertEqual(discovery.read_cache(path, identity, 60)["documentation"]["semantic_sources"],
                         merged["documentation"]["semantic_sources"])

    def test_positional_metadata_is_a_sibling_and_group_declarations_are_unchanged(self):
        first = json.loads((ROOT / "profiles/esptool-write-flash.json").read_text(encoding="utf-8"))
        second = deepcopy(first)
        second["documentation"] = {"source": "synthetic:other-positional"}
        second["positional_group"]["argument_count"] = 3
        # The copied two-slot semantics is invalid for the changed declaration;
        # it must remain source evidence instead of changing the first group.
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(merged["positional_group"], first["positional_group"])
        self.assertEqual(merged["positional_value_semantics"], first["positional_value_semantics"])
        self.assertIn("source_semantics_invalid", self.codes(merged))
        self.assertEqual(validate_profile_semantics(merged), ())

    def test_identity_mismatch_does_not_activate_unmatched_metadata(self):
        first = self.profile("synthetic:esptool4")
        first["command"], first["identity"] = ["esptool"], "esptool-v4"
        for option in options(first).values():
            option.pop("value_semantics", None)
        first.pop("value_definitions")
        second = self.profile("synthetic:esptool5")
        second["command"], second["identity"] = ["esptool"], "esptool-v5"
        merged = discovery.merge_profiles([first, second])
        self.assertNotIn("value_semantics", options(merged)["--delay"])
        self.assertIn("value_semantics_conflict", self.codes(merged))
        self.assertEqual(merged["identity"], "esptool-v4")

    def test_arity_changes_retain_the_original_semantic_source_and_declaration(self):
        first, second = self.profile("synthetic:required-one"), self.profile("synthetic:required-two")
        options(second)["--delay"].pop("value_semantics")
        options(second)["--delay"].update(argument="NAME VALUE", argument_count=2)
        # A one-slot composite cannot silently become a two-slot declaration.
        first["categories"][0]["options"] = [options(first)["--delay"]]
        first["value_definitions"]["pair"] = {
            "kind": "composite", "meaning": "Synthetic joined pair", "slots": 1,
            "components": [{"id": "delay", "slot": 1, "required": True, "semantics": {"ref": "delay"}}]}
        options(first)["--delay"]["value_semantics"]["variants"] = [{"ref": "pair"}]
        merged = discovery.merge_profiles([first, second])
        self.assertNotIn("value_semantics", options(merged)["--delay"])
        retained = next(item for item in merged["documentation"]["alternatives"] if item.get("option") == "--delay")
        self.assertEqual(retained["source"], "synthetic:required-one")
        self.assertEqual(retained["declaration"]["argument"], "DURATION")
        self.assertIn("semantics_arity_review", self.codes(merged))

    def test_valid_alternative_positional_groups_do_not_replace_the_first_group(self):
        first = json.loads((ROOT / "profiles/esptool-write-flash.json").read_text(encoding="utf-8"))
        second = deepcopy(first)
        second["documentation"] = {"source": "synthetic:three-slots"}
        second["positional_group"].update(argument="ADDRESS FILE OTHER", argument_count=3)
        node = second["positional_value_semantics"]["variants"][0]
        node["slots"] = 3
        extra = deepcopy(node["components"][1])
        extra.update(id="other", slot=3)
        node["components"].append(extra)
        self.assertEqual(validate_profile_semantics(second), ())
        merged = discovery.merge_profiles([first, second])
        self.assertEqual(merged["positional_group"], first["positional_group"])
        self.assertIn("positional_semantics_review", self.codes(merged))
        self.assertTrue(any(item.get("declaration", {}).get("argument_count") == 3
                            for item in merged["documentation"]["alternatives"]))

    def test_legacy_arity_policy_and_literal_buffer_edits_are_preserved(self):
        profile = discovery.build_profile("synthetic", [("synthetic:short", "  --pair  Supply a pair\n  --maybe[=N]  Optional count\n"),
                                                         ("synthetic:manual", "  --pair NAME VALUE  Two values\n  --maybe=N  Required count\n")])
        self.assertEqual(options(profile)["--pair"]["argument_count"], 2)
        self.assertFalse(options(profile)["--maybe="]["argument_optional"])
        before = deepcopy(profile)
        for option in options(profile).values():
            line = "synthetic   --par  untouched $(untrusted)"
            start, end = len("synthetic   "), len("synthetic   --par")
            edited, point = insert_option(Context(line, end, start, end, "--par", profile), option)
            self.assertEqual(edited[:start], line[:start])
            self.assertTrue(edited.endswith(line[end:]))
            self.assertEqual(point, start + len(option["flag"]) + (0 if option["flag"].endswith("=") else 1))
        self.assertEqual(profile, before)

    def test_metadata_kinds_and_qualifications_survive_merge_and_cache_round_trips(self):
        seen = set()
        for path in sorted((ROOT / "profiles").glob("*.json")):
            profile = json.loads(path.read_text(encoding="utf-8"))
            kinds = {profile.get("value_definitions", {}).get(node.get("ref"), node)["kind"]
                     for option in options(profile).values() for node in option.get("value_semantics", {}).get("variants", [])}
            if not kinds - seen and not profile.get("positional_value_semantics"):
                continue
            seen.update(kinds)
            original = deepcopy(profile)
            merged = discovery.merge_profiles([profile])
            cache = self.folder / (path.stem + ".json")
            identity = {"command": profile["command"], "version": discovery.CACHE_VERSION}
            discovery.write_cache(cache, identity, merged)
            loaded = discovery.read_cache(cache, identity, 60)
            with self.subTest(profile=path.stem):
                self.assertEqual(loaded, merged)
                self.assertEqual(profile, original)
                for flag, option in options(profile).items():
                    if "value_semantics" in option:
                        self.assertEqual(options(loaded)[flag]["value_semantics"], option["value_semantics"])
                        before = format_value_semantics(option["value_semantics"], definitions=profile.get("value_definitions"))
                        after = format_value_semantics(options(loaded)[flag]["value_semantics"], definitions=loaded.get("value_definitions"))
                        self.assertEqual(after, before)
                        self.assertEqual(validate_value_semantics(option["value_semantics"], mode="external", definitions=profile.get("value_definitions")),
                                         validate_value_semantics(options(loaded)[flag]["value_semantics"], mode="external", definitions=loaded.get("value_definitions")))
        self.assertTrue({"duration", "quantity", "count", "identifier", "index", "level", "enumeration", "timestamp", "composite", "delegated", "nonnumerical"} <= seen)

    def test_cache_rejects_malformed_semantics_but_accepts_incomplete_legacy_content(self):
        profile = self.profile()
        identity = {"command": profile["command"]}
        path = self.folder / "cache.json"
        discovery.write_cache(path, identity, profile)
        self.assertEqual(discovery.read_cache(path, identity, 60), profile)
        document = json.loads(path.read_text(encoding="utf-8"))
        document["profile"]["value_definitions"]["delay"]["forms"][0]["unit"]["multiplier"] = "0"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertIsNone(discovery.read_cache(path, identity, 60))
        invalid = document["profile"]
        no_write = self.folder / "invalid.json"
        discovery.write_cache(no_write, identity, invalid)
        self.assertFalse(no_write.exists())
        legacy = deepcopy(profile)
        legacy.pop("value_definitions")
        for option in options(legacy).values():
            option.pop("value_semantics", None)
        discovery.write_cache(path, identity, legacy)
        self.assertEqual(discovery.read_cache(path, identity, 60), legacy)
        draft = deepcopy(legacy)
        options(draft)["--delay"]["value_semantics"] = {"schema_version": 1, "variants": [{"kind": "unresolved", "investigation": "Synthetic grammar is undocumented"}]}
        discovery.write_cache(path, identity, draft)
        self.assertEqual(discovery.read_cache(path, identity, 60), draft)
        self.assertTrue(validate_profile_semantics(draft, mode="maintained"))

    def test_cache_legacy_malformed_expired_and_wrong_identity_cases_are_misses(self):
        profile = self.profile()
        identity = {"command": profile["command"], "version": discovery.CACHE_VERSION}
        path = self.folder / "cache.json"
        discovery.write_cache(path, identity, profile)
        original = json.loads(path.read_text(encoding="utf-8"))
        for key, value in (("identity", {**identity, "version": discovery.CACHE_VERSION - 1}), ("created", 0),
                           ("created", "invalid"), ("profile", {}), ("profile", {**profile, "command": ["different"]})):
            document = deepcopy(original)
            document[key] = value
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.subTest(field=key, value=value):
                self.assertIsNone(discovery.read_cache(path, identity, 60))
        path.write_text("{not-json", encoding="utf-8")
        self.assertIsNone(discovery.read_cache(path, identity, 60))

    def test_mocked_discovery_cold_warm_invalidation_and_warning_preservation(self):
        executable = self.folder / "synthetic-contract"
        executable.write_text("Inert identity specimen; never executed", encoding="utf-8")
        cache_dir = self.folder / "cache"
        cache_dir.mkdir()
        settings = discovery.Settings(cache_dir=cache_dir)
        text = "Options:\n  --delay=N  Wait in seconds\n\nUNKNOWN is a number in milliseconds.\n"
        with patch("discovery.shutil.which", side_effect=lambda name: None if name == "man" else str(executable)), \
                patch("discovery.run_probe", return_value=text) as probe:
            cold = discovery.discover("synthetic-contract", settings)
            warm = discovery.discover("synthetic-contract", settings)
            self.assertEqual(cold, warm)
            self.assertEqual(probe.call_count, 1)
            self.assertIn("shared_documentation_unassigned", self.codes(warm))
            self.assertTrue(any("shared_documentation_unassigned" in warning for warning in warm["discovery"]["warnings"]))
            with patch("discovery.CACHE_VERSION", discovery.CACHE_VERSION + 1):
                refreshed = discovery.discover("synthetic-contract", settings)
            self.assertEqual(probe.call_count, 2)
            self.assertEqual(refreshed["documentation"], cold["documentation"])
            self.assertEqual(len(list(cache_dir.glob("*.json"))), 2)
            discovery.discover("synthetic-contract", settings, refresh=True)
            self.assertEqual(probe.call_count, 3)

    def test_deterministic_pure_transformations_and_opaque_provenance(self):
        first, second = self.profile(), self.profile("synthetic:second")
        first["documentation"].update(platform="synthetic-os", chip="synthetic-chip", reviewed="synthetic-review")
        first["documentation"]["shared"] = None  # Opaque legacy field remains in the source record.
        originals = deepcopy([first, second])
        with patch("builtins.open", side_effect=AssertionError("Unexpected file I/O")), \
                patch("pathlib.Path.open", side_effect=AssertionError("Unexpected path I/O")):
            merged = discovery.merge_profiles([first, second])
            repeated = discovery.merge_profiles([first, second])
            self.assertEqual(merged, repeated)
        self.assertEqual([first, second], originals)
        self.assertEqual(merged["documentation"]["sources"][0]["documentation"], first["documentation"])
        self.assertEqual(merged["documentation"]["platform"], "synthetic-os")
        validate_profile(merged, Path("synthetic:merged"))


if __name__ == "__main__":
    unittest.main()
