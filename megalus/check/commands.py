"""Check command."""
import os
from typing import List, Tuple, Optional

import arrow
import click
import docker
from docker import DockerClient
from docker.errors import ImageNotFound
from loguru import logger

from megalus.main import Megalus

client = docker.from_env()


def get_services_to_check(meg: Megalus, service: str, service_list: List[str], ignore_list: List[str], tree: List[str],
                          compose_data: dict) -> Optional[Tuple[List, List]]:
    """Get services to check.

    Recursively get all services to check and ignore.

    :param meg: click context object
    :param service: service to inspect
    :param service_list: services to check list
    :param ignore_list: services to ignore list
    :param tree: current service dependencies list
    :param compose_data: docker-compose data
    :return: Tuple
    """
    if service in service_list or service in ignore_list:
        return  # type: ignore

    service_list.append(service) if compose_data.get('build', None) else ignore_list.append(  # type: ignore
        service)
    if compose_data.get('depends_on', None):
        tree = compose_data['depends_on']

    if tree:
        for key in tree:
            key_data = meg.find_service(key)
            get_services_to_check(meg, key, service_list, ignore_list, tree, key_data['compose_data'])
    return service_list, ignore_list


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def check(meg: Megalus, services) -> None:
    """Check services.

    This command will check the selected services for:

    * Need build because does not have image
    * Need build because his image is outdated

    To find out if the image needs updating,
    add the list of files in the megalus.yml file,
    whose update date should be compared to the build date of the image.

    Example: if you add the 'Dockerfile', 'requirements.txt' and 'Pipfile'
    inside the 'check_for_build: files:' section in megalus.yml, this command will compare,
    for each file, his last modification date against docker image build date
    for the service.

    :param meg: click context object
    :param services: services list to be inspected
    :return: None
    """
    def get_docker_image(compose_data: dict) -> Optional[DockerClient]:  # type: ignore
        """Get docker image data.

        :param compose_data: compose parsed data.
        :return: DockerClient image instance or None
        """
        if compose_data.get('image', None) and compose_data.get('build', None):
            try:
                return client.images.get(compose_data['image'])
            except ImageNotFound:
                return None

    def has_old_image(ctx: Megalus, service: str) -> bool:
        """Check if image is outdated.

        :param ctx: Megalus instance
        :param service: docker service selected
        :return: bool
        """
        def get_date_from_file(file: str) -> arrow:
            """Get date from file.

            :param file: file full path
            :return: Arrow instance
            """
            date = arrow.get(os.path.getmtime(os.path.join(data['working_dir'], file))).to('local')
            logger.debug("Last update for file {} is {}".format(file, date))
            return date

        data = ctx.find_service(service)
        image = get_docker_image(data['compose_data'])
        if not image:
            return False
        else:
            image_date_created = arrow.get(image.attrs['Created']).to('local')
            global_files_to_watch = meg.config_data['defaults'].get('check_for_build', [])
            list_dates = [
                get_date_from_file(file)
                for file in global_files_to_watch
                if os.path.isfile(os.path.join(data['working_dir'], file))
                # FIXME: Acertar o working_dir + build.context para achar o path dos arquivos
            ]
            if list_dates and image_date_created < max(list_dates):
                return True
            return False

    service_list = []  # type: List[str]
    ignore_list = []  # type: List[str]
    for service in services:
        logger.info("Checking {}...".format(service))
        service_data = meg.find_service(service)
        service_list, ignore_list = get_services_to_check(  # type: ignore
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
