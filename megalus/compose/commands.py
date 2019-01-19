"""
commands.
"""

import click

from megalus.utils import find_service


def run_compose_command(meg, action, service_data, options=""):
    meg.run_command(
        "cd {working_dir} && docker-compose {action}{options}{services}".format(
            working_dir=service_data['working_dir'],
            options=" {} ".format(options) if options else " ",
            action=action,
            services=service_data['name']
        )
    )


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def restart(meg, services):
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "restart", service_data)


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def stop(meg, services):
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "stop", service_data)


@click.command()
@click.argument('service', required=True)
@click.argument('number', required=True, default=1, type=click.INT)
@click.pass_obj
def scale(meg, service, number):
    service_data = meg.find_service(service)
    options = "-d --scale {}={}".format(service_data['name'], number)
    run_compose_command(meg, "up", options=options, service_data=service_data)


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('-d', is_flag=True)
@click.pass_obj
def up(meg, services, d):
    options = "-d" if d else ""
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "up", options=options, service_data=service_data)
