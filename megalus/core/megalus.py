import asyncio
import os
import sys
from abc import ABC, ABCMeta, abstractmethod
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
    command: str

    def __init__(self, command, return_code, stdout, stderr):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class ServiceData:
    name: str
    data: dict
    base_path: Path
    language_name: str
    language_version: str


class AbstractMegalus(metaclass=ABCMeta):
    result: CommandResult
    services: List[ServiceData] = []
    settings: Type[BaseSettings]
    platform: str

    def __init__(self, settings):
        self.settings = settings

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
            service for service in self.services if service_name in service.name.lower()
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
            for toml_path in sorted(Path(real_path).rglob("*project.toml")):
                logger.debug(
                    f"{toml_path} found. Checking for megalus configuration..."
                )
                async with aiofiles.open(toml_path, "r") as file:
                    toml_data = toml.loads(await file.read())
                service_dict = toml_data.get("tool", {}).get("megalus")
                if service_dict:
                    service_data = ServiceData()
                    service_data.name = service_dict.get("name", toml_path.parent.name)
                    service_data.base_path = toml_path.parent.resolve()
                    service_data.language_name = service_dict.get("language_name")
                    service_data.language_version = service_dict.get("language_version")
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

    @abstractmethod
    def execute(self, detached, service, command_key, event):
        pass

    async def run_queue(self, command_key, target, detached, service_list) -> List[CommandResult]:
        queue = asyncio.Queue()
        tasks = []
        for service in service_list:
            command = service.data.get(command_key, {}).get(self.platform)
            if target:
                command = command.get(target)
            if not command:
                if self.settings.exit_on_errors:
                    logger.error(
                        f"Command '{command_key}' not found for service {service.name}. Exiting..."
                    )
                    self.exit(1)
                else:
                    logger.info(
                        f"Command '{command_key}' not found for service {service.name}. Ignoring service..."
                    )
                    return [CommandResult(return_code=0, command="", stdout="", stderr="")]

            # TODO: Remove check after remove Python 3.6
            if hasattr(asyncio, "create_task"):
                tasks.append(
                    asyncio.create_task(self.execute(detached, service, command, queue))
                )
            else:
                loop = asyncio.get_event_loop()
                tasks.append(
                    loop.create_task(self.execute(detached, service, command, queue))
                )
        # TODO: Remove check after remove Python 3.6
        if hasattr(asyncio, "create_task"):
            result = await queue.join()
        else:
            result = [await task for task in tasks]
        return result

    async def show_results(self, results):
        for result in results:
            if result.return_code == 0:
                if result.command:
                    logger.success(f"Command {result.command} run successfully.")
            else:
                logger.error(f"Error during command {result.command}:")
                self.error(result.stderr)


class PosixMixin:
    script_directory = "bin"
    decoding = "utf-8"

    async def get_python_version(self, service):
        return f"python{service.language_version}"

    async def run_command(
            self, command: str, capture: bool = False
    ) -> CommandResult:
        if capture:
            stdout_pipe = asyncio.subprocess.PIPE
        else:
            stdout_pipe = None
            logger.warning(f"Running: {command}")

        stderr_pipe = asyncio.subprocess.PIPE

        proc = await asyncio.create_subprocess_shell(command, stdout=stdout_pipe, stderr=stderr_pipe)
        stdout, stderr = await proc.communicate()
        return CommandResult(
            command=command,
            return_code=proc.returncode,
            stdout=stdout.decode(self.decoding) if stdout else "",
            stderr=stderr.decode(self.decoding) if stderr else ""
        )


class WindowsMixin:
    script_directory = "Scripts"
    decoding = "ISO-8859-1"

    async def get_python_version(self, service):
        python_version = f"Python{service.language_version.replace('.', '')}"
        result = await self.run_command("where python", capture=True, silent=True)
        python_paths = result.stdout.split("\r\n")
        location = [path for path in python_paths if python_version in path][0]
        if not location:
            raise ValueError(f"{python_version} not found.")
        logger.debug(f"Python locations found: {python_paths}")
        return location

    async def run_command(
            self, command: str, capture: bool = False, silent: bool = False
    ) -> CommandResult:
        import subprocess

        if not silent:
            logger.warning(f"Running: {command}")

        stdout_pipe = subprocess.PIPE if capture else None
        stderr_pipe = stdout_pipe

        proc = subprocess.run(
            command.split(" "), stdout=stdout_pipe, stderr=stderr_pipe, shell=True
        )
        return CommandResult(
            command=command,
            return_code=proc.returncode,
            stdout=proc.stdout.decode(self.decoding) if proc.stdout else "",
            stderr=proc.stderr.decode(self.decoding) if proc.stderr else "",
        )


if "win" in sys.platform:

    class Megalus(AbstractMegalus, WindowsMixin, ABC):
        pass


else:

    class Megalus(AbstractMegalus, PosixMixin, ABC):
        pass
