import asyncio
import hashlib
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

import aiofiles
import click
import stringcase
from loguru import logger

from megalus.core import Megalus, ServiceData
from megalus.core.decorators import run_async
from megalus.core.settings import BaseSettings


class VirtualenvSettings(BaseSettings):
    use_local_env = bool(os.getenv("MEGALUS_USE_LOCAL_ENV", False))
    default_venv_name = os.getenv("MEGALUS_DEFAULT_VENV_NAME", "venv")


class VirtualMegalus(Megalus):
    settings: VirtualenvSettings
    platform = "virtualenv"

    async def remove_virtualenv(self, service: ServiceData):
        # Get Virtualenv paths
        base_path, venv_name, venv_path = await self.get_virtualenv_paths(service)

        if venv_path.exists():
            logger.warning(f"Removing directory {venv_path}")
            shutil.rmtree(venv_path)
        else:
            logger.info(f"Directory {venv_path} not found. Skipping...")

    async def prepare_virtualenv(
            self, service: ServiceData
    ) -> Tuple[Path, Dict[str, str]]:

        # Get Virtualenv paths
        base_path, venv_name, venv_path = await self.get_virtualenv_paths(service)

        # Define Python location
        python_location = await self.get_python_version(service)

        if not venv_path.exists():
            logger.debug(f"Creating virtualenv in {venv_path}...")
            await self.run_command(
                f"cd {base_path} && virtualenv {venv_name} --python={python_location}"
            )

        logger.debug(f"Activating virtualenv in {venv_path}...")
        activate_this_file = venv_path.joinpath(
            self.script_directory, "activate_this.py"
        ).resolve()
        async with aiofiles.open(str(activate_this_file), "r") as file:
            data = await file.read()
        exec(data, {"__file__": str(activate_this_file)})

        return venv_path

    async def get_virtualenv_paths(self, service) -> Tuple[Path, str, Path]:
        if self.settings.use_local_env:
            venv_name = self.settings.default_venv_name
            base_path = Path(service.base_path)
            venv_path = base_path.joinpath(venv_name).resolve()
        else:
            path_hash = hashlib.md5(str(service.base_path).encode()).hexdigest()
            venv_name = f"{stringcase.snakecase(service.name)}_{path_hash[:8]}".lower()
            base_path = self.settings.base_folder.joinpath("virtualenvs")
            venv_path = base_path.joinpath(venv_name).resolve()
        return base_path, venv_name, venv_path

    async def execute(self, detached, service, command, queue):
        await self.prepare_virtualenv(service)

        command = f"cd {service.base_path} && " f"{command}"

        ret = await self.run_command(command, capture=detached)

        # TODO: Remove check after remove Python 3.6
        if hasattr(asyncio, "create_task"):
            queue.task_done()
        return ret


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def build(meg: VirtualMegalus, services: List[str], detached, need_reset):
    service_list = [
        await meg.find_service(service_name)
        for service_name in services
    ]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    results = await meg.run_queue('build', detached, service_list)
    await meg.show_results(results)


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@click.option("--build", "need_build", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def config(meg: VirtualMegalus, services: List[str], detached, need_build, need_reset):
    service_list = [
        await meg.find_service(service_name)
        for service_name in services
    ]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    if need_build:
        results = await meg.run_queue('build', detached, service_list)
        await meg.show_results(results)

    results = await meg.run_queue('config', detached, service_list)
    await meg.show_results(results)


@click.command()
@click.argument("service_name")
@click.argument("service_target")
@click.option("--build", "need_build", is_flag=True)
@click.option("--config", "need_config", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def run(
        meg: VirtualMegalus,
        service_name: str,
        service_target: str,
        need_build: bool,
        need_config: bool,
        need_reset: bool
):
    service_list = [
        await meg.find_service(service_name)
    ]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    if need_build:
        results = await meg.run_queue('build', None, False, service_list)
        await meg.show_results(results)

    if need_config:
        results = await meg.run_queue('config', None, False, service_list)
        await meg.show_results(results)

    results = await meg.run_queue('run', service_target, False, service_list)
    await meg.show_results(results)

@click.command()
@click.argument("services", nargs=-1)
@run_async
@click.pass_obj
async def rm(
        meg: VirtualMegalus,
        services: List[str]
):
    service_list = [
        await meg.find_service(service_name)
        for service_name in services
    ]

    for service in service_list:
        await meg.remove_virtualenv(service)