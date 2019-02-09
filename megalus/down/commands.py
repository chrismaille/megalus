import os

import click

from megalus import get_path
from megalus.main import Megalus


@click.command()
@click.option('--remove-all', is_flag=True)
@click.argument('projects', nargs=-1)
@click.pass_obj
def down(meg: Megalus, projects, remove_all):
    options = "--rmi all -v --remove-orphans" if remove_all else ""

    for project_name in meg.config_data['compose_projects']:
        if (projects and project_name in projects) or not projects:
            compose_files = meg.config_data['compose_projects'][project_name]['files']
            meg.run_command(
                "cd {working_dir} && docker-compose {files} down {options}".format(
                    working_dir=os.path.dirname(get_path(compose_files[0], meg.base_path)),
                    files="-f ".join(compose_files),
                    options=options
                )
            )
