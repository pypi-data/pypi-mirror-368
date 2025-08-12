from typing import Optional, TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE, COMMAND_PATTERN_SERVICE
from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class ServiceCommandResolver(AbstractCommandResolver):
    @classmethod
    def get_pattern(cls) -> str:
        return COMMAND_PATTERN_SERVICE

    @classmethod
    def get_type(cls) -> str:
        return COMMAND_TYPE_SERVICE

    def build_command_path(
            self,
            request: "CommandRequest",
            extension: str
    ) -> Optional[str]:
        return f"{self.kernel.workdir.get_resolved()}cli/{request.name}.{extension}"

    def build_command_function_name(self, request: "CommandRequest") -> Optional[str]:
        import re
        return re.sub(r'[^a-zA-Z0-9_]', '', request.name.replace("/", "__"))

    def build_registry_data(self, test: bool = False):
        registry = {}

        return registry