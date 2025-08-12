from typing import TYPE_CHECKING

from wexample_helpers.const.types import UPGRADE_TYPE_MINOR
from wexample_helpers.helpers.version import version_increment
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.common.execution_context import ExecutionContext


@option(name="version", type=str, required=True)
@option(name="type", type=str)
@option(name="increment", type=int)
@option(name="build", type=bool)
@command()
def default__version__increment(
        context: "ExecutionContext",
        version: str,
        type: str = UPGRADE_TYPE_MINOR,
        increment: int = 1,
        build: bool = False,
) -> str:
    return version_increment(
        version=version,
        type=type,
        increment=increment,
        build=build,
    )
