from typing import TYPE_CHECKING

from wexample_filestate.item.file.yaml_file import YamlFile

if TYPE_CHECKING:
    from wexample_wex_core.registry.kernel_registry import KernelRegistry
    from wexample_wex_core.common.kernel import Kernel


class KernelRegistryFile(YamlFile):
    def create_registry(self, kernel: "Kernel") -> "KernelRegistry":
        from wexample_wex_core.registry.kernel_registry import KernelRegistry

        return KernelRegistry(kernel=kernel)

    def create_registry_and_save(self, kernel: "Kernel") -> "KernelRegistry":
        registry = self.create_registry(kernel=kernel)

        self.write(registry.serialize())

        return registry

    def create_registry_from_content(self, kernel: "Kernel") -> "KernelRegistry":
        registry = self.create_registry(kernel=kernel)
        registry.hydrate(data=self.read())

        return registry
