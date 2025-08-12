from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException


class CommandRunnerNotFoundException(UndefinedException):
    """Exception raised when no suitable runner is found for a command.
    
    This exception is thrown when the system cannot find an appropriate runner
    to execute a command, which means the command cannot be executed.
    """
    error_code: str = "COMMAND_RUNNER_NOT_FOUND"

    def __init__(
            self,
            command_name: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Store command_name as instance attribute
        self.command_name = command_name

        # Call parent constructor with appropriate parameters
        super().__init__(
            message=f"Not runner found supporting execution of command \"{command_name}\"",
            cause=cause,
            previous=previous
        )
