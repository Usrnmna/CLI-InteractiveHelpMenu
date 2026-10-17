"""Compare saved update conflicts and apply explicit, backed-up file choices."""

import argparse
import ast
import difflib
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

import installation as install
from guided_merge import GuidedMerge


MAX_TEXT_BYTES = 512 * 1024
PAGE_LINES = 20
STATE = "review-state.json"


def display(text):
    """Escape terminal controls and bidirectional formatting in untrusted text."""
    return "".join(char if char.isprintable() or char in "\n\t" else ascii(char)[1:-1] for char in str(text))


def read_bytes(path):
    """Read a bounded regular file without accepting symlink components."""
    install.safe_path(path)
    if not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError(f"Expected a regular file no larger than {MAX_TEXT_BYTES} bytes: {path}")
    with path.open("rb") as stream:
        data = stream.read(MAX_TEXT_BYTES + 1)
    if len(data) > MAX_TEXT_BYTES:
        raise ValueError("File grew beyond the review size limit.")
    return data


def read_json(path):
    """Read bounded JSON metadata without executing file content."""
    return json.loads(read_bytes(path))


def file_state(root, name):
    """Describe a path without following a link or opening a special file."""
    install.safe_path(root)
    path = root
    for component in Path(name).parts:
        path = path / component
        try:
            info = path.lstat()
        except FileNotFoundError:
            return {"kind": "missing"}
        if stat.S_ISLNK(info.st_mode):
            return {"kind": "blocked", "path": str(path.relative_to(root)), "link": os.readlink(path)}
        if path != root / name and not stat.S_ISDIR(info.st_mode):
            return {"kind": "blocked", "path": str(path.relative_to(root)), "mode": info.st_mode}
    if not stat.S_ISREG(info.st_mode):
        return {"kind": "blocked", "mode": info.st_mode}
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            checksum.update(block)
    return {"kind": "file", "sha256": checksum.hexdigest(), "size": info.st_size,
            "mode": stat.S_IMODE(info.st_mode)}


def text_content(data):
    """Require bounded UTF-8 text for diffing and editing; binary copying is separate."""
    if len(data) > MAX_TEXT_BYTES or b"\0" in data:
        raise ValueError("Binary or oversized content cannot be shown or edited as text.")
    text = data.decode("utf-8")
    if len(text.splitlines()) > 10000:
        raise ValueError("Text exceeds the 10,000-line comparison limit.")
    return text


