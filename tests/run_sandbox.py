"""Run tests against disposable working-tree copies on the host or Ubuntu 24.04."""

import argparse
import os
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"noble310": "3.10", "noble312": "3.12"}
PODMAN = ["podman", "--remote=false"]
ENVIRONMENT = {
    "HOME": "/tmp/home", "PATH": "/usr/bin:/bin", "SHELL": "/bin/bash",
    "LC_ALL": "C.UTF-8", "TERM": "xterm-256color", "PYTHONDONTWRITEBYTECODE": "1",
}
# Both backends unpack the same archive. Only the native sandbox needs a
# synthetic account database; the container runtime supplies its own.
BOOTSTRAP = """
set -eu
if [ "$(id -u)" = 0 ]; then echo 'Tests require an unprivileged user.' >&2; exit 1; fi
if [ "$1" = host ]; then
    printf 'tester:x:%s:%s:Test:/tmp/home:/bin/bash\n' "$(id -u)" "$(id -g)" > /etc/passwd
    printf 'tester:x:%s:\n' "$(id -g)" > /etc/group
fi
. /usr/lib/os-release
printf '%s | Bash %s | ' "$PRETTY_NAME" "$BASH_VERSION"
python3 -VV
if [ "$1" != host ]; then
    test "$ID:$VERSION_ID" = ubuntu:24.04
    python3 -c 'import sys; assert "%d.%d" % sys.version_info[:2] == sys.argv[1]' "$1"
fi
shift
mkdir -m 700 /tmp/home /tmp/src
cd /tmp/src
tar --no-same-owner -xf -
exec "$@" </dev/null
"""


def snapshot(stream, extra_files):
    """Archive tracked working-tree bytes and explicitly named new regular files."""
    listing = subprocess.check_output(["git", "ls-files", "--cached", "--deduplicate", "-z"], cwd=ROOT)
    tracked = {Path(os.fsdecode(name)) for name in listing.split(b"\0") if name}
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name in sorted(tracked.union(extra_files)):
            path = ROOT / name
            if (name.is_absolute() or ".." in name.parts or ".git" in name.parts
                    or path.parent.resolve() != path.parent):
                raise ValueError(f"Expected a path inside the checkout with real parent directories: {name}")
            try:
                mode = path.lstat().st_mode
            except FileNotFoundError:
                if name in extra_files:
                    raise
                continue  # A tracked deletion belongs in the snapshot.
            if not stat.S_ISREG(mode):
                raise ValueError(f"Expected a regular source file: {name}")
            archive.add(path, arcname=str(name), recursive=False)
    stream.seek(0)


def image_name(target):
    """Return the local image tag used by both preparation and offline runs."""
    return "localhost/cli-help-noble:" + TARGETS[target].replace(".", "")


def sandbox_command(target):
    """Construct an offline unprivileged process with private writable scratch space."""
    if target == "host":
        command = ["bwrap", "--unshare-all", "--new-session", "--die-with-parent", "--cap-drop", "ALL",
                   "--clearenv", "--ro-bind", "/usr", "/usr",
                   "--tmpfs", "/etc", "--ro-bind", "/etc/alternatives", "/etc/alternatives",
                   "--proc", "/proc", "--dev", "/dev", "--size", "1073741824", "--tmpfs", "/tmp",
                   "--chdir", "/tmp"]
        for directory in ("bin", "sbin", "lib", "lib64"):
            command.extend(["--symlink", "usr/" + directory, "/" + directory])
        for key, value in ENVIRONMENT.items():
            command.extend(["--setenv", key, value])
    else:
        command = [*PODMAN, "run", "--rm", "-i", "--pull=never", "--network=none",
                   "--userns=keep-id", "--cap-drop=all", "--security-opt=no-new-privileges",
                   "--http-proxy=false", "--read-only", "--read-only-tmpfs=false",
                   "--tmpfs=/tmp:rw,exec,nosuid,nodev,size=1g,mode=1777", "--pids-limit=256",
                   image_name(target), "/usr/bin/env", "-i"]
        command.extend(f"{key}={value}" for key, value in ENVIRONMENT.items())
    return [*command, "/bin/bash", "--noprofile", "--norc", "-c", BOOTSTRAP, "sandbox",
            TARGETS.get(target, "host")]


def main():
    """Prepare one image on request or run the supplied argv in a fresh sandbox."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["host", *TARGETS], default="host")
    parser.add_argument("--prepare", action="store_true", help="build the selected Ubuntu image with network access")
    parser.add_argument("--include", type=Path, action="append", default=[], metavar="FILE",
                        help="include an untracked file relative to the repository root (repeatable)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command after -- (default: bash tests/run.sh)")
    args = parser.parse_args()
    if os.getuid() == 0:
        parser.error("Run the sandbox runner as an ordinary user.")
    if args.prepare:
        if args.target == "host" or args.command or args.include:
            parser.error("--prepare takes only an Ubuntu image target.")
        with tempfile.TemporaryDirectory() as context:
            return subprocess.run([*PODMAN, "build", "--layers", "--target", args.target,
                                   "-t", image_name(args.target), "-f", str(ROOT / "tests/sandbox/Containerfile"),
                                   context]).returncode
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    with tempfile.TemporaryFile() as archive:
        snapshot(archive, set(args.include))
        return subprocess.run([*sandbox_command(args.target), *(command or ["bash", "tests/run.sh"])],
                              stdin=archive).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
