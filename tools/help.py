# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
from tools.utils import bcolors

INICIAL = u"Este help mostra os comandos da ferramenta MEG-Tools.\nPara apenas visualizar os comandos e suas opções, digite 'li'.\nPara ver a Ajuda de todos os comandos, digite 'meg help'.\nPara ver a Ajuda de um comando específico digite 'meg help <comando>'.\n"

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
                  'options': 'meg test [<app>] [--using=(django|nose|pytest)] [--rds]',
                  'description': u'Use para rodar os testes unitários da aplicação.\nA ferramenta permite o uso das livrarias: nose (com coverage) e pytest. Para isto basta informar qual utilizar com a opção "--using".\nSe nenhuma livraria estiver instalada ou nenhuma for selecionada, será usado o Unittest padrão do Python.\nUtilize as opções abaixo para configurar os testes:\n* --using: Use uma das opções a seguir: nose, pytest, django\n* --rds: Use o banco de dados na Amazon (utilizado pelo ambiente de Staging) ao invés do banco de dados local, para rodar os testes',
                  'examples': 'meg test painel (abre o Painel rodando unittest e banco de dados local)\nmeg test loja --using=django (abre o Site rodando django e banco de dados local)',
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
                  'description': u'Lista as aplicações existentes no Docker-Compose, e informa as seguintes informações:\n* O nome da aplicação e se o container está rodando\n* A branch em que o container está.\n* As diferenças no branch, em relação ao VCS (commits a frente/atrás, etc...).\n* A porta que está sendo exposta no container\n\nPara listar outras livrarias, digite elas após o comando, separando com espaço.',
                  'examples': 'meg list (para a lista padrao)\nmeg list django flask gunicorn (Para listar as versões do Django, Flask e Gunicorn que estão rodando dentro dos containers.)',
                  'long_desc': None},
                 {'command': 'rebuild',
                  'options': 'meg rebuild',
                  'description': u'Este comando exclui todas as imagens e containers existentes na máquina.\nEm seguida atualiza os repositórios existentes e baixa os novos.\nApós isso, inicia a build de todos os containers.\nCertifique-se de ter feito um backup do seu banco de dados local, antes de iniciar esse comando.',
                  'examples': None,
                  'long_desc': None},
                  {'command': 'tunnel',
                  'options': 'meg tunnel <subdominio> <aplicacao>',
                  'description': u'Este comando cria um tunel reverso a partir de uma instância amazon (tunnel.awsli.com.br) para uma das aplicações rodando localmente.\nUse quando é necessário informar, em um serviço de terceiros, um endereço http ou https, ao invés de "localhost".\nO ngrok usa o <subdomínio> informado para criar a URL (subdominio.tunnel.awsli.com.br), tanto para http, quanto https e redireciona as chamadas para a porta da <aplicação> informada.\nEquivale ao comando "ngrok --subdomain=<subdominio informado> <porta informada>"',
                  'examples': u'meg tunnel retorno painel (Cria o tunel "http://retorno.tunnel.maisimovel.net" e redireciona as chamadas para a aplicação MaisPainel)\nmeg tunnel ret-facebook site (Cria o túnel "http://ret-facebook.maisimovel.net" e redireciona as requisições para o Site)',
                  'long_desc': None}
                  ]


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
