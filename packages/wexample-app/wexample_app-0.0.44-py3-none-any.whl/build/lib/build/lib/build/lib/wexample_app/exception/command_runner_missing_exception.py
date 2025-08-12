from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandRunnerMissingData(ExceptionData):
    """Data model for CommandRunnerMissing exception."""
    command_name: str


class CommandRunnerMissingException(UndefinedException):
    """Exception raised when no runner is available for a command."""
    error_code: str = "COMMAND_RUNNER_MISSING"

    def __init__(
            self,
            command_name: str, cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandRunnerMissingData(command_name=command_name)

        # Store command_name as instance attribute for backward compatibility
        self.command_name = command_name

        super().__init__(
            message=f"No runner available for command: {command_name}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
