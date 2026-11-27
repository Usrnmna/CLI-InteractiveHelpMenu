"""Plan the manual CI pilot and reconcile its unittest evidence per Python target."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
from statistics import median
import sys
import unittest

from timed_unittest import test_ids


TESTS = Path(__file__).resolve().parent
TARGETS = ("3.10", "3.12", "3.14")
SHARDS = (1, 2, 3)
# Reserve time for the existing once-per-version checks, including package verification.
EXTRA_SECONDS = 45


def partition(ids, weights):
    """Assign whole flat test modules longest-first; unknown modules use the target median."""
    modules = {name.partition(".")[0] for name in ids}
    if len(modules) < len(SHARDS) or len(ids) != len(set(ids)):
        raise ValueError("Discovery must contain unique IDs and at least three modules")
    estimate = median(weights.values())
    costs = {module: weights.get(module, estimate) for module in modules}
    loads = [EXTRA_SECONDS, 0, 0]
    owners = {}
    empty = set(range(len(SHARDS)))
    for position, module in enumerate(sorted(modules, key=lambda name: (-costs[name], name))):
        # Reserve one module for each remaining empty shard, even in a small suite.
        candidates = sorted(empty) if len(modules) - position == len(empty) else range(len(SHARDS))
        index = min(candidates, key=loads.__getitem__)
        empty.discard(index)
        owners[module] = index + 1
        loads[index] += costs[module]
    groups = [[name for name in ids if owners[name.partition(".")[0]] == shard] for shard in SHARDS]
    if not all(groups):
        raise ValueError("Empty shard")
    return groups, loads, sorted(modules - weights.keys())


def plan(shard, directory, commit):
    """Discover on this interpreter; write the manifest and ordered runner arguments."""
    target = f"{sys.version_info.major}.{sys.version_info.minor}"
    loader = unittest.TestLoader()
    suite = loader.discover(str(TESTS), pattern="test_*.py")
    if loader.errors:
        raise ValueError("\n".join(loader.errors))
    ids = list(test_ids(suite))
    weights = json.loads((TESTS / "ci-module-seconds.json").read_text())[target]
    groups, loads, unknown = partition(ids, weights)
    selected = groups[shard - 1] if shard else ids
    manifest = dict(target=target, python=sys.version.split()[0], image=os.getenv("ImageVersion", ""),
                    commit=commit, shard=shard, discovery=ids, selected=selected,
                    estimated_seconds=loads[shard - 1] if shard else sum(loads), untimed_modules=unknown)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (directory / "selected.txt").write_text("\n".join(selected) + "\n")
    print(f"Python {target}, shard {shard}: {len(selected)}/{len(ids)} tests; "
          f"estimated {manifest['estimated_seconds']:.0f}s including assigned standalone checks")
    if unknown:
        print("Modules using the median estimate:", ", ".join(unknown))


def check_execution(selected, events):
    """Account for every selected ID using ordered case callbacks or explicit setup skips."""
    if not events or events[0]["event"] != "suite-start" or events[-1]["event"] != "suite-end":
        raise ValueError("Incomplete timing stream")
    if events[-1]["exit_code"] != 0 or events[-1]["phase"] != "unittest":
        raise ValueError("Suite failed or stopped during preflight")
    started = [e["test"] for e in events if e["event"] == "test-start"]
    ended = [e for e in events if e["event"] == "test-end"]
    summaries = [e for e in events if e["event"] == "unittest-end"]
    if len(summaries) != 1 or summaries[0]["tests_run"] != len(ended):
        raise ValueError("Unittest completion count differs from recorded cases")
    if any(summaries[0][key] for key in ("errors", "failures", "unexpected_successes")):
        raise ValueError("Unittest reported unsuccessful outcomes")
    outcomes = {}
    costs = Counter()
    for row in ended:
        name = row["test"]
        if not row["outcomes"] or any(result["status"] not in ("pass", "skip", "expected-failure")
                                      for result in row["outcomes"]):
            raise ValueError(f"Unsuccessful or incomplete outcome: {name}")
        outcomes[name] = row["outcomes"]
        costs[name.partition(".")[0]] += row["seconds"]
    setup_skips = set()
    for row in events:
        if row["event"] != "fixture-outcome":
            continue
        match = re.fullmatch(r"setUp(?:Class|Module) \(([^)]+)\)", row["test"])
        if not match or row["status"] != "skip":
            raise ValueError(f"Unresolved fixture outcome: {row}")
        affected = [name for name in selected if name.startswith(match[1] + ".")]
        if not affected or any(name in outcomes for name in affected):
            raise ValueError(f"Inconsistent fixture skip: {row['test']}")
        for name in affected:
            outcomes[name] = [dict(status="fixture-skip", fixture=row["test"], reason=row["reason"])]
        setup_skips.update(affected)
    expected = [name for name in selected if name not in setup_skips]
    if expected != started or expected != [e["test"] for e in ended]:
        missing = sorted(set(expected) - set(started))
        duplicates = [name for name, n in Counter(started).items() if n > 1]
        raise ValueError(f"Execution differs from assignment (missing={missing}, duplicates={duplicates}, "
                         f"unexpected={sorted(set(started) - set(expected))}, check order and end events)")
    return outcomes, costs, events[-1]["monotonic"] - events[0]["monotonic"]


def collect(directory, target, commit, shards):
    """Validate coverage across a target's artifacts and report its measured suite costs."""
    reference = None
    identity = None
    combined = {}
    modules = set()
    durations = {}
    costs = Counter()
    for shard in shards:
        suffix = f"-shard-{shard}" if shard else ""
        folder = directory / f"linux-tests-python-{target}{suffix}"
        manifest = json.loads((folder / "manifest.json").read_text())
        ids, selected = manifest["discovery"], manifest["selected"]
        if (manifest["commit"], manifest["target"], manifest["shard"]) != (commit, target, shard):
            raise ValueError(f"{folder.name}: wrong commit, target, or shard")
        runtime = (manifest["python"], manifest["image"])
        if reference is None:
            reference, identity = ids, runtime
        if ids != reference or runtime != identity or len(ids) != len(set(ids)) or not selected:
            raise ValueError(f"{folder.name}: inconsistent discovery, runtime, or empty assignment")
        selection = set(selected)
        if selected != [name for name in ids if name in selection]:
            raise ValueError(f"{folder.name}: assignment differs from unique discovery order")
        overlap = combined.keys() & set(selected)
        if overlap:
            raise ValueError(f"{folder.name}: repeated IDs {sorted(overlap)}")
        assigned_modules = {name.partition(".")[0] for name in selected}
        if modules & assigned_modules:
            raise ValueError(f"{folder.name}: split modules {sorted(modules & assigned_modules)}")
        modules.update(assigned_modules)
        events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]
        if not shard and [row["tests"] for row in events if row["event"] == "discovery-end"] != [ids]:
            raise ValueError(f"{folder.name}: control run discovered different IDs")
        try:
            outcomes, module_seconds, durations[shard] = check_execution(selected, events)
        except ValueError as error:
            raise ValueError(f"{folder.name}: {error}") from error
        combined.update(outcomes)
        costs.update(module_seconds)
    if combined.keys() != set(reference):
        raise ValueError(f"Python {target}: missing={sorted(set(reference) - combined.keys())}, "
                         f"unexpected={sorted(combined.keys() - set(reference))}")
    slowest = max(durations, key=durations.get)
    skips = sum(any("skip" in result["status"] for result in values) for values in combined.values())
    print(f"Python {target}: {len(combined)} IDs, {skips} with skips; "
          f"slowest suite {slowest} at {durations[slowest]:.1f}s; top module by case time {costs.most_common(1)}")
    return reference, identity, combined


