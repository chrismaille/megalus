import click
from loguru import logger

from megalus.main import Megalus


@click.command()
@click.option('--remove-all', is_flag=True)
@click.argument('subgroups', nargs=-1)
@click.pass_obj
def down(meg: Megalus, subgroups, remove_all):
    options = "--rmi all -v --remove-orphans" if remove_all else ""

    if not subgroups:
        subgroups = [
            subgroup
            for subgroup in meg.config_data['compose_files']
        ]

    all_working_dirs = set([
        data['working_dir']
        for subgroup in subgroups
        for data in meg.all_services
        if data['subgroup'] == subgroup
    ])
    logger.debug("All working directories: {}".format(", ".join(list(all_working_dirs))))
    for path in list(all_working_dirs):
        meg.run_command(
            "cd {working_dir} && docker-compose down {options}".format(
                working_dir=path,
                options=options
            )
        )
