import os
from tools import settings
from tools.config import get_config_data
from tools.messages import notify
from tools.utils import run_command, get_app


def run_build(application):
    data = get_config_data()
    if not data:
        return False

    if application == "base" or not application:
        path = os.path.join(
            data['project_path'],
            settings.DOCKER_BASE_IMAGE_REPO
        )
        ret = run_command(
            title="Gera Imagem Base do Docker",
            command_list=[
                {
                    'command': "cd {} && docker build -t megbase:dev .".format(
                        path
                    ),
                    'run_stdout': False
                },
            ]
        )
        if not ret:
            return False

        if application == "base":
            notify(msg="A operação de Build foi concluída")
            return True

    name = ""
    container_id = None
    if application:
        container_id, name = get_app(
            application=application,
            title="Build da Aplicacao",
            data=data,
            stop=True
        )
        if not container_id:
            return False

    if settings.USE_ECR:
        run_command(
            get_stdout=False,
            command_list=[
                {
                    'command': "aws ecr get-login"
                    " --region {region}".format(
                        region=data['aws_region']),
                    'run_stdout': True
                }
            ]
        )

    run_command(
        get_stdout=False,
        title="Rodar Comando Docker: BUILD",
        command_list=[
            {
                'command': "cd {} && docker-compose stop".format(
                    data['docker_compose_path']),
                'run_stdout': False
            }
        ]
    )
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
    os.system(
        "cd {folder} && docker-compose build {app}".format(
            folder=data['docker_compose_path'],
            app=name)
    )
    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    notify(msg="A operação de Build foi concluída")
