"""ControlPoint error class"""


class ControlPointError(Exception):
    """Represents a ZCC controller error."""


class ControlPointCannotConnectError(ControlPointError):
    """Represents a connect connect error when connecting to zcc."""


class ControlPointInvalidHostError(ControlPointError):
    """Represents an invalid host error when connecting to zcc."""


class ControlPointConnectionRefusedError(ControlPointError):
    """Represents a connection refused when connecting to zcc."""


class ControlPointTimeoutError(ControlPointError):
    """Represents a connection timeout when connecting to zcc."""
