from typing import Optional, ClassVar, TYPE_CHECKING

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel
    from wexample_filestate.item.item_target_directory import ItemTargetDirectory
    from wexample_app.common.abstract_kernel import AbstractKernel


class KernelWorkdir(AbstractKernelChild, ProjectWorkdir):
    # Class-scoped constant for the tmp shortcut
    SHORTCUT_REGISTRY: ClassVar[str] = "registry"
    SHORTCUT_TMP: ClassVar[str] = "tmp"
    FILE_REGISTRY: ClassVar[str] = "registry.yml"

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        ProjectWorkdir.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        from wexample_wex_core.path.kernel_registry_file import KernelRegistryFile

        config = super().prepare_value(
            raw_value=raw_value
        )

        children = raw_value["children"]

        children.append({
            "shortcut": self.SHORTCUT_TMP,
            "name": self.SHORTCUT_TMP,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True,
            "children": [
                {
                    "class": KernelRegistryFile,
                    "name": KernelWorkdir.FILE_REGISTRY,
                    "shortcut": KernelWorkdir.SHORTCUT_REGISTRY,
                    "type": DiskItemType.FILE,
                }
            ]
        })

        return config

    @classmethod
    def create_from_kernel(
            cls,
            kernel: "Kernel",
            **kwargs
    ) -> "ItemTargetDirectory":
        return super().create_from_path(
            path=kernel.entrypoint_path,
            kernel=kernel,
            io=kernel.io,
            **kwargs
        )
