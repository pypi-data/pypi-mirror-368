import traceback
import uuid
from typing import Dict, Any, Optional

from pydantic import BaseModel


class ExceptionData(BaseModel):
    """Base model for exception data using Pydantic."""
    pass


class AbstractException(Exception):
    """Base exception class for all application exceptions.
    
    Provides enhanced functionality including:
    - Unique error codes
    - Structured error data using Pydantic
    - Error tracing
    - Serialization support
    """
    # Class-level error code, should be overridden by subclasses
    error_code: str = "GENERAL_ERROR"

    def __init__(self,
                 message: str,
                 data: Optional[Dict[str, Any]] = None,
                 cause: Optional[Exception] = None,
                 previous: Optional[Exception] = None):
        self.message = message
        self.data = data or {}
        self.cause = cause
        self.previous = previous
        self.exception_id = str(uuid.uuid4())
        self.traceback = traceback.format_exc() if traceback.format_exc() != 'NoneType: None\n' else None
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "exception_id": self.exception_id
        }

        if self.data:
            result["data"] = self.data

        if self.cause:
            result["cause"] = str(self.cause)

        return result

    def with_data(self, **kwargs) -> 'AbstractException':
        """Add additional data to the exception."""
        self.data.update(kwargs)
        return self
