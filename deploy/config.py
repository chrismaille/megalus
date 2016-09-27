import os
from os.path import expanduser

APPLICATIONS = [
    'LI-Docker',
    'LI-Api-Carrinho',
    'LI-Api-Catalogo',
    'LI-Api-Envio',
    'LI-Api-Faturamento',
    'LI-Api-Integration',
    'LI-Api-Marketplace',
    'LI-Api-Pagador',
    'LI-Api-Pedido',
    'LI-Api-Plataforma',
    'LI-Api-V2',
    'LI-AppApi',
    'LI-AppConciliacao',
    'LI-AppLoja',
    'LI-AppPainel',
    'LI-Worker',
    'LI-Worker-Integration',
    'LI-Repo'
]

MINIFY_BEFORE = [
    'LI-AppLoja'
]

SYNC_S3 = [
    'LI-AppLoja',
    'LI-AppPainel'
]


def get_config_data(filename="li-config"):
    # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = {
        "aws_key": None,
        "aws_secret": None,
        "aws_account": None,
        "aws_region": None,
        "project_path": None,
        "slack_user": None,
        "slack_url": None,
        "slack_channel": None,
        "slack_icon": None,
        "datadog_api_key": None,
        "datadog_app_key": None
    }
    basepath = expanduser("~")
    filepath = "{}/.{}".format(basepath, filename)
    try:
        with open(filepath, 'r') as file:
            for line in file:
                key = line.split("=")[0].lower()
                value = line.split("=")[1].rstrip()
                config[key] = value

        with open(filepath, 'a') as file:
            for key in config:
                if not config.get(key):
                    value = input("Informe {}: ".format(key))
                    config[key] = value
                    file.write("{}={}\n".format(key.upper(), value))

    except:
        print("\n>> Configuração Inicial")
        print("***********************")
        with open(filepath, 'w') as file:
            for key in config:
                value = input("Informe {}: ".format(key))
                config[key] = value
                file.write("{}={}\n".format(key.upper(), value))

        # Grava arquivo de credenciais da Amazon
        aws_folder = "{}/.aws/".format(basepath)
        if not os.path.exists(aws_folder):
            os.makedirs(aws_folder)
        with open("{}/config".format(aws_folder), 'w') as file:
            file.write("[config]")

        with open("{}/credentials".format(aws_folder), 'w') as file:
            file.write('[default]')
            file.write('aws_access_key_id = {}'.format(config['aws_key']))
            file.write(
                'aws_secret_access_key = {}'.format(
                    config['aws_secret']))

        # Grava no bashrc a variavel LI-PROJECT-PATH
        pass

        # Clona os repositorios LI
        pass

    return config
