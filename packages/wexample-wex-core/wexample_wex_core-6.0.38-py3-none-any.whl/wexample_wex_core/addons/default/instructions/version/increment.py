from wexample_helpers.const.types import UPGRADE_TYPE_MINOR
from wexample_helpers.helpers.version import version_increment
from wexample_wex_core.common.kernel import Kernel


def default__version__increment(
        kernel: "Kernel",
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
