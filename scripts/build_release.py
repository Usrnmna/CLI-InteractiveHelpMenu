"""Build deterministic Linux release archives, a native launcher, and SHA-256 files."""

import argparse
from contextlib import ExitStack
import fnmatch
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORIES = ("bash", "cli_help", "config", "docs", "native", "profiles", "scripts", "tests", "tools", ".github")
SOURCE_FILES = ("VERSION", "README.md", "CHANGELOG.md", "install.sh", "uninstall.sh", "update.sh",
                "review-update.sh", "update-from-github.sh", ".gitignore", ".gitattributes", ".editorconfig", "lychee.toml")
PRIVATE_DIRECTORIES = frozenset({".git", ".cache", ".venv", "venv", "__pycache__", "reports", "dist",
    "generated-help", "node_modules", "htmlcov", ".review-backups", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".aws", ".azure", ".ssh", ".gnupg", ".kube", ".docker", ".dotnet", ".nuget", ".bun", ".ansible", ".arduino15", ".npm"})
PRIVATE_NAMES = frozenset({".import.lock", ".scan.lock", ".cli-help-install.json", ".git-credentials", ".netrc",
    ".pypirc", ".bash_history", ".python_history", ".lesshst", ".wget-hsts", ".lycheecache", ".coverage",
    ".DS_Store", "Thumbs.db", "Desktop.ini"})
PRIVATE_PATHS = ((".config", "gcloud"), (".config", "gh"), (".config", "cli-help"),
                 (".config", "containers"), (".local", "share", "containers"),
                 (".local", "share", "cli-interactive-help"))
PRIVATE_PATTERNS = ("*.pyc", "*.pyo", "*.swp", "*.swo", "*~", ".coverage.*", ".cli-help-write-*.tmp",
    ".cli-help-rc-*", ".review-state-*", ".cli-help-stage-*", "*.install.lock", "*.update-backup-*",
    "*.update-review-backup-*", "*.release-update-*", "*.cli-help-backup-*")
PRIVATE_DIRECTORY_PATTERNS = ("cli-help-installer.*",
    "cli-help-probe-*", "cli-help-review-*", "cli-help-screen-*", "cli-help-build-*", "cli-help-media-*",
    "cli-help-ignore-*", "cli-help-inventory-*", "cli-help-capture-*", "cli-help-functional-review-*",
    "cli-help-workflow-verification-*")


def excluded_source(relative, directory=False):
    """Exclude reserved private/generated names without hiding authored examples or media."""
    if any(relative.parts[index:index + len(parts)] == parts
           for parts in PRIVATE_PATHS for index in range(len(relative.parts))):
        return True
    for index, part in enumerate(relative.parts):
        if part in PRIVATE_DIRECTORIES or part in PRIVATE_NAMES:
            return True
        if part == ".env" or part.startswith(".env.") and not part.endswith((".example", ".sample", ".template")):
            return True
        if any(fnmatch.fnmatchcase(part, pattern) for pattern in PRIVATE_PATTERNS):
            return True
        if (directory or index < len(relative.parts) - 1) and any(fnmatch.fnmatchcase(part, pattern) for pattern in PRIVATE_DIRECTORY_PATTERNS):
            return True
    return False


def source_files(root):
    """Select maintained source, documentation, and fixtures without local reports or caches."""
    files = [root / name for name in SOURCE_FILES]
    for directory in SOURCE_DIRECTORIES:
        source = root / directory
        if source.is_symlink() or source.exists() and not source.is_dir():
            raise ValueError("Maintained release input directories must be real directories.")
        if not source.exists():
            continue
        def unreadable(error):
            raise error
        for parent, directories, names in os.walk(source, followlinks=False, onerror=unreadable):
            directories[:] = sorted(name for name in directories if not excluded_source((Path(parent) / name).relative_to(root), directory=True))
            for name in directories + sorted(names):
                path = Path(parent) / name
                if excluded_source(path.relative_to(root), directory=name in directories):
                    continue
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                    raise ValueError(f"Release inputs must be regular files or real directories: {path}")
                if stat.S_ISREG(mode):
                    files.append(path)
    for path in files:
        relative = path.relative_to(root).as_posix()
        if "\\" in relative or any(ord(character) < 32 or ord(character) == 127 for character in relative):
            raise ValueError("Release input paths must not contain backslashes or control characters.")
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked release input: {path}")
        if any(parent.is_symlink() for parent in path.parents if root in parent.parents):
            raise ValueError(f"Symlinked release input directory: {path}")
    return sorted(files)


