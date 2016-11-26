# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
import platform
from os.path import expanduser
from tools.utils import run_command, confirma
from tools import settings
from git import Repo


def get_config_data(filename=settings.CONFIG_FILE, start_over=False):
    # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = settings.CONFIG_DICT
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
                if "=" in line:
                    key = line.split("=")[0].lower()
                    value = line.split("=")[1].rstrip()
                    config[key] = value

        for key in config:
            if not config.get(key):
                ret = False

        if not os.environ.get(settings.ENV_NAME):
            ret = False
        elif not os.path.exists(os.environ.get(settings.ENV_NAME)):
            ret = False

    if ret and not start_over:
        return config
    else:
        path_message = None
        print("\n\033[93m>> Configuração")
        print("***************\033[0m")
        project_path = config['project_path']
        config_list = [
            '.bash_profile',
            '.bashrc',
            '.zshrc',
            '.profile'
        ]
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
                        ask = "Informe {} [{}]: ".format(
                            key.upper(), config.get(key))
                    else:
                        ask = "Informe {}: ".format(key.upper())

                    resposta_ok = False
                    while not resposta_ok:
                        try:
                            value = str(raw_input(ask))
                            if not value and config[key]:
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), config[key]))
                                resposta_ok = True
                            if value:
                                config[key] = value
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), value))
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("\nOperação interrompida")
                            return False
                        except:
                            print('erro')
                            pass
            # Grava arquivo de credenciais da Amazon
            if settings.USE_AWS:
                aws_folder = os.path.join(basepath, ".aws")
                if not os.path.exists(aws_folder):
                    os.makedirs(aws_folder)
                with open(os.path.join(aws_folder, "config"), 'w') as file:
                    file.write("[config]\n")
                    file.write('region = {}\n'.format(config['aws_region']))

                with open(os.path.join(aws_folder, "credentials"), 'w') as file:
                    file.write('[default]\n')
                    file.write(
                        'aws_access_key_id = {}\n'.format(
                            config['aws_key']))
                    file.write(
                        'aws_secret_access_key = {}\n'.format(
                            config['aws_secret']))

        # Grava a variavel de ambiente nos arquivos de configuracao
        print("\n")
        one_file_ok = False
        for filename in config_list:
            export_found = False
            try:
                profile_path = os.path.join(basepath, filename)
                with open(profile_path) as file:
                    for line in file:
                        if settings.ENV_NAME in line:
                            export_found = True
                            one_file_ok = True
                    if not export_found:
                        ret = run_command(
                            title=None,
                            command_list=[
                                {
                                    'command': "echo export {}='{}' >> {}".format(
                                        settings.ENV_NAME,
                                        project_path,
                                        profile_path),
                                    'run_stdout': False}])
                        if ret:
                            print(
                                "Adicionando {} no arquivo {}".format(
                                    settings.ENV_NAME, filename))
                            export_found = True
                            one_file_ok = True
                    else:
                        export_found = True
                        one_file_ok = True
            except:
                pass
            finally:
                run_command(
                    title=None,
                    command_list=[
                        {
                            'command': "export {}='{}'".format(
                                settings.ENV_NAME,
                                project_path),
                            'run_stdout': False
                        }
                    ]
                )
        if not one_file_ok:
            path_message = "Certifique-se que o {} esteja no seu arquivo .profile, .bashrc ou .zshrc correspondente".format(
                settings.ENV_NAME)

        # Clona os repositorios LI
        resp = confirma("\nDeseja clonar os Repositórios")
        if resp == "S":
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            run_command(
                title="Clonando Repositorios",
                command_list=[
                    {
                        'command': "git config --global credential.helper 'cache --timeout=3600'",
                        'run_stdout': False}])

            # Baixa APPLICATIONS
            baixa_repositorios(config)

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
                    print(u"(A localização padrão é: '{}/{}')\n".format(
                        project_path,
                        settings.DOCKER_REPO_NAME
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
                            if rep and int(rep) in xrange(1, num + 2):
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
                        if os.path.exists(
                            os.path.join(
                                rep,
                                "docker-compose.yml")):
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
        print("* (Windows) A variável de ambiente {} esteja configurada.".format(settings.ENV_NAME))
        print("* (Windows) Rode o comando 'aws configure'")
    elif path_message:
        print("* {}".format(path_message))
    print("* O comando 'aws configure' tenha sido rodado no repositório, antes do deploy.")
    print("* O comando 'eb init' tenha sido rodado no repositório, antes do deploy.")
    return False


def run_update():
    data = get_config_data()

    if not data:
        return False

    print("\n\033[1m\033[93m>> Atualizar Repositórios")
    print("****************************\033[0m")

    resp = confirma(
        u"Este comando atualiza todos os Repositórios\n"
        "que estejam nas branchs 'production' ou 'master'.\n"
        "Além disso, baixa novos repositórios que ainda\n"
        "não estejam na pasta do projeto.\n"
        "Deseja continuar")
    if resp == "S":
        # Iterar todos os repositórios
        # Checar em que branch está
        # Se tiver em production ou master, dar o git pull
        for app in settings.APPLICATIONS:
            app_name = app[0]
            app_main_branch = app[1][-1]
            caminho = os.path.join(data['project_path'], app_name)
            if os.path.exists(caminho):
                repo = Repo(
                    os.path.join(data['project_path'], app_name)
                )
                branch = repo.active_branch.name
                if branch == app_main_branch:
                    print("\n\033[1m\033[94mAtualizando '{}'\033[0m".format(app_name))
                    os.chdir(caminho)
                    run_command(
                        title=None,
                        command_list=[
                            {
                                'command': 'git remote update && git fetch && git pull --all',
                                'run_stdout': False
                            }
                        ]
                    )
        # Baixa os repositorios faltantes
        baixa_repositorios(data)


def baixa_repositorios(data):
    for app, branch_list in settings.APPLICATIONS:
        if os.path.exists(os.path.join(data['project_path'], app)):
            continue
        print("\n\033[1m\033[94mBaixando '{}'\033[0m".format(app))
        first_branch = True
        for branch in branch_list:
            github_url = "{}{}.git".format(
                settings.VCS_BASE_URL,
                app.lower())
            if first_branch:
                ret = run_command(
                    title=None,
                    command_list=[
                        {
                            'command': 'git clone -b {branch} {url} "{dir}"'.format(
                                branch=branch,
                                url=github_url,
                                dir=os.path.join(data['project_path'], app)
                            ),
                            'run_stdout': False
                        }
                    ]
                )
                first_branch = False
            else:
                if ret:
                    os.chdir(os.path.join(data['project_path'], app))
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
