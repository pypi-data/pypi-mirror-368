from wexample_wex_core.common.kernel import Kernel


def default__info__show(
        kernel: "Kernel",
        arguments # TODO TMP
) -> None:
    from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV

    kernel.io.properties(
        title="General",
        properties={
            "Location": kernel.workdir.get_resolved(),
            "Environment": kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV),
            "Arguments": kernel._sys_argv,
        }
    )

    kernel.io.properties(
        title="Resolvers",
        properties=kernel.get_resolvers()
    )

    kernel.io.properties(
        title="Runners",
        properties=kernel.get_runners()
    )
