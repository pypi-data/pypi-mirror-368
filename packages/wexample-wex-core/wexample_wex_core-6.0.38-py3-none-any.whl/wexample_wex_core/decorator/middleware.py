from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

def middleware(
        name: str,
        **kwargs
) -> "AnyCallable":
    def decorator(command_wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        command_wrapper.register_middleware(name, kwargs)
        return command_wrapper

    return decorator
