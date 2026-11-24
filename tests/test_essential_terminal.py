"""Exercise discovery using recorded replies, an empty bundled directory and a private tmux server."""

import json
import lzma
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_essential_media import FIXTURES, RELEASES, combined_inventory, media_input, media_manual
from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TmuxShell
from presentation import option_text
from ui import Browser, option_label_width, option_row, wrap_cells

HELP = FIXTURES / "help"
CASES = [r for r in json.loads((HELP / "matrix.json").read_text()) if r["tier"] == "essential"]
CAPTURES = json.loads((HELP / "captured.json").read_text())
WORKFLOW = json.loads((HELP / "workflow-baseline-captured.json").read_text())
MAN_ARGS = ["-P", "/bin/cat", "--no-hyphenation", "--no-justification", "-s", "1:8", "--"]
# These routes have a secondary manual. Git uses the manual as its only source.
MANUALS = {name: name for name in
           "ffmpeg ffprobe npm pip wget rsync jq rg cp mv rm sort head tail du df sed gzip xz".split()}
MANUALS.update({"docker run": "docker-run", "docker image ls": "docker-image-ls",
                "npm install": "npm-install", "npm run": "npm-run-script",
                "pip install": "pip-install", "pip3 install": "pip-install", "pip download": "pip-download"})


def fixed_inputs(case, release, supplement=None):
    """Return exact permitted probe argv, deterministic reply text and independent arities."""
    name = case["command"]
    if supplement:
        replies = {}
        for item in supplement["sources"]:
            argv = item["argv"]
            if argv[0] == "man":
                argv = ["man", *MAN_ARGS, argv[-1]]
            if "file" in item:
                path = FIXTURES / "essential" / item["file"]
                reply = lzma.decompress(path.read_bytes()).decode() if path.suffix == ".xz" else path.read_text()
            else:
                reply = item["text"]
            replies[tuple(argv)] = reply
        if name in MANUALS:
            replies.setdefault(("man", *MAN_ARGS, MANUALS[name]), "")
        return replies, supplement["options"]
    if release:
        text = media_input(name, release)
        source = [name, "--help"]
        expected = combined_inventory(name, release)
    else:
        if name in CAPTURES:
            record = CAPTURES[name]
            text, source = record["text"], record["source"]
        else:
            record = WORKFLOW[name]
            text = (HELP / case["fixture"]).read_text()
            source = [record["source_program"], *record["source_arguments"]]
        family = next(path for path in ("packages", "git-docker", "utilities")
                      if name in inventory(path))
        expected = inventory(family)[name]
    replies = {}
    if source[0] == "man":
        replies[("man", *MAN_ARGS, source[-1])] = text
    else:
        replies[tuple(source)] = text
        if name in MANUALS:
            replies[("man", *MAN_ARGS, MANUALS[name])] = media_manual(name, release) if release else ""
    return replies, expected


def inventory(family):
    """Read the family's independent inventory in this sandbox snapshot."""
    return json.loads((FIXTURES / "essential" / (family + ".json")).read_text())


def recording_tools(folder, executable, replies):
    """Install exact-argv stubs for both possible probes. Any other invocation leaves evidence."""
    toolbin = folder / "bin"
    toolbin.mkdir()
    for program in (executable, "man"):
        body = ["#!/bin/sh"]
        for index, (request, text) in enumerate(replies.items()):
            if request[0] != program:
                continue
            path = folder / f"reply-{index}"
            path.write_text(text)
            conditions = ['[ "$#" = ' + str(len(request) - 1) + ' ]']
            conditions += [f'[ "${n}" = {shlex.quote(word)} ]' for n, word in enumerate(request[1:], 1)]
            body += ["if " + " && ".join(conditions) + "; then",
                     "  echo " + str(index) + " >> " + shlex.quote(str(folder / "requests")),
                     "  exec /bin/cat " + shlex.quote(str(path)), "fi"]
        body += ["echo unexpected >> " + shlex.quote(str(folder / "executed")), "exit 99"]
        stub = toolbin / program
        stub.write_text("\n".join(body) + "\n")
        stub.chmod(0o700)
    return toolbin


