from typing import TYPE_CHECKING

from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable


def command():
    def decorator(function: "AnyCallable"):
        return CommandMethodWrapper(function=function)

    return decorator
