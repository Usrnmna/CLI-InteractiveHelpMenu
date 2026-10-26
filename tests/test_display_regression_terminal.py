"""Render captured descriptions in a private terminal without target discovery."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from test_discovery import ROOT
from discovery import build_profile
from core import validate_profile
from test_terminal_screen import TMUX_AVAILABLE, TmuxShell


CASES = (
    ("git commit", "-m", "Use the given <msg>"),
    ("docker run", "-e", "Set environment variables"),
    ("curl", "-H", "Pass custom header(s) to server"),
    ("terraform plan", "-var", "Set a value for one of the input variables"),
    ("kubectl logs", "-c", "Print the logs of this container"),
    ("ffmpeg", "-y", "overwrite output files"),
    ("aws s3 cp", "--exclude", "Exclude all files or objects from the"),
)


@unittest.skipUnless(TMUX_AVAILABLE, "Captured-description screen checks require Linux and tmux")
class CapturedDescriptionScreenTests(unittest.TestCase):
    def test_opening_description_and_spacing_survive_real_rendering(self):
        """Check actual cells, narrow/wide redraws and cancellation for seven families."""
        captures = json.loads((ROOT / "tests/fixtures/help/captured.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="cli-help-description-screen-") as folder:
            profiles = Path(folder) / "profiles"
            profiles.mkdir()
            expected = {}
            for command, flag, opening in CASES:
                profile = build_profile(command.split(), [("captured fixture", captures[command]["text"])])
                category = next(c for c in profile["categories"] if any(o["flag"] == flag for o in c["options"]))
                option = next(o for o in category["options"] if o["flag"] == flag)
                self.assertTrue(option["summary"].startswith(opening))
                expected[command] = option["summary"]
                # Isolate selection while retaining the real captured declaration,
                # description, continuation paragraphs and source attribution.
                selected = deepcopy(profile)
                selected["categories"] = [{**category, "options": [option]}]
                validate_profile(selected, Path("captured-fixture.json"))
                (profiles / (command.replace(" ", "-") + ".json")).write_text(json.dumps(selected), encoding="utf-8")
            shell = TmuxShell(folder, profile_directory=profiles)
            try:
                for command, flag, opening in CASES:
                    with self.subTest(command=command):
                        shell.keys("C-u")
                        pending = command + " --partial"
                        shell.text(pending)
                        # The supplied partial token has no matches; clear it in
                        # the browser, without changing the pending shell buffer.
                        shell.open_menu()
                        shell.keys("C-u")
                        for width, height in ((160, 40), (60, 16), (100, 24), (160, 40)):
                            state = shell.resize(width, height)
                            self.assertIn("OPTIONS", state.cells[3])
                            self.assertIn(opening[:10], state.cells[4])
                            if width == 160:
                                start = 5 + max(3, (height - 9) // 2)
                                details = "\n".join(state.cells[start:height - 3])
                                if command == "aws s3 cp":
                                    # This full capture merges usage/examples before
                                    # the description. Later repetitions remain
                                    # deliberate evidence, not opening duplicates.
                                    self.assertIn(expected[command], details)
                                else:
                                    self.assertEqual(details.count(expected[command]), 1)
                        shell.cancel()
                        self.assertEqual(shell.read_buffer(), (pending, len(pending)))
                        shell.open_menu()
                        shell.cancel()
                        self.assertEqual(shell.read_buffer(), (pending, len(pending)))
                        self.assertFalse(shell.executed.exists())
            finally:
                shell.close()


if __name__ == "__main__":
    unittest.main()
