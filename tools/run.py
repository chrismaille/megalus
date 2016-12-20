#!/usr/bin/env python
# coding: utf-8
"""Ferramenta Mais Imovel/Megalus.
Para mais detalhes digite 'meg help'

Usage:
    meg bash     [<app>]
    meg build    [<app>] [--no-cache]
    meg config   [--clone-only]
    meg debug    [<app>]
    meg deploy
    meg help     [<option>]
    meg list     [<libs>...]
    meg rebuild  [-y | --yes]
    meg run      [<app>] [<command> ...]
    meg telnet   [<app>] (<port>)
    meg test     [<app>] [--django] [--rds]
    meg update   [-y | --yes] [--production | --staging]

Options:
    --help          Mostra esta tela
    --django        Roda o teste unitario do Django. (Padrao: Unittest.)
    --rds           Nos testes usar o RDS da Amazon
    --no-cache      Na build nao utilizar o cache
    <command>       Rode um comando para o run do container
    -y --yes        Confirma automaticamente
    <libs>          Mostrar a versão das livrarias solicitadas
    --production    Muda para a branch mais estável (ex. 'production')
    --staging       Altera as branchs para staging/beta durante o update

"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
from docopt import docopt
from tools import __version__
from tools import docker
from tools import settings
from tools.config import get_config_data, run_update
from tools.deploy import run_deploy
from tools.help import get_help
from tools.lists import show_list
from tools.utils import confirma
from tools.version import show_version_warning


def main():
    """Faz o Parse dos Comandos"""
    arguments = docopt(__doc__, version=__version__)

    if not arguments['help']:
        print("Para ajuda digite: meg help")
    #
    # CONFIG
    #
    if arguments['config'] is True:
        clone_only = arguments['--clone-only']
        data = get_config_data()
        if data and not clone_only:
            print("Configuração Atual:")
            print(json.dumps(data, indent=2))
        if clone_only:
            resposta = "S"
        else:
            resposta = confirma(u"Deseja rodar a configuração?")
        if resposta == "S":
            data = get_config_data(
                start_over=True,
                clone_only=clone_only
            )
        return True
    #
    # DEPLOY
    #
    if arguments['deploy'] is True:
        ret = run_deploy()
        return ret
    #
    # DEBUG
    #
    if arguments['debug'] is True:
        ret = docker.run_debug(
            application=arguments['<app>']
        )
        return ret
    #
    # TELNET
    #
    if arguments['telnet'] is True:
        ret = docker.run_telnet(
            application=arguments['<app>'],
            port=arguments['<port>']
        )
        return ret
    #
    # BASH
    #
    if arguments['bash'] is True:
        ret = docker.run_bash(
            application=arguments['<app>']
        )
        return ret
    #
    # TEST
    #
    if arguments['test'] is True:
        ret = docker.run_test(
            application=arguments['<app>'],
            test_type="django" if arguments['--django'] else None,
            rds=arguments['--rds']
        )
        return ret
    #
    # RUN APP
    #
    if arguments['run'] is True:
        ret = docker.run_runapp(
            application=arguments['<app>'],
            action='up' if not arguments['<command>'] else 'exec',
            arg=arguments['<command>']
        )
        return ret
    #
    # BUILD ADD
    #
    if arguments['build'] is True:
        ret = docker.run_runapp(
            application=arguments['<app>'],
            action='build',
            opt="--no-cache" if arguments['--no-cache'] else None
        )
        return ret
    #
    # UPDATE
    #
    if arguments['update'] is True:
        ret = run_update(
            no_confirm=arguments['--yes'],
            stable=arguments['--production'],
            staging=arguments['--staging'])
        return ret
    #
    # REBUILD
    #
    if arguments['rebuild'] is True:
        ret = docker.rebuild_docker(no_confirm=arguments['--yes'])
        return ret
    #
    # HELP
    #
    if arguments['help'] is True:
        ret = get_help(app=arguments['<option>'])
        return ret
    #
    # LIST
    #
    if arguments['list'] is True:
        ret = show_list(libs=arguments['<libs>'])
        return ret


def start():
    print(
        "\033[94m\033[1m\n\n************************\n\n"
        "{cmd}-Tools v{version}\n\n"
        "************************\n\033[0m".format(
            cmd=settings.TERMINAL_CMD.upper(), version=__version__)
    )
    show_version_warning()
    retorno = main()
    if retorno:
        print('\n')
    else:
        print("\nOperação finalizada.\n")


if __name__ == "__main__":
    start()
