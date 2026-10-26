"""Verify passive operand recovery and source-scoped manual association.

Real expectations use unchanged captures and their recorded provenance. Generic
specimens exercise formatting rules, not command-specific compatibility claims.
"""

from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "cli_help"), str(ROOT / "tests"), str(ROOT / "scripts")]
import discovery
import inventory_numerical_descriptions as inventory
from core import Context, HelpError, find_context, insert_option
from drivers import parse_driver
from manual_import import ManualCollection, import_manual
from bulk_scan import scan_record
from diagnostics import inspect_cache
import presentation


def options(profile):
    """Index literal active options without deriving aliases from shared prose."""
    return {o["flag"]: o for c in profile["categories"] for o in c["options"]}


class ParserAssociationTests(unittest.TestCase):
    def setUp(self):
        parent = (ROOT / ".cache/parser-association-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.folder = parent / uuid.uuid4().hex
        self.folder.mkdir()
        if self.folder.resolve().parent != parent or self.folder.is_symlink():
            raise RuntimeError("Disposable directory left its selected parent")
        self.addCleanup(shutil.rmtree, self.folder)
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                     "socket.create_connection", "socket.getaddrinfo", "urllib.request.urlopen",
                     "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(name, side_effect=AssertionError("Passive test attempted execution or network access")))

    def capture(self, name):
        return (ROOT / "tests/fixtures/help" / name).read_text(encoding="utf-8")

    def test_comma_choices_keep_complete_operands_and_following_aliases(self):
        text = "Options:\n  --lfnf={all,none}, --last-failed-no-failures={all,none}  Choose a policy"
        parsed = options(discovery.build_profile("specimen", [("fixture", text)]))
        self.assertEqual(set(parsed), {"--lfnf=", "--last-failed-no-failures="})
        for option in parsed.values():
            self.assertEqual(option["argument"], "{all,none}")
            self.assertEqual(option["summary"], "Choose a policy")
        for operand in ("<first,second>", "[first,second]", "{first,second}"):
            parsed = options(discovery.build_profile("specimen", [("fixture",
                f"--first={operand}, --second={operand}  Retained description")]))
            self.assertEqual(set(parsed), {"--first=", "--second="})
            self.assertTrue(all(o["argument"] == operand for o in parsed.values()))

    def test_shared_equals_alias_retains_psql_variable_declaration(self):
        profile = discovery.build_profile("psql", [("fixture", self.capture("followup-systems/psql.txt"))])
        parsed = options(profile)
        for flag in ("-v", "--set=", "--variable="):
            self.assertIn(flag, parsed)
            self.assertEqual(parsed[flag]["argument"], "NAME=VALUE")
            self.assertNotIn("--variable=", parsed[flag]["summary"])

    def test_mirrored_lowercase_operands_and_quoted_alias_annotations_survive(self):
        parsed = options(discovery.build_profile("sed", [("fixture", self.capture("workflow-sed.txt"))]))
        for flag, argument in (("-e", "script"), ("--expression=", "script"),
                               ("-f", "script-file"), ("--file=", "script-file")):
            self.assertEqual(parsed[flag]["argument"], argument)
        parsed = options(discovery.build_profile("psql", [("fixture", self.capture("followup-systems/psql.txt"))]))
        for flag in ("-1", "--single-transaction"):
            self.assertEqual(parsed[flag]["argument"], "")
            self.assertIn('("one")', parsed[flag]["detail"])
            self.assertIn("execute as a single transaction", parsed[flag]["detail"])

    def test_trailing_declaration_comma_is_not_description_prose(self):
        parsed = options(discovery.build_profile("specimen", [("fixture",
            "Options:\n  --first, --second,\n      Retained continuation description")]))
        self.assertEqual(set(parsed), {"--first", "--second"})
        self.assertTrue(all(o["summary"] == "Retained continuation description" for o in parsed.values()))

    def borrowed(self, marker="COMMON OPTIONS"):
        """Use unrelated names and flags to rule out target-specific selection."""
        return ("REFERENCE-ENGINE(1)\n\nNAME\n  reference-engine - describe an engine\n\n" + marker + "\n"
                "  -a, --appearance MODE  Select appearance\n\nSPECIFIC OPTIONS\n"
                "  --engine-only VALUE  Available only for the engine's private state\n")

    def test_compound_optional_and_multiple_operand_declarations(self):
        cases = [
            ("  --quota <amount>[<suffix>]  Select a quota", "<amount>[<suffix>]", False, 1),
            ("  --quota [<amount>[<suffix>]]  Select a quota", "[<amount>[<suffix>]]", True, 1),
            ("  --quota [<amount>][/<other>]  Select a quota", "[<amount>][/<other>]", True, 1),
            ("  --quota[=<amount>[<suffix>]]  Select a quota", "[=<amount>[<suffix>]]", True, 1),
            ("  --items[=<first,second,...>]  Select one list value", "[=<first,second,...>]", True, 1),
            ("  --quota=<amount>[<suffix>]  Select a quota", "<amount>[<suffix>]", False, 1),
            ("  --pair <left> <right>  Select a pair", "<left> <right>", False, 2),
            ("  --quantity <integer [0 .. 512]>  Select a value", "<integer [0 .. 512]>", False, 1),
        ]
        for line, argument, optional, count in cases:
            with self.subTest(line=line):
                option = discovery.parse_option_line(line)[0][0]
                self.assertEqual(option["argument"], argument)
                self.assertEqual(option["argument_optional"], optional)
                self.assertEqual(option.get("argument_count", 1), count)
                self.assertNotIn("value_semantics", option)

    def test_bracketed_prose_and_unbalanced_text_do_not_become_values(self):
        for line in ("  --flag  [A note about output]", "  --flag  Print <amount>[<suffix>] literally"):
            self.assertEqual(discovery.parse_option_line(line)[0][0]["argument"], "")
        self.assertIsNone(discovery.placeholder_prefix("<amount>[<suffix>"))
        self.assertIsNone(discovery.placeholder_prefix("[missing"))
        self.assertIsNone(discovery.placeholder_prefix("<command>..."))
        self.assertIsNone(discovery.placeholder_prefix("[username[:password]]"))
        self.assertIsNone(discovery.placeholder_prefix("[address:]port"))
        self.assertEqual(discovery.placeholder_prefix("[PREFIX]VALUE rest"), ("[PREFIX]VALUE", False))

    def test_alias_operand_recovery_and_wrapped_details_keep_adjacent_flags(self):
        text = ("OPTIONS\n  -q, --quota <amount>[<suffix>]  Select an amount\n"
                "      whose suffix is documented by its source.\n  --quiet  Avoid progress output\n")
        profile = discovery.build_profile("specimen", [("supplied help", text)])
        for flag in ("-q", "--quota"):
            self.assertEqual(options(profile)[flag]["argument"], "<amount>[<suffix>]")
            self.assertIn("suffix is documented", options(profile)[flag]["detail"])
        self.assertFalse(options(profile)["--quiet"]["argument"])

    def test_captured_aws_exclusion_description_preserves_its_opening(self):
        """Spacing inside the captured prose must not discard its opening words."""
        captured = json.loads(self.capture("captured.json"))["aws s3 sync"]["text"]
        profile = discovery.build_profile(["aws", "s3", "sync"], [("captured help", captured)])
        option = options(profile)["--exclude"]
        self.assertEqual(option["argument"], "(string)")
        self.assertEqual(" ".join(option["summary"].split()),
                         "Exclude all files or objects from the command that")
        self.assertIn("matches the specified pattern.", option["detail"])
        self.assertIn("Exclude all files or objects from the", option["detail"])

    def test_description_spacing_preserves_aliases_values_and_continuations(self):
        """Prose spacing cannot change explicit operands or lose description text."""
        cases = [
            ("--select (string)", ["--select"], "(string)", False),
            ("-s, --select FILE", ["-s", "--select"], "FILE", False),
            ("--select[=WHEN]", ["--select"], "[=WHEN]", True),
            ("--select <left> <right>", ["--select"], "<left> <right>", False),
        ]
        for declaration, flags, argument, optional in cases:
            for boundary in (" ", "  ", "\t"):
                for spacing in (" ", "  ", "\t"):
                    with self.subTest(declaration=declaration, boundary=boundary, spacing=spacing):
                        text = ("Options:\n  " + declaration + boundary + "Select records from the"
                                + spacing + "source.\n      Preserve the continuation.\n"
                                "  --quiet  Suppress progress.\n")
                        parsed = options(discovery.build_profile("specimen", [("fixture", text)]))
                        self.assertEqual(set(parsed), {*flags, "--quiet"})
                        for flag in flags:
                            option = parsed[flag]
                            self.assertEqual(option["argument"], argument)
                            self.assertEqual(option["argument_optional"], optional)
                            self.assertEqual(option.get("argument_count", 1), 2 if "<right>" in argument else 1)
                            self.assertEqual(" ".join(option["summary"].split()), "Select records from the source.")
                            self.assertIn("Preserve the continuation.", option["detail"])

    def test_option_mentions_in_prose_are_preserved_without_becoming_aliases(self):
        """A flag reference, including one after a comma, remains description text."""
        for prose in ("Use --verbose for details.", "Use --verbose or --quiet for output.",
                      "For more detail, --verbose is available.",
                      "Use normal output or --quiet for silence.", "Use normal output | --quiet for silence."):
            for boundary in (" ", "  ", "\t"):
                with self.subTest(prose=prose, boundary=boundary):
                    declaration = "  -s, --select FILE" + boundary + prose + "  Keep this sentence."
                    entries, summary = discovery.parse_option_line(declaration)
                    self.assertEqual([o["flag"] for o in entries], ["-s", "--select"])
                    self.assertTrue(all(o["argument"] == "FILE" for o in entries))
                    self.assertEqual(" ".join(summary.split()), prose + " Keep this sentence.")

    def test_unrecognized_tail_remains_prose_not_an_inferred_argument(self):
        """An unrecognized tail is preserved instead of discarded at alignment."""
        entries, summary = discovery.parse_option_line("  --quiet Suppress progress  while copying.")
        self.assertEqual(entries, [{"flag": "--quiet", "argument": "", "argument_optional": False}])
        self.assertEqual(" ".join(summary.split()), "Suppress progress while copying.")
        entries, summary = discovery.parse_option_line("  --select FILE suppress progress  while copying.")
        self.assertEqual(entries[0]["argument"], "FILE")
        self.assertEqual(" ".join(summary.split()), "suppress progress while copying.")

    def test_pre_description_repair_cache_is_rejected_and_new_text_roundtrips(self):
        """Old parsed descriptions cannot be reused under the repaired parser identity."""
        profile = discovery.build_profile("specimen", [("fixture", "--select FILE Select the  source.")])
        old_identity = {"command": ["specimen"], "version": 13}
        identity = {"command": ["specimen"], "version": discovery.CACHE_VERSION}
        path = self.folder / "description-cache.json"
        discovery.write_cache(path, old_identity, profile)
        self.assertIsNone(discovery.read_cache(path, identity, 60))
        discovery.write_cache(path, identity, profile)
        loaded = discovery.read_cache(path, identity, 60)
        self.assertEqual(" ".join(options(loaded)["--select"]["summary"].split()), "Select the source.")

    def test_podman_capture_recovers_required_memory_operands_and_literal_edits(self):
        path = ROOT / "tests/fixtures/help/followup-systems/podman-run.txt"
        original = path.read_bytes()
        profile = discovery.build_profile(["podman", "run"], [("captured help", original.decode("utf-8"))])
        for flag in ("--memory", "-m", "--memory-reservation"):
            option = options(profile)[flag]
            self.assertEqual(option["argument"], "<number>[<unit>]")
            self.assertFalse(option["argument_optional"])
            self.assertEqual(option.get("argument_count", 1), 1)
            self.assertIn("kibibytes", option["detail"])
            self.assertNotIn("value_semantics", option)
        line = 'podman run --mem image "private value"'
        context = find_context(line, len("podman run --mem"), [profile])
        edited, point = insert_option(context, options(profile)["--memory"])
        self.assertEqual(edited, 'podman run --memory image "private value"')
        self.assertEqual(point, len("podman run --memory "))
        self.assertEqual(path.read_bytes(), original)

    def test_sftp_nested_flags_remain_context_and_cannot_be_inserted_as_root(self):
        profile = discovery.build_profile("sftp", [("man sftp", self.capture("sftp.txt"))])
        self.assertNotIn("-1", options(profile))
        self.assertEqual(options(profile)["-l"]["argument"], "limit")
        self.assertEqual(options(profile)["-R"]["argument"], "num_requests")
        shared = profile["documentation"]["shared"]
        self.assertTrue(any("ls [-1afhlnrSt]" in p["text"] and not p["options"] for p in shared))
        selected = options(profile)["-l"]
        view = presentation.option_text(profile, profile["categories"][0], selected)
        self.assertIn("single columnar", "\n".join(view.details))
        self.assertNotIn("single columnar", view.searchable)
        context = Context("sftp ", 5, 5, 5, "", profile)
        with self.assertRaisesRegex(HelpError, "absent"):
            insert_option(context, {"flag": "-1", "argument": "", "summary": "Nested only"})

    def test_generic_nested_section_resumes_at_later_root_options(self):
        text = ("OPTIONS\n  --before N  A root operand\n\nINTERACTIVE COMMANDS\n"
                "  browse [--nested]\n      --nested  Internal browse flag\n"
                "      --before  Different nested meaning\n\nMORE OPTIONS:\n"
                "  --after  Another root action\n")
        document = discovery.parse_help_document(text, "specimen")
        self.assertEqual({o["flag"] for o in document["options"]}, {"--before", "--after"})
        self.assertTrue(any("--nested" in p["text"] and not p["options"] for p in document["shared"]))
        self.assertNotIn("Internal browse", next(o for o in document["options"] if o["flag"] == "--before")["detail"])

    def test_separate_alias_pairs_do_not_share_targeted_documentation(self):
        text = ("OPTIONS\n  -7 --first, -8 --second, -9 --third\n      Select the documented choice.\n\n"
                "The units for --first are described separately.\n")
        groups = discovery.parse_option_groups("  -7 --first, -8 --second, -9 --third")
        self.assertEqual([[o["flag"] for o in pair] for pair, _ in groups],
                         [["-7", "--first"], ["-8", "--second"], ["-9", "--third"]])
        parsed = discovery.parse_help_document(text, "specimen")
        for option in parsed["options"]:
            self.assertEqual("The units for" in option["detail"], option["flag"] in {"-7", "--first"})

    def test_git_capture_keeps_common_diff_formatting_and_inactive_specific_selectors(self):
        captured = json.loads(self.capture("expansion-development-captured.json"))["git stash show"]
        text, request = captured["text"], captured["source"]
        profile = discovery.build_profile(["git", "stash", "show"], [("man git-diff", text)],
                                         source_requests={"man git-diff": request},
                                         source_scopes={"man git-diff": "common_options"})
        self.assertTrue({"-p", "--stat"} <= options(profile).keys())
        self.assertTrue({"-0", "-1", "--base", "-2", "--ours", "-3", "--theirs"}.isdisjoint(options(profile)))
        source = profile["documentation"]["sources"][0]["documentation"]["provenance"]
        self.assertEqual(source["requested_command"], ["git", "stash", "show"])
        self.assertEqual(source["source_manual"], "GIT-DIFF")
        self.assertEqual(source["source_request"], request)
        self.assertTrue(source["scope_mismatch"])
        category = next(c for c in profile["categories"] if options(profile)["--stat"] in c["options"])
        view = presentation.option_text(profile, category, options(profile)["--stat"])
        self.assertIn("Only its declared common/shared option section is active", "\n".join(view.details))
        retained = "\n".join(p["text"] for p in profile["documentation"]["shared"] if not p["options"])
        self.assertIn("-1 --base, -2 --ours, -3 --theirs", retained)
        self.assertIn("Can be used only when comparing the working tree", " ".join(retained.split()))
        native = discovery.parse_command_help(text, "man git-diff", ["git", "diff"], request)
        self.assertTrue({"--base", "--ours", "--theirs"} <= {o["flag"] for o in native["options"]})

    def test_common_section_and_wrapped_closing_marker_are_generic(self):
        for text in (self.borrowed(), self.borrowed().replace("COMMON OPTIONS", "OPTIONS").replace(
                "\nSPECIFIC OPTIONS", "\nFor details on these common\noptions, consult the reference.\n\nSPECIFIC OPTIONS")):
            with self.subTest(text=text):
                profile = discovery.build_profile(["unrelated", "view"], [("man reference-engine", text)],
                                                  source_scopes={"man reference-engine": "common_options"})
                self.assertEqual(set(options(profile)), {"-a", "--appearance"})
                self.assertTrue(any(d["code"] == "manual_source_scope" for d in profile["documentation"]["diagnostics"]))

    def test_unassigned_foreign_source_survives_beside_native_help_without_rebinding(self):
        foreign = "FOREIGN(1)\n\nOPTIONS\n  --choice UNIT  A foreign interpretation\n  --foreign-only  Another action\n"
        profile = discovery.build_profile("native", [("native --help", "OPTIONS\n  --choice NAME  A native name\n"),
                                                     ("man foreign", foreign)], source_scopes={"man foreign": "common_options"})
        self.assertEqual(set(options(profile)), {"--choice"})
        self.assertEqual(options(profile)["--choice"]["argument"], "NAME")
        self.assertNotIn("foreign interpretation", options(profile)["--choice"]["detail"])
        self.assertTrue(any("foreign interpretation" in p["text"] for p in profile["documentation"]["shared"]))
        self.assertEqual(profile["documentation"]["sources"][-1]["documentation"]["provenance"]["manual_lookup"], "foreign")
        inferred = discovery.build_profile("native", [("man foreign", foreign)])
        self.assertIn("--foreign-only", options(inferred))
        self.assertTrue(any(n["code"] == "manual_source_scope_unverified" for n in inferred["documentation"]["diagnostics"]))
        self.assertTrue(any("applicability is unverified" in p["text"] for p in inferred["documentation"]["shared"]))

    def test_unscoped_foreign_manual_retains_legacy_merge_inventory(self):
        profile = discovery.build_profile("native", [("native --help", "OPTIONS\n  --name NAME  Select a name\n"),
            ("man foreign", "FOREIGN(1)\n\nOPTIONS\n  --other VALUE  Complementary declaration\n")])
        self.assertEqual(set(options(profile)), {"--name", "--other"})
        self.assertTrue(any(n["code"] == "manual_source_scope_unverified" for n in profile["documentation"]["diagnostics"]))

    def test_root_commands_heading_is_not_an_interactive_section(self):
        profile = discovery.build_profile("specimen", [("help", "Commands:\n  --flush  Flush data\n  --rotate  Rotate data\n")])
        self.assertEqual(set(options(profile)), {"--flush", "--rotate"})

    def test_whole_manual_borrowing_preserves_legacy_options_with_qualification(self):
        captured = json.loads(self.capture("expansion-development-captured.json"))["git stash list"]
        profile = discovery.build_profile(["git", "stash", "list"], [("man git-log", captured["text"])],
                                         source_requests={"man git-log": captured["source"]})
        self.assertIn("--author=", options(profile))
        self.assertIn("--graph", options(profile))
        self.assertTrue(any(n["code"] == "manual_source_scope_unverified" for n in profile["documentation"]["diagnostics"]))

    def test_unmapped_text_import_keeps_legacy_use_and_exposes_title_uncertainty(self):
        profile = discovery.build_profile("chosen-name", [("Imported manual text: supplied.txt",
                                          "CANONICAL(1)\n\nOPTIONS\n  --flag  A supplied action\n")])
        self.assertIn("--flag", options(profile))
        self.assertTrue(any(n["code"] == "manual_title_review" for n in profile["documentation"]["diagnostics"]))

    def test_qualified_documents_and_recovered_operands_survive_cache_without_mutation(self):
        text = self.borrowed().replace("MODE", "<amount>[<unit>]")
        profile = discovery.build_profile("consumer", [("man reference-engine", text)],
                                          source_scopes={"man reference-engine": "common_options"})
        original = deepcopy(profile)
        identity = {"command": ["consumer"], "version": discovery.CACHE_VERSION}
        cache = self.folder / "cache.json"
        discovery.write_cache(cache, identity, profile)
        loaded = discovery.read_cache(cache, identity, 60)
        self.assertEqual(loaded, profile)
        self.assertEqual(profile, original)
        self.assertEqual(options(loaded)["--appearance"]["argument"], "<amount>[<unit>]")
        previous = json.loads(cache.read_text(encoding="utf-8"))
        previous["identity"]["version"] -= 1
        cache.write_text(json.dumps(previous), encoding="utf-8")
        self.assertIsNone(discovery.read_cache(cache, identity, 60))

    def test_discovery_uses_same_fixed_request_and_current_cache_generation(self):
        executable, renderer = self.folder / "consumer", self.folder / "man"
        executable.write_text("Inert identity fixture, never executed", encoding="utf-8")
        renderer.write_text("Inert renderer identity fixture, never executed", encoding="utf-8")
        _, driver = parse_driver({"command": "consumer", "paths": [
            {"command": ["view"], "help": [], "man": "reference-engine", "manual_scope": "common_options"}]})
        settings = discovery.Settings(mode="man", cache_dir=self.folder / "discovery-cache")
        def which(name):
            return str(renderer if name == "man" else executable)
        with patch("discovery.shutil.which", side_effect=which), patch("discovery.run_probe", return_value=self.borrowed()) as probe:
            cold = discovery.discover("consumer", settings, subcommands=("view",), driver_registry={"consumer": driver})
            self.assertNotIn("--engine-only", options(cold))
            self.assertEqual(probe.call_count, 1)
            request = probe.call_args.args[0]
            self.assertEqual(request[-2:], ["--", "reference-engine"])
            self.assertEqual(cold["documentation"]["sources"][0]["documentation"]["provenance"]["source_request"], request)
            probe.reset_mock()
            warm = discovery.discover("consumer", settings, subcommands=("view",), driver_registry={"consumer": driver})
            probe.assert_not_called()
            self.assertEqual(cold, warm)
            report, _ = inspect_cache(["consumer", "view"], "consumer",
                                      SimpleNamespace(module=None, interpreter_options=()), settings, {"consumer": driver})
            self.assertEqual(report["status"], "available")

    def test_scope_validation_and_cache_identity_are_additive(self):
        route = {"command": ["view"], "help": [], "man": "reference-engine"}
        _, legacy = parse_driver({"command": "consumer", "paths": [route]})
        self.assertIsNone(legacy.paths[("view",)].manual_scope)
        for value in (None, "all", True, {}, ["common_options"]):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "manual_scope"):
                parse_driver({"command": "consumer", "paths": [{**route, "manual_scope": value}]})
        with self.assertRaisesRegex(ValueError, "manual_scope"):
            parse_driver({"command": "consumer", "paths": [{**route, "man": None, "help": ["--help"], "manual_scope": "common_options"}]})
        executable = self.folder / "inert"
        executable.write_text("No execution", encoding="utf-8")
        settings = discovery.Settings(cache_dir=self.folder)
        old = discovery.cache_identity(["consumer", "view"], str(executable), [], "reference-engine", None, settings)
        scoped = discovery.cache_identity(["consumer", "view"], str(executable), [], "reference-engine", None,
                                          settings, manual_scope="common_options")
        self.assertNotEqual(old, scoped)
        self.assertEqual({k: v for k, v in scoped.items() if k != "manual_scope"}, old)

    def test_collection_preserves_declared_scope_and_missing_scope_sections_fail_closed(self):
        _, driver = parse_driver({"command": "consumer", "paths": [{"command": ["view"], "help": [],
                                  "man": "reference-engine", "manual_scope": "common_options"}]})
        with ManualCollection(self.folder / "scoped-collection") as collection, patch(
                "bulk_scan.read_manual", return_value=(self.borrowed(), "man reference-engine", "reference-engine")):
            record = scan_record({"command": ["consumer", "view"], "manual": "reference-engine"}, collection,
                                 {"consumer": driver}, 1, False)
        self.assertTrue(record["generated"], record)
        document = json.loads(Path(record["driver"]).read_text(encoding="utf-8"))
        self.assertEqual(document["paths"][0]["manual_scope"], "common_options")
        profile = json.loads(Path(record["profile"]).read_text(encoding="utf-8"))
        self.assertNotIn("--engine-only", options(profile))
        replacement = self.folder / "replacement.txt"
        replacement.write_text(self.borrowed(), encoding="utf-8")
        saved = import_manual(["consumer", "view"], self.folder / "scoped-collection",
                              manual="reference-engine", text_file=replacement, replace=True)
        reloaded = json.loads(Path(saved["profile"]).read_text(encoding="utf-8"))
        self.assertNotIn("--engine-only", options(reloaded))
        self.assertEqual(json.loads(Path(saved["driver"]).read_text(encoding="utf-8"))["paths"][0]["manual_scope"], "common_options")
        with self.assertRaisesRegex(HelpError, "No applicable root"):
            discovery.build_profile("consumer", [("man reference-engine", "REFERENCE-ENGINE(1)\n\nOPTIONS\n  --specific  Action\n")],
                                    source_scopes={"man reference-engine": "common_options"})

    def test_import_and_mocked_collection_transforms_retain_the_recovered_operand(self):
        text = self.capture("followup-systems/podman-run.txt")
        source = self.folder / "supplied-help.txt"
        source.write_text(text, encoding="utf-8")
        saved = import_manual(["podman", "run"], self.folder / "imported", text_file=source)
        imported = json.loads(Path(saved["profile"]).read_text(encoding="utf-8"))
        self.assertEqual(options(imported)["--memory"]["argument"], "<number>[<unit>]")
        with ManualCollection(self.folder / "collected") as collection, patch("bulk_scan.read_manual", return_value=(text, "man podman-run", "podman-run")):
            record = scan_record({"command": ["podman", "run"], "manual": "podman-run"}, collection, {}, 1, False)
        self.assertTrue(record["generated"], record)
        collected = json.loads(Path(record["profile"]).read_text(encoding="utf-8"))
        self.assertEqual(options(collected)["--memory"]["argument"], "<number>[<unit>]")

    def test_repeated_parsing_is_deterministic_and_preserves_capture_bytes(self):
        paths = [ROOT / "tests/fixtures/help/sftp.txt", ROOT / "tests/fixtures/help/followup-systems/podman-run.txt"]
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertEqual(discovery.parse_help_document(text, "source"), discovery.parse_help_document(text, "source"))
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    def test_inventory_locations_follow_each_repeated_source_declaration(self):
        text = "OPTIONS\n  --format FIRST  First meaning\n\nMORE OPTIONS:\n  --format SECOND  Second meaning\n"
        reader = inventory.Inventory(self.folder)
        reader.help_text(text, ("specimen",), {"path": "tests/fixtures/help/repeated.txt"}, "fixture_help", {})
        entry = reader.entries["option|specimen|--format"]
        self.assertEqual({(o["option"]["argument"], o["source"]["line"]) for o in entry["observations"]},
                         {("FIRST", 2), ("SECOND", 5)})

    def test_actual_captures_round_trip_with_source_scope_and_original_sections(self):
        captured = json.loads(self.capture("expansion-development-captured.json"))["git stash show"]
        cases = [(["podman", "run"], "captured help", self.capture("followup-systems/podman-run.txt"), None),
                 (["sftp"], "man sftp", self.capture("sftp.txt"), None),
                 (["git", "stash", "show"], "man git-diff", captured["text"], "common_options")]
        for command, label, text, scope in cases:
            with self.subTest(command=command):
                profile = discovery.build_profile(command, [(label, text)], source_scopes={label: scope} if scope else {})
                identity = {"version": discovery.CACHE_VERSION, "command": command}
                if scope:
                    identity["manual_scope"] = scope
                cache = self.folder / ("-".join(command) + ".json")
                discovery.write_cache(cache, identity, profile)
                loaded = discovery.read_cache(cache, identity, 60)
                self.assertEqual(loaded, profile)
                if scope:
                    source_only = [p for p in loaded["documentation"]["shared"] if "-1 --base" in p["text"]]
                    self.assertTrue(source_only)
                    self.assertTrue(all("(Options)" in p["section"] for p in source_only))


if __name__ == "__main__":
    unittest.main()
