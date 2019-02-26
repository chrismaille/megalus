import sys

import click
from blessed import Terminal
from dashing import dashing
from colorama import Style

from megalus.main import Megalus


@click.command()
@click.pass_obj
def status(meg: Megalus) -> None:
    term = Terminal()
    try:
        with term.fullscreen():
            with term.hidden_cursor():
                with term.cbreak():
                    while True:
                        key_pressed = term.inkey(timeout=0)
                        if 'q' in key_pressed.lower():
                            raise KeyboardInterrupt
                        ui = meg.get_layout(term)
                        ui.display()
    except KeyboardInterrupt:
        print(term.color(0))
        sys.exit(0)
    except BaseException as exc:
        print(term.exit_fullscreen)
        print(Style.RESET_ALL)
        raise exc