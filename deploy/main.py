import os
from git import Repo
from deploy.config import get_config_data
from deploy.messages import Message
from deploy.utils import run_command

TEST = True


def main():
    print(
        "\n\n************************\n\n"
        "LI-Deploy v1.0\n\n"
        "************************\n"
    )

    # Pega a configuracao
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
    last_commit = repo.head.commit.message
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
        message = Message(config, branch, last_commit, folder_name, test=TEST)
        message.send_datadog(alert_type="warning", action="INICIANDO")
        message.send_slack(action="INICIANDO")

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker",
        command_list=[
            {
                'command': "aws ecr get-login --region us-east-1",
                'run_stdout': True
            },
            {
                'command': "docker build -f ./deploy/Dockerfile_local -t {} .".format(
                    folder_name
                ),
                'run_stdout': False
            },
            {
                'command': 'docker tag {app}:{branch} 157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:latest'.format(
                    app=folder_name,
                    branch=branch_name
                ),
                'run_stdout': False
            },
            {
                'command': 'docker push 157607069902.dkr.ecr.us-east-1.amazonaws.com/{app}:{branch}'.format(
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
    ret = run_command(
        title="Roda EB Deploy",
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
    pass
