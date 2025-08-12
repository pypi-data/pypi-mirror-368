from typing import Any, Optional, List, Type

from wexample_helpers.exception.not_allowed_item_exception import NotAllowedItemException


class ResponseInvalidContentTypeException(NotAllowedItemException):
    """Exception raised when a response contains invalid content that cannot be properly processed."""
    error_code: str = "RESPONSE_INVALID_CONTENT"

    def __init__(
            self,
            content: Any,
            allowed_content_types: List[Type],
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None,
    ):
        from wexample_helpers.helpers.string import string_truncate

        # Get the content type name
        content_type = type(content).__name__
        
        # Convert to string but limit length to avoid huge error messages
        content_str = string_truncate(str(content), 100)

        # Convert type objects to strings for the allowed values
        allowed_values = [t.__name__ for t in allowed_content_types]
        
        # Use the parent class (NotAllowedItemException) initialization
        super().__init__(
            item_type="content type",
            item_value=content_type,
            allowed_values=allowed_values,
            cause=cause,
            previous=previous
        )
        
        # Store additional content info as instance attributes
        self.content_value = content_str
