# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import subprocess


def run_command(command_list, title=None):
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
        else:
            ret = subprocess.call(
                task['command'],
                shell=True,
                stderr=subprocess.STDOUT
            )

        if ret != 0:
            print('Ocorreu um erro. Processo abortado')
            return False

    return True
