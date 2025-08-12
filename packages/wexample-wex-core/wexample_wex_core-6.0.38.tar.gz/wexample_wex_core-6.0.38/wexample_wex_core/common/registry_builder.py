from typing import TYPE_CHECKING

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_config.config_value.config_value import ConfigValue

if TYPE_CHECKING:
    from wexample_wex_core.registry.kernel_registry import KernelRegistry


class RegistryBuilder(AbstractKernelChild, ConfigValue):
    def __init__(self, kernel: "AbstractKernel", **kwargs) -> None:
        ConfigValue.__init__(self, raw={}, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def create_registry(self) -> "KernelRegistry":
        from wexample_wex_core.registry.kernel_registry import KernelRegistry

        return KernelRegistry(kernel=self.kernel)

    def get_str(self, type_check: bool = True) -> str:
        import yaml
        return yaml.dump(self.create_registry().to_dict())
