from __future__ import annotations

from typing import List, Dict, Any, TYPE_CHECKING

from pydantic import PrivateAttr


if TYPE_CHECKING:
    from wexample_app.const.types import CommandLineArgumentsList
    from wexample_app.common.command_request import CommandRequest
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.response.abstract_response import AbstractResponse


class CommandLineKernel():
    _sys_argv: list[str] = PrivateAttr(default_factory=list)
    _sys_argv_start_index: int = 1
    _sys_argv_end_index: int | None = None
    _core_argv: list[str] = PrivateAttr(default_factory=list)

    def _init_command_line_kernel(self: "AbstractKernel"):
        import sys

        self._sys_argv = sys.argv.copy()

        self._handle_core_args()

    def _get_core_args(self: "AbstractKernel") -> List[Dict[str, Any]]:
        return []

    def _handle_core_args(self: "AbstractKernel"):
        from wexample_helpers.helpers.args import args_shift_one

        for arg_config in self._get_core_args():
            if args_shift_one(self._sys_argv, arg_config["arg"], True) is not None:
                setattr(self, arg_config["attr"], arg_config["value"])

    def exec_argv(self: "AbstractKernel") -> None:
        """
        Main entrypoint from command line calls.
        May not be called by an internal script.
        """
        try:
            command_requests = self._build_command_requests_from_arguments(
                self._sys_argv[self._sys_argv_start_index:self._sys_argv_end_index]
            )
        except Exception as e:
            self.io.error(
                exception=e,
                fatal=True
            )

            return

        for command_request in command_requests:
            self.execute_kernel_command_and_print(command_request)

    def _build_command_requests_from_arguments(
            self: "AbstractKernel",
            arguments: "CommandLineArgumentsList"
    ) -> list["CommandRequest"]:
        # By default, allow one request per execution call.
        return self._build_single_command_request_from_arguments(arguments)

    def _build_single_command_request_from_arguments(
            self: "AbstractKernel",
            arguments: "CommandLineArgumentsList"
    ):
        return [
            self._get_command_request_class()(
                kernel=self,
                name=arguments[0],
                arguments=arguments[1:])
        ]
