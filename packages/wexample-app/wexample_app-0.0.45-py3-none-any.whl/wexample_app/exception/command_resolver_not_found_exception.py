from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandResolverNotFoundData(ExceptionData):
    """Data model for CommandResolverNotFound exception."""
    command_type: str


class CommandResolverNotFoundException(UndefinedException):
    """Exception raised when no resolver is found for a specific command type."""
    error_code: str = "COMMAND_RESOLVER_NOT_FOUND"

    def __init__(
            self,
            command_type: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandResolverNotFoundData(command_type=command_type)

        # Store command_type as instance attribute for backward compatibility
        self.command_type = command_type

        super().__init__(
            message=f"No resolver found for command type: {command_type}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
