import os
import time
from colorama import Fore, Style
from megalus.commands.build import run_build
from megalus.core.messages import notify
from megalus.core.utils import run_command, get_app, confirma, print_title
from megalus.projects.config import get_config_data, run_update
from megalus.projects.setup import settings


def _stop_all(data):
    run_command(
        get_stdout=False,
        title=None,
        command_list=[
            {
                'command': "cd {} && docker-compose stop".format(
                    data['docker_compose_path']),
                'run_stdout': False}])
    ret_docker = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': 'docker ps -q',
                'run_stdout': False
            }
        ]
    )
    if ret_docker:
        run_command(
            get_stdout=False,
            command_list=[
                {
                    'command': 'docker stop $(docker ps -q)',
                    'run_stdout': False
                }
            ]
        )


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

    if action == "exec":
        print(Fore.YELLOW + ("Rodando comando '{}' em '{}'".format(
            " ".join(arg), name)) + Style.RESET_ALL)
        os.system(
            "docker {cmd} -ti {app}{arg}".format(
                cmd=action,
                app=container_id,
                arg=" {}".format(" ".join(arg)) if arg else "")
        )
    else:
        # Parar os containers
        _stop_all(data)

        # Rodar o comando
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
                'command': "cd {} && "
                "docker-compose stop {}".format(
                    data['docker_compose_path'], name),
                'run_stdout': False
            },
        ]
    )
    os.system(
        'cd {} && docker-compose run '
        '--service-ports {}\n'.format(
            data['docker_compose_path'], name)
    )

    print("Reiniciando o container...")
    run_command(
        command_list=[
            {'command': "cd {} && "
             "docker-compose up -d {}".format(
                 data['docker_compose_path'], name),
             'run_stdout': False}
        ]
    )

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


