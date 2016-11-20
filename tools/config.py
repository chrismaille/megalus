# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
import platform
from os.path import expanduser
from tools.utils import run_command, confirma

APPLICATIONS = [
    ('LI-Docker', ['master']),
    ('LI-Api-Carrinho', ['development', 'staging', 'production']),
    ('LI-Api-Catalogo', ['development', 'staging', 'production']),
    ('LI-Api-Envio', ['development', 'staging', 'production']),
    ('LI-Api-Faturamento', ['development', 'staging', 'production']),
    ('li-api-integration', ['development', 'staging', 'production']),
    ('LI-Api-Marketplace', ['development', 'staging', 'production']),
    ('LI-Api-Pagador', ['development', 'staging', 'production']),
    ('LI-Api-Pedido', ['development', 'staging', 'production']),
    ('LI-Api-Plataforma', ['development', 'staging', 'production']),
    ('LI-Api-V2', ['development', 'staging', 'production']),
    ('LI-AppApi', ['development', 'staging', 'production']),
    ('LI-AppConciliacao', ['staging', 'production']),
    ('LI-AppLoja', ['development', 'staging', 'production']),
    ('LI-AppPainel', ['development', 'staging', 'production']),
    ('LI-Worker', ['development', 'staging', 'production']),
    ('li-api-pagamento', ['beta', 'master']),
    ('li-worker-pagamento', ['beta', 'master']),
    ('li-worker-integration', ['development', 'staging', 'production']),
    ('LI-Repo', ['master']),
    ('LI-ApiClient', ['master']),
    ('LI-Common', ['master']),
    ('LI-Api-Flask', ['master']),
    ('Li-Worker-Importacao', ['production', 'staging']),
    ('LI-AWS-Deploy', ['master', 'develop'])
]

MINIFY_BEFORE = [
    'LI-AppLoja'
]

SYNC_S3 = [
    'LI-AppLoja',
    'LI-AppPainel'
]


