import os
from importlib import import_module
from typing import Type

import aiofiles
import yaml
from loguru import logger

from megalus.core import Megalus
from megalus.core.settings import BaseSettings


def _get_megalus_file():
    settings = BaseSettings()
    megalus_info_path = settings.base_folder.joinpath("megalus.yml")
    if megalus_info_path.exists():
        return megalus_info_path


def load_config_file():
    megalus_info_path = _get_megalus_file()
    if not megalus_info_path:
        return {}
    with open(megalus_info_path, "r") as file:
        info_data = yaml.safe_load(file.read())
    return info_data


async def load_config_file_async():
    megalus_info_path = _get_megalus_file()
    if not megalus_info_path:
        return {}
    async with aiofiles.open(megalus_info_path, "r") as file:
        info_data = yaml.safe_load(await file.read())
    return info_data


def get_current_platform(info_data):
    # Get from env.
    current_platform = os.getenv("MEGALUS_USE_PLATFORM")
    if not current_platform:
        # Get from megalus.yaml file
        current_platform = info_data.get("current_platform")
    if not current_platform:
        # Get default
        current_platform = "virtualenv"

    # import module
    if current_platform == "virtualenv":
        platform_module = import_module(f"megalus.ext.{current_platform}")
    else:
        platform_module = import_module(f"megalus_{current_platform}")

    return platform_module


def get_platform_commands(cli):
    info_data = load_config_file()
    platform_module = get_current_platform(info_data)
    logger.info(f"Loading commands in: {platform_module.__name__}")
    getattr(platform_module, "get_commands")(cli)


async def get_platform_context_object() -> Type[Megalus]:
    info_data = await load_config_file_async()
    platform_module = get_current_platform(info_data)
    return await getattr(platform_module, "get_context_object")()
