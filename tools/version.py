# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
import urllib2
from distutils.version import StrictVersion, LooseVersion
from tools import __version__
from tools import settings


def versions():
    url = "https://pypi.python.org/pypi/{}/json".format(settings.PYPI_NAME)
    data = None
    versions = None
    try:
        ret = urllib2.urlopen(urllib2.Request(url), timeout=1)
        data = json.load(ret)
    except:
        pass
    if data:
        versions = data["releases"].keys()
        versions.sort(key=LooseVersion)
    return versions


def show_version_warning():
    last_version = __version__
    version_data = versions()
    if version_data:
        last_version = version_data[-1]
    if LooseVersion(last_version) > LooseVersion(__version__) and \
        "rc" not in last_version:
        print("\033[91mSua versão está desatualizada.")
        print("Última versão: {}\n\033[0m".format(last_version))
