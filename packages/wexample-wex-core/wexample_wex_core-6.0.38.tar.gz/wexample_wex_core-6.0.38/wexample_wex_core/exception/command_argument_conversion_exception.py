from typing import Optional, Any, Type

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandArgumentConversionData(ExceptionData):
    """Data model for CommandArgumentConversion exception."""
    argument_name: str
    value: str
    target_type: str


class CommandArgumentConversionException(UndefinedException):
    """Exception raised when a command argument cannot be converted to the expected type."""
    error_code: str = "COMMAND_ARGUMENT_CONVERSION_ERROR"

    def __init__(
            self,
            argument_name: str,
            value: str,
            target_type: Type,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandArgumentConversionData(
            argument_name=argument_name,
            value=value,
            target_type=str(target_type)
        )

        # Store attributes as instance attributes
        self.argument_name = argument_name
        self.value = value
        self.target_type = target_type

        super().__init__(
            message=f"Cannot convert value '{value}' for argument '{argument_name}' to type {target_type.__name__}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
