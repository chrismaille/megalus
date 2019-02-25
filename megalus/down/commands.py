"""Docker-Compose down module."""
from typing import List

import click

from megalus import get_path
from megalus.main import Megalus


@click.command()
@click.option('--remove-all', is_flag=True)
@click.argument('projects', nargs=-1)
@click.pass_obj
def down(meg: Megalus, projects: List[str], remove_all: bool) -> None:
    """Down compose project.

    :param meg: Megalus instance
    :param projects: projects to down
    :param remove_all: remove image and containers too
    :return: None
    """
    options = "--rmi all -v --remove-orphans" if remove_all else ""

    for project_name in meg.config_data['compose_projects']:
        if (projects and project_name in projects) or not projects:
            compose_files = meg.config_data['compose_projects'][project_name]['files']
            compose_path = meg.config_data['compose_projects'][project_name]['path']
            meg.run_command(
                "cd {working_dir} && docker-compose -f {files} down {options}".format(
                    working_dir=get_path(compose_path, meg.base_path),
                    files=" -f ".join(compose_files),
                    options=options
                )
            )
