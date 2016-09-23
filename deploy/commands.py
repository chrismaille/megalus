#!/usr/bin/env python
'''Deploy Tool for Loja Integrada
Usage:
    lideploy -q --quiet
    lideploy -n --no-static
    lideploy -h --help
    lideploy -v --version
    lideploy -t --test
Options:
    -h --help                           Show this help.
    -q --quiet                          Do not show messages
    -n --no-static                      Do not make static files operations
    -v --version                        Show version
    -t --test                           Run for tests
'''
from docopt import docopt
from deploy.main import main


class ArgParser(object):
    def __init__(self, arguments):
        self.arguments = arguments

    def run(self):
        if self.arguments.get['--version']:
            print("version 1.0 (23/09/16")
        else:
            ret = main(
                quiet=self.arguments['--quiet'],
                no_static=self.arguments['--no-static'],
                test=self.arguments['--test']
            )
        if not ret:
            print("A operação não foi concluída")


def start():
    arguments = docopt(__doc__, version='2.0')
    parser = ArgParser(arguments)
    parser.run()


if __name__ == '__main__':
    start()
