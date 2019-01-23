"""
commands.
"""
import re
import sys
from time import sleep

import arrow
import click
from buzio import console
from loguru import logger

from megalus.main import Megalus
from megalus.utils import find_containers, find_service


def show_log(name, line):
    config = {
        "handlers": [
            {
                "sink": sys.stderr,
                "format": "<d><lvl>{level: <8}</lvl> | <cyan>{extra[container]}</cyan> "
                          "| <blue>{extra[docker_timestamp]}</blue></d> | <lvl>{message}</lvl>",
                "colorize": True
            }
        ],
        "extra": {
            "container": name,
            "docker_timestamp": arrow.get(line[:22]).to('local')
        }
    }
    logger.configure(**config)
    if "ERROR:" in line or "FATAL:" in line or "CRITICAL:" in line:
        logger.error(line[31:])
    elif "WARNING:" in line:
        logger.warning(line[31:])
    elif "DEBUG:" in line:
        logger.debug(line[31:])
    else:
        logger.info(line[31:])


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--regex')
@click.pass_obj
def logs(meg: Megalus, services: list, regex: str):
    try:
        time_to_fetch = 2
        services_data_to_log = [
            meg.find_service(service_to_find)
            for service_to_find in services
        ]
        while True:
            for service_data in services_data_to_log:
                if len(services_data_to_log) > 1:
                    console.section(service_data['name'])
                containers = find_containers(service_data['name'])
                for container in containers:
                    log_data = container.logs(timestamps=True, stream=True, since=time_to_fetch)
                    for data in log_data:
                        if data:
                            line = data.decode('UTF-8').replace("\n", "")
                            if regex:
                                ret = re.search(regex, line)
                                if not ret:
                                    continue
                            show_log(container.name, line)
            sleep(time_to_fetch)
    except KeyboardInterrupt:
        sys.exit(0)
