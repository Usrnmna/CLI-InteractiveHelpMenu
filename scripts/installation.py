"""Manage per-user runtime files and an explicitly delimited Bash startup block.

Only manifest-listed, unchanged regular files are removed. Startup edits use
byte-preserving backups and atomic replacement; no shell startup code is executed.
"""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid


ROOT = Path(__file__).resolve().parents[1]
MARKER = ".cli-help-install.json"
APPLICATION = "cli-interactive-help"
BEGIN = b"# >>> cli-interactive-help >>>"
END = b"# <<< cli-interactive-help <<<"
PAYLOAD = ("install.sh", "uninstall.sh", "scripts/installation.py", "bash/interactive-help.bash",
           "cli_help/*.py", "profiles/*.json", "config/keys.example.json", "config/drivers.example/*.json")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    """Return an absolute path, rejecting controls and symlinked components."""
    if any(ord(char) < 32 or ord(char) == 127 for char in str(value)):
        raise ValueError("Paths must not contain control characters.")
    path = Path(os.path.abspath(os.path.expanduser(str(value))))
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError(f"Symlinked paths are not supported: {component}")
    return path


def startup_block(prefix):
    """Quote the adapter path as literal Bash data, including spaces and apostrophes."""
    adapter = shlex.quote(str(prefix / "bash/interactive-help.bash"))
    return (BEGIN + b"\n" +
            f"if [[ $- == *i* && -r {adapter} ]]; then\n    source {adapter}\nfi\n".encode() +
            END + b"\n")


def block_span(data):
    """Locate exactly one complete managed block, refusing ambiguous markers."""
    lines = data.splitlines(keepends=True)
    begins = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == BEGIN]
    ends = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == END]
    if not begins and not ends:
        return None
    if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
        raise ValueError("The Bash rc file has incomplete or duplicate CLI help markers.")
    return sum(map(len, lines[:begins[0]])), sum(map(len, lines[:ends[0] + 1]))


def read_rc(path):
    """Read an existing regular startup file; absence is treated as empty content."""
    safe_path(path)
    if path.exists() and not path.is_file():
        raise ValueError(f"The Bash rc path is not a regular file: {path}")
    return path.read_bytes() if path.exists() else b""


