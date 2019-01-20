import datetime
import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from buzio import console
from loguru import logger

from megalus.utils import get_path

__version__ = "2.0.0a3"


class Megalus:

    def __init__(self, config_file):
        self._config_file = config_file
        self.compose_data_list = []
        self._data = {}  # type: Dict[str, Any]
        self.all_services = []

    def _convert_lists(self, data, key):
        """Convert list to dict inside yaml data.

        Works only for Key=Value lists.

        Example:
            environment:
                - DEBUG=false
            ports:
                - "8090:8080"

        Result:
            environment: {"DEBUG": "false"}
            ports: ['8090:8080']

        """
        if isinstance(data[key], list) and "=" in data[key][0]:
            data[key] = {obj.split("=")[0]: obj.split("=")[-1] for obj in data[key]}
        if isinstance(data[key], dict):
            for k in data[key]:
                self._convert_lists(data[key], k)

    def _load_data_from_override(self, source, target, key):
        """Append override data in self.compose.

        Example Compose::
        ---------------
        core:
            build:
                context: ../core
            image: core
            networks:
                - backend
            environment:
                - DEBUG=false
            ports:
             - "8080:80"

        Example override::
        ----------------
        core:
            build:
                dockerfile: Docker_dev
            depends_on:
                - api
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            ports:
                - "9000:80"

        Final Result::
        ------------
        core:
            build:
                context: ../core
                dockerfile: Docker_dev
            depends_on:
                - api
            image: core
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            networks:
                - backend
            ports:
             - "8080:80"
             - "9000:80"

        """
        if target.get(key, None):
            if isinstance(source[key], dict):
                for k in source[key]:
                    self._load_data_from_override(
                        source=source[key],
                        target=target[key],
                        key=k
                    )
            else:
                if isinstance(target[key], list) and isinstance(source[key], list):
                    target[key] += source[key]
                else:
                    target[key] = source[key]
        else:
            if isinstance(target, list) and isinstance(source[key], list):
                target[key] += source[key]
            else:
                target[key] = source[key]

    def get_all_compose_data(self):
        for compose_subgroup_name in self.config_data['compose_files']:
            compose_paths = self.get_compose_files_for_group(compose_subgroup_name)
            compose_data = self.get_compose_data_for_group(compose_paths)
            for service in compose_data['services']:
                self.all_services.append(
                    {
                        'index': "{}_{}".format(service, compose_subgroup_name),
                        'name': service,
                        'subgroup': compose_subgroup_name,
                        'working_dir': os.path.dirname(compose_paths[0]),
                        'compose_data': compose_data['services'][service]
                    }
                )

    def find_service(self, service_informed):

        exact_matches = [
            data
            for data in self.all_services
            if data['name'] == service_informed
        ]
        if len(exact_matches) == 1:
            return exact_matches[0]

        eligible_services = [
            eligible_service
            for eligible_service in self.all_services
            if service_informed in eligible_service['name']
        ]
        if not eligible_services:
            logger.error("Service not found")
            sys.exit(1)
        elif len(eligible_services) == 1:
            return eligible_services[0]
        else:
            choice_list = [
                data['index']
                for data in eligible_services
            ]
            service_name = console.choose(choice_list, 'Please select the service')
        return [
            data
            for data in eligible_services
            if service_name == data['index']
        ][0]

    def get_compose_data_for_group(self, compose_paths) -> dict:
        """Read docker compose files data.

        :return: None
        """
        compose_data_list = []
        for compose_file in compose_paths:
            with open(compose_file, 'r') as file:
                compose_data = yaml.load(file.read())
                for key in compose_data:  # type: ignore
                    self._convert_lists(compose_data, key)
                compose_data_list.append(compose_data)
        reversed_list = list(reversed(compose_data_list))
        self._data = reversed_list[-1]
        for index, override in enumerate(reversed_list):
            self.override = override
            if index + 1 == len(reversed_list):
                break
            for key in self.override:
                self._load_data_from_override(self.override, self._data, key)
        return self._data

    def _resolve_path(self, compose):
        base_compose_path = os.path.dirname(compose)
        if "." in base_compose_path:
            base_compose_path = self.config_data['project']['working_dir']
        return get_path(compose, base_path=base_compose_path)

    def get_compose_files_for_group(self, group):
        return [
            self._resolve_path(compose)
            for compose in self.config_data['compose_files'][group]
        ]

    @property
    def working_dir(self):
        return self._resolve_path(self.config_data['project']['working_dir'])

    @property
    def config_data(self):
        with open(self._config_file) as file:
            config_data = yaml.load(file.read())
        return config_data

    def get_config_from_service(self, service, key):
        return self.config_data.get('services', {}).get(service, {}).get('config', {}).get(key, None)

    @property
    def run_before(self):
        return self.config_data['project'].get('run_before', "")

    @property
    def run_after(self):
        return self.config_data['project'].get('run_after', "")

    def run_command(self, command):
        logger.debug("Running command: {}".format(command))
        command_to_run = "{run_before}{command}{run_after}".format(
            run_before="{} && ".format(self.run_before) if self.run_before else "",
            command=command,
            run_after=" && {}".format(self.run_after) if self.run_after else ""
        )
        ret = console.run(command_to_run)
        if not ret:
            sys.exit(1)


BASE_LOG_PATH = os.path.join(str(Path.home()), '.megalus', 'logs')

if not os.path.exists(BASE_LOG_PATH):
    os.makedirs(BASE_LOG_PATH)

now = datetime.datetime.now().isoformat()
LOGFILE = os.path.join(BASE_LOG_PATH, '{}.log'.format(now))

config = {
    "handlers": [
        {"sink": sys.stdout},
        {"sink": LOGFILE, "retention": "7 days"}
    ],
}
logger.configure(**config)
