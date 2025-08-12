from typing import Optional, TYPE_CHECKING, List, Dict, Any, Union

from pydantic import BaseModel, Field

from wexample_helpers.classes.mixin.has_class_dependencies import HasClassDependencies
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit
from wexample_helpers.const.types import Kwargs
from wexample_wex_core.command.option import Option

if TYPE_CHECKING:
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.common.execution_context import ExecutionContext


class AbstractMiddleware(
    HasSnakeShortClassNameClassMixin,
    HasTwoStepInit,
    HasClassDependencies,
    BaseModel
):
    options: List[Union[Dict[str, Any], Option]] = Field(default_factory=list)
    normalized_options: List[Option] = Field(default_factory=list)
    stop_on_failure: Union[None, bool, str] = False
    max_iterations: Optional[int] = None
    parallel: Union[None, bool, str] = False
    show_progress: Union[None, bool, str] = False

    def __init__(self, **kwargs: Kwargs) -> None:
        super().__init__(**kwargs)

        self.normalized_options = self.build_options()

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'

    def get_first_option(self) -> Optional["Option"]:
        """Get the path option from the normalized options."""
        if self.normalized_options:
            return self.normalized_options[0]
        return None

    def build_options(self) -> List["Option"]:
        from wexample_wex_core.command.option import Option

        """Convert options from various formats to Option objects."""
        normalized = []

        for option in self.options:
            if isinstance(option, dict):
                normalized.append(Option(**option))
            elif isinstance(option, Option):
                normalized.append(option)
            else:
                raise TypeError(f"Unsupported option type: {type(option)}")

        return normalized

    def append_options(
            self,
            request: "CommandRequest",
            command_wrapper: "CommandMethodWrapper"
    ) -> None:
        from wexample_wex_core.const.middleware import MIDDLEWARE_OPTION_VALUE_OPTIONAL
        from wexample_wex_core.command.option import Option

        if self.parallel:
            self.stop_on_failure = False
            request.kernel.io.log("Option \"stop_on_failure\" will be ignored due to parallelization")

        if self.parallel == MIDDLEWARE_OPTION_VALUE_OPTIONAL:
            command_wrapper.set_option(Option(
                name="parallel",
                short_name="pll",
                type=bool,
                description="Execute async when possible",
                default=False,
                is_flag=True,
            ))

        if self.show_progress == MIDDLEWARE_OPTION_VALUE_OPTIONAL:
            command_wrapper.set_option(Option(
                name="progress",
                short_name="prgs",
                type=bool,
                description="Display progress bar",
                default=False,
                is_flag=True,
            ))

        if self.stop_on_failure == MIDDLEWARE_OPTION_VALUE_OPTIONAL:
            command_wrapper.set_option(Option(
                name="stop-on-failure",
                short_name="sof",
                type=bool,
                description="Stop at first failure response if not async",
                default=False,
                is_flag=True,
            ))

    def validate_options(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> bool:
        return True

    def build_execution_contexts(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> List["ExecutionContext"]:
        from wexample_wex_core.common.execution_context import ExecutionContext

        self.validate_options(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )

        return [
            ExecutionContext(
                middleware=self,
                command_wrapper=command_wrapper,
                request=request,
                function_kwargs=function_kwargs
            )
        ]
