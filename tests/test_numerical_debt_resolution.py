"""Protect source-reviewed debt corrections and their actual UI/search path.

Reference expectations are independent of production metadata. No target,
pending value, external editor, network request or operational workload runs.
"""
from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
sys.path.insert(0, str(ROOT / "scripts"))
if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub
import check_numerical_coverage as coverage
import presentation
from ui import Browser, draw, load_keys
from test_functional_matrix import FakeScreen
from value_semantics import validate_value_semantics


class NumericalDebtResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load maintained inputs before pure API assertions; never probe targets."""
        cls.profiles = {path.stem: json.loads(path.read_text(encoding="utf-8"))
                        for path in sorted((ROOT / "profiles").glob("*.json"))}
        cls.facts = json.loads((ROOT / "tests/fixtures/value-semantics/debt-resolution-evidence.json")
                               .read_text(encoding="utf-8"))["cases"]

    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                     "socket.create_connection", "socket.getaddrinfo", "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(name, side_effect=AssertionError("Debt verification attempted a non-passive action")))

    def entry(self, name, flag):
        profile = self.profiles[name]
        return next((profile, category, option) for category in profile["categories"]
                    for option in category["options"] if option["flag"] == flag)

    def node(self, name, flag):
        profile, _, option = self.entry(name, flag)
        variants = option["value_semantics"]["variants"]
        self.assertEqual(len(variants), 1)
        return profile.get("value_definitions", {}).get(variants[0].get("ref"), variants[0])

    def assert_accessible(self, name, flag, phrases, *, search_only=()):
        """Check concise rules in details and retained audit context in search."""
        profile, _, option = self.entry(name, flag)
        browser = Browser(profile, flag)
        details = " ".join(browser.text(option).details)
        for phrase in phrases:
            with self.subTest(profile=name, option=flag, phrase=phrase):
                self.assertIn(phrase.casefold(), details.casefold())
                browser.set_query(phrase)
                self.assertIn(option, browser.options())
        for phrase in search_only:
            with self.subTest(profile=name, option=flag, search_only=phrase):
                browser.set_query(phrase)
                self.assertIn(option, browser.options())
        return details

    def test_complete_current_gate_has_no_debt_or_exceptions(self):
        reviews = json.loads((ROOT / "docs/numerical-inventory/review.json").read_text(encoding="utf-8"))
        self.assertEqual(reviews["coverage_policy"]["legacy_baseline"]["entries"], [])
        self.assertEqual(reviews["coverage_policy"]["exceptions"], [])
        result = coverage.check_coverage(ROOT, reviews, mode="strict")
        self.assertTrue(result["passed"], [d for d in result["diagnostics"] if d["severity"] == "error"])
        self.assertTrue(result["full_maintained_ready"])
        self.assertEqual(result["remaining_debt"], [])
        self.assertEqual(result["counts"]["complete_records"], result["counts"]["contract_required_records"])

    def test_openssl_cli_depth_rejects_zero_independently_of_depth_api_meaning(self):
        fact = self.facts["openssl_verify"]
        node = self.node("openssl-s_client", "-verify")
        self.assertEqual(node["forms"][0]["bounds"]["min"], fact["minimum"])
        self.assertFalse(any(value["value"] == "0" for form in node["forms"] for value in form.get("special_values", [])))
        self.assert_accessible("openssl-s_client", "-verify", ["zero", "rejected", fact["subject"], *fact["excluded_certificates"]], search_only=[fact["version"]])
        profile, _, option = self.entry("openssl-s_client", "-verify")
        browser = Browser(profile, "-verify")
        screen = FakeScreen(24, 160)
        draw(screen, browser, load_keys(None))
        self.assertIn("positive", screen.text().casefold())

    def test_openssl_seconds_and_platform_width_are_explained_without_guessing_a_bound(self):
        fact = self.facts["openssl_checkend"]
        form = self.node("openssl-x509", "-checkend")["forms"][0]
        self.assertEqual(form["unit"], {"base": fact["base"], "multiplier": fact["multiplier"]})
        self.assert_accessible("openssl-x509", "-checkend", ["seconds", "negative", "0x", "time_t", "current instant"])

    def test_sftp_defaults_are_not_universal_server_caps_or_newer_option_bounds(self):
        fact = self.facts["sftp"]
        self.assert_accessible("sftp", "-B", ["bytes", "strtol", "wrap/truncate", "-X"],
                               search_only=[fact["fallback_buffer_bytes"], fact["version_zero_buffer_cap_bytes"], "server"])
        self.assert_accessible("sftp", "-R", ["requests", "zero"], search_only=[fact["fallback_requests"], "open-handle"])
        self.assertEqual(self.node("sftp", "-B")["forms"][0]["unit"], {"base": "byte", "multiplier": "1"})
        for flag in ("-B", "-R"):
            self.assertNotIn("bounds", self.node("sftp", flag)["forms"][0])

    def test_worker_counts_explain_zero_and_actual_signed_parser_behavior(self):
        fact = self.facts["arduino_jobs"]
        node = self.node("arduino-cli-compile", "--jobs")
        self.assertEqual(node["forms"][0]["bounds"], {"min": fact["minimum_parser_value"], "max": fact["maximum_parser_value"]})
        self.assert_accessible("arduino-cli-compile", "--jobs", ["CPU cores", "negative", "stall"], search_only=[fact["version"]])
        ansible = self.facts["ansible"]
        self.assertEqual(self.node("ansible-playbook", "--forks")["forms"][0]["bounds"]["min"], ansible["fork_minimum"])
        self.assert_accessible("ansible-playbook", "--forks", ["process", ansible["fork_default"], "zero", "rejected"])
        self.assert_accessible("ansible-playbook", "--limit", ["zero-based", "single negative", "nonnegative", "inclusive"])

    def test_dotnet_enum_alias_codes_are_not_linear_verbosity_levels(self):
        fact = self.facts["dotnet"]
        node = self.node("dotnet-build", "--verbosity")
        self.assertEqual(node["kind"], "level")
        self.assertEqual(node["bare"]["state"], "accepted")
        self.assertTrue(all("unit" not in form for form in node["forms"]))
        codes = [str(index) + "=" + name for index, name in enumerate(fact["verbosity_numeric_names"])]
        self.assert_accessible("dotnet-build", "--verbosity", [*codes, "not a count", "case insensitive", "undefined codes"],
                               search_only=[fact["enum_dependency_version"]])

    def test_gcloud_count_and_binary_display_tokens_survive_actual_search(self):
        fact = self.facts["gcloud"]
        for flag in ("--limit", "--page-size"):
            node = self.node("gcloud-compute-instances-list", flag)
            self.assertEqual(node["forms"][0]["bounds"]["min"], fact["minimum_count"])
            literal = next(f for f in node["forms"] if f["notation"] == "literal")
            self.assertEqual(literal["tokens"], [fact["unlimited_token"]])
            self.assertEqual(literal["case"], fact["unlimited_case"])
            self.assert_accessible("gcloud-compute-instances-list", flag, ["zero", "rejected", "sys.maxsize", "unlimited"],
                                   search_only=[fact["version"]])
        self.assert_accessible("gcloud-storage-ls", "--readable-sizes", [fact["readable_bytes_per_KiB"], "KiB", "--long", "no numerical operand"])

    def test_connection_identifier_lists_are_not_measurements(self):
        fact = self.facts["psql"]
        port = self.node("psql", "--port")
        self.assertEqual(port["kind"], "identifier")
        self.assertEqual(port["forms"][0]["bounds"], {"min": fact["port_minimum"], "max": fact["port_maximum"]})
        self.assert_accessible("psql", "--port", ["comma-separated", "empty", fact["port_maximum"], "socket"])
        endpoint = self.node("openssl-s_client", "-connect")
        self.assertEqual(endpoint["slots"], 1)
        self.assertEqual({component["id"] for component in endpoint["components"]}, {"host", "port"})
        self.assert_accessible("openssl-s_client", "-connect", ["IPv6", "service name", "4433"])
        self.assert_accessible("platformio-device-monitor", "--port", ["not converted", "index", "ordering"],
                               search_only=[self.facts["platformio"]["version"]])

    def test_git_date_heuristics_and_expiry_sentinels_remain_distinct(self):
        fact = self.facts["git_date"]
        self.assert_accessible("git-log", "--since=", [fact["epoch_heuristic_threshold"], "epoch seconds", "local", "relative"])
        expiry = self.node("git-worktree-prune", "--expire")
        for tokens in (fact["zero_cutoff_tokens"], fact["maximum_cutoff_tokens"]):
            self.assertTrue(any(form.get("tokens") == tokens for form in expiry["forms"]))
        self.assert_accessible("git-worktree-prune", "--expire", ["TIME_MAX", "never", "false", "all", "now"])

    def test_yq_zero_negative_and_ignored_encoder_cases_remain_qualified(self):
        fact = self.facts["yq_indent"]
        node = self.node("yq-eval", "--indent")
        self.assertIn(fact["default"], node["when_absent"]["meaning"])
        self.assert_accessible("yq-eval", "--indent", [fact["subject"], "YAML zero", "four-space", "negative", "JSON", "XML", "other encoders", "not promise one-line XML"])

    def test_named_and_delegated_values_have_specific_owning_grammars(self):
        for flag, kind in (("--configuration", "configuration_kind"), ("--framework", "framework_kind"), ("--runtime", "runtime_kind")):
            node = self.node("dotnet-build", flag)
            self.assertEqual(node["kind"], self.facts["dotnet"][kind])
            self.assertTrue(all("unit" not in form for form in node["forms"]))
        self.assert_accessible("dotnet-test", "--filter", [self.facts["dotnet"]["filter_property"], "adapter", "without one numerical unit"])
        self.assert_accessible("az-account-show", "--query", ["zero", "negative", "installed JMESPath library", "physical unit"])
        ruff = self.facts["ruff"]
        self.assert_accessible("ruff-format", "--extension", [*ruff["extension_languages"], "not py", "colon-separated"])
        self.assert_accessible("uv-venv", "--python", ["3.12", "version", "not measured"], search_only=["0.6.14"])
        _, _, option = self.entry("git-commit", "--file")
        self.assertEqual(option["value_semantics"]["variants"][0]["kind"], "nonnumerical")

    def test_evidence_mutation_and_presentation_omissions_are_still_rejected(self):
        metadata = deepcopy(self.entry("gcloud-compute-instances-list", "--page-size")[2]["value_semantics"])
        metadata["variants"][0]["bare"] = {"state": "unverified", "reason": "Controlled loss of factual evidence"}
        self.assertIn("sem_false_verification", {d.code for d in validate_value_semantics(metadata)})
        record = next(r for r in coverage.profile_records(self.profiles["sftp"], "profiles/sftp.json") if r["option"].get("flag") == "-B")
        original = presentation.option_text
        for field, code in (("details", "coverage_details_missing"), ("searchable", "coverage_search_missing")):
            def omit(*args, **kwargs):
                text = original(*args, **kwargs)
                return presentation.OptionText(text.compact, () if field == "details" else text.details,
                                               "" if field == "searchable" else text.searchable)
            with self.subTest(field=field), patch.object(presentation, "option_text", side_effect=omit):
                self.assertIn(code, {d["code"] for d in coverage.propagation_diagnostics(record)})

    def test_repeated_presentation_and_search_do_not_mutate_migrated_data(self):
        original = deepcopy(self.profiles)
        for name, flag in (("psql", "--port"), ("sftp", "-B"), ("yq-eval", "--indent"), ("dotnet-build", "--runtime")):
            self.assert_accessible(name, flag, [], search_only=[self.node(name, flag)["applicability"]["version"]["values"][0]])
            self.assert_accessible(name, flag, [self.node(name, flag)["meaning"]])
        self.assertEqual(self.profiles, original)


if __name__ == "__main__":
    unittest.main()