def atomic_bytes(path, data):
    """Replace review metadata atomically, retaining exact recovery bytes."""
    install.safe_path(path)
    descriptor, temporary = tempfile.mkstemp(prefix=".review-state-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def atomic_json(path, value):
    """Serialize review metadata through the atomic replacement helper."""
    atomic_bytes(path, (json.dumps(value, indent=2) + "\n").encode("utf-8"))


class ReviewSession:
    """Maintain comparison snapshots and queued choices for one installed runtime.

    The original report is immutable. Decisions are saved separately; unchanged
    local choices remain protected by their original installation ownership hash.
    """

    def __init__(self, report_path):
        self.path = install.safe_path(report_path)
        self.report_bytes = read_bytes(self.path)
        self.report = json.loads(self.report_bytes)
        if not isinstance(self.report, dict) or not isinstance(self.report.get("prefix"), str):
            raise ValueError("Expected an update report with an installation prefix.")
        self.prefix = install.safe_path(self.report["prefix"])
        self.folder = self.path.parent
        if (self.path.name != "report.json" or self.folder.parent != self.prefix.parent
                or not self.folder.name.startswith(self.prefix.name + ".update-backup-")):
            raise ValueError("Select report.json in its original sibling update-backup directory.")
        self.manifest = install.load_manifest(self.prefix)
        self.manifest_bytes = read_bytes(self.prefix / install.MARKER)
        records = self.report.get("preserved")
        if not isinstance(records, list):
            raise ValueError("The report requires a preserved conflict list.")
        self.records = {}
        for entry in records:
            if (not isinstance(entry, dict) or not isinstance(entry.get("path"), str)
                    or not install.allowed_file(entry["path"]) or entry["path"] in self.records
                    or not isinstance(entry.get("reason"), str)):
                raise ValueError("Invalid or duplicate conflict path.")
            install.safe_path(self.folder / "incoming" / entry["path"])
            self.records[entry["path"]] = entry
        self.incoming = self.folder / "incoming"
        install.safe_path(self.incoming)
        if not self.incoming.is_dir():
            raise ValueError("The incoming distribution is missing.")
        self.incoming_snapshot = install.tree_state(self.incoming)
        self.state_path = self.folder / STATE
        install.safe_path(self.state_path)
        self.state_bytes = read_bytes(self.state_path) if self.state_path.exists() else None
        self.state = json.loads(self.state_bytes) if self.state_bytes is not None else {"decisions": {}}
        if not isinstance(self.state, dict) or not isinstance(self.state.get("decisions"), dict):
            raise ValueError("Invalid review state.")
        for name, decision in self.state["decisions"].items():
            if (name not in self.records or not isinstance(decision, dict)
                    or decision.get("choice") not in {"local", "incoming", "edit"}
                    or any(not isinstance(decision.get(side), dict)
                           or decision[side].get("kind") not in {"missing", "file", "blocked"}
                           for side in ("local", "incoming"))):
                raise ValueError("Invalid saved review decision.")
        if self.state_bytes:
            if (self.state.get("schema_version") != 1
                    or self.state.get("report_sha256") != install.digest(self.report_bytes)):
                raise ValueError("Review state belongs to a different or changed report.")
            expected = self.state.get("manifest_sha256")
        else:
            expected = self.report.get("installed_manifest_sha256")
        self.legacy = self.report.get("schema_version") is None
        if self.legacy:
            if not self.state_bytes:
                self.validate_legacy_manifest()
        elif self.report.get("schema_version") != 1:
            raise ValueError("Unsupported update report version.")
        else:
            incoming_files = self.report.get("incoming_files")
            if not isinstance(incoming_files, dict) or not incoming_files:
                raise ValueError("The incoming distribution has no recorded checksums.")
            for name, checksum in incoming_files.items():
                if (not install.allowed_file(name) or not isinstance(checksum, str) or len(checksum) != 64
                        or file_state(self.incoming, name).get("sha256") != checksum):
                    raise ValueError("Incoming distribution changed since the update; create a fresh update report.")
            for name in self.records:
                decision = self.state["decisions"].get(name, {})
                resolved_deletion = (isinstance(decision, dict)
                                     and decision.get("local") == {"kind": "missing"})
                if name not in incoming_files and name not in self.manifest["files"] and not resolved_deletion:
                    raise ValueError("Conflict path is neither installed nor part of the incoming distribution.")
                if name not in incoming_files and file_state(self.incoming, name)["kind"] != "missing":
                    raise ValueError("An obsolete incoming path was added after the update.")
        if (not self.legacy or self.state_bytes) and expected != install.digest(self.manifest_bytes):
            raise ValueError("Installation metadata changed since this report; use the latest update report.")
        self.original = install.tree_state(self.prefix)
        if self.original.get(install.MARKER, (None, None))[1] != install.digest(self.manifest_bytes):
            raise ValueError("Installation metadata changed while opening review; retry.")
        self.choices = {}
        self.guided_drafts = {}

    def validate_legacy_manifest(self):
        """Reconstruct old unversioned reports without trusting arbitrary targets.

        Legacy reports did not record incoming checksums. Their current incoming
        files must be inspected as supplied; no historical integrity is inferred.
        """
        previous = read_json(self.folder / "previous" / install.MARKER)
        if not isinstance(previous, dict) or not isinstance(previous.get("files"), dict):
            raise ValueError("Legacy report requires its previous installation manifest.")
        ownership = dict(previous["files"])
        for action in ("updated", "added", "adopted", "removed"):
            names = self.report.get(action, [])
            if not isinstance(names, list) or any(not isinstance(name, str) or not install.allowed_file(name) for name in names):
                raise ValueError("Invalid legacy update path list.")
            for name in names:
                if action == "removed":
                    ownership.pop(name, None)
                else:
                    ownership[name] = install.digest(read_bytes(self.incoming / name))
        if {**previous, "files": ownership} != self.manifest:
            raise ValueError("Legacy report does not match the installed manifest; run update again.")

    def status(self, name):
        """Invalidate saved decisions when local or incoming content changes."""
        if name in self.choices:
            return "queued " + self.choices[name][0]
        decision = self.state["decisions"].get(name)
        if (isinstance(decision, dict) and decision.get("local") == file_state(self.prefix, name)
                and decision.get("incoming") == file_state(self.incoming, name)):
            return "saved " + str(decision.get("choice"))
        return "pending"

    def content(self, name, incoming=False):
        """Read comparison bytes, distinguishing missing files from blocked paths."""
        root = self.incoming if incoming else self.prefix
        state = file_state(root, name)
        if state["kind"] == "missing":
            return None
        if state["kind"] != "file":
            raise ValueError("Symlink, directory, or special-file conflict: keep local or resolve manually.")
        return read_bytes(root / name)

    def choose(self, name, choice, data=None):
        """Queue a reversible decision; no installed file is changed here."""
        if name not in self.records or choice not in {"local", "incoming", "edit"}:
            raise ValueError("Unknown conflict or choice.")
        if choice != "local":
            self.content(name)
            incoming = self.content(name, incoming=True)
            if choice == "incoming":
                data = incoming
            else:
                text = text_content(data)
                if name.endswith(".json"):
                    json.loads(text)
                elif name.endswith(".py"):
                    ast.parse(text, filename=name)
        self.choices[name] = (choice, data)

    def edit(self, name):
        """Launch an explicitly configured editor on a retained private draft."""
        seed = self.choices.get(name, (None, None))[1]
        if seed is None:
            seed = self.content(name)
        if seed is None:
            seed = self.content(name, incoming=True) or b""
        text_content(seed)
        editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "")
        if not editor:
            raise ValueError("Set VISUAL or EDITOR to an editor executable and optional arguments.")
        install.safe_path(self.folder)
        descriptor, draft_name = tempfile.mkstemp(prefix="review-draft-", suffix=Path(name).suffix, dir=self.folder)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(seed)
        print("Retained edit draft: " + display(draft_name), flush=True)
        result = subprocess.run([*editor, draft_name], cwd=self.folder, check=False)
        if result.returncode:
            raise ValueError("Editor failed; its draft remains available at the printed path.")
        self.choose(name, "edit", read_bytes(Path(draft_name)))

    def unchanged(self):
        """Reject stale inputs before and after staging, including another review."""
        for path in (self.prefix, self.incoming, self.state_path):
            install.safe_path(path)
        current_state = read_bytes(self.state_path) if self.state_path.exists() else None
        if (read_bytes(self.path) != self.report_bytes or current_state != self.state_bytes
                or install.tree_state(self.prefix) != self.original
                or install.tree_state(self.incoming) != self.incoming_snapshot):
            raise ValueError("Files or review metadata changed during review; reopen the report before saving.")

    def save(self):
        """Apply queued choices under the install lock with a complete rollback copy.

        A failed metadata write restores the original runtime. Both the previous
        and failed candidate remain available if recovery itself encounters errors.
        """
        if not self.choices:
            raise ValueError("No choices are queued.")
        with install.installation_lock(self.prefix):
            self.unchanged()
            with tempfile.TemporaryDirectory(prefix=".cli-help-stage-", dir=self.prefix.parent) as temporary:
                candidate = Path(temporary) / "runtime"
                shutil.copytree(self.prefix, candidate, symlinks=True)
                ownership = dict(self.manifest["files"])
                decisions = dict(self.state["decisions"])
                for name, (choice, data) in self.choices.items():
                    if choice != "local":
                        target = candidate / name
                        install.safe_path(target)
                        if data is None:
                            target.unlink(missing_ok=True)
                            ownership.pop(name, None)
                        else:
                            source = Path(temporary) / "selected"
                            source.write_bytes(data)
                            source.chmod(0o755 if name.endswith(".sh") else 0o644)
                            install.replace_staged_file(source, target)
                            if choice == "incoming" or data == self.content(name, incoming=True):
                                ownership[name] = install.digest(data)
                    decisions[name] = {"choice": choice, "local": file_state(candidate, name),
                                       "incoming": file_state(self.incoming, name)}
                manifest = {**self.manifest, "files": ownership}
                marker = candidate / install.MARKER
                marker.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
                state = {"schema_version": 1, "report_sha256": install.digest(self.report_bytes),
                         "manifest_sha256": install.digest(marker.read_bytes()), "decisions": decisions}
                self.unchanged()
                backup = Path(tempfile.mkdtemp(prefix=self.prefix.name + ".update-review-backup-", dir=self.prefix.parent))
                (backup / "review-state.before.json").write_bytes(self.state_bytes or b"null\n")
                atomic_json(backup / "decisions.json", state)
                print("Review backup: " + display(backup), flush=True)
                self.prefix.rename(backup / "previous")
                try:
                    candidate.rename(self.prefix)
                    atomic_json(self.state_path, state)
                except BaseException:
                    if self.prefix.exists():
                        self.prefix.rename(backup / "failed-runtime")
                    (backup / "previous").rename(self.prefix)
                    # An interruption can arrive just after atomic state replacement.
                    # Restore only this save's state, never a different writer's data.
                    if self.state_path.exists() and read_json(self.state_path) == state:
                        if self.state_bytes is None:
                            self.state_path.unlink()
                        else:
                            atomic_bytes(self.state_path, self.state_bytes)
                    raise
        self.__init__(self.path)
        return backup


