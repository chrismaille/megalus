import subprocess


def run_command(command_list, title=None):
    if title:
        print("\n\n>> {}".format(title))
        print("{:*^{num}}".format('', num=len(title) + 3))
    # try:
    for task in command_list:
        if task['run_stdout']:
            ret = subprocess.run(
                [task['command']],
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True)

            if ret.returncode != 0:
                print('Ocorreu um erro. Processo abortado')
                return False

            ret = subprocess.run(
                [ret.stdout],
                shell=True,
                universal_newlines=True)
        else:
            ret = subprocess.run(
                [task['command']],
                shell=True,
                universal_newlines=True)

        if ret.returncode != 0:
            print('Ocorreu um erro. Processo abortado')
            return False

    return True
