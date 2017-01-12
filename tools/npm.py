# -*- coding: utf-8 -*-
import os
from tools import settings
from tools.config import get_config_data, run_update
from tools.messages import notify
from tools.utils import run_command, get_app, confirma


def run_watch(application):
    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Rodar em modo Watch",
        data=data
    )
    if not container_id:
        return False

    watch_path = os.join(
        data['project_path'],
        name.lower(),
        'frontend'
    )

    os.system(
        'cd {}/ && ./node_modules/.bin/webpack --config webpack.config.js --watch\n'.format(
            watch_path)
    )
