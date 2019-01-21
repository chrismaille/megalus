"""
BUILD
Usage: geru build [--no-cache]| [<service> ...]
This command will build the selected service (using docker-compose build).
Use the --no-cache option to force installing without cache
If you do not inform any service, the command will make the minimal install
**Do not start this until you have tested your docker install.**

This command will make the minimum install: ***core***, ***migrate***,
***awscli***, ***geru-ngrok***, ***ftp*** and ***monitor*** services.

If you have issues with docker cache during install, use the command
`geru forcebuild <service>` to make install.


##### Troubleshooting:

1. Check if the repositories are in their default branches (ie. stage)
2. Check if you have permission to read the repositories
3. Check if you git personal token has all "repo" operations marked
4. Check if your docker are working correctly typing `docker run busybox
  nslookup google.com`
5. Check you have at least 40Gb free disk space.
6. Check your internet connection. You can run again `geru build` (the
   build will resume the operation)
"""
from typing import List

import click
from loguru import logger

from megalus import LOGFILE
from megalus.main import Megalus


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
        logger.success('Service {} builded.'.format(service_data['name']))


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def build(meg: Megalus, services: List, force: bool) -> None:
    _build_services(meg, force, services)


@click.command()
@click.argument('groups', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def buildgroup(meg: Megalus, groups: List, force: bool) -> None:
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
