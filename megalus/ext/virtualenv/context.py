import asyncio
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Tuple

import aiofiles
import stringcase
from loguru import logger

from megalus.core import BaseMegalus, ServiceData
from megalus.ext.virtualenv import settings


class VirtualMegalus(BaseMegalus):
    settings: settings.VirtualenvSettings
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
