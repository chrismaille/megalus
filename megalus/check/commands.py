"""Create folders in FTP.

Use the /app/ftp_tree.yaml to get tree structure.

Attributes
----------
    BASE_DIR (TYPE): Base dir for .geru files

"""
import os

import arrow
import click
import docker
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

    def get_docker_image(compose_data):
        if compose_data.get('image', None) and compose_data.get('build', None):
            try:
                return client.images.get(compose_data['image'])
            except ImageNotFound:
                return None

    def has_old_image(ctx, service):

        def get_date_from_file(file):
            date = arrow.get(os.path.getmtime(os.path.join(data['working_dir'], file))).to('local')
            logger.debug("Last update for file {} is {}".format(file, date))
            return date

        data = ctx.find_service(service)
        image = get_docker_image(data['compose_data'])
        if not image:
            return False
        else:
            image_date_created = arrow.get(image.attrs['Created']).to('local')
            global_files_to_watch = meg.config_data['project'].get('check_for_build', {}).get('files', [])
            project_files_to_watch = meg.config_data['services'].get(service, {}).get('check_for_build', {}).get('files', [])
            all_files = global_files_to_watch + project_files_to_watch
            list_dates = [
                get_date_from_file(file)
                for file in all_files
                if os.path.isfile(os.path.join(data['working_dir'], file))  # FIXME: Acertar o working_dir + build.context para achar o path dos arquivos
            ]
            if list_dates and image_date_created < max(list_dates):
                return True
            return False


    service_list = []
    ignore_list = []
    for service in services:
        logger.info("Checking {}...".format(service))
        service_data = meg.find_service(service)
        service_list, ignore_list = get_services(
            meg, service, service_list, ignore_list, [],
            service_data['compose_data']
        )

    services_without_images = [
        service
        for service in service_list
        if get_docker_image(meg.find_service(service))
    ]

    if services_without_images:
        logger.warning("Services without images: {}".format(", ".join(services_without_images)))

    services_with_old_images = [
        service
        for service in service_list
        if service not in services_without_images and has_old_image(meg, service)
    ]

    if services_with_old_images:
        logger.warning("Services with old images: {}".format(", ".join(services_with_old_images)))
