from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandFunctionNameMissingData(ExceptionData):
    """Data model for CommandFunctionNameMissing exception."""
    command_name: str


class CommandFunctionNameMissingException(UndefinedException):
    """Exception raised when a command function name cannot be determined."""
    error_code: str = "COMMAND_FUNCTION_NAME_MISSING"

    def __init__(
            self,
            command_name: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandFunctionNameMissingData(command_name=command_name)

        # Store command_name as instance attribute for backward compatibility
        self.command_name = command_name

        super().__init__(
            message=f"Command function name could not be determined for: {command_name}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
