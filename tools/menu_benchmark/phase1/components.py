"""Isolated warm component measurements. Run from the repository root with system Python."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from contextlib import ExitStack
from unittest.mock import patch

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / name) for name in ("cli_help", "tests")]
from core import find_context, load_profiles
from test_discovery import HELP_TEXT, make_commands, write_executable


def emit(**record):
    print(json.dumps(record), flush=True)


def load_once(folder, custom=None):
    """Exclude interpreter startup from the load timer, include it in peak RSS."""
    cpu = time.process_time_ns()
    wall = time.monotonic_ns()
    profiles = load_profiles(Path(folder), custom)
    elapsed = (time.monotonic_ns() - wall) / 1e6
    cpu_ms = (time.process_time_ns() - cpu) / 1e6
    line = "git worktree remove "
    start = time.process_time_ns()
    assert find_context(line, len(line), profiles).profile["command"] == line.split()
    lookup = (time.process_time_ns() - start) / 1e6
    fields = Path("/proc/self/status").read_text().splitlines()
    peak = int(next(row for row in fields if row.startswith("VmHWM:")).split()[1])
    emit(count=len(profiles), wall=elapsed, cpu=cpu_ms, lookup=lookup, peak=peak,
         file_bytes=sum(path.stat().st_size for path in Path(folder).glob("*.json")))


def load_sweep(folder):
    """Hold the requested file constant and add unrelated valid profiles."""
    paths = sorted((ROOT / "profiles").glob("*.json"))
    selected = ROOT / "profiles/git-worktree-remove.json"
    paths.remove(selected)
    targets = []
    for count in (1, 19, 76, 152):
        dest = folder / str(count)
        dest.mkdir()
        for path in [selected, *paths][:count]:
            shutil.copyfile(path, dest / path.name)
        if count > 76:
            for path in [selected, *paths]:
                extra = json.loads(path.read_bytes())
                extra["command"] = ["benchmark", *extra["command"]]
                if extra.get("switch_syntax") == "7zip":
                    # The reserved end marker is valid only for the two 7-Zip command paths.
                    extra = dict(json.loads(selected.read_bytes()), command=extra["command"])
                extra.pop("identity", None)
                extra.pop("switch_syntax", None)
                (dest / ("extra-" + path.name)).write_text(json.dumps(extra, ensure_ascii=False, indent=2))
        targets.append(dest)
    for i in range(21):
        for dest in (targets if i % 2 else reversed(targets)):
            data = subprocess.check_output([sys.executable, __file__, "load-one", str(dest)])
            if i:
                emit(trial=i, **json.loads(data))


def timed_call(owner, name, clock, totals, counts, key=None):
    """Report inclusive time per function, optionally distinguishing actual probe argv."""
    original = getattr(owner, name)
    def measured(*args, **kwargs):
        label = key(*args, **kwargs) if key else name
        start = clock()
        try:
            return original(*args, **kwargs)
        finally:
            duration = (clock() - start) / 1e6
            if name == "concise_description":
                caller = "clean-from-" + sys._getframe(1).f_code.co_name
                totals[caller] += duration
                counts[caller] += 1
            totals[label] += duration
            counts[label] += 1
    return patch.object(owner, name, measured)


def load_stages(custom=None):
    """Attribute the full collection's warm load CPU by operation and command relevance."""
    import core
    for trial in range(13):
        totals, counts = Counter(), Counter()
        def group(path):
            return "selected" if path.name == "git-worktree-remove.json" else "unrelated"
        with ExitStack() as scope:
            scope.enter_context(timed_call(Path, "read_text", time.process_time_ns, totals, counts))
            scope.enter_context(timed_call(json, "loads", time.process_time_ns, totals, counts))
            scope.enter_context(timed_call(core, "read_json", time.process_time_ns, totals, counts,
                                          lambda path: "read/" + group(path)))
            scope.enter_context(timed_call(core, "validate_profile", time.process_time_ns, totals, counts,
                                          lambda profile, path: "validate/" + group(path)))
            scope.enter_context(timed_call(core, "require_text", time.process_time_ns, totals, counts))
            profiles = core.load_profiles(ROOT / "profiles", custom)
            if custom is None:
                assert len(profiles) == 76
        if trial:
            emit(trial=trial, ms=totals, count=counts)


