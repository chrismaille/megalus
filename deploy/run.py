import os
import json
from git import Repo
from deploy.config import get_config_data
from deploy.messages import Message
from deploy.utils import run_command

TEST = True


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

    # Confirma operação
    branch_name = branch.name
    last_commit = repo.head.commit.message.split("(adiciona Dockerrun)")
    folder_name = os.path.split(current_dir)[-1].lower()
    print("Repositório: {}".format(folder_name))
    print("Branch Atual: {}".format(branch_name))
    print("Último Commit: {}".format(last_commit))

    resposta_ok = False
    while not resposta_ok:
        resposta = input("Deseja continuar (S/N)? ")
        if resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    if resposta[0].upper() == "N":
        return False

    # Gera Dockerrun
    json_model = {
        'AWSEBDockerrunVersion': '1',
        'Image': {
            'Name': '157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:{branch}'.format(
                app=folder_name,
                branch=branch_name),
            'Update': 'true'},
        'Ports': [
            {
                'ContainerPort': '80'}],
        'Logging': "/var/eb_log"}
    with open("./Dockerrun.aws.json", 'w') as file:
        file.write(json.dumps(json_model, indent=2))
    ret = run_command(title="Adiciona Dockerrun",
                      command_list=[{'command': "git add ./Dockerrun.aws.json",
                                     'run_stdout': False},
                                    {'command': "git commit -m \"{}(adiciona Dockerrun)\"".format(last_commit),
                                     'run_stdout': False},
                                    ])

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
            test=TEST,
            action="INICIADO")
        message.send_datadog(alert_type="warning")
        message.send_slack()

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker",
        command_list=[
            {
                'command': "aws ecr get-login --region us-east-1",
                'run_stdout': True
            },
            {
                'command': "docker build -f Dockerfile_local -t {} .".format(
                    folder_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {app}:latest 157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:latest".format(
                    app=folder_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push 157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:latest".format(
                    app=folder_name
                ),
                'run_stdout': False
            },
            {
                'command': "docker push 157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:{branch}".format(
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
    pass

    # Rodar EB Deploy
    pass

    # Mensagem final
    pass

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
