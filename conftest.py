"""Pytest Configuration file."""
import json as json_loader
import logging
import os
from unittest.mock import Mock

import pytest
# noinspection PyUnresolvedReferences
from _pytest.logging import caplog as _caplog
from loguru import logger

from megalus.main import Megalus


def pytest_generate_tests(metafunc):
    """Tests Pre-Run."""
    os.environ['MEGALUS_PROJECT_CONFIG_FILE'] = './example/megalus.yml'


@pytest.fixture
def caplog(_caplog):
    """Hack pytest caplog for use with Loguru."""

    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropogateHandler(), format="{message}")
    yield _caplog


@pytest.fixture
def obj() -> Megalus:
    """Return click context object.

    :return: Megalus Instance
    """
    obj = Megalus(
        config_file=os.getenv('MEGALUS_PROJECT_CONFIG_FILE'),
        logfile='/temp/log'
    )
    obj.get_services()
    return obj


@pytest.fixture
def django_container():
    """Return mock container data."""
    container_data = Mock()
    container_data.name = 'test_django_1'
    container_data.short_id = "1234abcd"
    return container_data


@pytest.fixture
def ngrok_response():
    """Mock ngrok request response.

    :return: None
    """

    def _return_json():
        return json_loader.loads(response.content)

    def _raise_for_status():
        return True

    response = Mock()
    response.content = \
        b'{"tunnels":[{"name":"core","uri":"/api/tunnels/core","public_url":"https://87f3557f.ngrok.io",' \
        b'"proto":"https","config":{"addr":"http://localhost:6544","inspect":true},' \
        b'"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,' \
        b'"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}},' \
        b'{"name":"vitas","uri":"/api/tunnels/vitas","public_url":"https://10e3ea7f.ngrok.io",' \
        b'"proto":"https","config":{"addr":"http://localhost:6600","inspect":true},"metrics":' \
        b'{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},' \
        b'"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}},' \
        b'{"name":"core (http)","uri":"/api/tunnels/core%20%28http%29",' \
        b'"public_url":"http://87f3557f.ngrok.io","proto":"http","config":' \
        b'{"addr":"http://localhost:6544","inspect":true},"metrics":{"conns":' \
        b'{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},' \
        b'"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}},' \
        b'{"name":"vitas (http)","uri":"/api/tunnels/vitas%20%28http%29","public_url":' \
        b'"http://10e3ea7f.ngrok.io","proto":"http","config":{"addr":"http://localhost:6600",' \
        b'"inspect":true},"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,' \
        b'"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,' \
        b'"p50":0,"p90":0,"p95":0,"p99":0}}}],"uri":"/api/tunnels"}\n'
    response.json = _return_json
    response.status_code = 200
    response.raise_for_status = _raise_for_status
    return response
