from typing import Any, TYPE_CHECKING

from wexample_app.const.types import ResponsePrintable
from wexample_app.exception.response_invalid_content_type_exception import ResponseInvalidContentTypeException
from wexample_app.response.abstract_response import AbstractResponse
from wexample_helpers.helpers.args import args_is_basic_value

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel


class DefaultResponse(AbstractResponse):
    content: Any

    def __init__(self, kernel: "AbstractKernel", **kwargs) -> None:
        super().__init__(kernel, **kwargs)

        if not args_is_basic_value(self.content):
            from wexample_helpers.const.types import Scalar

            raise ResponseInvalidContentTypeException(
                content=self.content,
                allowed_content_types=Scalar
            )

    def get_printable(self) -> ResponsePrintable:
        # For now consider every output as a string
        return str(self.content)
