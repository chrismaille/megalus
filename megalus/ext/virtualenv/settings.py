import os

from megalus.core.settings import BaseSettings


class VirtualenvSettings(BaseSettings):
    use_local_env: bool
    default_venv_name: str

    def __init__(self):
        self.use_local_env = bool(os.getenv("MEGALUS_USE_LOCAL_ENV", False))
        self.default_venv_name = os.getenv("MEGALUS_DEFAULT_VENV_NAME", "venv")
