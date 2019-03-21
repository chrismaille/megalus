"""Megalus Start Command."""
import click

from megalus import get_path
from megalus.main import Megalus


@click.command()
@click.argument('projects', nargs=-1, required=True)
@click.option('-d', is_flag=True)
@click.pass_obj
def start(meg: Megalus, projects: str, d: bool) -> None:
    """Start selected projects.

    :param meg: Megalus instance
    :param projects: Megalus projects to be started up
    :param d: detached option
    :return: None
    """
    options = "-d" if d or len(projects) > 1 else ""
    for project_name in meg.config_data['compose_projects']:
        if project_name in projects:
            compose_files = meg.config_data['compose_projects'][project_name]['files']
            compose_path = meg.config_data['compose_projects'][project_name]['path']
            meg.run_command(
                "cd {working_dir} && docker-compose -f {files} up {options}".format(
                    working_dir=get_path(compose_path, meg.base_path),
                    files=" -f ".join(compose_files),
                    options=options
                )
            )
