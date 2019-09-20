from click import Group

from megalus.ext.virtualenv.main import VirtualenvSettings, VirtualMegalus, build


def get_context_object() -> VirtualMegalus:
    virtualenv_settings = VirtualenvSettings()
    obj = VirtualMegalus(settings=virtualenv_settings)
    return obj


def get_commands(cli: Group) -> None:
    cli.add_command(build)
