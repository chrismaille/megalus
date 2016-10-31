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
    print("Subindo container...")
    run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "docker-compose stop {}".format(name),
                'run_stdout': False
            },
        ]
    )

    # Rodar o container com o endereco do
    # Banco de dados selecionado
    if rds:
        host = "li-db-staging.ciksobkqlidb.us-east-1.rds.amazonaws.com"
        port = "5432"
    else:
        host = "postgres_host"
        port = "5432"

    new_container_id = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "docker-compose run -d -e DATABASE_HOST={} -e DATABASE_PORT={} {}".format(host, port, name),
                'run_stdout': False
            },
        ]
    )
    new_container_id = new_container_id.replace("\n", "")
    # os.system("docker-compose run -d -e DATABASE_HOST={} {}".format(host, name))

    database_path = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "docker exec -ti {} printenv | grep DATABASE_HOST".format(new_container_id),
                'run_stdout': False}])
    print("\nRodando testes em: {}".format(
        "Django" if test_type == "django" else "Unittest"))
    print("Usando banco de dados: {}:{}".format(
        database_path.replace("\n", "").split("=")[1],
        port)
    )
    if test_type == "django":
        command = "python /opt/app/manage.py test"
    else:
        command = "python -m unittest discover -v -s /opt/app"

    os.system(
        'docker exec -ti {} {}'.format(
            new_container_id, command
        )
    )

    print("Parando container...")
    os.system("docker stop {}".format(new_container_id))
    # os.system("docker-compose run -d {}".format(name))

    return False
