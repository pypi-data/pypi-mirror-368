from typing import Optional

from wexample_helpers.exception.undefined_exception import UndefinedException, ExceptionData


class CommandModuleLoadErrorData(ExceptionData):
    """Data model for CommandModuleLoadError exception."""
    file_path: str


class CommandModuleLoadErrorException(UndefinedException):
    """Exception raised when a Python module cannot be loaded from a command file."""
    error_code: str = "COMMAND_MODULE_LOAD_ERROR"

    def __init__(
            self,
            file_path: str,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        data_model = CommandModuleLoadErrorData(file_path=file_path)

        # Store file_path as instance attribute for backward compatibility
        self.file_path = file_path

        super().__init__(
            message=f"Failed to load Python module from file: {file_path}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