def run_test(application, using, rds, verbose):
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

    finalmsg = "Teste não efetuado."
    # Rodar o container com o endereco do
    # Banco de dados selecionado
    dbdata = [
        obj
        for obj in settings.LOCAL_DBS
        if obj.get('admin') == name
    ]
    if rds:
        host = dbdata[0].get('stage_name', None)
        port = dbdata[0].get('stage_port', None)
    else:
        host = dbdata[0].get('local_name', None)
        port = dbdata[0].get('local_port', None)

    if not host or not port:
        print(
            Fore.RED +
            "ERRO: Nome ou Porta do Banco não encontrado." +
            Style.RESET_ALL)
        return False

    os.chdir(data['project_path'])
    # Parar o container
    print(("Rodar Testes - {}".format(name)))
    print("Reiniciando container...")
    run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && "
                "docker-compose stop {}".format(
                    data['docker_compose_path'], name),
                'run_stdout': False
            },
        ]
    )

    # Encontrar o programa
    test_app = using if using else data['use_for_tests']
    if not using:
        check_list = [test_app] + settings.TEST_PRIORITY
        ret_pip = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "cd {} && "
                    "docker-compose run {} pip freeze".format(
                        data['docker_compose_path'],
                        name),
                    'run_stdout': False}])
        for test in check_list:
            if "{}==".format(test) in ret_pip:
                test_app = test
                break

    # Checa se o coverage está instalado
    dependencies_found = True
    if 'coverage' not in ret_pip:
        dependencies_found = False
    if 'pydocstyle' not in ret_pip:
        dependencies_found = False
    if 'pycodestyle' not in ret_pip:
        dependencies_found = False

    # Rodar novo container
    # Para Unittest, Django, Pytest e Nose rodar via Docker-Compose
    new_container_id = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && docker-compose "
                "run -d -e DATABASE_HOST={} -e DATABASE_PORT={} {}".format(
                    data['docker_compose_path'],
                    host,
                    port,
                    name),
                'run_stdout': False},
        ])

    if new_container_id and dependencies_found:

        new_container_id = new_container_id.replace("\n", "")

        database_path = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "docker exec -ti {} printenv"
                    " | grep DATABASE_HOST".format(
                        new_container_id),
                    'run_stdout': False
                }
            ]
        )
        os.system('cls' if os.name == 'nt' else 'clear')
        print(
            Fore.LIGHTYELLOW_EX +
            "**********************************************")
        print("Rodando testes com: {}".format(test_app.upper()))
        print("Usando banco de dados: {}".format(
            database_path.replace("\n", "").split("=")[1])
        )
        print(
            "**********************************************\n" +
            Style.RESET_ALL)

        if test_app == "django":
            command = "coverage run --source='.' manage.py test{}".format(
                ' -v2' if verbose else ""
            )
        elif test_app == "nose":
            command = "nosetests --with-coverage --cover-package=app"
        elif test_app == "pytest":
            command = "coverage run pytest"
        else:
            command = "coverage run -m unittest discover -v -s /opt/app"

        os.system(
            'docker exec -ti {} {}'.format(
                new_container_id, command
            )
        )
        # Coverage
        print_title("Coverage Reports")
        os.system(
            "docker exec -ti {} coverage report -m --skip-covered".format(new_container_id)
        )
        print_title("Coverage Result")
        coverage_result = run_command(
            get_stdout=False,
            command_list=[
                {
                    "command": "docker exec -ti {} ./config/check_cover.sh".format(new_container_id),
                    "run_stdout": False
                }
            ]
        )
        # PEP8
        pep8_result = run_command(
            title="PEP8 Check",
            get_stdout=False,
            command_list=[
                {
                    "command": "docker exec -ti {} pycodestyle {}--exclude=manage.py,settings.py,venv,migrations,frontend .".format(
                        new_container_id,
                        "--show-source " if verbose else ""),
                    "run_stdout": False}])
        print(
            "\nResult: {}".format(
                Fore.GREEN +
                "OK" +
                Style.RESET_ALL if pep8_result else Fore.RED +
                "FAIL" +
                Style.RESET_ALL))
        # PEP257
        pep257_result = run_command(
            title="PEP257 Check",
            get_stdout=False,
            command_list=[
                {
                    "command": "docker exec -ti {} pydocstyle --match-dir='[^venv|^migrations|^frontend].*' --match='(?!__|manage).*\.py'".format(
                        new_container_id
                    ),
                    "run_stdout": False
                }
            ]
        )
        print(
            "\nResult: {}\n".format(
                Fore.GREEN +
                "OK" +
                Style.RESET_ALL if pep257_result else Fore.RED +
                "FAIL" +
                Style.RESET_ALL))

        if coverage_result and pep8_result and pep257_result:
            finalmsg = "Todos os Testes passaram com sucesso."
            print(Fore.GREEN + "\n{}".format(finalmsg) + Style.RESET_ALL)
        else:
            finalmsg = "ERROS ENCONTRADOS DURANTE OS TESTES. Verifique os logs."
            print(Fore.RED + "\n{}".format(finalmsg) + Style.RESET_ALL)

    elif not dependencies_found:
        print(
            Fore.RED +
            "Erro: Devem estar instalados no container: coverage, pydocstyle e pycodestyle" +
            Style.RESET_ALL)
    else:
        print(Fore.RED + "ERRO: Nenhum container encontrado" +
              Style.RESET_ALL)

    print("\n------------\nReiniciando container...")
    os.system("docker stop {}".format(new_container_id))
    os.system(
        "cd {} && docker-compose "
        "up -d {}".format(
            data['docker_compose_path'], name))

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    notify(msg="Teste Unitário em {}: {}".format(name, finalmsg))
    return False


def rebuild_docker(no_confirm):
    data = get_config_data()
    if not data:
        return False

    if no_confirm:
        resp = True
    else:
        resp = confirma(
            "Este comando exclui todas as imagens\n"
            "e containers existentes na máquina,\n"
            "e inicia um novo Update/Build.\n"
            "\n\033[91mCertifique-se que você tenha um backup\n"
            "do banco de dados antes de rodar esse comando e\n"
            "que todas as alterações importantes"
            " estejam commitadas.\033[0m\n\n"
            "Deseja continuar")

    if resp:
        # Parar containers
        _stop_all(data)

        # Excluir containers e imagens
        run_command(
            title="Excluir Containers do Docker",
            command_list=[
                {
                    'command': 'docker rm $(docker ps -a -q)',
                    'run_stdout': False
                }
            ]
        )
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
        run_build(application=None)

        # Finaliza
        notify(msg="Rebuild dos Containers finalizado")
        os.system('cls' if os.name == 'nt' else 'clear')
        print("O Rebuild foi concluído.")
        print("Antes de iniciar os containers, digite o(s) comando(s):")
        for dbdata in settings.LOCAL_DBS:
            print(
                "'cd {} && docker-compose up "
                "{}'".format(
                    data['docker_compose_path'],
                    dbdata['local_name']))
        print("para iniciar o Banco de dados pela primeira vez.")
        print("Em seguida use o comando 'meg run'.")
        return True


