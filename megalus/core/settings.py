import os

from pathlib import Path
from typing import List


class BaseSettings:
    base_folder: Path
    project_paths: List[Path]
    exit_on_errors: bool

    def __init__(self):
        self.base_folder = Path(
            os.getenv("MEGALUS_BASE_FOLDER", Path("~/.megalus").expanduser())
        )
        self.project_paths = [
            Path(folder) for folder in os.environ.get("MEGALUS_PROJECT_PATHS", "").split(",")
        ]
        self.exit_on_errors = bool(os.getenv("MEGALUS_EXIT_ON_ERRORS", False))
