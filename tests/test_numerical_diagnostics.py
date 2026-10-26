"""Protect source-scoped diagnostic dispositions without suppressing signals.

Factual comparisons are bounded to the primary references recorded in the exact
review groups and diagnostic-investigation.md. No target or upstream code runs.
"""

from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "cli_help")]
import check_numerical_coverage as coverage
import presentation
from value_semantics import validate_value_semantics


class NumericalDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inspect actual maintained sources under process/network tripwires."""
        stack = ExitStack()
        cls.addClassCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen",
                       "socket.socket", "socket.create_connection", "socket.getaddrinfo",
                       "urllib.request.urlopen", "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Offline inspection boundary")))
        cls.reviews = json.loads((ROOT / coverage.inventory.REVIEW_PATH).read_text(encoding="utf-8"))
        cls.groups = {group["id"]: group for group in cls.reviews["groups"]}
        cls.inventory = coverage.inventory.build_inventory(ROOT, cls.reviews)
        cls.entries = {entry["id"]: entry for entry in cls.inventory["entries"]}
        cls.strict = coverage.check_coverage(ROOT, cls.reviews, mode="strict")

    def group(self, identity):
        return self.groups[self.entries[identity]["review_group"]]

    def test_output_byte_warnings_remain_visible_without_invented_operands(self):
        """fd 9.0.0 bool and GNU tar bare action distinguish output from input."""
        for command, flag, token in (("fd", "--print0", "NUL bytes"),
                                     ("fdfind", "--print0", "NUL bytes"),
                                     ("tar", "--totals", "bytes processed")):
            with self.subTest(command=command):
                identity = f"option|{command}|{flag}"
                profile = json.loads((ROOT / "profiles" / (command + ".json")).read_text(encoding="utf-8"))
                category, option = next((c, o) for c in profile["categories"] for o in c["options"] if o["flag"] == flag)
                original = deepcopy(profile)
                self.assertFalse(option.get("argument"))
                self.assertNotIn("value_semantics", option)
                self.assertEqual(self.group(identity)["classification"], "nonnumerical")
                self.assertNotEqual(self.group(identity)["evidence"], "verified")
                self.assertTrue(any(d["identity"] == identity and d["code"] == "coverage_numerical_prose"
                                    and d["severity"] == "warning" for d in self.strict["diagnostics"]))
                view = presentation.option_text(profile, category, option)
                self.assertIn(token, "\n".join(view.details))
                self.assertIn(token.casefold(), view.searchable)
                self.assertEqual(profile, original)

    def test_fixed_digits_classify_the_documented_action_or_count(self):
        """Pinned fd/fzf/psql/yq and coreutils sections support these distinctions."""
        actions = ["du|-0", "fd|-0", "fdfind|-0", "psql|-0", "psql|-1", "scp|-3", "yq eval|-0"]
        counts = ["fd|-1", "fdfind|-1", "fzf|-0", "fzf|-1"]
        for classification, names in (("nonnumerical", actions), ("count", counts)):
            for name in names:
                identity = "option|" + name
                with self.subTest(identity=identity):
                    entry = self.entries[identity]
                    group = self.group(identity)
                    self.assertTrue(entry["numeric_fixed_spelling"])
                    self.assertEqual(group["classification"], classification)
                    self.assertEqual(group["evidence"], "source-derived")
                    self.assertFalse(any(o["role"] == "bundled_option" for o in entry["observations"]))
                    self.assertTrue(any(ref.startswith("https://") for ref in group["references"]))

    def test_reclassified_fixed_actions_cannot_evade_future_maintained_contracts(self):
        """A source-reviewed external action is not a future bundled exemption."""
        profile = {"command": ["controlled-specimen"], "categories": [{"name": "Actions", "options": [
            {"flag": "-0", "summary": "Select a delimiter"}]}]}
        for option in ({"flag": "-0", "summary": "Select a delimiter"},
                       {"flag": "--name", "argument": "TEXT", "summary": "Select a name"}):
            profile["categories"][0]["options"][0] = option
            record = next(coverage.profile_records(profile, "profiles/controlled.json"))
            self.assertTrue(coverage.needs_contract(record, "nonnumerical"))
            codes = {d.code for d in validate_value_semantics(record["metadata"], mode="maintained", context=record["context"])}
            self.assertIn("sem_metadata_missing", codes)

    def test_nested_manual_context_does_not_become_verified_root_compatibility(self):
        """Git 2.43 diff stages and OpenSSH 9.6p1 interactive ls retain ownership."""
        for name in ("git stash show|-0", "git stash show|-1", "git stash show|-2", "sftp|-1"):
            identity = "option|" + name
            self.assertNotIn(identity, self.entries)
        git_entry = self.entries["option|git stash show|--stat"]
        contexts = [self.inventory["contexts"][o["context_id"]] for o in git_entry["observations"] if o["role"] == "captured_help"]
        self.assertTrue(any("git-diff" in context.get("source", []) for context in contexts))
        self.assertTrue(any(context.get("documentation", {}).get("provenance", {}).get("manual_scope") == "common_options"
                            for context in contexts))
        self.assertTrue(any("-1 --base" in paragraph["text"] for context in contexts
                            for paragraph in context.get("documentation", {}).get("shared", [])))
        sftp_entry = self.entries["option|sftp|-B"]
        contexts = [self.inventory["contexts"].get(o.get("context_id"), {}) for o in sftp_entry["observations"]]
        self.assertTrue(any("single columnar" in paragraph["text"] and not paragraph["options"]
                            for context in contexts for paragraph in context.get("documentation", {}).get("shared", [])))

    def test_sort_composite_disposition_follows_an_explicit_source_declaration(self):
        """coreutils 9.4, sort invocation: KEYDEF positions start at one."""
        raw = (ROOT / "tests/fixtures/help/workflow-sort.txt").read_text(encoding="utf-8")
        self.assertIn("-k, --key=KEYDEF", raw)
        for name in ("-k", "--key"):
            entry = self.entries["option|sort|" + name]
            self.assertEqual(self.group(entry["id"])["classification"], "composite")
            observed = [o for o in entry["observations"] if o["role"] == "fixture_help"]
            self.assertTrue(any("-k" in o.get("aliases", []) and "--key=" in o.get("aliases", []) for o in observed))
            self.assertTrue(any("origin 1" in o["option"].get("detail", "") for o in observed))

    def test_external_groups_report_logical_entries_not_observations(self):
        """Every repeated capture/matrix relationship remains inspectable."""
        expected = Counter()
        observations = 0
        for entry in self.inventory["entries"]:
            roles = {o["role"] for o in entry["observations"]}
            if entry["kind"] in {"option", "keyword"} and "bundled_option" not in roles and roles & {"fixture_help", "captured_help"}:
                expected[entry["review_group"]] += 1
                observations += len(entry["observations"])
        actual = {d["pointer"].removeprefix("/groups/"): d for d in self.strict["diagnostics"] if d["gate"] == "external"}
        self.assertEqual(set(actual), {name for name in expected if self.groups[name]["evidence"] != "verified"})
        for name, diagnostic in actual.items():
            self.assertTrue(diagnostic["message"].startswith(str(expected[name]) + " external-only logical entries"))
            self.assertEqual((diagnostic["code"], diagnostic["severity"]), ("coverage_external_uncertainty", "info"))
        self.assertEqual(sum(expected.values()), self.strict["external_only_logical_entries"])
        self.assertGreater(observations, sum(expected.values()))

    def test_resource_observations_keep_unresolved_forms_and_capture_scope(self):
        """Podman 4.9.3 base quantities do not establish a complete input grammar."""
        for flag in ("--cpu-period", "--cpu-quota", "--memory", "-m", "--memory-reservation",
                     "--memory-swap", "--timeout", "--pids-limit", "--blkio-weight",
                     "--health-interval", "--device-read-bps", "--device-write-bps"):
            identity = "option|podman run|" + flag
            self.assertEqual(self.group(identity)["classification"], "unresolved")
            self.assertEqual(self.group(identity)["evidence"], "source-derived")
            for observation in self.entries[identity]["observations"]:
                context = self.inventory["contexts"].get(observation.get("context_id"), {})
                if observation["role"] == "fixture_help":
                    self.assertTrue(any(a.get("version") == "podman version 4.9.3" for a in context.get("associations", [])))
        # Operand loss is an explicitly deferred parser issue, not a passing
        # assertion that requires the parser to retain its current defect.
        raw = (ROOT / "tests/fixtures/help/followup-systems/podman-run.txt").read_text(encoding="utf-8")
        self.assertIn("--memory <number>[<unit>]", raw)
        self.assertIn("k (kibibytes)", raw)

    def test_synthetic_vlc_and_unversioned_pip_do_not_inherit_versioned_evidence(self):
        """VLC 3.0.21 marks volume obsolete; pip 24.0 is a separate module capture."""
        for flag in ("--volume", "--rate"):
            identity = "option|vlc|" + flag
            self.assertEqual(self.group(identity)["classification"], "unresolved")
            self.assertEqual(self.group(identity)["evidence"], "source-derived")
            contexts = [self.inventory["contexts"].get(o.get("context_id"), {}) for o in self.entries[identity]["observations"]]
            self.assertFalse(any(c.get("version") for c in contexts))
        root = self.entries["option|pip|--timeout"]
        module = self.entries["option|<selected-python> -m pip|--timeout"]
        self.assertNotEqual(root["id"], module["id"])
        self.assertTrue(any(o.get("option", {}).get("detail") == "Set timeout" for o in root["observations"]))
        self.assertTrue(any("15 seconds" in o.get("option", {}).get("detail", "") for o in module["observations"]))
        self.assertEqual(self.group(root["id"])["evidence"], "source-derived")

    def test_current_strict_readiness_has_no_debt_or_exceptions(self):
        self.assertEqual(self.inventory["diagnostics"], [])
        self.assertTrue(self.strict["passed"], self.strict["diagnostics"])
        self.assertTrue(self.strict["full_maintained_ready"])
        self.assertEqual(self.strict["remaining_debt"], [])
        self.assertEqual(self.reviews["coverage_policy"]["legacy_baseline"]["entries"], [])
        self.assertEqual(self.reviews["coverage_policy"]["exceptions"], [])
        self.assertEqual(self.strict["counts"]["complete_records"], self.strict["counts"]["contract_required_records"])


if __name__ == "__main__":
    unittest.main()
