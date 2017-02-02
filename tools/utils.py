import os
import subprocess
import sys
import yaml
from colorama import Fore, Style
from unidecode import unidecode


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_title(text):
    line1 = "\n>> {}".format(text)
    line2 = "{:*^{num}}\n".format('', num=len(line1) - 1)
    print(Fore.YELLOW + '\033[1m' + line1)
    print(line2 + Style.RESET_ALL)


def confirma(pergunta):
    """Retorna S ou N"""
    resposta_ok = False
    while not resposta_ok:
        resposta = input("\n{} (s/n)? ".format(pergunta))
        if resposta and resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    return resposta[0].upper() == "S"


def unitext(text):
    text = unidecode(text)
    return text


def run_command(command_list, title=None, get_stdout=False):
    if title:
        print("\033[1m\033[93m\n\n>> {}".format(unitext(title)))
        print("{:*^{num}}\033[0m".format(
            '',
            num=len(title) + 3)
        )
    try:
        for task in command_list:
            if task.get('run_stdout', None):
                command = subprocess.check_output(
                    task['command'],
                    shell=True
                )

                if not command:
                    print('Ocorreu um erro. Processo abortado')
                    return False

                ret = subprocess.call(
                    command,
                    shell=True
                )
            elif get_stdout is True:
                ret = subprocess.check_output(
                    task['command'],
                    shell=True
                )
            else:
                ret = subprocess.call(
                    task['command'],
                    shell=True,
                    stderr=subprocess.STDOUT
                )

            if ret != 0 and not get_stdout:
                # print('Ocorreu um erro. Processo abortado')
                return False
    except:
        return False

    return True if not get_stdout else ret.decode('utf-8')


def get_app(application, data, title=None, stop=False):
    # 1. Lista todos os containers que estao rodando
    # docker ps -a | grep painel | awk '{print $1,$2}'
    if not stop:
        ret = run_command(
            title=title,
            get_stdout=True,
            command_list=[
                {
                    'command': "docker ps | awk '{print $1, $NF}'",
                    'run_stdout': False
                }
            ]
        )
    else:
        ret = run_command(
            title=title,
            get_stdout=True,
            command_list=[
                {
                    'command': "docker ps -a | awk '{print $1, $NF}'",
                    'run_stdout': False
                }
            ]
        )
    raw_list = ret.split('\n')

    app_list = []

    for obj in raw_list:
        if obj.startswith("CONTAINER"):
            continue
        if len(obj.split(" ")) != 2:
            continue

        app_list.append((
            obj.split(" ")[0],
            obj.split(" ")[1]
        ))

    # 2. Identifica qual o container que bate com o app solicitado
    filtered_list = [
        app
        for app in app_list
        if application and application in app[1]
    ]

    ask_for_app = False
    if filtered_list:
        if len(filtered_list) == 1:
            return (filtered_list[0][0], filtered_list[0][1])
        else:
            ask_for_app = True
    elif app_list:
        ask_for_app = True
    else:
        print("Nenhum aplicativo encontrado.")
        return (None, None)

    if ask_for_app:
        all_apps = filtered_list or app_list
        i = 1
        for app in all_apps:
            print("{}. {}".format(i, app[1]))
            i += 1
        resposta_ok = False
        print("\n")
        while not resposta_ok:
            try:
                rep = input(
                    "Selecione o App: (1-{}): ".format(i - 1))
                if rep and int(rep) in range(1, i):
                    resposta_ok = True
            except KeyboardInterrupt:
                print("\n")
                return (None, None)
            except:
                pass
        return (all_apps[int(rep) - 1][0], all_apps[int(rep) - 1][1])


def progress_bar(iteration, total, prefix='Lendo',
                 suffix='Complete', barLength=50):
    """
    Gerador de Barra de Progresso
    """
    formatStr = "{0:.2f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write(
        '\r%s |%s| %s%s %s ' %
        (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()


def get_compose_data(data):
    dc_path = os.path.join(
        data['docker_compose_path'],
        'docker-compose.yml'
    )

    with open(dc_path, 'r') as file:
        dc_data = yaml.load(file)

    return dc_data
