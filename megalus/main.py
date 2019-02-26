"""Main module."""
import os
import sys
from typing import Any, Dict, List, Tuple, Optional

import docker
import yaml
from blessed import terminal
from buzio import console, formatStr
from dashing.dashing import HSplit, Text
from git import InvalidGitRepositoryError, Repo
from loguru import logger
from tabulate import tabulate

from megalus.utils import get_path

client = docker.from_env()


class Megalus:
    """Megalus main class."""

    def __init__(self, config_file: str, logfile: str) -> None:
        """Initialize class.

        :param config_file: path for megalus config path
        :param logfile: path for save log file
        """
        self.service = None
        self._config_file = config_file
        self.base_path = get_path(os.path.dirname(config_file), '.')
        self.compose_data_list = []  # type: List[dict]
        self._data = {}  # type: Dict[str, Any]
        self.all_services = []  # type: List[dict]
        self.all_composes = {}  # type: dict
        self.logfile = logfile
        self._config_data = {}  # type: dict

    @property
    def config_data(self) -> dict:
        """Return megalus configuration data.

        :return: dict
        """
        if self._config_data:
            return self._config_data

        config_path = os.path.join(
            self.base_path,
            os.path.basename(self._config_file)
        )
        with open(config_path) as file:
            self._config_data = yaml.safe_load(file.read()) or {}
        return self._config_data

    def _convert_lists(self, data: dict, key: str) -> None:
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

    def _load_data_from_override(self, source: dict, target: dict, key: str) -> None:
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

    def _get_compose_data_for(self, compose_path: str, compose_files: List[str]) -> dict:
        """Read docker compose files data.

        :return: dict
        """
        resolved_paths = [
            get_path(os.path.join(compose_path, file), base_path=self.base_path)
            for file in compose_files
        ]

        compose_data_list = []
        for compose_file in resolved_paths:
            with open(compose_file, 'r') as file:
                compose_data = yaml.safe_load(file.read())
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

    def get_services(self) -> None:
        """Build service configuration from yaml files.

        :return: None
        """
        for compose_project in self.config_data.get('compose_projects', []):
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
    def run_command(command: str) -> bool:
        """Run command inside subprocess.

        :param command: string: command to be run
        :return: bool
        """
        logger.debug("Running command: {}".format(command))
        ret = console.run(command)
        if not ret:
            sys.exit(1)
        return ret

    def find_service(self, service_informed: str) -> dict:
        """Find service inside megalus service data.

        :param service_informed: string: docker service informed in command.
        :return: docker service megalus data.
        """
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

    def get_layout(self, term: terminal) -> HSplit:
        """Get dashing terminal layout.

        :param term: Blessed Terminal
        :return: dashing instance
        """
        boxes = [self.get_box(project) for project in self.config_data['compose_projects'].keys()]
        ui = HSplit(*boxes, terminal=term, main=True, color=7, background_color=16)
        return ui

    def get_box(self, project: str) -> Text:
        """Return Box widget.

        :param project: project name
        :return: dashing Text widget
        """
        all_services = [
            service
            for service in self.all_composes[project]['services']
        ]
        project_path = self.config_data['compose_projects'][project]['path']
        project_name = os.path.basename(project_path)
        ignore_list = self.config_data['compose_projects'][project].get('show_status', {}).get('ignore_list', [])

        table_header = ['name', 'status', 'git']
        table_lines = []
        for service in all_services:
            if service in ignore_list:
                continue
            name, service_status = self.get_service_status(service, project_name)
            service_context_path = self.all_composes[project]['services'][service].get('build', {}).get('context', None)
            git_status = None
            if service_context_path:
                git_status = self.get_git_status(service_context_path, project_path)
            if not git_status:
                git_status = formatStr.info('--', use_prefix=False, theme="dark")
            table_lines.append([name, service_status, git_status])

        table = tabulate(table_lines, table_header)
        return Text(table, color=6, border_color=5, background_color=16,
                    title=project)

    def get_service_status(self, service: str, project_name: str) -> Tuple[str, str]:
        """Get formatted service name and status.

        :param service: service name
        :param project_name: project name
        :return: Tuple
        """
        service_status = [
            container.status
            for container in client.containers.list()
            if "{}_{}".format(project_name, service) in container.name
        ]
        if not service_status:
            return (
                formatStr.info(service, use_prefix=False, theme="dark"),
                formatStr.info("Not Found", use_prefix=False, theme="dark")
            )

        main_status = max(set(service_status), key=service_status.count)
        replicas = len(service_status)
        replicas_in_main_status = service_status.count(main_status)

        if replicas == replicas_in_main_status:
            text = "{}{}".format(
                main_status.title(),
                " x{}".format(replicas) if replicas > 1 else ""
            )
        else:
            text = "{} x{}/{}".format(
                main_status.title(),
                replicas_in_main_status,
                replicas
            )
        return (
            formatStr.success(service, use_prefix=False)
            if "running" in main_status else formatStr.warning(service, use_prefix=False),
            formatStr.success(text, use_prefix=False)
            if "running" in main_status else formatStr.warning(text, use_prefix=False)
        )

    def get_git_status(self, service_path: str, project_path: str) -> Optional[str]:
        """Get formatted git status.

        :param service_path: service build context path
        :param project_path: project base path
        :return: String
        """
        git_path = get_path(os.path.join(project_path, service_path), self.base_path)
        try:
            service_repo = Repo(git_path)
        except InvalidGitRepositoryError:
            return None
        is_dirty = service_repo.is_dirty()
        text = "{}{}".format(
            service_repo.active_branch.name,
            " (modified)" if is_dirty else ""
        )
        if is_dirty:
            return formatStr.warning(text, use_prefix=False)
        else:
            return formatStr.info(text, use_prefix=False)