def verify(directory, commit, control=None):
    """Fail for any missing shard or outcome drift from an optional same-commit control."""
    failed = False
    for target in TARGETS:
        try:
            ids, runtime, actual = collect(directory, target, commit, SHARDS)
            if control:
                baseline, control_runtime, expected = collect(control, target, commit, (0,))
                if ids != baseline or runtime != control_runtime:
                    raise ValueError("Control discovery or runtime identity differs")
                drift = [name for name in ids if actual[name] != expected[name]]
                if drift:
                    raise ValueError(f"Outcomes or skip reasons differ from the control: {drift}")
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"Python {target}: {error}", file=sys.stderr)
            failed = True
    return int(failed)


def main():
    """Create one target-local plan or verify the downloaded pilot artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planner = commands.add_parser("plan")
    planner.add_argument("--shard", type=int, choices=(0, *SHARDS), required=True)
    checker = commands.add_parser("verify")
    checker.add_argument("--control", type=Path)
    for command in (planner, checker):
        command.add_argument("directory", type=Path)
        command.add_argument("--commit", required=True)
    args = parser.parse_args()
    if args.command == "plan":
        sys.path.insert(0, str(TESTS.parent))
        plan(args.shard, args.directory, args.commit)
        return 0
    return verify(args.directory, args.commit, args.control)


if __name__ == "__main__":
    raise SystemExit(main())
