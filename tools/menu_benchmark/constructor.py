"""Measure fresh Browser construction for each preloaded bundled profile."""

import gc
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def single_reference(option):
    """Independently identify a candidate reuse key in the bundled JSON inventory."""
    contract = option.get("value_semantics")
    count = option.get("argument_count", 1) if option.get("argument") else 0
    optional = option.get("argument_optional", False)
    if (not isinstance(contract, dict) or set(contract) != {"schema_version", "variants"}
            or type(contract["schema_version"]) is not int or contract["schema_version"] != 1
            or type(count) is not int or type(optional) is not bool):
        return None
    variants = contract["variants"]
    if not isinstance(variants, list) or len(variants) != 1:
        return None
    variant = variants[0]
    if not isinstance(variant, dict) or set(variant) != {"ref"} or not isinstance(variant["ref"], str):
        return None
    return variant["ref"], count, optional


def sweep(revision, pair):
    """In a fresh interpreter, exclude profile loading, collection and destruction from CPU time."""
    root = Path(os.environ["MENU_BENCH_DIR"]).resolve() / revision
    sys.path.insert(0, str(root / "cli_help"))
    from core import load_profiles
    from ui import Browser

    for profile in load_profiles(root / "profiles"):
        rows = [option for category in profile["categories"] for option in category["options"]]
        refs = [key for option in rows if (key := single_reference(option)) is not None]
        gc.collect()
        start = time.process_time_ns()
        browser = Browser(profile)
        elapsed_ms = (time.process_time_ns() - start) / 1e6
        del browser
        if pair:
            print(json.dumps([" ".join(profile["command"]), revision, pair,
                              len(rows), len(refs), len(set(refs)), elapsed_ms]))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        for pair in range(13):
            order = ("before", "after") if pair % 2 == 0 else ("after", "before")
            for revision in order:
                subprocess.run([sys.executable, "-B", __file__, revision, str(pair)], check=True)
    else:
        sweep(sys.argv[1], int(sys.argv[2]))
