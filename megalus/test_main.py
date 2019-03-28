"""Test main code."""
from megalus.main import Megalus


def test_open_with_invalid_file(caplog):
    """Test open program with invalid file."""
    instance = Megalus(config_file="/path/not/found", logfile='/tmp/logfile')
    instance.get_services()
    running_command = [
        message
        for message in caplog.messages
        if "not found" in message
    ][0]
    assert "/path/not/found not found. Skipping..." in running_command
