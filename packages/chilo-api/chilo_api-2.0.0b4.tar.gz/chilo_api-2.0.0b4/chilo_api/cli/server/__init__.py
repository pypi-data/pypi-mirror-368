from typing import Any
from werkzeug.serving import run_simple

from chilo_api.cli.server.arguments import ServerArguments
from chilo_api.cli.importer import CLIImporter
from chilo_api.cli.logger import CLILogger
from chilo_api.cli.validator import CLIValidator
from chilo_api.cli.server.grpc import GRPCServer


class Server:
    '''
    A class to manage the server operations, including running the server and handling API imports.
    This class provides methods to initialize the server, run it, and handle command line arguments.
    Methods
    ----------
    run():
        Parses command line arguments and executes the corresponding action.
    '''

    def __init__(self, args: Any) -> None:
        self.args: Any = args
        self.validator: CLIValidator = CLIValidator()
        self.logger: CLILogger = CLILogger()
        self.importer: CLIImporter = CLIImporter()

    def run(self) -> None:
        self.logger.log_server_start()
        api: Any = self.importer.get_api_module(self.args.api)
        self.__run_server(api)

    def __run_server(self, api: Any) -> None:
        server_args = ServerArguments(self.args, api)
        self.logger.log_server_settings(server_args)  # type: ignore
        if server_args.api_type == 'grpc':
            GRPCServer(server_args, self.logger).run()  # type: ignore
        else:
            run_simple(server_args.host, server_args.port, api.route, use_reloader=server_args.reload, use_debugger=server_args.verbose)
        self.logger.log_end()
