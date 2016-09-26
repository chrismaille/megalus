from os.path import expanduser

APPLICATIONS = [
    'li-api-carrinho',
    'li-api-catalogo',
    'li-api-envio',
    'li-api-faturamento',
    'li-api-integration',
    'li-api-marketplace',
    'li-api-pagador',
    'li-api-pedido',
    'li-api-plataforma',
    'li-api-v2',
    'li-appapi',
    'li-appconciliacao',
    'li-apploja',
    'li-apppainel',
    'li-worker',
    'li-worker-integration',
    'li-repo',
    'li-deploy'
]

MINIFY_BEFORE = [
    'li-apploja'
]

SYNC_S3 = [
    'li-apploja',
    'li-apppainel'
]


def get_config_data():
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
    filepath = "{}/.li-config".format(expanduser("~"))
    try:
        with open(filepath, 'r') as file:
            for line in file:
                key = line.split("=")[0].lower()
                value = line.split("=")[1].rstrip()
                config[key] = value
    except:
        print("\n>> Configurar opções")
        print("********************")
        with open(filepath, 'w') as file:
            for key in config:
                value = input("Informe {}: ".format(key))
                config[key] = value
                file.write("{}={}\n".format(key.upper(), value))

    return config
