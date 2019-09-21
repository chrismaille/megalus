"""Main module."""
import asyncio

import click
from click import Context

from megalus.commands.status import status
from megalus.core.config import initialize_folders, initialize_logger
from megalus.core.decorators import run_async
from megalus.core.platform import get_platform_commands, get_platform_context_object


@click.group()
@click.pass_context
@run_async
async def cli(ctx: Context) -> None:
    """Using Megalus.

    The first command to run is which platform you want to use.
    The default platform is "virtualenv", but you can use
    another platforms using plugins. For example, to use Docker
    install first the megalus-docker plugin:

    $ pip install megalus-docker

    And then, select docker using:

    $ meg use docker
    """
    megalus = await get_platform_context_object()
    await megalus.find_services()
    ctx.obj = megalus


initialize_folders()
initialize_logger()
cli.add_command(status)
get_platform_commands(cli)

if __name__ == "__main__":

    if hasattr(asyncio, "run"):
        asyncio.run(cli())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cli())
