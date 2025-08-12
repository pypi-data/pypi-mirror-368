from wexample_app.const.types import ResponsePrintable
from wexample_app.response.abstract_response import AbstractResponse


class NullResponse(AbstractResponse):
    def get_printable(self) -> ResponsePrintable:
        return None
