"""Init module."""
import json
from os import path

from megalus.utils import get_path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "..", "version.json")) as json_file:
    version_data = json.load(json_file)

__version__ = version_data['version']
