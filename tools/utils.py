# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
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
        print("\n\n>> {}".format(title))
        print("{:*^{num}}".format('', num=len(title) + 3))
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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
