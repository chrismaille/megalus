import click

from megalus.bash.commands import bash
from megalus.build.commands import build
from megalus.check.commands import check
from megalus.commands.commands import config, init, install, reset, update
from megalus.compose.commands import restart, scale, up
from megalus.down.commands import down
from megalus.logs.commands import logs
from megalus.main import Megalus
from megalus.run.commands import run
from megalus.stop.commands import stop


@click.group()
@click.option('--config_file', envvar='MEGALUS_PROJECT_CONFIG_FILE', required=True, type=click.Path())
@click.pass_context
def cli(ctx, config_file):
    meg = Megalus(config_file=config_file)
    meg.get_services()
    ctx.obj = meg


cli.add_command(bash)
cli.add_command(build)
cli.add_command(config)
cli.add_command(down)
cli.add_command(install)
cli.add_command(logs)
cli.add_command(reset)
cli.add_command(restart)
cli.add_command(run)
cli.add_command(scale)
cli.add_command(stop)
cli.add_command(up)
cli.add_command(update)
cli.add_command(check)
cli.add_command(init)


def start():
    cli()
