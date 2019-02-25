"""Stop command."""
from typing import List, Optional

import click

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus


def stop_all(meg: Megalus) -> None:
    """Stop all containers.

    :param meg: Megalus instance
    :return: None
    """
    compose_set = set([
        data['working_dir']
        for data in meg.all_services
    ])
    for compose_dir in list(compose_set):
        meg.run_command("cd {} && docker-compose stop".format(compose_dir))


@click.command()
@click.argument('services', nargs=-1)
@click.pass_obj
def stop(meg: Megalus, services: List[str]) -> None:
    """Stop selected services.

    :param meg: Megalus instance
    :param services: services to be stopped
    :return: None
    """
    if not services:
        stop_all(meg)
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "stop", service_data)
