from click import Group

from megalus.ext.virtualenv.commands import build


def includeme(cli: Group) -> None:
    cli.add_command(build)
