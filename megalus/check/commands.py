"""Create folders in FTP.

Use the /app/ftp_tree.yaml to get tree structure.

Attributes
----------
    BASE_DIR (TYPE): Base dir for .geru files

"""

import click
import docker
from buzio import console
from docker.errors import ImageNotFound
from loguru import logger

from megalus.main import Megalus

client = docker.from_env()

def get_services(meg, service, service_list, ignore_list, tree, compose_data):
    if service in service_list or service in ignore_list:
        return

    service_list.append(service) if compose_data.get('build', None) else ignore_list.append(
        service)
    if compose_data.get('depends_on', None):
        tree = compose_data['depends_on']

    if tree:
        for key in tree:
            key_data = meg.find_service(key)
            get_services(meg, key, service_list, ignore_list, tree, key_data['compose_data'])
    return service_list, ignore_list


@click.command()
@click.argument('services', nargs=-1)
@click.pass_obj
def check(meg: Megalus, services):
    """Run main code."""

    def need_docker_image(service_data):
        if service_data.get('image', None) and service_data.get('build', None):
            try:
                client.images.get(service_data['image'])
                return False
            except ImageNotFound:
                return True
        return False

    service_list = []
    ignore_list = []
    for service in services:
        logger.info("Checking {}...".format(service))
        service_data = meg.find_service(service)
        service_list, ignore_list = get_services(meg, service, service_list, ignore_list, [], service_data['compose_data'])

    need_build = [
        service
        for service in service_list
        if need_docker_image(meg.find_service(service)['compose_data'])
    ]

    if need_build:
        logger.warning("Services without images: {}".format(", ".join(need_build)))

    # all_services = service_list + ignore_list
    # use_database = [
    #     service
    #     for service in all_services
    #     if 'postgres' in data['services'][service].get('depends_on', [])
    # ]
    #
    # psql_command = "psql -h 127.0.0.1 -p 5433 -U geru -lqt | cut -d \| -f 1 | grep -w {} >/dev/null"
    # if use_database:
    #     need_migrate = [
    #         service
    #         for service in use_database
    #         if not console.run(psql_command.format(service)) and
    #            'sentry' not in service and 'worker' not in service
    #     ]
    #     if need_migrate:
    #         console.warning("Services without databases: {}".format(", ".join(need_migrate)))
