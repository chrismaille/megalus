from click import Group

from megalus.ext.virtualenv.context import VirtualMegalus
from megalus.ext.virtualenv.commands import build, config, run, rm
from megalus.ext.virtualenv.settings import VirtualenvSettings


async def get_context_object() -> VirtualMegalus:
    virtualenv_settings = VirtualenvSettings()
    obj = VirtualMegalus(settings=virtualenv_settings)
    return obj


def get_commands(cli: Group) -> None:
    cli.add_command(build)
    cli.add_command(run)
    cli.add_command(config)
    cli.add_command(rm)
