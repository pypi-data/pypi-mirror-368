from wexample_app.const.types import ResponsePrintable
from wexample_app.response.abstract_response import AbstractResponse


class BooleanResponse(AbstractResponse):
    content: bool

    def get_printable(self) -> ResponsePrintable:
        from wexample_helpers.helpers.string import string_render_boolean

        return string_render_boolean(self.content)
