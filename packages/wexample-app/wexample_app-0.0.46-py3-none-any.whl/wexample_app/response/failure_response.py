from typing import TYPE_CHECKING, Optional, Any

from wexample_app.const.types import ResponsePrintable
from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    pass


class FailureResponse(AbstractResponse):
    exception: Optional[Any] = None
    message: Optional[str] = None

    def get_printable(self) -> ResponsePrintable:
        # Build a string representation from exception and/or message
        if self.exception and self.message:
            return f"{self.message}: {str(self.exception)}"
        elif self.exception:
            return str(self.exception)
        elif self.message:
            return self.message
        else:
            return "Unknown failure"
