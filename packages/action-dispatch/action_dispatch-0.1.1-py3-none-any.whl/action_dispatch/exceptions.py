"""
Exception classes for the action-dispatch library.
"""


class ActionDispatchError(Exception):
    """Base exception class for all action-dispatch related errors."""

    pass


class InvalidDimensionError(ActionDispatchError):
    """Raised when an invalid dimension parameter is provided."""

    def __init__(self, dimension: str, available_dimensions: list[str]) -> None:
        self.dimension = dimension
        self.available_dimensions = available_dimensions
        super().__init__(
            f"Invalid dimension parameter '{dimension}', "
            f"available dimensions: {available_dimensions}"
        )


class HandlerNotFoundError(ActionDispatchError):
    """Raised when no handler is found for a given action and rules."""

    def __init__(self, action: str, rules: dict[str, str]) -> None:
        self.action = action
        self.rules = rules
        super().__init__(f"No handler found for action '{action}' with rules {rules}")


class InvalidActionError(ActionDispatchError):
    """Raised when an invalid action name is provided."""

    def __init__(
        self, message: str = "Action name must be provided for dispatching."
    ) -> None:
        super().__init__(message)
