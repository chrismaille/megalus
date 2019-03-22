"""Docker-Compose commands module."""
from typing import List

import click

from megalus.main import Megalus


def run_compose_command(meg: Megalus, action: str, service_data: dict, options: str = "") -> None:
    """Run docker-compose command.

    :param meg: Megalus instance
    :param action: docker-compose command
    :param service_data: docker service parsed data
    :param options: docker-compose command options
    :return: None
    """
    meg.run_command(
        "cd {working_dir} && docker-compose {files} {action}{options}{services}".format(
            working_dir=service_data['working_dir'],
            files="-f {}".format(" -f ".join(service_data['compose_files'])),
            options=" {} ".format(options) if options else " ",
            action=action,
            services=service_data.get('name', "")
        )
    )


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def restart(meg: Megalus, services: List[str]) -> None:
    """Restart selected services.

    :param meg: Megalus instance.
    :param services: Docker services
    :return: None
    """
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "restart", service_data)


@click.command()
@click.argument('service', required=True)
@click.argument('number', required=True, default=1, type=click.INT)
@click.pass_obj
def scale(meg: Megalus, service: str, number: int) -> None:
    """Scale selected services.

    :param meg: Megalus instance
    :param service: docker service to be scaled
    :param number: number of replicas
    :return: None
    """
    service_data = meg.find_service(service)
    options = "-d --scale {}={}".format(service_data['name'], number)
    run_compose_command(meg, "up", options=options, service_data=service_data)


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('-d', is_flag=True)
@click.pass_obj
def up(meg: Megalus, services: List[str], d: bool) -> None:
    """Start selected services.

    :param meg: Megalus instance
    :param services: Services to be started up
    :param d: detached option
    :return: None
    """
    options = "-d" if d or len(services) > 1 else ""
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "up", options=options, service_data=service_data)
