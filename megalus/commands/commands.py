"""
commands.
"""
import sys
from typing import Union, Optional

import click
from loguru import logger

from megalus.main import Megalus
from megalus.utils import run_command


def find_and_run_command(meg, service, action):
    if not service:
        config_command = meg.config_data['project'].get('commands').get(action, None)
    else:
        config_command = meg.config_data['services'].get(service, {}).get('commands', {}).get(action, {})
    if config_command:
        meg.run_command(config_command)
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


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def reset(meg: Megalus, service: Optional[str]):
    find_and_run_command(meg, service, "reset")


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def update(meg: Megalus, service: Optional[str]):
    find_and_run_command(meg, service, "update")
