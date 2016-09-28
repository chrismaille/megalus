#! /usr/bin/env python3
import os
import json
from git import Repo
from deploy.config import get_config_data, APPLICATIONS, MINIFY_BEFORE, SYNC_S3
from deploy.messages import Message
from deploy.utils import run_command
from deploy.compress import minifyCSS, minifyJS


def main():
    config = get_config_data()

    # Pega a pasta atual e verifica
    # se é uma pasta valida para deploy
    current_dir = os.getcwd()
    try:
        repo = Repo(current_dir)
        branch = repo.active_branch
    except:
        print("Repositório GIT não encontrado.")
        print("O comando deve ser executado na mesma "
              "pasta onde se encontra a subpasta .git.")
        print("Comando abortado.")
        return False
    app_list = [
        app
        for app, branch in APPLICATIONS
    ]
    if branch not in app_list and branch != "LI-Deploy":
        print("Repositório não reconhecido.")
        return False

    # Confirma operação
    branch_name = branch.name
    last_commit = repo.head.commit.message
    folder_name = os.path.split(current_dir)[-1]
    print("Repositório: {}".format(folder_name))
    print("Branch Atual: {}".format(branch_name))
    print("Último Commit: {}".format(last_commit))

    resposta_ok = False
    while not resposta_ok:
        resposta = input("Deseja continuar (s/n)? ")
        if resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    if resposta[0].upper() == "N":
        return False

    # Gera Dockerrun
    json_model = {
        'AWSEBDockerrunVersion': '1',
        'Image': {
            'Name': '{account}.dkr.ecr.{region}.amazonaws.com/{app}:{branch}'.format(
                app=folder_name,
                branch=branch_name),
            'Update': 'true'},
        'Ports': [
            {
                'ContainerPort': '80'}],
        'Logging': "/var/eb_log"}

    print("\n>> Atualiza Dockerrun")
    print("*********************")
    with open("./Dockerrun.aws.json", 'w') as file:
        file.write(json.dumps(json_model, indent=2))

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
                'command': "docker build -f Dockerfile_local -t {} .".format(
                    folder_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {app}:latest {account}.dkr.ecr.{region}.amazonaws.com/{app}:latest".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=folder_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}.dkr.ecr.{region}.amazonaws.com/{app}:latest".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=folder_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}.dkr.ecr.{region}.amazonaws.com/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=folder_name,
                    branch=branch_name
                ),
                'run_stdout': False
            }
        ]
    )
    if not ret:
        return False

    # Ações específicas do App
    # 1. Minify estáticos
    if branch_name in MINIFY_BEFORE:
        print("\n>> Minificando arquivos estáticos")
        print("*********************************")
        ret = minifyCSS()
        if not ret:
            return False

        ret = minifyJS()
        if not ret:
            return False

    # 2. Sincronizar estáticos
    if branch_name in SYNC_S3:
        ret = run_command(
            title="Sincronizando arquivos estáticos no S3/{}".format(branch_name),
            command_list=[
                {
                    'command': "aws s3 sync static/ s3://lojaintegrada.cdn/{branch}/static/ --acl public-read".format(branch_name),
                    'run_stdout': False}])
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
            action="FINALIZADO")
        message.send_datadog()
        message.send_slack()

    return True


def start():
    print(
        "\n\n************************\n\n"
        "LI-Deploy v1.0\n\n"
        "************************\n"
    )
    retorno = main()
    if not retorno:
        print("Operação não concluída.\n")

if __name__ == "__main__":
    start()
