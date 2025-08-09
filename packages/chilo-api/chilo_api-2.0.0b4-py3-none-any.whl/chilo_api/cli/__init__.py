import argparse

from chilo_api.cli.openapi import OpenAPI
from chilo_api.cli.server import Server


class CLIManager:
    '''
    Manages the CLI commands for the Chilo API.
    This class provides methods to parse command line arguments and execute the appropriate actions.

    Attributes
    ----------
    args: argparse.Namespace
        Parsed command line arguments.

    Methods
    ----------
    run():
        Parses command line arguments and executes the corresponding action.
    '''

    def __init__(self) -> None:
        self.__args: argparse.Namespace = self.__get_command_line_args()

    @property
    def args(self) -> argparse.Namespace:
        return self.__args

    def run(self) -> None:
        if self.args.action == 'generate-openapi':
            OpenAPI(self.args).generate()
        elif self.args.action == 'serve':
            Server(self.args).run()

    def __get_command_line_args(self) -> argparse.Namespace:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog='Chilo',
            description='Chilo CLI Tool'
        )
        parser.add_argument(
            'action',
            help='the action to take',
            choices=['generate-openapi', 'serve']
        )
        parser.add_argument(
            '-a',
            '--api',
            help='api file to run',
            required=False
        )
        parser.add_argument(
            '-o',
            '--output',
            help='(optional) directory location to save openapi file; defaults handlers directory location',
            required=False
        )
        parser.add_argument(
            '-f',
            '--format',
            help='(optional) comma deliminted format options (yml, json)',
            choices=['yml', 'json', 'yml,json', 'json,yml'],
            required=False
        )
        parser.add_argument(
            '-d',
            '--delete',
            help='(optional) will delete routes and methods not found in code base',
            action='store_true',
            required=False
        )
        parser.add_argument(
            '-s',
            '--host',
            help='(optional) host ip/domain for server; default: 127.0.0.1',
            required=False
        )
        parser.add_argument(
            '-p',
            '--port',
            help='(optional) port to run server on; default 3000',
            required=False
        )
        parser.add_argument(
            '-r',
            '--reload',
            help='(optional) will reload app on file change; default: False',
            required=False
        )
        parser.add_argument(
            '-v',
            '--verbose',
            help='(optional) will run server in verbose/debug mode; default: False',
            required=False
        )
        return parser.parse_args()
