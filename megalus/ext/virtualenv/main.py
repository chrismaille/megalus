import hashlib
import os
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

    async def prepare_virtualenv(
            self, service: ServiceData
    ) -> Tuple[Path, Dict[str, str]]:

        if self.settings.use_local_env:
            venv_name = self.settings.default_venv_name
            base_path = Path(service.base_path)
            venv_path = base_path.joinpath(venv_name).resolve()
        else:
            path_hash = hashlib.md5(str(service.base_path).encode()).hexdigest()
            venv_name = f"{stringcase.snakecase(service.name)}_{path_hash[:8]}".lower()
            base_path = self.settings.base_folder.joinpath('virtualenvs')
            venv_path = base_path.joinpath(venv_name).resolve()

        if not venv_path.exists():
            logger.debug(f"Creating virtualenv in {venv_path}...")
            await self.run_command(
                f"cd {base_path} && virtualenv {venv_name} --python=python{service.python_version}"
            )

        activate_this_file = venv_path.joinpath("bin", "activate_this.py").resolve()
        async with aiofiles.open(str(activate_this_file), "r") as file:
            data = await file.read()
        exec(data, {"__file__": str(activate_this_file)})

        return venv_path

    async def execute(self, detached, service, command, event):
        await self.prepare_virtualenv(service)

        command = (
            f"cd {service.base_path} && "
            f"{command}"
        )

        await self.run_command(command, show=not detached)
        event.set()


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@run_async
@click.pass_obj
async def build(meg: VirtualMegalus, services: List[str], detached):
    for service_name in services:
        service = await meg.find_service(service_name)
        await meg.execute_in_thread(service, "build", detached)


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@click.option("--build", "need_build", is_flag=True)
@run_async
@click.pass_obj
async def config(meg: VirtualMegalus, services: List[str], detached, need_build):
    for service_name in services:
        service = await meg.find_service(service_name)
        if need_build:
            await meg.execute_in_thread(service, "build", False)
        await meg.execute_in_thread(service, "config", detached)


@click.command()
@click.argument("service_name")
@click.option("--build", "need_build", is_flag=True)
@click.option("--config", "need_config", is_flag=True)
@click.option("--build_config", "build_config", is_flag=True)
@run_async
@click.pass_obj
async def run(
        meg: VirtualMegalus,
        service_name: str,
        need_build: bool,
        need_config: bool,
        build_config: bool,
):
    service = await meg.find_service(service_name)
    if need_build or build_config:
        await meg.execute_in_thread(service, "build", False)
    if need_config or build_config:
        await meg.execute_in_thread(service, "config", False)
    await meg.execute_in_thread(service, "run", False)
