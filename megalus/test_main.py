"""Test main code."""
import os
import platform
import tempfile

import pytest

from megalus.main import Megalus


def test_open_with_not_found_file(caplog):
    """Test open program with not found file."""

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = os.path.join(temp_dir_name, "docker-compose.yml")
        instance = Megalus(config_file=temp_dir, logfile='/tmp/logfile')
        instance.get_services()
        running_command = [
            message
            for message in caplog.messages
            if "not found" in message
        ][0]
        assert "{} not found. Skipping...".format(temp_dir) in running_command


@pytest.mark.skipif("windows" in platform.system().lower(), reason="Not reliable in Windows.")
@pytest.mark.xfail
def test_open_with_invalid_file(caplog):
    """Test open program with invalid file."""

    with tempfile.TemporaryDirectory() as temp_dir_name:
        with tempfile.NamedTemporaryFile(dir=temp_dir_name) as temp_file:
            instance = Megalus(config_file=temp_file.name, logfile='/tmp/logfile')
            instance.get_services()
            running_command = [
                message
                for message in caplog.messages
                if "not found" in message
            ][0]
            assert "{} has a invalid configuration. Skipping...".format(temp_file) in running_command
