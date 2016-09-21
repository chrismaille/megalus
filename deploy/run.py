import os
import subprocess
from git import Repo
from .config import get_config_data
from .messages import Message


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
    last_commit = repo.head.commit.message
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
    print("\n>> Atualiza GitHub...")
    git_command = "git push origin {}".format(branch.name)
    try:
        subprocess.run([git_command], shell=True, check=True)
    except:
        print('Ocorreu um erro. Processo abortado')
        return False

    # Envia Mensagem Datadog/Slack
    if branch.name in ['production', 'master']:
        message = Message(config, branch, last_commit)
        message.send_datadog(alert_type="warning")

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
    retorno = main()
    if not retorno:
        print("Operação não concluída.\n")
