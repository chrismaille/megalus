"""
clone.
"""
import os
from pathlib import Path
from typing import List

import click
from loguru import logger

from megalus import LOGFILE, Megalus
from megalus.utils import backup_folder


def get_clone_path(service_data: dict) -> Path:
    path = service_data['compose_data'].get('build', {}).get('context', None)
    clone_path = Path(os.path.join(service_data['working_dir'], path)).resolve()
    logger.debug("Clone path for service {} is: {}".format(service_data['name'], clone_path))
    return clone_path


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def clone(meg: Megalus, services: List, force: bool) -> None:
    for service in services:
        service_data = meg.find_service(service)

        clone_path = get_clone_path(service_data)
        if os.path.exists(clone_path):
            if not force:
                logger.warning("Ignoring path {} - already exists.".format(clone_path))
                continue
            else:
                backup_folder(clone_path)

        repository_url = meg.get_config_from_service(service, "repository")
        if repository_url:
            logger.info("Cloning {} in path {}".format(repository_url, clone_path))
            meg.run_command(
                "git clone --progress {} {} 2> {}".format(repository_url, clone_path, LOGFILE)
            )