def paged(lines):
    """Display bounded pages without starting a shell or external pager."""
    for start in range(0, len(lines), PAGE_LINES):
        for line in lines[start:start + PAGE_LINES]:
            clean = display(line.rstrip("\n"))
            print(clean[:500] + (" ... [line truncated]" if len(clean) > 500 else ""))
        if start + PAGE_LINES < len(lines) and input("Enter: next page; q: back > ").strip().lower() == "q":
            break


def review_entry(session, name):
    """Compare one entry and queue a file-level selection or a manually edited merge."""
    while True:
        print("\nConflict: " + display(name) + " [" + display(session.status(name)) + "]")
        print("Reason: " + display(session.records[name]["reason"]))
        for label, root in (("Local", session.prefix), ("Incoming", session.incoming)):
            print(label + ": " + display(json.dumps(file_state(root, name), sort_keys=True)))
        print("d diff | l local | i incoming | m merged draft | k keep local | r use incoming (delete if absent)")
        print("g guided changes | e external editor | x clear | b back")
        command = input("Choice > ").strip().lower()
        try:
            if command in {"d", "l", "i"}:
                local = session.content(name) if command != "i" else None
                incoming = session.content(name, incoming=True) if command != "l" else None
                if command == "d":
                    print("Local: " + ("missing" if local is None else f"{len(local)} bytes") +
                          "; incoming: " + ("deleted" if incoming is None else f"{len(incoming)} bytes"))
                    lines = list(difflib.unified_diff(text_content(local or b"").splitlines(keepends=True),
                                                     text_content(incoming or b"").splitlines(keepends=True),
                                                     fromfile="local/" + name, tofile="incoming/" + name))
                    paged(lines or ["No text differences."])
                else:
                    data = incoming if command == "i" else local
                    paged(text_content(data).splitlines() if data is not None else ["File absent."])
            elif command == "m":
                choice, data = session.choices.get(name, (None, None))
                if choice != "edit":
                    raise ValueError("No edited merge is queued.")
                paged(text_content(data).splitlines())
            elif command in {"k", "r"}:
                session.choose(name, "local" if command == "k" else "incoming")
                return
            elif command == "e":
                session.edit(name)
                return
            elif command == "g":
                guided_edit(session, name)
            elif command == "x":
                session.choices.pop(name, None)
                session.guided_drafts.pop(name, None)
            elif command == "b":
                return
            else:
                print("Unknown choice.")
        except (OSError, ValueError, SyntaxError, RecursionError) as error:
            print(display(error))


