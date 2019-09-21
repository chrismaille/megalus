import os

from megalus.core.settings import BaseSettings


class VirtualenvSettings(BaseSettings):
    use_local_env = bool(os.getenv("MEGALUS_USE_LOCAL_ENV", False))
    default_venv_name = os.getenv("MEGALUS_DEFAULT_VENV_NAME", "venv")
