"""
Settings para o MEG-Tools

Chaves do JSON:

CONFIG_FILE = Nome do arquivo de configuração (ex: "meg-config")
ENV_NAME = Variável de ambiente com o path do projeto (ex: "MEGALUS_PATH")
LOCAL_DBS = Lista com a configuração de cada banco de dados do projeto:
ex: [
    {
        'local_name': "service.postgres.local",
        'desc': "Banco de dados do Painel",
        'local_port': 5432,
        'user': 'nome_do_usuario',
        'name': 'nome_do_banco',
        'admin': "nome do container docker usado para enviar os comandos (ex.:frontend.painel.local)",
        'stage_name': "",
        'stage_port': 5432
    }
]
CHECK_VPN = Usa VPN para acessar AWS?
TEST_PRIORITY = Lista com os programas para rodar testes, na ordem de prioridade.
Ex.: [
    'nose',
    'pytest'
]
APPLICATIONS = Lista de Aplicações do Projeto.
A ordem das branchs é da mais volátil até a mais estável.
Ex.: [
    ['app1', ['master']],
    ['app2', ['develop', 'master']]
]
LIBRARIES = Lista de livrarias para mostrar no comando meg list:
Ex.: [
    'Django'
]
MINIFY_BEFORE = Aplicações que minificam arquivos durante o deploy
ex.: [
    'app1'
]
SYNC_S3 = Aplicações que sincronizam arquivos no S3 durante o deploy
Ex.: [
    'app1'
]
baseDirStatic = Caminho da pasta base para Compressão de arquivos estáticos nos aplicativos acima
Ex.: [
    "dir1", "dir2", static"
]
jsSources = Caminho relativo a base dos arquivos JS para minificar num unico arquivo.
Todos os arquivos são comprimidos no arquivo "all.min.js"
Ex.: [
    ['folder3', 'index.js'],
    ['folder4', 'app.js']
]
cssSources = Caminho relativo a base dos arquivos CSS para minificar num unico arquivo.
Todos os arquivos são comprimidos no arquivo "all.min.css"
Ex.: [
    ['folder3', 'index.css'],
    ['folder4', 'app.css']
]
jsAlone = Arquivos JS para minificar individualmente

Ex.: [
    ["js", "index.js"]
]
#
cssAlone =  Arquivos CSS para minificar individualmente
Exemplo: index.css será salvo como index.min.css
Ex.: [
    ["css", "index.css"]
]
DOCKER_REPO_NAME = Nome do projeto com o Docker-Compose.yaml (ex.: "megdocker")
DOCKER_BASE_IMAGE_REPO = Imagem usada como base para a build das restantes (ex.: "megbase")
DOCKERFILE_DEPLOY = Nome do arquivo Dockerfile para deploy. Ex: "Dockerfile_deploy"
DOCKERFILE_DEVELOPMENT = Nome do arquivo Dockerfile para develop. Ex.:"Dockerfile_dev"
VCS_NAME = Nome do VCS. Ex: "Bitbucket"
VCS_BASE_URL = URL base do VCS: Ex.: "https://bitbucket.org/NOME/"
VCS_BASE_API_URL = URL base para API. Ex.: 'https://api.bitbucket.org/'
REPOSITORY_API_URL = '2.0/repositories/NOME/{repo}/commit/{commit}/statuses'
PULL_REQUEST_API_URL = '2.0/repositories/NOME/{repo}/pullrequests/'
USE_AWS = Projeto hospedado na Amazon?
S3_SYNC_CMD = Comando para sincronizar o S3. Ex.: "aws s3 sync static/ s3://dominio.cdn/{branch}/static/ --acl public-read"
USE_ECR = Projeto hospeda as imagens Docker no ECR Amazon?
ECR_NAME = Faz o De/Para do nome do projeto para o nome do container no ECS
Ex.: {
    'app1': 'prod.app'
}
USE_REDIS = Usa Redis?
USE_MEMCACHED = Usa Memcached?
USE_SLACK = Usa Slack?
TEST_CHANNEL = Canal para testes no Slack. Ex.: "#teste_automacao"
USE_DATADOG = Usa Datadog?
USE_GRAFANA = Usa Grafana?
GRAFANA_MSG_URL = URL para enviar eventos ao Grafana. Ex: "http://dominio:porta/write?db=msgs"
"""
import os
import json
from collections import OrderedDict
from megalus.core.utils import print_title


class Setting():
    def __init__(self, project):
        self.project = project
        curdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if curdir.endswith("megalus"):
            self.path = os.path.join(
                curdir,
                "projects",
                "data"
            )
        else:
            self.path = os.path.join(
                curdir,
                "megalus",
                "projects",
                "data"
            )

    def get_project(self):
        if not self.project:
            print_title("Selecione o Projeto")
            all_projects = [
                filename.replace(".json", "").replace("_", " ").title()
                for root, dirs, file in os.walk(self.path)
                for filename in file
                if filename.endswith(".json")
            ]
            if len(all_projects) == 1:
                return all_projects[0]
            i = 1
            for app in all_projects:
                print("{}. {}".format(i, app))
                i += 1
            resposta_ok = False
            print("\n")
            while not resposta_ok:
                try:
                    rep = input(
                        "Selecione o Projeto: (1-{}): ".format(i - 1))
                    if rep and int(rep) in range(1, i):
                        resposta_ok = True
                except KeyboardInterrupt:
                    print("\n")
                    self.project = False
                    break
                except:
                    pass
            self.project = all_projects[int(rep) - 1]

        return self.project

    def read(self):
        name = self.get_project()
        if not name:
            return False
        filename = os.path.join(self.path, "{}.json".format(
            name.replace(" ", "_").lower()
        ))
        with open(filename, "r") as file:
            config_dict = json.loads(file.read())
            for key in config_dict:
                setattr(self, key, config_dict[key])


project_name = os.environ.get('MEG_CUR_PROJ')
settings = Setting(project_name)
settings.read()

if settings.project:
    settings.CONFIG_DICT = OrderedDict.fromkeys(
        [
            "project_path",
            "docker_compose_path",
            "use_for_tests",
            "vcs_username",
            'vcs_password'
        ]
    )
    settings.CONFIG_DICT['use_for_tests'] = 'unittest'

    if settings.USE_AWS:
        settings.CONFIG_DICT['aws_key'] = None
        settings.CONFIG_DICT['aws_secret'] = None
        settings.CONFIG_DICT['aws_region'] = None
        settings.CONFIG_DICT['aws_account'] = None

    if settings.USE_SLACK:
        settings.CONFIG_DICT['slack_url'] = None
        settings.CONFIG_DICT['slack_channel'] = None
        settings.CONFIG_DICT['slack_icon'] = None
        settings.CONFIG_DICT['slack_user'] = None

    if settings.USE_DATADOG:
        settings.CONFIG_DICT['datadog_api_key'] = None
        settings.CONFIG_DICT['datadog_app_key'] = None

    if settings.USE_REDIS:
        settings.CONFIG_DICT['redis_host'] = None
        settings.CONFIG_DICT['redis_port'] = None
        settings.CONFIG_DICT['redis_db'] = None

    if settings.USE_MEMCACHED:
        settings.CONFIG_DICT['memcached_host'] = None
        settings.CONFIG_DICT['memcached_port'] = None