def guided_edit(session, name):
    """Review individual changed blocks and queue a validated merge without an editor."""
    local = session.content(name)
    incoming = session.content(name, incoming=True)
    text_content(local or b"")
    text_content(incoming or b"")
    draft = session.guided_drafts.get(name)
    if draft is None:
        draft = GuidedMerge(local, incoming)
        session.guided_drafts[name] = draft
    elif (draft.local, draft.incoming) != (local, incoming):
        raise ValueError("Comparison files changed; clear the guided draft or reopen the report.")
    if not draft.changes:
        print("No changes to select.")
        return
    index = 0
    while True:
        kind, start, end, new_start, new_end = draft.changes[index]
        decision = {None: "undecided", True: "accept incoming", False: "keep local"}[draft.accepted[index]]
        print(f"\nGuided change {index + 1}/{len(draft.changes)}: {kind} [{decision}]")
        print(f"Local lines {start + 1}-{end}; incoming lines {new_start + 1}-{new_end}")
        lines = ["LOCAL (" + ("missing" if local is None else "present") + ")"]
        lines += ["- " + line.decode("utf-8").rstrip("\n") for line in draft.local_lines[start:end]]
        lines += ["INCOMING (" + ("deletion" if incoming is None else "present") + ")"]
        lines += ["+ " + line.decode("utf-8").rstrip("\n") for line in draft.incoming_lines[new_start:new_end]]
        paged(lines)
        print("a accept | r reject | n/p next/previous | v preview | d queue result | b back")
        command = input("Guided > ").strip().lower()
        try:
            if command in {"a", "r"}:
                draft.decide(index, command == "a")
                index = min(index + 1, len(draft.changes) - 1)
            elif command == "n":
                index = min(index + 1, len(draft.changes) - 1)
            elif command == "p":
                index = max(0, index - 1)
            elif command == "v":
                result = draft.result(require_complete=False)
                print("Preview keeps undecided changes local.")
                paged(text_content(result).splitlines() if result is not None else ["File absent."])
            elif command == "d":
                result = draft.result()
                if result == local:
                    session.choose(name, "local")
                elif result == incoming:
                    session.choose(name, "incoming")
                else:
                    session.choose(name, "edit", result)
                print("Guided result queued; save from the review menu to apply it.")
                return
            elif command == "b":
                return
            else:
                print("Select a guided editing command.")
        except (ValueError, SyntaxError, RecursionError) as error:
            print(display(error))


