# -*- coding: utf-8 -*-
import os
from tools.utils import run_command
from tools.config import get_config_data


def get_app(application):
    data = get_config_data()
    if not data:
        return False
    folder_name = os.path.split(data['project_path'])[-1]
    # 1. Lista todos os containers que estao rodando
    # docker ps -a | grep painel | awk '{print $1,$2}'
    ret = run_command(
        title=None,
        get_stdout=True,
        command_list=[
            {
                'command': "docker ps -a | awk '{print $1,$2}'",
                'run_stdout': False
            }
        ]
    )
    raw_list = ret.split('\n')
    print(raw_list)

    app_list = []
    i = 1

    for obj in raw_list:
        if obj == "CONTAINER ID":
            continue
        if len(obj.split(" ")) != 2:
            continue
        if obj.split(" ")[1].startswith(folder_name):
            app_list.append((
                i,
                obj.split(" ")[0],
                obj.split(" ")[1].replace("{}_".format(folder_name), "")
            ))
            i += 1

    # 2. Identifica qual o container que bate com o app solicitado
    pass


def run_deploy(application):
    # 1. Identifica o container
    container_id, name = get_app(application)
    if not container_id:
        return False
    
    # 2. Parar o container
    # docker-compose stop $app
    pass
    
    # 3. Inicia o container para Depurar
    # clear
    # echo "Rodando Depuração em $app"
    # echo "================="
    # docker-compose run --service-ports $app
