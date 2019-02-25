import logging
import os
from unittest.mock import Mock

import pytest
# noinspection PyUnresolvedReferences
from _pytest.logging import caplog as _caplog
from loguru import logger

from megalus.main import Megalus


def pytest_generate_tests(metafunc):
    os.environ['MEGALUS_PROJECT_CONFIG_FILE'] = './example/megalus.yml'


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropogateHandler(), format="{message}")
    yield _caplog


@pytest.fixture
def obj():
    obj = Megalus(
        config_file=os.getenv('MEGALUS_PROJECT_CONFIG_FILE'),
        logfile='/temp/log'
    )
    obj.get_services()
    return obj


@pytest.fixture
def django_container():
    container_data = Mock()
    container_data.name = 'test_django_1'
    container_data.short_id = "1234abcd"
    return container_data