def get_config_data(filename="li-config", start_over=False):
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
        "datadog_app_key": None,
        "docker_compose_path": None
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
        elif not os.path.exists(os.environ.get('LI_PROJECT_PATH')):
            ret = False

    if ret and not start_over:
        return config
    else:
        path_message = None
        print("\n>> Configuração")
        print("***************")
        if start_over:
            resp = confirma("Deseja configurar as chaves")
        else:
            resp = "S"
        if resp == "S":
            with open(filepath, 'w') as file:
                for key in config:
                    if key == "docker_compose_path" and not config.get(key):
                        continue
                    if config.get(key):
                        ask = "Informe {} [{}]: ".format(key.upper(), config.get(key))
                    else:
                        ask = "Informe {}: ".format(key.upper())

                    resposta_ok = False
                    while not resposta_ok:
                        try:
                            value = raw_input(ask)
                            if value:
                                config[key] = value
                                file.write("{}={}\n".format(key.upper(), value))
                                resposta_ok = True
                            elif config[key]:
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("\nOperação interrompida")
                            return False
                        except:
                            pass
            # Grava arquivo de credenciais da Amazon
            aws_folder = os.path.join(basepath, ".aws")
            if not os.path.exists(aws_folder):
                os.makedirs(aws_folder)
            with open(os.path.join(aws_folder, "config"), 'w') as file:
                file.write("[config]\n")
                file.write('region = {}\n'.format(config['aws_region']))

            with open(os.path.join(aws_folder, "credentials"), 'w') as file:
                file.write('[default]\n')
                file.write('aws_access_key_id = {}\n'.format(config['aws_key']))
                file.write(
                    'aws_secret_access_key = {}\n'.format(
                        config['aws_secret']))

            # Grava no bashrc a variavel LI_PROJECT_PATH
            profile_path = os.path.join(basepath, '.bash_profile')
            project_path = config['project_path']
            bashrc_path = os.path.join(basepath, '.bashrc')
            if os.path.exists(profile_path):
                try:
                    if 'LI_PROJECT_PATH' not in open(profile_path).read():
                        run_command(
                            title=None, command_list=[
                                {
                                    'command': "echo export LI_PROJECT_PATH='{}' >> {}".format(
                                        project_path, profile_path), 'run_stdout': False}, {
                                    'command': "export LI_PROJECT_PATH='{}'".format(
                                        project_path), 'run_stdout': False}], )
                except:
                    path_message = "Certifique que o LI_PROJECT_PATH='{}'\nesteja no seu arquivo .profile".format(project_path)

            if os.path.exists(bashrc_path):
                try:
                    if 'LI_PROJECT_PATH' not in open(bashrc_path).read():
                        run_command(
                            title=None,
                            command_list=[
                                {
                                    'command': "echo LI_PROJECT_PATH='{}' >> {}".format(
                                        project_path,
                                        bashrc_path),
                                    'run_stdout': False}])
                except:
                    path_message = "Certifique que o LI_PROJECT_PATH='{}'\nesteja no seu arquivo .bashrc".format(project_path)

        # Clona os repositorios LI
        resp = confirma("\nDeseja clonar os Repositorios")
        if resp == "S":
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            run_command(
                title="Clonando Repositorios",
                command_list=[
                    {
                        'command': "git config --global credential.helper 'cache --timeout=3600'",
                        'run_stdout': False}])
            for app, branch_list in APPLICATIONS:
                if os.path.exists(os.path.join(project_path, app)):
                    continue
                first_branch = True
                for branch in branch_list:
                    github_url = "https://github.com/lojaintegrada/{}.git".format(
                        app.lower())
                    if first_branch:
                        run_command(
                            title=None,
                            command_list=[
                                {
                                    'command': 'git clone -b {branch} {url} "{dir}"'.format(
                                        branch=branch,
                                        url=github_url,
                                        dir=os.path.join(project_path, app)
                                    ),
                                    'run_stdout': False
                                }
                            ]
                        )
                        first_branch = False
                    else:
                        os.chdir(os.path.join(project_path, app))
                        run_command(
                            title=None,
                            command_list=[
                                {
                                    'command': 'git checkout -b {branch} remotes/origin/{branch}'.format(
                                        branch=branch
                                    ),
                                    'run_stdout': False
                                }
                            ]
                        )

        # Confirma o caminho do docker-compose.yml
        if not config.get('docker_compose_path'):
            ret = run_command(
                title="Localizando arquivo docker-compose.yml",
                get_stdout=True,
                command_list=[
                    {
                        'command': "locate docker-compose.yml",
                        'run_stdout': False
                    }
                ]
            )
            if ret:
                paths_found = ret.split('\n')
                if paths_found[-1] == '':
                    paths_found.pop(-1)
                if len(paths_found) == 1:
                    config['docker_compose_path'] = paths_found[
                        0].replace('docker-compose.yml', '')
                elif paths_found:
                    print(
                        u"Informe a localização do arquivo 'docker-compose.yml' da Loja Integrada")
                    print(u"(A localização padrão é: '{}/LI-Docker')\n".format(
                        project_path
                    ))
                    print("Os caminhos encontrados foram:")
                    for num, path in enumerate(paths_found):
                        print("{}. {}".format(num + 1, path))
                    resposta_ok = False
                    print("\n")
                    while not resposta_ok:
                        try:
                            rep = raw_input(
                                "Selecione o caminho: (1-{}): ".format(num + 1))
                            if rep and int(rep) in xrange(1, num + 1):
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("Operação interrompida\n")
                            return False
                        except:
                            pass
                    config['docker_compose_path'] = paths_found[
                        int(rep) - 1].replace('docker-compose.yml', '')
            else:
                resposta_ok = False
                while not resposta_ok:
                    try:
                        rep = raw_input(
                            "Informe o caminho do arquivo docker-compose.yml: ")
                        if os.path.exists(os.path.join(rep,"docker-compose.yml")):
                            resposta_ok = True
                            config['docker_compose_path'] = rep
                    except KeyboardInterrupt:
                        print("Operação interrompida\n")
                        return False
                    except:
                        pass

            if config.get('docker_compose_path'):
                print('Arquivo encontrado!')
                with open(filepath, 'a') as file:
                    file.write(
                        "{}={}\n".format(
                            "DOCKER_COMPOSE_PATH",
                            config.get('docker_compose_path')
                        ))

    print("\n\n\nConfiguração concluída.")
    print("Para trabalhar com os repositórios certifique-se que:")
    print("* O docker e o docker-compose estejam instalados.")
    if platform.system() == "Windows":
        print("* (Windows) A variável de ambiente 'LI_PROJECT_PATH' esteja configurada.")
        print("* (Windows) Rode o comando 'aws configure'")
    elif path_message:
        print(path_message)
    print("* O comando 'aws configure' tenha sido rodado no repositório, antes do deploy.")
    print("* O comando 'eb init' tenha sido rodado no repositório, antes do deploy.")
    return False