def read_source(root, relative):
    """Capture a regular input through pinned, no-follow directory/file descriptors.

    Enumeration is only a preliminary check. Each open refuses symlinks and
    special files, and identity checks reject replacements or edits during a
    read. This is a per-file capture, not an atomic multi-file snapshot.
    """
    message = "Release source is unsafe or changed during capture; use stable regular files and real directories."
    def identity(metadata):
        return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
                metadata.st_mtime_ns, metadata.st_ctime_ns)
    try:
        with ExitStack() as descriptors:
            directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.callback(os.close, directory)
            root_identity = os.fstat(directory)
            parents = []
            for part in relative.parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                descriptors.callback(os.close, child)
                parents.append((directory, part, os.fstat(child)))
                directory = child
            descriptor = os.open(relative.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory)
            descriptors.callback(os.close, descriptor)
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError(message)
            chunks = []
            remaining = before.st_size + 1
            while remaining:
                chunk = os.read(descriptor, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            after = os.fstat(descriptor)
            named = os.stat(relative.name, dir_fd=directory, follow_symlinks=False)
            data = b"".join(chunks)
            if len(data) != before.st_size or identity(before) != identity(after) or identity(after) != identity(named):
                raise ValueError(message)
            # Pinning prevents traversal escapes; these checks also refuse a
            # renamed/replaced directory even when its descriptor stays usable.
            for parent, name, expected in parents:
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if (current.st_dev, current.st_ino, current.st_mode) != (expected.st_dev, expected.st_ino, expected.st_mode):
                    raise ValueError(message)
            current_root = root.stat(follow_symlinks=False)
            if (current_root.st_dev, current_root.st_ino) != (root_identity.st_dev, root_identity.st_ino):
                raise ValueError(message)
            return data
    except OSError:
        raise ValueError(message) from None


def archive(files, top):
    """Create a reproducible gzip/tar payload with normalized modes and timestamps."""
    result = io.BytesIO()
    with gzip.GzipFile(fileobj=result, mode="wb", mtime=0, filename="") as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as bundle:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo(top + "/" + name)
                member.size = len(data)
                member.mode = 0o755 if name.endswith(".sh") or name == "cli-help" else 0o644
                member.mtime = 0
                bundle.addfile(member, io.BytesIO(data))
    return result.getvalue()


def installer(payload, top):
    """Wrap a verified runtime archive with an installer that forwards literal arguments."""
    checksum = hashlib.sha256(payload).hexdigest()
    header = f'''#!/usr/bin/env bash
# Self-extracting Linux installation package; inspect the source archive for implementation.
set -euo pipefail
if [[ ${{1:-}} == --help ]]; then
    printf '%s\\n' 'Usage: bash installer.run [install|update] [--prefix PATH] [installer options]' 'Use --verify to check the embedded archive without installing.'
    exit 0
fi
action=install
case "${{1:-}}" in
    install|update) action=$1; shift ;;
    --verify) action=verify; shift ;;
esac
stage=$(mktemp -d "${{TMPDIR:-/tmp}}/cli-help-installer.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
archive="$stage/runtime.tar.gz"
tail -n +PAYLOAD_LINE -- "$0" > "$archive"
printf '%s  %s\\n' '{checksum}' "$archive" | sha256sum -c - >/dev/null
if [[ $action == verify ]]; then
    printf '%s\\n' 'Embedded archive checksum verified.'
    exit 0
fi
tar --no-same-owner -xzf "$archive" -C "$stage"
status=0
bash "$stage/{top}/$action.sh" "$@" || status=$?
if [[ $status == 2 && $action == update ]]; then
    trap - EXIT
    printf 'Source retained for conflict review: %s\\n' "$stage/{top}"
fi
exit "$status"
'''
    header = header.replace("PAYLOAD_LINE", str(header.count("\n") + 1))
    return header.encode() + payload


def build(root, destination):
    """Compile the native convenience launcher and write complete versioned deliverables."""
    root = root.resolve(strict=True)
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("This release builder currently targets Linux x86_64.")
    version = read_source(root, Path("VERSION")).decode("utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-z0-9.]+)?", version):
        raise ValueError("VERSION must contain a simple semantic version.")
    if destination.exists() or destination.is_symlink():
        raise ValueError("The output directory already exists; select a new directory to preserve previous builds.")
    destination = destination.resolve()
    if any(destination == root / name or root / name in destination.parents for name in SOURCE_DIRECTORIES):
        raise ValueError("Release output must be outside maintained source directories; use dist/ or .cache/.")
    selected = source_files(root)
    contents = {path.relative_to(root).as_posix(): read_source(root, path.relative_to(root)) for path in selected}
    if contents["VERSION"].decode("utf-8").strip() != version:
        raise ValueError("VERSION changed during source capture; repeat the build from stable inputs.")
    if "native/cli_help.c" not in contents:
        raise ValueError("The native launcher source is missing from release inputs.")
    compiler = shutil.which(os.environ.get("CC", "gcc"))
    if not compiler:
        raise ValueError("A C compiler is required; install GCC or set CC to its executable.")
    with tempfile.TemporaryDirectory(prefix="cli-help-build-") as temporary:
        source = Path(temporary) / "cli_help.c"
        source.write_bytes(contents["native/cli_help.c"])
        executable = Path(temporary) / "cli-help"
        subprocess.run([compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=none", "-s",
                        f'-DCLI_HELP_VERSION="{version}"', str(source), "-o", str(executable)], check=True)
        binary = executable.read_bytes()
        subprocess.run([str(executable), "--version"], check=True)
    base = f"cli-interactive-help-v{version}"
    top = base
    binary_name = f"cli-help-v{version}-linux-x86_64"
    runtime = archive({**contents, "cli-help": binary}, top)
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
    info = {"version": version, "platform": "linux-x86_64", "python_required": "3.10+", "bash_required": "4.4+",
            "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
            "build_platform": platform.platform(), "source_files": manifest}
    artifacts = {f"{base}-source.tar.gz": archive(contents, top),
                 f"{base}-linux-x86_64.tar.gz": runtime,
                 f"{base}-linux-x86_64.run": installer(runtime, top),
                 binary_name: binary,
                 "BUILD-INFO.json": (json.dumps(info, indent=2, sort_keys=True) + "\n").encode()}
    destination.mkdir(parents=True)
    checksums = []
    for name, data in artifacts.items():
        path = destination / name
        path.write_bytes(data)
        if name.endswith(".run") or name == binary_name:
            path.chmod(0o755)
        line = f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        (destination / (name + ".checksum")).write_text(line, encoding="utf-8")
        checksums.append(line)
    (destination / "SHA256SUMS.checksum").write_text("".join(checksums), encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory for release artifacts")
    args = parser.parse_args()
    try:
        print("Built release: " + str(build(ROOT, args.output.absolute())))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
