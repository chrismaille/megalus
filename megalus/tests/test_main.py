import sys
import tempfile
from pathlib import Path

import semantic_version
from loguru import logger

from megalus import __version__
from megalus.core.helpers import initialize_folders, initialize_logger


def test_version():
    assert isinstance(__version__, str)
    assert semantic_version.validate(__version__) is True


def test_initialize_folders(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv('MEGALUS_BASE_FOLDER', temp_dir)
        initialize_folders()
        assert Path(temp_dir).joinpath('virtualenvs').exists()


def test_initialize_logger(monkeypatch, mocker):
    mock_logger = mocker.patch.object(logger, 'configure')
    monkeypatch.setenv('MEGALUS_LOG_LEVEL', 'ERROR')
    initialize_logger()

    default_logger_message = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> |"
        " <level>{level: <8}</level> | <level>{message}</level>"
    )

    expected_config = {
        "handlers": [
            {"sink": sys.stdout, "format": default_logger_message, "level": "ERROR"}
        ]
    }

    mock_logger.assert_called_once_with(**expected_config)
