from typing import Callable, Any, TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.helpers.response import response_normalize

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_app.common.command_request import CommandRequest
    from wexample_app.common.abstract_kernel import AbstractKernel


class Command(AbstractKernelChild, BaseModel):
    function: Callable[..., Any] = None

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def execute_request(self, request: "CommandRequest") -> Any:
        # Basic way to execute command.
        return self.function(
            kernel=self.kernel,
            arguments=request.arguments
        )

    def execute_request_and_normalize(self, request: "CommandRequest") -> "AbstractResponse":
        return response_normalize(
            kernel=self.kernel,
            response=self.execute_request(
                request=request
            )
        )
