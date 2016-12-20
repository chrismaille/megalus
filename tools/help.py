# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
from tools.utils import bcolors

INICIAL = u"Este help mostra os comandos da ferramenta Meg-Tools.\nPara apenas visualizar os comandos e suas opções, digite 'li'.\nPara ver a Ajuda de todos os comandos, digite 'meg help'.\nPara ver a Ajuda de um comando específico digite 'meg help <comando>'.\n"

HELP_COMMANDS = [{'command': 'config',
                  'options': 'meg config [--clone-only]',
                  'description': u'Use para configurar o ambiente de desenvolvimento local.\nUse a opção `--clone-only` para clonar/baixar os repositórios apenas',
                  'examples': None,
                  'long_desc': None},
                 {'command': 'deploy',
                  'options': 'meg deploy',
                  'description': u'Use para fazer o deploy de um ambiente local na Amazon.\nÉ preciso rodar este comando na pasta-raiz de um dos repositorios clonados pelo comando `meg config`',
                  'examples': None,
                  'long_desc': None},
                 {'command': 'telnet',
                  'options': 'meg telnet <app> <port>',
                  'description': u'Use para abrir a aplicação informada num TTY que faz um telnet dentro do Docker para o endereco 127.0.0.1 e a porta especificada.\nSe não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.\nEquivale ao comando "docker exec -ti _container_ telnet 127.0.0.1 _porta_"',
                  'examples': 'meg telnet worker 6908',
                  'long_desc': None},
                 {'command': 'test',
                  'options': 'meg test <app> [--django] [--rds]',
                  'description': u'Use para rodar os testes unitários da aplicação selecionada usando Python Unittest. Utilize as opções abaixo para configurar os testes:\n* --django: Use os testes do Django ao invés de Unittest\n* --rds: Use o banco de dados na Amazon (utilizado pelo Travis) ao invés do banco de dados local, para rodar os testes',
                  'examples': 'meg test painel (abre o painel rodando unittest e banco de dados local)\nmeg test loja --django (abre o painel rodando django e banco de dados local)\nmeg test worker --rds (abre o painel rodando unittest e banco de dados de staging na Amazon)',
                  'long_desc': None},
                 {'command': 'bash',
                  'options': 'meg bash <app>',
                  'description': u'Use para abrir a aplicação informada num terminal bash (usuario root).\nSe não informar a aplicação a ferramenta irá perguntar qual aplicação abrir, a partir dos containers em atividade.\nEquivale ao comando "docker exec -ti _container_ /bin/bash"',
                  'examples': 'meg bash carrinho',
                  'long_desc': None},
                 {'command': 'run',
                  'options': 'meg run <app>',
                  'description': u'Roda a aplicação informada e suas dependências ou todas as aplicações/containers se não informar nenhuma aplicação.\nEquivale ao comando "docker-compose stop && docker-compose up _aplicacao_"',
                  'examples': 'meg run (roda todos os containers)\nmeg run painel (roda o container do Painel e os containers dependentes',
                  'long_desc': None},
                 {'command': 'build',
                  'options': 'meg build <app> [--no-cache]',
                  'description': u'Use para fazer a build do container da aplicação selecionada. Se nenhuma aplicação for informada, será feito a build de todos os containers:\n* --no-cache: Durante a build, forçar o download de todas as livrarias/dependencias\nEquivale ao comando "docker-compose stop && docker-compose build _aplicacao_"',
                  'examples': 'meg build (faz o build de todos os containers)\nmeg build loja (faz a build do container da Loja)',
                  'long_desc': None},
                 {'command': 'update',
                  'options': 'meg update [--yes] [--production | --staging]',
                  'description': u'Roda em cada repositório clonado pelo comando `meg config` o comando "git remote update && git fetch && git pull --all", desde que o repositorio esteja na branch prodution, staging, beta, release ou master (repositórios que estejam em outros branchs são ignorados)\nEm adição ele clona novos repositórios que não estejam na pasta do projeto informado.\nUse a opção --yes ou -y para confirmar automaticamente as operações.\nUse a opção --production para fazer o git checkout para a branch mais estável do projeto (exemplo: production, master, etc) antes do update.',
                  'examples': u'meg update (atualiza todas as branchs atuais)\nmeg update --production (faz o checkout para a branch mais estável e atualiza)\nmeg update --staging (faz o checkout para staging/beta e atualiza os repositórios',
                  'long_desc': None},
                 {'command': 'list',
                  'options': 'meg list [<libs>...]',
                  'description': u'Lista as aplicações existentes no Docker-Compose, e informa as seguintes informações:\n* O nome da aplicação e se o container está rodando\n* A branch em que o container está.\n* As diferenças no branch, em relação ao VCS (commits a frente/atrás, etc...).\n* A versão do LI-Repo que está instalado dentro do container.\n\nPara listar outras livrarias, digite elas após o comando, separando com espaço.',
                  'examples': 'meg list (para a lista padrao)\nmeg list django flask gunicorn (Para listar as versões do Django, Flask e Gunicorn que estão rodando dentro dos containers.)',
                  'long_desc': None},
                 {'command': 'rebuild',
                  'options': 'meg rebuild',
                  'description': u'Este comando exclui todas as imagens e containers existentes na máquina.\nEm seguida atualiza os repositórios existentes e baixa os novos.\nApós isso, inicia a build de todos os containers.\nCertifique-se de ter feito um backup do seu banco de dados local, antes de iniciar esse comando.',
                  'examples': None,
                  'long_desc': None}]


def get_help(app=None):
    if app:
        command_help = [
            obj
            for obj in HELP_COMMANDS
            if obj.get('command') == app
        ]
        if command_help:
            show_help(command_help, show_long_desc=True)
            return True
        else:
            return True
    else:
        show_help(sorted(HELP_COMMANDS, key=lambda x: x['command']))
        return True


def show_help(help_list, show_long_desc=False):
    if not show_long_desc:
        print(INICIAL)
    for command in help_list:
        print("\n{}{}Commando: {}{}".format(
            bcolors.BOLD,
            bcolors.WARNING,
            command['command'].upper(),
            bcolors.ENDC
        )
        )
        if command['options']:
            print("{}Opções:{}".format(bcolors.BOLD, bcolors.ENDC))
            print(command['options'])
        print("\n{}Resumo:{}".format(bcolors.BOLD, bcolors.ENDC))
        print(command['description'].encode("UTF-8"))
        if show_long_desc and command['long_desc']:
            print('\n{}'.format(command['long_desc']))
        if command['examples']:
            print("\n{}Exemplos:{}".format(bcolors.BOLD, bcolors.ENDC))
            print(command['examples'])
