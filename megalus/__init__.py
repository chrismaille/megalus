import datetime
import os
import sys
from pathlib import Path

from loguru import logger

from megalus.utils import get_path

__version__ = "2.0.0a5"

BASE_LOG_PATH = os.path.join(str(Path.home()), '.megalus', 'logs')

if not os.path.exists(BASE_LOG_PATH):
    os.makedirs(BASE_LOG_PATH)

now = datetime.datetime.now().isoformat()
LOGFILE = os.path.join(BASE_LOG_PATH, '{}.log'.format(now))

config = {
    "handlers": [
        {"sink": sys.stdout},
        {"sink": LOGFILE, "retention": "7 days"}
    ],
}
logger.configure(**config)
