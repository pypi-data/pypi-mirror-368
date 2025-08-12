from typing import TYPE_CHECKING, List, cast, Type

from pydantic import BaseModel

from wexample_helpers.service.mixins.registry_container_mixin import RegistryContainerMixin

if TYPE_CHECKING:
    from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class MiddlewaresRegistry(RegistryContainerMixin, BaseModel):
    """Middleware configuration for command execution.
    
    Middlewares can modify the behavior of commands, such as by iterating over
    multiple values for a single option, running in parallel, etc.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._init_middlewares()

    def _init_middlewares(self):
        self.register_items(
            'middlewares',
            self._get_middlewares_classes()
        )

    def _get_middlewares_classes(self) -> List[Type["AbstractMiddleware"]]:
        from wexample_wex_core.middleware.each_directory_middleware import EachDirectoryMiddleware
        from wexample_wex_core.middleware.each_file_middleware import EachFileMiddleware
        from wexample_wex_core.middleware.each_path_middleware import EachPathMiddleware

        return [
            EachDirectoryMiddleware,
            EachFileMiddleware,
            EachPathMiddleware,
        ]

    def create_middleware_instance(self, name: str):
        from wexample_app.service.service_registry import ServiceRegistry
        cast(ServiceRegistry, self.get_registry('middlewares').get(name))
