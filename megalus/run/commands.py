"""
commands.
"""
from typing import Optional

import click
from loguru import logger

from megalus.main import Megalus


@click.command()
@click.argument('command', nargs=1, required=True)
@click.argument('services', nargs=-1, required=False)
@click.pass_obj
def run(meg: Megalus, command: str, services: Optional[list]) -> None:

    line_to_run = meg.config_data['defaults'].get('scripts', {}).get(command, None)
    if not line_to_run:
        logger.warning('Command "{}" not found in configuration file.'.format(command))
    else:
        if services:
            for service in services:
                service_data = meg.find_service(service)
                meg.run_command(line_to_run.format(service=service_data['name']))
        else:
            meg.run_command(line_to_run)
