import requests
from colorama import Fore, Style
from distutils.version import LooseVersion
from tools import __version__
from tools import settings


def versions():
    url = "https://pypi.python.org/pypi/{}/json".format(settings.PYPI_NAME)
    data = None
    versions = None
    try:
        ret = requests.get(url, timeout=1)
        data = ret.json()
    except:
        pass
    if data:
        versions = list(data["releases"].keys())
        versions.sort(key=LooseVersion)
    return versions


def show_version_warning():
    last_version = __version__
    version_data = versions()
    if version_data:
        last_version = version_data[-1]
    if LooseVersion(last_version) > LooseVersion(__version__) and \
            "rc" not in last_version:
        print(Fore.LIGHTMAGENTA_EX + "Sua versão está desatualizada.")
        print("Última versão: {}\n".format(last_version) + Style.RESET_ALL)
