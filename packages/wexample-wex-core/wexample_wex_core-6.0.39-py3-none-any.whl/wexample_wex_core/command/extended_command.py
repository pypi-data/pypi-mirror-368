import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Dict, Any, List

from wexample_app.common.command import Command
from wexample_app.response.failure_response import FailureResponse
from wexample_helpers.const.types import Kwargs
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
from wexample_wex_core.common.execution_context import ExecutionContext
from wexample_wex_core.const.middleware import MIDDLEWARE_OPTION_VALUE_ALLWAYS, MIDDLEWARE_OPTION_VALUE_OPTIONAL
from wexample_wex_core.const.types import ParsedArgs
from wexample_wex_core.exception.command_argument_conversion_exception import CommandArgumentConversionException
from wexample_wex_core.exception.command_option_missing_exception import CommandOptionMissingException
from wexample_wex_core.exception.command_unexpected_argument_exception import CommandUnexpectedArgumentException

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class ExtendedCommand(Command):
    command_wrapper: CommandMethodWrapper

    def __init__(self, command_wrapper: CommandMethodWrapper, *args: Any, **kwargs: Kwargs):
        kwargs['command_wrapper'] = command_wrapper

        super().__init__(
            function=command_wrapper.function,
            *args,
            **kwargs
        )

    def execute_request(self, request: "CommandRequest") -> Any:
        from wexample_app.helpers.response import response_normalize
        from wexample_app.response.multiple_response import MultipleResponse

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
            output = MultipleResponse(kernel=self.kernel)

            for middleware in self.command_wrapper.middlewares:
                show_progress = middleware.show_progress == MIDDLEWARE_OPTION_VALUE_ALLWAYS or (
                        middleware.show_progress == MIDDLEWARE_OPTION_VALUE_OPTIONAL and function_kwargs[
                    "show_progress"])

                # Each middleware can multiply the executions,
                # e.g. executing the command on every file of a list.
                execution_contexts = middleware.build_execution_contexts(
                    command_wrapper=self.command_wrapper,
                    request=request,
                    function_kwargs=function_kwargs
                )

                # Apply limit if specified
                if isinstance(middleware.max_iterations, int) and middleware.max_iterations > 0:
                    execution_contexts = execution_contexts[:middleware.max_iterations]
                    self.kernel.io.info(
                        f'Middleware \"{middleware.get_short_class_name()}\" truncated list to {middleware.max_iterations} items')

                # Check if middleware should run in parallel
                if (middleware.parallel == MIDDLEWARE_OPTION_VALUE_ALLWAYS
                        or (middleware.parallel == MIDDLEWARE_OPTION_VALUE_OPTIONAL
                            and "parallel" in function_kwargs and function_kwargs["parallel"])):
                    # Execute passes in parallel using asyncio
                    responses = asyncio.run(self._execute_passes_parallel(
                        execution_contexts=execution_contexts,
                    ))

                    # Add all responses to output
                    for response in responses:
                        output.append(response)

                        # Check if we should stop on failure
                        if isinstance(response, FailureResponse) and middleware.stop_on_failure:
                            # "Stop" does not mean "fail", so we just stop the process.
                            return output
                else:
                    i = 0
                    length = len(execution_contexts)

                    if show_progress:
                        # First bar.
                        request.kernel.io.progress(length, i)

                    # Execute passes sequentially
                    for context in execution_contexts:

                        response = response_normalize(
                            kernel=self.kernel,
                            response=self.function(
                                **context.function_kwargs
                            )
                        )

                        output.append(response)
                        i += 1

                        if show_progress:
                            request.kernel.io.progress(length, i)

                        if isinstance(response, FailureResponse) and (
                                middleware.stop_on_failure == MIDDLEWARE_OPTION_VALUE_ALLWAYS
                                or (middleware.stop_on_failure == MIDDLEWARE_OPTION_VALUE_OPTIONAL
                                    and "stop_on_failure" in function_kwargs and function_kwargs["stop_on_failure"])
                        ):
                            # "Stop" does not mean "fail", so we just stop the process.
                            return output

            return output

        context = ExecutionContext(
            middleware=None,
            command_wrapper=self.command_wrapper,
            request=request,
            function_kwargs=function_kwargs
        )

        return response_normalize(
            kernel=self.kernel,
            response=self.function(
                **context.function_kwargs
            )
        )

    async def _execute_passes_parallel(self, execution_contexts: List[ExecutionContext]) -> List[Any]:
        """Execute multiple passes in parallel using asyncio.
        
        Args:
            execution_contexts: List of ExecutionPass objects to execute in parallel
            
        Returns:
            List of normalized responses from all executions
        """
        from wexample_app.helpers.response import response_normalize
        from wexample_app.response.abstract_response import AbstractResponse

        # Create a list to store all tasks
        tasks = []

        # Create an executor for running CPU-bound functions in a thread pool
        executor = ThreadPoolExecutor(max_workers=min(32, len(execution_contexts)))

        # Define a coroutine that executes a single pass
        async def execute_single_pass(execution_context: ExecutionContext) -> "AbstractResponse":
            from wexample_prompt.output.buffer_output_handler import BufferOutputHandler

            output = BufferOutputHandler()
            # Detach io manager to print log result at the end.
            execution_context._init_io_manager(
                output=output
            )

            # Run the function in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.function(**execution_context.function_kwargs)
            )

            self.kernel.io.print_responses(
                output.buffer
            )

            # Normalize the response
            return response_normalize(kernel=self.kernel, response=result)

        # Create a task for each pass
        for execution_context in execution_contexts:
            task = asyncio.create_task(execute_single_pass(execution_context))
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)

        # Close the executor
        executor.shutdown(wait=False)

        return responses

    def _parse_arguments(self, arguments: List[str]) -> ParsedArgs:
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
                option = self.command_wrapper.find_option_by_kebab_name(option_name)

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
        # Allow middleware to add extra options.
        for middleware in self.command_wrapper.middlewares:
            middleware.append_options(
                request=request,
                command_wrapper=self.command_wrapper,
            )

        """Execute the command with the given request arguments."""
        # Parse and convert arguments to appropriate types
        parsed_args = self._parse_arguments(request.arguments)

        """Build the final kwargs dictionary for the function call."""
        function_kwargs = {}

        # Process all declared options
        for option in self.command_wrapper.options:
            # If the option is in parsed args, use that value
            if option.name in parsed_args:
                option.value = function_kwargs[option.name] = parsed_args[option.name]
            # Otherwise, use the default value if available
            elif option.default is not None:
                option.value = function_kwargs[option.name] = option.default
            # If the option is required but not provided, raise an error
            elif option.required:
                raise CommandOptionMissingException(option_name=option.name)

        return function_kwargs
