# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
import urllib2
from distutils.version import StrictVersion, LooseVersion
from tools import VERSION


def versions():
    url = "https://pypi.python.org/pypi/li-aws-deploy/json"
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
    last_version = VERSION
    version_data = versions()
    if version_data:
        last_version = version_data[-1]
    if LooseVersion(last_version) > LooseVersion(VERSION):
        print("\033[91mSua versão está desatualizada.")
        print("Última versão: {}\n\033[0m".format(last_version))
