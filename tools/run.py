#!/usr/bin/env python
# coding: utf-8
"""Ferramenta Loja Integrada.
Para mais detalhes acesse: https://bitbucket.org/maisimovel/megtools

Usage:
    meg config
    meg deploy
    meg update
    meg debug    [<app>]
    meg test     [<app>] [--django] [--rds]
    meg telnet   [<app>] (<port>)
    meg bash     [<app>]
    meg run      [<app>] [<command> ...]
    meg build    [<app>] [--no-cache]

Options:
    --help          Mostra esta tela
    --django        Roda o teste unitario do Django. (Padrao: Unittest.)
    --rds           Nos testes usar o RDS da Amazon
    --no-cache      Na build nao utilizar o cache
    <command>       Rode um comando para o run do container

"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
from docopt import docopt
from tools.config import get_config_data, run_update
from tools.utils import confirma
from tools.deploy import run_deploy
from tools.docker import run_debug, run_telnet, run_test, run_bash, run_runapp
from tools.version import show_version_warning
from tools import VERSION
from tools import settings


def main():
    """Faz o Parse dos Comandos"""
    arguments = docopt(__doc__, version=VERSION)
    #
    # CONFIG
    #
    if arguments['config'] is True:
        data = get_config_data()
        if data:
            print("Configuração Atual:")
            print(json.dumps(data, indent=2))
            resposta = confirma(u"Deseja rodar a configuração?")
            if resposta == "S":
                data = get_config_data(start_over=True)
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
        ret = run_debug(
            application=arguments['<app>']
        )
        return ret
    #
    # TELNET
    #
    if arguments['telnet'] is True:
        ret = run_telnet(
            application=arguments['<app>'],
            port=arguments['<port>']
        )
        return ret
    #
    # BASH
    #
    if arguments['bash'] is True:
        ret = run_bash(
            application=arguments['<app>']
        )
        return ret
    #
    # TEST
    #
    if arguments['test'] is True:
        ret = run_test(
            application=arguments['<app>'],
            test_type="django" if arguments['--django'] else None,
            rds=arguments['--rds']
        )
    #
    # RUN APP
    #
    if arguments['run'] is True:
        ret = run_runapp(
            application=arguments['<app>'],
            action='up' if not arguments['<command>'] else 'exec',
            arg=arguments['<command>']
        )
    #
    # BUILD ADD
    #
    if arguments['build'] is True:
        ret = run_runapp(
            application=arguments['<app>'],
            action='build',
            opt="--no-cache" if arguments['--no-cache'] else None
        )
    #
    # UPDATE
    #
    if arguments['update'] is True:
        ret = run_update()


def start():
    print(
        "\033[94m\033[1m\n\n************************\n\n"
        "{cmd}-Tools v{version}\n\n"
        "************************\n\033[0m".format(
            cmd=settings.TERMINAL_CMD.upper(), version=VERSION)
    )
    show_version_warning()
    retorno = main()
    if retorno:
        print('\n')
    else:
        print("Operação finalizada.\n")


if __name__ == "__main__":
    start()
