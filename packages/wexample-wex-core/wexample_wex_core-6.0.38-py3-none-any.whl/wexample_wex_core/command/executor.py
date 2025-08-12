from typing import TYPE_CHECKING, Dict, Any, List

from wexample_helpers.const.types import Kwargs
from wexample_app.common.command import Command
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
from wexample_wex_core.exception.command_argument_conversion_exception import CommandArgumentConversionException
from wexample_wex_core.exception.command_option_missing_exception import CommandOptionMissingException
from wexample_wex_core.exception.command_unexpected_argument_exception import CommandUnexpectedArgumentException

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class Executor(Command):
    command_wrapper: CommandMethodWrapper

    def __init__(self, command_wrapper: CommandMethodWrapper, *args: Any, **kwargs: Kwargs):
        kwargs['command_wrapper'] = command_wrapper

        super().__init__(
            function=command_wrapper.function,
            *args,
            **kwargs
        )

    def execute_request(self, request: "CommandRequest") -> Any:
        middlewares_attributes = self.command_wrapper.middlewares_attributes
        middlewares_registry = self.kernel.get_registry('middlewares')

        for name in middlewares_attributes:
            middleware_class = middlewares_registry.get_class(name)
            middleware = middleware_class(name=name, **middlewares_attributes[name])
            self.command_wrapper.set_middleware(middleware)

        function_kwargs = self._build_function_kwargs(
            request=request
        )

        if len(self.command_wrapper.middlewares) > 0:
            output = []

            for middleware in self.command_wrapper.middlewares:
                passes = middleware.build_execution_passes(
                    command_wrapper=self.command_wrapper,
                    request=request,
                    function_kwargs=function_kwargs
                )

                for execution_pass_kwargs in passes:
                    output.append(
                        self.function(
                            **execution_pass_kwargs
                        )
                    )

            return output

        # Execute the function with the processed arguments
        return self.function(
            **function_kwargs
        )

    def _parse_arguments(self, arguments: List[str]) -> Dict[str, Any]:
        from wexample_helpers.helpers.cli import cli_argument_convert_value

        """Parse raw command line arguments into a dictionary of option name to value."""
        result: Dict[str, Any] = {}
        skip_next = False

        for i, arg in enumerate(arguments):
            # Skip this iteration if we've already processed this argument as a value
            if skip_next:
                skip_next = False
                continue

            # Check if the argument is an option (starts with - or --)
            if arg.startswith('--'):
                # Long option name (e.g., --version)
                option_name = arg[2:]
                option = self.command_wrapper.find_option_by_name(option_name)

                if not option:
                    # Raise exception for unexpected argument
                    raise CommandUnexpectedArgumentException(
                        argument=arg,
                        allowed_arguments=self.command_wrapper.get_options_names()
                    )

                # Process the option
                if option.is_flag:
                    result[option.name] = True
                elif i + 1 < len(arguments) and not arguments[i + 1].startswith('-'):
                    try:
                        result[option.name] = cli_argument_convert_value(arguments[i + 1], option.type)
                        skip_next = True
                    except Exception as e:
                        raise CommandArgumentConversionException(
                            argument_name=option.name,
                            value=arguments[i + 1],
                            target_type=option.type,
                            cause=e
                        )
                else:
                    result[option.name] = option.default if option.default is not None else None

            elif arg.startswith('-') and len(arg) > 1:
                # Short option name (e.g., -v)
                short_name = arg[1:]
                option = self.command_wrapper.find_option_by_short_name(short_name)

                if not option:
                    # Raise exception for unexpected argument
                    raise CommandUnexpectedArgumentException(
                        argument=arg,
                        allowed_arguments=self.command_wrapper.get_options_names()
                    )

                # Process the option
                if option.is_flag:
                    result[option.name] = True
                elif i + 1 < len(arguments) and not arguments[i + 1].startswith('-'):
                    try:
                        result[option.name] = cli_argument_convert_value(arguments[i + 1], option.type)
                        skip_next = True
                    except Exception as e:
                        raise CommandArgumentConversionException(
                            argument_name=option.name,
                            value=arguments[i + 1],
                            target_type=option.type,
                            cause=e
                        )
                else:
                    result[option.name] = option.default if option.default is not None else None

        return result

    def _build_function_kwargs(self, request: "CommandRequest") -> Dict[str, Any]:
        """Execute the command with the given request arguments."""
        # Parse and convert arguments to appropriate types
        parsed_args = self._parse_arguments(request.arguments)

        """Build the final kwargs dictionary for the function call."""
        function_kwargs = {}

        # Process all declared options
        for option in self.command_wrapper.options:
            # If the option is in parsed args, use that value
            if option.name in parsed_args:
                function_kwargs[option.name] = parsed_args[option.name]
            # Otherwise, use the default value if available
            elif option.default is not None:
                function_kwargs[option.name] = option.default
            # If the option is required but not provided, raise an error
            elif option.required:
                raise CommandOptionMissingException(option_name=option.name)

        # Add kernel to the kwargs
        function_kwargs["kernel"] = self.kernel

        return function_kwargs
