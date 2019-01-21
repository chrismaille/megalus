import click

from megalus.compose.commands import run_compose_command


def stop_all(meg):
    compose_set = set([
        data['working_dir']
        for data in meg.all_services
    ])
    for compose_dir in list(compose_set):
        meg.run_command("cd ${} && docker-compose stop".format(compose_dir))


@click.command()
@click.argument('services', nargs=-1)
@click.pass_obj
def stop(meg, services):
    if not services:
        stop_all(meg)
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "stop", service_data)
