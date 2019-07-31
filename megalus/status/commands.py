"""Status command module."""
import sys

import arrow
import click
from blessed import Terminal
from colorama import Style

from megalus.main import Megalus
from megalus.status.dashboard import Dashboard


@click.command()
@click.option('--all', is_flag=True)
@click.pass_obj
def status(meg: Megalus, all: bool) -> None:
    """Return docker services status.

    :param all: Show all services
    :param meg: Megalus instance
    :return: None
    """
    dashboard = Dashboard(meg)
    term = Terminal()
    last_update = arrow.utcnow()
    timeout = 0
    try:
        with term.fullscreen():
            with term.hidden_cursor():
                with term.cbreak():
                    while True:
                        now = arrow.utcnow()
                        if now >= last_update.shift(seconds=timeout):
                            ui, timeout = dashboard.get_layout(term, all)
                            ui.display()
                            last_update = arrow.utcnow()

                        key_pressed = term.inkey(timeout=0)
                        if 'd' in key_pressed.lower():
                            diff = not diff
                        if 'q' in key_pressed.lower():
                            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print(term.color(0))
        sys.exit(0)
    except BaseException as exc:
        print(term.exit_fullscreen)
        print(Style.RESET_ALL)
        raise exc
