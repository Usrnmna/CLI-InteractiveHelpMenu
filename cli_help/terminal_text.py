"""Strip terminal sequences from Unicode text without interpreting terminal state.

Sequence shapes follow the xterm control reference:
https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
This is a text sanitizer, not a cursor, character-set or screen emulator.
"""


ESC = "\x1b"
CSI = "\x9b"
ST = "\x9c"
ESC_STRINGS = "]PX^_"  # OSC, DCS, SOS, PM, APC
C1_STRINGS = "\x9d\x90\x98\x9e\x9f"


def _csi_end(text, position):
    """Consume CSI parameters/intermediates and an optional final character.

    Incomplete syntax is discarded up to, but not including, an unexpected
    character. Newlines, Unicode prose and a new introducer remain available.
    """
    while position < len(text) and "0" <= text[position] <= "?":
        position += 1
    while position < len(text) and " " <= text[position] <= "/":
        position += 1
    if position < len(text) and "@" <= text[position] <= "~":
        position += 1
    return position


def _string_end(text, start, osc):
    """Find a control-string terminator without buffering the payload.

    ST terminates every string; BEL also terminates OSC. CAN/SUB cancel it.
    At a line boundary, ESC, other C1 control or EOF, preserve ambiguous payload
    by returning its start. A new introducer stops lookahead, so recovery scans
    each payload at most twice rather than repeatedly searching a shared suffix.
    """
    position = start
    while position < len(text):
        char = text[position]
        if char in (ST, "\x18", "\x1a") or osc and char == "\x07":
            return position + 1
        if char == ESC and position + 1 < len(text) and text[position + 1] == "\\":
            return position + 2
        if char in "\r\n" or char == ESC or "\x80" <= char <= "\x9f":
            return start
        position += 1
    return start


def strip_terminal_sequences(text):
    """Remove ESC/C1 sequences in linear time with no pending-payload buffer.

    Ordinary text, including line breaks, tabs and backspaces, is left for the
    caller's existing whitespace, overstrike and control-character policy.
    Output storage is proportional to input; complete control payloads are not
    copied. Unterminated strings lose only their introducer, preserving prose.
    """
    if text.isprintable():
        return text
    output = []
    position = 0
    while position < len(text):
        char = text[position]
        if char == ESC:
            position += 1
            if position == len(text):
                break
            following = text[position]
            if following == "[":
                position = _csi_end(text, position + 1)
            elif following in ESC_STRINGS:
                position = _string_end(text, position + 1, following == "]")
            else:
                # ESC intermediates followed by a final include character-set
                # designators such as ESC ( B and single controls such as ESC 7.
                while position < len(text) and " " <= text[position] <= "/":
                    position += 1
                if position < len(text) and "0" <= text[position] <= "~":
                    position += 1
        elif char == CSI:
            position = _csi_end(text, position + 1)
        elif char in C1_STRINGS:
            position = _string_end(text, position + 1, char == "\x9d")
        elif "\x80" <= char <= "\x9f":
            position += 1
        else:
            output.append(char)
            position += 1
    return "".join(output)
