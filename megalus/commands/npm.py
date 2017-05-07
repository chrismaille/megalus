import os
import json
from colorama import Fore, Style
from megalus.core.li_tabulate import tabulate
from megalus.core.utils import get_app, get_compose_data, run_command
from megalus.projects.config import get_config_data


def run_watch(application, dev):
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
    if dev:
        os.system(
        'cd {}/ && ./node_modules/.bin/webpack --config '
        'webpack.config.js\n'.format(
            watch_path)
    )

    os.system(
        'cd {}/ && ./node_modules/.bin/webpack --config '
        'webpack.config.js --watch\n'.format(
            watch_path)
    )


def run_list(application):
    data = get_config_data()
    if not data:
        return False

    container_id, name = get_app(
        application=application,
        title="Listagem NPM de Dependências",
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

    ret_npm = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': 'cd {path} && npm ll -json'.format(path=watch_path),
                'run_stdout': False
            }
        ]
    )
    if not ret_npm:
        return False

    npm_json = json.loads(ret_npm)

    npm_dependencies = npm_json['dependencies']
    npm_depdev = npm_json['devDependencies']

    npm_list = []
    for dep in npm_dependencies:
        status = Fore.LIGHTGREEN_EX + "OK" + Style.RESET_ALL
        if npm_dependencies[dep]['extraneous']:
            status = Fore.LIGHTYELLOW_EX + 'Não incluído' + Style.RESET_ALL

        description = npm_dependencies[dep]['description']
        if len(description) > 60:
            description = description[:56] + ' ...'

        if dep in npm_depdev:
            dep_type = Fore.LIGHTBLACK_EX + "Dev" + Style.RESET_ALL
        else:
            dep_type = "Prod"

        npm_list.append(
            (npm_dependencies[dep]['name'],
             npm_dependencies[dep]['version'],
             dep_type,
             status,
             description)
        )

    final_list = sorted(npm_list, key=lambda x: x[0])

    print(tabulate(
        final_list,
        headers=['Nome', "Versão", "Tipo", "Status", "Descrição"]
    )
    )
