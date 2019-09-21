from typing import Tuple

from click import Group

from megalus.ext.virtualenv.main import VirtualMegalus, VirtualenvSettings, build, run, config


async def get_context_object() -> VirtualMegalus:
    virtualenv_settings = VirtualenvSettings()
    obj = VirtualMegalus(settings=virtualenv_settings)
    return obj


def get_commands(cli: Group) -> None:
    cli.add_command(build)
    cli.add_command(run)
    cli.add_command(config)
