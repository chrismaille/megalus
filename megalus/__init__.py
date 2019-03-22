"""Init module."""
import json

from megalus.utils import get_path

with open("version.json") as json_file:
    version_data = json.load(json_file)

__version__ = version_data['version']
