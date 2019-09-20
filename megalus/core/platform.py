import os
from importlib import import_module

from typing import Type

import aiofiles
import yaml
from loguru import logger

from megalus.core import Megalus
from megalus.core.settings import BaseSettings


async def get_current_platform(sync: bool = False):
    settings = BaseSettings()
    # Get from env.
    current_platform = os.getenv('MEGALUS_USE_PLATFORM')
    if not current_platform:
        # Get from file
        megalus_info_path = settings.base_folder.joinpath('megalus.yml')
        if megalus_info_path.exists():
            if sync:
                with open(megalus_info_path, "r") as file:
                    info_data = yaml.safe_load(file.read())
            else:
                async with aiofiles.open(megalus_info_path, "r") as file:
                    info_data = yaml.safe_load(await file.read())
            current_platform = info_data.get('current_platform')
    if not current_platform:
        # Get default
        current_platform = "virtualenv"

    # import module
    logger.info(f"Current platform is: {current_platform}")
    if current_platform == "virtualenv":
        platform_module = import_module(f"megalus.ext.{current_platform}")
    else:
        platform_module = import_module(f"megalus_{current_platform}")

    return platform_module


def initialize_commands_per_platform(cli):
    platform_module = get_current_platform(sync=True)
    logger.info(f"Loading commands included in: {platform_module.__name__}")
    getattr(platform_module, "get_commands")(cli)


async def get_platform_context_object() -> Type[Megalus]:
    platform_module = await get_current_platform()
    return await getattr(platform_module, "get_context_object")()
