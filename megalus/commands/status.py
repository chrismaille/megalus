import click
import tkinter as tk

from megalus.commands.dashboard import Dashboard
from megalus.core import Megalus
from megalus.core.decorators import run_async


@click.command()
@click.option("--all", is_flag=True)
@run_async
@click.pass_obj
async def status(meg: Megalus, all: bool) -> None:
    """Return docker services status.

    :param all: Show all services
    :param meg: Megalus instance
    :return: None
    """
    root = tk.Tk()
    app = Dashboard(master=root)
    app.mainloop()
