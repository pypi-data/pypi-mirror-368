from typing import Optional, Dict, Any

from wexample_helpers.exception.undefined_exception import UndefinedException


class AbstractCommandOptionException(UndefinedException):
    """Base exception class for command option related errors."""
    error_code: str = "COMMAND_OPTION_ERROR"

    def __init__(
            self,
            option_name: str,
            message: str,
            data: Optional[Dict[str, Any]] = None,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Merge provided data with base data
        merged_data = {
            option_name: option_name
        }
        if data:
            merged_data.update(data)

        # Store option_name as instance attribute
        self.option_name = option_name

        super().__init__(
            message=message,
            data=merged_data,
            cause=cause,
            previous=previous
        )
