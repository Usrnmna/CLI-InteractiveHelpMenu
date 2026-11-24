"""Check ownership, arity and Details in the two historical package-help corpora."""

import json
import lzma
import unittest

from test_program_corpus import CAPTURED, FIXTURES, build_profile, options_by_flag, parse_help


def package_options(command):
    """Extract the candidate rows from the recorded Ubuntu client response."""
    record = CAPTURED[command]
    label = " ".join(record["source"])
    return options_by_flag(build_profile(command.split(), [(label, record["text"])]))


def complete_responses(record):
    """Read both fixed-source responses in production priority order."""
    base = FIXTURES.parent / "essential"
    return [(" ".join(source["argv"]), lzma.decompress((base / source["file"]).read_bytes()).decode())
            for source in record["sources"]]


class EssentialPackageHelpTests(unittest.TestCase):
    def test_complete_historical_capture_inventories(self):
        inventories = json.loads((FIXTURES.parent / "essential/packages.json").read_text())
        for route, expected in inventories.items():
            with self.subTest(route=route):
                if route == "npm":
                    self.assertEqual(parse_help(CAPTURED[route]["text"], "npm --help"), [])
                    continue
                rows = package_options(route)
                observed = {flag: row.get("argument_count", 1) if row["argument"] else 0
                            for flag, row in rows.items()}
                self.assertEqual(expected, observed)

    def test_bracketed_repeatability_and_detached_command_aliases(self):
        rows = package_options("npm install")
        for flag in ("-w", "--workspace"):
            self.assertEqual(rows[flag]["argument"], "<workspace-name>")
            self.assertFalse(rows[flag]["argument_optional"])
            self.assertIn("[-w|--workspace <workspace-name> ...]", rows[flag]["detail"])
            self.assertEqual(rows[flag]["detail"].count("Source: "), 1)
        self.assertIn("[--omit <dev|optional|peer> ...]", rows["--omit"]["detail"])
        self.assertIn("installation on disk", rows["--omit"]["summary"])
        self.assertIn("npm 9.2.0", rows["--omit"]["detail"])
        self.assertIn("pre- and post-scripts", package_options("npm run")["--ignore-scripts"]["summary"])
        self.assertTrue(all(row["summary"] != "Documented option" for row in rows.values()))
        self.assertNotIn("--workspaces", rows["--no-install-links"]["detail"])
        self.assertNotIn("aliases: add", rows["--workspaces"]["summary"])
        profile = build_profile(["npm", "install"], [("npm --help install", CAPTURED["npm install"]["text"])])
        context = profile["documentation"]["shared"]
        self.assertTrue(any(p["association"] == "unassigned" and "aliases: add" in p["text"] for p in context))

    def test_negation_has_distinct_meaning_without_inventing_missing_text(self):
        rows = package_options("pnpm install")
        self.assertIn("negated form of --frozen-lockfile", rows["--no-frozen-lockfile"]["summary"])
        self.assertNotEqual(rows["--no-frozen-lockfile"]["summary"], rows["--frozen-lockfile"]["summary"])
        self.assertIn("default in CI environments, so use", rows["--no-frozen-lockfile"]["detail"])
        self.assertIn("dependencies are not available in local", rows["--offline"]["detail"])

    def test_wrapped_option_qualifications_and_referenced_switches(self):
        for command in ("pip install", "pip3 install"):
            self.assertIn("multiple times", package_options(command)["--requirement"]["detail"])
            self.assertIn("Use --upgrade to replace existing", package_options(command)["--target"]["detail"])
        platform = package_options("pip download")
        self.assertNotIn("--implementation", platform)
        self.assertIn("multiple platforms supported", platform["--platform"]["detail"])
        self.assertIn("requirements files", package_options("uv pip install")["--no-deps"]["detail"])
        self.assertIn("prior to running", package_options("uv run")["--directory"]["detail"])

    def test_complete_fixed_clients_and_manuals(self):
        base = FIXTURES.parent / "essential"
        for inventory in ("packages-full.json", "packages-noble.json"):
            for command, record in json.loads((base / inventory).read_text()).items():
                with self.subTest(inventory=inventory, command=command):
                    sources = complete_responses(record)
                    if not record["options"]:
                        for label, text in sources:
                            self.assertEqual(parse_help(text, label), [])
                        continue
                    rows = options_by_flag(build_profile(command.split(), sources))
                    self.assertEqual(record["options"],
                                     {flag: o.get("argument_count", 1) if o["argument"] else 0
                                      for flag, o in rows.items()})

    def test_full_source_explanations_and_ownership(self):
        base = FIXTURES.parent / "essential"
        records = json.loads((base / "packages-full.json").read_text())
        for command in ("uv run", "uv pip install"):
            rows = options_by_flag(build_profile(command.split(), complete_responses(records[command])))
            self.assertIn("silent mode", rows["-q"]["detail"])
            self.assertIn("--verbose...", rows["--verbose"]["detail"])
        rows = options_by_flag(build_profile(["pnpm", "install"], complete_responses(records["pnpm install"])))
        self.assertIn("--filter <pattern>^...", rows["--filter"]["detail"])
        self.assertIn("--package-import-method hardlink", rows["--package-import-method"]["detail"])
        self.assertIn("--reporter silent", rows["--reporter"]["detail"])
        self.assertNotIn("Filtering options", rows["--silent"]["detail"])
        rows = options_by_flag(build_profile(["npm", "install"], complete_responses(records["npm install"])))
        self.assertIn("default unless -D or -O", rows["-P"]["detail"])
        self.assertNotIn("package-lock.json", rows["-B"]["detail"])
        noble = json.loads((base / "packages-noble.json").read_text())
        profile = build_profile(["pip"], complete_responses(noble["pip"]))
        self.assertIn("appends verbose output", options_by_flag(profile)["--log-file"]["detail"])
        self.assertTrue(any(p["section"] == "INSTALL OPTIONS" and p["association"] == "unassigned"
                            for p in profile["documentation"]["shared"]))
