"""Replay the second Ubuntu source edition in the discovery audit's Bash/tmux harness."""

import json
import unittest

from test_essential_terminal import DiscoveryScreenChecks, screen_case
from test_discovery_system_tools import FIXTURES, ROOT
from test_terminal_screen import TMUX_AVAILABLE


@unittest.skipUnless(TMUX_AVAILABLE, "Requires real Bash/tmux on Linux")
class SystemSourceEditionScreens(DiscoveryScreenChecks, unittest.TestCase):
    """Optional full-row terminal checks for the Resolute baseline and alternate yq release."""

    source_directory = FIXTURES


def install_cases():
    """Register each edition under its exact matrix route for targeted replays."""
    records = json.loads((FIXTURES / "system-resolute.json").read_text())
    matrix = json.loads((ROOT / "tests/fixtures/help/matrix.json").read_text())
    for case in matrix:
        name = case["command"]
        if name in records:
            setattr(SystemSourceEditionScreens, "test_" + name.replace(" ", "_"),
                    screen_case(case, None, records[name]))


install_cases()


if __name__ == "__main__":
    unittest.main()
