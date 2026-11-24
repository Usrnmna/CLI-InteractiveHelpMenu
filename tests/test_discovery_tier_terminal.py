"""Verify each Next and Extended route with independent declarations and fixed replies."""

import json
import unittest

from test_essential_terminal import DiscoveryScreenChecks, FIXTURES, screen_case
from test_terminal_screen import TMUX_AVAILABLE


SOURCES = FIXTURES / "discovery-tiers"
CASES = [case for case in json.loads((FIXTURES / "help/matrix.json").read_text())
         if case["tier"] in {"next", "extended"}]


def routes_by_name():
    """Load independent family inventories, rejecting duplicate route ownership."""
    routes = {}
    for filename in ("next-tools.json", "extended-tools.json", "cloud.json"):
        for name, record in json.loads((SOURCES / filename).read_text()).items():
            if name in routes:
                raise ValueError(f"Duplicate discovery inventory for {name}")
            routes[name] = record
    if routes.keys() != {case["command"] for case in CASES}:
        raise ValueError("Discovery inventories must cover exactly the Next and Extended routes")
    return routes


@unittest.skipUnless(TMUX_AVAILABLE, "Requires real Bash/tmux on Linux")
class DiscoveryTierScreenTests(DiscoveryScreenChecks, unittest.TestCase):
    """Each method reports the terminal outcome of one matrix path."""

    source_directory = SOURCES


def install_cases():
    """Bind independently reportable tests in maintained matrix order."""
    routes = routes_by_name()
    for case in CASES:
        name = case["command"]
        record = routes[name]
        if case.get("profile_only"):
            # The fixed documentation request belongs to the root. exercise()
            # also checks direct rejection of the extraction subcommand.
            record = routes[name.split()[0]]
        method = "test_" + case["tier"] + "_" + name.replace(" ", "_").replace(".", "_")
        setattr(DiscoveryTierScreenTests, method, screen_case(case, None, record))


install_cases()
