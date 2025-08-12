from abc import abstractmethod
from typing import TYPE_CHECKING

from wexample_app.runner.abstract_command_runner import AbstractCommandRunner

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class AbstractFileCommandRunner(AbstractCommandRunner):
    @abstractmethod
    def get_file_extension(self) -> str:
        pass

    def build_command_path(self, request: "CommandRequest") -> str:
        return request.resolver.build_command_path(
            request=request,
            extension=self.get_file_extension()
        )

    def will_run(self, request: "CommandRequest") -> bool:
        import os.path
        path = self.build_command_path(request=request)
        # Will run if file exists.
        return path is not None and os.path.exists(path)
