# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import yaml
import os
import re
from li_tabulate import tabulate
from git import Repo
from tools.config import get_config_data
from tools.utils import run_command, bcolors, progress_bar
from tools.settings import DOCKER_PATH_VAR, LIBRARIES


def show_list(libs=[]):
    data = get_config_data()
    if not data:
        return False

    dc_path = os.path.join(
        data['docker_compose_path'],
        'docker-compose.yml'
    )

    with open(dc_path, 'r') as file:
        dc_data = yaml.load(file)

    print("\n\033[93m>> Lendo Aplicações Docker")
    print("**************************\033[0m\n")

    services_list = dc_data['services']

    table_data = []
    total = len(services_list)
    i = 0
    blank = max([
        len(obj)
        for obj in services_list
    ])
    for service in sorted(services_list):
        # Barra de progresso
        i += 1
        progress_bar(i, total, suffix=service.ljust(blank))
        # 1. Checa se o container está rodando
        docker_ret = run_command(
            command_list=[
                {
                    'command': "docker ps | grep {service}".format(
                        service=service),
                    'run_stdout': False
                }
            ],
            get_stdout=True,
            title=False
        )
        if docker_ret:
            container = docker_ret[:12]
        else:
            container = None

        if container:
            rodando = "{}SIM{}".format(bcolors.OKGREEN, bcolors.ENDC)
        else:
            rodando = "{}NÃO{}".format(bcolors.FAIL, bcolors.ENDC)

        # 2. Checa a branch
        try:
            caminho_dict = services_list.get(service)
            path = caminho_dict.get('build').get('context')
            caminho_path = os.path.join(
                data['project_path'],
                *path.split("/")[1:]
            )
            repo = Repo(caminho_path)
            branch = repo.active_branch.name
        except:
            branch = "--"
            caminho_path = None

        # 3. Checa status do Git
        if branch != "--":
            os.chdir(caminho_path)
            status_ret = run_command(
                command_list=[
                    {
                        'command': 'git status -bs --porcelain',
                        'run_stdout': False
                    }
                ],
                get_stdout=True,
                title=None
            )
            if status_ret.count('\n') > 1 or "[" in status_ret:
                branch = "{}{}{}".format(bcolors.WARNING, branch, bcolors.ENDC)
                ahead = re.search("ahead (\d+)", status_ret)
                behind = re.search("behind (\d+)", status_ret)
                if ahead or behind:
                    branch = "{} {}[{}{}{}]{}".format(
                        branch,
                        bcolors.WARNING,
                        "{}+{}{}".format(bcolors.OKBLUE, ahead.group(1), bcolors.ENDC) if ahead else "",
                        "{}-{}{}".format(bcolors.FAIL, behind.group(1), bcolors.ENDC) if behind else "",
                        bcolors.WARNING,
                        bcolors.ENDC
                    )

        # 4. Checa versão das livrarias
        lib_list = []
        pip_ret = None
        if caminho_path:
            for lib in LIBRARIES + libs:
                if container:
                    pip_ret = run_command(
                        command_list=[
                            {
                                'command': 'docker exec -ti {container} pip freeze | grep -i {library}== | tail -1'.format(
                                    container=container,
                                    library=lib),
                                'run_stdout': False}],
                        get_stdout=True,
                        title=None)
                elif branch != "--":
                    try:
                        pip_ret = run_command(
                            command_list=[
                                {
                                    'command': 'cd {path} && docker-compose run {service} pip freeze | grep -i {library}== | tail -1'.format(
                                        path=data['docker_compose_path'],
                                        service=service,
                                        library=lib
                                    ),
                                    'run_stdout':False
                                }
                            ],
                            get_stdout=True,
                            title=None
                        )
                    except:
                        pip_ret = None
                if pip_ret:
                    lib_list.append(pip_ret.split("==")[1])
                else:
                    lib_list.append("--" if "SIM" in rodando else "")

        # 5. Pega a Porta
        try:
            porta = dc_data['services'][service]['ports'][0].split(":")[0]
        except:
            porta = "--"
            
        table_data.append([service, branch, rodando, porta] + lib_list)

    # Exclui containers extra
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n\033[93m>> Listar Aplicações Docker")
    print("**************************\033[0m\n")
    print(tabulate(
        table_data,
        headers=["Aplicação", "Branch", "Rodando", "Porta"] + LIBRARIES + libs
    )
    )
