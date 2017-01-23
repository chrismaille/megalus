#!/usr/bin/env python3
"""Ferramenta Megalus/Mais Imovel.
Para mais detalhes digite 'meg help'

Usage:
    meg bash        [<app>]
    meg build       [<app>] [--no-cache]
    meg config      [--clone-only]
    meg debug       [<app>]
    meg deploy
    meg help        [<option>]
    meg list        [<libs>...]
    meg npm list    <app>
    meg rebuild     [-y | --yes]
    meg release     [(major|minor|patch)]
    meg release eb     
    meg run         [<app>] [<command> ...]
    meg service     (redis|memcached) [<key>]
    meg telnet      [<app>] (<port>)
    meg test        [<app>] [--using=(django|nose|pytest)] [--rds]
    meg tunnel      [<subdomain>] [<app>]
    meg update      [-y | --yes] [--production | --staging]
    meg watch       <app>

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
    <subdomain>     O subdominio para o tunel reverso, via ngrok
    <app>           Aplicacao que sera alvo do comando

"""

from colorama import Fore, Style
from docopt import docopt
from tools import __version__
from tools import docker
from tools import settings
from tools.build import run_build
from tools.config import get_config_data, run_update
from tools.deploy import run_deploy
from tools.help import get_help
from tools.li_tabulate import tabulate
from tools.lists import show_list
from tools.npm import run_watch, run_list
from tools.services import run_service
from tools.tunnel import run_ngrok
from tools.utils import bcolors, confirma, run_command
from tools.version import show_version_warning
from tools.release import make_pull_request


def check_vpn():
    # Checa se a VPN está ativa
    if settings.CHECK_VPN:
        ret_tun = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': 'ifconfig | grep tun',
                    'run_stdout': False
                }
            ]
        )

        if not ret_tun:
            print("\n{}{}ERRO:{} VPN não encontrada.".format(
                bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
            print("Por favor, ative a VPN e tente novamente.")
            return False

    return True


def main():
    """Faz o Parse dos Comandos"""
    arguments = docopt(__doc__, version=__version__)

    if not arguments['help']:
        print(
            Fore.LIGHTBLACK_EX +
            "\nPara ajuda digite: meg help\n" +
            Style.RESET_ALL)

    #
    # CONFIG
    #
    if arguments['config'] is True and check_vpn():
        clone_only = arguments['--clone-only']
        data = get_config_data()
        if data and not clone_only:
            print(
                Fore.LIGHTCYAN_EX +
                "\nConfiguração Atual:\n" +
                Style.RESET_ALL)
            config_list = [
                (obj, data[obj])
                for obj in data
            ]
            print(tabulate(
                config_list,
                headers=["Opção", "Valor"]
            ))
        if clone_only or not data:
            resposta = True
        else:
            resposta = confirma("Deseja rodar a configuração?")
        if resposta:
            data = get_config_data(
                start_over=True,
                clone_only=clone_only
            )
        return True
    #
    # DEPLOY
    #
    if arguments['deploy'] is True and check_vpn():
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
            using=arguments['--using'],
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
    # BUILD APP
    #
    if arguments['build'] is True:
        ret = run_build(
            application=arguments['<app>']
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
    if arguments['list'] and not arguments['npm']:
        ret = show_list(libs=arguments['<libs>'])
        return ret
    #
    # TUNNEL
    #
    if arguments['tunnel'] is True and check_vpn():
        ret = run_ngrok(
            subdomain=arguments['<subdomain>'],
            app=arguments['<app>']
        )
        return ret
    #
    # SERVICE
    #
    if arguments['service'] is True:
        if arguments['redis']:
            service = 'redis'
        else:
            service = 'memcached'
        ret = run_service(
            service=service,
            key=arguments['<key>']
        )
        return ret
    #
    # WATCH
    #
    if arguments['watch'] is True:
        ret = run_watch(application=arguments['<app>'])
        return ret
    #
    # NPM LIST
    #
    if arguments['npm'] and arguments['list']:
        ret = run_list(application=arguments['<app>'])
        return ret
    #
    # RELEASE
    # 
    if arguments['release'] and not arguments['eb']:
        if arguments['major']:
            release = 'major'
        elif arguments['minor']:
            release = 'minor'
        elif arguments['patch']:
            release = 'patch'
        else:
            release = "same"
        ret = make_pull_request(release=release)
        return ret
    #
    # RELEASE EB
    #
    if arguments['release'] and arguments['eb']:
        pass

def start():
    print(
        Fore.CYAN +
        "\033[1m\n\n************************\n\n"
        "{cmd}-Tools v{version}\n\n"
        "************************".format(
            cmd=settings.TERMINAL_CMD.upper(),
            version=__version__) +
        Style.RESET_ALL)
    show_version_warning()
    retorno = main()
    if retorno:
        print('\n')
    else:
        print("\nOperação finalizada.\n")


if __name__ == "__main__":
    start()
