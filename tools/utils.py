# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import os
import subprocess


def confirma(pergunta):
    """Retorna S ou N"""
    resposta_ok = False
    while not resposta_ok:
        resposta = raw_input("{} (s/n)? ".format(pergunta))
        if resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    return resposta[0].upper()


def run_command(command_list, title=None, get_stdout=False):
    if title:
        print(u"\n\n>> {}".format(title.decode('utf-8')))
        print(u"{:*^{num}}".format('', num=len(title) + 3))
    # try:
    for task in command_list:
        if task['run_stdout']:
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
            print('Ocorreu um erro. Processo abortado')
            return False

    return True if not get_stdout else ret


def get_app(application, data, title=None):
    folder_name = os.path.split(data['project_path'])[-1]
    # 1. Lista todos os containers que estao rodando
    # docker ps -a | grep painel | awk '{print $1,$2}'
    ret = run_command(
        title=title,
        get_stdout=True,
        command_list=[
            {
                'command': "docker ps | awk '{print $1,$2}'",
                'run_stdout': False
            }
        ]
    )
    raw_list = ret.split('\n')

    app_list = []

    for obj in raw_list:
        if obj.startswith("CONTAINER ID"):
            continue
        if len(obj.split(" ")) != 2:
            continue
        if obj.split(" ")[1].startswith(folder_name):
            app_list.append((
                obj.split(" ")[0],
                obj.split(" ")[1].replace("{}_".format(folder_name), "")
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
                rep = raw_input(
                    "Selecione o App: (1-{}): ".format(i - 1))
                if int(rep) in xrange(1, i):
                    resposta_ok = True
            except KeyboardInterrupt:
                print("\n")
                return (None, None)
            except:
                pass
        return (all_apps[int(rep) - 1][0], all_apps[int(rep) - 1][1])


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
