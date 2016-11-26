# -*- coding: utf-8 -*-
"""
Settings para o LI-Tools
"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes


# Linha de comando para o prompt
################################
TERMINAL_CMD = "meg"

# Configurações do Projeto
##########################
CONFIG_FILE = "meg-config"
ENV_NAME = "MEGALUS_PATH"

STAGE_DB = "li-db-staging.ciksobkqlidb.us-east-1.rds.amazonaws.com"
STAGE_PORT = 5432

LOCAL_DB = "meg_postgres_host"
LOCAL_PORT = 5432

PYPI_NAME = "meg-tools"

# Lista de Aplicações do Projeto
################################

# A ordem dos branchs é da
# branch mais volátil até a de producao
# Ex: develop, master
APPLICATIONS = [
    ('megdocker', ['master']),
    ('megpainel', ['develop', 'master']),
    ('megtools', ['master'])
]

# Aplicações que minificam arquivos durante o deploy
MINIFY_BEFORE = [

]

# Aplicações que sincronizam arquivos no S3 durante o deploy
SYNC_S3 = [

]

# Compressão de arquivos estáticos
##################################
baseDirStatic = ["static"]

# Arquivos JS para minificar num unico arquivo
jsSources = [
    ("js", "app_painel.js")
]

# Arquivos CSS para minificar num unico arquivo
cssSources = [
    ("css", "app_painel.css")
]

# Arquivos JS para minificar individualmente
jsAlone = [
    ("js", "app_painel.js")
]

# Arquivos CSS para minificar individualmente
cssAlone = [
    ("css", "app_painel.css")
]

# CONFIGURACAO PARA DOCKER
##########################
DOCKER_REPO_NAME = "megtools"
DOCKERFILE_NAME = "Dockerfile_local"

# CONFIGURAÇÃO PARA VCS
#######################
VCS_NAME = "Bitbucket"
VCS_BASE_URL = "https://github.com/lojaintegrada/"


# CONFIGURACAO PARA AMAZON WEB SERVICES
#######################################
USE_AWS = False
S3_SYNC_CMD = "aws s3 sync static/ s3://lojaintegrada.cdn/{branch}/static/ --acl public-read"

# AWS EC2 CONTAINER SERVICE
###########################

# Caso o nome do container seja
# diferente do nome da aplicacao
# fazer o de/para aqui
USE_ECR = False
ECR_NAME = {

}


# CONFIGURACAO PARA SLACK
#########################
USE_SLACK = False
TEST_CHANNEL = "#teste_automacao"

# CONFIGURACAO PARA DATADOG
###########################
USE_DATADOG = False


# DICIONARIO DE DADOS
#####################

CONFIG_DICT = {
    "project_path": None,
    "docker_compose_path": None
}

if USE_AWS:
    CONFIG_DICT['aws_key'] = None
    CONFIG_DICT['aws_secret'] = None
    CONFIG_DICT['aws_region'] = None

if USE_SLACK:
    CONFIG_DICT['slack_url'] = None
    CONFIG_DICT['slack_channel'] = None
    CONFIG_DICT['slack_icon'] = None
    CONFIG_DICT['slack_user'] = None

if USE_DATADOG:
    CONFIG_DICT['datadog_api_key'] = None
    CONFIG_DICT['datadog_app_key'] = None