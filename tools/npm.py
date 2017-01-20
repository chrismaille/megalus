import os
from colorama import Fore, Style
from tools.config import get_config_data
from tools.utils import get_app, get_compose_data


def run_watch(application):
    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Rodar em modo Watch",
        data=data
    )
    if not name:
        return False

    dc_data = get_compose_data(data)

    try:
        if "_" in name:
            name = name.split("_")[1]
        app_folder = dc_data['services'][name][
            'build']['context'].split('/')[-1]
    except:
        print(Fore.RED + 'Pasta não encontrada.' + Style.RESET_ALL)
        return False

    watch_path = os.path.join(
        data['project_path'],
        app_folder,
        'frontend'
    )

    os.system(
        'cd {}/ && ./node_modules/.bin/webpack --config '
        'webpack.config.js --watch\n'.format(
            watch_path)
    )
