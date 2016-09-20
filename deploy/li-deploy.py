import os
import sys
from os.path import expanduser
from git import Repo


def main():
    # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = {
        "aws_key": None,
        "aws_secret": None,
        "project_path": None,
        "slack_user": None,
        "slack_url": None,
        "slack_channel": None,
        "slack_icon": None,
        "datadog_key": None,
        "datadog_secret": None
    }
    filepath = "{}/.li-config".format(expanduser("~"))
    try:
        with open(filepath, 'r') as file:
            for line in file:
                key = line.split("=")[0].lower()
                value = line.split("=")[1].rstrip()
                config[key] = value
    except:
        print("Configurar opções")
        with open(filepath, 'w') as file:
            for key in config:
                value = input("Informe {}: ".format(key))
                config[key] = value
                file.write("{}={}\n".format(key.upper(), value))

    # Pega a pasta atual e verifica
    # se é uma pasta valida para deploy
    current_dir = os.getcwd()
    try:
        repo = Repo(current_dir)
        branch = repo.active_branch
    except:
        print("Repositório GIT não encontrado. Abortando.")
        return

    # Atualiza GitHub
    pass

    # Envia Mensagem Datadog/Slack
    pass

    # Gerar imagem do Docker
    pass

    # Ações específicas do App
    pass

    # Rodar EB Deploy
    pass

    # Mensagem final
    pass


if __name__ == "__main__":
    print(
        "\n\n************************\n\n"
        "LI-Deploy v1.0\n\n"
        "************************\n"
    )
    main()
    print("\n")
