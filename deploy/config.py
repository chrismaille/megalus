from os.path import expanduser


def get_config_data():
        # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = {
        "aws_key": None,
        "aws_secret": None,
        "project_path": None,
        "slack_user": None,
        "slack_url": None,
        "slack_channel": None,
        "slack_icon": None,
        "datadog_key": None,
        "datadog_secret": None
    }
    filepath = "{}/.li-config".format(expanduser("~"))
    try:
        with open(filepath, 'r') as file:
            for line in file:
                key = line.split("=")[0].lower()
                value = line.split("=")[1].rstrip()
                config[key] = value
    except:
        print(">> Configurar opções")
        with open(filepath, 'w') as file:
            for key in config:
                value = input("Informe {}: ".format(key))
                config[key] = value
                file.write("{}={}\n".format(key.upper(), value))

    return config
