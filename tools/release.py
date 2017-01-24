import json
import os
import requests
from colorama import Fore, Style
from git import Repo
from requests.auth import HTTPBasicAuth
from tools import settings
from tools.config import get_config_data
from tools.deploy import run_deploy
from tools.messages import Message, notify
from tools.utils import run_command, confirma, print_title
from tools.release_eb import AWSManager


def make_pull_request(release):

    data = get_config_data()
    if not data:
        return False

    # Para criar o pull request para stable
    # é preciso verificar antes:
    print_title("Release: Gerar/Atualizar Pull Request")
    # 1. A branch atual é production
    current_dir = os.getcwd()
    folder_name = os.path.split(current_dir)[-1]
    try:
        repo = Repo(current_dir)
        branch = repo.active_branch
    except:
        print(Fore.RED + "Repositório GIT não encontrado.")
        print("O comando deve ser executado na pasta raiz")
        print("do repositório a ser enviado.")
        print("Comando abortado." + Style.RESET_ALL)
        return False
    if "release" not in branch.name:
        print(
            Fore.RED +
            "Erro: a branch deve ser 'release'" +
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
    api_repo_url = settings.VCS_BASE_API_URL + \
        settings.REPOSITORY_API_URL.format(
            repo=os.path.split(current_dir)[-1],
            commit=repo.commit().hexsha
        )
    try:
        ret_vcs = requests.get(
            url=api_repo_url,
            auth=HTTPBasicAuth(data['vcs_username'], data['vcs_password']),
            timeout=1
        )
        if ret_vcs.status_code == requests.codes.ok:
            commit_data = ret_vcs.json()
            build_status = commit_data['values'][0]['state']
            if build_status != 'SUCCESSFUL':
                print(Fore.RED + 'Erro: O status da última build é {}'.format(
                    build_status) + Style.RESET_ALL)
                return False
            else:
                print('Última build {}OK{}'.format(
                    Fore.GREEN, Style.RESET_ALL))
        else:
            raise ValueError()
    except:
        print(
            Fore.RED +
            "Não é possível determinar o status da última build." +
            Style.RESET_ALL)
        return False

    # 4. Gera a tag:
    try:
        last_version = repo.tags[-1].name.split(".")
    except:
        last_version = [0, 0, 0]

    major = int(last_version[0])
    minor = int(last_version[1])
    patch = int(last_version[2])

    if release == "major":
        major += 1
        minor = 0
        patch = 0
    elif release == "minor":
        minor += 1
        patch = 0
    elif release == "patch":
        patch += 1

    new_version = "{}.{}.{}".format(major, minor, patch)
    print(
        "Versão para o PR: {} -> {}{}{}".format(
            '.'.join(str(e) for e in last_version),
            Fore.YELLOW,
            new_version,
            Style.RESET_ALL))

    # 4. Confirma a operação
    resp = confirma('Deseja continuar')

    if not resp:
        return False

    if release != "same":
        run_command(
            command_list=[
                {
                    'command': 'git tag {}'.format(new_version),
                    'run_stdout': False
                }
            ]
        )

    ret = run_deploy(only_pr=True)

    # 5. Gerar o pull-request
    if ret:
        pr_url = settings.VCS_BASE_API_URL + \
            settings.PULL_REQUEST_API_URL.format(
                repo=os.path.split(current_dir)[-1]
            )
        post_data = {
            "destination": {
                "branch": {
                    "name": "master"
                }
            },
            "source": {
                "branch": {
                    "name": branch.name
                }
            },
            "title": "Pull Request para a versão {}".format(new_version)
        }

        resp = requests.post(
            url=pr_url,
            headers={"Content-Type": "application/json"},
            auth=HTTPBasicAuth(data['vcs_username'], data['vcs_password']),
            data=json.dumps(post_data)
        )

    if resp.status_code == requests.codes.created:
        title = "Pull Request gerado para {}".format(folder_name)
        text = "O usuário {} criou Pull Request do {} para a release {}".format(
            data['vcs_username'], folder_name, new_version)
        tags = ['Pull Request']

        # Envia Mensagem Datadog/Slack
        message = Message(
            config=data,
            branch=branch.name,
            title=title,
            text=text,
            repo=folder_name
        )
        message.send(alert_type="info", tags=tags)
        print(
            Fore.GREEN +
            "\nPull Request efetuado com sucesso." +
            Style.RESET_ALL)
        notify(msg='Pull Request efetuado com sucesso.')
        return True
    else:
        msg = 'Ocorreu um erro ao tentar enviar o Pull Request'
        print(Fore.RED + msg + Style.RESET_ALL)
        notify(msg=msg)
        return False


def start_deploy():
    if not os.environ.get('BITBUCKET_BRANCH'):
        print(
            Fore.RED +
            "ERRO: Este comando não pode ser executado localmente." +
            Style.RESET_ALL)
        return False

    print_title("Release: Iniciar Deploy")
    app_name = os.environ.get('APPLICATION_NAME')
    title = "Deploy Iniciado para".format(app_name)
    text = "Deploy Iniciado para {}".format(
        app_name)
    tags = ['Deploy']

    data = {
        'slack_url': os.environ.get('SLACK_URL'),
        'slack_channel': 'deploy',
        'slack_icon': 'ghost',
        'slack_user': 'bitbucket',
        'datadog_api_key': os.environ.get('DATADOG_API_KEY'),
        'datadog_app_key': os.environ.get('DATADOG_APP_KEY')
    }

    # Envia Mensagem Datadog/Slack
    message = Message(
        config=data,
        branch="master",
        title=title,
        text=text,
        repo=os.environ.get('APP_NAME')
    )
    message.send(alert_type="warning", tags=tags)

    status = AWSManager().deploy()

    if status == 'finished':
        title = "SUCESSO: Deploy finalizado para".format(app_name)
        text = "Deploy finalizado com SUCESSO para {}".format(
            app_name)
        tags = ['Deploy']
        alert_type = 'info'
    elif status == 'failure':
        title = "ERRO: Deploy para".format(app_name)
        text = "Deploy com ERRO para {}".format(
            app_name)
        tags = ['Deploy']
        alert_type = 'warning'
    else:
        title = "EM ANDAMENTO: Deploy para".format(app_name)
        text = "Deploy em andamento para {}. "
        "Por favor acompanhe pelo console do AWS.".format(
            app_name)
        tags = ['Deploy']
        alert_type = 'warning'

    message.send(alert_type=alert_type, tags=tags)

    return True if status != "failure" else False
