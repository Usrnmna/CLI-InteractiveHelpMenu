"""Resolve the local impact map against unittest discovery inside the extracted sandbox."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
YQ_DIR = Path("tests/reports/yq-revisit")
YQ_CLIENTS = {str(YQ_DIR / ("yq-" + v)) for v in ("4.44.3", "4.54.3")}
NOBLE_IP = "tests/reports/iproute2-revisit/noble-client.tgz"
LYCHEE = "tests/reports/lychee"
LYCHEE_CA = "tests/reports/lychee-ca.pem"
LINK_GATE = "offline Markdown links and fragments including inbound links"
IP_GATE = "packaged iproute2 listing and option probe"


def leaves(suite):
    """Yield test cases in the order and class groupings of ordinary discovery."""
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from leaves(case)
        else:
            yield case


def link_roots():
    """Locate public roots needed to initialize Lychee even in its offline mode."""
    for bundle in (Path(LYCHEE_CA), Path("/etc/ssl/certs/ca-certificates.crt")):
        if bundle.is_file():
            return {"SSL_CERT_FILE": str(bundle.resolve())}
    directory = Path("/usr/share/ca-certificates/mozilla")
    if any(directory.glob("*.crt")):
        return {"SSL_CERT_DIR": str(directory)}
    return {}


def selection(delta, config, cases, target):
    """Build a serializable plan from snapshot paths, discovered cases and target-local fixtures."""
    indexed = {}
    routes = {}
    fallback = []
    for case in cases:
        name = case.id()
        if name in indexed:
            fallback.append("duplicate discovery ID: " + name)
        indexed[name] = case
        method = getattr(case, getattr(case, "_testMethodName", ""), None)
        route = getattr(method, "command_path", None)
        if route:
            routes.setdefault(route, []).append(name)

    groups = {}
    reasons = {}
    fixtures = {}
    gates = ["shell syntax", "numerical review", "collection", "example driver collection"]
    changes = delta["changes"]
    docs = any(p.endswith(".md") for p in changes)
    if docs:
        gates.append(LINK_GATE)
        fixtures[LYCHEE] = os.access(LYCHEE, os.X_OK) or bool(shutil.which("lychee"))
        roots = link_roots()
        fixtures[next(iter(roots.values()), LYCHEE_CA)] = bool(roots)
    if delta["unresolved"]:
        fallback.append("unresolved untracked paths: " + ", ".join(delta["unresolved"]))
    for path, status in sorted(changes.items()):
        owners = [f for f, spec in config["families"].items() if path in spec["inputs"]]
        if status == "added" and path in YQ_CLIENTS | {NOBLE_IP, LYCHEE, LYCHEE_CA}:
            continue  # Explicit offline tools accompany the source snapshot.
        if status == "deleted":
            fallback.append("deleted or renamed input: " + path)
        if not owners:
            fallback.append("shared or unmapped input: " + path)
        for family in owners:
            groups.setdefault(family, []).append(path)
    if not groups and not fallback:
        fallback.append("no mapped source changes")
    for family, paths in groups.items():
        spec = config["families"][family]
        reason = family + ": " + ", ".join(paths)
        if not spec["tests"] or not spec["routes"]:
            fallback.append("empty pilot group: " + family)
        for pattern in [*config["shared_tests"], *spec["tests"]]:
            matches = [name for name in indexed if name == pattern or name.startswith(pattern + ".")]
            if not matches:
                fallback.append("missing test or empty group: " + pattern)
            for name in matches:
                reasons.setdefault(name, set()).add(reason)
        for route in spec["routes"]:
            matches = routes.get(route, [])
            if len(matches) != 1:
                fallback.append("missing or ambiguous route: " + route)
            else:
                reasons.setdefault(matches[0], set()).add(reason)
        for path in [*config["shared_fixtures"], *spec["inputs"], *spec["fixtures"]]:
            fixtures[path] = Path(path).is_file()
        fixtures["tmux"] = bool(shutil.which("tmux"))
        if family == "iproute2":
            gates.append(IP_GATE)
            if target == "host":
                for program in ("ip", "ss"):
                    fixtures[program] = bool(shutil.which(program))
            else:
                fixtures[NOBLE_IP] = Path(NOBLE_IP).is_file()
    missing = sorted(path for path, found in fixtures.items() if not found)
    if missing:
        fallback.append("missing required fixtures: " + ", ".join(missing))
    if not indexed:
        fallback.append("empty discovery")
    # Keep common fallback reasons once, including when the plan contains thousands of IDs.
    tests = {name: sorted(reasons.get(name, ())) or ["full-suite fallback"]
             for name in indexed if fallback or name in reasons}
    expected_skips = {}
    for name in tests:
        case = indexed[name]
        for owner in (type(case), getattr(case, case._testMethodName, None)):
            if getattr(owner, "__unittest_skip__", False):
                expected_skips[name] = owner.__unittest_skip_why__
                break
    return dict(**delta, target=target, expected_skips=expected_skips,
                required_targets=["host", "noble310", "noble312"] if fallback else [target],
                suite="full" if fallback else "selected", fallback=fallback,
                fixtures=fixtures, missing=missing, gates=gates, tests=tests)


def check_ip_clients(target):
    """Exercise the read-only client probe inside the private network and temporary filesystem."""
    probe = ["python3", "tests/fixtures/iproute2/check-packaged.py"]
    if target == "host":
        return subprocess.run([*probe, "ip", "ss"]).returncode
    with tempfile.TemporaryDirectory() as folder:
        subprocess.run(["tar", "-xzf", NOBLE_IP, "-C", folder], check=True)
        root = Path(folder)
        environment = dict(os.environ, LD_LIBRARY_PATH=str(root / "lib/x86_64-linux-gnu"))
        return subprocess.run([*probe, root / "bin/ip", root / "bin/ss"], env=environment).returncode


def check_links():
    """Scan all maintained Markdown for local targets and inbound anchors in the offline sandbox."""
    checker = LYCHEE if os.access(LYCHEE, os.X_OK) else "lychee"
    return subprocess.run([checker, "--offline", "--config", "lychee.toml", "--no-progress",
                           "**/*.md", ".github/CONTRIBUTING.md", ".github/pull_request_template.md"],
                          env={**os.environ, **link_roots()}).returncode


def execute(plan):
    """Use the full suite's preflight and unittest runner, propagating failures and incomplete inputs."""
    argv = ["bash", "tests/run.sh"]
    if plan["suite"] == "selected":
        argv.extend(["--selected", *plan["tests"]])
    status = subprocess.run(argv).returncode
    if status:
        return status
    if plan["unresolved"] or plan["missing"] or not plan["tests"]:
        return 1
    if LINK_GATE in plan["gates"]:
        status = check_links()
        if status:
            return status
    if IP_GATE in plan["gates"]:
        return check_ip_clients(plan["target"])
    return 0


def main():
    """Discover without running cases or their class fixtures; report import failures explicitly."""
    delta, target, mode = sys.argv[1:]
    delta = json.loads(delta)
    if all(Path(p).is_file() for p in YQ_CLIENTS):
        os.environ["YQ_TEST_BINDIR"] = str(YQ_DIR.resolve())
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py")
    try:
        config = json.loads((ROOT / "tests/test-impact.json").read_text())
        plan = selection(delta, config, leaves(suite), target)
    except (OSError, ValueError, KeyError, TypeError) as error:
        plan = selection(delta, {"families": {}}, leaves(suite), target)
        plan["fallback"].append(f"unusable impact map: {error}")
    if loader.errors:
        plan["suite"] = "full"
        plan["required_targets"] = ["host", "noble310", "noble312"]
        plan["fallback"].extend(loader.errors)
        plan["tests"] = {case.id(): ["incomplete discovery"] for case in leaves(suite)}
    print(json.dumps(plan, indent=2), flush=True)
    if mode == "execute":
        return execute(plan)
    return int(bool(delta["unresolved"] or plan["missing"] or loader.errors or not plan["tests"]))


if __name__ == "__main__":
    sys.exit(main())
