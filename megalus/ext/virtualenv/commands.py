from typing import List

import click

from megalus.core.decorators import run_async
from megalus.ext.virtualenv import VirtualMegalus


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def build(meg: VirtualMegalus, services: List[str], detached, need_reset):
    service_list = [await meg.find_service(service_name) for service_name in services]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    results = await meg.run_queue("build", None, detached, service_list)
    await meg.show_results(results)


@click.command()
@click.argument("services", nargs=-1)
@click.option("--d", "--detached", "detached", is_flag=True)
@click.option("--build", "need_build", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def config(
    meg: VirtualMegalus, services: List[str], detached, need_build, need_reset
):
    service_list = [await meg.find_service(service_name) for service_name in services]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    if need_build:
        results = await meg.run_queue("build", None, detached, service_list)
        await meg.show_results(results)

    results = await meg.run_queue("config", None, detached, service_list)
    await meg.show_results(results)


@click.command()
@click.argument("service_name")
@click.argument("service_target")
@click.option("--build", "need_build", is_flag=True)
@click.option("--config", "need_config", is_flag=True)
@click.option("--reset", "need_reset", is_flag=True)
@run_async
@click.pass_obj
async def run(
    meg: VirtualMegalus,
    service_name: str,
    service_target: str,
    need_build: bool,
    need_config: bool,
    need_reset: bool,
):
    service_list = [await meg.find_service(service_name)]

    if need_reset:
        for service in service_list:
            await meg.remove_virtualenv(service)

    if need_build:
        results = await meg.run_queue("build", None, False, service_list)
        await meg.show_results(results)

    if need_config:
        results = await meg.run_queue("config", None, False, service_list)
        await meg.show_results(results)

    results = await meg.run_queue("run", service_target, False, service_list)
    await meg.show_results(results)


@click.command()
@click.argument("services", nargs=-1)
@run_async
@click.pass_obj
async def rm(meg: VirtualMegalus, services: List[str]):
    service_list = [await meg.find_service(service_name) for service_name in services]

    for service in service_list:
        await meg.remove_virtualenv(service)
