#! /usr/bin/env python3
import os
from os.path import expanduser
from deploy.utils import run_command

APPLICATIONS = [
    ('LI-Docker','master'),
    ('LI-Api-Carrinho', 'staging'),
    ('LI-Api-Catalogo', 'staging'),
    ('LI-Api-Envio', 'staging'),
    ('LI-Api-Faturamento', 'staging'),
    ('LI-Api-Integration', 'staging'),
    ('LI-Api-Marketplace', 'staging'),
    ('LI-Api-Pagador', 'staging'),
    ('LI-Api-Pedido', 'staging'),
    ('LI-Api-Plataforma', 'staging'),
    ('LI-Api-V2', 'staging'),
    ('LI-AppApi', 'staging'),
    ('LI-AppConciliacao', 'staging')
    ('LI-AppLoja', 'staging'),
    ('LI-AppPainel', 'staging'),
    ('LI-Worker', 'staging'),
    ('LI-Worker-Integration', 'staging'),
    ('LI-Repo', 'master')
]

MINIFY_BEFORE = [
    'LI-AppLoja'
]

SYNC_S3 = [
    'LI-AppLoja',
    'LI-AppPainel'
]


def get_config_data(filename="li-config"):
    # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = {
        "aws_key": None,
        "aws_secret": None,
        "aws_account": None,
        "aws_region": None,
        "project_path": None,
        "slack_user": None,
        "slack_url": None,
        "slack_channel": None,
        "slack_icon": None,
        "datadog_api_key": None,
        "datadog_app_key": None
    }
    basepath = expanduser("~")
    filepath = os.path.join(basepath, ".{}".format(filename))

    # Checa:
    # 1. arquivo de configuracao existe,
    # 2. arquivo está completo
    # 3. a variavel de ambiente está na memoria
    # 4. a pasta das aplicações existe

    ret = True

    if not os.path.exists(filepath):
        ret = False
    else:
        with open(filepath, 'r') as file:
            for line in file:
                key = line.split("=")[0].lower()
                value = line.split("=")[1].rstrip()
                config[key] = value

        for key in config:
            if not config.get(key):
                ret = False

        if not os.environ.get('LI_PROJECT_PATH'):
            ret = False

        if not os.path.exists(os.environ.get('LI_PROJECT_PATH')):
            ret = False

    if ret:
        return config
    else:
        print("\n>> Configuração")
        print("***************")
        with open(filepath, 'a') as file:
            for key in config:
                if not config.get(key):
                    value = input("Informe {}: ".format(key))
                    config[key] = value
                    file.write("{}={}\n".format(key.upper(), value))

        # Grava arquivo de credenciais da Amazon
        aws_folder = os.path.join(basepath, ".aws")
        if not os.path.exists(aws_folder):
            os.makedirs(aws_folder)
            with open(os.path.join(aws_folder, "config"), 'w') as file:
                file.write("[config]")

        with open(os.path.join(aws_folder, "credentials"), 'w') as file:
            file.write('[default]')
            file.write('aws_access_key_id = {}'.format(config['aws_key']))
            file.write(
                'aws_secret_access_key = {}'.format(
                    config['aws_secret']))

        # Grava no bashrc a variavel LI_PROJECT_PATH
        profile_path = os.path.join(basepath, '.profile')
        project_path = config['project_path']
        if 'LI_PROJECT_PATH' not in open(profile_path).read():
            run_command(
                title=None, command_list=[
                    {
                        'command': "echo export LI_PROJECT_PATH='{}' >> {}".format(
                            project_path, profile_path), 'run_stdout': False}, {
                        'command': "export LI_PROJECT_PATH='{}'".format(
                            project_path), 'run_stdout': False}], )

        # Clona os repositorios LI
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            for app, branch in APPLICATIONS:
                # git config --global credential.helper 'cache --timeout=3600'
                run_command(
                    title="Clonando Repositórios"
                    command_list=[
                        {
                            'command': "git config --global credential.helper 'cache --timeout=3600'"
                            'run_stdout': False
                        }
                    ]
                )
                run_command(
                    title=None,
                    command_list=[
                        {
                            'command': "git clone -b {branch} {url} {dir}".format(
                                branch=branch,
                                url="https://github.com/lojaintegrada/{}.git".format(app.lower()),
                                dir=os.path.join(project_path, app)
                            ),
                            'run_stdout': False
                        }
                    ]
                )

    return config
