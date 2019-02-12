import os
import sys
from pathlib import Path

import arrow
from loguru import logger

from megalus.utils import get_path

__version__ = "2.0.0a8"

BASE_LOG_PATH = os.path.join(str(Path.home()), '.megalus', 'logs')

if not os.path.exists(BASE_LOG_PATH):
    os.makedirs(BASE_LOG_PATH)

now = arrow.utcnow().to("local").isoformat()
LOGFILE = os.path.join(BASE_LOG_PATH, '{}.log'.format(now))

DEFAULT_LOGGER_MESSAGE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> |" \
                         " <level>{level: <8}</level> - <level>{message}</level>"

config = {
    "handlers": [
        {"sink": sys.stdout, "format": DEFAULT_LOGGER_MESSAGE},
        {"sink": LOGFILE, "retention": "7 days", "format": DEFAULT_LOGGER_MESSAGE}
    ],
}
logger.configure(**config)
