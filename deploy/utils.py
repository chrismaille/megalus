import subprocess


def run_command(command_list, title=None):
    if title:
        print("\n>> {}".format(title))
    # try:
    ret = subprocess.run(
        command_list,
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    if ret.returncode != 0:
        print('Ocorreu um erro. Processo abortado')
