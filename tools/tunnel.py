# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, nested_scopes
import yaml
import os
from tools.config import get_config_data
from tools.utils import get_app

def run_ngrok(subdomain, app):
    # Busca configuração    
    data = get_config_data()
    if not data:
        return False

    # Busca docker-compose.yml
    dc_path = os.path.join(
        data['docker_compose_path'],
        'docker-compose.yml'
    )
    with open(dc_path, 'r') as file:
        dc_data = yaml.load(file)

    # Identifica aplicação
    name = ""
    container_id = None
    container_id, name = get_app(
        application=app,
        title="Rodar Túnel ngrok",
        data=data
    )
    if not container_id:
        return False

    # Busca a porta da aplicação
    try:
        services = dc_data['services']
        service_data = services[name]
        service_ports = service_data['ports']
        porta = service_ports[0].split(":")[0]
    except:
        porta = None

    if not porta:
        print("Nenhuma porta encontrada para a aplicação {}".format(name))
        return False

    os.system(
            "cd {} && ./ngrok -subdomain={} {}".format(data['docker_compose_path'], subdomain, porta)
        )

    return True