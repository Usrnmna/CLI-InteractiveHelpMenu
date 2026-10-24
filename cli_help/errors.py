"""Safe application errors shared by parsing, discovery, and diagnostics."""


class HelpError(ValueError):
    """Describe a rejected operation without retaining pending argument values.

    Codes are stable diagnostic identifiers. Messages remain actionable display
    text; callers must not interpolate unreviewed input or subprocess output.
    """

    def __init__(self, message, code="invalid_configuration"):
        super().__init__(message)
        self.code = code
