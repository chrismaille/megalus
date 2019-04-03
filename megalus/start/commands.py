"""Megalus Start Command."""
import click

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus
from megalus.utils import get_path


@click.command()
@click.argument('projects', nargs=-1, required=True)
@click.pass_obj
def start(meg: Megalus, projects: str) -> None:
    """Start selected projects.

    :param meg: Megalus instance
    :param projects: Megalus projects to be started up
    :return: None
    """
    for project_name in meg.config_data['compose_projects']:
        if project_name in projects:
            service_data = {
                'compose_files': meg.config_data['compose_projects'][project_name]['files'],
                'working_dir': get_path(meg.config_data['compose_projects'][project_name]['path'], meg.base_path)
            }
            run_compose_command(
                meg,
                action="up -d",
                service_data=service_data,
                all_services=True
            )
