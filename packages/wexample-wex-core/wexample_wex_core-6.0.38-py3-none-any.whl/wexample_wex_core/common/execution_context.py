from typing import Optional

from pydantic import BaseModel, Field

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.const.types import Kwargs
from wexample_prompt.mixins.with_required_io_manager import WithRequiredIoManager
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
from wexample_wex_core.common.command_request import CommandRequest
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class ExecutionContext(
    AbstractKernelChild,
    WithRequiredIoManager,
    BaseModel,
):
    command_wrapper: CommandMethodWrapper
    function_kwargs: Kwargs = Field(default_factory=dict)
    middleware: Optional[AbstractMiddleware]
    request: CommandRequest

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)

        AbstractKernelChild.__init__(
            self,
            kernel=self.request.kernel
        )

        WithRequiredIoManager.__init__(
            self,
            io=self.kernel.io
        )

        self.function_kwargs["context"] = self
