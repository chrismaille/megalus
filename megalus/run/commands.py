"""
commands.
"""
import sys

import click
from buzio import console
from loguru import logger

from megalus.main import Megalus
from megalus.utils import run_command


@click.command()
@click.argument('commands', nargs=-1, required=True)
@click.pass_obj
def run(meg: Megalus, commands: list):
    for command in commands:
        line_to_run = meg.config_data['project'].get('scripts', {}).get(command, None)
        if not line_to_run:
            logger.warning('Command "{}" not found in configuration file.'.format(command))
        else:
            run_command(meg, line_to_run)

