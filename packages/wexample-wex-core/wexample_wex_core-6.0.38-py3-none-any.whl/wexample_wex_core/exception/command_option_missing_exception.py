from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData
from wexample_wex_core.exception.abstract_command_option_exception import AbstractCommandOptionException


class CommandOptionMissingData(ExceptionData):
    """Data model for CommandOptionMissing exception."""
    option_name: str


class CommandOptionMissingException(AbstractCommandOptionException):
    """Exception raised when a required command option is missing."""
    error_code: str = "COMMAND_OPTION_MISSING"

    def __init__(
            self,
            option_name: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandOptionMissingData(option_name=option_name)

        # Store option_name as instance attribute
        self.option_name = option_name

        super().__init__(
            option_name=option_name,
            message=f"Required option '{option_name}' is missing",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
