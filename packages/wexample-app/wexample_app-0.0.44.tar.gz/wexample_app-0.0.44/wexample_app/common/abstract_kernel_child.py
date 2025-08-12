from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel


class AbstractKernelChild:
    _kernel: Optional["AbstractKernel"]

    def __init__(self, kernel: "AbstractKernel"):
        from wexample_app.common.abstract_kernel import AbstractKernel
        assert isinstance(kernel, AbstractKernel)

        self._kernel = kernel

    @property
    def kernel(self) -> "AbstractKernel":
        return self._kernel

    @kernel.setter
    def kernel(self, value: "AbstractKernel"):
        self._kernel = value
