from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandBuildFailedData(ExceptionData):
    """Data model for CommandBuildFailed exception."""
    command_name: str
    resolver_name: str


class CommandBuildFailedException(UndefinedException):
    """Exception raised when a command cannot be built by its resolver."""
    error_code: str = "COMMAND_BUILD_FAILED"

    def __init__(
            self,
            command_name: str,
            resolver_name: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandBuildFailedData(command_name=command_name, resolver_name=resolver_name)

        # Store attributes as instance attributes for backward compatibility
        self.command_name = command_name
        self.resolver_name = resolver_name

        super().__init__(
            message=f"Failed to build command '{command_name}' with resolver: {resolver_name}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous,
        )
