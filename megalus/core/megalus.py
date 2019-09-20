import asyncio
import os
import sys
from pathlib import Path
from typing import List, Type

import aiofiles
import click
import toml
from buzio import console
from loguru import logger
from tabulate import tabulate

from megalus.core.config import get_path
from megalus.core.settings import BaseSettings


class CommandResult:
    return_code: int
    stdout: str
    stderr: str

    def __init__(self, return_code, stdout, stderr):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class ServiceData:
    name: str
    data: dict
    base_path: Path
    python_version: str


class Megalus:
    result: CommandResult
    services: List[ServiceData] = []
    settings: Type[BaseSettings]

    def __init__(self, settings):
        self.settings = settings

    async def run_command(self, command) -> int:
        logger.info(f"Running command: {command}")
        my_env = os.environ.copy()
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=my_env)

        stdout, stderr = await proc.communicate()
        self.result = CommandResult(
            return_code=proc.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
        return proc.returncode

    async def show_command(self, command: str):
        logger.info(f"Running command: {command}")
        proc = await asyncio.create_subprocess_shell(
            command)

        await proc.communicate()
        self.result = CommandResult(
            return_code=proc.returncode,
            stdout="",
            stderr=""
        )
        return proc.returncode

    def echo_result(self):
        if self.result.stdout:
            click.echo(self.result.stdout)
        if self.result.stderr:
            self.error(self.result.stderr)

    def info(self, message: str):
        return click.echo(click.style(message, fg="bright_cyan"))

    def warn(self, message: str):
        return click.echo(click.style(f"Warning: {message}", fg="bright_yellow"))

    def error(self, message: str, exit_code: int = 1):
        click.echo(click.style(f"Error: {message}", fg="bright_red"))
        sys.exit(exit_code)

    def success(self, message: str):
        return click.echo(click.style(f"Success: {message}", fg="bright_green"))

    def table(self, fields: list, data_list):
        def get_row(obj) -> List[str]:
            return [getattr(obj, field) for field in fields]

        table_rows = [get_row(obj) for obj in data_list]

        return click.echo(click.style(tabulate(table_rows, fields), fg="yellow"))

    async def find_service(self, service_name: str) -> ServiceData:
        eligible_services = [
            service
            for service in self.services
            if service_name in service.name.lower()
        ]
        if not eligible_services:
            self.error(f"{service_name} was not found.")
        if len(eligible_services) == 1:
            return eligible_services[0]
        service = console.choose(eligible_services, "Please select the service")
        logger.info(f"Service is {service.name}")
        return service

    async def find_services(self):
        project_paths = self.settings.project_paths
        for project_path in project_paths:
            real_path = get_path(project_path, os.getcwd())
            logger.debug(f"Looking into {real_path}")
            for toml_path in sorted(Path(real_path).rglob("pyproject.toml")):
                logger.debug(f"{toml_path} found. Checking for megalus configuration...")
                async with aiofiles.open(toml_path, "r") as file:
                    toml_data = toml.loads(await file.read())
                service_dict = toml_data.get('tool', {}).get('megalus')
                if service_dict:
                    service_data = ServiceData()
                    service_data.name = service_dict.get('name', toml_path.parent.name)
                    service_data.base_path = toml_path.parent.resolve()
                    service_data.python_version = service_dict.get('python_version')
                    service_data.data = service_dict
                    self.services.append(service_data)
                    logger.debug(f"Megalus configuration loaded.")
                    logger.debug(f"Project Name: {service_data.name}")
                    logger.debug(f"Project base path: {service_data.base_path}")
                    logger.debug(f"Project dict: {service_data.data}")
                else:
                    logger.debug(f"Megalus configuration not found.")

    @staticmethod
    def exit(return_code: int = 0):
        sys.exit(return_code)
