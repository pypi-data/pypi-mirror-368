from pathlib import Path
from typing import Optional, TYPE_CHECKING, cast

from wexample_helpers.helpers.string import string_to_snake_case
from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON, COMMAND_PATTERN_ADDON, COMMAND_SEPARATOR_FUNCTION_PARTS
from wexample_wex_core.const.registries import RegistryResolverData
from wexample_wex_core.exception.addon_not_registered_exception import AddonNotRegisteredException
from wexample_wex_core.resolver.abstract_command_resolver import AbstractCommandResolver

if TYPE_CHECKING:
    from wexample_wex_core.common.command_request import CommandRequest


class AddonCommandResolver(AbstractCommandResolver):
    @classmethod
    def get_pattern(cls) -> str:
        return COMMAND_PATTERN_ADDON

    @classmethod
    def get_type(cls) -> str:
        return COMMAND_TYPE_ADDON

    def build_command_path(
            self,
            request: "CommandRequest",
            extension: str
    ) -> Optional[str]:
        from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

        match = request.match

        # Extract addon, group and command from match
        addon_name = string_to_snake_case(match.group(1))
        group = string_to_snake_case(match.group(2))
        command = string_to_snake_case(match.group(3))

        addon_registry = self.kernel.get_registry('addon')
        if not addon_registry.has(addon_name):
            # Get list of available addons for better error reporting
            available_addons = list(addon_registry.get_all().keys())
            raise AddonNotRegisteredException(
                addon_name=addon_name,
                available_addons=available_addons
            )

        addon_manager = cast(AbstractAddonManager, addon_registry.get(addon_name))

        return str(
            Path(addon_manager.workdir.get_resolved())
            / "commands"
            / group
            / f"{command}.{extension}"
        )

    def build_command_function_name(self, request: "CommandRequest") -> Optional[str]:
        return string_to_snake_case(
            COMMAND_SEPARATOR_FUNCTION_PARTS.join(self.get_function_name_parts(
                request.match.groups()
            ))
        )

    def build_registry_data(self, test: bool = False) -> RegistryResolverData:
        registry: RegistryResolverData = {}

        for addon in self.kernel.get_addons().values():
            assert isinstance(addon, AbstractAddonManager)
            registry[addon.get_snake_short_class_name()] = {}

        return registry
