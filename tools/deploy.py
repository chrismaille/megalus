# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
import os
import platform
import re
from git import Repo
from tools import settings
from tools.compress import minifyCSS, minifyJS
from tools.config import get_config_data
from tools.messages import Message, notify
from tools.utils import bcolors, run_command, confirma


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
        print("Repositório GIT não encontrado.")
        print("O comando deve ser executado na pasta raiz")
        print("do repositório a ser enviado.")
        print("Comando abortado.")
        return False
    app_list = [
        app.lower()
        for app, br in settings.APPLICATIONS
    ]
    folder_name = os.path.split(current_dir)[-1]
    if folder_name.lower() not in app_list:
        print("Repositório não reconhecido.")
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
    if resposta == "N":
        return False

    # Ações específicas do App
    # 1. Minify estáticos
    if folder_name in settings.MINIFY_BEFORE:
        print("\n\033[1m\033[94m\n>> Minificando arquivos estáticos")
        print("*********************************\033[0m")
        ret = minifyCSS(current_dir=current_dir)
        if not ret:
            return False

        ret = minifyJS(current_dir=current_dir)
        if not ret:
            return False

    # 2. Sincronizar estáticos
    if folder_name in settings.SYNC_S3:
        ret = run_command(
            title="Sincronizando arquivos estáticos no S3/{}".format(branch_name),
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
            'Name': '{account}.dkr.ecr.{region}.amazonaws.com/{app}:{branch}'.format(
                account=config['aws_account'],
                app=app_name,
                branch=branch_name,
                region=config['aws_region']),
            'Update': 'true'},
        'Ports': [
            {
                'ContainerPort': '80'}],
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

    # Atualiza GitHub
    ret = run_command(
        title="Atualiza GitHub - {}".format(folder_name),
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

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker - {}".format(folder_name),
        command_list=[
            {
                'command': "aws ecr get-login --region {region}".format(region=config['aws_region']),
                'run_stdout': True
            },
            {
                'command': "docker build -f {name} -t {app}:{branch} .".format(
                    name=settings.DOCKERFILE_NAME,
                    app=app_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {app}:{branch} {account}.dkr.ecr.{region}.amazonaws.com/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=app_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}.dkr.ecr.{region}.amazonaws.com/{app}:{branch}".format(
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
