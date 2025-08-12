from typing import TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
from wexample_helpers.classes.mixin.serializable_mixin import SerializableMixin
from wexample_helpers.const.types import StructuredData

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class KernelRegistry(AbstractKernelChild, SerializableMixin, BaseModel):
    env: str

    def __init__(
            self,
            kernel: "Kernel",
            **kwargs
    ) -> None:
        from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV
        kwargs["env"] = kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV)

        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)
        SerializableMixin.__init__(self)

    def serialize(self) -> StructuredData:
        resolvers = {}

        for command_resolver in self.kernel.get_resolvers().values():
            assert isinstance(command_resolver, AbstractCommandResolver)
            resolvers[command_resolver.get_snake_short_class_name()] = command_resolver.build_registry_data()

        return {
            "env": self.env,
            "resolvers": resolvers
        }

    def hydrate(self, data: StructuredData) -> None:
        self.env = data["env"]
        self.resolvers = data["resolvers"]
