from typing import TYPE_CHECKING

from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.common.execution_context import ExecutionContext


@command()
def default__info__show(
        context: "ExecutionContext"
) -> None:
    registry = context.kernel.get_configuration_registry()
    
    context.io.properties(
        title="General",
        properties={
            "Location": context.kernel.workdir.get_resolved(),
            "Environment": registry.env,
            "Arguments": context.kernel._sys_argv,
        }
    )

    context.kernel.io.properties(
        title="Resolvers",
        properties=context.kernel.get_resolvers()
    )

    context.kernel.io.properties(
        title="Runners",
        properties=context.kernel.get_runners()
    )
