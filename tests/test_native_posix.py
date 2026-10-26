"""Verify real local POSIX processes, permissions and collection recovery.

Child processes run only closed test operations. Checkpoints pause execution at
inspected write boundaries; locks, replacements, signals and files remain real.
TemporaryDirectory follows the explicitly selected TMPDIR for filesystem runs.
"""

from contextlib import ExitStack
from copy import deepcopy
import json
import os
from pathlib import Path
import select
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
if sys.platform.startswith("linux"):
    from collection import inspect_collection, restore_review_backup
    from core import HelpError
    import manual_import
    from manual_import import ManualCollection, atomic_bytes, atomic_json
    from review import ReviewSession


class Checkpoint:
    """Send bounded child events and wait for an explicit parent release."""
    def __init__(self, events, control):
        self.events, self.control = events, control

    def emit(self, event):
        os.write(self.events, (json.dumps({"event": event}) + "\n").encode())

    def pause(self, event):
        self.emit(event)
        if os.read(self.control, 1) != b"g":
            raise RuntimeError("The owned checkpoint was not released")


class OwnedChild:
    """Own one forked test operation and reap only its recorded PID."""
    def __init__(self, operation):
        self.events, events_out = os.pipe()
        control_in, self.control = os.pipe()
        self.status = None
        self.pid = os.fork()
        if self.pid == 0:
            os.close(self.events)
            os.close(self.control)
            checkpoint = Checkpoint(events_out, control_in)
            try:
                operation(checkpoint)
                checkpoint.emit("finished")
                os._exit(0)
            except BaseException as error:
                os.write(events_out, (json.dumps({"event": "error", "type": type(error).__name__, "detail": str(error)}) + "\n").encode())
                os._exit(1)
        os.close(events_out)
        os.close(control_in)
        self.buffer = b""

    def receive(self, timeout=8):
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.events], [], [], max(0, remaining))[0]:
                raise AssertionError("Owned child did not reach its checkpoint")
            chunk = os.read(self.events, 65536)
            if not chunk:
                raise AssertionError("Owned child exited without the expected event")
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line)

    def release(self):
        os.write(self.control, b"g")

    def join(self):
        deadline = time.monotonic() + 8
        while self.status is None and time.monotonic() < deadline:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                self.status = os.waitstatus_to_exitcode(status)
                break
            time.sleep(0.01)
        if self.status is None:
            raise AssertionError("Owned child did not terminate within its deadline")
        return self.status

    def close(self):
        if self.status is None:
            try:
                os.kill(self.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status = os.waitpid(self.pid, 0)
            self.status = os.waitstatus_to_exitcode(status)
        os.close(self.events)
        os.close(self.control)


@unittest.skipUnless(sys.platform.startswith("linux") and hasattr(os, "fork"), "Native POSIX checks require Linux and fork")
class NativePosixTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-native-posix-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.root = self.folder / "collection"
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen", "socket.socket",
                     "socket.create_connection", "socket.getaddrinfo", "urllib.request.urlopen",
                     "discovery.run_probe", "manual_import.run_probe"):
            stack.enter_context(patch(name, side_effect=AssertionError("Native filesystem test attempted a target or network operation")))
        stack.enter_context(patch.dict(os.environ, {"CLI_HELP_DRIVERS": ""}))
        self.profile = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        with ManualCollection(self.root) as collection:
            self.paths = collection.save(self.profile, "synthetic-contract")
        self.report = self.root / "scan-report.json"
        atomic_json(self.report, {"schema_version": 1, "finished": True, "records": [
            {"command": self.profile["command"], "status": "needs_adjustment", "generated": True}]})

    def child(self, operation):
        child = OwnedChild(operation)
        self.addCleanup(child.close)
        return child

    def bytes(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in (Path(self.paths["profile"]), Path(self.paths["driver"]), self.report)}

    def changed(self, session):
        draft = session.open_draft(0)
        document = draft.document()
        document["profile"]["categories"][0]["name"] = "Reviewed specimen"
        draft.text = json.dumps(document, ensure_ascii=False)
        return draft

    def test_actual_process_locks_contend_and_normal_exit_releases_them(self):
        before = self.bytes()
        def holder(checkpoint):
            with ReviewSession(self.report):
                checkpoint.pause("locked")
        child = self.child(holder)
        self.assertEqual(child.receive(), {"event": "locked"})
        for owner in (ManualCollection(self.root), ReviewSession(self.report)):
            with self.assertRaises(HelpError):
                with owner:
                    self.fail("A second process acquired an existing writer lock")
        self.assertIn("lock_ownership_uncertain", {f["code"] for f in inspect_collection(self.root)["findings"]})
        self.assertEqual(self.bytes(), before)
        child.release()
        self.assertEqual(child.receive(), {"event": "finished"})
        self.assertEqual(child.join(), 0)
        self.assertFalse((self.root / ".scan.lock").exists())
        self.assertFalse((self.root / ".import.lock").exists())

    def test_atomic_replacement_preserves_old_open_descriptor_and_complete_new_bytes(self):
        target = self.folder / "atomic.json"
        old, new = b'{"state":"old"}\n', b'{"state":"new","padding":"' + b"x" * 100000 + b'"}\n'
        target.write_bytes(old)
        def writer(checkpoint):
            atomic_bytes(target, new, before_replace=lambda: checkpoint.pause("staged"))
        with target.open("rb") as original:
            child = self.child(writer)
            self.assertEqual(child.receive(), {"event": "staged"})
            self.assertEqual(target.read_bytes(), old)
            child.release()
            self.assertEqual(child.receive(), {"event": "finished"})
            self.assertEqual(child.join(), 0)
            self.assertEqual(original.read(), old)
        self.assertEqual(target.read_bytes(), new)
        self.assertEqual(sorted(path.name for path in self.folder.iterdir()), ["atomic.json", "collection"])

    def test_real_permission_denial_preserves_saved_pair_and_retains_backup(self):
        directory = self.root / "profiles"
        if os.geteuid() == 0:
            self.skipTest("Root bypasses the permission boundary; an unprivileged run is required")
        before = self.bytes()
        with ReviewSession(self.report) as session:
            draft = self.changed(session)
            mode = directory.stat().st_mode & 0o777
            try:
                directory.chmod(0o500)
                try:
                    descriptor = os.open(directory / "permission-witness", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                except PermissionError:
                    pass
                else:
                    os.close(descriptor)
                    (directory / "permission-witness").unlink()
                    self.skipTest("This filesystem does not enforce chmod write denial; no permission result is established")
                with self.assertRaisesRegex(HelpError, "Save incomplete"):
                    session.save(draft)
                self.assertEqual(self.bytes(), before)
                self.assertTrue(session.save_failed)
                self.assertTrue(list((self.root / ".review-backups").glob("*/manifest.json")))
                self.assertNotEqual(draft.text, draft.original)
            finally:
                directory.chmod(mode)
        self.assertFalse((self.root / ".scan.lock").exists())
        self.assertFalse((self.root / ".import.lock").exists())

    def test_sigkill_before_replace_retains_original_and_diagnosable_temporary(self):
        target = Path(self.paths["profile"])
        before = target.read_bytes()
        def writer(checkpoint):
            descriptor = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                atomic_bytes(target, b'{"staged":"not published"}\n', directory_fd=descriptor,
                             before_replace=lambda: checkpoint.pause("staged"))
            finally:
                os.close(descriptor)
        child = self.child(writer)
        self.assertEqual(child.receive(), {"event": "staged"})
        os.kill(child.pid, signal.SIGKILL)
        self.assertEqual(child.join(), -signal.SIGKILL)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(len(list(target.parent.glob(".cli-help-write-*.tmp"))), 1)
        self.assertIn("temporary_write_present", {f["code"] for f in inspect_collection(self.root)["findings"]})

    def test_concurrent_file_change_and_cancelled_draft_do_not_overwrite_saved_data(self):
        before = self.bytes()
        with ReviewSession(self.report) as session:
            self.changed(session)
        self.assertEqual(self.bytes(), before)
        self.assertFalse((self.root / ".review-backups").exists())
        with ReviewSession(self.report) as session:
            draft = self.changed(session)
            target = Path(self.paths["profile"])
            external = deepcopy(self.profile)
            external["description"] = "Concurrent synthetic writer"
            def writer(checkpoint):
                atomic_json(target, external)
            child = self.child(writer)
            self.assertEqual(child.receive(), {"event": "finished"})
            self.assertEqual(child.join(), 0)
            saved = target.read_bytes()
            with self.assertRaisesRegex(HelpError, "changed outside"):
                session.save(draft)
            self.assertEqual(target.read_bytes(), saved)
            self.assertNotEqual(draft.text, draft.original)
        self.assertFalse((self.root / ".scan.lock").exists())
        self.assertFalse((self.root / ".import.lock").exists())

    def test_interrupted_pair_save_keeps_backup_and_guarded_recovery_restores_bytes(self):
        for interrupt in (signal.SIGINT, signal.SIGKILL):
            with self.subTest(signal=interrupt):
                before = self.bytes()
                previous = set((self.root / ".review-backups").iterdir()) if (self.root / ".review-backups").exists() else set()
                target = Path(self.paths["profile"])
                def writer(checkpoint):
                    original = manual_import.atomic_json
                    def checkpoint_after_profile(path, document, **kwargs):
                        original(path, document, **kwargs)
                        if Path(path) == target:
                            checkpoint.pause("profile_replaced")
                    try:
                        with patch("manual_import.atomic_json", checkpoint_after_profile), ReviewSession(self.report) as session:
                            session.save(self.changed(session))
                    except HelpError as error:
                        if "Save incomplete" not in str(error):
                            raise
                        checkpoint.emit("interrupted")
                child = self.child(writer)
                self.assertEqual(child.receive(), {"event": "profile_replaced"})
                owned = {name: (self.root / name).stat().st_ino for name in (".scan.lock", ".import.lock")}
                os.kill(child.pid, interrupt)
                if interrupt == signal.SIGINT:
                    self.assertEqual(child.receive(), {"event": "interrupted"})
                    self.assertEqual(child.receive(), {"event": "finished"})
                    self.assertEqual(child.join(), 0)
                    self.assertTrue(all(not (self.root / name).exists() for name in owned))
                else:
                    self.assertEqual(child.join(), -signal.SIGKILL)
                    state = inspect_collection(self.root)
                    name = next(iter(set((self.root / ".review-backups").iterdir()) - previous)).name
                    with self.assertRaises(HelpError) as raised:
                        restore_review_backup(self.root, name, state["snapshot"])
                    self.assertEqual(raised.exception.code, "collection_locked")
                    # Only the test's known-dead child locks are released. The
                    # application never infers that age/PID proves staleness.
                    for lock, inode in owned.items():
                        path = self.root / lock
                        self.assertEqual(path.stat().st_ino, inode)
                        self.assertEqual(path.read_bytes(), b"")
                        path.unlink()
                self.assertNotEqual(target.read_bytes(), before[str(target.relative_to(self.root))])
                backup = next(iter(set((self.root / ".review-backups").iterdir()) - previous))
                self.assertTrue((backup / "manifest.json").exists())
                state = inspect_collection(self.root)
                result = restore_review_backup(self.root, backup.name, state["snapshot"])
                self.assertEqual(result["status"], "restored")
                self.assertEqual(self.bytes(), before)
                self.assertTrue(Path(result["backup"]).is_dir())
                repeated = restore_review_backup(self.root, backup.name, inspect_collection(self.root)["snapshot"])
                self.assertEqual(repeated["status"], "unchanged")


if __name__ == "__main__":
    unittest.main()
