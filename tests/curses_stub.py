"""Minimal curses stand-in for hosts that do not ship the module (for example, Windows).

The stub is installed into ``sys.modules`` only when the real module is absent,
so Linux hosts and CI continue to use the platform implementation. It supplies
the constants and no-op functions referenced by ``cli_help/ui.py``; it provides
no terminal device and must not be used to claim rendered-terminal evidence.
"""


class error(Exception):
    """Mirror ``curses.error`` for exception handling in ``ui.py``."""


# Distinct integer values stand in for the platform constants.
KEY_UP = 412
KEY_DOWN = 413
KEY_LEFT = 414
KEY_RIGHT = 415
KEY_PPAGE = 416
KEY_NPAGE = 417
KEY_HOME = 418
KEY_END = 419
KEY_ENTER = 420
KEY_RESIZE = 421
A_BOLD = 1
A_REVERSE = 2


def curs_set(*_arguments):
    """No-op replacement for ``curses.curs_set``."""


def raw(*_arguments):
    """No-op replacement for ``curses.raw``."""


def set_escdelay(*_arguments):
    """No-op replacement for ``curses.set_escdelay``."""
