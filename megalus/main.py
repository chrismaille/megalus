import os
import sys
from typing import Any, Dict

import yaml
from buzio import console
from loguru import logger

from megalus.utils import get_path


class Megalus:

    def __init__(self, config_file):
        self.service = None
        self._config_file = config_file
        self.base_path = get_path(os.path.dirname(config_file), '.')
        self.compose_data_list = []
        self._data = {}  # type: Dict[str, Any]
        self.all_services = []
        self.all_composes = {}

    @property
    def config_data(self):
        with open(self._config_file) as file:
            config_data = yaml.load(file.read())
        return config_data

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
                - api1
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
                - api1
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

    def _get_compose_data_for(self, compose_path, compose_files) -> dict:
        """Read docker compose files data.

        :return: None
        """
        resolved_paths = [
            get_path(os.path.join(compose_path, file), base_path=self.base_path)
            for file in compose_files
        ]

        compose_data_list = []
        for compose_file in resolved_paths:
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

    def get_services(self):

        for compose_project in self.config_data.get('compose_projects'):
            compose_path = self.config_data['compose_projects'][compose_project]['path']
            compose_files = self.config_data['compose_projects'][compose_project]['files']
            compose_data = self._get_compose_data_for(compose_path, compose_files)
            self.all_composes.update({compose_project: compose_data})
            for service in compose_data['services']:
                self.all_services.append(
                    {
                        'name': service,
                        'compose': compose_project,
                        'full_name': "{} ({})".format(service, compose_project),
                        'compose_files': compose_files,
                        'working_dir': os.path.dirname(
                            get_path(os.path.join(compose_path, compose_files[0]), self.base_path)),
                        'compose_data': compose_data['services'][service]
                    }
                )

    @staticmethod
    def run_command(command):
        logger.debug("Running command: {}".format(command))
        ret = console.run(command)
        if not ret:
            sys.exit(1)
        return ret

    def find_service(self, service_informed):

        exact_matches = [
            data
            for data in self.all_services
            if data['name'] == service_informed
        ]
        if len(exact_matches) == 1:
            self.service = exact_matches[0]['name']
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
            self.service = eligible_services[0]['name']
            return eligible_services[0]
        else:
            choice_list = [
                data['full_name']
                for data in eligible_services
            ]
            service_name = console.choose(choice_list, 'Please select the service')
        data = [
            data
            for data in eligible_services
            if service_name == data['full_name']
        ][0]
        self.service = data['name']
        return data
