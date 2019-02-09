"""
commands.
"""
import sys
from typing import Optional

import arrow
import click
from loguru import logger

from megalus.main import Megalus
from megalus.utils import save_status


def find_and_run_command(meg, service, action):
    if not service:
        config_command = meg.config_data['defaults'].get('config_commands', {}).get('default')
    else:
        config_command = meg.config_data['defaults'].get('config_commands', {}).get(service)
    if config_command:
        if "{service}" in config_command:
            meg.run_command(config_command.format(service=service))
        else:
            meg.run_command(config_command)
        save_status(service, "last_{}".format(action), arrow.utcnow().to('local').isoformat())
    else:
        logger.error("No command defined in configuration.")
        sys.exit(1)


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def config(meg: Megalus, service: Optional[str]):
    find_and_run_command(meg, service, "config")


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def install(meg: Megalus, service: Optional[str]):
    find_and_run_command(meg, service, "install")


