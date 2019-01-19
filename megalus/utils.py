import datetime
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

import docker
from buzio import console
from loguru import logger

client = docker.from_env()


def find_service(compose_file, service_informed):
    compose_services = compose_file['services']

    if service_informed in compose_services:
        service_name = service_informed
    else:
        eligible_services = [
            eligible_service
            for eligible_service in compose_services
            if service_informed in eligible_service
        ]
        if not eligible_services:
            logger.error("Service not found")
            sys.exit(1)
        elif len(eligible_services) == 1:
            service_name = eligible_services[0]
        else:
            service_name = console.choose(eligible_services, 'Please select the service')
    return service_name, compose_file['services'][service_name]


def find_containers(service):
    eligible_containers = [
        container
        for container in client.containers.list()
        if service in container.name
    ]
    return eligible_containers


def backup_folder(folder_path):
    folders = list(Path(folder_path).parts)
    folder_hash = hashlib.md5(datetime.datetime.now().isoformat().encode("utf-8")).hexdigest()
    last_folder = "{}_{}".format(folders[-1], folder_hash[:10])
    folders.remove(folders[-1])
    folders.append(last_folder)
    backup_path = os.path.join(*folders)
    logger.warning('Directory already exists. Moving folder to {}'.format(backup_path))
    shutil.move(folder_path, backup_path)


def run_command(meg, command):
    logger.debug("Running command: {}".format(command))
    command_to_run = "{run_before}{command}{run_after}".format(
        run_before="{} && ".format(meg.run_before) if meg.run_before else "",
        command=command,
        run_after=" && {}".format(meg.run_after) if meg.run_after else ""
    )
    ret = console.run(command_to_run)
    if not ret:
        sys.exit(1)


def get_path(path: str, base_path: str) -> str:
    """Return real path from string.

    Converts environment variables to path
    Converts relative path to full path
    """

    def _convert_env_to_path(env_in_path):
        s = re.search(r"\${(\w+)}", env_in_path)
        if not s:
            s = re.search(r"(\$\w+)", env_in_path)
        if s:
            env = s.group(1).replace("$", "")
            name = os.environ.get(env)
            if not name:
                raise ValueError("Can't find value for {}".format(env))
            path_list = [
                part if "$" not in part else name
                for part in env_in_path.split("/")
            ]
            path = os.path.join(*path_list)
        else:
            raise ValueError("Cant find path for {}".format(env_in_path))
        return path

    if "$" in base_path:
        base_path = _convert_env_to_path(base_path)
    if "$" in path:
        path = _convert_env_to_path(path)
    if path.startswith("."):
        list_path = os.path.join(base_path, path)
        path = os.path.abspath(list_path)
    return path
