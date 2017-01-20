import json
import os
import platform
import re
from colorama import Fore, Style
from git import Repo
from tools import settings
from tools.compress import minifyCSS, minifyJS
from tools.config import get_config_data
from tools.messages import Message, notify
from tools.utils import bcolors, run_command, confirma, print_title


def run_deploy():
    config = get_config_data()

    if not config:
        return False

    # Pega a pasta atual e verifica
    # se é uma pasta valida para deploy
    current_dir = os.getcwd()
    try:
        repo = Repo(current_dir)
        branch = repo.active_branch
    except:
        print(Fore.RED + "Repositório GIT não encontrado.")
        print("O comando deve ser executado na pasta raiz")
        print("do repositório a ser enviado.")
        print("Comando abortado." + Style.RESET_ALL)
        return False
    app_list = [
        app.lower()
        for app, br in settings.APPLICATIONS
    ]
    folder_name = os.path.split(current_dir)[-1]
    if folder_name.lower() not in app_list:
        print(Fore.RED + "Repositório não reconhecido." + Style.RESET_ALL)
        return False

    # Confirma operação
    branch_name = branch.name
    last_commit = repo.head.commit.message
    text_repo = "{}{}{}{}".format(
        bcolors.BOLD,
        bcolors.OKBLUE,
        folder_name,
        bcolors.ENDC
    )
    print("Repositório: {}".format(
        text_repo if platform.system() != "Windows" else folder_name.upper()
    ))
    text_branch = "{}{}{}{}".format(
        bcolors.BOLD,
        bcolors.FAIL if branch_name in [
            'production',
            'master'] else bcolors.WARNING,
        branch_name.upper(),
        bcolors.ENDC)
    print("Branch Atual: {}".format(
        text_branch if platform.system() != "Windows" else branch_name.upper()
    ))
    print("Último Commit:\n{}".format("{}{}{}".format(
        bcolors.WARNING,
        last_commit,
        bcolors.ENDC
    )))

    # Roda EB Status
    eb_status = False
    ret = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "eb status",
                'run_stdout': False
            }
        ]
    )
    if ret:
        m = re.search("Status: (\w+)", ret)
        if m:
            eb_status_name = m.group(1)
            if eb_status_name == "Ready":
                eb_status = True
            print ("\nO Status do ElasticBeanstalk é: {}".format(
                "{}{}{}{}".format(
                    bcolors.BOLD,
                    bcolors.OKGREEN if eb_status else bcolors.FAIL,
                    eb_status_name.upper(),
                    bcolors.ENDC
                )
            ))
        else:
            print (ret)

    if not eb_status:
        return False

    resposta = confirma("Confirma o Deploy")
    if not resposta:
        return False

    # Se existir a pasta frontend
    # rodar o build do webpack
    wbpath = os.path.join(current_dir, 'frontend')
    if os.path.exists(wbpath):
        ret = run_command(
            get_stdout=False,
            title="Gerando Build do Webpack",
            command_list=[
                {
                    'command': 'cd {} && ./node_modules/.bin/webpack'
                    ' --config webpack.config.deploy.js'.format(wbpath),
                    'run_stdout': False
                }
            ]
        )
        if not ret:
            return False

    # Ações específicas do App
    # 1. Minify manual
    if folder_name in settings.MINIFY_BEFORE:
        print_title("Minificando arquivos estáticos")
        ret = minifyCSS(current_dir=current_dir)
        if not ret:
            return False

        ret = minifyJS(current_dir=current_dir)
        if not ret:
            return False

    # 2. Sincronizar estáticos
    if folder_name in settings.SYNC_S3:
        ret = run_command(
            title="Sincronizando arquivos "
            "estáticos no S3/{}".format(branch_name),
            command_list=[
                {
                    'command': settings.S3_SYNC_CMD.format(
                        branch=branch_name),
                    'run_stdout': False}])
        if not ret:
            return False

    # Gera Dockerrun
    app_name = settings.ECR_NAME.get(folder_name, None)
    if not app_name:
        app_name = folder_name.lower()
    json_model = {
        'AWSEBDockerrunVersion': '1',
        'Image': {
            'Name': '{account}.dkr.ecr.{region}'
            '.amazonaws.com/{app}:{branch}'.format(
                account=config['aws_account'],
                app=app_name,
                branch=branch_name,
                region=config['aws_region']),
            'Update': 'true'},
        'Ports': [
            {
                'ContainerPort': '80'
            }
        ],
        "Volumes": [
            {
                "HostDirectory": "/tmp",
                "ContainerDirectory": "/tmp"
            }
        ],
        'Logging': "/var/eb_log"}

    with open("./Dockerrun.aws.json", 'w') as file:
        file.write(json.dumps(json_model, indent=2))

    ret = run_command(
        title="Adiciona Dockerrun",
        command_list=[
            {
                'command': "git add .",
                'run_stdout': False
            },
            {
                'command': "git commit -m \"{}\"".format(last_commit),
                'run_stdout': False
            }
        ]
    )

    # Atualiza VCS
    ret = run_command(
        title="Atualiza {} - {}".format(settings.VCS_NAME, folder_name),
        command_list=[
            {
                'command': "git push origin {}".format(branch.name),
                'run_stdout': False
            }
        ]
    )
    if not ret:
        return False

    # Envia Mensagem Datadog/Slack
    if branch.name in ['production', 'master']:
        message = Message(
            config,
            branch,
            last_commit,
            folder_name,
            action="INICIADO")
        message.send(alert_type="warning")

    # Gerar imagem base do Docker
    dockerbasepath = os.path.join(
        config['project_path'],
        settings.DOCKER_BASE_IMAGE_REPO
    )
    ret = run_command(
        title="Gera Imagem Base do Docker",
        command_list=[
            {
                'command': "aws ecr get-login "
                "--region {region}".format(region=config['aws_region']),
                'run_stdout': True
            },
            {
                'command': "cd {path} && docker build -t {app}:dev .".format(
                    path=dockerbasepath,
                    app=settings.DOCKER_BASE_IMAGE_REPO
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {base}:dev "
                "{account}.dkr.ecr.{region}.amazonaws.com"
                "/{base}:latest".format(
                    base=settings.DOCKER_BASE_IMAGE_REPO,
                    account=config['aws_account'],
                    region=config['aws_region'],
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}."
                "dkr.ecr.{region}.amazonaws.com/{base}:latest".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    base=settings.DOCKER_BASE_IMAGE_REPO
                ),
                'run_stdout': False
            },
        ]
    )
    if not ret:
        return False

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker - {}".format(folder_name),
        command_list=[
            {
                'command': "docker build -f {name} -t {app}:{branch} .".format(
                    name=settings.DOCKERFILE_DEPLOY,
                    app=app_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {app}:{branch} "
                "{account}.dkr.ecr.{region}.amazonaws.com"
                "/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=app_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}."
                "dkr.ecr.{region}.amazonaws.com/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=app_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
        ]
    )
    if not ret:
        return False

    # Rodar EB Deploy
    ret = run_command(
        title="Rodando EB Deploy - {}".format(folder_name),
        command_list=[
            {
                'command': "eb deploy --timeout 60",
                'run_stdout': False
            }
        ]
    )
    if not ret:
        return False

    # Mensagem final
    if branch.name in ['production', 'master']:
        message = Message(
            config,
            branch,
            last_commit,
            folder_name,
            action="FINALIZADO",
            alert_type="success")
        message.send(alert_type="success")

    notify(msg="O Deploy do {} foi finalizado".format(folder_name))
    return True
