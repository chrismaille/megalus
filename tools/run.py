#!/usr/bin/env python
# coding: utf-8
"""Ferramenta Loja Integrada.

Usage:
    li config
    li deploy
    li debug    [<app>]
    li test     [<app>] [--django] [--rds]
    li telnet   [<app>] (<port>)
    li bash     [<app>]

Options:
    --help          Mostra esta tela
    --django        Roda o teste unitario do Django. (Padrao: Unittest.)
    --rds           Nos testes usar o RDS da Amazon

"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
from docopt import docopt
from tools.config import get_config_data
from tools.utils import confirma
from tools.deploy import run_deploy
from tools.docker import run_debug, run_telnet, run_test, run_bash

VERSION = "2.2.4"


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
            resposta = confirma("Confirma os dados")
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


def start():
    print(
        "\n\n************************\n\n"
        "LI-Tools v{version}\n\n"
        "************************\n".format(version=VERSION)
    )
    retorno = main()
    if retorno:
        print('\n')
    else:
        print("Operação finalizada.\n")


if __name__ == "__main__":
    start()