def discovery_cases(folder):
    """Time real local fixture executables through the normal guarded static context."""
    import discovery as d
    from command_paths import load_driver_registry
    command, _, executed = make_commands(folder)
    yq = command.parent / "yq"
    flag = folder / "wrong"
    stall = folder / "stall-identity"
    write_executable(yq, "import os, sys, time\n"
                     f"if sys.argv[1:] == ['--version'] and os.path.exists({str(stall)!r}): time.sleep(2)\n"
                     f"if sys.argv[1:] == ['--version']: print('wrong' if os.path.exists({str(flag)!r}) "
                     "else 'yq (https://github.com/mikefarah/yq/) version v4.44.3')\n"
                     f"elif sys.argv[1:] == ['eval', '--help']: print({HELP_TEXT!r})\n"
                     "else: raise SystemExit(9)\n")
    profiles = load_profiles(ROOT / "profiles")
    registry = load_driver_registry(ROOT / "config/drivers.example")
    settings = d.Settings(cache_dir=folder / "cache")
    def resolve(name, subcommands=()):
        return d.discover(name, settings, subcommands=subcommands, driver_registry=registry)
    for trial in range(13):
        for guarded in (False, True):
            line = "yq eval " if guarded else "discover-tool "
            for state in ("miss", "hit", "expired", "bad-identity") if guarded else ("miss", "hit", "expired"):
                if state == "miss":
                    shutil.rmtree(settings.cache_dir, ignore_errors=True)
                if state == "expired":
                    for path in settings.cache_dir.glob("*.json"):
                        document = json.loads(path.read_bytes())
                        path.write_text(json.dumps(dict(document, created=0)))
                if state == "bad-identity":
                    flag.touch()
                totals, counts = Counter(), Counter()
                with ExitStack() as scope:
                    scope.enter_context(patch.dict(os.environ, PATH=str(command.parent)))
                    for name in ("verify_command_variant", "cache_identity", "parse_command_help", "merge_documents",
                                 "read_cache", "write_cache"):
                        scope.enter_context(timed_call(d, name, time.monotonic_ns, totals, counts))
                    def label(argv, *args, **kwargs):
                        return "probe:" + ("version" if argv[1:] == ["--version"] else Path(argv[0]).name)
                    scope.enter_context(timed_call(d, "run_probe", time.monotonic_ns, totals, counts, label))
                    start = time.monotonic_ns()
                    try:
                        result = find_context(line, len(line), profiles, discover=resolve, driver_registry=registry)
                        assert state != "bad-identity"
                        assert ("discovery" not in result.profile) == guarded
                    except d.HelpError as error:
                        assert state == "bad-identity" and "different or unverified" in str(error)
                    elapsed = (time.monotonic_ns() - start) / 1e6
                probes = sum(v for k, v in counts.items() if k.startswith("probe:"))
                assert counts["probe:version"] == int(guarded)
                assert probes == int(guarded) + (0 if state in ("hit", "bad-identity") else 1 + int(not guarded)), (state, counts)
                assert not executed.exists()
                flag.unlink(missing_ok=True)
                if trial:
                    emit(trial=trial, command=line.strip(), state=state, wall=elapsed, ms=totals, count=counts)

    # A fresh, valid entry exists. A timed-out identity check must reject before reading it.
    stall.touch()
    with patch.dict(os.environ, PATH=str(command.parent)), patch.object(d, "read_cache", side_effect=AssertionError):
        try:
            d.discover("yq", d.Settings(cache_dir=settings.cache_dir, timeout=0.15),
                       subcommands=("eval",), driver_registry=registry)
            raise AssertionError("unverified guard accepted")
        except d.ProbeError as error:
            assert error.code == "probe_timeout"



def presentation():
    """Record inclusive constructor and draw-path CPU in separate instrumented replays."""
    import presentation as p
    import ui
    from test_numerical_presentation import CellScreen
    keys = ui.load_keys()
    for name in ("ffmpeg", "git-worktree-remove"):
        profile = json.loads((ROOT / "profiles" / (name + ".json")).read_bytes())
        for trial in range(9):
            totals, counts = Counter(), Counter()
            with ExitStack() as scope:
                for owner, fn in ((ui, "option_text"), (p, "description_blocks"), (p, "concise_description"),
                                  (p, "terminal_prose"), (p, "value_text"), (ui.Browser, "options"),
                                  (ui, "option_label_width"), (ui, "wrap_cells")):
                    scope.enter_context(timed_call(owner, fn, time.process_time_ns, totals, counts))
                def step(label, action):
                    totals.clear()
                    counts.clear()
                    start = time.process_time_ns()
                    result = action()
                    if trial:
                        emit(trial=trial, name=name, stage=label, cpu=(time.process_time_ns() - start)/1e6,
                             ms=totals, count=counts)
                    return result
                b = step("constructor", lambda: ui.Browser(profile))
                for level in ui.LEVELS:
                    b.level = level
                    step(level, lambda: ui.draw(CellScreen(24, 80), b, keys))
                b.level = "Simple"
                step("first-bps", lambda: (b.set_query("bps"), ui.draw(CellScreen(24, 80), b, keys)))
                step("repeat-bps", lambda: ui.draw(CellScreen(24, 80), b, keys))


if __name__ == "__main__":
    if sys.argv[1] == "load-one":
        load_once(sys.argv[2], Path(sys.argv[3]) if len(sys.argv) > 3 else None)
    else:
        with tempfile.TemporaryDirectory() as scratch:
            if sys.argv[1] == "load":
                load_sweep(Path(scratch))
            elif sys.argv[1] == "load-stages":
                load_stages(Path(sys.argv[2]) if len(sys.argv) > 2 else None)
            elif sys.argv[1] == "discovery":
                discovery_cases(Path(scratch))
            elif sys.argv[1] == "presentation":
                presentation()