def reset_db(application):
    data = get_config_data()
    if not data:
        return False

    # Selecionar Banco
    container_id, name = get_app(
        application=application,
        title="Redefinir Banco de Dados",
        data=data
    )

    if not name:
        return False

    dbdata = [
        obj
        for obj in settings.LOCAL_DBS
        if obj.get('admin') == name
    ]

    if not dbdata:
        print(
            Fore.RED +
            "ERRO: Banco de Dados não encontrado para a Aplicação." +
            Style.RESET_ALL)
        return False

    local_name = dbdata[0].get('local_name', None)
    db_name = dbdata[0].get('name', None)
    db_user = dbdata[0].get('user', None)

    if not local_name or not db_name or not db_user:
        print(
            Fore.RED +
            "ERRO: Configuração do Banco de Dados não encontrado." +
            Style.RESET_ALL)
        return False

    # Confirmar
    warning_text = Fore.RED + "Este comando exclui o banco de dados '{}'\n".format(
        local_name.upper()) + Style.RESET_ALL
    resp = confirma(
        warning_text + "\nDeseja continuar"
    )
    if resp:
        # Parar os containers
        print("\n" + Fore.YELLOW + "Parando containers" + Style.RESET_ALL)
        _stop_all(data)

        # Iniciar o Postgres
        print(
            "\n" +
            Fore.YELLOW +
            "Iniciando {}".format(local_name) +
            Style.RESET_ALL)
        new_container_id = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "cd {} && docker-compose "
                    "run -d {}".format(
                        data['docker_compose_path'],
                        local_name),
                    'run_stdout': False
                },
            ]
        )
        new_container_id = new_container_id.replace("\n", "")

        # Apagar o banco antigo
        cmd = "dropdb -U {user} {database}".format(
            user=db_user,
            database=db_name
        )
        print(
            Fore.YELLOW +
            "\nRodando comando: {}".format(cmd) +
            Style.RESET_ALL)
        os.system(
            "docker exec -ti {container} {com}".format(
                folder=data['docker_compose_path'],
                container=new_container_id,
                com=cmd)
        )
        # Criar o banco novo
        cmd = "createdb -U {user} -O {user} {database}".format(
            user=db_user,
            database=db_name
        )
        print(
            Fore.YELLOW +
            "\nRodando comando: {}".format(cmd) +
            Style.RESET_ALL)
        os.system(
            "docker exec -ti {container} {com}".format(
                folder=data['docker_compose_path'],
                container=new_container_id,
                com=cmd)
        )
        # Reiniciar os containers
        print(
            Fore.YELLOW +
            "\nReiniciando Containers".format(cmd) +
            Style.RESET_ALL)
        _stop_all(data)
        os.system(
            "cd {folder} && docker-compose up -d".format(
                folder=data['docker_compose_path']
            )
        )
        # Rodar makemigrations
        cmd = "python manage.py makemigrations"
        print(
            Fore.YELLOW +
            "\nRodando comando: {}".format(cmd) +
            Style.RESET_ALL)
        os.system(
            "cd {folder} && docker-compose {cmd} {app} {com}".format(
                folder=data['docker_compose_path'],
                cmd="run",
                app=name,
                com=cmd)
        )
        # Rodar migrate
        cmd = "python manage.py migrate"
        print(
            Fore.YELLOW +
            "\nRodando comando: {}".format(cmd) +
            Style.RESET_ALL)
        os.system(
            "cd {folder} && docker-compose {cmd} {app} {com}".format(
                folder=data['docker_compose_path'],
                cmd="run",
                app=name,
                com=cmd)
        )
        # Rodar createdata
        cmd = "python manage.py createdata"
        print(
            Fore.YELLOW +
            "\nRodando comando: {}".format(cmd) +
            Style.RESET_ALL)
        os.system(
            "cd {folder} && docker-compose {cmd} {app} {com}".format(
                folder=data['docker_compose_path'],
                cmd="run",
                app=name,
                com=cmd)
        )
        # Aguardar alguns segundos para as tarefas assincronas
        time.sleep(2)
        # Parar os containers
        print(Fore.YELLOW + "\nParando containers" + Style.RESET_ALL)
        _stop_all(data)

        # Excluir containers extra
        os.system(
            "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
        )

        return True