def interactive(session):
    """Review a paginated queue and require confirmation before saving decisions."""
    names = list(session.records)
    page = 0
    print("Update conflict review: " + display(session.prefix))
    if session.legacy:
        print("Legacy report: incoming files have no historical checksums; inspect comparisons before saving.")
    while True:
        for index in range(page, min(page + 12, len(names))):
            name = names[index]
            print(f"{index + 1}. {display(name)} [{display(session.status(name))}]")
        print(f"{len(session.choices)} queued; number: compare | n/p: pages | s: save | q: quit")
        command = input("Review > ").strip().lower()
        if command == "q":
            if not (session.choices or session.guided_drafts) or input("Discard queued choices? [y/N] > ").strip().lower() == "y":
                return
        elif command == "s":
            for name, (choice, data) in session.choices.items():
                action = "incoming deletion" if choice == "incoming" and data is None else choice
                print(display(name) + ": " + action)
            if session.choices and input("Apply queued choices with backups? [y/N] > ").strip().lower() == "y":
                session.save()
                print("Choices saved. Open a new Bash session after reviewing runtime changes.")
        elif command == "n":
            page = page + 12 if page + 12 < len(names) else page
        elif command == "p":
            page = max(0, page - 12)
        elif command.isdecimal() and 0 < int(command) <= len(names):
            review_entry(session, names[int(command) - 1])
        else:
            print("Select a listed number or menu command.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="report.json printed by update.sh")
    args = parser.parse_args()
    try:
        if not sys.platform.startswith("linux") or sys.version_info < (3, 10):
            raise ValueError("Update review requires Linux and Python 3.10 or newer.")
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("Interactive update review requires a terminal.")
        interactive(ReviewSession(args.report))
    except (EOFError, KeyboardInterrupt):
        print("\nReview cancelled; unsaved choices were discarded.")
        return 130
    except (OSError, ValueError, RecursionError) as error:
        print("Update review: " + display(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
