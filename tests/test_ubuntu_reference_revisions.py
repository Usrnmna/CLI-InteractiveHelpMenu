"""Verify exact provider, revision and manual matching at the discovery entry point."""
import hashlib
import json
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError
from discovery import Settings, discover
from drivers import Driver, HelpRoute
from ubuntu_manual_routes import REVIEWED_MANUAL_ROOTS
from ubuntu_reference import REFERENCE, installed_reference, keyword_prefix, lookup_record, matched_manual


class ReferenceRevisionTests(unittest.TestCase):
    def setUp(self):
        self.page = "Options:\n  --foreign  A flag belonging to the other entry point.\n"
        self.digest = hashlib.sha256(self.page.encode()).hexdigest()
        self.record = {"command": "xzgrep", "targets": ["/usr/bin/xzgrep"], "package": "manual-pkg",
                       "version": "2", "launcher_package": "provider", "launcher_version": "2",
                       "page": "provider(1)", "sha256": "a" * 64, "usage": "xzgrep PATTERN FILE",
                       "reviewed_manual_sha256": [self.digest], "options": [], "keywords": ["primary"],
                       "revision_variants": {"1": {"version": "1", "launcher_version": "1",
                                                    "sha256": "b" * 64, "keywords": ["older"]}}}

    def status(self, package="provider", version="2"):
        """Supply a fresh dpkg status stream per read including its final unterminated stanza."""
        content = f"Package: {package}\nStatus: install ok installed\nVersion: {version}\n"
        return patch.object(Path, "open", side_effect=lambda *args, **kwargs: StringIO(content))

    def test_fixed_manual_allowlist_covers_exactly_the_packaged_fingerprints(self):
        names = set()
        for path in REFERENCE.glob("*/*.jsonl"):
            with path.open(encoding="utf-8") as source:
                for line in source:
                    if '"reviewed_manual_sha256"' in line:
                        names.add(json.loads(line)["command"])
        self.assertEqual(names, REVIEWED_MANUAL_ROOTS)

    def test_exact_version_and_manual_digest_are_both_required(self):
        for revision, keywords in (("1", ["older"]), ("2", ["primary"])):
            with self.subTest(revision=revision), self.status(version=revision):
                self.assertEqual(installed_reference(self.record)["keywords"], keywords)
                match = matched_manual(self.record, self.page)
                self.assertEqual(match is not None, revision == "2")
                self.assertIsNone(matched_manual(self.record, self.page + "\n"))
        self.record["revision_variants"]["1"]["reviewed_manual_sha256"] = [self.digest]
        with self.status(version="1"):
            self.assertEqual(matched_manual(self.record, self.page)["keywords"], ["older"])
        for provider, version in (("manual-pkg", "2"), ("provider", "3")):
            with self.subTest(provider=provider, version=version), self.status(provider, version):
                with self.assertRaises(HelpError) as error:
                    matched_manual(self.record, self.page)
                self.assertEqual(error.exception.code, "usage_guidance")

    def test_xzgrep_fixed_manual_rejects_the_recursion_example_on_both_revisions(self):
        page = (ROOT / "tests/fixtures/ubuntu-coverage/resolute-xzgrep-manual.txt").read_text()
        self.assertIn("-r, --recursive", page)
        record = lookup_record("xzgrep", "resolute", "/usr/bin", "/usr/bin/xzgrep")
        paths = {"xzgrep": "/usr/bin/xzgrep", "man": "/usr/bin/man"}
        for version in ("5.8.3-1", "5.8.3-1ubuntu0.1"):
            with self.subTest(version=version), self.status("xz-utils", version), \
                    patch("discovery.shutil.which", side_effect=paths.get), \
                    patch("discovery.reference_record", return_value=record), \
                    patch("discovery.executable_identity", return_value={}), \
                    patch("discovery.run_probe", return_value=page):
                profile = discover("xzgrep", Settings(mode="man"))
                choices = {o["flag"]: o for c in profile["categories"] for o in c["options"]}
                self.assertNotIn("--recursive", choices)
                self.assertNotIn("-r", choices)
                self.assertEqual(choices["--regexp"]["argument_style"], "equals")
                self.assertEqual(profile["discovery"]["matched_manual"], "xzgrep")
                self.assertIn(version + ",", profile["discovery"]["sources"][0])

    def test_keyword_prefix_follows_selected_revision(self):
        with patch("ubuntu_reference.reference_record", return_value=self.record), \
                patch("ubuntu_reference.shutil.which", return_value="/usr/bin/xzgrep"), self.status(version="1"):
            self.assertTrue(keyword_prefix("xzgrep", "old"))
            self.assertFalse(keyword_prefix("xzgrep", "prim"))

    def test_fixed_manual_lookup_bypasses_stale_cache_and_respects_explicit_driver(self):
        paths = {"xzgrep": "/usr/bin/xzgrep", "man": "/usr/bin/man"}
        with tempfile.TemporaryDirectory() as tmp, \
                patch("discovery.shutil.which", side_effect=paths.get), \
                patch("discovery.reference_record", return_value=self.record), \
                patch("discovery.executable_identity", return_value={}), \
                patch("discovery.run_probe", return_value=self.page) as run, self.status():
            settings = Settings(cache_dir=Path(tmp))
            with patch("discovery.read_cache", side_effect=AssertionError("Stale manual cache")):
                first = discover("xzgrep", settings)
                self.assertEqual(first["discovery"]["matched_manual"], "xzgrep")
                self.assertEqual(first["categories"][0]["options"][0]["flag"], "primary")
                # A one-byte page change restores the installed source's own declaration.
                run.return_value = self.page + "\n"
                second = discover("xzgrep", settings)
                self.assertEqual(second["categories"][0]["options"][0]["flag"], "--foreign")
            self.assertTrue(all(call.args[0] == [paths["man"], "-P", "/bin/cat", "--no-hyphenation",
                                                  "--no-justification", "-s", "1:8", "--", "xzgrep"]
                                for call in run.call_args_list))
            driver = Driver(paths={(): HelpRoute((), "xzgrep", source="configured.json")})
            run.return_value = self.page
            third = discover("xzgrep", Settings(), driver_registry={"xzgrep": driver})
            self.assertEqual(third["categories"][0]["options"][0]["flag"], "--foreign")
