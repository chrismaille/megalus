# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
import json
import platform
from git import Repo
from deploy.config import get_config_data, APPLICATIONS, MINIFY_BEFORE, SYNC_S3
from deploy.messages import Message
from deploy.utils import bcolors, run_command
from deploy.compress import minifyCSS, minifyJS

ECR_NAME = {
    'LI-AppPainel': 'app-painel-production',
    'LI-AppApi': 'li-api-v1',
    'LI-AppLoja': 'li-app-loja',
    'LI-AppConciliacao': 'li-app-conciliacao'
}


def main():
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
        for app, br in APPLICATIONS
    ]
    folder_name = os.path.split(current_dir)[-1]
    if folder_name.lower() not in app_list and not folder_name in [
            "LI-Deploy", "li-deploy"]:
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
    print("Último Commit: {}".format(last_commit))

    resposta_ok = False
    while not resposta_ok:
        resposta = raw_input("Deseja continuar (s/n)? ")
        if resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    if resposta[0].upper() == "N":
        return False

    # Ações específicas do App
    # 1. Minify estáticos
    if folder_name in MINIFY_BEFORE:
        print("\n>> Minificando arquivos estáticos")
        print("*********************************")
        ret = minifyCSS(current_dir=current_dir)
        if not ret:
            return False

        ret = minifyJS(current_dir=current_dir)
        if not ret:
            return False

    # 2. Sincronizar estáticos
    if folder_name in SYNC_S3:
        ret = run_command(
            title="Sincronizando arquivos estáticos no S3/{}".format(branch_name),
            command_list=[
                {
                    'command': "aws s3 sync static/ s3://lojaintegrada.cdn/{branch}/static/ --acl public-read".format(branch=branch_name),
                    'run_stdout': False}])
        if not ret:
            return False

    # Gera Dockerrun
    app_name = ECR_NAME.get(folder_name, None)
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
        title="Atualiza GitHub",
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
        message.send_datadog(alert_type="warning")
        message.send_slack()

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker",
        command_list=[
            {
                'command': "aws ecr get-login --region {region}".format(region=config['aws_region']),
                'run_stdout': True
            },
            {
                'command': "docker build -f Dockerfile_local -t {app}:{branch} .".format(
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
        title="Rodando EB Deploy",
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
        message.send_datadog()
        message.send_slack()

    return True


def start():
    print(
        "\n\n************************\n\n"
        "LI-Deploy v1.3.4\n\n"
        "************************\n"
    )
    retorno = main()
    if not retorno:
        print("Operação finalizada.\n")

if __name__ == "__main__":
    start()
