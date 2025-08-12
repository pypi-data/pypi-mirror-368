from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.const.types import ResponsePrintable

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel


class AbstractResponse(AbstractKernelChild, BaseModel):
    def __init__(self, /, kernel: "AbstractKernel", **kwargs: Any) -> None:
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    @abstractmethod
    def get_printable(self) -> ResponsePrintable:
        pass

    def get_wrapped_printable(self) -> str:
        printable = self.get_printable()

        if printable is None:
            return ''

        return printable
