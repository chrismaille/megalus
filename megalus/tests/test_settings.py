from pathlib import Path

from megalus.core.settings import BaseSettings


def test_base_settings(monkeypatch):
    monkeypatch.setenv('MEGALUS_BASE_FOLDER', '/tmp')
    monkeypatch.setenv('MEGALUS_PROJECT_PATHS', './example')
    monkeypatch.setenv('MEGALUS_EXIT_ON_ERRORS', True)
    settings = BaseSettings()
    assert settings.base_folder == Path("/tmp")
    assert settings.project_paths == [Path('./example')]
    assert settings.exit_on_errors is True
