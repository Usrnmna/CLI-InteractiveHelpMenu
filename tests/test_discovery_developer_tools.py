"""Check source ownership and option forms against complete fixed developer-tool replies."""

import json
import unittest

from test_essential_terminal import FIXTURES, fixed_inputs
from core import HelpError, find_context, insert_option
from discovery import MAX_OUTPUT_BYTES, build_profile

SOURCE_DIR = FIXTURES / "discovery-tiers"
INVENTORY = json.loads((SOURCE_DIR / "next-tools.json").read_text())


def discovered(name, *, scope=True):
    """Build a passive profile from the same permitted source bytes used in Bash."""
    record = INVENTORY[name]
    replies, _ = fixed_inputs({"command": name}, None, record, SOURCE_DIR)
    scopes = {"man git-diff": "common_options"} if name == "git stash show" else {}
    if name == "git stash list" and scope:
        scopes["man git-log"] = "stash_reflog"
    sources, requests = [], {}
    for argv, response in replies.items():
        if name.startswith("yarn ") and argv[1:] == ("--version",):
            continue
        if len(response.encode()) > MAX_OUTPUT_BYTES:
            # The runtime rejects the whole GCC manual before parsing it.
            if name != "gcc" or argv[0] != "man":
                raise AssertionError(f"Unexpected oversized source for {name}")
            continue
        label = "man " + argv[-1] if argv[0] == "man" else " ".join(argv)
        sources.append((label, response))
        requests[label] = list(argv)
    return build_profile(name.split(), sources, source_requests=requests, source_scopes=scopes)


def spellings(profile):
    """Index selectable entries without guessing alternative names or arity."""
    return {o["flag"]: o for group in profile["categories"] for o in group["options"]}


class DeveloperDiscoveryTests(unittest.TestCase):
    def test_every_complete_fixed_inventory(self):
        for name, case in INVENTORY.items():
            with self.subTest(name=name):
                rows = spellings(discovered(name))
                self.assertEqual(
                    case["options"],
                    {flag: o.get("argument_count", 1) if o["argument"] else 0 for flag, o in rows.items()},
                )

    def test_shared_git_pages_do_not_offer_another_operations_switches(self):
        self.assertEqual(set(spellings(discovered("git stash apply"))), {"--index", "-q", "--quiet"})
        self.assertEqual(set(spellings(discovered("git worktree remove"))), {"--force", "-f"})
        self.assertEqual(spellings(discovered("git worktree"))["add"]["kind"], "keyword")
        self.assertIn("twice", spellings(discovered("git worktree remove"))["--force"]["detail"])
        scoped = discovered("git stash list")
        self.assertNotIn("--graph", spellings(scoped))
        self.assertIn("--graph", spellings(discovered("git stash list", scope=False)))
        self.assertTrue(any("--graph" in p["text"] for p in scoped["documentation"]["shared"]))

    def test_go_recovers_synopsis_tables_and_excludes_prose(self):
        tidy = spellings(discovered("go mod tidy"))
        self.assertIn("go.sum", tidy["-diff"]["detail"])
        self.assertIn("prior", tidy["-compat="]["detail"])
        self.assertEqual(spellings(discovered("go run"))["-exec"]["argument"], "xprog")
        self.assertNotIn("-timeout", spellings(discovered("go test")))
        build = spellings(discovered("go build"))
        self.assertEqual(build["-C"]["argument"], "dir")
        self.assertTrue(build["-buildvcs"]["argument_optional"])

    def test_compiler_argument_forms_and_subordinate_options(self):
        profile = discovered("gcc")
        gcc = spellings(profile)
        self.assertTrue(gcc["-save-temps"]["argument_optional"])
        for flag in ("--help", "-save-temps"):
            line = "gcc  source.c"
            context = find_context(line, 4, [profile])
            self.assertEqual(
                insert_option(context, gcc[flag]), ("gcc " + flag + " source.c", 5 + len(flag))
            )
        self.assertTrue({"-Wa", "-Wp", "-Wl", "-###"}.isdisjoint(gcc))
        clang = spellings(discovered("clang"))
        self.assertEqual(clang["-Xopenmp-target="]["argument_count"], 2)
        self.assertEqual(clang["-R"]["argument_style"], "attached_only")
        cmake = spellings(discovered("cmake"))
        self.assertNotIn("--parallel", cmake)
        self.assertNotIn("--target", cmake)
        self.assertTrue(cmake["--help"]["argument_optional"])
        self.assertTrue({"-LR", "-LRA", "-LRH", "-LRAH"} <= cmake.keys())

    def test_tool_dispatch_stops_root_insertion(self):
        cases = {
            "ninja": ("-t commands -s", "-tcommands -s"),
            "cmake": (
                "-E env --unset=PRIVATE",
                "--build out",
                "--install out",
                "--open out",
                "--workflow test",
            ),
        }
        for name, suffixes in cases.items():
            profile = discovered(name)
            for suffix in suffixes:
                with self.subTest(name=name, suffix=suffix):
                    line = f"{name} {suffix} "
                    with self.assertRaises(HelpError) as refused:
                        find_context(line, len(line), [profile])
                    self.assertEqual(refused.exception.code, "child_argument_boundary")
        generic = build_profile(
            "ninja", [("import", "Options:\n  -t TOOL  Select the toolset for the build.\n")]
        )
        self.assertFalse(generic.get("stop_at_options"))

    def test_versioned_runtime_aliases_and_optional_values(self):
        dotnet = spellings(discovered("dotnet run"))
        self.assertIn("-?, -h, --help", dotnet["--help"]["detail"])
        self.assertIn("-h", dotnet)
        bun = spellings(discovered("bun run"))
        for flag in ("--inspect", "--inspect-wait", "--inspect-brk", "-c", "--config"):
            self.assertTrue(bun[flag]["argument_optional"])
            self.assertEqual(bun[flag]["argument_style"], "equals")
        cargo = spellings(discovered("cargo test"))
        self.assertTrue(cargo["--bin"]["argument_optional"])
        self.assertFalse(cargo["--features"].get("argument_optional", False))
