"""Build command."""
from typing import List

import arrow as arrow
import click
from loguru import logger

from megalus import LOGFILE
from megalus.main import Megalus
from megalus.utils import update_service_status


def _build_services(meg, force, services) -> None:
    for service_to_find in services:
        logger.info('Looking for Service: {}'.format(service_to_find))
        service_data = meg.find_service(service_to_find)

        meg.run_command(
            'cd {} && docker-compose build --force-rm {}{} | pv -lft -D 2 >> {}'.format(
                service_data['working_dir'],
                " --no-cache " if force else "",
                service_data['name'],
                LOGFILE
            ))
        update_service_status(service_data['name'], "last_build", arrow.utcnow().to('local').isoformat())
        logger.success('Service {} builded.'.format(service_data['name']))


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def build(meg: Megalus, services: List, force: bool) -> None:
    """Run the build command on selected services.

    Use this command to build the selected services.

    :param meg: click context object
    :param services: services list to build
    :param force: use the --force to add the --no-cache option in build
    :return:
    """
    _build_services(meg, force, services)


@click.command()
@click.argument('groups', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def buildgroup(meg: Megalus, groups: List, force: bool) -> None:
    """Build a group of services.

    You can define a docker-compose services group in
    the megalus.yml file. This command will run the 'build'
    command for every one of them.

    :param meg: click context object
    :param groups: group list name
    :param force: use the --force to add the --no-cache option to build
    :return: None
    """
    all_groups = set(
        [
            meg.get_config_from_service(service, "group")
            for service in meg.config_data.get('services', {})
            if meg.get_config_from_service(service, "group") is not None
        ]
    )
    for group in groups:
        if group in all_groups:
            logger.info("Build group {}".format(group))
            group_services = [
                service
                for service in meg.config_data['services']
                if meg.get_config_from_service(service, "group") == group
            ]
            _build_services(meg, force, group_services)
        else:
            logger.warning("Group {} not found".format(group))
