"""Build a literal text merge from explicit decisions on changed line blocks."""

from difflib import SequenceMatcher


class GuidedMerge:
    """Keep original bytes and per-block decisions without mutating either input.

    Line terminators are retained. Adjacent changed lines form one block; equal
    lines separate blocks. A missing file differs from a present empty file.
    """

    def __init__(self, local, incoming):
        self.local = local
        self.incoming = incoming
        self.local_lines = (local or b"").splitlines(keepends=True)
        self.incoming_lines = (incoming or b"").splitlines(keepends=True)
        self.operations = SequenceMatcher(None, self.local_lines, self.incoming_lines).get_opcodes()
        self.changes = [operation for operation in self.operations if operation[0] != "equal"]
        if not self.changes and (local is None) != (incoming is None):
            self.changes = [("existence", 0, 0, 0, 0)]
        self.accepted = [None] * len(self.changes)

    def decide(self, index, accept):
        """Accept incoming content or reject it in favor of the local block."""
        if type(index) is not int or not 0 <= index < len(self.changes) or type(accept) is not bool:
            raise ValueError("A valid change index and an accept/reject decision are required.")
        self.accepted[index] = accept

    def result(self, require_complete=True):
        """Assemble selected bytes; previews temporarily keep undecided local blocks."""
        if require_complete and None in self.accepted:
            raise ValueError("Accept or reject every change before queuing the merge.")
        if not self.changes or not any(value is True for value in self.accepted):
            return self.local
        if all(value is True for value in self.accepted):
            return self.incoming
        pieces = []
        index = 0
        for kind, start, end, new_start, new_end in self.operations:
            use_incoming = False
            if kind != "equal":
                use_incoming = self.accepted[index] is True
                index += 1
            pieces.extend(self.incoming_lines[new_start:new_end] if use_incoming else self.local_lines[start:end])
        return b"".join(pieces)
