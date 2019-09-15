import sys
from pathlib import Path
from typing import List

import click
from loguru import logger

from megalus.core import Megalus
from megalus.core.decorators import run_async
from megalus.core.megalus import ServiceData


async def prepare_virtualenv(service: ServiceData, meg: Megalus):
    base_path = Path(service.base_path)
    venv_path = base_path.joinpath('venv')

    if not venv_path.exists():
        await meg.run_command(f"cd {base_path} && virtualenv venv --python==python{service.python_version}")

    await meg.run_command(f"cd {base_path} && deactivate && source venv/bin/activate")


@click.command()
@click.argument("services", nargs=-1)
@run_async
@click.pass_obj
async def build(meg: Megalus, services: List[str]):
    for service_name in services:
        service = await meg.find_service(service_name)
        logger.info(f"Service is {service.name}")

        await prepare_virtualenv(service, meg)

        command = f"cd {service.base_path} && " \
                  f"{service.data.get('build').get('virtualenv')}"

        return_code = await meg.show_command(command)

        sys.exit(return_code)