@unittest.skipUnless(TMUX_AVAILABLE, "Requires real Bash/tmux on Linux")
class EssentialDiscoveryScreenTests(unittest.TestCase):
    def exercise(self, case, release=None, supplement=None):
        """Refresh the private cache, open the actual discovered menu, and edit a pending line."""
        name = case["command"]
        words = name.split()
        with tempfile.TemporaryDirectory(prefix="discovered-menu-") as directory:
            folder = Path(directory)
            runtime = folder / "runtime"
            shutil.copytree(ROOT / "cli_help", runtime / "cli_help", ignore=shutil.ignore_patterns("__pycache__"))
            (runtime / "bash").symlink_to(ROOT / "bash")
            (runtime / "profiles").mkdir()
            replies, expected = fixed_inputs(case, release, supplement)
            toolbin = recording_tools(folder, words[0], replies)
            settings = {"PATH": str(toolbin) + ":/usr/bin:/bin", "CLI_HELP_DISCOVERY": "auto",
                        "CLI_HELP_DRIVERS": str(ROOT / "config/drivers.example"),
                        "CLI_HELP_CACHE_DIR": str(folder / "cache")}
            env = {**settings, "HOME": directory, "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"}
            run = subprocess.run([sys.executable, str(runtime / "cli_help/main.py"), "--discover", *words,
                                  "--refresh"], env=env, cwd=folder, capture_output=True, text=True, timeout=20)
            requests = folder / "requests"
            self.assertEqual(requests.read_text().splitlines(), list(map(str, range(len(replies)))))
            shell = TmuxShell(folder, runtime=runtime)
            try:
                shell.text("export " + " ".join(k + "=" + shlex.quote(v) for k, v in settings.items()))
                shell.keys("Enter")
                shell.wait_for(lambda s: s.cells[s.y] == PROMPT.rstrip())
                prefix, suffix = name + " ", " 'private operand'"
                shell.text(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                if not expected:
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("No recognizable option declarations", run.stderr)
                    shell.resize(60, 16)
                    shell.keys("Escape", "h")
                    shell.wait_for(lambda s: not s.alternate and "help_unparsed" in "".join(s.cells))
                    self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                    self.assertEqual(requests.read_text().splitlines(), list(map(str, range(len(replies)))) * 2)
                    return
                self.assertEqual(run.returncode, 0, run.stderr)
                profile = json.loads(run.stdout)
                options = [o for c in profile["categories"] for o in c["options"]]
                arities = {o["flag"]: o.get("argument_count", 1) if o["argument"] else 0 for o in options}
                self.assertEqual(expected, arities)
                self.walk(shell, profile)
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                self.small_edit(shell, profile, prefix, suffix, release)
                if not supplement:
                    boundary = " -- "
                    # At the pip root the driver rejects the ambiguous path before lookup.
                    diagnostic = "unsupported_option" if name == "pip" else "end_of_options"
                    if name in {"docker run", "docker compose exec", "docker compose run", "uv run", "npm run"}:
                        boundary = " operand child "
                        diagnostic = "child_argument_boundary"
                    shell.keys("C-a", "C-k")
                    pending = name + boundary
                    shell.text(pending)
                    shell.keys("Escape", "h")
                    shell.wait_for(lambda s: not s.alternate and diagnostic in "".join(s.cells))
                    self.assertEqual(shell.read_buffer(), (pending, len(pending)))
                self.assertEqual(requests.read_text().splitlines(), list(map(str, range(len(replies)))))
            finally:
                shell.close()
                self.assertFalse(shell.executed.exists(), "The pending command or an unexpected probe ran")

    def walk(self, shell, profile):
        """Compare every selected row and all displayed Details, including long component definitions."""
        width = 220
        derived = [[option_text(profile, c, o) for o in c["options"]] for c in profile["categories"]]
        def lines(view):
            return [line for p in view.details for paragraph in p.splitlines() for line in wrap_cells(paragraph, width - 2)]
        longest = max(len(lines(view)) for category in derived for view in category)
        shell.resize(width, max(64, longest * 2 + 16))
        menu = shell.open_menu()
        self.assertEqual(menu.cells[1], profile["description"])
        for ci, category in enumerate(profile["categories"]):
            if ci:
                shell.keys("Right")
            label_width = option_label_width(category, width - 27)
            for i, (row, view) in enumerate(zip(category["options"], derived[ci])):
                if i:
                    shell.keys("Down")
                rendered = option_row(row, view, width - 27, label_width, True).rstrip()
                # wait_for_option compares the full Details cells and selected declaration/summary.
                shell.wait_for_option("", "", lines(view), exact_row=rendered)
        shell.cancel()

    def small_edit(self, shell, profile, prefix, suffix, release):
        """Search at minimum size, scroll through a qualifying row, cancel, then accept it."""
        shell.resize(60, 16)
        browser = Browser(profile)
        rows = [o for c in profile["categories"] for o in c["options"]]
        # Prefer a value-taking entry with enough text to exercise Details scrolling.
        candidates = [o for o in rows if len(browser.text(o).searchable) < 1600] or rows
        row = max(candidates, key=lambda o: (bool(o["argument"]), len(browser.text(o).searchable)))
        query = row["flag"]
        if profile["command"] == ["ffmpeg"] and release == "resolute":
            query = "without reencoding"
        browser.set_query(query)
        row = browser.options()[0]
        view = browser.text(row)
        details = [line for p in view.details for para in p.splitlines() for line in wrap_cells(para, 58)]
        for accept in (False, True):
            shell.open_menu()
            shell.keys("/")
            shell.text(query)
            shell.keys("Enter")
            menu = shell.wait_for(lambda s: s.cells[2] == "Filter: " + query)
            if not accept:
                if len(details) > 5:
                    shell.keys(*(["]"] * (len(details) - 5)))
                shell.wait_for(lambda s: s.cells[-3].split(" |")[0].endswith(f"-{len(details)}/{len(details)}")
                               and details[-1] in s.cells[8:-3])
            shell.cancel("Enter" if accept else "Escape")
            if not accept:
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        literal = row["flag"]
        if row.get("argument_style") == "equals" and not literal.endswith("="):
            literal += "="
        joined_value = literal.endswith("=") or row.get("argument_style") == "attached_only"
        self.assertEqual(shell.read_buffer(), (prefix + literal + suffix,
                         len(prefix + literal) + int(not joined_value)))


def screen_case(case, release, supplement=None):
    """Give each matrix route its own independently reportable test method."""
    def test(self):
        self.exercise(case, release, supplement)
    return test


for case in CASES:
    name = case["command"]
    for release in RELEASES if name in {"ffmpeg", "ffprobe"} else (None,):
        method = "test_" + name.replace(" ", "_") + ("_" + release if release else "")
        setattr(EssentialDiscoveryScreenTests, method, screen_case(case, release))

for manifest in sorted((FIXTURES / "essential").glob("*.json")):
    if not manifest.stem.endswith(("-full", "-noble")):
        continue
    for name, supplement in json.loads(manifest.read_text()).items():
        case = next(item for item in CASES if item["command"] == name)
        suffix = "_noble" if manifest.stem.endswith("-noble") else ""
        setattr(EssentialDiscoveryScreenTests, "test_complete_" + name.replace(" ", "_") + suffix,
                screen_case(case, None, supplement))
