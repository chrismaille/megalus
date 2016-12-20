# -*- coding: utf-8 -*-
import os
from tools import settings
from tools.config import get_config_data, run_update
from tools.messages import notify
from tools.utils import run_command, get_app, confirma


def run_runapp(application, action, opt=None, arg=None):
    data = get_config_data()
    if not data:
        return False

    name = ""
    container_id = None
    if application:
        container_id, name = get_app(
            application=application,
            title="Build/Run da Aplicacao",
            data=data,
            stop=False if action == "exec" else True
        )
        if not container_id:
            return False

    if action == 'build' and settings.USE_ECR:
        run_command(
            get_stdout=False,
            command_list=[
                {
                    'command': "aws ecr get-login --region {region}".format(region=data['aws_region']),
                    'run_stdout': True
                }
            ]
        )

    if action == "exec":
        print("\n\033[1m\033[94mRodando comando '{}' em '{}'\033[0m".format(
            " ".join(arg), name))
        os.system(
            "docker {cmd} -ti {app}{arg}".format(
                cmd=action,
                app=container_id,
                arg=" {}".format(" ".join(arg)) if arg else "")
        )
    else:
        run_command(
            get_stdout=False,
            title="Rodar Comando Docker: {}".format(action.upper()),
            command_list=[
                {
                    'command': "cd {} && docker-compose stop".format(
                        data['docker_compose_path']),
                    'run_stdout': False
                }
            ]
        )
        os.system(
            "cd {folder} && docker-compose {cmd} {opt} {app}".format(
                folder=data['docker_compose_path'],
                cmd=action,
                app=name,
                opt=opt if opt else "")
        )
    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    if action == "run":
        os.system(
            "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
        )
    if action == "build":
        notify(msg=u"A operação de Build foi concluída")


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
                'command': "cd {} && docker-compose stop {}".format(data['docker_compose_path'], name),
                'run_stdout': False
            },
        ]
    )
    os.system(
        'cd {} && docker-compose run --service-ports {}\n'.format(data['docker_compose_path'], name)
    )

    print("Reiniciando o container...")
    run_command(command_list=[{'command': "cd {} && docker-compose up -d {}".format(
        data['docker_compose_path'], name), 'run_stdout': False}, ])

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    return False


def run_telnet(application, port):
    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Rodar Telnet",
        data=data
    )

    if not container_id:
        return False

    os.chdir(data['project_path'])
    os.system(
        'docker exec -ti {} telnet 127.0.0.1 {}'.format(
            container_id, port
        )
    )

    return False


def run_bash(application):

    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Rodar Bash",
        data=data
    )

    if not container_id:
        return False

    os.chdir(data['project_path'])
    os.system(
        'docker exec -ti {} /bin/bash'.format(
            container_id
        )
    )

    return False


def run_test(application, test_type, rds):
    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Rodar Teste",
        data=data
    )

    if not container_id:
        return False

    os.chdir(data['project_path'])
    os.system('cls' if os.name == 'nt' else 'clear')
    # Parar o container
    print("Rodar Testes - {}".format(name))
    print("Reiniciando container...")
    run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && docker-compose stop {}".format(data['docker_compose_path'], name),
                'run_stdout': False
            },
        ]
    )

    # Rodar o container com o endereco do
    # Banco de dados selecionado
    if rds:
        host = settings.STAGE_DB
        port = settings.STAGE_PORT
    else:
        host = settings.LOCAL_DB
        port = settings.LOCAL_PORT

    new_container_id = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && docker-compose run -d -e DATABASE_HOST={} -e DATABASE_PORT={} {}".format(
                    data['docker_compose_path'],
                    host,
                    port,
                    name),
                'run_stdout': False},
        ])
    new_container_id = new_container_id.replace("\n", "")
    # os.system("docker-compose run -d -e DATABASE_HOST={} {}".format(host, name))

    database_path = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "docker exec -ti {} printenv | grep DATABASE_HOST".format(new_container_id),
                'run_stdout': False}])
    print("\033[93m\n************************************")
    print("Rodando testes com: {}".format(
        "Django" if test_type == "django" else "Unittest"))
    print("Usando banco de dados: {}".format(
        database_path.replace("\n", "").split("=")[1])
    )
    print("Usando a Porta: {}".format(port))
    print("************************************\n\033[0m")
    if test_type == "django":
        command = "python /opt/app/manage.py test"
    else:
        command = "python -m unittest discover -v -s /opt/app"

    os.system(
        'docker exec -ti {} {}'.format(
            new_container_id, command
        )
    )

    print("Reiniciando container...")
    os.system("docker stop {}".format(new_container_id))
    os.system(
        "cd {} && docker-compose run -d {}".format(data['docker_compose_path'], name))

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    notify(title="LI-Tools", msg="Teste Unitário em {} finalizado.".format(name))
    return False


def rebuild_docker(no_confirm):
    data = get_config_data()
    if not data:
        return False

    if no_confirm:
        resp = "S"
    else:
        resp = confirma(
            u"Este comando exclui todas as imagens\n"
            u"e containers existentes na máquina,\n"
            u"e inicia um novo Update/Build.\n"
            u"\n\033[91mCertifique-se que você tenha um backup\n"
            u"do banco de dados antes de rodar esse comando.\033[0m\n\n"
            u"Deseja continuar")

    if resp == "S":
        # Parar containers
        run_command(
            get_stdout=False,
            title=None,
            command_list=[
                {
                    'command': "cd {} && docker-compose stop".format(
                        data['docker_compose_path']),
                    'run_stdout': False
                }
            ]
        )
        # docker rm $(docker ps -a -q)
        run_command(
            title="Excluir Containers do Docker",
            command_list=[
                {
                    'command': 'docker rm $(docker ps -a -q)',
                    'run_stdout': False
                }
            ]
        )
        # docker rmi $(docker images -q)
        run_command(
            title="Excluir Imagens do Docker",
            command_list=[
                {
                    'command': 'docker rmi $(docker images -q)',
                    'run_stdout': False
                }
            ]
        )

        # Roda Update
        run_update(no_confirm=True, stable=True, staging=False)

        # Roda Build
        run_runapp(application=None, action="build")

        # Finaliza
        notify(msg="Rebuild dos Containers finalizado")
        os.system('cls' if os.name == 'nt' else 'clear')
        print(u"O Rebuild foi concluído.")
        print(u"Antes de iniciar os containers, digite o comando:")
        print(u"'cd {} && docker-compose up service.postgres.local'".format(data['docker_compose_path']))
        print(u"para iniciar o Banco de dados pela primeira vez.")
        print(u"Em seguida use o comando 'meg run'.")
        return True
