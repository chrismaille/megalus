# -*- coding: utf-8 -*-
import os
from tools.utils import run_command, get_app
from tools.config import get_config_data


def run_debug(application):
    data = get_config_data()
    if not data:
        return False
    # 1. Identifica o container
    container_id, name = get_app(
        application=application,
        title="Rodar em Modo Depuração",
        data=data)
    if not container_id:
        return False

    # 2. Parar e reiniciar o container com service ports
    # docker-compose stop $app
    # docker-compose run --service-ports $app
    os.system('cls' if os.name == 'nt' else 'clear')
    os.chdir(data['project_path'])
    run_command(
        title="Modo Depuração: {}".format(name),
        get_stdout=True,
        command_list=[
            {
                'command': "docker-compose stop {}".format(name),
                'run_stdout': False
            },
        ]
    )
    os.system(
        'docker-compose run --service-ports {}\n'.format(
            name
        )
    )

    return False
