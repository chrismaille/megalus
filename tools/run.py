#!/usr/bin/env python
# coding: utf-8
"""Ferramenta Loja Integrada.

Usage:
    li config
    li deploy
    li debug    [<app>]
    li test     [<app>] (--django | --unit)
    li telnet   [<app>] (--p)
    li bash     [<app>]

Options:
    -h  --help          Mostra esta tela
    -p <port>           Porta para Telnet
    -j  --django        Roda o teste unitario do Django
    -u  --unit          Roda o teste unitario do Python
"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import json
from docopt import docopt
from tools.config import get_config_data
from tools.utils import confirma
from tools.deploy import run_deploy
from tools.docker import run_debug

VERSION = "1.4b3"


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
