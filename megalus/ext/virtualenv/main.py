import hashlib
import os
from pathlib import Path
from typing import List, Tuple

import click
from loguru import logger

from megalus.core import Megalus, ServiceData
from megalus.core.decorators import run_async
from megalus.core.settings import BaseSettings


class VirtualenvSettings(BaseSettings):
    use_local_env = bool(os.getenv('MEGALUS_USE_LOCAL_ENV', False))
    default_venv_name = os.getenv('MEGALUS_DEFAULT_VENV_NAME', 'venv')


class VirtualMegalus(Megalus):
    settings: VirtualenvSettings

    async def prepare_virtualenv(self, service: ServiceData) -> Tuple[Path, str]:

        if self.settings.use_local_env:
            venv_name = self.settings.default_venv_name
            base_path = Path(service.base_path)
            venv_path = base_path.joinpath(venv_name).resolve()
        else:
            path_hash = hashlib.md5(str(service.base_path).encode()).hexdigest()
            venv_name = f"{service.name}_{path_hash[:8]}".lower()
            base_path = self.settings.base_folder
            venv_path = base_path.joinpath(venv_name).resolve()

        if not venv_path.exists():
            logger.debug(f"Creating virtualenv in {venv_path}...")
            await self.run_command(f"cd {base_path} && virtualenv {venv_name} --python==python{service.python_version}")

        virtualenv_command = "source bin/activate"

        return venv_path, virtualenv_command


@click.command()
@click.argument("services", nargs=-1)
@run_async
@click.pass_obj
async def build(meg: VirtualMegalus, services: List[str]):
    for service_name in services:
        service = await meg.find_service(service_name)

        virtualenv_path, virtualenv_command = await meg.prepare_virtualenv(service)

        command = f"cd {virtualenv_path} && deactivate && {virtualenv_command} && " \
                  f"cd {service.base_path} && " \
                  f"{service.data.get('build').get('virtualenv')}"

        return_code = await meg.show_command(command)

        meg.exit(return_code)
