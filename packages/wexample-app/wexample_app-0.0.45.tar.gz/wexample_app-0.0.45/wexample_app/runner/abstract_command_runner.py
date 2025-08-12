from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.common.service.service_mixin import ServiceMixin
from wexample_helpers.const.types import AnyCallable

if TYPE_CHECKING:
    from wexample_app.common.command import Command
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.common.command_request import CommandRequest


class AbstractCommandRunner(AbstractKernelChild, ServiceMixin, BaseModel):
    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return "CommandRunner"

    @abstractmethod
    def _build_command_function(self, request: "CommandRequest") -> AnyCallable:
        pass

    def _build_command_function_or_fail(self, request: "CommandRequest") -> AnyCallable:
        function = self._build_command_function(request=request)

        if not function:
            from wexample_app.exception.command_function_not_found_exception import CommandFunctionNotFoundException

            path = self.build_command_path(request)
            function_name = request.resolver.build_command_function_name(request)
            raise CommandFunctionNotFoundException(function_name=function_name, module_path=path)

        return function

    def will_run(self, request: "CommandRequest") -> bool:
        return False

    def build_runnable_command(self, request: "CommandRequest") -> Optional["Command"]:
        from wexample_app.common.command import Command
        function = self._build_command_function_or_fail(request=request)

        return Command(
            kernel=self.kernel,
            function=function
        )
