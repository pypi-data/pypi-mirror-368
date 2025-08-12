from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_wex_core.common.kernel import Kernel


def response_normalize(kernel: "Kernel", response: Any) -> "AbstractResponse":
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_app.response.null_response import NullResponse

    if isinstance(response, AbstractResponse):
        return response
    if isinstance(response, bool):
        from wexample_app.response.boolean_response import BooleanResponse
        return BooleanResponse(kernel=kernel, content=response)
    if response is None:
        return NullResponse(kernel=kernel)

    from wexample_app.response.default_response import DefaultResponse
    return DefaultResponse(kernel=kernel, content=response)
