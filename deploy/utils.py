import subprocess


def run_command(command_list, title=None):
    if title:
        print("\n>> {}".format(title))
    # try:
    for task in command_list:
        ret = subprocess.run(
            [task['command']],
            shell=True,
            stdout=subprocess.PIPE,
            universal_newlines=True)

        if ret.returncode != 0:
            print('Ocorreu um erro. Processo abortado')
            return False

        if task['run_stdout']:
            ret = subprocess.run(
                [ret.stdout],
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True)

        if ret.returncode != 0:
            print('Ocorreu um erro. Processo abortado')
            return False

    return True