def write_rc(path, before, after):
    """Back up existing bytes and replace the rc file only if it has not changed."""
    if before == after:
        return
    safe_path(path)
    if read_rc(path) != before:
        raise ValueError("The Bash rc file changed during installation; retry after inspecting it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    if path.exists():
        backup = path.with_name(path.name + ".cli-help-backup-" + uuid.uuid4().hex)
        with backup.open("xb") as stream:
            os.chmod(backup, mode)
            stream.write(before)
        print(f"Startup backup: {backup}")
    descriptor, temporary = tempfile.mkstemp(prefix=".cli-help-rc-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(after)
        if read_rc(path) != before:
            raise ValueError("The Bash rc file changed before replacement; no replacement was made.")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def allowed_file(name):
    """Restrict manifest paths to runtime payload locations, never arbitrary files."""
    path = Path(name)
    return (not path.is_absolute() and ".." not in path.parts and str(path) == name
            and any(path.match(pattern) and len(path.parts) == len(Path(pattern).parts)
                    for pattern in PAYLOAD))


def load_manifest(prefix):
    """Validate installation identity and deletion boundaries before any mutation."""
    marker = prefix / MARKER
    safe_path(marker)
    if not marker.is_file():
        raise ValueError(f"Refusing an unmanaged installation directory: {prefix}")
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("application") != APPLICATION or manifest.get("schema_version") != 1
            or manifest.get("prefix") != str(prefix)):
        raise ValueError("Installation metadata does not match this directory.")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Installation metadata has no valid file list.")
    for name, checksum in files.items():
        if (not allowed_file(name) or not isinstance(checksum, str) or len(checksum) != 64
                or any(char not in "0123456789abcdef" for char in checksum)):
            raise ValueError("Installation metadata contains an invalid file entry.")
    rc = manifest.get("rc_file")
    if rc is not None and (not isinstance(rc, str) or not Path(rc).is_absolute()):
        raise ValueError("Installation metadata contains an invalid Bash rc path.")
    if manifest.get("separator") not in ("", "\n"):
        raise ValueError("Installation metadata contains an invalid separator.")
    return manifest


@contextmanager
def installation_lock(prefix):
    """Serialize cooperating install/uninstall processes for one destination."""
    prefix.parent.mkdir(parents=True, exist_ok=True)
    lock = prefix.with_name(prefix.name + ".install.lock")
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def remove_files(prefix, manifest):
    """Remove unchanged managed files and empty directories; preserve everything else."""
    parents = set()
    retained = []
    for name, checksum in manifest["files"].items():
        path = prefix / name
        try:
            safe_path(path)
        except ValueError:
            retained.append(name)
            continue
        if path.is_file() and digest(path.read_bytes()) == checksum:
            path.unlink()
        elif path.exists():
            retained.append(name)
        parents.update(parent for parent in path.parents if parent != prefix and prefix in parent.parents)
    (prefix / MARKER).unlink()
    for directory in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        prefix.rmdir()
    except OSError:
        pass
    return retained


def install(prefix, rc):
    """Validate a staged payload, install once, and optionally add a startup block."""
    import curses  # Installation checks the browser dependency; uninstall does not need it.

    if prefix == ROOT or prefix in ROOT.parents or ROOT in prefix.parents:
        raise ValueError("The installation directory must be separate from the source checkout.")
    if rc is not None and (rc == prefix or prefix in rc.parents):
        raise ValueError("The Bash rc file must be outside the installation directory.")
    before = read_rc(rc) if rc else b""
    span = block_span(before)
    block = startup_block(prefix)
    if prefix.exists():
        manifest = load_manifest(prefix)
        if manifest["rc_file"] != (str(rc) if rc else None):
            raise ValueError("Existing installation uses different startup settings; uninstall it first.")
        source_names = {str(path.relative_to(ROOT)) for pattern in PAYLOAD for path in ROOT.glob(pattern)}
        if source_names != set(manifest["files"]):
            raise ValueError("The source payload changed; uninstall before installing this version.")
        for name, checksum in manifest["files"].items():
            path = safe_path(prefix / name)
            source = safe_path(ROOT / name)
            if (not path.is_file() or digest(path.read_bytes()) != checksum or not source.is_file()
                    or digest(source.read_bytes()) != checksum):
                raise ValueError("Installed or source files differ; uninstall before installing this version.")
        if rc and (span is None or before[span[0]:span[1]] != block):
            raise ValueError("The managed startup block was removed or edited; inspect it before reinstalling.")
        print(f"Already installed: {prefix}")
        return
    if span is not None:
        raise ValueError("A CLI help startup block already exists; uninstall that installation first.")
    separator = b"\n" if before and not before.endswith(b"\n") else b""
    files = {}
    with tempfile.TemporaryDirectory(prefix=".cli-help-stage-", dir=prefix.parent) as temporary:
        staging = Path(temporary) / "runtime"
        staging.mkdir()
        for pattern in PAYLOAD:
            matches = sorted(ROOT.glob(pattern))
            if not matches:
                raise ValueError(f"Missing source payload: {pattern}")
            for source in matches:
                safe_path(source)
                name = str(source.relative_to(ROOT))
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                if name in {"install.sh", "uninstall.sh"}:
                    target.chmod(0o755)
                files[name] = digest(target.read_bytes())
        environment = {key: value for key, value in os.environ.items() if not key.startswith("CLI_HELP_")}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        subprocess.run([sys.executable, str(staging / "cli_help/main.py"), "--check"],
                       check=True, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        manifest = {"application": APPLICATION, "schema_version": 1, "prefix": str(prefix),
                    "files": files, "rc_file": str(rc) if rc else None, "separator": separator.decode()}
        (staging / MARKER).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        staging.rename(prefix)
    try:
        if rc:
            write_rc(rc, before, before + separator + block)
    except Exception:
        remove_files(prefix, manifest)
        raise
    print(f"Installed: {prefix}")
    print("Open a new interactive Bash session, or load the adapter in the current session:")
    print("source " + shlex.quote(str(prefix / "bash/interactive-help.bash")))


def uninstall(prefix):
    """Remove one installation and its unmodified startup block, retaining user edits."""
    if not prefix.exists():
        print(f"No installation at: {prefix}")
        return
    manifest = load_manifest(prefix)
    rc = safe_path(manifest["rc_file"]) if manifest["rc_file"] else None
    if rc:
        before = read_rc(rc)
        span = block_span(before)
        if span:
            if before[span[0]:span[1]] != startup_block(prefix):
                raise ValueError("The managed startup block was edited; no files were removed.")
            start, end = span
            # Undo the inserted line separator only when the block remains at EOF.
            if manifest["separator"] and end == len(before) and start and before[start - 1:start] == b"\n":
                start -= 1
            write_rc(rc, before, before[:start] + before[end:])
    retained = remove_files(prefix, manifest)
    print(f"Uninstalled: {prefix}")
    if prefix.exists():
        print(f"Retained edited files, extra files, or runtime caches in: {prefix}")
    if retained:
        print("Retained managed paths: " + ", ".join(retained))
    print("Existing Bash sessions retain their binding; run cli_help_unbind or open a new session.")


def main():
    """Parse installation options and report failures without running pending commands."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--prefix", help="Installation directory (default: XDG_DATA_HOME/cli-interactive-help)")
    parser.add_argument("--rc-file", help="Bash startup file for install (default: ~/.bashrc)")
    parser.add_argument("--no-rc", action="store_true", help="Install without editing a Bash startup file")
    args = parser.parse_args()
    if args.action == "uninstall" and (args.rc_file or args.no_rc):
        parser.error("Uninstall uses the startup path saved during installation.")
    if args.no_rc and args.rc_file:
        parser.error("--no-rc and --rc-file cannot be combined.")
    try:
        if sys.version_info < (3, 10) or not sys.platform.startswith("linux"):
            raise ValueError("Installation requires Linux and Python 3.10 or newer.")
        data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
        if not data.is_absolute():
            raise ValueError("XDG_DATA_HOME must be absolute.")
        default = ROOT if args.action == "uninstall" and (ROOT / MARKER).exists() else data / APPLICATION
        prefix = safe_path(args.prefix or default)
        if prefix == Path(prefix.anchor) or prefix == Path.home():
            raise ValueError("The installation directory cannot be the filesystem root or home directory.")
        rc = None
        if args.action == "install" and not args.no_rc:
            rc = safe_path(args.rc_file or Path.home() / ".bashrc")
        with installation_lock(prefix):
            if args.action == "install":
                install(prefix, rc)
            else:
                uninstall(prefix)
    except (OSError, ValueError, subprocess.CalledProcessError, ImportError) as error:
        print(f"cli-help {args.action}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
