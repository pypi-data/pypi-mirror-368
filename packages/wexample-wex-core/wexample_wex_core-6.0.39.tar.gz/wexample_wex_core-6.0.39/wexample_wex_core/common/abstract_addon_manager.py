from typing import Optional, List, Type

from pydantic import BaseModel

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_filestate.mixins.with_workdir_mixin import WithWorkdirMixin
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class AbstractAddonManager(
    AbstractKernelChild,
    HasTwoStepInit,
    HasSnakeShortClassNameClassMixin,
    BaseModel,
    WithWorkdirMixin,
):
    def __init__(self, kernel: "AbstractKernel", **kwargs):
        import inspect
        import os.path

        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

        # Get the path of the actual addon manager class file
        manager_file = inspect.getfile(self.__class__)

        WithWorkdirMixin._init_workdir(
            self,
            entrypoint_path=os.path.dirname(manager_file),
            io_manager=self.kernel.io
        )

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return "AddonManager"

    def get_middlewares_classes(self) -> List[Type["AbstractMiddleware"]]:
        return []
