from typing import List, Optional, Union, TYPE_CHECKING
from typing import cast

from pydantic import BaseModel, Field, PrivateAttr
from wexample_app.exception.command_runner_not_found_exception import CommandRunnerNotFoundException

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.exception.command_build_failed_exception import CommandBuildFailedException
from wexample_app.exception.command_resolver_not_found_exception import CommandResolverNotFoundException
from wexample_app.exception.command_runner_missing_exception import CommandRunnerMissingException
from wexample_app.exception.command_type_not_found_exception import CommandTypeNotFoundException
from wexample_app.runner.abstract_command_runner import AbstractCommandRunner
from wexample_helpers.const.types import StringsMatch

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_app.response.abstract_response import AbstractResponse


class CommandRequest(
    AbstractKernelChild,
    BaseModel
):
    name: str
    arguments: List[Union[str, int]] = Field(default_factory=list)
    path: Optional[str] = None
    type: Optional[str] = None
    _match: Optional[StringsMatch] = None
    _resolver: Optional["AbstractCommandResolver"] = PrivateAttr(default=None)
    _runner: Optional["AbstractCommandRunner"] = PrivateAttr(default=None)

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

        self.type = self._guess_type()
        if self.type is None:
            raise CommandTypeNotFoundException(self.name)

        self.resolver = self._get_resolver()
        self.runner = self._guess_runner()
        if not self.runner:
            raise CommandRunnerNotFoundException(
                command_name=self.name
            )

        self.path = self.runner.build_command_path(request=self)

    @property
    def match(self) -> "StringsMatch":
        return self._match

    @match.setter
    def match(self, value: "StringsMatch") -> None:
        self._match = value

    @property
    def resolver(self) -> "AbstractCommandResolver":
        return self._resolver

    @resolver.setter
    def resolver(self, value: "AbstractCommandResolver") -> None:
        self._resolver = value

    @property
    def runner(self) -> "AbstractCommandRunner":
        return self._runner

    @runner.setter
    def runner(self, value: "AbstractCommandRunner") -> None:
        self._runner = value

    @property
    def kernel(self) -> Union["AbstractKernel", "CommandRunnerKernel"]:
        # Enforce typing
        return cast("CommandRunnerKernel", super().kernel)

    def execute(self) -> "AbstractResponse":
        if self.runner is None:
            raise CommandRunnerMissingException(
                command_name=self.name
            )

        try:
            command = self.resolver.build_command(request=self)
            if command is None:
                raise CommandBuildFailedException(
                    command_name=self.name,
                    resolver_name=self.resolver.__class__.__name__
                )

            return command.execute_request_and_normalize(self)
        except Exception as e:
            self.kernel.io.error(
                exception=e,
                fatal=True
            )

    def _get_resolver(self) -> "AbstractCommandResolver":
        resolver = self.kernel.get_resolver(self.type)
        if resolver is None:
            raise CommandResolverNotFoundException(self.type)
        return resolver

    def _guess_runner(self) -> Optional["AbstractCommandRunner"]:
        for runner in self.kernel.get_runners().values():
            if runner.will_run(self):
                return runner
        return None

    def _guess_type(self) -> Optional[str]:
        for resolver in self.kernel.get_resolvers().values():
            match = resolver.supports(request=self)
            if match is not None:
                self.match = match
                return resolver.get_type()
        return None
