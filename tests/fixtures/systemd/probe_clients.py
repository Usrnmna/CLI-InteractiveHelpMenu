"""Probe the two Ubuntu packages using disposable journal data in the host sandbox.

Pass an extracted Noble fixture directory containing systemctl, journalctl,
systemd-journal-remote and its private libraries. Resolute clients come from
/usr/bin. No probe uses a host journal, a service manager or a remote machine.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run(command, arguments, libraries=None, *, input_text=None, success=True):
    """Run a client with explicit bus isolation and return its uncolored stdout."""
    env = dict(os.environ, TMPDIR="/tmp", LC_ALL="C", SYSTEMD_COLORS="0", SYSTEMD_PAGER="cat",
               DBUS_SYSTEM_BUS_ADDRESS="unix:path=/nonexistent/systemd-probe",
               DBUS_SESSION_BUS_ADDRESS="unix:path=/nonexistent/systemd-probe")
    if libraries:
        env["LD_LIBRARY_PATH"] = str(libraries)
    result = subprocess.run([str(command), *arguments], env=env, input=input_text,
                            text=True, capture_output=True, timeout=10)
    assert (result.returncode == 0) == success, (arguments, result.returncode, result.stderr)
    return result.stdout.strip()


def check_clients(noble, directory):
    """Import labeled events once and verify query, cursor and parser contracts."""
    journal = directory / "fixture.journal"
    records = []
    for index, message in enumerate(("one", "two", "three"), 1):
        identifier = "first" if index == 1 else "next"
        invocation = ("a" if index < 3 else "b") * 32
        records.append(f"__REALTIME_TIMESTAMP={1700000000 + index}000000\n"
                       f"__MONOTONIC_TIMESTAMP={index}000000\n_BOOT_ID={'1' * 32}\n"
                       f"_MACHINE_ID={'2' * 32}\n_SYSTEMD_UNIT=fixture.service\n"
                       f"_SYSTEMD_INVOCATION_ID={invocation}\nSYSLOG_IDENTIFIER={identifier}\n"
                       f"MESSAGE={message}\n\n")
    run(noble / "systemd-journal-remote", ["--output=" + str(journal), "-"],
        noble, input_text="".join(records))
    for label, binaries, libs in (("Noble", noble, noble), ("Resolute", Path("/usr/bin"), None)):
        jctl = binaries / "journalctl"
        ctl = binaries / "systemctl"
        print(label, run(jctl, ["--version"], libs).splitlines()[0], flush=True)
        assert run(ctl, ["--version"], libs).splitlines()[0] == run(jctl, ["--version"], libs).splitlines()[0]
        base = ["--file=" + str(journal), "--no-pager", "-o", "cat"]
        assert run(jctl, [*base, "-t", "first"], libs) == "one"
        assert run(jctl, [*base, "-g", "^t"], libs).splitlines() == ["two", "three"]
        cursor = directory / ("cursor-" + label)
        first = [*base, "--cursor-file=" + str(cursor)]
        assert run(jctl, [*first, "-t", "first"], libs) == "one"
        assert cursor.read_text().strip()
        assert run(jctl, first, libs).splitlines() == ["two", "three"]
        assert not run(jctl, first, libs)
        assert run(jctl, [*base, "-n0"], libs) == ""
        assert run(jctl, [*base, "-n", "+1"], libs) == "one"
        assert run(jctl, [*base, "--verify"], libs) == ""
        for flag in ("--interval=0", "--vacuum-time=invalid", "--vacuum-size=1MiB"):
            run(jctl, [flag, "--version"], libs, success=False)
        for flag in ("--interval=15min", "--vacuum-files=0", "--vacuum-size=1K"):
            run(jctl, [flag, "--version"], libs)
        # --version terminates after argument parsing, before any manager connection.
        for option in ("--with-dependencies", "--reverse", "--legend=no", "-PId"):
            run(ctl, ["show", option, "--version"], libs)
        run(ctl, ["show", "--introspect-cli", "--version"], libs, success=False)
        run(jctl, ["--introspect-cli", "--version"], libs, success=False)
        if label == "Resolute":
            short = run(jctl, [*base, "-o", "short", "-T", "first"], libs)
            assert [line.rsplit(": ", 1)[1] for line in short.splitlines()] == ["two", "three"]
            assert run(jctl, [*base, "-T", "first"], libs).splitlines() == ["one", "two", "three"]
            structured = run(jctl, [*base, "-o", "json", "-T", "first"], libs)
            assert [json.loads(line)["MESSAGE"] for line in structured.splitlines()] == ["one", "two", "three"]
            assert run(jctl, [*base, "-I", "-u", "fixture.service"], libs) == "three"
            assert run(jctl, [*base, "--invocation=-1", "-u", "fixture.service"], libs).splitlines() == ["one", "two"]
            assert run(jctl, [*base, "-I", "--invocation=all"], libs).splitlines() == ["one", "two", "three"]
            run(ctl, ["--capsule=test", "--version"], libs)
        else:
            for option in ("-I", "--invocation=0", "--list-namespaces", "-W", "-i", "-T"):
                run(jctl, [option, "--version"], libs, success=False)
            run(ctl, ["--capsule=test", "--version"], libs, success=False)
        print(label, "journal queries, cursor resumption and isolated option parsing passed", flush=True)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as scratch:
        check_clients(Path(sys.argv[1]).resolve(), Path(scratch))
