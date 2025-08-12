from typing import Any, Optional

from wexample_app.exception.abstract_exception import AbstractException, ExceptionData


class ResponseInvalidContentData(ExceptionData):
    """Data model for ResponseInvalidContent exception."""
    content_type: str
    content_value: str


class ResponseInvalidContentException(AbstractException):
    """Exception raised when a response contains invalid content that cannot be properly processed."""
    error_code: str = "RESPONSE_INVALID_CONTENT"

    def __init__(
            self,
            content: Any,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        # Create structured data using Pydantic model
        content_type = type(content).__name__
        # Convert to string but limit length to avoid huge error messages
        content_str = str(content)
        if len(content_str) > 100:
            content_str = content_str[:97] + "..."
            
        data_model = ResponseInvalidContentData(
            content_type=content_type,
            content_value=content_str
        )

        # Store content info as instance attributes
        self.content_type = content_type
        self.content_value = content_str

        super().__init__(
            message=f"Response contains invalid content of type '{content_type}'. Expected a basic value (str, int, float, bool, None).",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
