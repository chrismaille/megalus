import os

from pathlib import Path


class BaseSettings:
    base_folder = Path(
        os.getenv("MEGALUS_BASE_FOLDER", Path("~/.megalus").expanduser())
    )
    project_paths = [
        Path(folder) for folder in os.environ.get("MEGALUS_PROJECT_PATHS").split(",")
    ]
    exit_on_errors = bool(os.getenv("MEGALUS_EXIT_ON_ERRORS", False))
