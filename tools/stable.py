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


def make_stable_pr():

    data = get_config_data()
    if not data:
        return False

    # Para criar o pull request para stable
    # é preciso verificar antes:

    # 1. A branch atual é production
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
    if branch.name != "production":
        print(
            Fore.RED +
            "Erro: a branch deve ser 'production'" +
            Style.RESET_ALL)
        return False

    # 2. O status git local está OK
    os.chdir(current_dir)
    status_ret = run_command(
        command_list=[
            {
                'command': 'git status -bs --porcelain',
                'run_stdout': False
            }
        ],
        get_stdout=True,
        title=None
    )
    if status_ret.count('\n') > 1 or "[" in status_ret:
        print(Fore.RED + "Erro - a branch está modificada:" + Style.RESET_ALL)
        print(status_ret)
        return False
    
    # 3. A ultima build da branch atual está OK
    # Usar endpoint: https://api.bitbucket.org/2.0/repositories/maisimovel/maispainel/commit/3b5ceda588c9e910e04f898a1991357720f5fda9/statuses
    # Buscar Chave: data['values'][0]['state'] == 'SUCCESSFUL'
    
    # 4. Confirma a operação

    # 1. Alterar o arquivo Dockerrun.aws.json
    # 2. Criar a imagem stable da branch
    # 3. Minificar/Sincronizar arquivos
    # 3. Commitar e subir o git
    # 4. Gerar o pull-request
