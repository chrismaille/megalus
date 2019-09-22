import asyncio
import os
import re
import sys
from functools import wraps
from pathlib import Path

from loguru import logger


def initialize_logger():
    default_logger_message = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> |"
        " <level>{level: <8}</level> | <level>{message}</level>"
    )
    log_level = os.getenv("MEGALUS_LOG_LEVEL", "DEBUG")
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": default_logger_message, "level": log_level}
        ]
    }
    logger.configure(**config)


def initialize_folders():
    base_log_path = os.getenv("MEGALUS_BASE_FOLDER", "~/.megalus")
    log_path = Path(base_log_path).expanduser().resolve()
    log_path.mkdir(parents=True, exist_ok=True)
    virtualenv_path = log_path.joinpath("virtualenvs")
    virtualenv_path.mkdir(parents=True, exist_ok=True)


def get_path(path: Path, base_path: str) -> Path:
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
                part if "$" not in part else name for part in env_in_path.split("/")
            ]
            path = os.path.join(*path_list)
        else:
            raise ValueError("Cant find path for {}".format(env_in_path))
        return path

    if "$" in base_path:
        base_path = _convert_env_to_path(base_path)
    path = str(path.resolve())
    if "$" in path:
        path = _convert_env_to_path(path)
    if path.startswith("."):
        list_path = os.path.join(base_path, path)
        path = os.path.abspath(list_path)
    return Path(path)


def run_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if hasattr(asyncio, "run"):
            return asyncio.run(f(*args, **kwargs))
        else:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(f(*args, **kwargs))

    return wrapper