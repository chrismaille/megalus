"""
Usage: geru bash <service>
This command will access bash inside the select service.
You can use this command on stopped containers.
Do not use this command to run unittests inside container.
To run unit tests please check the command geru test

#### Database migration:

For database migrate operations, first enter inside container, using the
command `geru bash <service>` and inside the container, type the needed
alembic command, replacing `alembic-development.ini` for
`alembic-docker.ini`. Make sure you have postgres running to enable the
migration `geru up postgres`

For example, to migrate Core database:

```bash
$ geru bash core
container@root$ alembic -c alembic-docker.ini upgrade head
```
"""

import click
from buzio import console
from loguru import logger

from megalus import Megalus
from megalus.utils import client, find_containers


@click.command()
@click.argument('service', nargs=1, required=True)
@click.pass_obj
def bash(meg: Megalus, service: str) -> None:
    service_data = meg.find_service(service)

    container_id = None
    eligible_containers = find_containers(service_data['name'])
    if not eligible_containers:
        logger.info("Running /bin/bash in service {}".format(service_data['name']))
        meg.run_command(
            'cd {} && docker-compose run --rm --service-ports {} /bin/bash'.format(service_data['working_dir'],
                                                                                   service_data['name'])
        )
    elif len(eligible_containers) == 1:
        container_id = eligible_containers[0].short_id
    else:
        container_names = [c.name for c in eligible_containers]
        container = console.choose(container_names, 'Please select the container')
        if container:
            container_id = client.containers.get(container).short_id
    if container_id:
        logger.info(
            "Running /bin/bash in service {} in container {}".format(service_data['name'], container_id))
        meg.run_command(
            'cd {} && docker exec -ti {} /bin/bash'.format(service_data['working_dir'], container_id)
        )
