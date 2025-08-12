from typing import TYPE_CHECKING

from wexample_app.common.command_request import CommandRequest as BaseCommandRequest

if TYPE_CHECKING:
    pass


class CommandRequest(BaseCommandRequest):
    request_id: str
