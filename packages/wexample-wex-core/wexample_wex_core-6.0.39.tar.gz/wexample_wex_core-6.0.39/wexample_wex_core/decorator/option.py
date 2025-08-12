from typing import TYPE_CHECKING, Type, Optional, Any

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def option(
        name: str,
        type: Type,
        short_name: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = False,
        default: Any = None,
        is_flag: bool = False
) -> "AnyCallable":
    def decorator(command_wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        from wexample_wex_core.command.option import Option

        command_wrapper.set_option(Option(
            name=name,
            short_name=short_name,
            type=type,
            description=description,
            required=required,
            default=default,
            is_flag=is_flag,
        ))

        return command_wrapper

    return decorator
