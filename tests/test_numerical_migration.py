"""Check the opt-in bundled migration against source-reviewed reference facts.

Only entries already carrying metadata are selected for completeness checks.
This is not an inventory-wide gate or a test of installed target programs.
"""

from contextlib import ExitStack
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import Context, insert_option, validate_profile
from value_semantics import (
    ValueContext, format_value_semantics, validate_profile_semantics,
    validate_value_semantics,
)


class NumericalMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Read authored data and the separate evidence fixture without discovery."""
        cls.profiles = {path.stem: json.loads(path.read_text(encoding="utf-8"))
                        for path in sorted((ROOT / "profiles").glob("*.json"))}
        cls.evidence = json.loads((ROOT / "tests/fixtures/value-semantics/migration-evidence.json")
                                  .read_text(encoding="utf-8"))
        cls.sources = cls.evidence["sources"]

    def option(self, profile, flag):
        return next(option for category in self.profiles[profile]["categories"]
                    for option in category["options"] if option["flag"] == flag)

    def nodes(self, profile, metadata):
        """Expand explicitly declared top-level references for reference assertions."""
        definitions = self.profiles[profile].get("value_definitions", {})
        return [definitions[node["ref"]] if "ref" in node else node
                for node in metadata["variants"]]

    def node(self, profile, flag, chip=None):
        nodes = self.nodes(profile, self.option(profile, flag)["value_semantics"])
        if chip:
            nodes = [node for node in nodes
                     if chip in node["applicability"]["chip"].get("values", [])]
        self.assertEqual(len(nodes), 1, (profile, flag, chip))
        return nodes[0]

    @staticmethod
    def form(node, identity):
        return next(form for form in node["forms"] if form["id"] == identity)

    def selected(self):
        """Enumerate only explicit opt-in fields, including positional contracts."""
        for name, profile in self.profiles.items():
            for ci, category in enumerate(profile["categories"]):
                for oi, option in enumerate(category["options"]):
                    if "value_semantics" not in option:
                        continue
                    context = ValueContext(
                        source=f"profiles/{name}.json", command=tuple(profile["command"]),
                        option=option["flag"], pointer=f"/categories/{ci}/options/{oi}/value_semantics",
                        argument_count=option.get("argument_count", 1) if option.get("argument") else 0,
                        value_optional=option.get("argument_optional", False))
                    yield name, profile, option["value_semantics"], context
            if "positional_value_semantics" in profile:
                group = profile["positional_group"]
                yield name, profile, profile["positional_value_semantics"], ValueContext(
                    source=f"profiles/{name}.json", command=tuple(profile["command"]),
                    option="<positional_group>", pointer="/positional_value_semantics",
                    argument_count=group["argument_count"], value_optional=False)

    def explanations(self, profile, flag):
        document = self.profiles[profile]
        return "\n".join(format_value_semantics(self.option(profile, flag)["value_semantics"],
                                              definitions=document.get("value_definitions")))

    def assert_unit(self, form, base, multiplier, per=None):
        self.assertEqual(form["unit"]["base"], base)
        self.assertEqual(Decimal(form["unit"]["multiplier"]), Decimal(multiplier))
        self.assertEqual(form["unit"].get("per"), per)

    def test_selected_verified_content_and_legacy_profiles(self):
        for name, profile in self.profiles.items():
            with self.subTest(profile=name):
                validate_profile(profile, Path(f"profiles/{name}.json"))
                self.assertEqual(validate_profile_semantics(profile, source=f"profiles/{name}.json"), ())
        self.assertTrue(any("value_semantics" not in option for profile in self.profiles.values()
                            for category in profile["categories"] for option in category["options"]))
        for name, profile, metadata, context in self.selected():
            nodes = self.nodes(name, metadata)
            verified = all(node["review"]["status"] == "verified" for node in nodes)
            diagnostics = validate_value_semantics(metadata, mode="maintained" if verified else "external",
                                                   context=context, definitions=profile.get("value_definitions"))
            with self.subTest(profile=name, option=context.option):
                self.assertFalse([d.to_dict() for d in diagnostics if d.severity == "error"])
                if verified:
                    self.assertEqual(diagnostics, ())
                    for node in nodes:
                        self.assertEqual(node["applicability"]["version"]["state"], "known")
                else:
                    self.assertIn("sem_review_required", {d.code for d in diagnostics})

    def test_reference_scales_distinguish_rsync_openssh_and_ffmpeg(self):
        rsync = self.node("rsync", "--bwlimit=")
        self.assert_unit(self.form(rsync, rsync["bare"]["form"]), "byte",
                         self.sources["rsync"]["bare_bytes_per_second"], "second")
        self.assert_unit(self.form(rsync, "binary-k"), "byte", self.sources["rsync"]["binary_k"], "second")
        self.assert_unit(self.form(rsync, "decimal-k"), "byte", self.sources["rsync"]["decimal_kb"], "second")
        self.assertEqual(self.form(rsync, "binary-k")["case"], "insensitive")
        self.assertIn("0", {value["value"] for value in self.form(rsync, "kibibytes")["special_values"]})
        for profile in ("scp", "sftp"):
            ssh = self.node(profile, "-l")
            value = self.form(ssh, ssh["bare"]["form"])
            self.assert_unit(value, "bit", self.sources["openssh"]["bare_bits_per_second"], "second")
            self.assertEqual(value["bounds"], {"min": self.sources["openssh"]["minimum"],
                                              "max": self.sources["openssh"]["maximum"]})
            self.assertEqual({form["notation"] for form in ssh["forms"]}, {"number"})
            self.assertIn("Zero is invalid", self.option(profile, "-l")["detail"])
        for flag in ("-b:v", "-b:a"):
            node = self.node("ffmpeg", flag)
            self.assert_unit(self.form(node, "bits"), self.sources["ffmpeg_bitrate"]["base"], "1", "second")
            self.assert_unit(self.form(node, "k"), "bit", self.sources["ffmpeg_number"]["k"], "second")
            self.assert_unit(self.form(node, "ki"), "bit", self.sources["ffmpeg_number"]["ki"], "second")
            self.assert_unit(self.form(node, "bytes"), "bit", self.sources["ffmpeg_number"]["byte_to_bits"], "second")
            self.assert_unit(self.form(node, "mib"), "bit", str(1024 ** 2 * 8), "second")

    def test_time_scales_explicit_units_and_literal_zero(self):
        for flag in ("-ss", "-t"):
            node = self.node("ffmpeg", flag)
            for form, field in (("seconds", "seconds"), ("ms", "milliseconds"), ("us", "microseconds")):
                self.assert_unit(self.form(node, form), "second", self.sources["ffmpeg_time"][field])
            self.assertEqual(node["bare"]["state"], "accepted")
        timeout = self.node("go-test", "-timeout")
        self.assertEqual(timeout["bare"]["state"], "not_accepted")
        for form, field in (("ns", "nanoseconds"), ("us", "microseconds"), ("ms", "milliseconds"),
                            ("m", "minutes"), ("h", "hours")):
            self.assert_unit(self.form(timeout, form), "second", self.sources["go_duration"][field])
        self.assertEqual(set(self.form(timeout, "us")["tokens"]), {"us", "µs", "μs"})
        self.assertIn(self.sources["go_test"]["default_timeout"] + self.sources["go_test"]["default_timeout_form"],
                      timeout["when_absent"]["meaning"])
        zero = next(form for form in timeout["forms"] if "0" in form.get("tokens", []))
        self.assertTrue(zero["sentinel"])
        self.assertNotIn("unit", zero)
        self.assertIn("compound", {form["id"] for form in timeout["forms"]})
        self.assertTrue(self.sources["go_alarm"]["nonpositive_disables_alarm"])
        self.assertIn("nonpositive", self.form(timeout, "compound")["grammar"].lower())
        self.assertIn("negative unit-bearing durations", self.option("go-test", "-timeout")["detail"])
        self.assertIn(self.sources["go_alarm"]["url"], {reference["source"] for reference in timeout["review"]["references"]})

    def test_literal_flash_tokens_have_actual_scale_and_chip_limits(self):
        for profile, suffix, source in (("esptool-write-flash", "-", "esptool5"),
                                        ("esptool.py-write-flash", "-", "esptool5"),
                                        ("esptool.py-write_flash", "_", "esptool4")):
            size = self.node(profile, "--flash" + suffix + "size", "ESP32")
            value = next(form for form in size["forms"] if "4MB" in form.get("tokens", []))
            self.assert_unit(value, "byte", str(4 * int(self.sources[source]["bytes_per_MB"])))
            self.assertEqual(value["case"], "sensitive")
            self.assertEqual(size["bare"]["state"], "not_accepted")
            self.assertEqual(size["applicability"]["version"]["values"], [self.sources[source]["version"]])
            c2 = self.node(profile, "--flash" + suffix + "freq", "ESP32-C2")
            self.assertNotIn("40m", [token for form in c2["forms"] for token in form.get("tokens", [])])
            self.assert_unit(next(form for form in c2["forms"] if "60m" in form.get("tokens", [])),
                             "hertz", str(60 * int(self.sources[source]["hertz_per_m"])))
            self.assertTrue(all(node["applicability"]["chip"]["state"] == "known"
                                for node in self.nodes(profile, self.option(profile, "--flash" + suffix + "size")["value_semantics"])))

    def test_counts_indices_levels_percentages_and_defaults(self):
        durations = self.node("pytest", "--durations")
        self.assertEqual(durations["kind"], "count")
        self.assertNotIn("unit", durations["forms"][0])
        self.assertIn("0", {item["value"] for item in durations["forms"][0]["special_values"]})
        nth = self.node("fzf", "--nth")
        self.assertEqual(nth["origin"], self.sources["fzf"]["origin"])
        self.assertEqual(nth["bare"]["state"], "accepted")
        self.assertIn("-1", self.option("fzf", "--nth")["detail"])
        height = self.node("fzf", "--height")
        percent = self.form(height, "percentage")
        self.assert_unit(percent, "ratio", self.sources["fzf"]["percentage"])
        self.assertEqual(percent["unit"]["relative_to"], "terminal height")
        for form in ("inverse-percent", "adaptive-percent"):
            self.assert_unit(self.form(height, form), "ratio", self.sources["fzf"]["percentage"])
        priority = self.node("journalctl", "--priority=")
        self.assertEqual(priority["kind"], "level")
        self.assertEqual(priority["forms"][0]["bounds"], {"min": self.sources["journal"]["priority_min"],
                                                       "max": self.sources["journal"]["priority_max"]})
        self.assertIn("Lower numerical levels", priority["ordering"])
        self.assertIn("greater severity", priority["ordering"])
        boot = self.node("journalctl", "--boot=")
        self.assertEqual(boot["kind"], "identifier")
        self.assertIn("current boot", boot["when_value_omitted"]["meaning"])
        self.assertIn("newest", self.option("journalctl", "--boot=")["detail"])
        for profile in ("pio-device-monitor", "platformio-device-monitor"):
            baud = self.node(profile, "--baud")
            self.assert_unit(baud["forms"][0], "baud", "1")
            self.assertIn(self.sources["platformio"]["baud_default"], baud["when_absent"]["meaning"])
        ruff = self.node("ruff-format", "--line-length")
        self.assertEqual(ruff["forms"][0]["bounds"], {"min": self.sources["ruff"]["minimum"], "max": self.sources["ruff"]["maximum"]})
        self.assertEqual(ruff["forms"][0]["unit"]["base"], "custom")
        self.assertIn("Unicode", ruff["forms"][0]["unit"]["definition"])
        for profile in ("ruff-check", "ruff-format"):
            target = self.node(profile, "--target-version")
            self.assertEqual(target["kind"], "identifier")
            self.assertEqual(target["forms"][0]["tokens"], self.sources["ruff"]["python_tokens"])
            self.assertEqual(target["bare"]["state"], "not_accepted")

    def test_composites_delegated_values_and_dates_preserve_distinctions(self):
        for name in ("esptool-write-flash", "esptool.py-write-flash", "esptool.py-write_flash"):
            profile = self.profiles[name]
            composite = self.nodes(name, profile["positional_value_semantics"])[0]
            self.assertEqual(composite["slots"], self.sources["esptool_address"]["token_slots"])
            self.assertEqual(composite["slots"], profile["positional_group"]["argument_count"])
            address = next(component["semantics"] for component in composite["components"] if component["id"] == "address")
            self.assertEqual(address["origin"], self.sources["esptool_address"]["origin"])
            self.assertIn("byte", address["meaning"])
        mapping = self.node("ffmpeg", "-map")
        self.assertEqual(mapping["slots"], 1)
        self.assertTrue(all(component["slot"] == 1 for component in mapping["components"]))
        self.assertEqual(mapping["components"][0]["semantics"]["origin"], self.sources["ffmpeg_number"]["origin"])
        config = self.node("ssh", "-o")
        self.assertEqual(config["kind"], "delegated")
        self.assertNotIn("unit", config["forms"][0])
        self.assertIn("ssh_config", config["grammar"]["name"])
        since = self.node("journalctl", "--since=")
        self.assertEqual(since["applicability"]["platform"]["values"], [self.sources["journal"]["platform"]])
        epoch = next(form for form in since["forms"] if "@" in form["syntax"])
        self.assert_unit(epoch, self.sources["systemd_time"]["epoch_base"], "1")
        expiry = self.node("git-worktree-prune", "--expire")
        self.assertEqual(self.form(expiry, "never")["tokens"], self.sources["git_expiry"]["zero_cutoff_tokens"])
        self.assertEqual(self.form(expiry, "all")["tokens"], self.sources["git_expiry"]["unbounded_cutoff_tokens"])
        self.assertEqual(expiry["bare"]["state"], "unverified")
        tail = self.node("podman-logs", "--tail")
        self.assertIn(self.sources["podman"]["all_tail"], {item["value"] for item in tail["forms"][0]["special_values"]})

    def test_display_fields_and_formatter_expose_essential_meaning(self):
        cases = (("rsync", "--bwlimit=", "KiB/s", "1024 bytes/second"),
                 ("scp", "-l", "1024 bits/s", "1024 bits/second"),
                 ("ffmpeg", "-b:v", "bits/s", "bits/second"),
                 ("ffmpeg", "-ss", "seconds", "0.001 second"),
                 ("esptool-write-flash", "--flash-size", "4 MiB", "4194304 byte"),
                 ("esptool-write-flash", "--flash-freq", "40 MHz", "40000000 hertz"),
                 ("fzf", "--height", "terminal rows", "0.01 of terminal height"),
                 ("ruff-format", "--line-length", "Unicode", "Unicode"),
                 ("yq-eval", "--indent", "spaces", "Spaces per indentation level"))
        for profile, flag, visible, formatted in cases:
            with self.subTest(profile=profile, flag=flag):
                self.assertIn(visible, self.option(profile, flag)["summary"])
                self.assertIn(formatted, self.explanations(profile, flag))
        self.assertIn("No bandwidth limit", self.explanations("rsync", "--bwlimit="))
        self.assertIn("5.0.2", self.explanations("esptool-write-flash", "--flash-size"))

    def test_unresolved_content_remains_diagnostic_and_not_verified(self):
        for case in self.evidence["unresolved_examples"]:
            name, flag = case["profile"], case["flag"]
            option = self.option(name, flag)
            definitions = self.profiles[name].get("value_definitions")
            with self.subTest(profile=name, flag=flag):
                self.assertTrue(all(node["review"]["status"] == "source_derived" for node in self.nodes(name, option["value_semantics"])))
                diagnostics = validate_value_semantics(option["value_semantics"], mode="maintained", definitions=definitions)
                self.assertIn("sem_review_required", {d.code for d in diagnostics})
                external = validate_value_semantics(option["value_semantics"], mode="external", definitions=definitions)
                self.assertTrue(all(d.severity == "warning" for d in external))
                self.assertIn("Evidence: source derived", self.explanations(name, flag))

    def test_missing_units_false_review_and_overlapping_chips_are_rejected(self):
        missing = deepcopy(self.option("rsync", "--bwlimit=")["value_semantics"])
        del missing["variants"][0]["forms"][0]["unit"]
        diagnostics = validate_value_semantics(missing, mode="maintained", context=ValueContext(
            source="synthetic:mutated-rsync", command=("rsync",), option="--bwlimit="))
        self.assertIn("sem_unit_missing", {d.code for d in diagnostics})
        self.assertTrue(all(d.source == "synthetic:mutated-rsync" and d.option == "--bwlimit=" and d.pointer for d in diagnostics))
        false_review = deepcopy(self.option("gcloud-compute-instances-list", "--page-size")["value_semantics"])
        false_review["variants"][0]["review"]["status"] = "verified"
        self.assertIn("sem_false_verification", {d.code for d in validate_value_semantics(false_review)})
        chips = deepcopy(self.option("esptool-write-flash", "--flash-freq")["value_semantics"])
        chips["variants"][1]["applicability"]["chip"] = deepcopy(chips["variants"][0]["applicability"]["chip"])
        self.assertIn("sem_variant_conflict", {d.code for d in validate_value_semantics(chips)})
        # A plausible but false positive multiplier is structurally valid. Source
        # expectations, rather than schema validation, detect that factual error.
        wrong_scale = deepcopy(self.form(self.node("scp", "-l"), "rate"))
        wrong_scale["unit"]["multiplier"] = "1000"
        with self.assertRaises(AssertionError):
            self.assert_unit(wrong_scale, "bit", self.sources["openssh"]["bare_bits_per_second"], "second")

    def test_explicit_aliases_and_shared_definition_conflicts(self):
        for path, groups in self.evidence["aliases"].items():
            profile = self.profiles[Path(path).stem]
            self.assertEqual(validate_profile_semantics(profile, source=path, alias_groups=groups), ())
        changed = deepcopy(self.profiles["fzf"])
        alias = next(option for category in changed["categories"] for option in category["options"] if option["flag"] == "-m")
        alias["value_semantics"] = deepcopy(self.option("fzf", "--multi")["value_semantics"])
        alias["value_semantics"]["variants"] = [deepcopy(changed["value_definitions"]["selection-limit"])]
        alias["value_semantics"]["variants"][0]["meaning"] = "Conflicting synthetic alias interpretation"
        self.assertIn("sem_alias_conflict", {d.code for d in validate_profile_semantics(changed, alias_groups=[["--multi", "-m"]])})

    def test_pure_validation_formatting_and_literal_edits(self):
        originals = deepcopy(self.profiles)
        blocked = AssertionError("Target execution, network access and unrequested file I/O are forbidden")
        with ExitStack() as stack:
            for target in ("subprocess.Popen", "subprocess.run", "socket.socket", "socket.create_connection",
                           "socket.getaddrinfo", "os.system", "os.popen", "builtins.open", "pathlib.Path.open"):
                stack.enter_context(patch(target, side_effect=blocked))
            for name, profile, metadata, context in self.selected():
                validate_value_semantics(metadata, context=context, definitions=profile.get("value_definitions"))
                first = format_value_semantics(metadata, context=context, definitions=profile.get("value_definitions"))
                self.assertEqual(first, format_value_semantics(metadata, context=context, definitions=profile.get("value_definitions")))
            for name, profile in self.profiles.items():
                legacy = deepcopy(profile)
                legacy.pop("value_definitions", None)
                legacy.pop("positional_value_semantics", None)
                for category in legacy["categories"]:
                    for option in category["options"]:
                        option.pop("value_semantics", None)
                for category, old_category in zip(profile["categories"], legacy["categories"]):
                    for option, old_option in zip(category["options"], old_category["options"]):
                        if "value_semantics" not in option:
                            continue
                        prefix = "echo keep && " + " ".join(profile["command"]) + "  "
                        line = prefix + "--part" + "  untouched; $(untrusted)"
                        start, end = len(prefix), len(prefix) + len("--part")
                        new = insert_option(Context(line, end, start, end, "--part", profile), option)
                        old = insert_option(Context(line, end, start, end, "--part", legacy), old_option)
                        self.assertEqual(new, old, (name, option["flag"]))
                        self.assertTrue(new[0].startswith(prefix))
                        self.assertTrue(new[0].endswith("  untouched; $(untrusted)"))
        self.assertEqual(self.profiles, originals)


if __name__ == "__main__":
    unittest.main()
