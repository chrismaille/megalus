import os
from importlib import import_module

from loguru import logger


def initialize_platform(cli):
    current_platform = os.getenv("MEGALUS_CURRENT_PLATFORM", "virtualenv")
    logger.info(f"Current platform is: {current_platform}")
    platform_module = import_module(f"megalus.ext.{current_platform}")
    getattr(platform_module, "includeme")(cli)