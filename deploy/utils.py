# -*- coding: utf-8 -*-
from __future__ import print_functions, unicode_literals
import subprocess


def run_command(command_list, title=None):
    if title:
        print("\n\n>> {}".format(title))
        print("{:*^{num}}".format('', num=len(title) + 3))
    # try:
    for task in command_list:
        if task['run_stdout']:
            ret = subprocess.call(
                [task['command']],
                shell=True,
                stdout=subprocess.PIPE
                )

            if ret.returncode != 0:
                print('Ocorreu um erro. Processo abortado')
                return False

            ret = subprocess.call(
                [ret.stdout],
                shell=True
                )
        else:
            ret = subprocess.call(
                [task['command']],
                shell=True
                )

        if ret.returncode != 0:
            print('Ocorreu um erro. Processo abortado')
            return False

    return True
