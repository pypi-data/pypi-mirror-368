from typing import Optional, List

from wexample_helpers.exception.undefined_exception import ExceptionData
from wexample_helpers.exception.not_allowed_item_exception import NotAllowedItemException


class CommandUnexpectedArgumentData(ExceptionData):
    """Data model for CommandUnexpectedArgument exception."""
    argument: str


class CommandUnexpectedArgumentException(NotAllowedItemException):
    """Exception raised when an unexpected argument is provided to a command."""
    error_code: str = "COMMAND_UNEXPECTED_ARGUMENT"

    def __init__(
            self,
            argument: str,
            allowed_arguments: List[str],
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Call parent constructor with appropriate parameters
        super().__init__(
            item_type="argument",
            item_value=argument,
            allowed_values=allowed_arguments,
            cause=cause,
            previous=previous
        )
