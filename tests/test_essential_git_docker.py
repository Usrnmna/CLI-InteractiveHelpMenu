"""Independent declarations and complete wrapped statements from fixed Git/Docker documentation."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
import discovery

HELP = ROOT / "tests/fixtures/help"
CAPTURES = json.loads((HELP / "captured.json").read_text())
WORKFLOWS = json.loads((HELP / "workflow-baseline-captured.json").read_text())
EXPECTED = json.loads((ROOT / "tests/fixtures/essential/git-docker.json").read_text())


def source_for(command):
    """Load an existing Noble fixed response or excerpt by its recorded source route."""
    if command in CAPTURES:
        return CAPTURES[command]["text"]
    return (HELP / WORKFLOWS[command]["fixture"]).read_text()


class EssentialGitDockerTests(unittest.TestCase):
    def test_all_captured_spellings_and_arity(self):
        for command, declarations in EXPECTED.items():
            with self.subTest(command=command):
                profile = discovery.build_profile(command.split(), [("capture", source_for(command))])
                options = {o["flag"]: o for c in profile["categories"] for o in c["options"]}
                actual = {flag: option.get("argument_count", 1) if option.get("argument") else 0
                          for flag, option in options.items()}
                self.assertEqual(actual, declarations)
                optional = {"git status": {"--porcelain", "-u", "--untracked-files"},
                            "git show": {"--pretty"}, "git switch": {"-t", "--track"},
                            "git diff": {"--color", "--stat"}}
                self.assertEqual({flag for flag, op in options.items() if op.get("argument_optional")},
                                 optional.get(command, set()))

    def test_manual_prose_cannot_define_an_option_or_steal_its_details(self):
        for command, flag in (("git commit", "--amend"), ("git fetch", "--prune"), ("git switch", "--track")):
            with self.subTest(command=command):
                options = discovery.parse_help(source_for(command), "man " + command.replace(" ", "-"))
                self.assertEqual([o["flag"] for o in options].count(flag), 1)
                if command == "git switch":
                    for option in (o for o in options if o["flag"] in ("-t", "--track")):
                        self.assertIn("--track in git-branch(1) for details.", option["detail"])
                if command == "git fetch":
                    jobs = next(o for o in options if o["flag"] == "--jobs=")
                    self.assertNotIn("an error.", jobs["detail"])

    def test_hard_wraps_produce_a_readable_opening_statement(self):
        examples = (
            ("docker run", "--rm", "Automatically remove the container and its associated anonymous volumes when it exits"),
            ("docker compose up", "--timeout", "Use this timeout in seconds for container shutdown when attached or when containers are already running"),
            ("git commit", "-m", "Use the given <msg> as the commit message."),
            ("docker compose build", "--memory", "Set memory limit for the build container."),
        )
        for command, flag, summary in examples:
            with self.subTest(command=command, flag=flag):
                option = next(o for o in discovery.parse_help(source_for(command), "capture") if o["flag"] == flag)
                self.assertEqual(option["summary"], summary)
                if flag == "--memory":
                    self.assertIn("Not supported by BuildKit.", option["detail"])

    def test_complete_release_sources_match_independent_declarations(self):
        import lzma

        folder = ROOT / "tests/fixtures/essential"
        common = json.loads((folder / "git-docker-full.json").read_text())
        noble = json.loads((folder / "git-docker-noble.json").read_text())
        for release, cases in (("resolute", common), ("noble", noble)):
            for command, case in cases.items():
                with self.subTest(release=release, command=command):
                    sources = []
                    for source in case["sources"]:
                        path = folder / source["file"]
                        content = lzma.decompress(path.read_bytes()).decode() if path.suffix == ".xz" else path.read_text()
                        sources.append((" ".join(source["argv"]), content))
                    profile = discovery.build_profile(command.split(), sources)
                    options = {o["flag"]: o for c in profile["categories"] for o in c["options"]}
                    self.assertEqual({flag: o.get("argument_count", 1) if o.get("argument") else 0
                                      for flag, o in options.items()}, case["options"])
                    if command == "git log":
                        self.assertTrue(options["--expand-tabs"]["argument_optional"])
                        self.assertTrue(options["-U"]["argument_optional"])
                        self.assertEqual(options["-U"]["argument_style"], "attached_only")
                        self.assertIn("-L:<funcname>:<file>", options["-L"]["detail"])
                        self.assertIn("maximum", options["--no-max-parents"]["summary"])
                    if command == "git commit":
                        self.assertIn("Allow a commit", options["--allow-empty"]["summary"])
                        if "-U" in options:
                            self.assertFalse(options["-U"]["argument_optional"])
                        self.assertIn("restores hook checks", options["--verify"]["detail"])
                        self.assertFalse(options["--no-gpg-sign"]["argument"])
                    if command == "docker run":
                        option = options["--kernel-memory"]
                        self.assertIn("29.1.3", option["summary"])
                        self.assertIn("no effect", option["detail"])
                        self.assertIn("when it exits", options["--rm"]["summary"])
                        self.assertNotIn("warning [p", options["--env"]["detail"])
                        self.assertIn("Create a tmpfs mount", options["--tmpfs"]["detail"])
